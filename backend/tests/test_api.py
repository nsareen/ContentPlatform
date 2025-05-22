"""
Test suite for the Content Platform API
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.database import Base, get_db
from app.models.models import Tenant, User, BrandVoice, BrandVoiceVersion, BrandVoiceStatus

# Create test database
TEST_DATABASE_URL = "sqlite:///./test_sql_app.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test data
test_tenant_id = "tenant-test-123"
test_user_id = "user-test-123"
test_brand_voice_id = "brand-voice-test-123"

# Setup test database
@pytest.fixture(scope="module")
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create test data
    db = TestingSessionLocal()
    
    # Create test tenant
    tenant = Tenant(
        id=test_tenant_id,
        name="Test Tenant",
        is_active=True
    )
    db.add(tenant)
    
    # Create test user
    user = User(
        id=test_user_id,
        tenant_id=test_tenant_id,
        email="test@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        full_name="Test User",
        role="admin",
        is_active=True
    )
    db.add(user)
    
    # Create test brand voice
    brand_voice = BrandVoice(
        id=test_brand_voice_id,
        tenant_id=test_tenant_id,
        name="Test Brand Voice",
        description="Test description",
        version=1,
        voice_metadata={"personality": "Bold", "tonality": "Confident"},
        dos="Do this",
        donts="Don't do that",
        status=BrandVoiceStatus.DRAFT,
        created_by_id=test_user_id
    )
    db.add(brand_voice)
    
    db.commit()
    db.close()
    
    # Override the get_db dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    client = TestClient(app)
    
    yield client
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

# Test authentication
def test_dev_token(test_db):
    """Test that the development token endpoint returns a valid token"""
    response = test_db.get("/api/dev-token")
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"

# Test brand voice endpoints
def test_get_brand_voices(test_db):
    """Test that the get brand voices endpoint returns a list of brand voices"""
    # Get dev token
    token_response = test_db.get("/api/dev-token")
    token = token_response.json()["access_token"]
    
    # Get brand voices
    response = test_db.get(
        "/api/voices/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == test_brand_voice_id

def test_get_brand_voice(test_db):
    """Test that the get brand voice endpoint returns a brand voice"""
    # Get dev token
    token_response = test_db.get("/api/dev-token")
    token = token_response.json()["access_token"]
    
    # Get brand voice
    response = test_db.get(
        f"/api/voices/{test_brand_voice_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == test_brand_voice_id
    assert response.json()["name"] == "Test Brand Voice"

def test_create_brand_voice(test_db):
    """Test that the create brand voice endpoint creates a brand voice"""
    # Get dev token
    token_response = test_db.get("/api/dev-token")
    token = token_response.json()["access_token"]
    
    # Create brand voice data
    brand_voice_data = {
        "tenant_id": test_tenant_id,
        "name": "New Test Brand Voice",
        "description": "New test description",
        "voice_metadata": {
            "personality": "Creative",
            "tonality": "Friendly"
        },
        "dos": "Do this new thing",
        "donts": "Don't do that new thing"
    }
    
    # Create brand voice
    response = test_db.post(
        "/api/voices/",
        headers={"Authorization": f"Bearer {token}"},
        json=brand_voice_data
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "New Test Brand Voice"
    assert response.json()["status"] == "draft"
    
    # Verify brand voice was created
    new_id = response.json()["id"]
    get_response = test_db.get(
        f"/api/voices/{new_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "New Test Brand Voice"

def test_update_brand_voice(test_db):
    """Test that the update brand voice endpoint updates a brand voice"""
    # Get dev token
    token_response = test_db.get("/api/dev-token")
    token = token_response.json()["access_token"]
    
    # Update brand voice data
    update_data = {
        "name": "Updated Test Brand Voice",
        "description": "Updated test description",
        "voice_metadata": {
            "personality": "Updated Bold",
            "tonality": "Updated Confident"
        }
    }
    
    # Update brand voice
    response = test_db.put(
        f"/api/voices/{test_brand_voice_id}",
        headers={"Authorization": f"Bearer {token}"},
        json=update_data
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Test Brand Voice"
    assert response.json()["description"] == "Updated test description"
    
    # Verify brand voice was updated
    get_response = test_db.get(
        f"/api/voices/{test_brand_voice_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Updated Test Brand Voice"

def test_publish_brand_voice(test_db):
    """Test that the publish brand voice endpoint publishes a brand voice"""
    # Get dev token
    token_response = test_db.get("/api/dev-token")
    token = token_response.json()["access_token"]
    
    # Publish brand voice
    update_data = {
        "status": "published"
    }
    
    response = test_db.put(
        f"/api/voices/{test_brand_voice_id}",
        headers={"Authorization": f"Bearer {token}"},
        json=update_data
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "published"
    
    # Verify brand voice was published
    get_response = test_db.get(
        f"/api/voices/{test_brand_voice_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "published"

def test_get_brand_voice_versions(test_db):
    """Test that the get brand voice versions endpoint returns versions"""
    # Get dev token
    token_response = test_db.get("/api/dev-token")
    token = token_response.json()["access_token"]
    
    # Get brand voice versions
    response = test_db.get(
        f"/api/voices/{test_brand_voice_id}/versions",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # There should be at least one version after publishing
    assert len(response.json()) > 0

def test_delete_brand_voice(test_db):
    """Test that the delete brand voice endpoint deletes a brand voice"""
    # Get dev token
    token_response = test_db.get("/api/dev-token")
    token = token_response.json()["access_token"]
    
    # Create a brand voice to delete
    brand_voice_data = {
        "tenant_id": test_tenant_id,
        "name": "Brand Voice to Delete",
        "description": "This will be deleted"
    }
    
    create_response = test_db.post(
        "/api/voices/",
        headers={"Authorization": f"Bearer {token}"},
        json=brand_voice_data
    )
    
    delete_id = create_response.json()["id"]
    
    # Delete brand voice
    response = test_db.delete(
        f"/api/voices/{delete_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    
    # Verify brand voice was deleted
    get_response = test_db.get(
        f"/api/voices/{delete_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert get_response.status_code == 404
