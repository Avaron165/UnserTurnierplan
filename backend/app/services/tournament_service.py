"""
Tournament service for business logic.

This service handles all tournament-related operations including CRUD,
lifecycle management, and permission checks.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from slugify import slugify

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tournament import Tournament, TournamentStatus, SportType, TournamentType
from app.models.tournament_participant import TournamentParticipant
from app.models.club import Club
from app.models.club_member import ClubMember
from app.schemas.tournament import (
    TournamentCreate, TournamentUpdate, TournamentStatusUpdate, TournamentFilters
)


class TournamentService:
    """Service for tournament operations"""
    
    @staticmethod
    async def create_tournament(
        db: AsyncSession,
        tournament_data: TournamentCreate,
        creator_id: UUID
    ) -> Tournament:
        """
        Create a new tournament.
        
        Args:
            db: Database session
            tournament_data: Tournament creation data
            creator_id: ID of the user creating the tournament
            
        Returns:
            Created tournament
            
        Raises:
            ValueError: If club doesn't exist or slug already exists
        """
        # Verify club exists
        club = await db.get(Club, tournament_data.club_id)
        if not club:
            raise ValueError("Club not found")
        
        # Generate unique slug
        base_slug = slugify(tournament_data.name)
        slug = base_slug
        counter = 1
        
        while True:
            result = await db.execute(
                select(Tournament).where(Tournament.slug == slug)
            )
            if not result.scalar_one_or_none():
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Create tournament
        tournament = Tournament(
            **tournament_data.model_dump(exclude={'club_id'}),
            club_id=tournament_data.club_id,
            created_by=creator_id,
            slug=slug,
            status=TournamentStatus.DRAFT.value,
            current_participants=0,
            is_active=True
        )
        
        db.add(tournament)
        await db.commit()
        await db.refresh(tournament)
        
        return tournament
    
    @staticmethod
    async def get_tournament_by_id(
        db: AsyncSession,
        tournament_id: UUID,
        load_relationships: bool = False
    ) -> Optional[Tournament]:
        """
        Get tournament by ID.
        
        Args:
            db: Database session
            tournament_id: Tournament UUID
            load_relationships: Whether to load club and participants
            
        Returns:
            Tournament or None if not found
        """
        query = select(Tournament).where(Tournament.id == tournament_id)
        
        if load_relationships:
            query = query.options(
                selectinload(Tournament.club),
                selectinload(Tournament.creator),
                selectinload(Tournament.participants)
            )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_tournament_by_slug(
        db: AsyncSession,
        slug: str,
        load_relationships: bool = False
    ) -> Optional[Tournament]:
        """
        Get tournament by slug.
        
        Args:
            db: Database session
            slug: Tournament slug
            load_relationships: Whether to load club and participants
            
        Returns:
            Tournament or None if not found
        """
        query = select(Tournament).where(Tournament.slug == slug)
        
        if load_relationships:
            query = query.options(
                selectinload(Tournament.club),
                selectinload(Tournament.creator),
                selectinload(Tournament.participants)
            )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_tournaments(
        db: AsyncSession,
        filters: Optional[TournamentFilters] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tournament]:
        """
        Get tournaments with optional filters.
        
        Args:
            db: Database session
            filters: Optional filter criteria
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of tournaments
        """
        query = select(Tournament).where(Tournament.is_active == True)
        
        # Apply filters
        if filters:
            if filters.sport_type:
                query = query.where(Tournament.sport_type == filters.sport_type)
            
            if filters.tournament_type:
                query = query.where(Tournament.tournament_type == filters.tournament_type)
            
            if filters.status:
                query = query.where(Tournament.status == filters.status)
            
            if filters.city:
                query = query.where(Tournament.city.ilike(f"%{filters.city}%"))
            
            if filters.min_start_date:
                query = query.where(Tournament.start_date >= filters.min_start_date)
            
            if filters.max_start_date:
                query = query.where(Tournament.start_date <= filters.max_start_date)
            
            if filters.is_public is not None:
                query = query.where(Tournament.is_public == filters.is_public)
            
            if filters.club_id:
                query = query.where(Tournament.club_id == filters.club_id)
        
        # Order by start date (upcoming first)
        query = query.order_by(Tournament.start_date.asc())
        
        # Pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_tournaments_by_club(
        db: AsyncSession,
        club_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tournament]:
        """
        Get all tournaments for a specific club.
        
        Args:
            db: Database session
            club_id: Club UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of tournaments
        """
        query = select(Tournament).where(
            and_(
                Tournament.club_id == club_id,
                Tournament.is_active == True
            )
        ).order_by(Tournament.start_date.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_tournaments_by_creator(
        db: AsyncSession,
        creator_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tournament]:
        """
        Get all tournaments created by a specific user.
        
        Args:
            db: Database session
            creator_id: User UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of tournaments
        """
        query = select(Tournament).where(
            and_(
                Tournament.created_by == creator_id,
                Tournament.is_active == True
            )
        ).order_by(Tournament.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_tournament(
        db: AsyncSession,
        tournament_id: UUID,
        tournament_data: TournamentUpdate
    ) -> Optional[Tournament]:
        """
        Update tournament.
        
        Args:
            db: Database session
            tournament_id: Tournament UUID
            tournament_data: Update data
            
        Returns:
            Updated tournament or None if not found
        """
        tournament = await TournamentService.get_tournament_by_id(db, tournament_id)
        if not tournament:
            return None
        
        # Update only provided fields
        update_data = tournament_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tournament, field, value)
        
        await db.commit()
        await db.refresh(tournament)
        
        return tournament
    
    @staticmethod
    async def update_tournament_status(
        db: AsyncSession,
        tournament_id: UUID,
        status_update: TournamentStatusUpdate
    ) -> Optional[Tournament]:
        """
        Update tournament status with validation.
        
        Args:
            db: Database session
            tournament_id: Tournament UUID
            status_update: Status update data
            
        Returns:
            Updated tournament or None if not found
            
        Raises:
            ValueError: If status transition is invalid
        """
        tournament = await TournamentService.get_tournament_by_id(db, tournament_id)
        if not tournament:
            return None
        
        # Validate status transitions
        current_status = tournament.status
        new_status = status_update.status
        
        # Define valid transitions
        valid_transitions = {
            TournamentStatus.DRAFT.value: [
                TournamentStatus.PUBLISHED.value,
                TournamentStatus.CANCELLED.value
            ],
            TournamentStatus.PUBLISHED.value: [
                TournamentStatus.REGISTRATION_OPEN.value,
                TournamentStatus.CANCELLED.value
            ],
            TournamentStatus.REGISTRATION_OPEN.value: [
                TournamentStatus.ACTIVE.value,
                TournamentStatus.CANCELLED.value
            ],
            TournamentStatus.ACTIVE.value: [
                TournamentStatus.COMPLETED.value,
                TournamentStatus.CANCELLED.value
            ],
            TournamentStatus.COMPLETED.value: [],  # Final state
            TournamentStatus.CANCELLED.value: []  # Final state
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise ValueError(
                f"Invalid status transition from {current_status} to {new_status}"
            )
        
        tournament.status = new_status
        
        await db.commit()
        await db.refresh(tournament)
        
        return tournament
    
    @staticmethod
    async def delete_tournament(
        db: AsyncSession,
        tournament_id: UUID
    ) -> bool:
        """
        Soft delete tournament (set is_active to False).
        
        Args:
            db: Database session
            tournament_id: Tournament UUID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ValueError: If tournament has participants or is not in draft status
        """
        tournament = await TournamentService.get_tournament_by_id(db, tournament_id)
        if not tournament:
            return False
        
        # Check if tournament can be deleted
        if tournament.current_participants > 0:
            raise ValueError("Cannot delete tournament with registered participants")
        
        if tournament.status not in [TournamentStatus.DRAFT.value, TournamentStatus.CANCELLED.value]:
            raise ValueError("Can only delete tournaments in draft or cancelled status")
        
        tournament.is_active = False
        
        await db.commit()
        
        return True
    
    @staticmethod
    async def can_user_create_tournament(
        db: AsyncSession,
        club_id: UUID,
        user_id: UUID,
        department: Optional[str] = None
    ) -> bool:
        """
        Check if user can create tournaments for a club/department.
        
        User can create if:
        - User is owner/admin of the club (all departments)
        - User is manager of the specified department
        
        Args:
            db: Database session
            club_id: Club UUID
            user_id: User UUID
            department: Optional department name
            
        Returns:
            True if user can create, False otherwise
        """
        # Check club membership
        result = await db.execute(
            select(ClubMember).where(
                and_(
                    ClubMember.club_id == club_id,
                    ClubMember.user_id == user_id
                )
            )
        )
        club_member = result.scalar_one_or_none()
        
        if not club_member:
            return False
        
        # Owner/Admin can create tournaments for any department
        if club_member.role in ["owner", "admin"]:
            return True
        
        # Manager can create tournaments for their department
        if club_member.role == "manager":
            if not department:
                return False  # Manager must specify department
            return club_member.department == department
        
        return False
    
    @staticmethod
    async def can_user_manage_tournament(
        db: AsyncSession,
        tournament_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Check if user can manage tournament.
        
        User can manage if:
        - User is the tournament creator
        - User is owner/admin of the hosting club (all departments)
        - User is manager of the tournament's department
        
        Args:
            db: Database session
            tournament_id: Tournament UUID
            user_id: User UUID
            
        Returns:
            True if user can manage, False otherwise
        """
        tournament = await TournamentService.get_tournament_by_id(db, tournament_id)
        if not tournament:
            return False
        
        # Check if user is creator
        if tournament.created_by == user_id:
            return True
        
        # Check club membership and role
        result = await db.execute(
            select(ClubMember).where(
                and_(
                    ClubMember.club_id == tournament.club_id,
                    ClubMember.user_id == user_id
                )
            )
        )
        club_member = result.scalar_one_or_none()
        
        if not club_member:
            return False
        
        # Owner/Admin can manage all tournaments
        if club_member.role in ["owner", "admin"]:
            return True
        
        # Manager can manage tournaments in their department
        if club_member.role == "manager":
            # If tournament has no department, only owner/admin can manage
            if not tournament.department:
                return False
            # Check if manager's department matches tournament's department
            return club_member.department == tournament.department
        
        return False
    
    @staticmethod
    async def get_tournament_statistics(
        db: AsyncSession,
        tournament_id: UUID
    ) -> dict:
        """
        Get tournament statistics.
        
        Args:
            db: Database session
            tournament_id: Tournament UUID
            
        Returns:
            Dictionary with tournament statistics
        """
        tournament = await TournamentService.get_tournament_by_id(
            db, tournament_id, load_relationships=True
        )
        if not tournament:
            return {}
        
        # Count participants by status
        result = await db.execute(
            select(
                TournamentParticipant.status,
                func.count(TournamentParticipant.id)
            ).where(
                TournamentParticipant.tournament_id == tournament_id
            ).group_by(TournamentParticipant.status)
        )
        status_counts = dict(result.all())
        
        return {
            "total_participants": tournament.current_participants,
            "max_participants": tournament.max_participants,
            "available_spots": tournament.max_participants - tournament.current_participants,
            "is_full": tournament.is_full,
            "participants_by_status": status_counts,
            "registration_open": tournament.is_registration_open,
            "can_register": tournament.can_register,
        }
