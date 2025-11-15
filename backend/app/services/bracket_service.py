"""
Bracket generation service for tournaments.

This service generates match brackets and schedules for different tournament types:
- Knockout (single/double elimination)
- Round-Robin (everyone plays everyone)
- Group Stage + Knockout (future)
"""

import math
import random
from typing import List, Tuple, Optional
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tournament import Tournament, TournamentType
from app.models.tournament_participant import TournamentParticipant
from app.models.match import Match, MatchStatus
from app.models.match_participant import MatchParticipant


class BracketService:
    """Service for generating tournament brackets and schedules."""
    
    @staticmethod
    async def generate_knockout_bracket(
        db: AsyncSession,
        tournament_id: UUID,
        shuffle_seeds: bool = False
    ) -> List[Match]:
        """
        Generate single-elimination knockout bracket.
        
        Creates matches for all rounds up to the final.
        Participants are matched based on seeding (or randomized).
        
        Algorithm:
        1. Get confirmed participants
        2. Calculate rounds needed (log2(n))
        3. Generate first round with byes if needed
        4. Generate empty subsequent rounds with dependencies
        
        Args:
            db: Database session
            tournament_id: Tournament UUID
            shuffle_seeds: Randomize seeds if True
            
        Returns:
            List of generated matches
            
        Raises:
            ValueError: If tournament not found or insufficient participants
        """
        # Get tournament
        tournament = await db.get(Tournament, tournament_id)
        if not tournament:
            raise ValueError("Tournament not found")
        
        # Get confirmed participants (ordered by seed)
        result = await db.execute(
            select(TournamentParticipant)
            .where(
                and_(
                    TournamentParticipant.tournament_id == tournament_id,
                    TournamentParticipant.status == "confirmed"
                )
            )
            .order_by(TournamentParticipant.seed.nullslast(), TournamentParticipant.created_at)
        )
        participants = list(result.scalars().all())
        
        if len(participants) < 2:
            raise ValueError("Need at least 2 confirmed participants for knockout bracket")
        
        # Shuffle if requested
        if shuffle_seeds:
            random.shuffle(participants)
        
        # Calculate tournament structure
        num_participants = len(participants)
        num_rounds = math.ceil(math.log2(num_participants))
        next_power_of_2 = 2 ** num_rounds
        num_byes = next_power_of_2 - num_participants
        
        matches = []
        round_names = BracketService._get_round_names(num_rounds)
        
        # Generate first round with byes if needed
        first_round_matches = []
        match_number = 1
        
        for i in range(0, num_participants, 2):
            if i + 1 < num_participants:
                # Regular match (two participants)
                match = Match(
                    tournament_id=tournament_id,
                    round_number=1,
                    match_number=match_number,
                    round_name=round_names[0],
                    phase="knockout",
                    status=MatchStatus.SCHEDULED.value,
                    is_bye=False,
                    is_finished=False
                )
                db.add(match)
                await db.flush()  # Get match ID
                
                # Add participants
                mp1 = MatchParticipant(
                    match_id=match.id,
                    participant_id=participants[i].id,
                    slot_number=1,
                    team_side="home"
                )
                mp2 = MatchParticipant(
                    match_id=match.id,
                    participant_id=participants[i + 1].id,
                    slot_number=2,
                    team_side="away"
                )
                db.add(mp1)
                db.add(mp2)
                
                first_round_matches.append(match)
                match_number += 1
            else:
                # Bye match (participant auto-advances)
                match = Match(
                    tournament_id=tournament_id,
                    round_number=1,
                    match_number=match_number,
                    round_name=round_names[0],
                    phase="knockout",
                    status=MatchStatus.COMPLETED.value,
                    is_bye=True,
                    is_finished=True,
                    winner_participant_id=participants[i].id
                )
                db.add(match)
                await db.flush()
                
                # Add single participant
                mp = MatchParticipant(
                    match_id=match.id,
                    participant_id=participants[i].id,
                    slot_number=1,
                    is_winner=True
                )
                db.add(mp)
                
                first_round_matches.append(match)
                match_number += 1
        
        matches.extend(first_round_matches)
        
        # Generate subsequent rounds (empty matches with dependencies)
        previous_round_matches = first_round_matches
        
        for round_num in range(2, num_rounds + 1):
            current_round_matches = []
            match_number = 1
            
            # Create matches for this round
            for i in range(0, len(previous_round_matches), 2):
                match1_id = previous_round_matches[i].id
                match2_id = previous_round_matches[i + 1].id if i + 1 < len(previous_round_matches) else None
                
                # Create match for this round
                match = Match(
                    tournament_id=tournament_id,
                    round_number=round_num,
                    match_number=match_number,
                    round_name=round_names[round_num - 1],
                    phase="knockout",
                    status=MatchStatus.SCHEDULED.value,
                    is_finished=False,
                    dependent_on_match_ids=[match1_id] if not match2_id else [match1_id, match2_id]
                )
                db.add(match)
                await db.flush()
                
                # Link previous matches to this match
                previous_round_matches[i].feeds_into_match_id = match.id
                if match2_id:
                    previous_round_matches[i + 1].feeds_into_match_id = match.id
                
                current_round_matches.append(match)
                match_number += 1
            
            matches.extend(current_round_matches)
            previous_round_matches = current_round_matches
        
        await db.commit()
        
        return matches
    
    @staticmethod
    async def generate_round_robin_schedule(
        db: AsyncSession,
        tournament_id: UUID,
        home_and_away: bool = False,
        group_name: Optional[str] = None
    ) -> List[Match]:
        """
        Generate round-robin schedule (everyone plays everyone).
        
        Uses circle method algorithm for fair scheduling.
        
        Algorithm:
        1. Get participants
        2. Use circle method to generate pairings
        3. Create matches for each round
        4. Optionally double for home & away
        
        Args:
            db: Database session
            tournament_id: Tournament UUID
            home_and_away: Double round-robin if True
            group_name: Optional group name (for group stage)
            
        Returns:
            List of generated matches
            
        Raises:
            ValueError: If tournament not found or insufficient participants
        """
        # Get tournament
        tournament = await db.get(Tournament, tournament_id)
        if not tournament:
            raise ValueError("Tournament not found")
        
        # Get confirmed participants
        query = select(TournamentParticipant).where(
            and_(
                TournamentParticipant.tournament_id == tournament_id,
                TournamentParticipant.status == "confirmed"
            )
        )
        
        # Filter by group if specified
        if group_name:
            query = query.where(TournamentParticipant.group_assignment == group_name)
        
        result = await db.execute(query)
        participants = list(result.scalars().all())
        
        if len(participants) < 2:
            raise ValueError("Need at least 2 confirmed participants for round-robin")
        
        # Generate round-robin pairings
        pairings = BracketService._generate_round_robin_pairings(len(participants))
        
        matches = []
        match_number = 1
        
        # Create matches for each round
        for round_num, round_pairings in enumerate(pairings, start=1):
            for pairing in round_pairings:
                home_idx, away_idx = pairing
                
                match = Match(
                    tournament_id=tournament_id,
                    round_number=round_num,
                    match_number=match_number,
                    round_name=f"Round {round_num}",
                    group_name=group_name,
                    phase="group_stage" if group_name else "round_robin",
                    status=MatchStatus.SCHEDULED.value,
                    is_finished=False
                )
                db.add(match)
                await db.flush()
                
                # Add participants
                mp_home = MatchParticipant(
                    match_id=match.id,
                    participant_id=participants[home_idx].id,
                    slot_number=1,
                    team_side="home"
                )
                mp_away = MatchParticipant(
                    match_id=match.id,
                    participant_id=participants[away_idx].id,
                    slot_number=2,
                    team_side="away"
                )
                db.add(mp_home)
                db.add(mp_away)
                
                matches.append(match)
                match_number += 1
        
        # Generate return matches if home_and_away
        if home_and_away:
            num_first_leg_rounds = len(pairings)
            
            for round_num, round_pairings in enumerate(pairings, start=num_first_leg_rounds + 1):
                for pairing in round_pairings:
                    # Swap home and away
                    away_idx, home_idx = pairing
                    
                    match = Match(
                        tournament_id=tournament_id,
                        round_number=round_num,
                        match_number=match_number,
                        round_name=f"Round {round_num}",
                        group_name=group_name,
                        phase="group_stage" if group_name else "round_robin",
                        status=MatchStatus.SCHEDULED.value,
                        is_finished=False
                    )
                    db.add(match)
                    await db.flush()
                    
                    mp_home = MatchParticipant(
                        match_id=match.id,
                        participant_id=participants[home_idx].id,
                        slot_number=1,
                        team_side="home"
                    )
                    mp_away = MatchParticipant(
                        match_id=match.id,
                        participant_id=participants[away_idx].id,
                        slot_number=2,
                        team_side="away"
                    )
                    db.add(mp_home)
                    db.add(mp_away)
                    
                    matches.append(match)
                    match_number += 1
        
        await db.commit()
        
        return matches
    
    @staticmethod
    def _get_round_names(num_rounds: int) -> List[str]:
        """
        Generate round names for knockout bracket.
        
        Args:
            num_rounds: Number of rounds
            
        Returns:
            List of round names
        """
        if num_rounds == 1:
            return ["Final"]
        elif num_rounds == 2:
            return ["Semifinal", "Final"]
        elif num_rounds == 3:
            return ["Quarterfinal", "Semifinal", "Final"]
        elif num_rounds == 4:
            return ["Round of 16", "Quarterfinal", "Semifinal", "Final"]
        elif num_rounds == 5:
            return ["Round of 32", "Round of 16", "Quarterfinal", "Semifinal", "Final"]
        else:
            # For larger tournaments
            names = [f"Round {i}" for i in range(1, num_rounds - 2)]
            names.extend(["Quarterfinal", "Semifinal", "Final"])
            return names
    
    @staticmethod
    def _generate_round_robin_pairings(n: int) -> List[List[Tuple[int, int]]]:
        """
        Generate round-robin pairings using circle method.
        
        Classic algorithm for fair round-robin scheduling.
        
        Args:
            n: Number of participants
            
        Returns:
            List of rounds, each containing list of (home, away) tuples
        """
        # Add dummy if odd number
        if n % 2 == 1:
            n += 1
        
        rounds = []
        participants = list(range(n))
        
        for round_num in range(n - 1):
            round_pairings = []
            
            for i in range(n // 2):
                # Skip dummy participant
                if participants[i] < n - 1 and participants[-(i + 1)] < n - 1:
                    round_pairings.append((participants[i], participants[-(i + 1)]))
            
            rounds.append(round_pairings)
            
            # Rotate participants (keep first fixed)
            participants = [participants[0]] + [participants[-1]] + participants[1:-1]
        
        return rounds
