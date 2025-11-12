"""
User model
"""
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    """User model"""
    
    __tablename__ = "users"
    
    # Basic Info
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Profile
    avatar_url = Column(String(500), nullable=True)
    language = Column(String(10), default="de", nullable=False)
    timezone = Column(String(50), default="Europe/Berlin", nullable=False)
    
    # Status
    email_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Security
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships (will be added later)
    club_memberships = relationship("ClubMember", back_populates="user")
    # tournaments_created = relationship("Tournament", back_populates="creator")
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
