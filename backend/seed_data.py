"""Seed data for NTAL Telehealth"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.models import Provider, Encounter, ProviderRole, EncounterStatus, EncounterUrgency
from app.core.security import get_password_hash


def seed_providers(db: Session):
    """Seed initial providers"""
    providers = [
        Provider(
            username="dr.smith",
            email="smith@ntal.health",
            hashed_password=get_password_hash("pass123"),
            full_name="Dr. John Smith",
            role=ProviderRole.DOCTOR
        ),
        Provider(
            username="nurse.jane",
            email="jane@ntal.health",
            hashed_password=get_password_hash("pass123"),
            full_name="Jane Doe",
            role=ProviderRole.NURSE
        ),
        Provider(
            username="chw.mary",
            email="mary@ntal.health",
            hashed_password=get_password_hash("pass123"),
            full_name="Mary Johnson",
            role=ProviderRole.CHW
        ),
    ]
    
    for provider in providers:
        existing = db.query(Provider).filter(Provider.username == provider.username).first()
        if not existing:
            db.add(provider)
    
    db.commit()
    print(f"✓ Seeded {len(providers)} providers")


def seed_encounters(db: Session):
    """Seed sample encounters"""
    encounters = [
        Encounter(
            patient_name="Alice Johnson",
            patient_phone="+1234567890",
            patient_age=35,
            patient_gender="female",
            chief_complaint="Persistent headache for 3 days",
            symptoms="Severe headache, sensitivity to light, nausea",
            duration="3 days",
            medical_history="No significant medical history",
            status=EncounterStatus.PENDING,
            urgency=EncounterUrgency.MEDIUM,
            source="web"
        ),
        Encounter(
            patient_name="Bob Williams",
            patient_phone="+1234567891",
            patient_age=45,
            patient_gender="male",
            chief_complaint="Chest pain and shortness of breath",
            symptoms="Chest tightness, difficulty breathing, sweating",
            duration="2 hours",
            medical_history="Hypertension, diabetes",
            status=EncounterStatus.PENDING,
            urgency=EncounterUrgency.HIGH,
            source="ussd"
        ),
        Encounter(
            patient_name="Carol Brown",
            patient_phone="+1234567892",
            patient_age=28,
            patient_gender="female",
            chief_complaint="Fever and cough",
            symptoms="High fever, dry cough, body aches",
            duration="5 days",
            medical_history="None",
            status=EncounterStatus.IN_PROGRESS,
            urgency=EncounterUrgency.MEDIUM,
            source="sms",
            assigned_provider_id=1
        ),
    ]
    
    for encounter in encounters:
        db.add(encounter)
    
    db.commit()
    print(f"✓ Seeded {len(encounters)} encounters")


def main():
    """Run all seed functions"""
    print("Starting database seeding...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    # Create session
    db = SessionLocal()
    
    try:
        seed_providers(db)
        seed_encounters(db)
        print("\n✅ Database seeding completed successfully!")
        print("\nTest credentials:")
        print("  Username: dr.smith / Password: pass123")
        print("  Username: nurse.jane / Password: pass123")
        print("  Username: chw.mary / Password: pass123")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
