"""
Pytest configuration and reusable fixtures for UnserTurnierplan tests.

This module provides fixtures for creating and cleaning up test resources
in a modular way, allowing tests to be composed from smaller building blocks.
"""

import os
import time
import pytest
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1_URL = f"{BASE_URL}/api/v1"


@dataclass
class User:
    """Represents a test user with authentication."""
    id: str
    email: str
    password: str
    first_name: str
    last_name: str
    token: str


@dataclass
class Club:
    """Represents a test club."""
    id: str
    name: str
    slug: str
    owner_id: str
    data: Dict[str, Any]


@dataclass
class Tournament:
    """Represents a test tournament."""
    id: str
    name: str
    slug: str
    club_id: str
    creator_id: str
    data: Dict[str, Any]


@dataclass
class Participant:
    """Represents a tournament participant."""
    id: str
    tournament_id: str
    participant_name: str
    data: Dict[str, Any]


@dataclass
class Match:
    """Represents a match."""
    id: str
    tournament_id: str
    round_number: int
    data: Dict[str, Any]


# ============================================================================
# Session-scoped fixtures (run once per test session)
# ============================================================================

@pytest.fixture(scope="session")
def api_client():
    """Provides a requests session for API calls."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="session")
def check_backend(api_client):
    """Verifies the backend is running before tests start."""
    try:
        response = api_client.get(f"{BASE_URL}/health")
        response.raise_for_status()
        assert "healthy" in response.text.lower()
        return True
    except Exception as e:
        pytest.fail(f"Backend is not running at {BASE_URL}: {e}")


# ============================================================================
# User fixtures - modular user creation
# ============================================================================

@pytest.fixture
def user_factory(api_client, check_backend):
    """
    Factory fixture for creating test users.

    Usage:
        user = user_factory("owner", "Max", "Mustermann")
    """
    created_users = []

    def _create_user(
        role: str = "user",
        first_name: str = "Test",
        last_name: str = "User",
        password: str = "Test1234!"
    ) -> User:
        """Create a new test user with authentication."""
        timestamp = int(time.time() * 1000)
        email = f"test_{role}_{timestamp}@test.com"

        # Register user
        register_data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        }

        response = api_client.post(
            f"{API_V1_URL}/auth/register",
            json=register_data
        )
        response.raise_for_status()
        user_data = response.json()

        # Login to get token
        login_data = {
            "email": email,
            "password": password
        }

        response = api_client.post(
            f"{API_V1_URL}/auth/login/json",
            json=login_data
        )
        response.raise_for_status()
        login_data = response.json()

        user = User(
            id=user_data["id"],
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            token=login_data["access_token"]
        )

        created_users.append(user)
        return user

    yield _create_user

    # Cleanup: Users are typically cleaned up by database reset
    # but we track them for potential cleanup
    created_users.clear()


@pytest.fixture
def owner_user(user_factory):
    """Creates a single owner user for tests."""
    return user_factory("owner", "Max", "Mustermann")


@pytest.fixture
def member_user(user_factory):
    """Creates a single member user for tests."""
    return user_factory("member", "Anna", "Schmidt")


@pytest.fixture
def two_users(user_factory):
    """Creates two users (owner and member) for tests."""
    owner = user_factory("owner", "Max", "Mustermann")
    member = user_factory("member", "Anna", "Schmidt")
    return {"owner": owner, "member": member}


# ============================================================================
# Club fixtures - modular club creation
# ============================================================================

@pytest.fixture
def club_factory(api_client):
    """
    Factory fixture for creating test clubs.

    Usage:
        club = club_factory(owner_user, "Test Club")
    """
    created_clubs = []

    def _create_club(
        user: User,
        name: Optional[str] = None,
        **kwargs
    ) -> Club:
        """Create a new test club."""
        timestamp = int(time.time() * 1000)
        club_name = name or f"Test Club {timestamp}"

        club_data = {
            "name": club_name,
            "description": kwargs.get("description", "A test club"),
            "city": kwargs.get("city", "Berlin"),
            "postal_code": kwargs.get("postal_code", "10115"),
            "country": kwargs.get("country", "Deutschland"),
            "phone": kwargs.get("phone", "+49 30 12345678"),
            "email": kwargs.get("email", "info@testclub.de"),
            "founded_date": kwargs.get("founded_date", "1950-01-15")
        }

        response = api_client.post(
            f"{API_V1_URL}/clubs",
            json=club_data,
            headers={"Authorization": f"Bearer {user.token}"}
        )
        response.raise_for_status()
        data = response.json()

        club = Club(
            id=data["id"],
            name=data["name"],
            slug=data["slug"],
            owner_id=user.id,
            data=data
        )

        created_clubs.append(club)
        return club

    yield _create_club

    # Cleanup clubs after test
    for club in created_clubs:
        try:
            # Note: Club deletion would need appropriate token
            pass
        except Exception:
            pass
    created_clubs.clear()


@pytest.fixture
def test_club(owner_user, club_factory):
    """Creates a single test club for tests."""
    return club_factory(owner_user)


# ============================================================================
# Tournament fixtures - modular tournament creation
# ============================================================================

@pytest.fixture
def tournament_factory(api_client):
    """
    Factory fixture for creating test tournaments.

    Usage:
        tournament = tournament_factory(owner_user, test_club, "Spring Tournament")
    """
    created_tournaments = []

    def _create_tournament(
        user: User,
        club: Club,
        name: Optional[str] = None,
        **kwargs
    ) -> Tournament:
        """Create a new test tournament."""
        timestamp = int(time.time() * 1000)
        tournament_name = name or f"Test Tournament {timestamp}"

        tournament_data = {
            "club_id": club.id,
            "name": tournament_name,
            "sport_type": kwargs.get("sport_type", "football"),
            "tournament_type": kwargs.get("tournament_type", "knockout"),
            "start_date": kwargs.get("start_date", "2025-06-01T10:00:00Z"),
            "end_date": kwargs.get("end_date", "2025-06-02T18:00:00Z"),
            "registration_start": kwargs.get("registration_start"),
            "registration_end": kwargs.get("registration_end"),
            "max_participants": kwargs.get("max_participants", 16),
            "participant_type": kwargs.get("participant_type", "team"),
            "description": kwargs.get("description", "A test tournament"),
            "location": kwargs.get("location", club.data.get("city")),
            "rules": kwargs.get("rules", "Standard rules apply")
        }

        # Remove None values
        tournament_data = {k: v for k, v in tournament_data.items() if v is not None}

        response = api_client.post(
            f"{API_V1_URL}/tournaments",
            json=tournament_data,
            headers={"Authorization": f"Bearer {user.token}"}
        )
        response.raise_for_status()
        data = response.json()

        tournament = Tournament(
            id=data["id"],
            name=data["name"],
            slug=data["slug"],
            club_id=club.id,
            creator_id=user.id,
            data=data
        )

        created_tournaments.append(tournament)
        return tournament

    yield _create_tournament

    # Cleanup tournaments after test
    created_tournaments.clear()


@pytest.fixture
def test_tournament(owner_user, test_club, tournament_factory):
    """Creates a single test tournament for tests."""
    return tournament_factory(owner_user, test_club)


# ============================================================================
# Participant fixtures - modular participant creation
# ============================================================================

@pytest.fixture
def participant_factory(api_client):
    """
    Factory fixture for creating tournament participants.

    Usage:
        participant = participant_factory(user, tournament, club, "Team A")
    """
    created_participants = []

    def _create_participant(
        user: User,
        tournament: Tournament,
        club: Club,
        name: Optional[str] = None,
        **kwargs
    ) -> Participant:
        """Create a new tournament participant."""
        timestamp = int(time.time() * 1000)
        participant_name = name or f"Test Team {timestamp}"

        participant_data = {
            "participant_club_id": club.id,
            "participant_name": participant_name,
            "display_name": kwargs.get("display_name", participant_name[:20]),
            "contact_email": kwargs.get("contact_email", user.email),
            "contact_phone": kwargs.get("contact_phone")
        }

        # Remove None values
        participant_data = {k: v for k, v in participant_data.items() if v is not None}

        response = api_client.post(
            f"{API_V1_URL}/tournaments/{tournament.id}/participants",
            json=participant_data,
            headers={"Authorization": f"Bearer {user.token}"}
        )
        response.raise_for_status()
        data = response.json()

        participant = Participant(
            id=data["id"],
            tournament_id=tournament.id,
            participant_name=participant_name,
            data=data
        )

        created_participants.append(participant)
        return participant

    yield _create_participant

    # Cleanup participants after test
    created_participants.clear()


@pytest.fixture
def confirmed_participant(participant_factory, api_client):
    """
    Factory for creating confirmed participants.

    Usage:
        participant = confirmed_participant(user, tournament, club, "Team A")
    """
    def _create_confirmed_participant(
        user: User,
        tournament: Tournament,
        club: Club,
        name: Optional[str] = None,
        **kwargs
    ) -> Participant:
        """Create and confirm a tournament participant."""
        participant = participant_factory(user, tournament, club, name, **kwargs)

        # Confirm the participant
        response = api_client.put(
            f"{API_V1_URL}/tournaments/{tournament.id}/participants/{participant.id}/status",
            json={"status": "confirmed"},
            headers={"Authorization": f"Bearer {user.token}"}
        )
        response.raise_for_status()
        participant.data = response.json()

        return participant

    return _create_confirmed_participant


@pytest.fixture
def multiple_participants(confirmed_participant):
    """
    Factory for creating multiple confirmed participants.

    Usage:
        participants = multiple_participants(user, tournament, club, count=8)
    """
    def _create_multiple(
        user: User,
        tournament: Tournament,
        club: Club,
        count: int = 4,
        name_prefix: str = "Team"
    ) -> List[Participant]:
        """Create multiple confirmed participants."""
        participants = []
        for i in range(1, count + 1):
            name = f"{name_prefix} {i}"
            participant = confirmed_participant(
                user, tournament, club, name,
                display_name=f"T{i}"
            )
            participants.append(participant)
        return participants

    return _create_multiple


# ============================================================================
# Match fixtures - modular match creation
# ============================================================================

@pytest.fixture
def match_factory(api_client):
    """
    Factory fixture for creating matches.

    Usage:
        match = match_factory(user, tournament, round_number=1)
    """
    created_matches = []

    def _create_match(
        user: User,
        tournament: Tournament,
        round_number: int = 1,
        **kwargs
    ) -> Match:
        """Create a new match."""
        match_data = {
            "tournament_id": tournament.id,
            "round_number": round_number,
            "match_number": kwargs.get("match_number", 1),
            "round_name": kwargs.get("round_name", f"Round {round_number}"),
            "scheduled_time": kwargs.get("scheduled_time"),
            "location": kwargs.get("location"),
            "participant_ids": kwargs.get("participant_ids", [])
        }

        # Remove None values
        match_data = {k: v for k, v in match_data.items() if v is not None}

        response = api_client.post(
            f"{API_V1_URL}/matches",
            json=match_data,
            headers={"Authorization": f"Bearer {user.token}"}
        )
        response.raise_for_status()
        data = response.json()

        match = Match(
            id=data["id"],
            tournament_id=tournament.id,
            round_number=round_number,
            data=data
        )

        created_matches.append(match)
        return match

    yield _create_match

    # Cleanup matches after test
    created_matches.clear()


# ============================================================================
# Helper fixtures for common operations
# ============================================================================

@pytest.fixture
def auth_headers():
    """
    Helper to generate authorization headers.

    Usage:
        headers = auth_headers(user.token)
    """
    def _headers(token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    return _headers


@pytest.fixture
def wait_for_status():
    """Helper to wait for a resource to reach a certain status."""
    def _wait(
        api_client,
        url: str,
        status_field: str,
        expected_status: str,
        token: str,
        max_attempts: int = 10,
        delay: float = 0.5
    ):
        """Wait for a resource to reach expected status."""
        for _ in range(max_attempts):
            response = api_client.get(
                url,
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get(status_field) == expected_status:
                    return data
            time.sleep(delay)

        raise TimeoutError(
            f"Resource did not reach status {expected_status} "
            f"in {max_attempts * delay} seconds"
        )

    return _wait


# ============================================================================
# Cleanup utilities
# ============================================================================

@pytest.fixture
def cleanup_tracker():
    """
    Tracks resources for cleanup after test.

    Usage:
        cleanup_tracker.add("club", club_id, delete_func)
    """
    items = []

    class CleanupTracker:
        def add(self, resource_type: str, resource_id: str, cleanup_func):
            items.append((resource_type, resource_id, cleanup_func))

        def cleanup_all(self):
            for resource_type, resource_id, cleanup_func in reversed(items):
                try:
                    cleanup_func(resource_id)
                except Exception as e:
                    print(f"Warning: Failed to cleanup {resource_type} {resource_id}: {e}")

    tracker = CleanupTracker()
    yield tracker
    tracker.cleanup_all()
