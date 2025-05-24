from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from uuid import uuid4

from app.db.database import Base

def generate_uuid():
    return str(uuid4())

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    BUSINESS_USER = "business_user"
    CONTENT_SPECIALIST = "content_specialist"

class BrandVoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    UNDER_REVIEW = "under_review"
    INACTIVE = "inactive"

class TaskStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    CLOSED = "closed"

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    users = relationship("User", back_populates="tenant")
    brand_voices = relationship("BrandVoice", back_populates="tenant")
    content_projects = relationship("ContentProject", back_populates="tenant")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"))
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    assigned_tasks = relationship("Task", back_populates="assignee")
    created_brand_voices = relationship("BrandVoice", back_populates="created_by")

class BrandVoice(Base):
    __tablename__ = "brand_voices"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    version = Column(Integer, default=1)
    voice_metadata = Column(JSON)  # Stores personality, tonality, etc.
    dos = Column(Text)  # Do's guidelines
    donts = Column(Text)  # Don'ts guidelines
    source_content = Column(Text, nullable=True)  # Original content used to generate the brand voice
    generation_metadata = Column(JSON, nullable=True)  # Metadata about the generation process
    status = Column(Enum(BrandVoiceStatus), default=BrandVoiceStatus.DRAFT)
    created_by_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))

    # Relationships
    tenant = relationship("Tenant", back_populates="brand_voices")
    created_by = relationship("User", back_populates="created_brand_voices")
    content_projects = relationship("ContentProject", back_populates="brand_voice")
    versions = relationship("BrandVoiceVersion", back_populates="brand_voice", 
                          order_by="desc(BrandVoiceVersion.version_number)", 
                          cascade="all, delete-orphan")

class BrandVoiceVersion(Base):
    __tablename__ = "brand_voice_versions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    brand_voice_id = Column(String, ForeignKey("brand_voices.id", ondelete="CASCADE"))
    version_number = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(String, ForeignKey("users.id"))
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Version data (snapshot of brand voice at the time of version creation)
    name = Column(String, nullable=False)
    description = Column(Text)
    voice_metadata = Column(JSON, nullable=True)
    dos = Column(Text)
    donts = Column(Text)
    source_content = Column(Text, nullable=True)  # Original content used to generate the brand voice
    generation_metadata = Column(JSON, nullable=True)  # Metadata about the generation process
    status = Column(Enum(BrandVoiceStatus), default=BrandVoiceStatus.DRAFT)
    
    # Relationships
    brand_voice = relationship("BrandVoice", back_populates="versions")
    created_by = relationship("User")

class ContentProject(Base):
    __tablename__ = "content_projects"

    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    schema_def = Column(JSON)  # JSON schema for content validation
    voice_id = Column(String, ForeignKey("brand_voices.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="content_projects")
    brand_voice = relationship("BrandVoice", back_populates="content_projects")
    tasks = relationship("Task", back_populates="content_project")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, ForeignKey("content_projects.id"))
    type = Column(String, nullable=False)  # translate, generate, review
    input_data = Column(JSON)  # Input content for the task
    output_data = Column(JSON)  # Generated content
    assignee_id = Column(String, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.OPEN)
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    closed_at = Column(DateTime(timezone=True))

    # Relationships
    content_project = relationship("ContentProject", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")
    feedback = relationship("Feedback", back_populates="task")
    audit_logs = relationship("AuditLog", back_populates="task")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=generate_uuid)
    task_id = Column(String, ForeignKey("tasks.id"))
    rating = Column(Integer)  # 1-5 rating
    comments = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="feedback")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    entity = Column(String, nullable=False)  # The entity being audited
    action = Column(String, nullable=False)  # The action performed
    user_id = Column(String, ForeignKey("users.id"))
    task_id = Column(String, ForeignKey("tasks.id"), nullable=True)
    details = Column(JSON)  # Additional audit details
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    task = relationship("Task", back_populates="audit_logs")
