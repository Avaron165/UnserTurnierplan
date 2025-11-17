# Pytest Test Suite for UnserTurnierplan

This directory contains the modular pytest-based test suite for UnserTurnierplan, rewritten from the original bash scripts. The tests are organized into three main sprints covering club management, tournament management, and match scheduling.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Modular Design](#modular-design)
- [Configuration](#configuration)
- [Test Coverage](#test-coverage)
- [Troubleshooting](#troubleshooting)

## Overview

The test suite is divided into three main test files, corresponding to the development sprints:

- **Sprint 2 (`test_sprint2_clubs.py`)**: Club CRUD, search, filtering, member management, and permissions
- **Sprint 3 (`test_sprint3_tournaments.py`)**: Tournament CRUD, status lifecycle, participant management, and payments
- **Sprint 4 (`test_sprint4_matches.py`)**: Match CRUD, bracket generation, round-robin scheduling, scoring, and standings

## Installation

### Prerequisites

- Python 3.9 or higher
- Backend API running on `http://localhost:8000` (or set `API_BASE_URL` environment variable)
- PostgreSQL database configured and running

### Install Dependencies

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Or install in a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-test.txt
```

## Running Tests

### Start the Backend

Before running tests, ensure the backend is running:

```bash
docker-compose up -d
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with output capture disabled (see print statements)
pytest -s
```

### Run Specific Test Files

```bash
# Run only Sprint 2 tests
pytest tests/test_sprint2_clubs.py

# Run only Sprint 3 tests
pytest tests/test_sprint3_tournaments.py

# Run only Sprint 4 tests
pytest tests/test_sprint4_matches.py
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest tests/test_sprint2_clubs.py::TestClubCRUD

# Run a specific test function
pytest tests/test_sprint2_clubs.py::TestClubCRUD::test_create_club
```

### Run Tests by Marker

```bash
# Run only CRUD tests
pytest -m crud

# Run only permission tests
pytest -m permissions

# Run Sprint 2 tests
pytest -m sprint2

# Run Sprint 3 tests
pytest -m sprint3

# Run Sprint 4 tests
pytest -m sprint4
```

### Run Tests in Parallel

If you have pytest-xdist installed, you can run tests in parallel:

```bash
# Run tests using all CPU cores
pytest -n auto

# Run tests using 4 workers
pytest -n 4
```

### Generate Test Reports

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Generate HTML test report
pytest --html=report.html --self-contained-html

# Generate JSON report
pytest --json-report --json-report-file=report.json
```

## Test Structure

### Directory Layout

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_sprint2_clubs.py          # Club management tests
├── test_sprint3_tournaments.py    # Tournament management tests
├── test_sprint4_matches.py        # Match and bracket tests
├── sprint2_tests.sh               # Original bash tests (reference)
├── sprint3_tests.sh               # Original bash tests (reference)
├── sprint4_tests.sh               # Original bash tests (reference)
└── README_PYTEST.md               # This file
```

### Test Classes

Each test file is organized into test classes based on functionality:

**Sprint 2 (test_sprint2_clubs.py):**
- `TestClubCRUD` - Basic club operations
- `TestClubSearch` - Search and filtering
- `TestClubMembers` - Member management
- `TestClubPermissions` - Permissions and member removal
- `TestClubDeletion` - Club deletion

**Sprint 3 (test_sprint3_tournaments.py):**
- `TestTournamentCRUD` - Basic tournament operations
- `TestTournamentFiltering` - Search and filtering
- `TestTournamentStatus` - Status lifecycle and statistics
- `TestParticipantManagement` - Participant registration and management
- `TestUserTournamentsAndPermissions` - User views and permissions
- `TestDeletion` - Participant and tournament deletion

**Sprint 4 (test_sprint4_matches.py):**
- `TestMatchCRUD` - Basic match operations
- `TestKnockoutBracket` - Knockout bracket generation
- `TestRoundRobinScheduling` - Round-robin scheduling
- `TestMatchScoring` - Match scoring system
- `TestMatchStatus` - Match status updates
- `TestTournamentStandings` - Standings calculation
- `TestMatchFiltering` - Match filtering and queries

## Modular Design

The tests are designed to be modular and reusable:

### Fixtures (conftest.py)

**User Fixtures:**
- `user_factory` - Create test users dynamically
- `owner_user` - Single owner user
- `member_user` - Single member user
- `two_users` - Owner and member pair

**Club Fixtures:**
- `club_factory` - Create test clubs dynamically
- `test_club` - Single test club with owner

**Tournament Fixtures:**
- `tournament_factory` - Create test tournaments dynamically
- `test_tournament` - Single test tournament

**Participant Fixtures:**
- `participant_factory` - Create individual participants
- `confirmed_participant` - Create and confirm participants
- `multiple_participants` - Create multiple confirmed participants

**Match Fixtures:**
- `match_factory` - Create test matches dynamically

### Reusable Helper Functions

Each test file includes modular helper functions at the bottom that can be imported and reused:

**test_sprint2_clubs.py:**
- `create_club_with_member()` - Create club with a member
- `delete_club()` - Delete a club

**test_sprint3_tournaments.py:**
- `create_tournament_with_participants()` - Create tournament with multiple participants

**test_sprint4_matches.py:**
- `generate_and_score_matches()` - Generate and score matches
- `create_tournament_with_bracket()` - Create tournament with knockout bracket

### Example Usage of Fixtures

```python
def test_my_feature(user_factory, club_factory, tournament_factory):
    # Create users
    owner = user_factory("owner", "John", "Doe")
    participant = user_factory("participant", "Jane", "Smith")

    # Create club
    club = club_factory(owner, city="Munich")

    # Create tournament
    tournament = tournament_factory(
        owner,
        club,
        max_participants=16,
        tournament_type="knockout"
    )

    # Run your test logic
    assert tournament.id is not None
```

## Configuration

### Environment Variables

You can configure the test environment using environment variables:

```bash
# Set custom API URL
export API_BASE_URL="http://localhost:3000"

# Run tests
pytest
```

### pytest.ini

The `pytest.ini` file in the project root contains default configuration:

- Test discovery patterns
- Console output settings
- Markers for categorizing tests
- Warning filters
- Default command-line options

## Test Coverage

### Current Coverage

The test suite covers:

**Sprint 2 - Club Management (18 tests):**
1. ✅ Club CRUD operations
2. ✅ Search and filtering (by name, city)
3. ✅ Member management (add, update, remove)
4. ✅ Permission system
5. ✅ Soft deletion

**Sprint 3 - Tournament Management (23 tests):**
1. ✅ Tournament CRUD operations
2. ✅ Filtering (by sport type, city with UTF-8)
3. ✅ Status lifecycle (draft → published → registration_open → cancelled)
4. ✅ Participant registration and management
5. ✅ Payment tracking
6. ✅ Statistics and reporting
7. ✅ User-specific views (my tournaments, my participations)
8. ✅ Permission system

**Sprint 4 - Match Scheduling & Brackets (27 tests):**
1. ✅ Match CRUD operations
2. ✅ Knockout bracket generation (with proper rounds)
3. ✅ Round-robin scheduling (circle method)
4. ✅ Match scoring with winner tracking
5. ✅ Match status updates (scheduled → in_progress → completed)
6. ✅ Tournament standings calculation
7. ✅ Standings recalculation
8. ✅ Match filtering (by round, status)

### View Coverage Report

```bash
# Generate and view coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

## Troubleshooting

### Backend Not Running

**Error:** Connection refused or health check fails

**Solution:**
```bash
# Start backend
docker-compose up -d

# Check backend status
curl http://localhost:8000/health
```

### Tests Fail Due to State

**Issue:** Previous test data interferes with new tests

**Solution:**
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'pytest'`

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements-test.txt
```

### Slow Test Execution

**Solution:**
```bash
# Run tests in parallel
pytest -n auto

# Run specific tests only
pytest tests/test_sprint2_clubs.py::TestClubCRUD
```

### API URL Configuration

**Issue:** Tests connect to wrong API endpoint

**Solution:**
```bash
# Set environment variable
export API_BASE_URL="http://localhost:8000"

# Or modify conftest.py:
BASE_URL = "http://your-api-url:port"
```

## Comparison with Original Tests

### Advantages of Pytest Tests

1. **Modularity**: Fixtures allow creating and reusing test resources
2. **Readability**: Tests are organized in classes with clear names
3. **Error Handling**: Better error messages and stack traces
4. **Parallel Execution**: Can run tests in parallel with pytest-xdist
5. **Integration**: Works with CI/CD, coverage tools, and IDEs
6. **Debugging**: Can use Python debugger (pdb) with pytest
7. **Reusability**: Fixtures and helper functions can be imported

### Original Bash Tests

The original bash test scripts are preserved in:
- `tests/sprint2_tests.sh`
- `tests/sprint3_tests.sh`
- `tests/sprint4_tests.sh`

You can still run them if needed:
```bash
./tests/sprint2_tests.sh
./tests/sprint3_tests.sh
./tests/sprint4_tests.sh
```

## Contributing

When adding new tests:

1. **Follow the pattern**: Organize tests into classes by functionality
2. **Use fixtures**: Leverage existing fixtures for creating resources
3. **Add markers**: Tag tests with appropriate markers (e.g., `@pytest.mark.sprint5`)
4. **Document**: Add docstrings to test functions
5. **Keep DRY**: Extract reusable logic into helper functions
6. **Clean up**: Tests should be independent and not leave residual state

## Best Practices

1. **Test Independence**: Each test should be able to run independently
2. **Use Factories**: Use factory fixtures instead of hardcoded test data
3. **Descriptive Names**: Test names should describe what they test
4. **Arrange-Act-Assert**: Follow the AAA pattern in test functions
5. **One Concept**: Each test should test one concept
6. **Fast Tests**: Keep tests fast by minimizing unnecessary operations

## Examples

### Creating a Complete Test

```python
import pytest

class TestMyFeature:
    """Tests for my new feature."""

    def test_feature_works_as_expected(self, api_client, owner_user, test_club):
        """Test that my feature works correctly."""
        # Arrange - set up test data
        feature_data = {
            "name": "Test Feature",
            "club_id": test_club.id
        }

        # Act - execute the feature
        response = api_client.post(
            f"{API_V1_URL}/features",
            json=feature_data,
            headers={"Authorization": f"Bearer {owner_user.token}"}
        )

        # Assert - verify the results
        response.raise_for_status()
        feature = response.json()
        assert feature["name"] == "Test Feature"
        assert feature["club_id"] == test_club.id
```

### Using Multiple Fixtures

```python
def test_complex_scenario(
    user_factory,
    club_factory,
    tournament_factory,
    multiple_participants
):
    """Test a complex multi-step scenario."""
    # Create resources
    owner = user_factory("owner", "John", "Doe")
    club = club_factory(owner, city="Berlin")
    tournament = tournament_factory(owner, club)
    participants = multiple_participants(owner, tournament, club, count=8)

    # Test logic here
    assert len(participants) == 8
```

## License

Same as the main project.
