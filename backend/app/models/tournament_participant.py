"""
TournamentParticipant model for UnserTurnierplan.

This module defines the TournamentParticipant model which represents
registrations of teams or individuals to tournaments. Manages the
many-to-many relationship between tournaments and participants.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column, String, Text, DateTime, Integer, Boolean,
    Numeric, ForeignKey, Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ParticipantStatus(str, Enum):
    """Registration status for tournament participants."""
    PENDING = "pending"  # Registration pending approval
    CONFIRMED = "confirmed"  # Registration confirmed
    CANCELLED = "cancelled"  # Registration cancelled
    WAITLIST = "waitlist"  # On waitlist (tournament full)


class PaymentStatus(str, Enum):
    """Payment status for entry fees."""
    NOT_REQUIRED = "not_required"  # No payment required
    PENDING = "pending"  # Payment pending
    PAID = "paid"  # Payment completed
    REFUNDED = "refunded"  # Payment refunded


class TournamentParticipant(BaseModel):
    """
    TournamentParticipant model.
    
    Represents a registration of a team or individual to a tournament.
    Manages the many-to-many relationship between tournaments and
    participants (clubs or users).
    
    Relationships:
        - tournament: The tournament being participated in
        - participant_club: The club participating (for team tournaments)
        - participant_user: The user participating (for individual tournaments)
    """
    
    __tablename__ = "tournament_participants"
    
    # Foreign Keys (id, created_at, updated_at inherited from BaseModel)
    
    # Foreign Keys
    tournament_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("tournaments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Participant can be either a club (team) or user (individual)
    participant_club_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("clubs.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    participant_user_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    # Registered by (the user who made the registration)
    registered_by = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Participant Information
    participant_name = Column(String(200), nullable=False)  # Team/Player name
    display_name = Column(String(200))  # Optional display name
    
    # Contact Information
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    
    # Registration Details
    registration_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Status Management
    status = Column(
        SQLEnum(
            ParticipantStatus,
            name='participant_status_enum',
            values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=ParticipantStatus.PENDING.value,
        index=True
    )
    
    # Payment Management
    payment_status = Column(
        SQLEnum(
            PaymentStatus,
            name='payment_status_enum',
            values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=PaymentStatus.NOT_REQUIRED.value
    )
    payment_amount = Column(Numeric(10, 2))
    payment_date = Column(DateTime)
    payment_reference = Column(String(100))
    
    # Tournament Seeding
    seed = Column(Integer)  # Seeding position (1 = top seed)
    
    # Additional Information
    notes = Column(Text)  # Admin notes
    player_list = Column(Text)  # JSON or text list of players
    
    # Relationships
    tournament = relationship("Tournament", back_populates="participants")
    participant_club = relationship("Club", foreign_keys=[participant_club_id])
    participant_user = relationship("User", foreign_keys=[participant_user_id])
    registrar = relationship("User", foreign_keys=[registered_by])
    
    # Constraints
    __table_args__ = (
        # Ensure a participant (club or user) can only register once per tournament
        UniqueConstraint(
            'tournament_id', 
            'participant_club_id',
            name='uq_tournament_club_participant'
        ),
        UniqueConstraint(
            'tournament_id',
            'participant_user_id',
            name='uq_tournament_user_participant'
        ),
        # Indexes for common queries
        Index('idx_participant_tournament_status', 'tournament_id', 'status'),
        Index('idx_participant_seed', 'tournament_id', 'seed'),
    )
    
    def __repr__(self) -> str:
        """String representation of TournamentParticipant."""
        return (
            f"<TournamentParticipant(id={self.id}, "
            f"tournament_id={self.tournament_id}, "
            f"name='{self.participant_name}', "
            f"status='{self.status}')>"
        )
    
    @property
    def is_confirmed(self) -> bool:
        """Check if participant is confirmed."""
        return self.status == ParticipantStatus.CONFIRMED.value
    
    @property
    def is_paid(self) -> bool:
        """Check if payment is completed."""
        return (
            self.payment_status == PaymentStatus.NOT_REQUIRED.value or
            self.payment_status == PaymentStatus.PAID.value
        )
    
    @property
    def participant_type(self) -> str:
        """Get participant type (club or user)."""
        if self.participant_club_id:
            return "club"
        elif self.participant_user_id:
            return "user"
        return "unknown"
