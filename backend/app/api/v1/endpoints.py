from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ...core.database import get_db
from ...core.security import decode_access_token
from ...models.models import Provider, Encounter, Callback, CallbackStatus, CallbackPriority
from ...schemas.schemas import (
    HealthCheck,
    EncounterCreate,
    Encounter as EncounterSchema,
    EncounterUpdate,
    LoginRequest,
    Token,
    Provider as ProviderSchema,
    USSDRequest,
    Callback as CallbackSchema,
    CallbackAssign,
    CallbackComplete,
    USSDMetrics,
)
from ...core.security import verify_password, create_access_token
from ...core.config import settings
from ...core.ussd_session import USSDSession
from ...core.ussd_state_machine import USSDStateMachine
from ...core.ussd_utils import hash_msisdn, mask_msisdn

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


def get_current_provider(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Provider:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    provider = db.query(Provider).filter(Provider.username == username).first()
    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provider not found",
        )
    return provider


@router.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )


@router.post("/auth/login", response_model=Token, tags=["auth"])
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """Provider login endpoint"""
    provider = db.query(Provider).filter(Provider.username == login_request.username).first()
    if not provider or not verify_password(login_request.password, provider.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": provider.username})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/triage", response_model=EncounterSchema, tags=["triage"], status_code=status.HTTP_201_CREATED)
async def create_triage(encounter: EncounterCreate, db: Session = Depends(get_db)):
    """Create a new triage encounter (store-and-forward)"""
    db_encounter = Encounter(**encounter.model_dump())
    db.add(db_encounter)
    db.commit()
    db.refresh(db_encounter)
    return db_encounter


@router.get("/encounters", response_model=List[EncounterSchema], tags=["encounters"])
async def list_encounters(
    skip: int = 0,
    limit: int = 100,
    current_provider: Provider = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """List all encounters (requires authentication)"""
    encounters = db.query(Encounter).offset(skip).limit(limit).all()
    return encounters


@router.get("/encounters/{encounter_id}", response_model=EncounterSchema, tags=["encounters"])
async def get_encounter(
    encounter_id: int,
    current_provider: Provider = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Get a specific encounter by ID (requires authentication)"""
    encounter = db.query(Encounter).filter(Encounter.id == encounter_id).first()
    if encounter is None:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter


@router.put("/encounters/{encounter_id}", response_model=EncounterSchema, tags=["encounters"])
async def update_encounter(
    encounter_id: int,
    encounter_update: EncounterUpdate,
    current_provider: Provider = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Update an encounter (requires authentication)"""
    encounter = db.query(Encounter).filter(Encounter.id == encounter_id).first()
    if encounter is None:
        raise HTTPException(status_code=404, detail="Encounter not found")
    
    for key, value in encounter_update.model_dump(exclude_unset=True).items():
        setattr(encounter, key, value)
    
    db.commit()
    db.refresh(encounter)
    return encounter


@router.get("/me", response_model=ProviderSchema, tags=["auth"])
async def get_current_provider_info(
    current_provider: Provider = Depends(get_current_provider)
):
    """Get current provider information"""
    return current_provider


# USSD Endpoints
@router.post("/ussd", tags=["ussd"])
async def ussd_handler(
    request: USSDRequest,
    db: Session = Depends(get_db)
):
    """
    Handle USSD requests from aggregator.
    
    Accepts: sessionId, phoneNumber, serviceCode, text
    Returns: "CON ..." or "END ..."
    """
    session_id = request.sessionId
    msisdn = request.phoneNumber
    user_input = request.text.strip() if request.text else ""
    
    # Log request with masked MSISDN
    logger.info(f"USSD request: session={session_id}, msisdn={mask_msisdn(msisdn)}, input='{user_input}'")
    
    # Check rate limit
    msisdn_hash_val = hash_msisdn(msisdn)
    session = USSDSession(session_id)
    
    if not await session.check_rate_limit(msisdn_hash_val):
        logger.warning(f"Rate limit exceeded for msisdn={mask_msisdn(msisdn)}")
        return {"response": "END " + "Limit reached. Try again tomorrow."}
    
    # Get or create session state
    state = await session.get_state()
    state["msisdn"] = msisdn
    
    # Extract current step and user input
    current_step = state.get("step", "consent")
    language = state.get("language", "en")
    
    # If this is first request (empty input), show consent
    if user_input == "":
        current_step = "consent"
        state["step"] = "consent"
    else:
        # Parse the last input from the text field
        # USSD sends accumulated input like "1*2*3", we want the last choice
        input_parts = user_input.split("*")
        user_input = input_parts[-1] if input_parts else ""
    
    # Process the step
    state_machine = USSDStateMachine(language)
    response_type, message, new_state = state_machine.process_step(
        current_step,
        user_input,
        state,
        db
    )
    
    # Save updated state
    if response_type == "CON":
        await session.set_state(new_state)
    else:
        # Session ended, clear state
        await session.clear()
    
    # Return USSD response
    response_text = f"{response_type} {message}"
    logger.info(f"USSD response: session={session_id}, type={response_type}")
    
    return {"response": response_text}


# Callback Endpoints
@router.get("/callbacks", response_model=List[CallbackSchema], tags=["callbacks"])
async def list_callbacks(
    status: Optional[CallbackStatus] = Query(None, description="Filter by status"),
    priority: Optional[CallbackPriority] = Query(None, description="Filter by priority"),
    current_provider: Provider = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """List callbacks with optional filters (requires authentication)."""
    query = db.query(Callback)
    
    if status:
        query = query.filter(Callback.status == status)
    if priority:
        query = query.filter(Callback.priority == priority)
    
    # Order by priority (urgent first) and creation time
    priority_order = case(
        (Callback.priority == CallbackPriority.URGENT, 1),
        (Callback.priority == CallbackPriority.HIGH, 2),
        (Callback.priority == CallbackPriority.MEDIUM, 3),
        (Callback.priority == CallbackPriority.LOW, 4),
        else_=5
    )
    
    callbacks = query.order_by(priority_order, Callback.created_at).all()
    return callbacks


@router.post("/callbacks/{callback_id}/assign", response_model=CallbackSchema, tags=["callbacks"])
async def assign_callback(
    callback_id: int,
    assignment: CallbackAssign,
    current_provider: Provider = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Assign a callback to a provider (requires authentication)."""
    callback = db.query(Callback).filter(Callback.id == callback_id).first()
    if not callback:
        raise HTTPException(status_code=404, detail="Callback not found")
    
    if callback.status != CallbackStatus.QUEUED:
        raise HTTPException(status_code=400, detail="Callback is not in queued status")
    
    # Verify provider exists
    provider = db.query(Provider).filter(Provider.id == assignment.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Update callback
    callback.provider_id = assignment.provider_id
    callback.status = CallbackStatus.IN_PROGRESS
    callback.assigned_at = datetime.utcnow()
    
    db.commit()
    db.refresh(callback)
    
    logger.info(f"Callback {callback_id} assigned to provider {assignment.provider_id}")
    return callback


@router.post("/callbacks/{callback_id}/complete", response_model=CallbackSchema, tags=["callbacks"])
async def complete_callback(
    callback_id: int,
    completion: CallbackComplete,
    current_provider: Provider = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Mark a callback as complete (requires authentication)."""
    callback = db.query(Callback).filter(Callback.id == callback_id).first()
    if not callback:
        raise HTTPException(status_code=404, detail="Callback not found")
    
    if callback.status not in [CallbackStatus.QUEUED, CallbackStatus.IN_PROGRESS]:
        raise HTTPException(status_code=400, detail="Callback is already completed or failed")
    
    # Update callback
    callback.status = CallbackStatus.DONE
    callback.outcome = completion.outcome
    callback.notes = completion.notes
    callback.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(callback)
    
    logger.info(f"Callback {callback_id} marked as complete")
    return callback


# Analytics/Metrics Endpoint
@router.get("/metrics/ussd", response_model=USSDMetrics, tags=["metrics"])
async def get_ussd_metrics(
    current_provider: Provider = Depends(get_current_provider),
    db: Session = Depends(get_db)
):
    """Get USSD analytics (requires admin authentication)."""
    if current_provider.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Total USSD encounters
    total_ussd = db.query(Encounter).filter(Encounter.channel == "USSD").count()
    
    # Encounters with risk assessment (completed)
    completed_ussd = db.query(Encounter).filter(
        Encounter.channel == "USSD",
        Encounter.risk_code.isnot(None)
    ).count()
    
    completion_rate = (completed_ussd / total_ussd * 100) if total_ussd > 0 else 0
    
    # Risk distribution
    risk_counts = db.query(
        Encounter.risk_code,
        func.count(Encounter.id)
    ).filter(
        Encounter.channel == "USSD",
        Encounter.risk_code.isnot(None)
    ).group_by(Encounter.risk_code).all()
    
    risk_distribution = {risk: count for risk, count in risk_counts}
    
    # Daily counts (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_encounters = db.query(
        func.date(Encounter.created_at).label("date"),
        func.count(Encounter.id)
    ).filter(
        Encounter.channel == "USSD",
        Encounter.created_at >= seven_days_ago
    ).group_by(func.date(Encounter.created_at)).all()
    
    daily_counts = {str(date): count for date, count in daily_encounters}
    
    # Callback SLA metrics
    total_callbacks = db.query(Callback).count()
    
    # Average time to assignment
    avg_time_to_assign = db.query(
        func.avg(
            func.julianday(Callback.assigned_at) - func.julianday(Callback.created_at)
        ) * 24  # Convert to hours
    ).filter(Callback.assigned_at.isnot(None)).scalar() or 0
    
    # Average time to completion
    avg_time_to_complete = db.query(
        func.avg(
            func.julianday(Callback.completed_at) - func.julianday(Callback.created_at)
        ) * 24  # Convert to hours
    ).filter(Callback.completed_at.isnot(None)).scalar() or 0
    
    callback_sla = {
        "total_callbacks": total_callbacks,
        "avg_time_to_assign_hours": round(avg_time_to_assign, 2),
        "avg_time_to_complete_hours": round(avg_time_to_complete, 2)
    }
    
    return USSDMetrics(
        total_sessions=total_ussd,
        completion_rate=round(completion_rate, 2),
        risk_distribution=risk_distribution,
        daily_counts=daily_counts,
        callback_sla=callback_sla
    )
