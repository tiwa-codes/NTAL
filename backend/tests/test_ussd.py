"""Tests for USSD functionality."""

import pytest
from unittest.mock import AsyncMock, patch
from app.core.ussd_session import USSDSession
from app.core.ussd_utils import hash_msisdn, mask_msisdn
from app.core.triage_engine import assess_risk, get_priority_from_risk
from app.models.models import Encounter, Callback
import json


def test_hash_msisdn():
    """Test MSISDN hashing."""
    msisdn = "+1234567890"
    hashed = hash_msisdn(msisdn)
    
    # Should be 64-character hex string (SHA-256)
    assert len(hashed) == 64
    assert all(c in "0123456789abcdef" for c in hashed)
    
    # Same input should produce same hash
    assert hash_msisdn(msisdn) == hashed
    
    # Different input should produce different hash
    assert hash_msisdn("+0987654321") != hashed


def test_mask_msisdn():
    """Test MSISDN masking for logging."""
    assert mask_msisdn("+1234567890") == "***890"
    assert mask_msisdn("+254712345678") == "***678"
    assert mask_msisdn("12") == "***"


def test_triage_engine_emergency():
    """Test triage engine identifies emergency cases."""
    symptoms = {
        "fever": True,
        "severe_headache": False,
        "danger_sign": True,
        "cough": False
    }
    
    risk_code, advice, urgent = assess_risk(symptoms)
    
    assert risk_code == "EMERGENCY"
    assert urgent is True
    assert "Emergency" in advice


def test_triage_engine_malaria_suspect():
    """Test triage engine identifies possible malaria."""
    symptoms = {
        "fever": True,
        "severe_headache": True,
        "danger_sign": False,
        "cough": False
    }
    
    risk_code, advice, urgent = assess_risk(symptoms)
    
    assert risk_code == "MALARIA_SUSPECT"
    assert urgent is False
    assert "malaria" in advice.lower()


def test_triage_engine_fever_general():
    """Test triage engine for general fever."""
    symptoms = {
        "fever": True,
        "severe_headache": False,
        "danger_sign": False,
        "cough": True
    }
    
    risk_code, advice, urgent = assess_risk(symptoms)
    
    assert risk_code == "FEVER_GENERAL"
    assert urgent is False


def test_triage_engine_low_risk():
    """Test triage engine for low risk cases."""
    symptoms = {
        "fever": False,
        "severe_headache": False,
        "danger_sign": False,
        "cough": True
    }
    
    risk_code, advice, urgent = assess_risk(symptoms)
    
    assert risk_code == "LOW_RISK"
    assert urgent is False


def test_priority_mapping():
    """Test risk code to priority mapping."""
    assert get_priority_from_risk("EMERGENCY") == "urgent"
    assert get_priority_from_risk("MALARIA_SUSPECT") == "high"
    assert get_priority_from_risk("FEVER_GENERAL") == "medium"
    assert get_priority_from_risk("LOW_RISK") == "low"


class MockRedis:
    """Mock Redis for testing with in-memory storage."""
    def __init__(self):
        self.storage = {}
    
    async def get(self, key):
        return self.storage.get(key)
    
    async def setex(self, key, ttl, value):
        self.storage[key] = value
    
    async def incr(self, key):
        val = self.storage.get(key, "0")
        new_val = str(int(val) + 1)
        self.storage[key] = new_val
        return int(new_val)
    
    async def delete(self, key):
        if key in self.storage:
            del self.storage[key]


@pytest.mark.asyncio
async def test_ussd_happy_path_low_risk(client, db):
    """Test complete USSD flow for low risk case."""
    session_id = "test-session-1"
    phone = "+254712345678"
    service_code = "*123#"
    
    # Mock Redis with state persistence
    mock_redis = MockRedis()
    
    with patch('app.core.ussd_session.get_redis', return_value=mock_redis):
        # Step 1: Initial consent
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": service_code,
            "text": ""
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("CON")
        assert "consent" in data["response"].lower()
        
        # Step 2: Accept consent (1=Yes)
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": service_code,
            "text": "1"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("CON")
        assert "language" in data["response"].lower() or "English" in data["response"]
        
        # Step 3: Select English
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": service_code,
            "text": "1*1"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("CON")
        assert "age" in data["response"].lower()
        
        # Step 4: Select age group (3 = 18-49)
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": service_code,
            "text": "1*1*3"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("CON")
        assert "gender" in data["response"].lower()
        
        # Step 5: Select gender (1 = Male)
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": service_code,
            "text": "1*1*3*1"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("CON")
        assert "fever" in data["response"].lower()
        
        # Step 6: No fever
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": service_code,
            "text": "1*1*3*1*2"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("CON")
        assert "headache" in data["response"].lower()
        
        # Step 7: No severe headache
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": service_code,
            "text": "1*1*3*1*2*2"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("CON")
        
        # Step 8: No danger signs
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": service_code,
            "text": "1*1*3*1*2*2*2"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("CON")
        assert "cough" in data["response"].lower()
        
        # Step 9: Yes to cough (still low risk)
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": service_code,
            "text": "1*1*3*1*2*2*2*1"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("CON")
        assert "low risk" in data["response"].lower() or "callback" in data["response"].lower()
        
        # Step 10: No callback
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": service_code,
            "text": "1*1*3*1*2*2*2*1*2"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("END")
        
        # Verify encounter was saved
        encounter = db.query(Encounter).filter(Encounter.channel == "USSD").first()
        assert encounter is not None
        assert encounter.risk_code == "LOW_RISK"
        assert encounter.consent_given is True


@pytest.mark.asyncio
async def test_ussd_emergency_path(client, db):
    """Test USSD flow for emergency case."""
    session_id = "test-session-emergency"
    phone = "+254712999999"
    
    mock_redis = MockRedis()
    
    with patch('app.core.ussd_session.get_redis', return_value=mock_redis):
        # Accept consent, English, age 18-49, male, yes fever, yes severe headache, YES danger sign
        # Step through to danger sign
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": ""})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1"})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1"})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1*3"})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1*3*1"})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1*3*1*1"})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1*3*1*1*1"})
        
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": "*123#",
            "text": "1*1*3*1*1*1*1"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("CON")
        
        # Continue to cough question
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": "*123#",
            "text": "1*1*3*1*1*1*1*2"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("CON")
        assert "emergency" in data["response"].lower()
        
        # Request callback
        response = client.post("/api/v1/ussd", json={
            "sessionId": session_id,
            "phoneNumber": phone,
            "serviceCode": "*123#",
            "text": "1*1*3*1*1*1*1*2*1"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("END")
        
        # Verify encounter and callback
        encounter = db.query(Encounter).filter(
            Encounter.channel == "USSD",
            Encounter.risk_code == "EMERGENCY"
        ).first()
        assert encounter is not None
        assert encounter.urgency == "critical"
        
        callback = db.query(Callback).filter(Callback.encounter_id == encounter.id).first()
        assert callback is not None
        assert callback.priority == "urgent"


@pytest.mark.asyncio
async def test_rate_limit_blocks_after_10(client):
    """Test that rate limiting blocks after 10 requests."""
    phone = "+254712888888"
    
    mock_redis = MockRedis()
    # Pre-set rate limit to exceeded
    mock_redis.storage[f"ussd:rate:{hash_msisdn(phone)}"] = "11"
    
    with patch('app.core.ussd_session.get_redis', return_value=mock_redis):
        response = client.post("/api/v1/ussd", json={
            "sessionId": "rate-limit-test",
            "phoneNumber": phone,
            "serviceCode": "*123#",
            "text": ""
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"].startswith("END")
        assert "limit" in data["response"].lower() or "tomorrow" in data["response"].lower()


def test_msisdn_is_hashed_on_encounter(client, db):
    """Test that MSISDN is hashed in database."""
    phone = "+254712777777"
    hashed = hash_msisdn(phone)
    
    mock_redis = MockRedis()
    
    with patch('app.core.ussd_session.get_redis', return_value=mock_redis):
        # Complete a minimal USSD flow
        session_id = "hash-test"
        
        # Fast path: consent, language, age, gender, all no symptoms, no callback
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": ""})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1"})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1"})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1*3"})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1*3*1"})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1*3*1*2"})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1*3*1*2*2"})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1*3*1*2*2*2"})
        client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1*3*1*2*2*2*2"})
        response = client.post("/api/v1/ussd", json={"sessionId": session_id, "phoneNumber": phone, "serviceCode": "*123#", "text": "1*1*3*1*2*2*2*2*2"})
        
        # Verify encounter has hashed MSISDN, not plain text
        encounter = db.query(Encounter).filter(Encounter.msisdn_hash == hashed).first()
        assert encounter is not None
        assert encounter.msisdn_hash == hashed
        # Ensure plain phone number is not stored
        assert encounter.patient_phone != phone or encounter.patient_phone is None


def test_callback_lifecycle_assign_complete(client, auth_headers, db):
    """Test callback assignment and completion lifecycle."""
    # Create an encounter and callback manually
    from app.core.ussd_utils import hash_msisdn
    
    encounter = Encounter(
        channel="USSD",
        msisdn_hash=hash_msisdn("+254712666666"),
        age_group="18-49",
        patient_gender="female",
        risk_code="MALARIA_SUSPECT",
        consent_given=True,
        status="pending",
        urgency="medium"
    )
    db.add(encounter)
    db.commit()
    db.refresh(encounter)
    
    callback = Callback(
        encounter_id=encounter.id,
        msisdn_hash=hash_msisdn("+254712666666"),
        priority="high",
        status="queued"
    )
    db.add(callback)
    db.commit()
    db.refresh(callback)
    
    # List callbacks
    response = client.get("/api/v1/callbacks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(c["id"] == callback.id for c in data)
    
    # Assign callback
    response = client.post(
        f"/api/v1/callbacks/{callback.id}/assign",
        json={"provider_id": 1},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["provider_id"] == 1
    assert data["assigned_at"] is not None
    
    # Complete callback
    response = client.post(
        f"/api/v1/callbacks/{callback.id}/complete",
        json={
            "outcome": "Patient advised to visit clinic",
            "notes": "Follow up in 3 days"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "done"
    assert data["outcome"] == "Patient advised to visit clinic"
    assert data["completed_at"] is not None
