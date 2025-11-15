"""
MatchParticipant model for UnserTurnierplan.

Junction model for Match <-> TournamentParticipant relationship.
Allows matches with 2+ participants (important for races, multi-player games).
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, Numeric, 
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, INTERVAL
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class MatchParticipant(BaseModel):
    """
    Match participant junction model.
    
    Links participants to matches with individual results and stats.
    Supports both 2-player matches (home/away) and N-player matches (races).
    
    Relationships:
        - match: The match
        - participant: The tournament participant
    """
    
    __tablename__ = "match_participants"
    
    # Foreign Keys
    match_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    participant_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("tournament_participants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Position in Match
    slot_number = Column(Integer, nullable=False)  # 1, 2, 3, ... (for ordering)
    team_side = Column(String(20))  # "home", "away", NULL (for >2 participants)
    
    # Individual Results
    final_position = Column(Integer)  # 1st, 2nd, 3rd place (for races)
    score_value = Column(Numeric(10, 3))  # Points/Goals/Time scored
    result_time = Column(INTERVAL)  # Finish time (for races) - e.g., "01:23:45.678"
    is_winner = Column(Boolean, default=False)
    is_disqualified = Column(Boolean, default=False)
    
    # Participant-specific detailed scoring (JSONB)
    detailed_score = Column(JSONB)
    # Examples:
    # Football: {"goals": 2, "assists": 1, "yellow_cards": 1, "red_cards": 0}
    # Basketball: {"points": 28, "rebounds": 12, "assists": 7, "fouls": 3}
    # Race: {"lap_times": ["1:23.456", "1:22.789", "1:23.012"], "best_lap": "1:22.789"}
    # Tennis: {"aces": 8, "double_faults": 2, "winners": 24}
    
    notes = Column(Text)
    
    # Relationships
    match = relationship("Match", back_populates="participants")
    participant = relationship("TournamentParticipant")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('match_id', 'participant_id', name='uq_match_participant'),
        Index('idx_match_participants_match', 'match_id'),
        Index('idx_match_participants_participant', 'participant_id'),
    )
    
    def __repr__(self) -> str:
        """String representation of MatchParticipant."""
        return f"<MatchParticipant(match={self.match_id}, participant={self.participant_id}, slot={self.slot_number})>"
