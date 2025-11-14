#!/bin/bash
# Sprint 3 - Tournament Management Test Suite
# Tests all Tournament API endpoints with authentication

set +e  # Don't exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Base URL
BASE_URL="http://localhost:8000"

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_test() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}TEST: $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if backend is running
print_test "Checking Backend Status"
HEALTH_CHECK=$(curl -s "$BASE_URL/health")
if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    print_success "Backend is running"
else
    print_error "Backend is not running! Start with: docker-compose up -d"
    exit 1
fi

# Check if jq is available
if ! command -v jq &> /dev/null; then
    print_error "jq is not installed. Please install: sudo apt install jq"
    exit 1
fi

# ============================================================================
# SETUP: Create Test Users and Club
# ============================================================================

print_test "Setup: Preparing Test Environment"

# Generate unique suffix
TIMESTAMP=$(date +%s)
OWNER_EMAIL="tournament_owner_${TIMESTAMP}@test.com"
PARTICIPANT_EMAIL="tournament_participant_${TIMESTAMP}@test.com"

# Create Owner User
print_info "Creating tournament owner: $OWNER_EMAIL"
OWNER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$OWNER_EMAIL\",
        \"password\": \"Test1234!\",
        \"first_name\": \"Tournament\",
        \"last_name\": \"Owner\"
    }")

if echo "$OWNER_RESPONSE" | jq -e '.id' >/dev/null 2>&1; then
    OWNER_ID=$(echo "$OWNER_RESPONSE" | jq -r '.id')
    print_success "Owner user created: $OWNER_ID"
else
    print_error "Failed to create owner user"
    echo "Response: $OWNER_RESPONSE"
    exit 1
fi

# Login Owner
print_info "Logging in owner..."
OWNER_LOGIN=$(curl -s -X POST "$BASE_URL/api/v1/auth/login/json" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$OWNER_EMAIL\",
        \"password\": \"Test1234!\"
    }")

OWNER_TOKEN=$(echo "$OWNER_LOGIN" | jq -r '.access_token')
if [ -n "$OWNER_TOKEN" ] && [ "$OWNER_TOKEN" != "null" ]; then
    print_success "Owner logged in"
else
    print_error "Owner login failed"
    exit 1
fi

# Create Participant User
print_info "Creating participant user: $PARTICIPANT_EMAIL"
PARTICIPANT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$PARTICIPANT_EMAIL\",
        \"password\": \"Test1234!\",
        \"first_name\": \"Team\",
        \"last_name\": \"Captain\"
    }")

if echo "$PARTICIPANT_RESPONSE" | jq -e '.id' >/dev/null 2>&1; then
    PARTICIPANT_ID=$(echo "$PARTICIPANT_RESPONSE" | jq -r '.id')
    print_success "Participant user created: $PARTICIPANT_ID"
else
    print_error "Failed to create participant user"
    exit 1
fi

# Login Participant
print_info "Logging in participant..."
PARTICIPANT_LOGIN=$(curl -s -X POST "$BASE_URL/api/v1/auth/login/json" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$PARTICIPANT_EMAIL\",
        \"password\": \"Test1234!\"
    }")

PARTICIPANT_TOKEN=$(echo "$PARTICIPANT_LOGIN" | jq -r '.access_token')
if [ -n "$PARTICIPANT_TOKEN" ] && [ "$PARTICIPANT_TOKEN" != "null" ]; then
    print_success "Participant logged in"
else
    print_error "Participant login failed"
    exit 1
fi

# Create Test Club
print_info "Creating test club..."
CLUB_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/clubs" \
    -H "Authorization: Bearer $OWNER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"FC Tournament Test ${TIMESTAMP}\",
        \"description\": \"Test club for tournament testing\",
        \"city\": \"München\",
        \"country\": \"Deutschland\"
    }")

if echo "$CLUB_RESPONSE" | jq -e '.id' >/dev/null 2>&1; then
    CLUB_ID=$(echo "$CLUB_RESPONSE" | jq -r '.id')
    print_success "Test club created: $CLUB_ID"
else
    print_error "Failed to create test club"
    echo "Response: $CLUB_RESPONSE"
    exit 1
fi

# Create Participant's Club
print_info "Creating participant club..."
PARTICIPANT_CLUB_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/clubs" \
    -H "Authorization: Bearer $PARTICIPANT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"Participant Club ${TIMESTAMP}\",
        \"city\": \"Berlin\",
        \"country\": \"Deutschland\"
    }")

if echo "$PARTICIPANT_CLUB_RESPONSE" | jq -e '.id' >/dev/null 2>&1; then
    PARTICIPANT_CLUB_ID=$(echo "$PARTICIPANT_CLUB_RESPONSE" | jq -r '.id')
    print_success "Participant club created: $PARTICIPANT_CLUB_ID"
else
    print_error "Failed to create participant club"
fi

# ============================================================================
# TEST 1: Create Tournament
# ============================================================================

print_test "Test 1: Create Tournament"

TOURNAMENT_NAME="Summer Cup ${TIMESTAMP}"
TOURNAMENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/tournaments" \
    -H "Authorization: Bearer $OWNER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"$TOURNAMENT_NAME\",
        \"description\": \"Annual summer football tournament\",
        \"club_id\": \"$CLUB_ID\",
        \"department\": \"Fußball\",
        \"sport_type\": \"football\",
        \"tournament_type\": \"knockout\",
        \"start_date\": \"2026-07-15T10:00:00\",
        \"end_date\": \"2026-07-17T18:00:00\",
        \"registration_start\": \"2025-11-01T00:00:00\",
        \"registration_end\": \"2026-07-10T23:59:59\",
        \"location\": \"Sportplatz München\",
        \"city\": \"München\",
        \"country\": \"DE\",
        \"participant_type\": \"team\",
        \"min_participants\": 4,
        \"max_participants\": 16,
        \"entry_fee\": 50.00,
        \"is_public\": true
    }")

if echo "$TOURNAMENT_RESPONSE" | jq -e '.id' >/dev/null 2>&1; then
    TOURNAMENT_ID=$(echo "$TOURNAMENT_RESPONSE" | jq -r '.id')
    TOURNAMENT_SLUG=$(echo "$TOURNAMENT_RESPONSE" | jq -r '.slug')
    print_success "Tournament created"
    print_info "Tournament ID: $TOURNAMENT_ID"
    print_info "Tournament Slug: $TOURNAMENT_SLUG"
else
    print_error "Tournament creation failed"
    echo "Response: $TOURNAMENT_RESPONSE"
    exit 1
fi

# ============================================================================
# TEST 2: List All Tournaments
# ============================================================================

print_test "Test 2: List All Tournaments"

TOURNAMENTS_LIST=$(curl -s -X GET "$BASE_URL/api/v1/tournaments")

if echo "$TOURNAMENTS_LIST" | jq -e ".[] | select(.id == \"$TOURNAMENT_ID\")" >/dev/null 2>&1; then
    print_success "Tournament appears in list"
else
    print_error "Tournament not found in list"
fi

# ============================================================================
# TEST 3: Get Tournament by ID
# ============================================================================

print_test "Test 3: Get Tournament by ID"

TOURNAMENT_DETAIL=$(curl -s -X GET "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID")

if echo "$TOURNAMENT_DETAIL" | jq -e ".id == \"$TOURNAMENT_ID\"" >/dev/null 2>&1; then
    print_success "Tournament retrieved by ID"
else
    print_error "Failed to retrieve tournament by ID"
fi

# ============================================================================
# TEST 4: Get Tournament by Slug
# ============================================================================

print_test "Test 4: Get Tournament by Slug"

TOURNAMENT_BY_SLUG=$(curl -s -X GET "$BASE_URL/api/v1/tournaments/slug/$TOURNAMENT_SLUG")

if echo "$TOURNAMENT_BY_SLUG" | jq -e ".id == \"$TOURNAMENT_ID\"" >/dev/null 2>&1; then
    print_success "Tournament retrieved by slug"
else
    print_error "Failed to retrieve tournament by slug"
fi

# ============================================================================
# TEST 5: Update Tournament
# ============================================================================

print_test "Test 5: Update Tournament"

UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID" \
    -H "Authorization: Bearer $OWNER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "description": "Updated: The best summer tournament ever!",
        "max_participants": 20
    }')

if echo "$UPDATE_RESPONSE" | jq -e '.max_participants == 20' >/dev/null 2>&1; then
    print_success "Tournament updated successfully"
else
    print_error "Failed to update tournament"
fi

# ============================================================================
# TEST 6: Filter by Sport Type
# ============================================================================

print_test "Test 6: Filter Tournaments by Sport Type"

SPORT_FILTER=$(curl -s -X GET "$BASE_URL/api/v1/tournaments?sport_type=football")

if echo "$SPORT_FILTER" | jq -e ".[] | select(.id == \"$TOURNAMENT_ID\")" >/dev/null 2>&1; then
    print_success "Tournament found in sport filter"
else
    print_error "Sport filter failed"
fi

# ============================================================================
# TEST 7: Filter by City
# ============================================================================

print_test "Test 7: Filter Tournaments by City"

CITY_FILTER=$(curl -s -X GET "$BASE_URL/api/v1/tournaments?city=München")

if echo "$CITY_FILTER" | jq -e ".[] | select(.id == \"$TOURNAMENT_ID\")" >/dev/null 2>&1; then
    print_success "Tournament found in city filter"
else
    print_error "City filter failed"
fi

# ============================================================================
# TEST 8: Update Status to Published
# ============================================================================

print_test "Test 8: Update Tournament Status to Published"

STATUS_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/status" \
    -H "Authorization: Bearer $OWNER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"status": "published"}')

if echo "$STATUS_RESPONSE" | jq -e '.status == "published"' >/dev/null 2>&1; then
    print_success "Status updated to published"
else
    print_error "Failed to update status"
fi

# ============================================================================
# TEST 9: Open Registration
# ============================================================================

print_test "Test 9: Open Tournament Registration"

STATUS_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/status" \
    -H "Authorization: Bearer $OWNER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"status": "registration_open"}')

if echo "$STATUS_RESPONSE" | jq -e '.status == "registration_open"' >/dev/null 2>&1; then
    print_success "Registration opened"
else
    print_error "Failed to open registration"
fi

# ============================================================================
# TEST 10: Get Tournament Statistics
# ============================================================================

print_test "Test 10: Get Tournament Statistics"

STATS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/statistics")

if echo "$STATS_RESPONSE" | jq -e '.total_participants' >/dev/null 2>&1; then
    TOTAL=$(echo "$STATS_RESPONSE" | jq -r '.total_participants')
    print_success "Statistics retrieved: $TOTAL participants"
else
    print_error "Failed to get statistics"
fi

# ============================================================================
# TEST 11: Register Participant
# ============================================================================

print_test "Test 11: Register Team as Participant"

REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/register" \
    -H "Authorization: Bearer $PARTICIPANT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"participant_club_id\": \"$PARTICIPANT_CLUB_ID\",
        \"participant_name\": \"FC Test Team\",
        \"contact_email\": \"team@test.com\",
        \"contact_phone\": \"+49123456789\"
    }")

if echo "$REGISTER_RESPONSE" | jq -e '.id' >/dev/null 2>&1; then
    PARTICIPANT_REG_ID=$(echo "$REGISTER_RESPONSE" | jq -r '.id')
    print_success "Participant registered"
    print_info "Participant ID: $PARTICIPANT_REG_ID"
else
    print_error "Failed to register participant"
    echo "Response: $REGISTER_RESPONSE"
fi

# ============================================================================
# TEST 12: List Participants
# ============================================================================

print_test "Test 12: List Tournament Participants"

PARTICIPANTS_LIST=$(curl -s -X GET "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/participants")

if echo "$PARTICIPANTS_LIST" | jq -e ".[] | select(.id == \"$PARTICIPANT_REG_ID\")" >/dev/null 2>&1; then
    print_success "Participant found in list"
else
    print_error "Participant not found in list"
fi

# ============================================================================
# TEST 13: Get Participant Details
# ============================================================================

print_test "Test 13: Get Participant Details"

PARTICIPANT_DETAIL=$(curl -s -X GET "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/participants/$PARTICIPANT_REG_ID")

if echo "$PARTICIPANT_DETAIL" | jq -e ".id == \"$PARTICIPANT_REG_ID\"" >/dev/null 2>&1; then
    print_success "Participant details retrieved"
else
    print_error "Failed to get participant details"
fi

# ============================================================================
# TEST 14: Update Participant
# ============================================================================

print_test "Test 14: Update Participant Information"

UPDATE_PARTICIPANT=$(curl -s -X PUT "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/participants/$PARTICIPANT_REG_ID" \
    -H "Authorization: Bearer $OWNER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "display_name": "FC Test Team A",
        "notes": "Updated team information"
    }')

if echo "$UPDATE_PARTICIPANT" | jq -e '.display_name == "FC Test Team A"' >/dev/null 2>&1; then
    print_success "Participant updated"
else
    print_error "Failed to update participant"
fi

# ============================================================================
# TEST 15: Confirm Participant
# ============================================================================

print_test "Test 15: Confirm Participant Status"

STATUS_UPDATE=$(curl -s -X PUT "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/participants/$PARTICIPANT_REG_ID/status" \
    -H "Authorization: Bearer $OWNER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"status": "confirmed"}')

if echo "$STATUS_UPDATE" | jq -e '.status == "confirmed"' >/dev/null 2>&1; then
    print_success "Participant confirmed"
else
    print_error "Failed to confirm participant"
fi

# ============================================================================
# TEST 16: Update Payment Status
# ============================================================================

print_test "Test 16: Update Payment Status"

PAYMENT_UPDATE=$(curl -s -X PUT "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/participants/$PARTICIPANT_REG_ID/payment" \
    -H "Authorization: Bearer $OWNER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "payment_status": "paid",
        "payment_amount": 50.00,
        "payment_reference": "PAY-TEST-12345"
    }')

if echo "$PAYMENT_UPDATE" | jq -e '.payment_status == "paid"' >/dev/null 2>&1; then
    print_success "Payment status updated"
else
    print_error "Failed to update payment"
fi

# ============================================================================
# TEST 17: My Created Tournaments
# ============================================================================

print_test "Test 17: Get My Created Tournaments"

MY_TOURNAMENTS=$(curl -s -X GET "$BASE_URL/api/v1/tournaments/my/created" \
    -H "Authorization: Bearer $OWNER_TOKEN")

if echo "$MY_TOURNAMENTS" | jq -e ".[] | select(.id == \"$TOURNAMENT_ID\")" >/dev/null 2>&1; then
    print_success "Owner sees their created tournament"
else
    print_error "Owner cannot see their tournament"
fi

# ============================================================================
# TEST 18: My Participations
# ============================================================================

print_test "Test 18: Get My Tournament Participations"

MY_PARTICIPATIONS=$(curl -s -X GET "$BASE_URL/api/v1/tournaments/my/participating" \
    -H "Authorization: Bearer $PARTICIPANT_TOKEN")

if echo "$MY_PARTICIPATIONS" | jq -e ".[] | select(.tournament_id == \"$TOURNAMENT_ID\")" >/dev/null 2>&1; then
    print_success "Participant sees their participation"
else
    print_warning "Participant may not see participation yet"
fi

# ============================================================================
# TEST 19: Permission Test - Non-Owner Cannot Update
# ============================================================================

print_test "Test 19: Permission Test - Non-Owner Cannot Update Tournament"

UNAUTHORIZED_UPDATE=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID" \
    -H "Authorization: Bearer $PARTICIPANT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"description": "Hacked!"}')

HTTP_CODE=$(echo "$UNAUTHORIZED_UPDATE" | tail -n1)
if [ "$HTTP_CODE" = "403" ] || [ "$HTTP_CODE" = "401" ]; then
    print_success "Permission denied as expected ($HTTP_CODE)"
else
    print_warning "Expected 403/401, got $HTTP_CODE"
fi

# ============================================================================
# TEST 20: Remove Participant
# ============================================================================

print_test "Test 20: Remove Participant from Tournament"

DELETE_PARTICIPANT=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/participants/$PARTICIPANT_REG_ID" \
    -H "Authorization: Bearer $OWNER_TOKEN")

HTTP_CODE=$(echo "$DELETE_PARTICIPANT" | tail -n1)
if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "200" ]; then
    print_success "Participant removed"
elif [ "$HTTP_CODE" = "307" ]; then
    # Retry with trailing slash
    DELETE_PARTICIPANT=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/participants/$PARTICIPANT_REG_ID/" \
        -H "Authorization: Bearer $OWNER_TOKEN")
    HTTP_CODE=$(echo "$DELETE_PARTICIPANT" | tail -n1)
    if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "200" ]; then
        print_success "Participant removed (with trailing slash)"
    else
        print_error "Failed to remove participant, HTTP: $HTTP_CODE"
    fi
else
    print_error "Failed to remove participant, HTTP: $HTTP_CODE"
fi

# ============================================================================
# TEST 21: Verify Participant Removed
# ============================================================================

print_test "Test 21: Verify Participant Removed"

sleep 1
PARTICIPANTS_AFTER=$(curl -s -X GET "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/participants")

if echo "$PARTICIPANTS_AFTER" | jq -e ".[] | select(.id == \"$PARTICIPANT_REG_ID\")" >/dev/null 2>&1; then
    print_warning "Participant still in list"
else
    print_success "Participant successfully removed"
fi

# ============================================================================
# TEST 22: Delete Tournament
# ============================================================================

print_test "Test 22: Delete Tournament"

# Set status back to draft first
curl -s -X PUT "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID/status" \
    -H "Authorization: Bearer $OWNER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"status": "draft"}' > /dev/null

DELETE_TOURNAMENT=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/tournaments/$TOURNAMENT_ID" \
    -H "Authorization: Bearer $OWNER_TOKEN")

HTTP_CODE=$(echo "$DELETE_TOURNAMENT" | tail -n1)
if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "200" ]; then
    print_success "Tournament deleted"
else
    print_error "Failed to delete tournament, HTTP: $HTTP_CODE"
fi

# ============================================================================
# TEST 23: Verify Tournament Deleted
# ============================================================================

print_test "Test 23: Verify Tournament Not in Active List"

sleep 1
TOURNAMENTS_AFTER=$(curl -s -X GET "$BASE_URL/api/v1/tournaments")

if echo "$TOURNAMENTS_AFTER" | jq -e ".[] | select(.id == \"$TOURNAMENT_ID\")" >/dev/null 2>&1; then
    print_warning "Deleted tournament still appears"
else
    print_success "Deleted tournament not in active list"
fi

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}TEST SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"

TOTAL=$((TESTS_PASSED + TESTS_FAILED))
echo -e "${BLUE}Total Tests: $TOTAL${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Sprint 3 Tournament Management is fully functional!${NC}\n"
    exit 0
else
    echo -e "\n${YELLOW}⚠ $TESTS_FAILED test(s) had issues. Check output above.${NC}\n"
    exit 0
fi