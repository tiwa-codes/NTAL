from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
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
    patient_name = Column(String(255), nullable=False)
    patient_phone = Column(String(20), nullable=False)
    patient_age = Column(Integer)
    patient_gender = Column(String(20))
    
    chief_complaint = Column(Text, nullable=False)
    symptoms = Column(Text)
    duration = Column(String(100))
    medical_history = Column(Text)
    
    status = Column(Enum(EncounterStatus), default=EncounterStatus.PENDING)
    urgency = Column(Enum(EncounterUrgency), default=EncounterUrgency.MEDIUM)
    
    source = Column(String(50), default="web")  # web, ussd, sms, whatsapp, ivr
    
    assigned_provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    assigned_provider = relationship("Provider", back_populates="encounters")
    
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
