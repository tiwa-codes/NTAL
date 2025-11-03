from pydantic import BaseModel, EmailStr
from typing import Optional
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
    patient_name: str
    patient_phone: str
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    chief_complaint: str
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
    source: str
    assigned_provider_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
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
