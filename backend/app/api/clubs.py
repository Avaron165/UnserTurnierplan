"""
Club API endpoints
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.club import (
    ClubCreate,
    ClubUpdate,
    ClubResponse,
    ClubWithMembers,
    ClubMemberCreate,
    ClubMemberUpdate,
    ClubMemberResponse,
    ClubMemberWithUser,
    ClubVerificationRequest,
    ClubVerificationDecision,
)
from app.services.club_service import ClubService
from app.services.club_member_service import ClubMemberService
from app.api.dependencies import (
    get_current_user,
    get_current_superuser,
    require_club_owner,
    require_club_admin,
    require_club_manager,
)
from app.models.user import User
from app.models.club_member import ClubRole

router = APIRouter(prefix="/clubs", tags=["Clubs"])


# ============================================================================
# CLUB MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
async def create_club(
        club_in: ClubCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    Create a new club. Creator becomes the owner.
    """
    try:
        club = await ClubService.create(db, club_in, current_user.id)
        await db.commit()
        return club
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[ClubResponse])
async def list_clubs(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        search: Optional[str] = Query(None, max_length=100),
        city: Optional[str] = Query(None, max_length=100),
        verified_only: bool = Query(False),
        db: AsyncSession = Depends(get_db),
):
    """
    List clubs with optional filters and pagination.
    """
    clubs = await ClubService.list_clubs(
        db,
        skip=skip,
        limit=limit,
        search=search,
        city=city,
        verified_only=verified_only
    )
    return clubs


@router.get("/count")
async def count_clubs(
        search: Optional[str] = Query(None, max_length=100),
        city: Optional[str] = Query(None, max_length=100),
        db: AsyncSession = Depends(get_db),
):
    """
    Count clubs with filters.
    """
    count = await ClubService.count_clubs(db, search=search, city=city)
    return {"count": count}


@router.get("/{club_id}")
async def get_club(
        club_id: UUID,
        include_members: bool = Query(False),
        db: AsyncSession = Depends(get_db),
):
    """
    Get club by ID.
    """
    club = await ClubService.get_by_id(db, club_id, include_members=include_members)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )

    # Return ClubResponse always (members loaded but not included in response for now)
    return ClubResponse.model_validate(club)


@router.get("/slug/{slug}", response_model=ClubResponse)
async def get_club_by_slug(
        slug: str,
        db: AsyncSession = Depends(get_db),
):
    """
    Get club by slug.
    """
    club = await ClubService.get_by_slug(db, slug)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    return club


@router.put("/{club_id}", response_model=ClubResponse)
async def update_club(
        club_id: UUID,
        club_update: ClubUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    Update club. Requires admin or owner role.
    """
    # Check permission
    await require_club_admin(club_id, current_user, db)

    try:
        club = await ClubService.update(db, club_id, club_update)
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Club not found"
            )
        await db.commit()
        return club
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_club(
        club_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    Delete club (soft delete). Requires owner role.
    """
    # Check permission
    await require_club_owner(club_id, current_user, db)

    success = await ClubService.delete(db, club_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )
    await db.commit()
    return None


# ============================================================================
# CLUB MEMBER MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/{club_id}/members", response_model=List[ClubMemberResponse])
async def list_club_members(
        club_id: UUID,
        role: Optional[ClubRole] = Query(None),
        db: AsyncSession = Depends(get_db),
):
    """
    List all members of a club.
    """
    # Verify club exists
    club = await ClubService.get_by_id(db, club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )

    members = await ClubMemberService.list_club_members(db, club_id, role=role)
    return members


@router.post("/{club_id}/members", response_model=ClubMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_club_member(
        club_id: UUID,
        member_in: ClubMemberCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    Add a member to club. Requires admin or owner role.
    """
    # Check permission
    await require_club_admin(club_id, current_user, db)

    try:
        member = await ClubMemberService.add_member(db, club_id, member_in)
        await db.commit()
        return member
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{club_id}/members/{user_id}", response_model=ClubMemberResponse)
async def update_club_member(
        club_id: UUID,
        user_id: UUID,
        member_update: ClubMemberUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    Update club member. Requires admin or owner role.
    """
    # Check permission
    await require_club_admin(club_id, current_user, db)

    member = await ClubMemberService.update_member(db, club_id, user_id, member_update)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    await db.commit()
    return member


@router.delete("/{club_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_club_member(
        club_id: UUID,
        user_id: UUID,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    Remove member from club. Requires admin or owner role.
    """
    # Check permission
    await require_club_admin(club_id, current_user, db)

    # Cannot remove yourself if you're the owner
    if user_id == current_user.id:
        is_owner = await ClubMemberService.is_owner(db, club_id, user_id)
        if is_owner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owners cannot remove themselves. Transfer ownership first."
            )

    try:
        success = await ClubMemberService.remove_member(db, club_id, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )
        await db.commit()
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me/memberships", response_model=List[ClubMemberResponse])
async def get_my_clubs(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    Get all clubs the current user is member of.
    """
    memberships = await ClubMemberService.list_user_clubs(db, current_user.id)
    return memberships


# ============================================================================
# VERIFICATION ENDPOINTS
# ============================================================================

@router.post("/{club_id}/verify")
async def request_verification(
        club_id: UUID,
        request_data: ClubVerificationRequest,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    """
    Request club verification. Requires owner role.
    """
    # Check permission
    await require_club_owner(club_id, current_user, db)

    club = await ClubService.get_by_id(db, club_id)
    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )

    # TODO: Implement verification request logic
    # - Store documents
    # - Send notification to admins
    # - Update status to pending

    return {
        "message": "Verification request submitted",
        "club_id": club_id,
        "status": "pending_review"
    }


@router.put("/{club_id}/verification", response_model=ClubResponse)
async def update_verification(
        club_id: UUID,
        decision: ClubVerificationDecision,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_superuser),
):
    """
    Update club verification status. Superuser only.
    """
    club = await ClubService.update_verification_status(
        db,
        club_id,
        decision.status,
        decision.notes
    )

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Club not found"
        )

    await db.commit()
    return club