"""
TournamentStandings model for UnserTurnierplan.

Cached tournament standings/rankings table.
Updated after each match completion for performance.
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column, String, Integer, Numeric, ForeignKey, 
    Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class TournamentStandings(BaseModel):
    """
    Tournament standings model.
    
    Cached standings/rankings for tournaments. Updated after each match
    completion to avoid expensive real-time calculations.
    
    Supports:
    - League/Round-Robin standings (points, goal difference, etc.)
    - Group stage standings
    - Tournament statistics
    
    Relationships:
        - tournament: Parent tournament
        - participant: Tournament participant
    """
    
    __tablename__ = "tournament_standings"
    
    # Foreign Keys
    tournament_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("tournaments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    participant_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("tournament_participants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Group (for group stage tournaments)
    group_name = Column(String(50))  # "Group A", "Pool 1", NULL for overall
    
    # Match Statistics
    matches_played = Column(Integer, default=0, nullable=False)
    matches_won = Column(Integer, default=0, nullable=False)
    matches_drawn = Column(Integer, default=0, nullable=False)
    matches_lost = Column(Integer, default=0, nullable=False)
    
    # Scoring
    points = Column(Integer, default=0, nullable=False)  # League points (3 for win, 1 for draw)
    score_for = Column(Numeric(10, 2), default=0, nullable=False)  # Goals/Points scored
    score_against = Column(Numeric(10, 2), default=0, nullable=False)  # Goals/Points conceded
    score_difference = Column(Numeric(10, 2), default=0, nullable=False)  # Goal difference
    
    # Rankings
    current_rank = Column(Integer)
    previous_rank = Column(Integer)
    
    # Additional Stats (JSONB for flexibility)
    additional_stats = Column(JSONB)
    # Examples:
    # Football: {"yellow_cards": 8, "red_cards": 1, "clean_sheets": 3}
    # Basketball: {"average_points": 85.5, "highest_score": 102, "lowest_score": 67}
    # Race: {"best_lap_time": "1:22.345", "average_finish_position": 3.2, "dnf_count": 1}
    
    # Form (recent results)
    recent_form = Column(String(20))  # "WWDLL" (W=Win, D=Draw, L=Loss) - last 5 matches
    
    # Relationships
    tournament = relationship("Tournament")
    participant = relationship("TournamentParticipant")
    
    # Constraints & Indexes
    __table_args__ = (
        UniqueConstraint(
            'tournament_id', 'participant_id', 'group_name',
            name='uq_tournament_standings'
        ),
        Index('idx_standings_tournament', 'tournament_id'),
        Index('idx_standings_tournament_group', 'tournament_id', 'group_name'),
        Index('idx_standings_rank', 'tournament_id', 'current_rank'),
    )
    
    def __repr__(self) -> str:
        """String representation of TournamentStandings."""
        return f"<TournamentStandings(tournament={self.tournament_id}, rank={self.current_rank}, points={self.points})>"
    
    @property
    def win_percentage(self) -> float:
        """Calculate win percentage."""
        if self.matches_played == 0:
            return 0.0
        return (self.matches_won / self.matches_played) * 100
    
    @property
    def points_per_game(self) -> float:
        """Calculate average points per game."""
        if self.matches_played == 0:
            return 0.0
        return float(self.points) / self.matches_played
