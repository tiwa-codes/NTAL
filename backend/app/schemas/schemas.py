from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProviderRole(str, Enum):
    DOCTOR = "doctor"
    NURSE = "nurse"
    CHW = "chw"
    ADMIN = "admin"


class EncounterStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"


class EncounterUrgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CallbackStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"


class CallbackPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Provider Schemas
class ProviderBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: ProviderRole = ProviderRole.NURSE


class ProviderCreate(ProviderBase):
    password: str


class Provider(ProviderBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Encounter Schemas
class EncounterBase(BaseModel):
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    chief_complaint: Optional[str] = None
    symptoms: Optional[str] = None
    duration: Optional[str] = None
    medical_history: Optional[str] = None


class EncounterCreate(EncounterBase):
    source: str = "web"


class EncounterUpdate(BaseModel):
    status: Optional[EncounterStatus] = None
    urgency: Optional[EncounterUrgency] = None
    assigned_provider_id: Optional[int] = None
    notes: Optional[str] = None


class Encounter(EncounterBase):
    id: int
    status: EncounterStatus
    urgency: EncounterUrgency
    source: Optional[str] = None
    channel: Optional[str] = None
    risk_code: Optional[str] = None
    age_group: Optional[str] = None
    assigned_provider_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# USSD Schemas
class USSDRequest(BaseModel):
    sessionId: str
    phoneNumber: str
    serviceCode: str
    text: str


class USSDResponse(BaseModel):
    response: str


# Callback Schemas
class CallbackBase(BaseModel):
    encounter_id: int
    msisdn_hash: str
    priority: CallbackPriority = CallbackPriority.MEDIUM


class CallbackCreate(CallbackBase):
    pass


class CallbackAssign(BaseModel):
    provider_id: int


class CallbackComplete(BaseModel):
    outcome: str
    notes: Optional[str] = None


class Callback(CallbackBase):
    id: int
    status: CallbackStatus
    provider_id: Optional[int] = None
    outcome: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# Health Check
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"


# Metrics Schemas
class USSDMetrics(BaseModel):
    total_sessions: int
    completion_rate: float
    risk_distribution: Dict[str, int]
    daily_counts: Dict[str, int]
    callback_sla: Dict[str, Any]
