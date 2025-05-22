"""
Script to add development user and tenant to the database
This ensures the user in the development token exists in the database
"""
from app.db.database import SessionLocal, Base, engine
from app.models.models import User, Tenant, UserRole
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

# Create password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create a database session
db = SessionLocal()

try:
    # Check if tenant exists
    tenant = db.query(Tenant).filter(Tenant.id == "tenant-123").first()
    
    if not tenant:
        print("Creating tenant-123...")
        tenant = Tenant(
            id="tenant-123",
            name="Development Tenant",
            is_active=True
        )
        db.add(tenant)
        db.commit()
        print("Tenant created successfully")
    else:
        print("Tenant tenant-123 already exists")
    
    # Check if user exists
    user = db.query(User).filter(User.id == "user-123").first()
    
    if not user:
        print("Creating user-123...")
        user = User(
            id="user-123",
            tenant_id="tenant-123",
            email="dev@example.com",
            hashed_password=pwd_context.hash("password123"),
            full_name="Development User",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(user)
        db.commit()
        print("User created successfully")
    else:
        print("User user-123 already exists")
        
except IntegrityError as e:
    db.rollback()
    print(f"Error: {e}")
except Exception as e:
    db.rollback()
    print(f"Unexpected error: {e}")
finally:
    db.close()
    print("Database session closed")
