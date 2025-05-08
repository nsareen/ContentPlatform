import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal, engine
from app.models.models import Base, Tenant, User, BrandVoice, ContentProject, UserRole, BrandVoiceStatus
from app.core.auth import get_password_hash

def seed_data():
    db = SessionLocal()
    try:
        # Create a tenant
        tenant = Tenant(
            name="Laureate Fashion",
            config={"theme": "default"},
            is_active=True
        )
        db.add(tenant)
        db.flush()  # Flush to get the tenant ID
        
        # Create an admin user
        admin_user = User(
            tenant_id=tenant.id,
            email="admin@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        
        # Create a business user
        business_user = User(
            tenant_id=tenant.id,
            email="business@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Business User",
            role=UserRole.BUSINESS_USER,
            is_active=True
        )
        db.add(business_user)
        
        # Create a content specialist
        content_specialist = User(
            tenant_id=tenant.id,
            email="specialist@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Content Specialist",
            role=UserRole.CONTENT_SPECIALIST,
            is_active=True
        )
        db.add(content_specialist)
        db.flush()  # Flush to get the user IDs
        
        # Create a brand voice
        brand_voice = BrandVoice(
            tenant_id=tenant.id,
            name="Laureate Asia-Pacific",
            description="Bold, expressive, and effortlessly stylish",
            version=1,
            voice_metadata={
                "personality": "Bold, expressive, and effortlessly stylish",
                "tonality": "Confident, energetic, sophisticated"
            },
            dos="Maintain an Empowering and Confident Tone\nKeep the Language Fun and Playful\nAppeal to the Desire for Convenience and Effortlessness",
            donts="Don't Overload with Technical Details\nAvoid Formal, Stiff Language\nSteer Clear of Overused Beauty Clichés",
            status=BrandVoiceStatus.PUBLISHED,
            created_by_id=business_user.id,
            published_at=datetime.now()
        )
        db.add(brand_voice)
        db.flush()  # Flush to get the brand voice ID
        
        # Create a content project
        content_project = ContentProject(
            tenant_id=tenant.id,
            name="Summer Collection Descriptions",
            description="Product descriptions for the summer collection",
            schema_def={
                "type": "object",
                "properties": {
                    "product_name": {"type": "string"},
                    "product_type": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["product_name", "product_type"]
            },
            voice_id=brand_voice.id
        )
        db.add(content_project)
        
        # Commit all changes
        db.commit()
        print("Seed data created successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating seed data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
