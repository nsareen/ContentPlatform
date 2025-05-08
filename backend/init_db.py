"""
Initialize the database and seed it with test data.
"""

import os
import sys
from datetime import datetime
from passlib.context import CryptContext

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import engine, SessionLocal, Base
from app.models.models import User, Tenant, BrandVoice, UserRole, BrandVoiceStatus

# Create password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    """Initialize the database by creating all tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

def seed_db():
    """Seed the database with test data."""
    print("Seeding database with test data...")
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(User).first():
        print("Database already has data, skipping seeding.")
        db.close()
        return
    
    try:
        # Create test tenant
        tenant = Tenant(
            id="tenant-123",
            name="Test Tenant",
            domain="example.com",
            created_at=datetime.now()
        )
        db.add(tenant)
        db.flush()  # Flush to get the tenant ID
        
        # Create test admin user
        admin_user = User(
            id="user-123",
            email="admin@example.com",
            hashed_password=pwd_context.hash("password123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            tenant_id=tenant.id,
            is_active=True,
            created_at=datetime.now()
        )
        db.add(admin_user)
        db.flush()  # Flush to get the user ID
        
        # Create test brand voices
        brand_voice1 = BrandVoice(
            id="bv-123",
            name="Laureate Asia-Pacific",
            description="Bold, expressive, and effortlessly stylish",
            status=BrandVoiceStatus.PUBLISHED,
            version=1,
            tenant_id=tenant.id,
            created_by_id=admin_user.id,
            created_at=datetime.now(),
            voice_metadata={
                "personality": "Bold, expressive, and effortlessly stylish",
                "tonality": "Confident, energetic, sophisticated"
            },
            dos="Maintain an Empowering and Confident Tone\nKeep the Language Fun and Playful\nAppeal to the Desire for Convenience and Effortlessness",
            donts="Don't Overload with Technical Details\nAvoid Formal, Stiff Language\nSteer Clear of Overused Beauty Clichés"
        )
        db.add(brand_voice1)
        
        brand_voice2 = BrandVoice(
            id="bv-456",
            name="TechVision Pro",
            description="Clear, authoritative, and forward-thinking",
            status=BrandVoiceStatus.DRAFT,
            version=2,
            tenant_id=tenant.id,
            created_by_id=admin_user.id,
            created_at=datetime.now(),
            voice_metadata={
                "personality": "Authoritative, innovative, precise",
                "tonality": "Professional, clear, forward-thinking"
            },
            dos="Use Clear, Precise Language\nIncorporate Technical Terms Appropriately\nMaintain a Forward-Thinking Perspective",
            donts="Avoid Overly Casual Language\nDon't Use Jargon Without Context\nAvoid Hyperbole and Exaggeration"
        )
        db.add(brand_voice2)
        
        # Commit the changes
        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    seed_db()
