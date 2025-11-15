"""
Match model for UnserTurnierplan.

This module defines the Match model which represents individual matches/games
in tournaments. Supports 2-N participants (for races), knockout progression,
and flexible scoring.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, 
    ForeignKey, Index, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class MatchStatus(str, Enum):
    """Match status lifecycle."""
    SCHEDULED = "scheduled"  # Match is scheduled
    IN_PROGRESS = "in_progress"  # Match currently playing
    COMPLETED = "completed"  # Match finished
    CANCELLED = "cancelled"  # Match cancelled
    POSTPONED = "postponed"  # Match postponed
    WALKOVER = "walkover"  # Walkover/forfeit


class MatchFormat(str, Enum):
    """Match format types."""
    SINGLE_GAME = "single_game"  # One game
    BEST_OF_3 = "best_of_3"  # Best of 3
    BEST_OF_5 = "best_of_5"  # Best of 5
    TIMED = "timed"  # Time-based (e.g., 90 minutes)
    LAPS = "laps"  # Lap-based (races)
    ROUNDS = "rounds"  # Round-based (boxing, etc.)


class Match(BaseModel):
    """
    Match model.
    
    Represents an individual match/game in a tournament. Supports:
    - 2-N participants (for races, free-for-all)
    - Knockout bracket progression
    - Flexible JSONB scoring
    - Round/group organization
    
    Relationships:
        - tournament: Parent tournament
        - participants: Match participants (N:M via MatchParticipant)
        - winner: Winning participant
        - referee: Assigned referee
        - next_match: Next match in bracket (for progression)
    """
    
    __tablename__ = "matches"
    
    # Foreign Keys
    tournament_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("tournaments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Match Organization
    round_number = Column(Integer, nullable=False)  # 1, 2, 3, ..., Final
    match_number = Column(Integer, nullable=False)  # Match # within round
    round_name = Column(String(100))  # "Quarterfinal", "Heat 1", "Group A Round 1"
    group_name = Column(String(50))  # "Group A", "Pool 1", NULL for knockout
    
    # Phase (optional - for multi-phase tournaments)
    phase = Column(String(50))  # "group_stage", "knockout", "qualifying", "final"
    
    # Scheduling
    scheduled_start = Column(DateTime)
    scheduled_end = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    
    # Location
    venue_name = Column(String(200))
    court_field_number = Column(String(50))  # "Court 1", "Field A", "Track 3"
    
    # Status
    status = Column(
        String(50),
        nullable=False,
        default=MatchStatus.SCHEDULED.value
    )
    
    # Match Configuration
    match_format = Column(String(50))
    duration_minutes = Column(Integer)  # Expected duration
    
    # Results
    is_finished = Column(Boolean, default=False)
    winner_participant_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("tournament_participants.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Flexible Scoring System (JSONB)
    score_data = Column(JSONB)
    # Examples:
    # Football: {"final_score": {"home": 2, "away": 1}, "halftime": {"home": 1, "away": 0}}
    # Basketball: {"quarters": [{"home": 25, "away": 22}, ...], "final": {"home": 98, "away": 95}}
    # Tennis: {"sets": [[6,4], [7,5]], "winner_sets": 2}
    # Race: {"ranking": [{"participant_id": "...", "position": 1, "time": "1:23.456"}]}
    
    # Match Metadata
    notes = Column(Text)
    is_bye = Column(Boolean, default=False)  # Freilos/Bye match
    requires_referee = Column(Boolean, default=True)
    referee_user_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Bracket Dependencies (for progression)
    dependent_on_match_ids = Column(ARRAY(PGUUID(as_uuid=True)))  # Matches this depends on
    feeds_into_match_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("matches.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    participants = relationship(
        "MatchParticipant",
        back_populates="match",
        cascade="all, delete-orphan"
    )
    winner = relationship(
        "TournamentParticipant",
        foreign_keys=[winner_participant_id]
    )
    referee = relationship("User", foreign_keys=[referee_user_id])
    next_match = relationship(
        "Match",
        remote_side="Match.id",
        foreign_keys=[feeds_into_match_id]
    )
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_match_tournament', 'tournament_id'),
        Index('idx_match_tournament_round', 'tournament_id', 'round_number'),
        Index('idx_match_tournament_status', 'tournament_id', 'status'),
        Index('idx_match_schedule', 'scheduled_start', 'scheduled_end'),
        Index('idx_match_venue', 'tournament_id', 'venue_name', 'court_field_number'),
    )
    
    def __repr__(self) -> str:
        """String representation of Match."""
        return f"<Match(id={self.id}, round={self.round_number}, match={self.match_number}, status='{self.status}')>"
    
    @property
    def is_in_progress(self) -> bool:
        """Check if match is currently in progress."""
        return self.status == MatchStatus.IN_PROGRESS.value
    
    @property
    def is_completed(self) -> bool:
        """Check if match is completed."""
        return self.status == MatchStatus.COMPLETED.value and self.is_finished
