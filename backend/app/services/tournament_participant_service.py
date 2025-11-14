"""
TournamentParticipant service for registration management.

This service handles all participant-related operations including
registration, status updates, and payment management.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tournament import Tournament, TournamentStatus
from app.models.tournament_participant import (
    TournamentParticipant, ParticipantStatus, PaymentStatus
)
from app.models.club import Club
from app.models.user import User
from app.schemas.tournament import (
    TournamentParticipantCreate, TournamentParticipantUpdate,
    ParticipantStatusUpdate, ParticipantPaymentUpdate
)


class TournamentParticipantService:
    """Service for tournament participant operations"""

    @staticmethod
    async def register_participant(
            db: AsyncSession,
            tournament_id: UUID,
            participant_data: TournamentParticipantCreate,
            registered_by: UUID
    ) -> TournamentParticipant:
        """
        Register a participant for a tournament.

        Args:
            db: Database session
            tournament_id: Tournament UUID
            participant_data: Participant registration data
            registered_by: User ID who is registering

        Returns:
            Created participant registration

        Raises:
            ValueError: If registration is not possible
        """
        # Get tournament
        tournament = await db.get(Tournament, tournament_id)
        if not tournament:
            raise ValueError("Tournament not found")

        # Check if registration is open
        if not tournament.can_register:
            if tournament.is_full:
                raise ValueError("Tournament is full")
            elif not tournament.is_registration_open:
                raise ValueError("Registration is not open")

        # Validate participant exists
        if participant_data.participant_club_id:
            club = await db.get(Club, participant_data.participant_club_id)
            if not club:
                raise ValueError("Club not found")
        elif participant_data.participant_user_id:
            user = await db.get(User, participant_data.participant_user_id)
            if not user:
                raise ValueError("User not found")
        else:
            raise ValueError("Either participant_club_id or participant_user_id must be provided")

        # Check if already registered
        existing = await TournamentParticipantService.get_participant_by_ids(
            db, tournament_id,
            participant_data.participant_club_id,
            participant_data.participant_user_id
        )
        if existing:
            raise ValueError("Participant already registered for this tournament")

        # Determine initial status
        initial_status = ParticipantStatus.PENDING.value
        if tournament.is_full:
            initial_status = ParticipantStatus.WAITLIST.value

        # Determine payment status
        payment_status = PaymentStatus.NOT_REQUIRED.value
        payment_amount = None
        if tournament.entry_fee and tournament.entry_fee > 0:
            payment_status = PaymentStatus.PENDING.value
            payment_amount = tournament.entry_fee

        # Create participant
        participant = TournamentParticipant(
            tournament_id=tournament_id,
            **participant_data.model_dump(),
            registered_by=registered_by,
            status=initial_status,
            payment_status=payment_status,
            payment_amount=payment_amount
        )

        db.add(participant)

        # Update tournament participant count if confirmed
        if initial_status == ParticipantStatus.CONFIRMED.value:
            tournament.current_participants += 1

        await db.commit()
        await db.refresh(participant)

        return participant

    @staticmethod
    async def get_participant_by_id(
            db: AsyncSession,
            participant_id: UUID,
            load_relationships: bool = False
    ) -> Optional[TournamentParticipant]:
        """
        Get participant by ID.

        Args:
            db: Database session
            participant_id: Participant UUID
            load_relationships: Whether to load tournament, club, user

        Returns:
            Participant or None if not found
        """
        query = select(TournamentParticipant).where(
            TournamentParticipant.id == participant_id
        )

        if load_relationships:
            query = query.options(
                selectinload(TournamentParticipant.tournament),
                selectinload(TournamentParticipant.participant_club),
                selectinload(TournamentParticipant.participant_user)
            )

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_participant_by_ids(
            db: AsyncSession,
            tournament_id: UUID,
            club_id: Optional[UUID] = None,
            user_id: Optional[UUID] = None
    ) -> Optional[TournamentParticipant]:
        """
        Get participant by tournament and participant IDs.

        Args:
            db: Database session
            tournament_id: Tournament UUID
            club_id: Club UUID (for team tournaments)
            user_id: User UUID (for individual tournaments)

        Returns:
            Participant or None if not found
        """
        conditions = [TournamentParticipant.tournament_id == tournament_id]

        if club_id:
            conditions.append(TournamentParticipant.participant_club_id == club_id)
        if user_id:
            conditions.append(TournamentParticipant.participant_user_id == user_id)

        query = select(TournamentParticipant).where(and_(*conditions))
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tournament_participants(
            db: AsyncSession,
            tournament_id: UUID,
            status: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[TournamentParticipant]:
        """
        Get all participants for a tournament.

        Args:
            db: Database session
            tournament_id: Tournament UUID
            status: Optional status filter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of participants
        """
        query = select(TournamentParticipant).where(
            TournamentParticipant.tournament_id == tournament_id
        )

        if status:
            query = query.where(TournamentParticipant.status == status)

        # Order by registration date
        query = query.order_by(TournamentParticipant.registration_date.asc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_user_participations(
            db: AsyncSession,
            user_id: UUID,
            include_club_participations: bool = True,
            skip: int = 0,
            limit: int = 100
    ) -> List[TournamentParticipant]:
        """
        Get all tournament participations for a user.

        Args:
            db: Database session
            user_id: User UUID
            include_club_participations: Include tournaments where user's club participates
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of participations
        """
        conditions = [TournamentParticipant.participant_user_id == user_id]

        if include_club_participations:
            # Would need to join with club_members here
            # For now, just return direct user participations
            pass

        query = select(TournamentParticipant).where(or_(*conditions))
        query = query.order_by(TournamentParticipant.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_participant(
            db: AsyncSession,
            participant_id: UUID,
            participant_data: TournamentParticipantUpdate
    ) -> Optional[TournamentParticipant]:
        """
        Update participant registration.

        Args:
            db: Database session
            participant_id: Participant UUID
            participant_data: Update data

        Returns:
            Updated participant or None if not found
        """
        participant = await TournamentParticipantService.get_participant_by_id(
            db, participant_id
        )
        if not participant:
            return None

        # Update only provided fields
        update_data = participant_data.model_dump(exclude_unset=True)

        # Handle status change separately if provided
        old_status = participant.status

        for field, value in update_data.items():
            setattr(participant, field, value)

        # Update tournament participant count if status changed
        if 'status' in update_data:
            new_status = update_data['status']
            await TournamentParticipantService._update_tournament_count(
                db, participant.tournament_id, old_status, new_status
            )

        await db.commit()
        await db.refresh(participant)

        return participant

    @staticmethod
    async def update_participant_status(
            db: AsyncSession,
            participant_id: UUID,
            status_update: ParticipantStatusUpdate
    ) -> Optional[TournamentParticipant]:
        """
        Update participant status.

        Args:
            db: Database session
            participant_id: Participant UUID
            status_update: Status update data

        Returns:
            Updated participant or None if not found
        """
        participant = await TournamentParticipantService.get_participant_by_id(
            db, participant_id
        )
        if not participant:
            return None

        old_status = participant.status
        new_status = status_update.status

        participant.status = new_status
        if status_update.notes:
            participant.notes = status_update.notes

        # Update tournament participant count
        await TournamentParticipantService._update_tournament_count(
            db, participant.tournament_id, old_status, new_status
        )

        await db.commit()
        await db.refresh(participant)

        return participant

    @staticmethod
    async def update_payment_status(
            db: AsyncSession,
            participant_id: UUID,
            payment_update: ParticipantPaymentUpdate
    ) -> Optional[TournamentParticipant]:
        """
        Update payment status.

        Args:
            db: Database session
            participant_id: Participant UUID
            payment_update: Payment update data

        Returns:
            Updated participant or None if not found
        """
        participant = await TournamentParticipantService.get_participant_by_id(
            db, participant_id
        )
        if not participant:
            return None

        participant.payment_status = payment_update.payment_status

        if payment_update.payment_amount:
            participant.payment_amount = payment_update.payment_amount

        if payment_update.payment_reference:
            participant.payment_reference = payment_update.payment_reference

        # Set payment date if status is paid
        if payment_update.payment_status == PaymentStatus.PAID.value:
            participant.payment_date = datetime.utcnow()

        await db.commit()
        await db.refresh(participant)

        return participant

    @staticmethod
    async def remove_participant(
            db: AsyncSession,
            participant_id: UUID
    ) -> bool:
        """
        Remove participant from tournament.

        Args:
            db: Database session
            participant_id: Participant UUID

        Returns:
            True if removed, False if not found
        """
        participant = await TournamentParticipantService.get_participant_by_id(
            db, participant_id
        )
        if not participant:
            return False

        tournament_id = participant.tournament_id
        old_status = participant.status

        # Delete participant
        await db.delete(participant)

        # Update tournament count if participant was confirmed
        if old_status == ParticipantStatus.CONFIRMED.value:
            tournament = await db.get(Tournament, tournament_id)
            if tournament:
                tournament.current_participants = max(0, tournament.current_participants - 1)

        await db.commit()

        return True

    @staticmethod
    async def _update_tournament_count(
            db: AsyncSession,
            tournament_id: UUID,
            old_status: str,
            new_status: str
    ):
        """
        Update tournament participant count based on status change.

        Args:
            db: Database session
            tournament_id: Tournament UUID
            old_status: Previous status
            new_status: New status
        """
        tournament = await db.get(Tournament, tournament_id)
        if not tournament:
            return

        # Increment count if status changed to confirmed
        if (old_status != ParticipantStatus.CONFIRMED.value and
                new_status == ParticipantStatus.CONFIRMED.value):
            tournament.current_participants += 1

        # Decrement count if status changed from confirmed
        elif (old_status == ParticipantStatus.CONFIRMED.value and
              new_status != ParticipantStatus.CONFIRMED.value):
            tournament.current_participants = max(0, tournament.current_participants - 1)

    @staticmethod
    async def can_user_modify_participant(
            db: AsyncSession,
            participant_id: UUID,
            user_id: UUID
    ) -> bool:
        """
        Check if user can modify participant registration.

        User can modify if:
        - User registered the participant
        - User is tournament creator/manager
        - User is from the participating club (for club registrations)

        Args:
            db: Database session
            participant_id: Participant UUID
            user_id: User UUID

        Returns:
            True if user can modify, False otherwise
        """
        participant = await TournamentParticipantService.get_participant_by_id(
            db, participant_id, load_relationships=True
        )
        if not participant:
            return False

        # Check if user registered this participant
        if participant.registered_by == user_id:
            return True

        # Check if user can manage tournament
        from app.services.tournament_service import TournamentService
        if await TournamentService.can_user_manage_tournament(
                db, participant.tournament_id, user_id
        ):
            return True

        # Check if user is from participating club (for club participations)
        if participant.participant_club_id:
            from app.models.club_member import ClubMember
            result = await db.execute(
                select(ClubMember).where(
                    and_(
                        ClubMember.club_id == participant.participant_club_id,
                        ClubMember.user_id == user_id,
                        ClubMember.role.in_(["owner", "admin", "manager"])
                    )
                )
            )
            if result.scalar_one_or_none():
                return True

        return False