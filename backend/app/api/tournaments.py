"""
Tournament API endpoints.

This module provides all tournament-related API endpoints including
CRUD operations, status management, and registration.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.tournament import (
    TournamentCreate, TournamentUpdate, TournamentResponse,
    TournamentDetail, TournamentListItem, TournamentStatusUpdate,
    TournamentFilters,
    TournamentParticipantCreate, TournamentParticipantUpdate,
    TournamentParticipantResponse, TournamentParticipantDetail,
    ParticipantStatusUpdate, ParticipantPaymentUpdate
)
from app.services.tournament_service import TournamentService
from app.services.tournament_participant_service import TournamentParticipantService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


# ==================== TOURNAMENT CRUD ====================

@router.post(
    "",
    response_model=TournamentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create tournament",
    description="Create a new tournament. Requires owner/admin role or manager role for specific department."
)
async def create_tournament(
        tournament_data: TournamentCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Create a new tournament.

    Permissions:
    - Club owner/admin: Can create tournaments for any department
    - Club manager: Can create tournaments only for their department
    """
    # Check permissions
    can_create = await TournamentService.can_user_create_tournament(
        db, tournament_data.club_id, current_user.id, tournament_data.department
    )
    if not can_create:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tournaments for this club/department"
        )

    try:
        tournament = await TournamentService.create_tournament(
            db, tournament_data, current_user.id
        )
        return tournament
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[TournamentListItem],
    summary="List tournaments",
    description="Get list of tournaments with optional filters"
)
async def list_tournaments(
        sport_type: Optional[str] = Query(None, description="Filter by sport type"),
        tournament_type: Optional[str] = Query(None, description="Filter by tournament type"),
        status: Optional[str] = Query(None, description="Filter by status"),
        city: Optional[str] = Query(None, description="Filter by city"),
        club_id: Optional[UUID] = Query(None, description="Filter by club"),
        is_public: Optional[bool] = Query(None, description="Filter by visibility"),
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=100, description="Maximum number of records"),
        db: AsyncSession = Depends(get_db)
):
    """Get list of tournaments with optional filters."""
    filters = TournamentFilters(
        sport_type=sport_type,
        tournament_type=tournament_type,
        status=status,
        city=city,
        club_id=club_id,
        is_public=is_public
    )

    tournaments = await TournamentService.get_tournaments(
        db, filters, skip, limit
    )
    return tournaments


@router.get(
    "/{tournament_id}",
    response_model=TournamentDetail,
    summary="Get tournament details",
    description="Get detailed information about a specific tournament"
)
async def get_tournament(
        tournament_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    """Get tournament by ID with full details."""
    tournament = await TournamentService.get_tournament_by_id(
        db, tournament_id, load_relationships=True
    )
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    return tournament


@router.get(
    "/slug/{slug}",
    response_model=TournamentDetail,
    summary="Get tournament by slug",
    description="Get tournament details using slug instead of ID"
)
async def get_tournament_by_slug(
        slug: str,
        db: AsyncSession = Depends(get_db)
):
    """Get tournament by slug."""
    tournament = await TournamentService.get_tournament_by_slug(
        db, slug, load_relationships=True
    )
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    return tournament


@router.put(
    "/{tournament_id}",
    response_model=TournamentResponse,
    summary="Update tournament",
    description="Update tournament details. Requires management permissions."
)
async def update_tournament(
        tournament_id: UUID,
        tournament_data: TournamentUpdate,
        db: AsyncSession = Depends(get_db),
        # current_user: User = Depends(get_current_user)
):
    """Update tournament."""
    # TODO: Uncomment when auth is implemented
    # # Check permissions
    # can_manage = await TournamentService.can_user_manage_tournament(
    #     db, tournament_id, current_user.id
    # )
    # if not can_manage:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not authorized to manage this tournament"
    #     )

    tournament = await TournamentService.update_tournament(
        db, tournament_id, tournament_data
    )
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    return tournament


@router.delete(
    "/{tournament_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete tournament",
    description="Delete tournament (soft delete). Only allowed for draft/cancelled tournaments without participants."
)
async def delete_tournament(
        tournament_id: UUID,
        db: AsyncSession = Depends(get_db),
        # current_user: User = Depends(get_current_user)
):
    """Delete tournament."""
    # TODO: Uncomment when auth is implemented
    # # Check permissions
    # can_manage = await TournamentService.can_user_manage_tournament(
    #     db, tournament_id, current_user.id
    # )
    # if not can_manage:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not authorized to manage this tournament"
    #     )

    try:
        deleted = await TournamentService.delete_tournament(db, tournament_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tournament not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/{tournament_id}/status",
    response_model=TournamentResponse,
    summary="Update tournament status",
    description="Change tournament status (draft → published → active → completed). Requires management permissions."
)
async def update_tournament_status(
        tournament_id: UUID,
        status_update: TournamentStatusUpdate,
        db: AsyncSession = Depends(get_db),
        # current_user: User = Depends(get_current_user)
):
    """Update tournament status."""
    # TODO: Uncomment when auth is implemented
    # # Check permissions
    # can_manage = await TournamentService.can_user_manage_tournament(
    #     db, tournament_id, current_user.id
    # )
    # if not can_manage:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not authorized to manage this tournament"
    #     )

    try:
        tournament = await TournamentService.update_tournament_status(
            db, tournament_id, status_update
        )
        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tournament not found"
            )
        return tournament
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ==================== TOURNAMENT QUERIES ====================

@router.get(
    "/my/created",
    response_model=List[TournamentListItem],
    summary="Get my created tournaments",
    description="Get all tournaments created by the current user"
)
async def get_my_tournaments(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get tournaments created by current user."""
    tournaments = await TournamentService.get_tournaments_by_creator(
        db, current_user.id, skip, limit
    )
    return tournaments


@router.get(
    "/my/participating",
    response_model=List[TournamentParticipantDetail],
    summary="Get tournaments I'm participating in",
    description="Get all tournaments where current user or their club is participating"
)
async def get_my_participations(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get tournaments where user is participating."""
    participations = await TournamentParticipantService.get_user_participations(
        db, current_user.id, include_club_participations=True, skip=skip, limit=limit
    )
    return participations


@router.get(
    "/{tournament_id}/statistics",
    summary="Get tournament statistics",
    description="Get detailed statistics about a tournament"
)
async def get_tournament_statistics(
        tournament_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    """Get tournament statistics."""
    stats = await TournamentService.get_tournament_statistics(db, tournament_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    return stats


# ==================== PARTICIPANT REGISTRATION ====================

@router.post(
    "/{tournament_id}/register",
    response_model=TournamentParticipantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register for tournament",
    description="Register a team or individual for a tournament"
)
async def register_for_tournament(
        tournament_id: UUID,
        participant_data: TournamentParticipantCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Register participant for tournament."""
    try:
        participant = await TournamentParticipantService.register_participant(
            db, tournament_id, participant_data, current_user.id
        )
        return participant
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{tournament_id}/participants",
    response_model=List[TournamentParticipantResponse],
    summary="Get tournament participants",
    description="Get all participants registered for a tournament"
)
async def get_tournament_participants(
        tournament_id: UUID,
        status: Optional[str] = Query(None, description="Filter by participant status"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    """Get all participants for a tournament."""
    participants = await TournamentParticipantService.get_tournament_participants(
        db, tournament_id, status, skip, limit
    )
    return participants


@router.get(
    "/{tournament_id}/participants/{participant_id}",
    response_model=TournamentParticipantDetail,
    summary="Get participant details",
    description="Get detailed information about a specific participant"
)
async def get_participant(
        tournament_id: UUID,
        participant_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    """Get participant by ID."""
    participant = await TournamentParticipantService.get_participant_by_id(
        db, participant_id, load_relationships=True
    )
    if not participant or participant.tournament_id != tournament_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    return participant


@router.put(
    "/{tournament_id}/participants/{participant_id}",
    response_model=TournamentParticipantResponse,
    summary="Update participant",
    description="Update participant registration details"
)
async def update_participant(
        tournament_id: UUID,
        participant_id: UUID,
        participant_data: TournamentParticipantUpdate,
        db: AsyncSession = Depends(get_db),
        # current_user: User = Depends(get_current_user)
):
    """Update participant registration."""
    # TODO: Uncomment when auth is implemented
    # # Check permissions
    # can_modify = await TournamentParticipantService.can_user_modify_participant(
    #     db, participant_id, current_user.id
    # )
    # if not can_modify:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not authorized to modify this participant"
    #     )

    participant = await TournamentParticipantService.update_participant(
        db, participant_id, participant_data
    )
    if not participant or participant.tournament_id != tournament_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    return participant


@router.delete(
    "/{tournament_id}/participants/{participant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove participant",
    description="Remove participant from tournament"
)
async def remove_participant(
        tournament_id: UUID,
        participant_id: UUID,
        db: AsyncSession = Depends(get_db),
        # current_user: User = Depends(get_current_user)
):
    """Remove participant from tournament."""
    # TODO: Uncomment when auth is implemented
    # # Check permissions
    # can_modify = await TournamentParticipantService.can_user_modify_participant(
    #     db, participant_id, current_user.id
    # )
    # if not can_modify:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not authorized to modify this participant"
    #     )

    # Verify participant belongs to tournament
    participant = await TournamentParticipantService.get_participant_by_id(db, participant_id)
    if not participant or participant.tournament_id != tournament_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )

    deleted = await TournamentParticipantService.remove_participant(db, participant_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )


@router.put(
    "/{tournament_id}/participants/{participant_id}/status",
    response_model=TournamentParticipantResponse,
    summary="Update participant status",
    description="Update participant status (pending → confirmed, etc.)"
)
async def update_participant_status(
        tournament_id: UUID,
        participant_id: UUID,
        status_update: ParticipantStatusUpdate,
        db: AsyncSession = Depends(get_db),
        # current_user: User = Depends(get_current_user)
):
    """Update participant status."""
    # TODO: Add permission check - only tournament managers

    participant = await TournamentParticipantService.update_participant_status(
        db, participant_id, status_update
    )
    if not participant or participant.tournament_id != tournament_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    return participant


@router.put(
    "/{tournament_id}/participants/{participant_id}/payment",
    response_model=TournamentParticipantResponse,
    summary="Update payment status",
    description="Update participant payment information"
)
async def update_participant_payment(
        tournament_id: UUID,
        participant_id: UUID,
        payment_update: ParticipantPaymentUpdate,
        db: AsyncSession = Depends(get_db),
        # current_user: User = Depends(get_current_user)
):
    """Update participant payment status."""
    # TODO: Add permission check - only tournament managers

    participant = await TournamentParticipantService.update_payment_status(
        db, participant_id, payment_update
    )
    if not participant or participant.tournament_id != tournament_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    return participant


@router.delete(
    "/{tournament_id}/participants/{participant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove participant"
)
async def delete_participant(
        tournament_id: UUID,
        participant_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Remove a participant from the tournament."""
    success = await TournamentParticipantService.remove_participant(
        db, participant_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    return None