"""
Sprint 2 - Club Management Tests (Pytest)

Tests all club management endpoints including:
- Club CRUD operations
- Club search and filtering
- Member management
- Permission system
"""

import pytest
import time
from conftest import (
    API_V1_URL, User, Club,
    api_client, check_backend, user_factory, owner_user, member_user,
    two_users, club_factory, test_club, auth_headers
)


# ============================================================================
# Test 1-5: Club CRUD Operations
# ============================================================================

class TestClubCRUD:
    """Tests for basic Club CRUD operations."""

    def test_create_club(self, api_client, owner_user, club_factory):
        """Test 1: Create a new club."""
        club = club_factory(owner_user, city="Berlin", postal_code="10115")

        assert club.id is not None
        assert club.slug is not None
        assert club.owner_id == owner_user.id
        assert club.data["city"] == "Berlin"

    def test_list_clubs(self, api_client, test_club):
        """Test 2: List all clubs."""
        response = api_client.get(f"{API_V1_URL}/clubs")
        response.raise_for_status()

        clubs = response.json()
        assert isinstance(clubs, list)

        # Verify our test club is in the list
        club_ids = [club["id"] for club in clubs]
        assert test_club.id in club_ids

    def test_get_club_by_id(self, api_client, test_club):
        """Test 3: Get club by ID."""
        response = api_client.get(f"{API_V1_URL}/clubs/{test_club.id}")
        response.raise_for_status()

        club = response.json()
        assert club["id"] == test_club.id
        assert club["name"] == test_club.name

    def test_get_club_by_slug(self, api_client, test_club):
        """Test 4: Get club by slug."""
        response = api_client.get(f"{API_V1_URL}/clubs/slug/{test_club.slug}")
        response.raise_for_status()

        club = response.json()
        assert club["id"] == test_club.id
        assert club["slug"] == test_club.slug

    def test_update_club(self, api_client, owner_user, test_club):
        """Test 5: Update club details."""
        update_data = {
            "description": "Aktualisierte Beschreibung für Tests",
            "website": "https://fctest.de"
        }

        response = api_client.put(
            f"{API_V1_URL}/clubs/{test_club.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {owner_user.token}"}
        )
        response.raise_for_status()

        updated_club = response.json()
        assert "Aktualisierte" in updated_club["description"]
        assert updated_club["website"] == "https://fctest.de"


# ============================================================================
# Test 6-8: Club Search and Filtering
# ============================================================================

class TestClubSearch:
    """Tests for club search and filtering functionality."""

    def test_search_clubs_by_name(self, api_client, club_factory, owner_user):
        """Test 6: Search clubs by name."""
        # Create a club with unique name
        timestamp = int(time.time() * 1000)
        club = club_factory(owner_user, name=f"SearchTest Sprint2 {timestamp}")

        response = api_client.get(
            f"{API_V1_URL}/clubs",
            params={"search": "SearchTest Sprint2"}
        )
        response.raise_for_status()

        clubs = response.json()
        club_ids = [c["id"] for c in clubs]
        assert club.id in club_ids

    def test_filter_clubs_by_city(self, api_client, club_factory, owner_user):
        """Test 7: Filter clubs by city."""
        # Create club in specific city
        club = club_factory(owner_user, city="Berlin")

        response = api_client.get(
            f"{API_V1_URL}/clubs",
            params={"city": "Berlin"}
        )
        response.raise_for_status()

        clubs = response.json()
        club_ids = [c["id"] for c in clubs]
        assert club.id in club_ids

        # Verify all returned clubs are from Berlin
        for c in clubs:
            assert c["city"] == "Berlin"

    def test_count_clubs(self, api_client):
        """Test 8: Count clubs."""
        response = api_client.get(f"{API_V1_URL}/clubs/count")
        response.raise_for_status()

        count_data = response.json()
        assert "count" in count_data
        assert isinstance(count_data["count"], int)
        assert count_data["count"] >= 0


# ============================================================================
# Test 9-13: Member Management
# ============================================================================

class TestClubMembers:
    """Tests for club member management."""

    def test_list_club_members_owner_present(self, api_client, owner_user, test_club):
        """Test 9: List club members - owner should be present."""
        response = api_client.get(f"{API_V1_URL}/clubs/{test_club.id}/members")
        response.raise_for_status()

        members = response.json()
        assert isinstance(members, list)

        # Owner should be a member
        owner_ids = [m["user_id"] for m in members]
        assert owner_user.id in owner_ids

    def test_add_member_to_club(self, api_client, two_users, test_club):
        """Test 10: Add a member to a club."""
        owner = two_users["owner"]
        member = two_users["member"]

        # Create a club for this test
        timestamp = int(time.time() * 1000)
        club_data = {
            "name": f"Member Test Club {timestamp}",
            "city": "Berlin"
        }

        club_response = api_client.post(
            f"{API_V1_URL}/clubs",
            json=club_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        club_response.raise_for_status()
        club = club_response.json()
        club_id = club["id"]

        # Add member to club
        member_data = {
            "user_id": member.id,
            "role": "member",
            "department": "Erste Mannschaft",
            "position": "Spieler"
        }

        response = api_client.post(
            f"{API_V1_URL}/clubs/{club_id}/members",
            json=member_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        member_result = response.json()
        assert member_result["user_id"] == member.id
        assert member_result["role"] == "member"

    def test_verify_member_count(self, api_client, two_users, club_factory):
        """Test 11: Verify member count increases after adding members."""
        owner = two_users["owner"]
        member = two_users["member"]

        # Create a fresh club
        club = club_factory(owner)

        # Get initial member count
        response = api_client.get(f"{API_V1_URL}/clubs/{club.id}/members")
        response.raise_for_status()
        initial_count = len(response.json())

        # Add a member
        member_data = {
            "user_id": member.id,
            "role": "member",
            "department": "Erste Mannschaft",
            "position": "Spieler"
        }

        api_client.post(
            f"{API_V1_URL}/clubs/{club.id}/members",
            json=member_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        ).raise_for_status()

        # Wait a moment for consistency
        time.sleep(0.5)

        # Get new member count
        response = api_client.get(f"{API_V1_URL}/clubs/{club.id}/members")
        response.raise_for_status()
        new_count = len(response.json())

        assert new_count >= initial_count + 1

    def test_update_member_role(self, api_client, two_users, club_factory):
        """Test 12: Update member role."""
        owner = two_users["owner"]
        member = two_users["member"]

        # Create club and add member
        club = club_factory(owner)

        member_data = {
            "user_id": member.id,
            "role": "member",
            "department": "Erste Mannschaft",
            "position": "Spieler"
        }

        api_client.post(
            f"{API_V1_URL}/clubs/{club.id}/members",
            json=member_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        ).raise_for_status()

        # Update member role to admin
        update_data = {
            "role": "admin",
            "position": "Co-Trainer"
        }

        response = api_client.put(
            f"{API_V1_URL}/clubs/{club.id}/members/{member.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        )
        response.raise_for_status()

        updated_member = response.json()
        assert updated_member["role"] == "admin"
        assert updated_member["position"] == "Co-Trainer"

    def test_get_my_club_memberships(self, api_client, two_users, club_factory):
        """Test 13: Get my club memberships."""
        owner = two_users["owner"]
        member = two_users["member"]

        # Create club and add member
        club = club_factory(owner)

        member_data = {
            "user_id": member.id,
            "role": "member"
        }

        api_client.post(
            f"{API_V1_URL}/clubs/{club.id}/members",
            json=member_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        ).raise_for_status()

        # Get member's memberships
        response = api_client.get(
            f"{API_V1_URL}/clubs/me/memberships",
            headers={"Authorization": f"Bearer {member.token}"}
        )
        response.raise_for_status()

        memberships = response.json()
        club_ids = [m["club_id"] for m in memberships]
        assert club.id in club_ids


# ============================================================================
# Test 14-16: Permissions and Member Removal
# ============================================================================

class TestClubPermissions:
    """Tests for club permissions and member removal."""

    def test_permission_non_admin_cannot_delete(self, api_client, two_users, club_factory):
        """Test 14: Non-owner cannot delete club."""
        owner = two_users["owner"]
        member = two_users["member"]

        # Create club
        club = club_factory(owner)

        # Try to delete as non-owner (should fail with 403)
        response = api_client.delete(
            f"{API_V1_URL}/clubs/{club.id}",
            headers={"Authorization": f"Bearer {member.token}"}
        )

        # Should be forbidden (403) or unauthorized (401)
        assert response.status_code in [403, 401]

    def test_remove_member_from_club(self, api_client, two_users, club_factory):
        """Test 15: Remove member from club."""
        owner = two_users["owner"]
        member = two_users["member"]

        # Create club and add member
        club = club_factory(owner)

        member_data = {
            "user_id": member.id,
            "role": "member"
        }

        api_client.post(
            f"{API_V1_URL}/clubs/{club.id}/members",
            json=member_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        ).raise_for_status()

        # Remove member
        response = api_client.delete(
            f"{API_V1_URL}/clubs/{club.id}/members/{member.id}",
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        # Accept both 200 and 204 as success
        assert response.status_code in [200, 204]

    def test_verify_member_removed(self, api_client, two_users, club_factory):
        """Test 16: Verify member is removed from club."""
        owner = two_users["owner"]
        member = two_users["member"]

        # Create club and add member
        club = club_factory(owner)

        member_data = {
            "user_id": member.id,
            "role": "member"
        }

        api_client.post(
            f"{API_V1_URL}/clubs/{club.id}/members",
            json=member_data,
            headers={"Authorization": f"Bearer {owner.token}"}
        ).raise_for_status()

        # Remove member
        api_client.delete(
            f"{API_V1_URL}/clubs/{club.id}/members/{member.id}",
            headers={"Authorization": f"Bearer {owner.token}"}
        )

        # Wait for consistency
        time.sleep(0.5)

        # Verify member is not in list
        response = api_client.get(f"{API_V1_URL}/clubs/{club.id}/members")
        response.raise_for_status()

        members = response.json()
        member_ids = [m["user_id"] for m in members]
        assert member.id not in member_ids


# ============================================================================
# Test 17-18: Club Deletion
# ============================================================================

class TestClubDeletion:
    """Tests for club deletion (soft delete)."""

    def test_delete_club(self, api_client, owner_user, club_factory):
        """Test 17: Delete club (soft delete)."""
        club = club_factory(owner_user)

        response = api_client.delete(
            f"{API_V1_URL}/clubs/{club.id}",
            headers={"Authorization": f"Bearer {owner_user.token}"}
        )

        # Accept both 200 and 204 as success
        assert response.status_code in [200, 204]

    def test_verify_deleted_club_not_in_list(self, api_client, owner_user, club_factory):
        """Test 18: Verify deleted club is not in active list."""
        club = club_factory(owner_user)

        # Delete the club
        api_client.delete(
            f"{API_V1_URL}/clubs/{club.id}",
            headers={"Authorization": f"Bearer {owner_user.token}"}
        )

        # Wait for consistency
        time.sleep(0.5)

        # Verify club is not in list
        response = api_client.get(f"{API_V1_URL}/clubs")
        response.raise_for_status()

        clubs = response.json()
        club_ids = [c["id"] for c in clubs]
        assert club.id not in club_ids


# ============================================================================
# Modular Test Functions (can be reused in other tests)
# ============================================================================

def create_club_with_member(api_client, owner: User, member: User, club_name: str = None) -> tuple:
    """
    Reusable function to create a club with a member.

    Returns:
        tuple: (club_id, club_data)
    """
    timestamp = int(time.time() * 1000)
    name = club_name or f"Test Club {timestamp}"

    # Create club
    club_data = {
        "name": name,
        "city": "Berlin"
    }

    response = api_client.post(
        f"{API_V1_URL}/clubs",
        json=club_data,
        headers={"Authorization": f"Bearer {owner.token}"}
    )
    response.raise_for_status()
    club = response.json()

    # Add member
    member_data = {
        "user_id": member.id,
        "role": "member"
    }

    api_client.post(
        f"{API_V1_URL}/clubs/{club['id']}/members",
        json=member_data,
        headers={"Authorization": f"Bearer {owner.token}"}
    ).raise_for_status()

    return club["id"], club


def delete_club(api_client, club_id: str, owner_token: str):
    """
    Reusable function to delete a club.

    Args:
        api_client: The API client
        club_id: ID of club to delete
        owner_token: Token of club owner
    """
    response = api_client.delete(
        f"{API_V1_URL}/clubs/{club_id}",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    response.raise_for_status()
