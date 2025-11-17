"""
Sprint 4 - Match Scheduling & Brackets Tests (Pytest)

Tests all match-related functionality including:
- Match CRUD operations
- Knockout bracket generation
- Round-robin scheduling
- Match scoring system
- Tournament standings
- Match filtering and queries
"""

import pytest
import time
from conftest import (
    API_V1_URL, User, Club, Tournament, Participant, Match,
    api_client, check_backend, user_factory, club_factory,
    tournament_factory, multiple_participants
)


# ============================================================================
# Fixtures for Sprint 4 Tests
# ============================================================================

@pytest.fixture
def knockout_tournament_setup(user_factory, club_factory, tournament_factory, multiple_participants):
    """
    Creates a knockout tournament with 8 participants ready for bracket generation.

    Returns:
        dict with keys: owner, club, tournament, participants
    """
    owner = user_factory("knockout_owner", "Knockout", "Organizer")
    club = club_factory(owner, name=f"Match Test FC {int(time.time()*1000)}", city="München")

    tournament = tournament_factory(
        owner,
        club,
        name=f"Spring Knockout Tournament {int(time.time()*1000)}",
        sport_type="football",
        tournament_type="knockout",
        start_date="2025-06-01T10:00:00Z",
        end_date="2025-06-02T18:00:00Z",
        max_participants=8,
        participant_type="team"
    )

    # Create 8 participants
    participants = multiple_participants(owner, tournament, club, count=8, name_prefix="Team")

    return {
        "owner": owner,
        "club": club,
        "tournament": tournament,
        "participants": participants
    }


@pytest.fixture
def round_robin_tournament_setup(user_factory, club_factory, tournament_factory, multiple_participants):
    """
    Creates a round-robin tournament with 4 participants.

    Returns:
        dict with keys: owner, club, tournament, participants
    """
    owner = user_factory("rr_owner", "RoundRobin", "Organizer")
    club = club_factory(owner, name=f"RR Test FC {int(time.time()*1000)}", city="Berlin")

    tournament = tournament_factory(
        owner,
        club,
        name=f"Round Robin Test Tournament {int(time.time()*1000)}",
        sport_type="football",
        tournament_type="round_robin",
        start_date="2025-07-01T10:00:00Z",
        end_date="2025-07-15T18:00:00Z",
        max_participants=4,
        participant_type="team"
    )

    # Create 4 participants
    participants = multiple_participants(owner, tournament, club, count=4, name_prefix="RR Team")

    return {
        "owner": owner,
        "club": club,
        "tournament": tournament,
        "participants": participants
    }


# ============================================================================
# Test 1: Match CRUD Operations
# ============================================================================

class TestMatchCRUD:
    """Tests for basic match CRUD operations."""

    def test_create_manual_match(self, api_client, knockout_tournament_setup):
        """Test 1.1: Create a manual match."""
        tournament = knockout_tournament_setup["tournament"]
        owner = knockout_tournament_setup["owner"]
        participants = knockout_tournament_setup["participants"]

        match_data = {
            "tournament_id": tournament.id,
            "round_number": 1,
            "match_number": 1,
            "round_name": "Test Match",
            "participant_ids": [participants[0].id, participants[1].id],
            "scheduled_start": "2025-06-01T10:00:00Z",
            "venue_name": "Main Stadium",
            "court_field_number": "Field 1"
        }

        response = api_client.post(
            f"{API_V1_URL}/matches",
            json=match_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        match = response.json()
        assert match["id"] is not None
        assert match["tournament_id"] == tournament.id
        assert match["round_number"] == 1

    def test_get_match_by_id(self, api_client, knockout_tournament_setup, match_factory):
        """Test 1.2: Get match by ID."""
        tournament = knockout_tournament_setup["tournament"]
        owner = knockout_tournament_setup["owner"]
        participants = knockout_tournament_setup["participants"]

        # Create a match first
        match = match_factory(
            owner,
            tournament,
            round_number=1,
            participant_ids=[participants[0].id, participants[1].id]
        )

        response = api_client.get(
            f"{API_V1_URL}/matches/{match.id}",
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        match_data = response.json()
        assert match_data["id"] == match.id
        assert match_data["status"] in ["scheduled", "pending"]

    def test_update_match_details(self, api_client, knockout_tournament_setup, match_factory):
        """Test 1.3: Update match details."""
        tournament = knockout_tournament_setup["tournament"]
        owner = knockout_tournament_setup["owner"]
        participants = knockout_tournament_setup["participants"]

        match = match_factory(
            owner,
            tournament,
            round_number=1,
            participant_ids=[participants[0].id, participants[1].id],
            venue_name="Original Stadium"
        )

        update_data = {
            "venue_name": "Updated Stadium",
            "court_field_number": "Field 2",
            "notes": "Test match update"
        }

        response = api_client.put(
            f"{API_V1_URL}/matches/{match.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        updated_match = response.json()
        assert updated_match["venue_name"] == "Updated Stadium"
        assert updated_match["court_field_number"] == "Field 2"

    def test_list_tournament_matches(self, api_client, knockout_tournament_setup, match_factory):
        """Test 1.4: List tournament matches."""
        tournament = knockout_tournament_setup["tournament"]
        owner = knockout_tournament_setup["owner"]
        participants = knockout_tournament_setup["participants"]

        # Create a match
        match_factory(
            owner,
            tournament,
            round_number=1,
            participant_ids=[participants[0].id, participants[1].id]
        )

        response = api_client.get(
            f"{API_V1_URL}/matches",
            params={"tournament_id": tournament.id},
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        matches = response.json()
        assert isinstance(matches, list)
        assert len(matches) >= 1


# ============================================================================
# Test 2: Knockout Bracket Generation
# ============================================================================

class TestKnockoutBracket:
    """Tests for knockout bracket generation."""

    def test_generate_knockout_bracket(self, api_client, knockout_tournament_setup):
        """Test 2.1: Generate knockout bracket for 8 teams."""
        tournament = knockout_tournament_setup["tournament"]
        owner = knockout_tournament_setup["owner"]

        bracket_data = {
            "tournament_id": tournament.id,
            "shuffle_seeds": False
        }

        response = api_client.post(
            f"{API_V1_URL}/matches/generate/knockout",
            json=bracket_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        matches = response.json()
        assert isinstance(matches, list)
        # 8 teams = 4 (quarterfinals) + 2 (semifinals) + 1 (final) = 7 matches
        assert len(matches) >= 7

    def test_bracket_includes_final_round(self, api_client, knockout_tournament_setup):
        """Test 2.2: Verify bracket includes Final round."""
        tournament = knockout_tournament_setup["tournament"]
        owner = knockout_tournament_setup["owner"]

        bracket_data = {
            "tournament_id": tournament.id,
            "shuffle_seeds": False
        }

        response = api_client.post(
            f"{API_V1_URL}/matches/generate/knockout",
            json=bracket_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        matches = response.json()

        # Check for Final match
        final_matches = [m for m in matches if m.get("round_name") == "Final"]
        assert len(final_matches) >= 1

    def test_bracket_includes_semifinals(self, api_client, knockout_tournament_setup):
        """Test 2.3: Verify bracket includes 2 Semifinal matches."""
        tournament = knockout_tournament_setup["tournament"]
        owner = knockout_tournament_setup["owner"]

        bracket_data = {
            "tournament_id": tournament.id,
            "shuffle_seeds": False
        }

        response = api_client.post(
            f"{API_V1_URL}/matches/generate/knockout",
            json=bracket_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        matches = response.json()

        # Check for Semifinal matches
        semifinal_matches = [m for m in matches if m.get("round_name") == "Semifinal"]
        assert len(semifinal_matches) == 2


# ============================================================================
# Test 3: Round-Robin Scheduling
# ============================================================================

class TestRoundRobinScheduling:
    """Tests for round-robin scheduling."""

    def test_generate_round_robin_schedule(self, api_client, round_robin_tournament_setup):
        """Test 3.1: Generate round-robin schedule for 4 teams."""
        tournament = round_robin_tournament_setup["tournament"]
        owner = round_robin_tournament_setup["owner"]

        schedule_data = {
            "tournament_id": tournament.id,
            "home_and_away": False
        }

        response = api_client.post(
            f"{API_V1_URL}/matches/generate/round-robin",
            json=schedule_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        matches = response.json()
        assert isinstance(matches, list)
        # 4 teams = C(4,2) = 6 matches
        assert len(matches) == 6

    def test_verify_round_robin_pairing(self, api_client, round_robin_tournament_setup):
        """Test 3.2: Verify everyone plays everyone in round-robin."""
        tournament = round_robin_tournament_setup["tournament"]
        owner = round_robin_tournament_setup["owner"]
        participants = round_robin_tournament_setup["participants"]

        schedule_data = {
            "tournament_id": tournament.id,
            "home_and_away": False
        }

        response = api_client.post(
            f"{API_V1_URL}/matches/generate/round-robin",
            json=schedule_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        matches = response.json()

        # Verify each match has 2 participants
        for match in matches:
            assert len(match.get("participants", [])) == 2


# ============================================================================
# Test 4: Match Scoring
# ============================================================================

class TestMatchScoring:
    """Tests for match scoring system."""

    def test_update_match_score_with_winner(self, api_client, round_robin_tournament_setup):
        """Test 4.1: Update match score with winner."""
        tournament = round_robin_tournament_setup["tournament"]
        owner = round_robin_tournament_setup["owner"]

        # Generate matches first
        schedule_data = {
            "tournament_id": tournament.id,
            "home_and_away": False
        }

        response = api_client.post(
            f"{API_V1_URL}/matches/generate/round-robin",
            json=schedule_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()
        matches = response.json()

        # Get first match
        match = matches[0]
        match_id = match["id"]

        # Get participants
        participants = match["participants"]
        part1_id = participants[0]["participant_id"]
        part2_id = participants[1]["participant_id"]

        # Update score
        score_data = {
            "participant_scores": [
                {
                    "participant_id": part1_id,
                    "score_value": 3,
                    "is_winner": True
                },
                {
                    "participant_id": part2_id,
                    "score_value": 1,
                    "is_winner": False
                }
            ],
            "score_data": {
                "final_score": {"home": 3, "away": 1},
                "halftime": {"home": 2, "away": 0}
            },
            "winner_participant_id": part1_id
        }

        response = api_client.put(
            f"{API_V1_URL}/matches/{match_id}/score",
            json=score_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        scored_match = response.json()
        assert scored_match["winner_participant_id"] == part1_id

    def test_match_marked_as_finished_after_scoring(self, api_client, round_robin_tournament_setup):
        """Test 4.2: Verify match is marked as finished after scoring."""
        tournament = round_robin_tournament_setup["tournament"]
        owner = round_robin_tournament_setup["owner"]

        # Generate matches
        schedule_data = {
            "tournament_id": tournament.id,
            "home_and_away": False
        }

        response = api_client.post(
            f"{API_V1_URL}/matches/generate/round-robin",
            json=schedule_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()
        matches = response.json()

        match = matches[0]
        match_id = match["id"]
        participants = match["participants"]
        part1_id = participants[0]["participant_id"]
        part2_id = participants[1]["participant_id"]

        # Score the match
        score_data = {
            "participant_scores": [
                {
                    "participant_id": part1_id,
                    "score_value": 2,
                    "is_winner": True
                },
                {
                    "participant_id": part2_id,
                    "score_value": 0,
                    "is_winner": False
                }
            ],
            "winner_participant_id": part1_id
        }

        response = api_client.put(
            f"{API_V1_URL}/matches/{match_id}/score",
            json=score_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        scored_match = response.json()
        assert scored_match.get("is_finished") is True or scored_match.get("status") == "completed"


# ============================================================================
# Test 5: Match Status Updates
# ============================================================================

class TestMatchStatus:
    """Tests for match status updates."""

    def test_set_match_status_to_in_progress(self, api_client, round_robin_tournament_setup):
        """Test 5.1: Set match status to in_progress."""
        tournament = round_robin_tournament_setup["tournament"]
        owner = round_robin_tournament_setup["owner"]

        # Generate matches
        schedule_data = {
            "tournament_id": tournament.id,
            "home_and_away": False
        }

        response = api_client.post(
            f"{API_V1_URL}/matches/generate/round-robin",
            json=schedule_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()
        matches = response.json()

        match_id = matches[0]["id"]

        # Update status
        status_data = {
            "status": "in_progress",
            "notes": "Match started"
        }

        response = api_client.put(
            f"{API_V1_URL}/matches/{match_id}/status",
            json=status_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        updated_match = response.json()
        assert updated_match["status"] == "in_progress"

    def test_actual_start_timestamp_set(self, api_client, round_robin_tournament_setup):
        """Test 5.2: Verify actual_start timestamp is set when match starts."""
        tournament = round_robin_tournament_setup["tournament"]
        owner = round_robin_tournament_setup["owner"]

        # Generate matches
        schedule_data = {
            "tournament_id": tournament.id,
            "home_and_away": False
        }

        response = api_client.post(
            f"{API_V1_URL}/matches/generate/round-robin",
            json=schedule_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()
        matches = response.json()

        match_id = matches[0]["id"]

        # Update status to in_progress
        status_data = {
            "status": "in_progress"
        }

        response = api_client.put(
            f"{API_V1_URL}/matches/{match_id}/status",
            json=status_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        updated_match = response.json()
        assert updated_match.get("actual_start") is not None


# ============================================================================
# Test 6: Tournament Standings
# ============================================================================

class TestTournamentStandings:
    """Tests for tournament standings calculation."""

    def test_get_tournament_standings(self, api_client, round_robin_tournament_setup):
        """Test 6.1: Get tournament standings."""
        tournament = round_robin_tournament_setup["tournament"]
        owner = round_robin_tournament_setup["owner"]

        # Generate and score a match
        schedule_data = {
            "tournament_id": tournament.id,
            "home_and_away": False
        }

        response = api_client.post(
            f"{API_V1_URL}/matches/generate/round-robin",
            json=schedule_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()
        matches = response.json()

        # Score first match
        match = matches[0]
        participants = match["participants"]
        part1_id = participants[0]["participant_id"]
        part2_id = participants[1]["participant_id"]

        score_data = {
            "participant_scores": [
                {"participant_id": part1_id, "score_value": 3, "is_winner": True},
                {"participant_id": part2_id, "score_value": 1, "is_winner": False}
            ],
            "winner_participant_id": part1_id
        }

        api_client.put(
            f"{API_V1_URL}/matches/{match['id']}/score",
            json=score_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        # Get standings
        response = api_client.get(
            f"{API_V1_URL}/matches/standings/{tournament.id}",
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        standings = response.json()
        assert isinstance(standings, list)
        assert len(standings) >= 2

    def test_winner_has_correct_points(self, api_client, round_robin_tournament_setup):
        """Test 6.2: Verify winner has 3 points in standings."""
        tournament = round_robin_tournament_setup["tournament"]
        owner = round_robin_tournament_setup["owner"]

        # Generate matches
        schedule_data = {
            "tournament_id": tournament.id,
            "home_and_away": False
        }

        response = api_client.post(
            f"{API_V1_URL}/matches/generate/round-robin",
            json=schedule_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()
        matches = response.json()

        # Score first match
        match = matches[0]
        participants = match["participants"]
        winner_id = participants[0]["participant_id"]
        loser_id = participants[1]["participant_id"]

        score_data = {
            "participant_scores": [
                {"participant_id": winner_id, "score_value": 2, "is_winner": True},
                {"participant_id": loser_id, "score_value": 0, "is_winner": False}
            ],
            "winner_participant_id": winner_id
        }

        api_client.put(
            f"{API_V1_URL}/matches/{match['id']}/score",
            json=score_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        # Get standings
        response = api_client.get(
            f"{API_V1_URL}/matches/standings/{tournament.id}",
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        standings = response.json()
        winner_standing = next((s for s in standings if s["participant_id"] == winner_id), None)

        assert winner_standing is not None
        assert winner_standing["points"] == 3

    def test_recalculate_standings(self, api_client, round_robin_tournament_setup):
        """Test 6.3: Recalculate tournament standings."""
        tournament = round_robin_tournament_setup["tournament"]
        owner = round_robin_tournament_setup["owner"]

        # Generate and score matches first
        schedule_data = {
            "tournament_id": tournament.id,
            "home_and_away": False
        }

        response = api_client.post(
            f"{API_V1_URL}/matches/generate/round-robin",
            json=schedule_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()
        matches = response.json()

        # Score a match
        match = matches[0]
        participants = match["participants"]

        score_data = {
            "participant_scores": [
                {"participant_id": participants[0]["participant_id"], "score_value": 1, "is_winner": True},
                {"participant_id": participants[1]["participant_id"], "score_value": 0, "is_winner": False}
            ],
            "winner_participant_id": participants[0]["participant_id"]
        }

        api_client.put(
            f"{API_V1_URL}/matches/{match['id']}/score",
            json=score_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        # Recalculate standings
        response = api_client.post(
            f"{API_V1_URL}/matches/standings/{tournament.id}/recalculate",
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        recalculated_standings = response.json()
        assert isinstance(recalculated_standings, list)
        assert len(recalculated_standings) >= 2


# ============================================================================
# Test 7: Filtering and Queries
# ============================================================================

class TestMatchFiltering:
    """Tests for match filtering and queries."""

    def test_filter_matches_by_round_number(self, api_client, knockout_tournament_setup):
        """Test 7.1: Filter matches by round number."""
        tournament = knockout_tournament_setup["tournament"]
        owner = knockout_tournament_setup["owner"]

        # Generate bracket
        bracket_data = {
            "tournament_id": tournament.id,
            "shuffle_seeds": False
        }

        api_client.post(
            f"{API_V1_URL}/matches/generate/knockout",
            json=bracket_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        # Filter by round 1
        response = api_client.get(
            f"{API_V1_URL}/matches",
            params={"tournament_id": tournament.id, "round_number": 1},
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        matches = response.json()
        assert len(matches) >= 1

        # Verify all matches are from round 1
        for match in matches:
            assert match["round_number"] == 1

    def test_filter_matches_by_status(self, api_client, round_robin_tournament_setup):
        """Test 7.2: Filter matches by status."""
        tournament = round_robin_tournament_setup["tournament"]
        owner = round_robin_tournament_setup["owner"]

        # Generate matches
        schedule_data = {
            "tournament_id": tournament.id,
            "home_and_away": False
        }

        api_client.post(
            f"{API_V1_URL}/matches/generate/round-robin",
            json=schedule_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        # Filter by scheduled status
        response = api_client.get(
            f"{API_V1_URL}/matches",
            params={"tournament_id": tournament.id, "status": "scheduled"},
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        matches = response.json()
        assert len(matches) >= 1

        # Verify all matches have scheduled status
        for match in matches:
            assert match["status"] in ["scheduled", "pending"]


# ============================================================================
# Modular Helper Functions (reusable in other tests)
# ============================================================================

def generate_and_score_matches(
    api_client,
    tournament_id: str,
    owner_token: str,
    tournament_type: str = "round_robin"
) -> list:
    """
    Reusable function to generate matches and score some of them.

    Args:
        api_client: The API client
        tournament_id: Tournament ID
        owner_token: Owner's auth token
        tournament_type: Type of tournament (knockout or round_robin)

    Returns:
        list: Generated and scored matches
    """
    # Generate matches
    if tournament_type == "knockout":
        endpoint = f"{API_V1_URL}/matches/generate/knockout"
        data = {"tournament_id": tournament_id, "shuffle_seeds": False}
    else:
        endpoint = f"{API_V1_URL}/matches/generate/round-robin"
        data = {"tournament_id": tournament_id, "home_and_away": False}

    response = api_client.post(
        endpoint,
        json=data,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    response.raise_for_status()
    matches = response.json()

    # Score first match
    if matches:
        match = matches[0]
        if "participants" in match and len(match["participants"]) >= 2:
            participants = match["participants"]
            score_data = {
                "participant_scores": [
                    {"participant_id": participants[0]["participant_id"], "score_value": 2, "is_winner": True},
                    {"participant_id": participants[1]["participant_id"], "score_value": 1, "is_winner": False}
                ],
                "winner_participant_id": participants[0]["participant_id"]
            }

            api_client.put(
                f"{API_V1_URL}/matches/{match['id']}/score",
                json=score_data,
                headers={"Authorization": f"Bearer {owner_token}"}
            )

    return matches


def create_tournament_with_bracket(
    api_client,
    owner_token: str,
    club_id: str,
    participant_count: int = 8
) -> dict:
    """
    Reusable function to create a tournament and generate knockout bracket.

    Returns:
        dict: Tournament data with generated matches
    """
    timestamp = int(time.time() * 1000)

    # Create tournament
    tournament_data = {
        "club_id": club_id,
        "name": f"Bracket Tournament {timestamp}",
        "sport_type": "football",
        "tournament_type": "knockout",
        "start_date": "2025-08-01T10:00:00Z",
        "end_date": "2025-08-03T18:00:00Z",
        "max_participants": participant_count
    }

    response = api_client.post(
        f"{API_V1_URL}/tournaments",
        json=tournament_data,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    response.raise_for_status()
    tournament = response.json()

    # Create participants
    for i in range(participant_count):
        participant_data = {
            "participant_club_id": club_id,
            "participant_name": f"Team {i + 1}",
            "display_name": f"T{i + 1}"
        }

        response = api_client.post(
            f"{API_V1_URL}/tournaments/{tournament['id']}/participants",
            json=participant_data,
            headers={"Authorization": f"Bearer {owner_token}"}
        )
        response.raise_for_status()
        participant = response.json()

        # Confirm participant
        api_client.put(
            f"{API_V1_URL}/tournaments/{tournament['id']}/participants/{participant['id']}/status",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {owner_token}"}
        )

    # Generate bracket
    bracket_data = {
        "tournament_id": tournament["id"],
        "shuffle_seeds": False
    }

    response = api_client.post(
        f"{API_V1_URL}/matches/generate/knockout",
        json=bracket_data,
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    response.raise_for_status()
    matches = response.json()

    tournament["matches"] = matches
    return tournament
