"""
Tests for the Brand Voice Version Comparison functionality.

These tests verify that the version comparison features work correctly,
including retrieving multiple versions and comparing their differences.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.models import BrandVoice, BrandVoiceVersion, User, UserRole
from app.db.database import get_db

# Test client for FastAPI
client = TestClient(app)

# Mock authentication token
MOCK_ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRlbmFudF9pZCI6InRlbmFudC0xMjMiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDc5NzcxNzV9.iRGPvHgK3GaH3ZDwgbfpZBgOhCCYe7pLRl3c1YROj6c"

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

def test_create_multiple_versions(db_session):
    """Test creating multiple versions of a brand voice."""
    # Create initial brand voice
    create_response = client.post(
        "/api/voices/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"},
        json={
            "name": "Comparison Test Voice",
            "description": "Initial version",
            "voice_metadata": {"personality": "Professional", "tonality": "Formal"},
            "dos": "Be concise",
            "donts": "Avoid jargon",
            "status": "published"
        }
    )
    assert create_response.status_code == 200
    voice_id = create_response.json()["id"]
    
    # Create second version
    update_response = client.put(
        f"/api/voices/{voice_id}",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"},
        json={
            "name": "Updated Voice",
            "description": "Initial version",  # Unchanged
            "voice_metadata": {"personality": "Friendly", "tonality": "Casual"},
            "dos": "Be concise\nUse simple language",
            "donts": "Avoid jargon",  # Unchanged
            "status": "draft"
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
    
    # Should have exactly 2 versions
    assert len(versions) == 2
    
    # Verify that the versions have different content
    assert versions[0]["name"] != versions[1]["name"]
    assert versions[0]["voice_metadata"]["personality"] != versions[1]["voice_metadata"]["personality"]
    assert versions[0]["voice_metadata"]["tonality"] != versions[1]["voice_metadata"]["tonality"]
    assert versions[0]["dos"] != versions[1]["dos"]
    assert versions[0]["status"] != versions[1]["status"]
    
    # Verify that some content remained the same
    assert versions[0]["description"] == versions[1]["description"]
    assert versions[0]["donts"] == versions[1]["donts"]

def test_restore_version(db_session):
    """Test restoring a previous version of a brand voice."""
    # Create initial brand voice
    create_response = client.post(
        "/api/voices/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"},
        json={
            "name": "Restore Test Voice",
            "description": "Initial version",
            "voice_metadata": {"personality": "V1", "tonality": "V1"},
            "dos": "V1 dos",
            "donts": "V1 donts",
            "status": "published"
        }
    )
    assert create_response.status_code == 200
    voice_id = create_response.json()["id"]
    
    # Create second version
    update_response = client.put(
        f"/api/voices/{voice_id}",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"},
        json={
            "name": "V2 Voice",
            "description": "V2 description",
            "voice_metadata": {"personality": "V2", "tonality": "V2"},
            "dos": "V2 dos",
            "donts": "V2 donts",
            "status": "draft"
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
    
    # Should have exactly 2 versions
    assert len(versions) == 2
    
    # Restore the first version
    version_to_restore = versions[1]["version_number"]  # The first created version
    restore_response = client.post(
        f"/api/voices/{voice_id}/versions/{version_to_restore}/restore/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"}
    )
    assert restore_response.status_code == 200
    
    # Get the current brand voice
    current_voice_response = client.get(
        f"/api/voices/{voice_id}/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"}
    )
    assert current_voice_response.status_code == 200
    current_voice = current_voice_response.json()
    
    # Verify that the current voice matches the restored version
    assert current_voice["name"] == "Restore Test Voice"
    assert current_voice["description"] == "Initial version"
    assert current_voice["voice_metadata"]["personality"] == "V1"
    assert current_voice["voice_metadata"]["tonality"] == "V1"
    assert current_voice["dos"] == "V1 dos"
    assert current_voice["donts"] == "V1 donts"
    
    # Get all versions again
    updated_versions_response = client.get(
        f"/api/voices/{voice_id}/versions/",
        headers={"Authorization": f"Bearer {MOCK_ADMIN_TOKEN}"}
    )
    assert updated_versions_response.status_code == 200
    updated_versions = updated_versions_response.json()
    
    # Should have 3 versions now (original + update + restore)
    assert len(updated_versions) == 3
