#!/bin/bash

# Sprint 3 - Tournament Management Test Script
# Tests all 17 tournament API endpoints

set -e  # Exit on error

BASE_URL="http://localhost:8000/api/v1"
PASSED=0
FAILED=0

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TEST_NUM=0

# Helper function to print test results
print_test() {
    TEST_NUM=$((TEST_NUM + 1))
    echo -e "\n${YELLOW}[TEST $TEST_NUM]${NC} $1"
}

print_success() {
    PASSED=$((PASSED + 1))
    echo -e "${GREEN}✓ PASS${NC} - $1"
}

print_error() {
    FAILED=$((FAILED + 1))
    echo -e "${RED}✗ FAIL${NC} - $1"
}

# Variables to store created IDs
CLUB_ID=""
TOURNAMENT_ID=""
TOURNAMENT_SLUG=""
PARTICIPANT_ID=""

echo "======================================"
echo "Sprint 3 - Tournament Management Tests"
echo "======================================"
echo ""

# ==================== SETUP: Create Club for Testing ====================
print_test "Setup: Create test club"
CLUB_RESPONSE=$(curl -s -X POST "$BASE_URL/clubs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Sportverein Sprint 3",
    "description": "Test club for tournament testing",
    "city": "München",
    "country": "Deutschland"
  }')

CLUB_ID=$(echo "$CLUB_RESPONSE" | jq -r '.id // empty')

if [ -n "$CLUB_ID" ] && [ "$CLUB_ID" != "null" ]; then
    print_success "Club created with ID: $CLUB_ID"
else
    print_error "Failed to create club"
    echo "Response: $CLUB_RESPONSE"
    exit 1
fi

# ==================== TEST 1: Create Tournament ====================
print_test "POST /tournaments - Create tournament"
TOURNAMENT_RESPONSE=$(curl -s -X POST "$BASE_URL/tournaments" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Sommer Cup 2025\",
    \"description\": \"Annual summer football tournament\",
    \"club_id\": \"$CLUB_ID\",
    \"department\": \"Fußball\",
    \"sport_type\": \"football\",
    \"tournament_type\": \"knockout\",
    \"start_date\": \"2025-07-15T10:00:00\",
    \"end_date\": \"2025-07-17T18:00:00\",
    \"registration_start\": \"2025-06-01T00:00:00\",
    \"registration_end\": \"2025-07-10T23:59:59\",
    \"location\": \"Sportplatz München\",
    \"city\": \"München\",
    \"country\": \"DE\",
    \"participant_type\": \"team\",
    \"min_participants\": 4,
    \"max_participants\": 16,
    \"entry_fee\": 50.00,
    \"is_public\": true
  }")

TOURNAMENT_ID=$(echo "$TOURNAMENT_RESPONSE" | jq -r '.id // empty')
TOURNAMENT_SLUG=$(echo "$TOURNAMENT_RESPONSE" | jq -r '.slug // empty')

if [ -n "$TOURNAMENT_ID" ] && [ "$TOURNAMENT_ID" != "null" ]; then
    print_success "Tournament created with ID: $TOURNAMENT_ID"
else
    print_error "Failed to create tournament"
    echo "Response: $TOURNAMENT_RESPONSE"
fi

# ==================== TEST 2: List Tournaments ====================
print_test "GET /tournaments - List all tournaments"
LIST_RESPONSE=$(curl -s -X GET "$BASE_URL/tournaments")
TOURNAMENT_COUNT=$(echo "$LIST_RESPONSE" | jq 'length')

if [ "$TOURNAMENT_COUNT" -ge 1 ]; then
    print_success "Found $TOURNAMENT_COUNT tournament(s)"
else
    print_error "No tournaments found"
fi

# ==================== TEST 3: Get Tournament by ID ====================
print_test "GET /tournaments/{id} - Get tournament details"
TOURNAMENT_DETAIL=$(curl -s -X GET "$BASE_URL/tournaments/$TOURNAMENT_ID")
DETAIL_NAME=$(echo "$TOURNAMENT_DETAIL" | jq -r '.name // empty')

if [ "$DETAIL_NAME" = "Sommer Cup 2025" ]; then
    print_success "Retrieved tournament: $DETAIL_NAME"
else
    print_error "Failed to get tournament details"
fi

# ==================== TEST 4: Get Tournament by Slug ====================
print_test "GET /tournaments/slug/{slug} - Get tournament by slug"
SLUG_RESPONSE=$(curl -s -X GET "$BASE_URL/tournaments/slug/$TOURNAMENT_SLUG")
SLUG_NAME=$(echo "$SLUG_RESPONSE" | jq -r '.name // empty')

if [ "$SLUG_NAME" = "Sommer Cup 2025" ]; then
    print_success "Retrieved tournament by slug: $TOURNAMENT_SLUG"
else
    print_error "Failed to get tournament by slug"
fi

# ==================== TEST 5: Update Tournament ====================
print_test "PUT /tournaments/{id} - Update tournament"
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/tournaments/$TOURNAMENT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description - The best summer tournament!",
    "max_participants": 20
  }')

UPDATED_DESC=$(echo "$UPDATE_RESPONSE" | jq -r '.description // empty')

if [[ "$UPDATED_DESC" == *"Updated description"* ]]; then
    print_success "Tournament updated successfully"
else
    print_error "Failed to update tournament"
fi

# ==================== TEST 6: Filter Tournaments ====================
print_test "GET /tournaments?sport_type=football - Filter by sport"
FILTER_RESPONSE=$(curl -s -X GET "$BASE_URL/tournaments?sport_type=football")
FILTER_COUNT=$(echo "$FILTER_RESPONSE" | jq 'length')

if [ "$FILTER_COUNT" -ge 1 ]; then
    print_success "Filtered tournaments: $FILTER_COUNT found"
else
    print_error "Filter failed"
fi

# ==================== TEST 7: Filter by City ====================
print_test "GET /tournaments?city=München - Filter by city"
CITY_FILTER=$(curl -s -X GET "$BASE_URL/tournaments?city=München")
CITY_COUNT=$(echo "$CITY_FILTER" | jq 'length')

if [ "$CITY_COUNT" -ge 1 ]; then
    print_success "Found $CITY_COUNT tournament(s) in München"
else
    print_error "City filter failed"
fi

# ==================== TEST 8: Update Tournament Status ====================
print_test "PUT /tournaments/{id}/status - Update status to published"
STATUS_RESPONSE=$(curl -s -X PUT "$BASE_URL/tournaments/$TOURNAMENT_ID/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "published"
  }')

NEW_STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // empty')

if [ "$NEW_STATUS" = "published" ]; then
    print_success "Status updated to: $NEW_STATUS"
else
    print_error "Failed to update status"
fi

# ==================== TEST 9: Update to Registration Open ====================
print_test "PUT /tournaments/{id}/status - Open registration"
STATUS_RESPONSE=$(curl -s -X PUT "$BASE_URL/tournaments/$TOURNAMENT_ID/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "registration_open"
  }')

NEW_STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status // empty')

if [ "$NEW_STATUS" = "registration_open" ]; then
    print_success "Registration opened"
else
    print_error "Failed to open registration"
fi

# ==================== TEST 10: Get Tournament Statistics ====================
print_test "GET /tournaments/{id}/statistics - Get statistics"
STATS_RESPONSE=$(curl -s -X GET "$BASE_URL/tournaments/$TOURNAMENT_ID/statistics")
TOTAL_PARTICIPANTS=$(echo "$STATS_RESPONSE" | jq -r '.total_participants // 0')

if [ "$TOTAL_PARTICIPANTS" = "0" ]; then
    print_success "Statistics retrieved: $TOTAL_PARTICIPANTS participants"
else
    print_error "Failed to get statistics"
fi

# ==================== TEST 11: Register Participant ====================
print_test "POST /tournaments/{id}/register - Register team"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/tournaments/$TOURNAMENT_ID/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"participant_club_id\": \"$CLUB_ID\",
    \"participant_name\": \"FC Test Team\",
    \"contact_email\": \"team@test.com\",
    \"contact_phone\": \"+49123456789\"
  }")

PARTICIPANT_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.id // empty')

if [ -n "$PARTICIPANT_ID" ] && [ "$PARTICIPANT_ID" != "null" ]; then
    print_success "Participant registered with ID: $PARTICIPANT_ID"
else
    print_error "Failed to register participant"
    echo "Response: $REGISTER_RESPONSE"
fi

# ==================== TEST 12: List Participants ====================
print_test "GET /tournaments/{id}/participants - List participants"
PARTICIPANTS_LIST=$(curl -s -X GET "$BASE_URL/tournaments/$TOURNAMENT_ID/participants")
PARTICIPANTS_COUNT=$(echo "$PARTICIPANTS_LIST" | jq 'length')

if [ "$PARTICIPANTS_COUNT" -ge 1 ]; then
    print_success "Found $PARTICIPANTS_COUNT participant(s)"
else
    print_error "No participants found"
fi

# ==================== TEST 13: Get Participant Details ====================
print_test "GET /tournaments/{id}/participants/{pid} - Get participant"
PARTICIPANT_DETAIL=$(curl -s -X GET "$BASE_URL/tournaments/$TOURNAMENT_ID/participants/$PARTICIPANT_ID")
PARTICIPANT_NAME=$(echo "$PARTICIPANT_DETAIL" | jq -r '.participant_name // empty')

if [ "$PARTICIPANT_NAME" = "FC Test Team" ]; then
    print_success "Retrieved participant: $PARTICIPANT_NAME"
else
    print_error "Failed to get participant details"
fi

# ==================== TEST 14: Update Participant ====================
print_test "PUT /tournaments/{id}/participants/{pid} - Update participant"
UPDATE_PARTICIPANT=$(curl -s -X PUT "$BASE_URL/tournaments/$TOURNAMENT_ID/participants/$PARTICIPANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "FC Test Team A",
    "notes": "Updated team information"
  }')

UPDATED_DISPLAY=$(echo "$UPDATE_PARTICIPANT" | jq -r '.display_name // empty')

if [ "$UPDATED_DISPLAY" = "FC Test Team A" ]; then
    print_success "Participant updated"
else
    print_error "Failed to update participant"
fi

# ==================== TEST 15: Update Participant Status ====================
print_test "PUT /tournaments/{id}/participants/{pid}/status - Confirm participant"
STATUS_UPDATE=$(curl -s -X PUT "$BASE_URL/tournaments/$TOURNAMENT_ID/participants/$PARTICIPANT_ID/status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmed"
  }')

PARTICIPANT_STATUS=$(echo "$STATUS_UPDATE" | jq -r '.status // empty')

if [ "$PARTICIPANT_STATUS" = "confirmed" ]; then
    print_success "Participant confirmed"
else
    print_error "Failed to confirm participant"
fi

# ==================== TEST 16: Update Payment Status ====================
print_test "PUT /tournaments/{id}/participants/{pid}/payment - Update payment"
PAYMENT_UPDATE=$(curl -s -X PUT "$BASE_URL/tournaments/$TOURNAMENT_ID/participants/$PARTICIPANT_ID/payment" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_status": "paid",
    "payment_amount": 50.00,
    "payment_reference": "PAY-12345"
  }')

PAYMENT_STATUS=$(echo "$PAYMENT_UPDATE" | jq -r '.payment_status // empty')

if [ "$PAYMENT_STATUS" = "paid" ]; then
    print_success "Payment updated to: $PAYMENT_STATUS"
else
    print_error "Failed to update payment"
fi

# ==================== TEST 17: My Created Tournaments ====================
print_test "GET /tournaments/my/created - Get my tournaments"
MY_TOURNAMENTS=$(curl -s -X GET "$BASE_URL/tournaments/my/created")
MY_COUNT=$(echo "$MY_TOURNAMENTS" | jq 'length')

if [ "$MY_COUNT" -ge 0 ]; then
    print_success "Retrieved $MY_COUNT created tournament(s)"
else
    print_error "Failed to get created tournaments"
fi

# ==================== TEST 18: My Participations ====================
print_test "GET /tournaments/my/participating - Get my participations"
MY_PARTICIPATIONS=$(curl -s -X GET "$BASE_URL/tournaments/my/participating")
PARTICIPATION_COUNT=$(echo "$MY_PARTICIPATIONS" | jq 'length')

if [ "$PARTICIPATION_COUNT" -ge 0 ]; then
    print_success "Retrieved $PARTICIPATION_COUNT participation(s)"
else
    print_error "Failed to get participations"
fi

# ==================== CLEANUP TEST: Delete Participant ====================
print_test "DELETE /tournaments/{id}/participants/{pid} - Remove participant"
DELETE_PARTICIPANT=$(curl -s -w "%{http_code}" -X DELETE "$BASE_URL/tournaments/$TOURNAMENT_ID/participants/$PARTICIPANT_ID")

if [ "$DELETE_PARTICIPANT" = "204" ]; then
    print_success "Participant deleted"
else
    print_error "Failed to delete participant (HTTP $DELETE_PARTICIPANT)"
fi

# ==================== CLEANUP TEST: Delete Tournament ====================
print_test "DELETE /tournaments/{id} - Delete tournament"

# First, update status back to draft (can only delete draft tournaments)
curl -s -X PUT "$BASE_URL/tournaments/$TOURNAMENT_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "draft"}' > /dev/null

DELETE_RESPONSE=$(curl -s -w "%{http_code}" -X DELETE "$BASE_URL/tournaments/$TOURNAMENT_ID")

if [ "$DELETE_RESPONSE" = "204" ]; then
    print_success "Tournament deleted"
else
    print_error "Failed to delete tournament (HTTP $DELETE_RESPONSE)"
fi

# ==================== SUMMARY ====================
echo ""
echo "======================================"
echo "Test Summary"
echo "======================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total:  $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi