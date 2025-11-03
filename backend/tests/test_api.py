import pytest
from fastapi import status


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"


def test_create_triage(client):
    """Test creating a triage encounter"""
    triage_data = {
        "patient_name": "John Doe",
        "patient_phone": "+1234567890",
        "patient_age": 30,
        "patient_gender": "male",
        "chief_complaint": "Fever and cough",
        "symptoms": "High fever, dry cough",
        "duration": "3 days",
        "medical_history": "None",
        "source": "web"
    }
    
    response = client.post("/api/v1/triage", json=triage_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["patient_name"] == "John Doe"
    assert data["status"] == "pending"
    assert "id" in data


def test_login_success(client, test_provider):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_user", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_provider):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_user", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_encounters_requires_auth(client):
    """Test that getting encounters requires authentication"""
    response = client.get("/api/v1/encounters")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_encounters_authenticated(client, auth_headers, db):
    """Test getting encounters with authentication"""
    # First create a triage
    triage_data = {
        "patient_name": "Jane Doe",
        "patient_phone": "+1234567890",
        "chief_complaint": "Headache",
        "source": "web"
    }
    client.post("/api/v1/triage", json=triage_data)
    
    # Then get encounters
    response = client.get("/api/v1/encounters", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_encounter_by_id(client, auth_headers):
    """Test getting a specific encounter"""
    # Create encounter
    triage_data = {
        "patient_name": "Bob Smith",
        "patient_phone": "+1234567890",
        "chief_complaint": "Chest pain",
        "source": "web"
    }
    create_response = client.post("/api/v1/triage", json=triage_data)
    encounter_id = create_response.json()["id"]
    
    # Get encounter
    response = client.get(f"/api/v1/encounters/{encounter_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == encounter_id
    assert data["patient_name"] == "Bob Smith"


def test_get_nonexistent_encounter(client, auth_headers):
    """Test getting a non-existent encounter"""
    response = client.get("/api/v1/encounters/99999", headers=auth_headers)
    assert response.status_code == 404


def test_update_encounter(client, auth_headers):
    """Test updating an encounter"""
    # Create encounter
    triage_data = {
        "patient_name": "Alice Brown",
        "patient_phone": "+1234567890",
        "chief_complaint": "Fever",
        "source": "web"
    }
    create_response = client.post("/api/v1/triage", json=triage_data)
    encounter_id = create_response.json()["id"]
    
    # Update encounter
    update_data = {
        "status": "in_progress",
        "urgency": "high",
        "notes": "Patient requires immediate attention"
    }
    response = client.put(
        f"/api/v1/encounters/{encounter_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["urgency"] == "high"
    assert data["notes"] == "Patient requires immediate attention"


def test_get_current_provider(client, auth_headers):
    """Test getting current provider info"""
    response = client.get("/api/v1/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_user"
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
