"""
Club service - Business logic for club operations
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.club import Club, VerificationStatus
from app.models.club_member import ClubMember, ClubRole
from app.models.user import User
from app.schemas.club import ClubCreate, ClubUpdate
import re


class ClubService:
    """Service for club operations"""
    
    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate URL-friendly slug from club name"""
        # Lowercase and replace spaces/special chars
        slug = name.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = slug.strip('-')
        return slug
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession, 
        club_id: UUID,
        include_members: bool = False
    ) -> Optional[Club]:
        """Get club by ID"""
        query = select(Club).where(Club.id == club_id)
        
        if include_members:
            query = query.options(
                selectinload(Club.members).selectinload(ClubMember.user)
            )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_slug(db: AsyncSession, slug: str) -> Optional[Club]:
        """Get club by slug"""
        result = await db.execute(
            select(Club).where(Club.slug == slug)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Club]:
        """Get club by name"""
        result = await db.execute(
            select(Club).where(Club.name == name)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_clubs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        city: Optional[str] = None,
        verified_only: bool = False
    ) -> List[Club]:
        """List clubs with filters"""
        query = select(Club).where(Club.is_active == True)
        
        if search:
            query = query.where(
                Club.name.ilike(f"%{search}%") | 
                Club.description.ilike(f"%{search}%")
            )
        
        if city:
            query = query.where(Club.city.ilike(f"%{city}%"))
        
        if verified_only:
            query = query.where(
                Club.verification_status == VerificationStatus.VERIFIED
            )
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def count_clubs(
        db: AsyncSession,
        search: Optional[str] = None,
        city: Optional[str] = None
    ) -> int:
        """Count clubs with filters"""
        query = select(func.count(Club.id)).where(Club.is_active == True)
        
        if search:
            query = query.where(
                Club.name.ilike(f"%{search}%") | 
                Club.description.ilike(f"%{search}%")
            )
        
        if city:
            query = query.where(Club.city.ilike(f"%{city}%"))
        
        result = await db.execute(query)
        return result.scalar_one()
    
    @staticmethod
    async def create(
        db: AsyncSession, 
        club_in: ClubCreate,
        creator_id: UUID
    ) -> Club:
        """Create new club and add creator as owner"""
        # Check if club with name already exists
        existing_club = await ClubService.get_by_name(db, club_in.name)
        if existing_club:
            raise ValueError("Club with this name already exists")
        
        # Generate unique slug
        base_slug = ClubService.generate_slug(club_in.name)
        slug = base_slug
        counter = 1
        while await ClubService.get_by_slug(db, slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Create club
        club = Club(
            name=club_in.name,
            slug=slug,
            description=club_in.description,
            address=club_in.address,
            city=club_in.city,
            postal_code=club_in.postal_code,
            country=club_in.country,
            phone=club_in.phone,
            email=club_in.email,
            website=club_in.website,
            founded_date=club_in.founded_date,
        )
        
        db.add(club)
        await db.flush()
        await db.refresh(club)
        
        # Add creator as owner
        owner_membership = ClubMember(
            club_id=club.id,
            user_id=creator_id,
            role=ClubRole.OWNER,
        )
        db.add(owner_membership)
        
        # Update member count
        club.member_count = 1
        
        await db.flush()
        await db.refresh(club)
        
        return club
    
    @staticmethod
    async def update(
        db: AsyncSession, 
        club_id: UUID, 
        club_in: ClubUpdate
    ) -> Optional[Club]:
        """Update club"""
        club = await ClubService.get_by_id(db, club_id)
        if not club:
            return None
        
        # Update fields
        update_data = club_in.model_dump(exclude_unset=True)
        
        # Check name uniqueness if name is being changed
        if "name" in update_data and update_data["name"] != club.name:
            existing_club = await ClubService.get_by_name(db, update_data["name"])
            if existing_club:
                raise ValueError("Club with this name already exists")
            
            # Regenerate slug if name changed
            base_slug = ClubService.generate_slug(update_data["name"])
            slug = base_slug
            counter = 1
            while await ClubService.get_by_slug(db, slug):
                if slug == club.slug:  # It's the same club
                    break
                slug = f"{base_slug}-{counter}"
                counter += 1
            club.slug = slug
        
        for field, value in update_data.items():
            setattr(club, field, value)
        
        await db.flush()
        await db.refresh(club)
        
        return club
    
    @staticmethod
    async def delete(db: AsyncSession, club_id: UUID) -> bool:
        """Delete club (soft delete)"""
        club = await ClubService.get_by_id(db, club_id)
        if not club:
            return False
        
        club.is_active = False
        await db.flush()
        
        return True
    
    @staticmethod
    async def update_verification_status(
        db: AsyncSession,
        club_id: UUID,
        status: VerificationStatus,
        notes: Optional[str] = None
    ) -> Optional[Club]:
        """Update club verification status (admin only)"""
        club = await ClubService.get_by_id(db, club_id)
        if not club:
            return None
        
        club.verification_status = status
        club.verification_notes = notes
        
        if status == VerificationStatus.VERIFIED:
            from datetime import date
            club.verification_badge_date = date.today()
        
        await db.flush()
        await db.refresh(club)
        
        return club
