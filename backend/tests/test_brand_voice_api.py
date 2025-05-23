"""
Tests for the Brand Voice API routes.

These tests verify that the brand voice API endpoints work correctly,
including authorization, CRUD operations, and versioning.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.main import app
from app.models.models import BrandVoice, BrandVoiceVersion, User, UserRole
from app.db.database import get_db

# Test client for FastAPI 0.95.1
client = TestClient(app)

# Mock authentication token
MOCK_ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRlbmFudF9pZCI6InRlbmFudC0xMjMiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDc5NzcxNzV9.iRGPvHgK3GaH3ZDwgbfpZBgOhCCYe7pLRl3c1YROj6c"
MOCK_USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTQ1NiIsInRlbmFudF9pZCI6InRlbmFudC00NTYiLCJyb2xlIjoidXNlciIsImV4cCI6MTc0Nzk3NzE3NX0.2kjdHmGpwrpfARl5eQnDrxIz0VeBcPP9EXYqJu4OlCk"

# Mock database session
@pytest.fixture
def db_session(monkeypatch):
    """Create a mock database session for testing."""
    # This would be replaced with a proper test database in a real implementation
    from app.db.database import SessionLocal
    db = SessionLocal()
    
    def mock_get_db():
        try:
            yield db
        finally:
            db.close()
    
    monkeypatch.setattr("app.api.routes.brand_voice.get_db", mock_get_db)
    return db

# Test cases
def test_get_all_brand_voices(db_session):
    """Test that admin users can get all brand voices."""
    response = client.get(
        "/api/voices/all/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_brand_voice_by_id(db_session):
    """Test getting a specific brand voice by ID."""
    # First create a brand voice to test with
    create_response = client.post(
        "/api/voices/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"},
        json={
            "name": "Test Voice",
            "description": "A test brand voice",
            "voice_metadata": {"personality": "Bold", "tonality": "Professional"},
            "dos": "Use active voice",
            "donts": "Avoid jargon"
        }
    )
    assert create_response.status_code == 200
    voice_id = create_response.json()["id"]
    
    # Now get the brand voice by ID
    response = client.get(
        f"/api/voices/{voice_id}/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"}
    )
    assert response.status_code == 200
    assert response.json()["id"] == voice_id
    assert response.json()["name"] == "Test Voice"

def test_update_brand_voice(db_session):
    """Test updating a brand voice."""
    # First create a brand voice to test with
    create_response = client.post(
        "/api/voices/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"},
        json={
            "name": "Original Voice",
            "description": "Original description",
            "voice_metadata": {"personality": "Original", "tonality": "Original"},
            "dos": "Original dos",
            "donts": "Original donts"
        }
    )
    assert create_response.status_code == 200
    voice_id = create_response.json()["id"]
    
    # Now update the brand voice
    update_response = client.put(
        f"/api/voices/{voice_id}",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"},
        json={
            "name": "Updated Voice",
            "description": "Updated description"
        }
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Voice"
    assert update_response.json()["description"] == "Updated description"
    
    # Verify that a new version was created
    versions_response = client.get(
        f"/api/voices/{voice_id}/versions/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"}
    )
    assert versions_response.status_code == 200
    assert len(versions_response.json()) > 0

def test_authorization(db_session):
    """Test that users can only access brand voices from their tenant."""
    # Create a brand voice as admin
    create_response = client.post(
        "/api/voices/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"},
        json={
            "name": "Admin Voice",
            "description": "Admin tenant voice",
            "voice_metadata": {"personality": "Admin", "tonality": "Admin"},
            "dos": "Admin dos",
            "donts": "Admin donts"
        }
    )
    assert create_response.status_code == 200
    voice_id = create_response.json()["id"]
    
    # Try to access as a regular user from a different tenant
    response = client.get(
        f"/api/voices/{voice_id}/",
        headers={"Authorization": f"Bearer {MOCK_USER_TOKEN}"}
    )
    assert response.status_code == 403  # Forbidden
    
    # Admin should still be able to access
    admin_response = client.get(
        f"/api/voices/{voice_id}/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"}
    )
    assert admin_response.status_code == 200

def test_brand_voice_versions(db_session):
    """Test brand voice versioning functionality."""
    # Create a brand voice
    create_response = client.post(
        "/api/voices/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"},
        json={
            "name": "Version Test Voice",
            "description": "Testing versions",
            "voice_metadata": {"personality": "V1", "tonality": "V1"},
            "dos": "V1 dos",
            "donts": "V1 donts"
        }
    )
    assert create_response.status_code == 200
    voice_id = create_response.json()["id"]
    
    # Make multiple updates to create versions
    for i in range(2, 4):
        update_response = client.put(
            f"/api/voices/{voice_id}",
            headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"},
            json={
                "name": f"Version {i} Voice",
                "description": f"Testing version {i}",
                "voice_metadata": {"personality": f"V{i}", "tonality": f"V{i}"},
                "dos": f"V{i} dos",
                "donts": f"V{i} donts"
            }
        )
        assert update_response.status_code == 200
    
    # Get all versions
    versions_response = client.get(
        f"/api/voices/{voice_id}/versions/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"}
    )
    assert versions_response.status_code == 200
    versions = versions_response.json()
    
    # Should have at least 2 versions (original + updates)
    assert len(versions) >= 2
    
    # Try restoring a previous version
    if len(versions) > 0:
        version_to_restore = versions[0]["version_number"]
        restore_response = client.post(
            f"/api/voices/{voice_id}/versions/{version_to_restore}/restore/",
            headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"}
        )
        assert restore_response.status_code == 200
        
        # Verify that a new version was created after restoration
        updated_versions_response = client.get(
            f"/api/voices/{voice_id}/versions/",
            headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"}
        )
        assert updated_versions_response.status_code == 200
        updated_versions = updated_versions_response.json()
        assert len(updated_versions) > len(versions)
