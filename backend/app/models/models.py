from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class ProviderRole(str, enum.Enum):
    DOCTOR = "doctor"
    NURSE = "nurse"
    CHW = "chw"
    ADMIN = "admin"


class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(ProviderRole), default=ProviderRole.NURSE)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    encounters = relationship("Encounter", back_populates="assigned_provider")
    callbacks = relationship("Callback", back_populates="provider")


class EncounterStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"


class EncounterUrgency(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Encounter(Base):
    __tablename__ = "encounters"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # For web-based encounters
    patient_name = Column(String(255), nullable=True)
    patient_phone = Column(String(20), nullable=True)
    patient_age = Column(Integer)
    patient_gender = Column(String(20))
    
    chief_complaint = Column(Text, nullable=True)
    symptoms = Column(Text)
    duration = Column(String(100))
    medical_history = Column(Text)
    
    # For USSD-based encounters (minimal PHI)
    channel = Column(String(50), default="web")  # web, ussd, sms, whatsapp, ivr
    msisdn_hash = Column(String(64), nullable=True, index=True)  # SHA-256 hashed phone number
    age_group = Column(String(20), nullable=True)  # <5, 5-17, 18-49, 50+
    symptoms_json = Column(JSON, nullable=True)  # Structured symptom responses
    risk_code = Column(String(50), nullable=True)  # EMERGENCY, MALARIA_SUSPECT, etc.
    consent_given = Column(Boolean, default=False)
    consent_version = Column(String(50), nullable=True)
    
    status = Column(Enum(EncounterStatus), default=EncounterStatus.PENDING)
    urgency = Column(Enum(EncounterUrgency), default=EncounterUrgency.MEDIUM)
    
    source = Column(String(50), default="web")  # Deprecated in favor of 'channel'
    
    assigned_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    assigned_provider = relationship("Provider", back_populates="encounters")
    
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    callbacks = relationship("Callback", back_populates="encounter")


class CallbackStatus(str, enum.Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"


class CallbackPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Callback(Base):
    __tablename__ = "callbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False)
    encounter = relationship("Encounter", back_populates="callbacks")
    
    msisdn_hash = Column(String(64), nullable=False, index=True)
    priority = Column(Enum(CallbackPriority), default=CallbackPriority.MEDIUM)
    status = Column(Enum(CallbackStatus), default=CallbackStatus.QUEUED, index=True)
    
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    provider = relationship("Provider", back_populates="callbacks")
    
    outcome = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    assigned_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
