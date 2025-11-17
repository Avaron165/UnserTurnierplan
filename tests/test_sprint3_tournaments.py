"""
Sprint 3 - Tournament Management Tests (Pytest)

Tests all tournament management endpoints including:
- Tournament CRUD operations
- Tournament status lifecycle
- Participant registration and management
- Payment tracking
- Statistics and reporting
- Filtering and permissions
"""

import pytest
import time
from urllib.parse import quote
from conftest import (
    API_V1_URL, User, Club, Tournament, Participant,
    api_client, check_backend, user_factory, club_factory,
    tournament_factory, participant_factory, confirmed_participant
)


# ============================================================================
# Fixtures for Sprint 3 Tests
# ============================================================================

@pytest.fixture
def tournament_setup(user_factory, club_factory, tournament_factory):
    """
    Creates a complete tournament setup with owner, participant, and clubs.

    Returns:
        dict with keys: owner, participant, owner_club, participant_club, tournament
    """
    owner = user_factory("tournament_owner", "Tournament", "Owner")
    participant_user = user_factory("tournament_participant", "Team", "Captain")

    owner_club = club_factory(owner, name=f"FC Tournament Test {int(time.time()*1000)}", city="München")
    participant_club = club_factory(participant_user, name=f"Participant Club {int(time.time()*1000)}", city="Berlin")

    tournament = tournament_factory(
        owner,
        owner_club,
        name=f"Summer Cup {int(time.time()*1000)}",
        description="Annual summer football tournament",
        sport_type="football",
        tournament_type="knockout",
        start_date="2026-07-15T10:00:00",
        end_date="2026-07-17T18:00:00",
        registration_start="2025-11-01T00:00:00",
        registration_end="2026-07-10T23:59:59",
        location="Sportplatz München",
        participant_type="team",
        min_participants=4,
        max_participants=16,
        entry_fee=50.00
    )

    return {
        "owner": owner,
        "participant": participant_user,
        "owner_club": owner_club,
        "participant_club": participant_club,
        "tournament": tournament
    }


# ============================================================================
# Test 1-5: Tournament CRUD Operations
# ============================================================================

class TestTournamentCRUD:
    """Tests for basic Tournament CRUD operations."""

    def test_create_tournament(self, tournament_setup):
        """Test 1: Create a new tournament."""
        tournament = tournament_setup["tournament"]
        owner = tournament_setup["owner"]

        assert tournament.id is not None
        assert tournament.slug is not None
        assert tournament.creator_id == owner.id
        assert tournament.data["sport_type"] == "football"
        assert tournament.data["max_participants"] == 16

    def test_list_tournaments(self, api_client, tournament_setup):
        """Test 2: List all tournaments."""
        tournament = tournament_setup["tournament"]

        response = api_client.get(f"{API_V1_URL}/tournaments")
        response.raise_for_status()

        tournaments = response.json()
        assert isinstance(tournaments, list)

        tournament_ids = [t["id"] for t in tournaments]
        assert tournament.id in tournament_ids

    def test_get_tournament_by_id(self, api_client, tournament_setup):
        """Test 3: Get tournament by ID."""
        tournament = tournament_setup["tournament"]

        response = api_client.get(f"{API_V1_URL}/tournaments/{tournament.id}")
        response.raise_for_status()

        tournament_data = response.json()
        assert tournament_data["id"] == tournament.id
        assert tournament_data["name"] == tournament.name

    def test_get_tournament_by_slug(self, api_client, tournament_setup):
        """Test 4: Get tournament by slug."""
        tournament = tournament_setup["tournament"]

        response = api_client.get(f"{API_V1_URL}/tournaments/slug/{tournament.slug}")
        response.raise_for_status()

        tournament_data = response.json()
        assert tournament_data["id"] == tournament.id
        assert tournament_data["slug"] == tournament.slug

    def test_update_tournament(self, api_client, tournament_setup):
        """Test 5: Update tournament details."""
        tournament = tournament_setup["tournament"]
        owner = tournament_setup["owner"]

        update_data = {
            "description": "Updated: The best summer tournament ever!",
            "max_participants": 20
        }

        response = api_client.put(
            f"{API_V1_URL}/tournaments/{tournament.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        updated_tournament = response.json()
        assert updated_tournament["max_participants"] == 20
        assert "best summer tournament" in updated_tournament["description"].lower()


# ============================================================================
# Test 6-7: Tournament Search and Filtering
# ============================================================================

class TestTournamentFiltering:
    """Tests for tournament filtering functionality."""

    def test_filter_by_sport_type(self, api_client, tournament_setup):
        """Test 6: Filter tournaments by sport type."""
        tournament = tournament_setup["tournament"]

        response = api_client.get(
            f"{API_V1_URL}/tournaments",
            params={"sport_type": "football"}
        )
        response.raise_for_status()

        tournaments = response.json()
        tournament_ids = [t["id"] for t in tournaments]
        assert tournament.id in tournament_ids

        # Verify all returned tournaments are football
        for t in tournaments:
            assert t["sport_type"] == "football"

    def test_filter_by_city(self, api_client, tournament_setup):
        """Test 7: Filter tournaments by city (with UTF-8 support)."""
        tournament = tournament_setup["tournament"]

        # Use URL-encoded München for proper umlaut handling
        city_encoded = quote("München")
        response = api_client.get(
            f"{API_V1_URL}/tournaments?city={city_encoded}"
        )
        response.raise_for_status()

        tournaments = response.json()

        # Check if our tournament is in results if it has city set
        if "city" in tournament.data:
            tournament_ids = [t["id"] for t in tournaments]
            assert tournament.id in tournament_ids


# ============================================================================
# Test 8-10: Tournament Status and Statistics
# ============================================================================

class TestTournamentStatus:
    """Tests for tournament status lifecycle and statistics."""

    def test_update_status_to_published(self, api_client, tournament_setup):
        """Test 8: Update tournament status to published."""
        tournament = tournament_setup["tournament"]
        owner = tournament_setup["owner"]

        response = api_client.put(
            f"{API_V1_URL}/tournaments/{tournament.id}/status",
            json={"status": "published"},
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        updated_tournament = response.json()
        assert updated_tournament["status"] == "published"

    def test_open_registration(self, api_client, tournament_setup):
        """Test 9: Open tournament registration."""
        tournament = tournament_setup["tournament"]
        owner = tournament_setup["owner"]

        # First set to published if needed
        api_client.put(
            f"{API_V1_URL}/tournaments/{tournament.id}/status",
            json={"status": "published"},
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        # Then open registration
        response = api_client.put(
            f"{API_V1_URL}/tournaments/{tournament.id}/status",
            json={"status": "registration_open"},
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        updated_tournament = response.json()
        assert updated_tournament["status"] == "registration_open"

    def test_get_tournament_statistics(self, api_client, tournament_setup):
        """Test 10: Get tournament statistics."""
        tournament = tournament_setup["tournament"]

        response = api_client.get(
            f"{API_V1_URL}/tournaments/{tournament.id}/statistics"
        )
        response.raise_for_status()

        stats = response.json()
        assert "total_participants" in stats
        assert isinstance(stats["total_participants"], int)


# ============================================================================
# Test 11-16: Participant Management
# ============================================================================

class TestParticipantManagement:
    """Tests for tournament participant registration and management."""

    def test_register_participant(self, api_client, tournament_setup):
        """Test 11: Register team as participant."""
        tournament = tournament_setup["tournament"]
        participant_user = tournament_setup["participant"]
        participant_club = tournament_setup["participant_club"]
        owner = tournament_setup["owner"]

        # Open registration first
        api_client.put(
            f"{API_V1_URL}/tournaments/{tournament.id}/status",
            json={"status": "registration_open"},
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        # Register participant
        register_data = {
            "participant_club_id": participant_club.id,
            "participant_name": "FC Test Team",
            "contact_email": "team@test.com",
            "contact_phone": "+49123456789"
        }

        response = api_client.post(
            f"{API_V1_URL}/tournaments/{tournament.id}/register",
            json=register_data,
            headers={"Authorization": f"Bearer {participant_user.token}"}
        )
        response.raise_for_status()

        registration = response.json()
        assert registration["id"] is not None
        assert registration["participant_name"] == "FC Test Team"

    def test_list_participants(self, api_client, participant_factory, tournament_setup):
        """Test 12: List tournament participants."""
        tournament = tournament_setup["tournament"]
        participant_user = tournament_setup["participant"]
        participant_club = tournament_setup["participant_club"]

        # Create a participant
        participant = participant_factory(
            participant_user,
            tournament,
            participant_club,
            "FC Test Team"
        )

        # List participants
        response = api_client.get(
            f"{API_V1_URL}/tournaments/{tournament.id}/participants"
        )
        response.raise_for_status()

        participants = response.json()
        participant_ids = [p["id"] for p in participants]
        assert participant.id in participant_ids

    def test_get_participant_details(self, api_client, participant_factory, tournament_setup):
        """Test 13: Get participant details."""
        tournament = tournament_setup["tournament"]
        participant_user = tournament_setup["participant"]
        participant_club = tournament_setup["participant_club"]

        participant = participant_factory(
            participant_user,
            tournament,
            participant_club,
            "FC Test Team"
        )

        response = api_client.get(
            f"{API_V1_URL}/tournaments/{tournament.id}/participants/{participant.id}"
        )
        response.raise_for_status()

        participant_data = response.json()
        assert participant_data["id"] == participant.id

    def test_update_participant(self, api_client, participant_factory, tournament_setup):
        """Test 14: Update participant information."""
        tournament = tournament_setup["tournament"]
        owner = tournament_setup["owner"]
        participant_user = tournament_setup["participant"]
        participant_club = tournament_setup["participant_club"]

        participant = participant_factory(
            participant_user,
            tournament,
            participant_club,
            "FC Test Team"
        )

        update_data = {
            "display_name": "FC Test Team A",
            "notes": "Updated team information"
        }

        response = api_client.put(
            f"{API_V1_URL}/tournaments/{tournament.id}/participants/{participant.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        updated_participant = response.json()
        assert updated_participant["display_name"] == "FC Test Team A"

    def test_confirm_participant(self, api_client, participant_factory, tournament_setup):
        """Test 15: Confirm participant status."""
        tournament = tournament_setup["tournament"]
        owner = tournament_setup["owner"]
        participant_user = tournament_setup["participant"]
        participant_club = tournament_setup["participant_club"]

        participant = participant_factory(
            participant_user,
            tournament,
            participant_club,
            "FC Test Team"
        )

        response = api_client.put(
            f"{API_V1_URL}/tournaments/{tournament.id}/participants/{participant.id}/status",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        confirmed = response.json()
        assert confirmed["status"] == "confirmed"

    def test_update_payment_status(self, api_client, participant_factory, tournament_setup):
        """Test 16: Update payment status."""
        tournament = tournament_setup["tournament"]
        owner = tournament_setup["owner"]
        participant_user = tournament_setup["participant"]
        participant_club = tournament_setup["participant_club"]

        participant = participant_factory(
            participant_user,
            tournament,
            participant_club,
            "FC Test Team"
        )

        payment_data = {
            "payment_status": "paid",
            "payment_amount": 50.00,
            "payment_reference": "PAY-TEST-12345"
        }

        response = api_client.put(
            f"{API_V1_URL}/tournaments/{tournament.id}/participants/{participant.id}/payment",
            json=payment_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        updated = response.json()
        assert updated["payment_status"] == "paid"


# ============================================================================
# Test 17-19: User Tournaments and Permissions
# ============================================================================

class TestUserTournamentsAndPermissions:
    """Tests for user-specific tournament views and permissions."""

    def test_get_my_created_tournaments(self, api_client, tournament_setup):
        """Test 17: Get my created tournaments."""
        tournament = tournament_setup["tournament"]
        owner = tournament_setup["owner"]

        response = api_client.get(
            f"{API_V1_URL}/tournaments/my/created",
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        my_tournaments = response.json()
        tournament_ids = [t["id"] for t in my_tournaments]
        assert tournament.id in tournament_ids

    def test_get_my_participations(self, api_client, participant_factory, tournament_setup):
        """Test 18: Get my tournament participations."""
        tournament = tournament_setup["tournament"]
        participant_user = tournament_setup["participant"]
        participant_club = tournament_setup["participant_club"]

        # Create participation
        participant_factory(
            participant_user,
            tournament,
            participant_club,
            "FC Test Team"
        )

        response = api_client.get(
            f"{API_V1_URL}/tournaments/my/participating",
            headers={"Authorization": f"Bearer {participant_user.token}"}
        )
        response.raise_for_status()

        participations = response.json()
        tournament_ids = [p["tournament_id"] for p in participations]
        assert tournament.id in tournament_ids

    def test_permission_non_owner_cannot_update(self, api_client, tournament_setup):
        """Test 19: Non-owner cannot update tournament."""
        tournament = tournament_setup["tournament"]
        participant_user = tournament_setup["participant"]

        update_data = {
            "description": "Hacked!"
        }

        response = api_client.put(
            f"{API_V1_URL}/tournaments/{tournament.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {participant_user.token}"}
        )

        # Should be forbidden or unauthorized
        assert response.status_code in [403, 401]


# ============================================================================
# Test 20-23: Participant and Tournament Deletion
# ============================================================================

class TestDeletion:
    """Tests for deleting participants and tournaments."""

    def test_remove_participant(self, api_client, participant_factory, tournament_setup):
        """Test 20: Remove participant from tournament."""
        tournament = tournament_setup["tournament"]
        owner = tournament_setup["owner"]
        participant_user = tournament_setup["participant"]
        participant_club = tournament_setup["participant_club"]

        participant = participant_factory(
            participant_user,
            tournament,
            participant_club,
            "FC Test Team"
        )

        response = api_client.delete(
            f"{API_V1_URL}/tournaments/{tournament.id}/participants/{participant.id}",
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        assert response.status_code in [200, 204]

    def test_verify_participant_removed(self, api_client, participant_factory, tournament_setup):
        """Test 21: Verify participant is removed."""
        tournament = tournament_setup["tournament"]
        owner = tournament_setup["owner"]
        participant_user = tournament_setup["participant"]
        participant_club = tournament_setup["participant_club"]

        participant = participant_factory(
            participant_user,
            tournament,
            participant_club,
            "FC Test Team"
        )

        # Remove participant
        api_client.delete(
            f"{API_V1_URL}/tournaments/{tournament.id}/participants/{participant.id}",
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        time.sleep(0.5)

        # Verify not in list
        response = api_client.get(
            f"{API_V1_URL}/tournaments/{tournament.id}/participants"
        )
        response.raise_for_status()

        participants = response.json()
        participant_ids = [p["id"] for p in participants]
        assert participant.id not in participant_ids

    def test_delete_tournament(self, api_client, user_factory, club_factory, tournament_factory):
        """Test 22: Delete tournament (after cancelling)."""
        owner = user_factory("delete_owner", "Delete", "Owner")
        club = club_factory(owner)
        tournament = tournament_factory(owner, club, "Delete Test Tournament")

        # First cancel the tournament
        cancel_response = api_client.put(
            f"{API_V1_URL}/tournaments/{tournament.id}/status",
            json={"status": "cancelled"},
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        # If cancellation succeeds, verify status
        if cancel_response.status_code == 200:
            cancelled = cancel_response.json()
            assert cancelled["status"] == "cancelled"

        # Delete tournament
        response = api_client.delete(
            f"{API_V1_URL}/tournaments/{tournament.id}",
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        assert response.status_code in [200, 204]

    def test_verify_tournament_deleted(self, api_client, user_factory, club_factory, tournament_factory):
        """Test 23: Verify deleted tournament is not in active list."""
        owner = user_factory("verify_delete_owner", "Verify", "Owner")
        club = club_factory(owner)
        tournament = tournament_factory(owner, club, "Verify Delete Tournament")

        # Cancel and delete
        api_client.put(
            f"{API_V1_URL}/tournaments/{tournament.id}/status",
            json={"status": "cancelled"},
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        api_client.delete(
            f"{API_V1_URL}/tournaments/{tournament.id}",
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        time.sleep(0.5)

        # Verify not in list
        response = api_client.get(f"{API_V1_URL}/tournaments")
        response.raise_for_status()

        tournaments = response.json()
        tournament_ids = [t["id"] for t in tournaments]
        assert tournament.id not in tournament_ids


# ============================================================================
# Modular Helper Functions (reusable in other tests)
# ============================================================================

def create_tournament_with_participants(
    api_client,
    owner: User,
    club: Club,
    participant_count: int = 4
) -> tuple:
    """
    Reusable function to create a tournament with multiple participants.

    Returns:
        tuple: (tournament_id, tournament_data, list of participant_ids)
    """
    timestamp = int(time.time() * 1000)

    # Create tournament
    tournament_data = {
        "club_id": club.id,
        "name": f"Test Tournament {timestamp}",
        "sport_type": "football",
        "tournament_type": "knockout",
        "start_date": "2025-06-01T10:00:00Z",
        "end_date": "2025-06-02T18:00:00Z",
        "max_participants": participant_count
    }

    response = api_client.post(
        f"{API_V1_URL}/tournaments",
        json=tournament_data,
        headers={"Authorization": f"Bearer {owner.token}"}
    )
    response.raise_for_status()
    tournament = response.json()

    # Open registration
    api_client.put(
        f"{API_V1_URL}/tournaments/{tournament['id']}/status",
        json={"status": "registration_open"},
        headers={"Authorization": f"Bearer {owner.token}"}
    )

    # Create participants
    participant_ids = []
    for i in range(participant_count):
        participant_data = {
            "participant_club_id": club.id,
            "participant_name": f"Team {i + 1}",
            "display_name": f"T{i + 1}"
        }

        response = api_client.post(
            f"{API_V1_URL}/tournaments/{tournament['id']}/participants",
            json=participant_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()
        participant = response.json()
        participant_ids.append(participant["id"])

        # Confirm participant
        api_client.put(
            f"{API_V1_URL}/tournaments/{tournament['id']}/participants/{participant['id']}/status",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {owner.token}"}
        )

    return tournament["id"], tournament, participant_ids
