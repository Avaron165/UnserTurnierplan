"""
Tournament model for UnserTurnierplan.

This module defines the Tournament model which represents sports tournaments
organized by clubs. Includes tournament types, status management, and
participant settings.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column, String, Text, DateTime, Date, Integer, Boolean, 
    Numeric, ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class TournamentType(str, Enum):
    """Tournament format types."""
    KNOCKOUT = "knockout"  # Single/Double Elimination
    ROUND_ROBIN = "round_robin"  # Everyone plays everyone
    GROUP_STAGE = "group_stage"  # Groups + Knockout
    SWISS = "swiss"  # Swiss system (chess-style)
    CUSTOM = "custom"  # Custom format


class TournamentStatus(str, Enum):
    """Tournament lifecycle status."""
    DRAFT = "draft"  # Being created
    PUBLISHED = "published"  # Visible but registration closed
    REGISTRATION_OPEN = "registration_open"  # Registration active
    ACTIVE = "active"  # Tournament in progress
    COMPLETED = "completed"  # Tournament finished
    CANCELLED = "cancelled"  # Tournament cancelled


class SportType(str, Enum):
    """Supported sport types."""
    FOOTBALL = "football"  # ⚽ Fußball
    BASKETBALL = "basketball"  # 🏀
    VOLLEYBALL = "volleyball"  # 🏐
    HANDBALL = "handball"  # 🤾
    HOCKEY = "hockey"  # 🏑
    TENNIS = "tennis"  # 🎾
    TABLE_TENNIS = "table_tennis"  # 🏓
    BADMINTON = "badminton"  # 🏸
    ESPORTS = "esports"  # 🎮
    OTHER = "other"  # Other sports


class ParticipantType(str, Enum):
    """Type of tournament participants."""
    TEAM = "team"  # Team-based tournament
    INDIVIDUAL = "individual"  # Individual players


class Tournament(BaseModel):
    """
    Tournament model.
    
    Represents a sports tournament organized by a club. Contains all
    tournament metadata, settings, and lifecycle status.
    
    Relationships:
        - club: The hosting club
        - created_by: The user who created the tournament
        - participants: Tournament participants (teams/individuals)
    """
    
    __tablename__ = "tournaments"
    
    # Foreign Keys (id, created_at, updated_at inherited from BaseModel)
    
    # Foreign Keys
    club_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_by = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Basic Information
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text)
    banner_url = Column(String(500))
    
    # Department/Abteilung (e.g. "Fußball", "Basketball")
    # Allows clubs with multiple departments to organize tournaments per department
    department = Column(String(100), nullable=True, index=True)
    
    # Tournament Classification
    sport_type = Column(
        SQLEnum(
            SportType,
            name='sport_type_enum',
            values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=SportType.FOOTBALL.value
    )
    tournament_type = Column(
        SQLEnum(
            TournamentType,
            name='tournament_type_enum',
            values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=TournamentType.KNOCKOUT.value
    )
    
    # Status Management
    status = Column(
        SQLEnum(
            TournamentStatus,
            name='tournament_status_enum',
            values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=TournamentStatus.DRAFT.value,
        index=True
    )
    
    # Dates & Times
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    registration_start = Column(DateTime)
    registration_end = Column(DateTime)
    
    # Location
    location = Column(String(300))
    venue_name = Column(String(200))
    address = Column(String(300))
    city = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(2), default="DE")  # ISO 3166-1 alpha-2
    
    # Participant Settings
    participant_type = Column(
        SQLEnum(
            ParticipantType,
            name='participant_type_enum',
            values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=ParticipantType.TEAM.value
    )
    min_participants = Column(Integer, default=2)
    max_participants = Column(Integer, nullable=False)
    current_participants = Column(Integer, default=0)
    
    # Tournament Details
    rules = Column(Text)  # Tournament rules & regulations
    prize_info = Column(Text)  # Prize/awards information
    entry_fee = Column(Numeric(10, 2))  # Entry fee in EUR
    
    # Visibility & Access
    is_public = Column(Boolean, default=True)  # Public or invite-only
    is_active = Column(Boolean, default=True)
    
    # Contact Information
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    
    # Relationships
    club = relationship("Club", back_populates="tournaments")
    creator = relationship("User", foreign_keys="[Tournament.created_by]", back_populates="tournaments_created")
    participants = relationship(
        "TournamentParticipant",
        back_populates="tournament",
        cascade="all, delete-orphan"
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_tournament_club_status', 'club_id', 'status'),
        Index('idx_tournament_sport_status', 'sport_type', 'status'),
        Index('idx_tournament_dates', 'start_date', 'end_date'),
        Index('idx_tournament_registration', 'registration_start', 'registration_end'),
    )
    
    def __repr__(self) -> str:
        """String representation of Tournament."""
        return f"<Tournament(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    @property
    def is_registration_open(self) -> bool:
        """Check if registration is currently open."""
        if self.status != TournamentStatus.REGISTRATION_OPEN.value:
            return False
        
        now = datetime.utcnow()
        
        if self.registration_start and now < self.registration_start:
            return False
        
        if self.registration_end and now > self.registration_end:
            return False
        
        return True
    
    @property
    def is_full(self) -> bool:
        """Check if tournament has reached max participants."""
        return self.current_participants >= self.max_participants
    
    @property
    def can_register(self) -> bool:
        """Check if new registrations are possible."""
        return self.is_registration_open and not self.is_full
