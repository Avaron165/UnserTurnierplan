"""
Sprint 4 Tests - Match Scheduling & Brackets
Tests all match-related functionality using pytest and requests
"""
import pytest
import requests
from typing import Dict, List
import time


BASE_URL = "http://localhost:8000/api/v1"


@pytest.fixture(scope="session")
def test_user() -> Dict:
    """Create a test user and return credentials"""
    timestamp = int(time.time())
    email = f"pytest_user_{timestamp}@test.com"
    password = "Test1234Pass"

    # Register
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Pytest",
            "last_name": "User"
        }
    )
    assert response.status_code == 201, f"Registration failed: {response.text}"
    user = response.json()

    # Login
    response = requests.post(
        f"{BASE_URL}/auth/login/json",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token_data = response.json()

    return {
        "id": user["id"],
        "email": email,
        "password": password,
        "token": token_data["access_token"]
    }


@pytest.fixture(scope="session")
def test_club(test_user: Dict) -> Dict:
    """Create a test club"""
    timestamp = int(time.time())
    response = requests.post(
        f"{BASE_URL}/clubs",
        headers={"Authorization": f"Bearer {test_user['token']}"},
        json={
            "name": f"Pytest Club {timestamp}",
            "city": "Munich"
        }
    )
    assert response.status_code == 201, f"Club creation failed: {response.text}"
    return response.json()


@pytest.fixture(scope="session")
def knockout_tournament(test_user: Dict, test_club: Dict) -> Dict:
    """Create a knockout tournament with 8 participants"""
    timestamp = int(time.time())

    # Create tournament
    response = requests.post(
        f"{BASE_URL}/tournaments",
        headers={"Authorization": f"Bearer {test_user['token']}"},
        json={
            "club_id": test_club["id"],
            "name": f"Knockout Tournament {timestamp}",
            "sport_type": "football",
            "tournament_type": "knockout",
            "start_date": "2025-06-01T10:00:00Z",
            "end_date": "2025-06-02T18:00:00Z",
            "max_participants": 8,
            "participant_type": "team"
        }
    )
    assert response.status_code == 201, f"Tournament creation failed: {response.text}"
    tournament = response.json()

    # Register 8 participants
    participant_ids = []
    for i in range(1, 9):
        response = requests.post(
            f"{BASE_URL}/tournaments/{tournament['id']}/participants",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "participant_club_id": test_club["id"],
                "participant_name": f"Team {i}",
                "display_name": f"T{i}"
            }
        )
        assert response.status_code == 201, f"Participant registration failed: {response.text}"
        participant = response.json()
        participant_ids.append(participant["id"])

        # Confirm participant
        response = requests.put(
            f"{BASE_URL}/tournaments/{tournament['id']}/participants/{participant['id']}/status",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={"status": "confirmed"}
        )
        assert response.status_code == 200

    tournament["participant_ids"] = participant_ids
    return tournament


@pytest.fixture(scope="session")
def round_robin_tournament(test_user: Dict, test_club: Dict) -> Dict:
    """Create a round-robin tournament with 4 participants"""
    timestamp = int(time.time())

    # Create tournament
    response = requests.post(
        f"{BASE_URL}/tournaments",
        headers={"Authorization": f"Bearer {test_user['token']}"},
        json={
            "club_id": test_club["id"],
            "name": f"Round Robin Tournament {timestamp}",
            "sport_type": "football",
            "tournament_type": "round_robin",
            "start_date": "2025-07-01T10:00:00Z",
            "end_date": "2025-07-15T18:00:00Z",
            "max_participants": 4,
            "participant_type": "team"
        }
    )
    assert response.status_code == 201, f"Tournament creation failed: {response.text}"
    tournament = response.json()

    # Register 4 participants
    participant_ids = []
    for i in range(1, 5):
        response = requests.post(
            f"{BASE_URL}/tournaments/{tournament['id']}/participants",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "participant_club_id": test_club["id"],
                "participant_name": f"RR Team {i}",
                "display_name": f"RR{i}"
            }
        )
        assert response.status_code == 201
        participant = response.json()
        participant_ids.append(participant["id"])

        # Confirm participant
        response = requests.put(
            f"{BASE_URL}/tournaments/{tournament['id']}/participants/{participant['id']}/status",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={"status": "confirmed"}
        )
        assert response.status_code == 200

    tournament["participant_ids"] = participant_ids
    return tournament


# ==================== MATCH CRUD TESTS ====================

class TestMatchCRUD:
    """Test basic Match CRUD operations"""

    def test_create_manual_match(self, test_user: Dict, knockout_tournament: Dict):
        """Test creating a manual match"""
        response = requests.post(
            f"{BASE_URL}/matches",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "tournament_id": knockout_tournament["id"],
                "round_number": 1,
                "match_number": 1,
                "round_name": "Test Match",
                "participant_ids": [
                    knockout_tournament["participant_ids"][0],
                    knockout_tournament["participant_ids"][1]
                ],
                "scheduled_start": "2025-06-01T10:00:00Z",
                "venue_name": "Main Stadium",
                "court_field_number": "Field 1"
            }
        )
        assert response.status_code == 201, f"Match creation failed: {response.text}"
        match = response.json()
        assert match["status"] == "scheduled"
        assert match["round_number"] == 1
        assert len(match["participants"]) == 2

    def test_get_match_by_id(self, test_user: Dict, knockout_tournament: Dict):
        """Test retrieving a match by ID"""
        # Create a match first
        create_response = requests.post(
            f"{BASE_URL}/matches",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "tournament_id": knockout_tournament["id"],
                "round_number": 1,
                "match_number": 2,
                "participant_ids": [
                    knockout_tournament["participant_ids"][2],
                    knockout_tournament["participant_ids"][3]
                ],
                "scheduled_start": "2025-06-01T11:00:00Z"
            }
        )
        assert create_response.status_code == 201
        match_id = create_response.json()["id"]

        # Get match
        response = requests.get(
            f"{BASE_URL}/matches/{match_id}",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        match = response.json()
        assert match["id"] == match_id
        assert match["status"] == "scheduled"

    def test_update_match(self, test_user: Dict, knockout_tournament: Dict):
        """Test updating match details"""
        # Create a match
        create_response = requests.post(
            f"{BASE_URL}/matches",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "tournament_id": knockout_tournament["id"],
                "round_number": 1,
                "match_number": 3,
                "participant_ids": [
                    knockout_tournament["participant_ids"][4],
                    knockout_tournament["participant_ids"][5]
                ],
                "scheduled_start": "2025-06-01T12:00:00Z",
                "venue_name": "Stadium A"
            }
        )
        assert create_response.status_code == 201
        match_id = create_response.json()["id"]

        # Update match
        response = requests.put(
            f"{BASE_URL}/matches/{match_id}",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "venue_name": "Stadium B",
                "court_field_number": "Field 2",
                "notes": "Updated venue"
            }
        )
        assert response.status_code == 200
        updated_match = response.json()
        assert updated_match["venue_name"] == "Stadium B"
        assert updated_match["court_field_number"] == "Field 2"

    def test_list_tournament_matches(self, test_user: Dict, knockout_tournament: Dict):
        """Test listing all matches for a tournament"""
        response = requests.get(
            f"{BASE_URL}/matches",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            params={"tournament_id": knockout_tournament["id"]}
        )
        assert response.status_code == 200
        matches = response.json()
        assert isinstance(matches, list)
        assert len(matches) >= 3  # We created at least 3 matches


# ==================== KNOCKOUT BRACKET TESTS ====================

class TestKnockoutBracket:
    """Test knockout bracket generation"""

    def test_generate_knockout_bracket(self, test_user: Dict, knockout_tournament: Dict):
        """Test generating a complete knockout bracket"""
        response = requests.post(
            f"{BASE_URL}/matches/generate/knockout",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "tournament_id": knockout_tournament["id"],
                "shuffle_seeds": False
            }
        )
        assert response.status_code == 201, f"Bracket generation failed: {response.text}"
        matches = response.json()

        # 8 teams = 4 + 2 + 1 = 7 matches
        assert len(matches) == 7, f"Expected 7 matches, got {len(matches)}"

    def test_knockout_bracket_structure(self, test_user: Dict, knockout_tournament: Dict):
        """Test that knockout bracket has correct round structure"""
        response = requests.get(
            f"{BASE_URL}/matches",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            params={"tournament_id": knockout_tournament["id"]}
        )
        assert response.status_code == 200
        matches = response.json()

        # Check for required rounds
        round_names = set(m["round_name"] for m in matches if m["round_name"])
        assert "Final" in round_names
        assert "Semifinal" in round_names
        assert "Quarterfinal" in round_names

        # Count matches per round
        semifinals = [m for m in matches if m["round_name"] == "Semifinal"]
        assert len(semifinals) == 2, f"Expected 2 semifinals, got {len(semifinals)}"

        finals = [m for m in matches if m["round_name"] == "Final"]
        assert len(finals) == 1, f"Expected 1 final, got {len(finals)}"


# ==================== ROUND-ROBIN TESTS ====================

class TestRoundRobin:
    """Test round-robin schedule generation"""

    def test_generate_round_robin_schedule(self, test_user: Dict, round_robin_tournament: Dict):
        """Test generating a round-robin schedule"""
        response = requests.post(
            f"{BASE_URL}/matches/generate/round-robin",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "tournament_id": round_robin_tournament["id"],
                "home_and_away": False
            }
        )
        assert response.status_code == 201, f"Round-robin generation failed: {response.text}"
        matches = response.json()

        # 4 teams, everyone plays everyone once = C(4,2) = 6 matches
        assert len(matches) == 6, f"Expected 6 matches, got {len(matches)}"

    def test_round_robin_everyone_plays_everyone(self, test_user: Dict, round_robin_tournament: Dict):
        """Verify that every team plays every other team exactly once"""
        response = requests.get(
            f"{BASE_URL}/matches",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            params={"tournament_id": round_robin_tournament["id"]}
        )
        assert response.status_code == 200
        matches = response.json()

        # Create set of all matchups
        matchups = set()
        for match in matches:
            parts = match["participants"]
            if len(parts) == 2:
                p1, p2 = parts[0]["participant_id"], parts[1]["participant_id"]
                # Store as sorted tuple to ensure uniqueness
                matchups.add(tuple(sorted([p1, p2])))

        # 4 teams = 6 unique pairings
        assert len(matchups) == 6


# ==================== MATCH SCORING TESTS ====================

class TestMatchScoring:
    """Test match scoring functionality"""

    def test_update_match_score(self, test_user: Dict, round_robin_tournament: Dict):
        """Test updating match score and setting winner"""
        # Get first match
        response = requests.get(
            f"{BASE_URL}/matches",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            params={"tournament_id": round_robin_tournament["id"]}
        )
        assert response.status_code == 200
        matches = response.json()
        assert len(matches) > 0

        match = matches[0]
        match_id = match["id"]
        participants = match["participants"]
        assert len(participants) == 2

        # Update score
        response = requests.put(
            f"{BASE_URL}/matches/{match_id}/score",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "participant_scores": [
                    {
                        "participant_id": participants[0]["participant_id"],
                        "score_value": 3,
                        "is_winner": True
                    },
                    {
                        "participant_id": participants[1]["participant_id"],
                        "score_value": 1,
                        "is_winner": False
                    }
                ],
                "score_data": {
                    "final_score": {"home": 3, "away": 1},
                    "halftime": {"home": 2, "away": 0}
                },
                "winner_participant_id": participants[0]["participant_id"]
            }
        )
        assert response.status_code == 200, f"Score update failed: {response.text}"
        updated_match = response.json()
        assert updated_match["winner_participant_id"] == participants[0]["participant_id"]
        assert updated_match["is_finished"] == True

    def test_match_status_progression(self, test_user: Dict, round_robin_tournament: Dict):
        """Test match status transitions"""
        # Get a scheduled match
        response = requests.get(
            f"{BASE_URL}/matches",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            params={
                "tournament_id": round_robin_tournament["id"],
                "status": "scheduled"
            }
        )
        assert response.status_code == 200
        matches = response.json()

        if len(matches) > 1:  # Need at least 2 matches (one was scored in previous test)
            match_id = matches[1]["id"]

            # Set to in_progress
            response = requests.put(
                f"{BASE_URL}/matches/{match_id}/status",
                headers={"Authorization": f"Bearer {test_user['token']}"},
                json={
                    "status": "in_progress",
                    "notes": "Match started"
                }
            )
            assert response.status_code == 200
            updated_match = response.json()
            assert updated_match["status"] == "in_progress"
            assert updated_match["actual_start"] is not None


# ==================== STANDINGS TESTS ====================

class TestStandings:
    """Test tournament standings calculation"""

    def test_get_standings(self, test_user: Dict, round_robin_tournament: Dict):
        """Test retrieving tournament standings"""
        response = requests.get(
            f"{BASE_URL}/matches/standings/{round_robin_tournament['id']}",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        standings = response.json()
        assert isinstance(standings, list)
        # Should have standings for all participants
        assert len(standings) >= 2

    def test_winner_has_correct_points(self, test_user: Dict, round_robin_tournament: Dict):
        """Test that match winner gets 3 points in standings"""
        # Get standings
        response = requests.get(
            f"{BASE_URL}/matches/standings/{round_robin_tournament['id']}",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        standings = response.json()

        # Find participant with points (from previous scored match)
        winners = [s for s in standings if s["points"] > 0]
        if winners:
            # Winner should have 3 points (standard football scoring)
            assert winners[0]["points"] == 3 or winners[0]["matches_won"] == 1

    def test_recalculate_standings(self, test_user: Dict, round_robin_tournament: Dict):
        """Test recalculating tournament standings"""
        response = requests.post(
            f"{BASE_URL}/matches/standings/{round_robin_tournament['id']}/recalculate",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        standings = response.json()
        assert isinstance(standings, list)
        assert len(standings) >= 2


# ==================== FILTERING TESTS ====================

class TestMatchFiltering:
    """Test match filtering and queries"""

    def test_filter_by_round(self, test_user: Dict, knockout_tournament: Dict):
        """Test filtering matches by round number"""
        response = requests.get(
            f"{BASE_URL}/matches",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            params={
                "tournament_id": knockout_tournament["id"],
                "round_number": 1
            }
        )
        assert response.status_code == 200
        matches = response.json()
        assert all(m["round_number"] == 1 for m in matches)

    def test_filter_by_status(self, test_user: Dict, round_robin_tournament: Dict):
        """Test filtering matches by status"""
        response = requests.get(
            f"{BASE_URL}/matches",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            params={
                "tournament_id": round_robin_tournament["id"],
                "status": "scheduled"
            }
        )
        assert response.status_code == 200
        matches = response.json()
        assert all(m["status"] == "scheduled" for m in matches)


# ==================== EDGE CASES ====================

class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_create_match_without_participants(self, test_user: Dict, knockout_tournament: Dict):
        """Test that creating a match without participants fails"""
        response = requests.post(
            f"{BASE_URL}/matches",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "tournament_id": knockout_tournament["id"],
                "round_number": 1,
                "match_number": 99,
                "participant_ids": []  # Empty!
            }
        )
        assert response.status_code == 422 or response.status_code == 400

    def test_get_nonexistent_match(self, test_user: Dict):
        """Test retrieving a match that doesn't exist"""
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = requests.get(
            f"{BASE_URL}/matches/{fake_uuid}",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 404

    def test_unauthorized_access(self, knockout_tournament: Dict):
        """Test that unauthorized users cannot access matches"""
        response = requests.get(
            f"{BASE_URL}/matches",
            params={"tournament_id": knockout_tournament["id"]}
            # No Authorization header
        )
        assert response.status_code == 401
