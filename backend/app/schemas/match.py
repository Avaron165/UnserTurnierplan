"""
Match schemas (Pydantic models for API).

Defines all schemas for match-related API operations including:
- Match CRUD
- Match scoring
- Bracket generation
- Tournament standings
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, validator


# ==================== MATCH SCHEMAS ====================

class MatchBase(BaseModel):
    """Base match schema."""
    round_number: int = Field(..., ge=1, description="Round number (1, 2, 3, ...)")
    match_number: int = Field(..., ge=1, description="Match number within round")
    round_name: Optional[str] = Field(None, max_length=100, description="e.g., 'Quarterfinal', 'Heat 1'")
    group_name: Optional[str] = Field(None, max_length=50, description="e.g., 'Group A', 'Pool 1'")
    phase: Optional[str] = Field(None, max_length=50, description="e.g., 'group_stage', 'knockout', 'qualifying'")
    
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    
    venue_name: Optional[str] = Field(None, max_length=200)
    court_field_number: Optional[str] = Field(None, max_length=50, description="e.g., 'Court 1', 'Field A'")
    
    match_format: Optional[str] = Field(None, description="e.g., 'single_game', 'best_of_3', 'timed'")
    duration_minutes: Optional[int] = Field(None, ge=1, description="Expected match duration")
    
    notes: Optional[str] = None
    requires_referee: bool = True


class MatchCreate(MatchBase):
    """Schema for creating a match."""
    tournament_id: UUID
    participant_ids: List[UUID] = Field(..., min_items=2, description="List of participant UUIDs (ordered)")
    
    @validator("participant_ids")
    def validate_participant_ids(cls, v):
        """Ensure at least 2 participants."""
        if len(v) < 2:
            raise ValueError("Match must have at least 2 participants")
        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Duplicate participant IDs not allowed")
        return v


class MatchUpdate(BaseModel):
    """Schema for updating a match."""
    round_name: Optional[str] = Field(None, max_length=100)
    group_name: Optional[str] = Field(None, max_length=50)
    phase: Optional[str] = Field(None, max_length=50)
    
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    
    venue_name: Optional[str] = Field(None, max_length=200)
    court_field_number: Optional[str] = Field(None, max_length=50)
    
    match_format: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1)
    
    notes: Optional[str] = None
    referee_user_id: Optional[UUID] = None


class MatchResponse(MatchBase):
    """Schema for match response."""
    id: UUID
    tournament_id: UUID
    status: str
    is_finished: bool
    winner_participant_id: Optional[UUID]
    score_data: Optional[Dict[str, Any]]
    is_bye: bool
    referee_user_id: Optional[UUID]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    dependent_on_match_ids: Optional[List[UUID]]
    feeds_into_match_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchDetail(MatchResponse):
    """Detailed match with participants."""
    participants: List["MatchParticipantResponse"] = []
    winner: Optional["TournamentParticipantResponse"] = None


class MatchListItem(BaseModel):
    """Lightweight match for lists."""
    id: UUID
    round_number: int
    match_number: int
    round_name: Optional[str]
    group_name: Optional[str]
    phase: Optional[str]
    scheduled_start: Optional[datetime]
    status: str
    is_finished: bool
    venue_name: Optional[str]
    court_field_number: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# ==================== MATCH PARTICIPANT SCHEMAS ====================

class MatchParticipantBase(BaseModel):
    """Base match participant schema."""
    slot_number: int = Field(..., ge=1, description="Position in match (1, 2, 3, ...)")
    team_side: Optional[str] = Field(None, max_length=20, description="'home', 'away', or NULL")


class MatchParticipantCreate(MatchParticipantBase):
    """Schema for adding participant to match."""
    participant_id: UUID


class MatchParticipantUpdate(BaseModel):
    """Schema for updating match participant."""
    final_position: Optional[int] = Field(None, ge=1, description="Finishing position (1st, 2nd, 3rd, ...)")
    score_value: Optional[Decimal] = Field(None, description="Points/Goals scored")
    result_time: Optional[timedelta] = Field(None, description="Finish time for races")
    is_winner: Optional[bool] = None
    is_disqualified: Optional[bool] = None
    detailed_score: Optional[Dict[str, Any]] = Field(None, description="Sport-specific statistics")
    notes: Optional[str] = None


class MatchParticipantResponse(MatchParticipantBase):
    """Schema for match participant response."""
    id: UUID
    match_id: UUID
    participant_id: UUID
    final_position: Optional[int]
    score_value: Optional[Decimal]
    result_time: Optional[timedelta]
    is_winner: bool
    is_disqualified: bool
    detailed_score: Optional[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchParticipantDetail(MatchParticipantResponse):
    """Detailed match participant with participant info."""
    participant: "TournamentParticipantResponse"


# ==================== MATCH SCORING SCHEMAS ====================

class ParticipantScoreEntry(BaseModel):
    """Individual participant score entry."""
    participant_id: UUID
    score_value: Optional[Decimal] = None
    final_position: Optional[int] = Field(None, ge=1)
    result_time: Optional[str] = Field(None, description="Time as string, e.g., '1:23.456'")
    is_winner: bool = False
    is_disqualified: bool = False
    detailed_score: Optional[Dict[str, Any]] = None


class MatchScoreUpdate(BaseModel):
    """Schema for updating match score."""
    participant_scores: List[ParticipantScoreEntry] = Field(..., min_items=1)
    score_data: Optional[Dict[str, Any]] = Field(None, description="Overall match score data (JSONB)")
    winner_participant_id: Optional[UUID] = None
    
    @validator("participant_scores")
    def validate_scores(cls, v, values):
        """Validate participant scores."""
        if len(v) < 1:
            raise ValueError("At least one participant score required")
        
        # Check for duplicate participants
        participant_ids = [score.participant_id for score in v]
        if len(participant_ids) != len(set(participant_ids)):
            raise ValueError("Duplicate participant IDs in scores")
        
        # Ensure only one winner if specified
        winners = [score for score in v if score.is_winner]
        if len(winners) > 1:
            raise ValueError("Only one participant can be marked as winner")
        
        return v


class MatchStatusUpdate(BaseModel):
    """Schema for updating match status."""
    status: str = Field(..., description="'scheduled', 'in_progress', 'completed', 'cancelled', 'postponed'")
    notes: Optional[str] = Field(None, max_length=500)


# ==================== BRACKET/SCHEDULE GENERATION SCHEMAS ====================

class BracketGenerationRequest(BaseModel):
    """Request to generate knockout bracket."""
    tournament_id: UUID
    shuffle_seeds: bool = Field(default=False, description="Randomize participant seeding")


class RoundRobinGenerationRequest(BaseModel):
    """Request to generate round-robin schedule."""
    tournament_id: UUID
    home_and_away: bool = Field(default=False, description="Double round-robin (home & away)")
    group_name: Optional[str] = Field(None, description="Group name for group stage tournaments")


class GroupStageGenerationRequest(BaseModel):
    """Request to generate group stage + knockout tournament."""
    tournament_id: UUID
    num_groups: int = Field(..., ge=2, le=8, description="Number of groups")
    teams_per_group: int = Field(..., ge=2, description="Teams per group")
    advance_per_group: int = Field(..., ge=1, description="Teams advancing from each group")
    home_and_away: bool = Field(default=False, description="Double round-robin within groups")


class MatchSchedulingRequest(BaseModel):
    """Request to schedule match times."""
    tournament_id: UUID
    start_time: datetime
    match_duration_minutes: int = Field(default=90, ge=1)
    break_duration_minutes: int = Field(default=15, ge=0)
    courts_available: int = Field(default=1, ge=1)
    matches_per_court_per_day: int = Field(default=6, ge=1)


# ==================== TOURNAMENT STANDINGS SCHEMAS ====================

class StandingsBase(BaseModel):
    """Base standings schema."""
    matches_played: int = 0
    matches_won: int = 0
    matches_drawn: int = 0
    matches_lost: int = 0
    points: int = 0
    score_for: Decimal = Decimal(0)
    score_against: Decimal = Decimal(0)
    score_difference: Decimal = Decimal(0)


class StandingsResponse(StandingsBase):
    """Schema for tournament standings response."""
    id: UUID
    tournament_id: UUID
    participant_id: UUID
    group_name: Optional[str]
    current_rank: Optional[int]
    previous_rank: Optional[int]
    recent_form: Optional[str]
    additional_stats: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StandingsDetail(StandingsResponse):
    """Detailed standings with participant info."""
    participant: "TournamentParticipantResponse"


class StandingsListItem(BaseModel):
    """Lightweight standings for tables."""
    participant_id: UUID
    participant_name: str
    current_rank: int
    matches_played: int
    matches_won: int
    matches_drawn: int
    matches_lost: int
    points: int
    score_for: Decimal
    score_against: Decimal
    score_difference: Decimal

    model_config = ConfigDict(from_attributes=True)


# Forward references - import from other schema files
from app.schemas.tournament import TournamentParticipantResponse

# Rebuild models to resolve forward references
MatchDetail.model_rebuild()
MatchParticipantDetail.model_rebuild()
StandingsDetail.model_rebuild()
