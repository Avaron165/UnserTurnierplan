#!/bin/bash

# Sprint 4 Tests - Match Scheduling & Brackets
# Tests all match-related functionality including CRUD, scoring, bracket generation, and standings

set -e  # Exit on error
set +H  # Disable history expansion (fixes ! in passwords)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000/api/v1"

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test helper functions
test_passed() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -e "${GREEN}✓${NC} $1"
}

test_failed() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -e "${RED}✗${NC} $1"
    echo -e "${RED}  Error: $2${NC}"
}

print_header() {
    echo ""
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}========================================${NC}"
}

print_summary() {
    echo ""
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}TEST SUMMARY${NC}"
    echo -e "${YELLOW}========================================${NC}"
    echo "Tests run: $TESTS_RUN"
    echo -e "${GREEN}Tests passed: $TESTS_PASSED${NC}"
    if [ $TESTS_FAILED -gt 0 ]; then
        echo -e "${RED}Tests failed: $TESTS_FAILED${NC}"
    else
        echo -e "${GREEN}All tests passed!${NC}"
    fi
    echo ""
}

# ==================== SETUP ====================

print_header "SPRINT 4 - MATCH SCHEDULING & BRACKETS TESTS"

# Create test user
echo "Setting up test environment..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "match_test@test.com",
        "password": "Test1234!",
        "first_name": "Match",
        "last_name": "Tester"
    }')

USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.id')

if [ "$USER_ID" == "null" ]; then
    echo -e "${RED}Failed to create test user${NC}"
    exit 1
fi

# Login to get token
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/json" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "match_test@test.com",
        "password": "Test1234!"
    }')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$ACCESS_TOKEN" == "null" ]; then
    echo -e "${RED}Failed to login${NC}"
    exit 1
fi

echo "Test user created. Token: ${ACCESS_TOKEN:0:20}..."

# Create test club
CLUB_RESPONSE=$(curl -s -X POST "$BASE_URL/clubs" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Match Test FC",
        "city": "München"
    }')

CLUB_ID=$(echo $CLUB_RESPONSE | jq -r '.id')
echo "Test club created: $CLUB_ID"

# Create test tournament
TOURNAMENT_RESPONSE=$(curl -s -X POST "$BASE_URL/tournaments" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "club_id": "'$CLUB_ID'",
        "name": "Spring Knockout Tournament 2025",
        "sport_type": "football",
        "tournament_type": "knockout",
        "start_date": "2025-06-01T10:00:00Z",
        "end_date": "2025-06-02T18:00:00Z",
        "max_participants": 8,
        "participant_type": "team"
    }')

TOURNAMENT_ID=$(echo $TOURNAMENT_RESPONSE | jq -r '.id')
echo "Test tournament created: $TOURNAMENT_ID"

# Register 8 participants
PARTICIPANT_IDS=()
for i in {1..8}; do
    PARTICIPANT_RESPONSE=$(curl -s -X POST "$BASE_URL/tournaments/$TOURNAMENT_ID/participants" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "participant_club_id": "'$CLUB_ID'",
            "participant_name": "Team '$i'",
            "display_name": "T'$i'"
        }')
    
    PARTICIPANT_ID=$(echo $PARTICIPANT_RESPONSE | jq -r '.id')
    PARTICIPANT_IDS+=($PARTICIPANT_ID)
    
    # Confirm participant
    curl -s -X PUT "$BASE_URL/tournaments/$TOURNAMENT_ID/participants/$PARTICIPANT_ID/status" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"status": "confirmed"}' > /dev/null
done

echo "8 participants registered and confirmed"
echo ""

# ==================== MATCH CRUD TESTS ====================

print_header "1. MATCH CRUD OPERATIONS"

# Test 1.1: Create manual match
MATCH_CREATE=$(curl -s -X POST "$BASE_URL/matches" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "tournament_id": "'$TOURNAMENT_ID'",
        "round_number": 1,
        "match_number": 1,
        "round_name": "Test Match",
        "participant_ids": ["'${PARTICIPANT_IDS[0]}'", "'${PARTICIPANT_IDS[1]}'"],
        "scheduled_start": "2025-06-01T10:00:00Z",
        "venue_name": "Main Stadium",
        "court_field_number": "Field 1"
    }')

MATCH_ID=$(echo $MATCH_CREATE | jq -r '.id')
if [ "$MATCH_ID" != "null" ]; then
    test_passed "Create manual match"
else
    test_failed "Create manual match" "$(echo $MATCH_CREATE | jq -r '.detail')"
fi

# Test 1.2: Get match by ID
MATCH_GET=$(curl -s -X GET "$BASE_URL/matches/$MATCH_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

MATCH_STATUS=$(echo $MATCH_GET | jq -r '.status')
if [ "$MATCH_STATUS" == "scheduled" ]; then
    test_passed "Get match by ID"
else
    test_failed "Get match by ID" "Expected status 'scheduled', got '$MATCH_STATUS'"
fi

# Test 1.3: Update match
MATCH_UPDATE=$(curl -s -X PUT "$BASE_URL/matches/$MATCH_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "venue_name": "Updated Stadium",
        "court_field_number": "Field 2",
        "notes": "Test match update"
    }')

UPDATED_VENUE=$(echo $MATCH_UPDATE | jq -r '.venue_name')
if [ "$UPDATED_VENUE" == "Updated Stadium" ]; then
    test_passed "Update match details"
else
    test_failed "Update match details" "Venue not updated"
fi

# Test 1.4: List tournament matches
MATCHES_LIST=$(curl -s -X GET "$BASE_URL/matches?tournament_id=$TOURNAMENT_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

MATCHES_COUNT=$(echo $MATCHES_LIST | jq '. | length')
if [ "$MATCHES_COUNT" -ge 1 ]; then
    test_passed "List tournament matches (count: $MATCHES_COUNT)"
else
    test_failed "List tournament matches" "No matches found"
fi

# ==================== KNOCKOUT BRACKET GENERATION ====================

print_header "2. KNOCKOUT BRACKET GENERATION"

# Test 2.1: Generate knockout bracket
BRACKET_GEN=$(curl -s -X POST "$BASE_URL/matches/generate/knockout" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "tournament_id": "'$TOURNAMENT_ID'",
        "shuffle_seeds": false
    }')

BRACKET_MATCHES_COUNT=$(echo $BRACKET_GEN | jq '. | length')
if [ "$BRACKET_MATCHES_COUNT" -ge 7 ]; then
    # 8 teams = 4 + 2 + 1 = 7 matches minimum
    test_passed "Generate knockout bracket ($BRACKET_MATCHES_COUNT matches)"
else
    test_failed "Generate knockout bracket" "Expected at least 7 matches, got $BRACKET_MATCHES_COUNT"
fi

# Test 2.2: Verify round structure
FINAL_MATCH=$(echo $BRACKET_GEN | jq '.[] | select(.round_name == "Final")')
if [ -n "$FINAL_MATCH" ]; then
    test_passed "Bracket includes Final round"
else
    test_failed "Bracket includes Final round" "No Final match found"
fi

SEMIFINAL_MATCHES=$(echo $BRACKET_GEN | jq '[.[] | select(.round_name == "Semifinal")] | length')
if [ "$SEMIFINAL_MATCHES" == "2" ]; then
    test_passed "Bracket includes 2 Semifinal matches"
else
    test_failed "Bracket includes 2 Semifinal matches" "Found $SEMIFINAL_MATCHES"
fi

# ==================== ROUND-ROBIN GENERATION ====================

print_header "3. ROUND-ROBIN GENERATION"

# Create round-robin tournament
RR_TOURNAMENT=$(curl -s -X POST "$BASE_URL/tournaments" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "club_id": "'$CLUB_ID'",
        "name": "Round Robin Test Tournament",
        "sport_type": "football",
        "tournament_type": "round_robin",
        "start_date": "2025-07-01T10:00:00Z",
        "end_date": "2025-07-15T18:00:00Z",
        "max_participants": 4,
        "participant_type": "team"
    }')

RR_TOURNAMENT_ID=$(echo $RR_TOURNAMENT | jq -r '.id')

# Register 4 participants
for i in {1..4}; do
    PART=$(curl -s -X POST "$BASE_URL/tournaments/$RR_TOURNAMENT_ID/participants" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "participant_club_id": "'$CLUB_ID'",
            "participant_name": "RR Team '$i'",
            "display_name": "RR'$i'"
        }')
    
    PART_ID=$(echo $PART | jq -r '.id')
    curl -s -X PUT "$BASE_URL/tournaments/$RR_TOURNAMENT_ID/participants/$PART_ID/status" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"status": "confirmed"}' > /dev/null
done

# Test 3.1: Generate round-robin schedule
RR_SCHEDULE=$(curl -s -X POST "$BASE_URL/matches/generate/round-robin" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "tournament_id": "'$RR_TOURNAMENT_ID'",
        "home_and_away": false
    }')

RR_MATCHES_COUNT=$(echo $RR_SCHEDULE | jq '. | length')
# 4 teams = 6 matches (C(4,2) = 6)
if [ "$RR_MATCHES_COUNT" == "6" ]; then
    test_passed "Generate round-robin schedule (6 matches for 4 teams)"
else
    test_failed "Generate round-robin schedule" "Expected 6 matches, got $RR_MATCHES_COUNT"
fi

# Test 3.2: Verify everyone plays everyone
RR_FIRST_MATCH=$(echo $RR_SCHEDULE | jq -r '.[0].id')

# ==================== MATCH SCORING ====================

print_header "4. MATCH SCORING"

# Get first match from round-robin for scoring test
SCORING_MATCH_ID=$RR_FIRST_MATCH

# Get match participants
SCORING_MATCH=$(curl -s -X GET "$BASE_URL/matches/$SCORING_MATCH_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

PART1_ID=$(echo $SCORING_MATCH | jq -r '.participants[0].participant_id')
PART2_ID=$(echo $SCORING_MATCH | jq -r '.participants[1].participant_id')

# Test 4.1: Update match score
SCORE_UPDATE=$(curl -s -X PUT "$BASE_URL/matches/$SCORING_MATCH_ID/score" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "participant_scores": [
            {
                "participant_id": "'$PART1_ID'",
                "score_value": 3,
                "is_winner": true
            },
            {
                "participant_id": "'$PART2_ID'",
                "score_value": 1,
                "is_winner": false
            }
        ],
        "score_data": {
            "final_score": {"home": 3, "away": 1},
            "halftime": {"home": 2, "away": 0}
        },
        "winner_participant_id": "'$PART1_ID'"
    }')

WINNER_ID=$(echo $SCORE_UPDATE | jq -r '.winner_participant_id')
if [ "$WINNER_ID" == "$PART1_ID" ]; then
    test_passed "Update match score with winner"
else
    test_failed "Update match score" "Winner not set correctly"
fi

# Test 4.2: Verify match status changed to completed
MATCH_FINISHED=$(echo $SCORE_UPDATE | jq -r '.is_finished')
if [ "$MATCH_FINISHED" == "true" ]; then
    test_passed "Match marked as finished after scoring"
else
    test_failed "Match marked as finished" "is_finished is $MATCH_FINISHED"
fi

# ==================== MATCH STATUS UPDATES ====================

print_header "5. MATCH STATUS UPDATES"

# Get a scheduled match
SCHEDULED_MATCHES=$(curl -s -X GET "$BASE_URL/matches?tournament_id=$RR_TOURNAMENT_ID&status=scheduled" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

STATUS_MATCH_ID=$(echo $SCHEDULED_MATCHES | jq -r '.[0].id')

# Test 5.1: Set match to in_progress
STATUS_UPDATE=$(curl -s -X PUT "$BASE_URL/matches/$STATUS_MATCH_ID/status" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "status": "in_progress",
        "notes": "Match started"
    }')

NEW_STATUS=$(echo $STATUS_UPDATE | jq -r '.status')
if [ "$NEW_STATUS" == "in_progress" ]; then
    test_passed "Set match status to in_progress"
else
    test_failed "Set match status" "Expected 'in_progress', got '$NEW_STATUS'"
fi

# Test 5.2: Verify actual_start is set
ACTUAL_START=$(echo $STATUS_UPDATE | jq -r '.actual_start')
if [ "$ACTUAL_START" != "null" ]; then
    test_passed "actual_start timestamp set"
else
    test_failed "actual_start timestamp" "actual_start is null"
fi

# ==================== TOURNAMENT STANDINGS ====================

print_header "6. TOURNAMENT STANDINGS"

# Test 6.1: Get standings
STANDINGS=$(curl -s -X GET "$BASE_URL/matches/standings/$RR_TOURNAMENT_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

STANDINGS_COUNT=$(echo $STANDINGS | jq '. | length')
if [ "$STANDINGS_COUNT" -ge 2 ]; then
    test_passed "Get tournament standings (count: $STANDINGS_COUNT)"
else
    test_failed "Get tournament standings" "Found $STANDINGS_COUNT standings"
fi

# Test 6.2: Verify winner has correct points
WINNER_STANDINGS=$(echo $STANDINGS | jq ".[] | select(.participant_id == \"$PART1_ID\")")
WINNER_POINTS=$(echo $WINNER_STANDINGS | jq -r '.points')
if [ "$WINNER_POINTS" == "3" ]; then
    test_passed "Winner has 3 points in standings"
else
    test_failed "Winner points" "Expected 3 points, got $WINNER_POINTS"
fi

# Test 6.3: Recalculate standings
RECALC_STANDINGS=$(curl -s -X POST "$BASE_URL/matches/standings/$RR_TOURNAMENT_ID/recalculate" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

RECALC_COUNT=$(echo $RECALC_STANDINGS | jq '. | length')
if [ "$RECALC_COUNT" -ge 2 ]; then
    test_passed "Recalculate standings"
else
    test_failed "Recalculate standings" "Failed to recalculate"
fi

# ==================== FILTERING & QUERIES ====================

print_header "7. FILTERING & QUERIES"

# Test 7.1: Filter matches by round
ROUND_1_MATCHES=$(curl -s -X GET "$BASE_URL/matches?tournament_id=$TOURNAMENT_ID&round_number=1" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

ROUND_1_COUNT=$(echo $ROUND_1_MATCHES | jq '. | length')
if [ "$ROUND_1_COUNT" -ge 1 ]; then
    test_passed "Filter matches by round number"
else
    test_failed "Filter by round" "No round 1 matches found"
fi

# Test 7.2: Filter matches by status
SCHEDULED_COUNT=$(curl -s -X GET "$BASE_URL/matches?tournament_id=$RR_TOURNAMENT_ID&status=scheduled" \
    -H "Authorization: Bearer $ACCESS_TOKEN" | jq '. | length')

if [ "$SCHEDULED_COUNT" -ge 1 ]; then
    test_passed "Filter matches by status"
else
    test_failed "Filter by status" "No scheduled matches found"
fi

# ==================== CLEANUP ====================

print_header "CLEANUP"

# Delete test matches (optional - CASCADE will handle this)
# Delete tournaments (this will cascade delete all matches)
curl -s -X DELETE "$BASE_URL/tournaments/$TOURNAMENT_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

curl -s -X DELETE "$BASE_URL/tournaments/$RR_TOURNAMENT_ID" \
    -H "Authorization: Bearer $ACCESS_TOKEN" > /dev/null

echo "Test data cleaned up"

# ==================== SUMMARY ====================

print_summary

# Exit with appropriate code
if [ $TESTS_FAILED -gt 0 ]; then
    exit 1
else
    exit 0
fi
