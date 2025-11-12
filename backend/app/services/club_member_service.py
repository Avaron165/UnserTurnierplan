"""
ClubMember service - Business logic for club membership operations
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.club import Club
from app.models.club_member import ClubMember, ClubRole
from app.models.user import User
from app.schemas.club import ClubMemberCreate, ClubMemberUpdate


class ClubMemberService:
    """Service for club member operations"""
    
    @staticmethod
    async def get_membership(
        db: AsyncSession,
        club_id: UUID,
        user_id: UUID
    ) -> Optional[ClubMember]:
        """Get membership of a user in a club"""
        result = await db.execute(
            select(ClubMember).where(
                and_(
                    ClubMember.club_id == club_id,
                    ClubMember.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_member_by_id(
        db: AsyncSession,
        member_id: UUID
    ) -> Optional[ClubMember]:
        """Get club member by ID"""
        result = await db.execute(
            select(ClubMember)
            .where(ClubMember.id == member_id)
            .options(selectinload(ClubMember.user))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_club_members(
        db: AsyncSession,
        club_id: UUID,
        role: Optional[ClubRole] = None
    ) -> List[ClubMember]:
        """List all members of a club"""
        query = select(ClubMember).where(ClubMember.club_id == club_id)
        query = query.options(selectinload(ClubMember.user))
        
        if role:
            query = query.where(ClubMember.role == role)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def list_user_clubs(
        db: AsyncSession,
        user_id: UUID
    ) -> List[ClubMember]:
        """List all clubs a user is member of"""
        result = await db.execute(
            select(ClubMember)
            .where(ClubMember.user_id == user_id)
            .options(selectinload(ClubMember.club))
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def add_member(
        db: AsyncSession,
        club_id: UUID,
        member_in: ClubMemberCreate
    ) -> ClubMember:
        """Add a member to club"""
        # Check if already member
        existing = await ClubMemberService.get_membership(
            db, club_id, member_in.user_id
        )
        if existing:
            raise ValueError("User is already a member of this club")
        
        # Check if user exists
        user_result = await db.execute(
            select(User).where(User.id == member_in.user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        
        # Create membership
        membership = ClubMember(
            club_id=club_id,
            user_id=member_in.user_id,
            role=member_in.role,
            department=member_in.department,
            position=member_in.position,
            notes=member_in.notes,
        )
        
        db.add(membership)
        await db.flush()
        
        # Update club member count
        club_result = await db.execute(
            select(Club).where(Club.id == club_id)
        )
        club = club_result.scalar_one_or_none()
        if club:
            club.member_count += 1
            await db.flush()
        
        await db.refresh(membership)
        
        return membership
    
    @staticmethod
    async def update_member(
        db: AsyncSession,
        club_id: UUID,
        user_id: UUID,
        member_in: ClubMemberUpdate
    ) -> Optional[ClubMember]:
        """Update club member"""
        membership = await ClubMemberService.get_membership(db, club_id, user_id)
        if not membership:
            return None
        
        # Update fields
        update_data = member_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(membership, field, value)
        
        await db.flush()
        await db.refresh(membership)
        
        return membership
    
    @staticmethod
    async def remove_member(
        db: AsyncSession,
        club_id: UUID,
        user_id: UUID
    ) -> bool:
        """Remove member from club"""
        membership = await ClubMemberService.get_membership(db, club_id, user_id)
        if not membership:
            return False
        
        # Check if trying to remove the last owner
        if membership.role == ClubRole.OWNER:
            owners = await ClubMemberService.list_club_members(
                db, club_id, role=ClubRole.OWNER
            )
            if len(owners) <= 1:
                raise ValueError("Cannot remove the last owner of the club")
        
        await db.delete(membership)
        await db.flush()
        
        # Update club member count
        club_result = await db.execute(
            select(Club).where(Club.id == club_id)
        )
        club = club_result.scalar_one_or_none()
        if club and club.member_count > 0:
            club.member_count -= 1
            await db.flush()
        
        return True
    
    @staticmethod
    async def check_permission(
        db: AsyncSession,
        club_id: UUID,
        user_id: UUID,
        required_role: ClubRole = ClubRole.MEMBER
    ) -> bool:
        """
        Check if user has required role in club
        
        Role hierarchy: OWNER > ADMIN > MANAGER > MEMBER > VOLUNTEER
        """
        membership = await ClubMemberService.get_membership(db, club_id, user_id)
        if not membership:
            return False
        
        role_hierarchy = {
            ClubRole.OWNER: 5,
            ClubRole.ADMIN: 4,
            ClubRole.MANAGER: 3,
            ClubRole.MEMBER: 2,
            ClubRole.VOLUNTEER: 1,
        }
        
        user_level = role_hierarchy.get(membership.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    @staticmethod
    async def is_owner(
        db: AsyncSession,
        club_id: UUID,
        user_id: UUID
    ) -> bool:
        """Check if user is owner of club"""
        return await ClubMemberService.check_permission(
            db, club_id, user_id, ClubRole.OWNER
        )
    
    @staticmethod
    async def is_admin_or_owner(
        db: AsyncSession,
        club_id: UUID,
        user_id: UUID
    ) -> bool:
        """Check if user is admin or owner of club"""
        return await ClubMemberService.check_permission(
            db, club_id, user_id, ClubRole.ADMIN
        )
    
    @staticmethod
    async def can_manage(
        db: AsyncSession,
        club_id: UUID,
        user_id: UUID
    ) -> bool:
        """Check if user can manage club"""
        return await ClubMemberService.check_permission(
            db, club_id, user_id, ClubRole.MANAGER
        )
