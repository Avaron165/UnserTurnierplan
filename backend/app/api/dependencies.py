"""
FastAPI dependencies for authentication and permissions
"""
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import verify_token
from app.services.user_service import UserService
from app.services.club_member_service import ClubMemberService
from app.models.user import User
from app.models.club_member import ClubRole

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Get current authenticated user from token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise credentials_exception
    
    # Get user_id from token
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise credentials_exception
    
    user = await UserService.get_by_id(db, user_uuid)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


# Optional authentication (for public endpoints that can use auth if available)
async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise None
    """
    if token is None:
        return None
    
    try:
        return await get_current_user(db=db, token=token)
    except HTTPException:
        return None


# ============================================================================
# CLUB PERMISSION DEPENDENCIES
# ============================================================================

async def require_club_owner(
    club_id: UUID,
    current_user: User,
    db: AsyncSession
) -> None:
    """
    Require user to be owner of the club.
    Raises 403 if not owner.
    """
    is_owner = await ClubMemberService.is_owner(db, club_id, current_user.id)
    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club owners can perform this action"
        )


async def require_club_admin(
    club_id: UUID,
    current_user: User,
    db: AsyncSession
) -> None:
    """
    Require user to be admin or owner of the club.
    Raises 403 if not admin or owner.
    """
    is_admin = await ClubMemberService.is_admin_or_owner(db, club_id, current_user.id)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club admins/owners can perform this action"
        )


async def require_club_manager(
    club_id: UUID,
    current_user: User,
    db: AsyncSession
) -> None:
    """
    Require user to be manager, admin or owner of the club.
    Raises 403 if insufficient permissions.
    """
    can_manage = await ClubMemberService.can_manage(db, club_id, current_user.id)
    if not can_manage:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club managers/admins/owners can perform this action"
        )


async def require_club_member(
    club_id: UUID,
    current_user: User,
    db: AsyncSession
) -> None:
    """
    Require user to be member of the club.
    Raises 403 if not a member.
    """
    is_member = await ClubMemberService.check_permission(
        db, club_id, current_user.id, ClubRole.MEMBER
    )
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only club members can perform this action"
        )

