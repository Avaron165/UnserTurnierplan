"""
User service - Business logic for user operations
"""
from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """Service for user operations"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, user_in: UserCreate) -> User:
        """Create new user"""
        # Check if user already exists
        existing_user = await UserService.get_by_email(db, user_in.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user
        user = User(
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            phone=user_in.phone,
            language=user_in.language,
            timezone=user_in.timezone,
        )
        
        db.add(user)
        await db.flush()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def update(
        db: AsyncSession, user_id: UUID, user_in: UserUpdate
    ) -> Optional[User]:
        """Update user"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return None
        
        # Update fields
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.flush()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def authenticate(
        db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """Authenticate user"""
        user = await UserService.get_by_email(db, email)
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    async def verify_email(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Verify user email"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return None
        
        user.email_verified = True
        await db.flush()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def update_password(
        db: AsyncSession, user_id: UUID, new_password: str
    ) -> Optional[User]:
        """Update user password"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return None
        
        user.password_hash = get_password_hash(new_password)
        await db.flush()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def delete(db: AsyncSession, user_id: UUID) -> bool:
        """Delete user (soft delete by setting is_active=False)"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return False
        
        user.is_active = False
        await db.flush()
        
        return True
