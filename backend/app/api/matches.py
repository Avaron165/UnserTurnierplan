"""
Match API endpoints.

This module provides all match-related API endpoints including:
- Match CRUD operations
- Match scoring and status updates
- Bracket generation
- Tournament standings
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.match import (
    MatchCreate, MatchUpdate, MatchResponse, MatchDetail,
    MatchListItem, MatchScoreUpdate, MatchStatusUpdate,
    BracketGenerationRequest, RoundRobinGenerationRequest,
    StandingsResponse, StandingsDetail
)
from app.services.match_service import MatchService
from app.services.bracket_service import BracketService
from app.services.standings_service import StandingsService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/matches", tags=["matches"])


# ==================== MATCH CRUD ====================

@router.post(
    "",
    response_model=MatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create match",
    description="Create a new match manually. Requires tournament management permissions."
)
async def create_match(
    match_data: MatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new match.
    
    Manually creates a match with specified participants.
    Typically used for custom tournaments or corrections.
    
    Permissions:
    - Tournament creator or club admin
    """
    try:
        match = await MatchService.create_match(db, match_data)
        return match
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[MatchListItem],
    summary="List matches",
    description="Get list of matches for a tournament with optional filters"
)
async def list_matches(
    tournament_id: UUID = Query(..., description="Tournament ID"),
    round_number: Optional[int] = Query(None, ge=1, description="Filter by round number"),
    group_name: Optional[str] = Query(None, description="Filter by group name"),
    phase: Optional[str] = Query(None, description="Filter by phase (e.g., 'knockout', 'group_stage')"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of matches for a tournament.
    
    Supports filtering by round, group, phase, and status.
    """
    matches = await MatchService.get_tournament_matches(
        db, tournament_id, round_number, group_name, phase, status, skip, limit
    )
    return matches


@router.get(
    "/{match_id}",
    response_model=MatchDetail,
    summary="Get match details",
    description="Get detailed information about a specific match"
)
async def get_match(
    match_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get match by ID with full details including participants."""
    match = await MatchService.get_match_by_id(db, match_id, load_relationships=True)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    return match


@router.put(
    "/{match_id}",
    response_model=MatchResponse,
    summary="Update match",
    description="Update match details (scheduling, venue, etc.)"
)
async def update_match(
    match_id: UUID,
    match_data: MatchUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update match details.
    
    Can update scheduling, venue, notes, etc.
    Does not update scores (use PUT /matches/{id}/score).
    
    Permissions:
    - Tournament creator or club admin
    """
    try:
        match = await MatchService.update_match(db, match_id, match_data)
        return match
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{match_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete match",
    description="Delete a match"
)
async def delete_match(
    match_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a match.
    
    Permissions:
    - Tournament creator or club owner
    """
    success = await MatchService.delete_match(db, match_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )


# ==================== MATCH SCORING ====================

@router.put(
    "/{match_id}/score",
    response_model=MatchResponse,
    summary="Update match score",
    description="Update match score and results"
)
async def update_match_score(
    match_id: UUID,
    score_data: MatchScoreUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update match score and determine winner.
    
    Automatically recalculates tournament standings after score update.
    
    Permissions:
    - Tournament creator, club admin, or assigned referee
    """
    try:
        match = await MatchService.update_match_score(db, match_id, score_data)
        
        # Recalculate standings after score update
        await StandingsService.calculate_standings(db, match.tournament_id)
        
        return match
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/{match_id}/status",
    response_model=MatchResponse,
    summary="Update match status",
    description="Update match status (scheduled, in_progress, completed, etc.)"
)
async def update_match_status(
    match_id: UUID,
    status_update: MatchStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update match status.
    
    Valid statuses:
    - scheduled: Match is scheduled
    - in_progress: Match is currently being played
    - completed: Match is finished
    - cancelled: Match was cancelled
    - postponed: Match was postponed
    
    Permissions:
    - Tournament creator, club admin, or assigned referee
    """
    try:
        match = await MatchService.update_match_status(db, match_id, status_update)
        return match
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== BRACKET GENERATION ====================

@router.post(
    "/generate/knockout",
    response_model=List[MatchResponse],
    summary="Generate knockout bracket",
    description="Generate single-elimination knockout bracket for tournament"
)
async def generate_knockout_bracket(
    request: BracketGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate knockout (single-elimination) bracket.
    
    Creates all matches from first round to final.
    Supports byes for non-power-of-2 participant counts.
    
    Permissions:
    - Tournament creator or club admin
    """
    try:
        matches = await BracketService.generate_knockout_bracket(
            db, request.tournament_id, request.shuffle_seeds
        )
        return matches
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/generate/round-robin",
    response_model=List[MatchResponse],
    summary="Generate round-robin schedule",
    description="Generate round-robin schedule (everyone plays everyone)"
)
async def generate_round_robin_schedule(
    request: RoundRobinGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate round-robin schedule.
    
    Creates matches so everyone plays everyone once (or twice if home_and_away=True).
    Uses circle method for fair scheduling.
    
    Permissions:
    - Tournament creator or club admin
    """
    try:
        matches = await BracketService.generate_round_robin_schedule(
            db,
            request.tournament_id,
            request.home_and_away,
            request.group_name
        )
        return matches
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== TOURNAMENT STANDINGS ====================

@router.get(
    "/standings/{tournament_id}",
    response_model=List[StandingsDetail],
    summary="Get tournament standings",
    description="Get current tournament standings/rankings"
)
async def get_tournament_standings(
    tournament_id: UUID,
    group_name: Optional[str] = Query(None, description="Filter by group name"),
    recalculate: bool = Query(False, description="Force recalculation from matches"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get tournament standings.
    
    Returns cached standings by default.
    Set recalculate=true to force recalculation from all completed matches.
    """
    if recalculate:
        standings = await StandingsService.calculate_standings(
            db, tournament_id, group_name
        )
    else:
        standings = await StandingsService.get_standings(
            db, tournament_id, group_name
        )
    
    return standings


@router.post(
    "/standings/{tournament_id}/recalculate",
    response_model=List[StandingsDetail],
    summary="Recalculate standings",
    description="Force recalculation of tournament standings"
)
async def recalculate_standings(
    tournament_id: UUID,
    group_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recalculate tournament standings from scratch.
    
    Recalculates based on all completed matches.
    
    Permissions:
    - Tournament creator or club admin
    """
    standings = await StandingsService.calculate_standings(
        db, tournament_id, group_name
    )
    return standings
