"""
Match service for business logic.

This service handles all match-related operations including CRUD,
scoring, status management, and match participant management.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.match import Match, MatchStatus
from app.models.match_participant import MatchParticipant
from app.models.tournament import Tournament
from app.models.tournament_participant import TournamentParticipant
from app.schemas.match import (
    MatchCreate, MatchUpdate, MatchScoreUpdate, MatchStatusUpdate,
    ParticipantScoreEntry
)


class MatchService:
    """Service for match operations."""
    
    @staticmethod
    async def create_match(
        db: AsyncSession,
        match_data: MatchCreate
    ) -> Match:
        """
        Create a new match with participants.
        
        Args:
            db: Database session
            match_data: Match creation data
            
        Returns:
            Created match
            
        Raises:
            ValueError: If tournament doesn't exist or participants invalid
        """
        # Verify tournament exists
        tournament = await db.get(Tournament, match_data.tournament_id)
        if not tournament:
            raise ValueError("Tournament not found")
        
        # Verify all participants exist and belong to this tournament
        for participant_id in match_data.participant_ids:
            result = await db.execute(
                select(TournamentParticipant).where(
                    and_(
                        TournamentParticipant.id == participant_id,
                        TournamentParticipant.tournament_id == match_data.tournament_id
                    )
                )
            )
            participant = result.scalar_one_or_none()
            if not participant:
                raise ValueError(f"Participant {participant_id} not found in tournament")
        
        # Create match
        match = Match(
            tournament_id=match_data.tournament_id,
            round_number=match_data.round_number,
            match_number=match_data.match_number,
            round_name=match_data.round_name,
            group_name=match_data.group_name,
            phase=match_data.phase,
            scheduled_start=match_data.scheduled_start,
            scheduled_end=match_data.scheduled_end,
            venue_name=match_data.venue_name,
            court_field_number=match_data.court_field_number,
            match_format=match_data.match_format,
            duration_minutes=match_data.duration_minutes,
            notes=match_data.notes,
            requires_referee=match_data.requires_referee,
            status=MatchStatus.SCHEDULED.value,
            is_finished=False
        )
        
        db.add(match)
        await db.flush()  # Get match ID
        
        # Add participants
        num_participants = len(match_data.participant_ids)
        for idx, participant_id in enumerate(match_data.participant_ids, start=1):
            # Determine team_side for 2-participant matches
            team_side = None
            if num_participants == 2:
                team_side = "home" if idx == 1 else "away"
            
            match_participant = MatchParticipant(
                match_id=match.id,
                participant_id=participant_id,
                slot_number=idx,
                team_side=team_side,
                is_winner=False,
                is_disqualified=False
            )
            db.add(match_participant)
        
        await db.commit()
        await db.refresh(match)
        
        return match
    
    @staticmethod
    async def get_match_by_id(
        db: AsyncSession,
        match_id: UUID,
        load_relationships: bool = False
    ) -> Optional[Match]:
        """
        Get match by ID.
        
        Args:
            db: Database session
            match_id: Match UUID
            load_relationships: Whether to load participants, tournament, etc.
            
        Returns:
            Match or None if not found
        """
        query = select(Match).where(Match.id == match_id)
        
        if load_relationships:
            query = query.options(
                selectinload(Match.participants).selectinload(MatchParticipant.participant),
                selectinload(Match.tournament),
                selectinload(Match.winner),
                selectinload(Match.referee)
            )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_tournament_matches(
        db: AsyncSession,
        tournament_id: UUID,
        round_number: Optional[int] = None,
        group_name: Optional[str] = None,
        phase: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Match]:
        """
        Get matches for a tournament with filters.
        
        Args:
            db: Database session
            tournament_id: Tournament UUID
            round_number: Optional round filter
            group_name: Optional group filter
            phase: Optional phase filter
            status: Optional status filter
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of matches
        """
        query = select(Match).where(Match.tournament_id == tournament_id)
        
        if round_number is not None:
            query = query.where(Match.round_number == round_number)
        
        if group_name is not None:
            query = query.where(Match.group_name == group_name)
        
        if phase is not None:
            query = query.where(Match.phase == phase)
        
        if status is not None:
            query = query.where(Match.status == status)
        
        query = query.order_by(Match.round_number, Match.match_number)
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_match(
        db: AsyncSession,
        match_id: UUID,
        match_data: MatchUpdate
    ) -> Match:
        """
        Update match details.
        
        Args:
            db: Database session
            match_id: Match UUID
            match_data: Update data
            
        Returns:
            Updated match
            
        Raises:
            ValueError: If match not found
        """
        match = await MatchService.get_match_by_id(db, match_id)
        if not match:
            raise ValueError("Match not found")
        
        # Update fields
        update_data = match_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(match, field, value)
        
        match.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(match)
        
        return match
    
    @staticmethod
    async def update_match_score(
        db: AsyncSession,
        match_id: UUID,
        score_data: MatchScoreUpdate
    ) -> Match:
        """
        Update match score and determine winner.
        
        Args:
            db: Database session
            match_id: Match UUID
            score_data: Score update data
            
        Returns:
            Updated match
            
        Raises:
            ValueError: If match not found or score invalid
        """
        match = await MatchService.get_match_by_id(db, match_id, load_relationships=True)
        if not match:
            raise ValueError("Match not found")
        
        # Update participant scores
        for score_entry in score_data.participant_scores:
            # Find match participant
            match_participant = next(
                (mp for mp in match.participants if str(mp.participant_id) == str(score_entry.participant_id)),
                None
            )
            
            if not match_participant:
                raise ValueError(f"Participant {score_entry.participant_id} not in match")
            
            # Update scores
            if score_entry.score_value is not None:
                match_participant.score_value = score_entry.score_value
            
            if score_entry.final_position is not None:
                match_participant.final_position = score_entry.final_position
            
            # Parse result_time if provided as string
            if score_entry.result_time:
                # Convert string time to timedelta (e.g., "1:23.456" -> timedelta)
                match_participant.result_time = MatchService._parse_time_string(score_entry.result_time)
            
            match_participant.is_winner = score_entry.is_winner
            match_participant.is_disqualified = score_entry.is_disqualified
            
            if score_entry.detailed_score:
                match_participant.detailed_score = score_entry.detailed_score
        
        # Update overall match score data
        if score_data.score_data:
            match.score_data = score_data.score_data
        
        # Set winner
        if score_data.winner_participant_id:
            match.winner_participant_id = score_data.winner_participant_id
            match.is_finished = True
            match.status = MatchStatus.COMPLETED.value
        
        match.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(match)
        
        return match
    
    @staticmethod
    async def update_match_status(
        db: AsyncSession,
        match_id: UUID,
        status_update: MatchStatusUpdate
    ) -> Match:
        """
        Update match status.
        
        Args:
            db: Database session
            match_id: Match UUID
            status_update: Status update data
            
        Returns:
            Updated match
            
        Raises:
            ValueError: If match not found
        """
        match = await MatchService.get_match_by_id(db, match_id)
        if not match:
            raise ValueError("Match not found")
        
        match.status = status_update.status
        
        # Update timestamps based on status
        if status_update.status == MatchStatus.IN_PROGRESS.value:
            match.actual_start = datetime.utcnow()
        elif status_update.status == MatchStatus.COMPLETED.value:
            if not match.actual_end:
                match.actual_end = datetime.utcnow()
            match.is_finished = True
        
        if status_update.notes:
            match.notes = status_update.notes
        
        match.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(match)
        
        return match
    
    @staticmethod
    async def delete_match(
        db: AsyncSession,
        match_id: UUID
    ) -> bool:
        """
        Delete a match.
        
        Args:
            db: Database session
            match_id: Match UUID
            
        Returns:
            True if deleted, False if not found
        """
        match = await MatchService.get_match_by_id(db, match_id)
        if not match:
            return False
        
        await db.delete(match)
        await db.commit()
        
        return True
    
    @staticmethod
    def _parse_time_string(time_str: str) -> timedelta:
        """
        Parse time string to timedelta.
        
        Supports formats:
        - "1:23.456" (minutes:seconds.milliseconds)
        - "1:23:45.678" (hours:minutes:seconds.milliseconds)
        
        Args:
            time_str: Time string
            
        Returns:
            timedelta object
        """
        try:
            parts = time_str.split(":")
            if len(parts) == 2:
                # Format: MM:SS.mmm
                minutes = int(parts[0])
                seconds = float(parts[1])
                return timedelta(minutes=minutes, seconds=seconds)
            elif len(parts) == 3:
                # Format: HH:MM:SS.mmm
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return timedelta(hours=hours, minutes=minutes, seconds=seconds)
            else:
                raise ValueError("Invalid time format")
        except Exception:
            # If parsing fails, return 0
            return timedelta(0)
