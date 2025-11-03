from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ...core.database import get_db
from ...core.security import decode_access_token
from ...models.models import Provider, Encounter
from ...schemas.schemas import (
    HealthCheck,
    EncounterCreate,
    Encounter as EncounterSchema,
    EncounterUpdate,
    LoginRequest,
    Token,
    Provider as ProviderSchema,
)
from ...core.security import verify_password, create_access_token
from ...core.config import settings

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
