"""
Club schemas (Pydantic models for API)
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.club import VerificationStatus
from app.models.club_member import ClubRole


# Base Club Schema
class ClubBase(BaseModel):
    """Base club schema"""
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

    # Contact
    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default="Deutschland", max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)

    # Details
    founded_date: Optional[date] = None


# Create Club Schema
class ClubCreate(ClubBase):
    """Schema for creating a club"""
    pass


# Update Club Schema
class ClubUpdate(BaseModel):
    """Schema for updating a club"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    logo_url: Optional[str] = Field(None, max_length=500)
    banner_url: Optional[str] = Field(None, max_length=500)

    address: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=500)

    founded_date: Optional[date] = None


# Club Response Schema
class ClubResponse(ClubBase):
    """Schema for club response"""
    id: UUID
    slug: str
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    verification_status: str  # Use string directly instead of Enum
    verification_badge_date: Optional[date] = None
    member_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


# Club with Members Schema
class ClubWithMembers(ClubResponse):
    """Schema for club with member list"""
    members: List["ClubMemberResponse"] = []


# ClubMember Schemas
class ClubMemberBase(BaseModel):
    """Base club member schema"""
    role: str = "member"  # Use string directly
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)


class ClubMemberCreate(BaseModel):
    """Schema for adding a member to club"""
    user_id: UUID
    role: str = "member"
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)


class ClubMemberUpdate(BaseModel):
    """Schema for updating club member"""
    role: Optional[str] = None
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)


class ClubMemberResponse(ClubMemberBase):
    """Schema for club member response"""
    id: UUID
    club_id: UUID
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


# Club Member with User Info
class ClubMemberWithUser(ClubMemberResponse):
    """Schema for club member with user details"""
    user: "UserResponse"  # Import from user schemas


# Verification Request
class ClubVerificationRequest(BaseModel):
    """Schema for requesting club verification"""
    message: Optional[str] = Field(None, max_length=1000)
    documents: Optional[List[str]] = []  # URLs to uploaded documents


# Verification Decision (Admin only)
class ClubVerificationDecision(BaseModel):
    """Schema for admin verification decision"""
    status: str  # "pending", "verified", or "rejected"
    notes: Optional[str] = Field(None, max_length=1000)


# Import UserResponse for ClubMemberWithUser
from app.schemas.user import UserResponse

ClubMemberWithUser.model_rebuild()
ClubWithMembers.model_rebuild()