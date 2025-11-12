"""
Club model - Vereine/Sportvereine
"""
from sqlalchemy import Column, String, Boolean, Date, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from app.models.base import BaseModel


class VerificationStatus(str, Enum):
    """Verification status for clubs"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Club(BaseModel):
    """Club/Sportverein model"""

    __tablename__ = "clubs"

    # Basic Info
    name = Column(String(200), unique=True, nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(String(2000), nullable=True)

    # Branding
    logo_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)

    # Contact Info
    address = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), default="Deutschland", nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)

    # Verification
    verification_status = Column(
        SQLEnum(VerificationStatus, name='verification_status_enum', values_callable=lambda x: [e.value for e in x]),
        default=VerificationStatus.PENDING.value,
        nullable=False,
        server_default='pending'
    )
    verification_badge_date = Column(Date, nullable=True)
    verification_notes = Column(String(1000), nullable=True)

    # Club Details
    founded_date = Column(Date, nullable=True)
    member_count = Column(Integer, default=0, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    members = relationship(
        "ClubMember",
        back_populates="club",
        cascade="all, delete-orphan"
    )
    tournaments = relationship("Tournament", back_populates="club", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Club {self.name}>"

    @property
    def is_verified(self) -> bool:
        """Check if club is verified"""
        return self.verification_status == VerificationStatus.VERIFIED