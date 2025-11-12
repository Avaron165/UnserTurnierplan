"""
Tournament schemas (Pydantic models for API)
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, validator


# Base Tournament Schema
class TournamentBase(BaseModel):
    """Base tournament schema"""
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    
    # Department/Abteilung (e.g. "Fußball", "Basketball")
    department: Optional[str] = Field(None, max_length=100)
    
    # Classification
    sport_type: str = "football"
    tournament_type: str = "knockout"
    
    # Dates
    start_date: datetime
    end_date: datetime
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    
    # Location
    location: Optional[str] = Field(None, max_length=300)
    venue_name: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=300)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(default="DE", max_length=2)
    
    # Participant Settings
    participant_type: str = "team"
    min_participants: int = Field(default=2, ge=2)
    max_participants: int = Field(..., ge=2)
    
    # Details
    rules: Optional[str] = None
    prize_info: Optional[str] = None
    entry_fee: Optional[Decimal] = Field(None, ge=0)
    
    # Visibility
    is_public: bool = True
    
    # Contact
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    
    @validator("end_date")
    def validate_end_date(cls, v, values):
        """Ensure end_date is after start_date"""
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v
    
    @validator("registration_end")
    def validate_registration_end(cls, v, values):
        """Ensure registration_end is before start_date"""
        if v and "start_date" in values and v > values["start_date"]:
            raise ValueError("registration_end must be before start_date")
        return v


# Create Tournament Schema
class TournamentCreate(TournamentBase):
    """Schema for creating a tournament"""
    club_id: UUID  # Must specify hosting club


# Update Tournament Schema
class TournamentUpdate(BaseModel):
    """Schema for updating a tournament"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    banner_url: Optional[str] = Field(None, max_length=500)
    
    department: Optional[str] = Field(None, max_length=100)
    sport_type: Optional[str] = None
    tournament_type: Optional[str] = None
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    
    location: Optional[str] = Field(None, max_length=300)
    venue_name: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = Field(None, max_length=300)
    city: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=2)
    
    participant_type: Optional[str] = None
    min_participants: Optional[int] = Field(None, ge=2)
    max_participants: Optional[int] = Field(None, ge=2)
    
    rules: Optional[str] = None
    prize_info: Optional[str] = None
    entry_fee: Optional[Decimal] = Field(None, ge=0)
    
    is_public: Optional[bool] = None
    
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)


# Tournament Response Schema
class TournamentResponse(TournamentBase):
    """Schema for tournament response"""
    id: UUID
    club_id: UUID
    created_by: Optional[UUID]
    slug: str
    banner_url: Optional[str] = None
    status: str
    current_participants: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed properties
    is_registration_open: bool = False
    is_full: bool = False
    can_register: bool = False

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


# Tournament Detail Schema (with relationships)
class TournamentDetail(TournamentResponse):
    """Schema for detailed tournament view with related data"""
    club: "ClubResponse"
    participants_preview: List["TournamentParticipantResponse"] = []


# Tournament List Item (lighter version for lists)
class TournamentListItem(BaseModel):
    """Lightweight schema for tournament lists"""
    id: UUID
    name: str
    slug: str
    department: Optional[str]
    sport_type: str
    tournament_type: str
    status: str
    start_date: datetime
    end_date: datetime
    location: Optional[str]
    city: Optional[str]
    current_participants: int
    max_participants: int
    banner_url: Optional[str]
    is_public: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


# Tournament Status Update
class TournamentStatusUpdate(BaseModel):
    """Schema for updating tournament status"""
    status: str  # "draft", "published", "registration_open", "active", "completed", "cancelled"
    notes: Optional[str] = Field(None, max_length=500)


# Tournament Filters
class TournamentFilters(BaseModel):
    """Schema for filtering tournaments"""
    sport_type: Optional[str] = None
    tournament_type: Optional[str] = None
    status: Optional[str] = None
    city: Optional[str] = None
    min_start_date: Optional[datetime] = None
    max_start_date: Optional[datetime] = None
    is_public: Optional[bool] = None
    club_id: Optional[UUID] = None


# ==================== TOURNAMENT PARTICIPANT SCHEMAS ====================

# Base Participant Schema
class TournamentParticipantBase(BaseModel):
    """Base tournament participant schema"""
    participant_name: str = Field(..., min_length=2, max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    player_list: Optional[str] = None
    notes: Optional[str] = None


# Create Participant Schema
class TournamentParticipantCreate(TournamentParticipantBase):
    """Schema for registering to a tournament"""
    participant_club_id: Optional[UUID] = None
    participant_user_id: Optional[UUID] = None
    
    @validator("participant_club_id")
    def validate_participant_id(cls, v, values):
        """Ensure either club_id or user_id is provided"""
        if not v and not values.get("participant_user_id"):
            raise ValueError("Either participant_club_id or participant_user_id must be provided")
        return v


# Update Participant Schema
class TournamentParticipantUpdate(BaseModel):
    """Schema for updating participant registration"""
    participant_name: Optional[str] = Field(None, min_length=2, max_length=200)
    display_name: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = None
    payment_status: Optional[str] = None
    seed: Optional[int] = Field(None, ge=1)
    player_list: Optional[str] = None
    notes: Optional[str] = None


# Participant Response Schema
class TournamentParticipantResponse(TournamentParticipantBase):
    """Schema for participant response"""
    id: UUID
    tournament_id: UUID
    participant_club_id: Optional[UUID]
    participant_user_id: Optional[UUID]
    registered_by: Optional[UUID]
    registration_date: datetime
    status: str
    payment_status: str
    payment_amount: Optional[Decimal]
    payment_date: Optional[datetime]
    seed: Optional[int]
    created_at: datetime
    
    # Computed
    participant_type: str = "unknown"
    is_confirmed: bool = False
    is_paid: bool = False

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


# Participant with Details
class TournamentParticipantDetail(TournamentParticipantResponse):
    """Schema for participant with related data"""
    tournament: TournamentListItem
    participant_club: Optional["ClubResponse"] = None
    participant_user: Optional["UserResponse"] = None


# Participant Status Update
class ParticipantStatusUpdate(BaseModel):
    """Schema for updating participant status"""
    status: str  # "pending", "confirmed", "cancelled", "waitlist"
    notes: Optional[str] = Field(None, max_length=500)


# Payment Update
class ParticipantPaymentUpdate(BaseModel):
    """Schema for updating payment information"""
    payment_status: str  # "not_required", "pending", "paid", "refunded"
    payment_amount: Optional[Decimal] = Field(None, ge=0)
    payment_reference: Optional[str] = Field(None, max_length=100)


# Import related schemas
from app.schemas.club import ClubResponse
from app.schemas.user import UserResponse

# Rebuild models to resolve forward references
TournamentDetail.model_rebuild()
TournamentParticipantDetail.model_rebuild()
