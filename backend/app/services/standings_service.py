"""
Tournament standings calculation service.

This service calculates and manages tournament standings/rankings
based on completed matches. Implements caching for performance.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tournament_standings import TournamentStandings
from app.models.match import Match
from app.models.match_participant import MatchParticipant
from app.models.tournament_participant import TournamentParticipant


class StandingsService:
    """Service for calculating and managing tournament standings."""
    
    @staticmethod
    async def calculate_standings(
        db: AsyncSession,
        tournament_id: UUID,
        group_name: Optional[str] = None
    ) -> List[TournamentStandings]:
        """
        Calculate tournament standings based on completed matches.
        
        Recalculates from scratch based on all completed matches.
        Updates cached standings in database.
        
        Args:
            db: Database session
            tournament_id: Tournament UUID
            group_name: Optional group filter (for group stage)
            
        Returns:
            List of standings (sorted by rank)
        """
        # Get all participants
        query = select(TournamentParticipant).where(
            TournamentParticipant.tournament_id == tournament_id
        )
        
        if group_name:
            query = query.where(TournamentParticipant.group_assignment == group_name)
        
        result = await db.execute(query)
        participants = list(result.scalars().all())
        
        # Initialize or get standings for each participant
        standings_dict = {}
        for participant in participants:
            standing = await StandingsService._get_or_create_standing(
                db, tournament_id, participant.id, group_name
            )
            # Reset statistics (recalculate from scratch)
            standing.matches_played = 0
            standing.matches_won = 0
            standing.matches_drawn = 0
            standing.matches_lost = 0
            standing.points = 0
            standing.score_for = Decimal(0)
            standing.score_against = Decimal(0)
            standing.score_difference = Decimal(0)
            
            standings_dict[str(participant.id)] = standing
        
        # Get completed matches
        matches_query = select(Match).where(
            and_(
                Match.tournament_id == tournament_id,
                Match.is_finished == True
            )
        ).options(
            selectinload(Match.participants)
        )
        
        if group_name:
            matches_query = matches_query.where(Match.group_name == group_name)
        
        result = await db.execute(matches_query)
        matches = list(result.scalars().all())
        
        # Calculate stats for each match
        for match in matches:
            # Skip bye matches
            if match.is_bye:
                continue
            
            match_participants = match.participants
            
            # Determine match result type
            if len(match_participants) == 2:
                # Standard 2-player match
                await StandingsService._process_two_player_match(
                    match_participants, standings_dict
                )
            else:
                # Multi-player match (races, etc.)
                await StandingsService._process_multi_player_match(
                    match_participants, standings_dict
                )
        
        # Sort standings and assign ranks
        standings_list = list(standings_dict.values())
        standings_list.sort(
            key=lambda s: (
                -s.points,  # Higher points first
                -s.score_difference,  # Better goal difference
                -s.score_for  # More goals scored
            )
        )
        
        # Assign ranks
        for rank, standing in enumerate(standings_list, start=1):
            standing.previous_rank = standing.current_rank
            standing.current_rank = rank
        
        await db.commit()
        
        return standings_list
    
    @staticmethod
    async def _get_or_create_standing(
        db: AsyncSession,
        tournament_id: UUID,
        participant_id: UUID,
        group_name: Optional[str]
    ) -> TournamentStandings:
        """
        Get existing standing or create new one.
        
        Args:
            db: Database session
            tournament_id: Tournament UUID
            participant_id: Participant UUID
            group_name: Group name or None
            
        Returns:
            TournamentStandings object
        """
        query = select(TournamentStandings).where(
            and_(
                TournamentStandings.tournament_id == tournament_id,
                TournamentStandings.participant_id == participant_id
            )
        )
        
        if group_name:
            query = query.where(TournamentStandings.group_name == group_name)
        else:
            query = query.where(TournamentStandings.group_name.is_(None))
        
        result = await db.execute(query)
        standing = result.scalar_one_or_none()
        
        if not standing:
            standing = TournamentStandings(
                tournament_id=tournament_id,
                participant_id=participant_id,
                group_name=group_name,
                matches_played=0,
                matches_won=0,
                matches_drawn=0,
                matches_lost=0,
                points=0,
                score_for=Decimal(0),
                score_against=Decimal(0),
                score_difference=Decimal(0)
            )
            db.add(standing)
            await db.flush()
        
        return standing
    
    @staticmethod
    async def _process_two_player_match(
        match_participants: List[MatchParticipant],
        standings_dict: Dict[str, TournamentStandings]
    ):
        """
        Process a standard 2-player match.
        
        Args:
            match_participants: List of match participants (should be 2)
            standings_dict: Dictionary of standings by participant ID
        """
        if len(match_participants) != 2:
            return
        
        mp1, mp2 = match_participants
        
        standing1 = standings_dict.get(str(mp1.participant_id))
        standing2 = standings_dict.get(str(mp2.participant_id))
        
        if not standing1 or not standing2:
            return
        
        # Update matches played
        standing1.matches_played += 1
        standing2.matches_played += 1
        
        # Update scores
        score1 = mp1.score_value or Decimal(0)
        score2 = mp2.score_value or Decimal(0)
        
        standing1.score_for += score1
        standing1.score_against += score2
        standing2.score_for += score2
        standing2.score_against += score1
        
        # Determine result
        if mp1.is_winner:
            # Player 1 wins
            standing1.matches_won += 1
            standing1.points += 3
            standing2.matches_lost += 1
        elif mp2.is_winner:
            # Player 2 wins
            standing2.matches_won += 1
            standing2.points += 3
            standing1.matches_lost += 1
        else:
            # Check for draw
            if score1 == score2:
                standing1.matches_drawn += 1
                standing1.points += 1
                standing2.matches_drawn += 1
                standing2.points += 1
            else:
                # One has higher score but no explicit winner marked
                # Assume higher score wins
                if score1 > score2:
                    standing1.matches_won += 1
                    standing1.points += 3
                    standing2.matches_lost += 1
                else:
                    standing2.matches_won += 1
                    standing2.points += 3
                    standing1.matches_lost += 1
        
        # Update score difference
        standing1.score_difference = standing1.score_for - standing1.score_against
        standing2.score_difference = standing2.score_for - standing2.score_against
    
    @staticmethod
    async def _process_multi_player_match(
        match_participants: List[MatchParticipant],
        standings_dict: Dict[str, TournamentStandings]
    ):
        """
        Process a multi-player match (races, etc.).
        
        For races and multi-player games, we use final_position.
        Points awarded based on position (e.g., F1-style: 25, 18, 15, 12, 10, 8, 6, 4, 2, 1)
        
        Args:
            match_participants: List of match participants
            standings_dict: Dictionary of standings by participant ID
        """
        # Simple point system for now (can be customized)
        # Winner gets 25 points, 2nd gets 18, 3rd gets 15, etc.
        points_by_position = {
            1: 25, 2: 18, 3: 15, 4: 12, 5: 10,
            6: 8, 7: 6, 8: 4, 9: 2, 10: 1
        }
        
        for mp in match_participants:
            standing = standings_dict.get(str(mp.participant_id))
            if not standing:
                continue
            
            standing.matches_played += 1
            
            # Award points based on position
            if mp.final_position and mp.final_position in points_by_position:
                position_points = points_by_position[mp.final_position]
                standing.points += position_points
            
            # Count wins (1st place)
            if mp.final_position == 1 or mp.is_winner:
                standing.matches_won += 1
            
            # Update score_for if available
            if mp.score_value:
                standing.score_for += mp.score_value
    
    @staticmethod
    async def get_standings(
        db: AsyncSession,
        tournament_id: UUID,
        group_name: Optional[str] = None
    ) -> List[TournamentStandings]:
        """
        Get current standings (from cache).
        
        Returns cached standings without recalculation.
        Use calculate_standings() to update.
        
        Args:
            db: Database session
            tournament_id: Tournament UUID
            group_name: Optional group filter
            
        Returns:
            List of standings (sorted by rank)
        """
        query = select(TournamentStandings).where(
            TournamentStandings.tournament_id == tournament_id
        ).options(
            selectinload(TournamentStandings.participant)
        )
        
        if group_name:
            query = query.where(TournamentStandings.group_name == group_name)
        else:
            query = query.where(TournamentStandings.group_name.is_(None))
        
        query = query.order_by(TournamentStandings.current_rank.nullslast())
        
        result = await db.execute(query)
        return list(result.scalars().all())
