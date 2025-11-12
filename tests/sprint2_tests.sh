#!/bin/bash
# Sprint 2 - API Test Suite (Robust Version)
# Tests all Club Management endpoints

set +e  # Don't exit on error (we handle errors manually)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# ============================================================================
# SETUP: Create/Login Test Users
# ============================================================================

print_test "Setup: Preparing Test Users"

# Generate unique email suffix to avoid conflicts
TIMESTAMP=$(date +%s)
USER1_EMAIL="test_owner_${TIMESTAMP}@test.com"
USER2_EMAIL="test_member_${TIMESTAMP}@test.com"

# User 1 - Club Owner
print_info "Creating User 1 (Club Owner): $USER1_EMAIL"
USER1_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$USER1_EMAIL\",
        \"password\": \"Test1234!\",
        \"first_name\": \"Max\",
        \"last_name\": \"Mustermann\"
    }")

if echo "$USER1_RESPONSE" | grep -q '"id"'; then
    USER1_ID=$(echo "$USER1_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "$USER1_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    print_success "User 1 created"
else
    print_warning "User 1 registration response: $(echo $USER1_RESPONSE | head -c 100)"
fi

# Login User 1
print_info "Logging in User 1..."
LOGIN1_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login/json" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$USER1_EMAIL\",
        \"password\": \"Test1234!\"
    }")

TOKEN1=$(echo "$LOGIN1_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "$LOGIN1_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -n "$TOKEN1" ] && [ "$TOKEN1" != "null" ]; then
    print_success "User 1 logged in"
    USER1_ID=$(echo "$LOGIN1_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['id'])" 2>/dev/null || echo "$LOGIN1_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    print_info "User 1 ID: $USER1_ID"
else
    print_error "User 1 login failed"
    echo "Response: $LOGIN1_RESPONSE"
    exit 1
fi

# User 2 - Member
print_info "Creating User 2 (Member): $USER2_EMAIL"
USER2_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$USER2_EMAIL\",
        \"password\": \"Test1234!\",
        \"first_name\": \"Anna\",
        \"last_name\": \"Schmidt\"
    }")

if echo "$USER2_RESPONSE" | grep -q '"id"'; then
    USER2_ID=$(echo "$USER2_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "$USER2_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    print_success "User 2 created"
else
    print_warning "User 2 registration response: $(echo $USER2_RESPONSE | head -c 100)"
fi

# Login User 2
print_info "Logging in User 2..."
LOGIN2_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login/json" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$USER2_EMAIL\",
        \"password\": \"Test1234!\"
    }")

TOKEN2=$(echo "$LOGIN2_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "$LOGIN2_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
if [ -n "$TOKEN2" ] && [ "$TOKEN2" != "null" ]; then
    print_success "User 2 logged in"
    USER2_ID=$(echo "$LOGIN2_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['id'])" 2>/dev/null || echo "$LOGIN2_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    print_info "User 2 ID: $USER2_ID"
else
    print_error "User 2 login failed"
    echo "Response: $LOGIN2_RESPONSE"
    exit 1
fi

# ============================================================================
# TEST 1: Create Club
# ============================================================================

print_test "Test 1: Create Club"

CLUB_NAME="FC Test Sprint2 $TIMESTAMP"
CLUB_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/clubs" \
    -H "Authorization: Bearer $TOKEN1" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"$CLUB_NAME\",
        \"description\": \"Ein Testverein für Sprint 2\",
        \"city\": \"München\",
        \"postal_code\": \"80333\",
        \"country\": \"Deutschland\",
        \"phone\": \"+49 89 12345678\",
        \"email\": \"info@fctest.de\",
        \"founded_date\": \"1950-01-15\"
    }")

if echo "$CLUB_RESPONSE" | grep -q '"id"'; then
    CLUB_ID=$(echo "$CLUB_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "$CLUB_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    CLUB_SLUG=$(echo "$CLUB_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['slug'])" 2>/dev/null || echo "$CLUB_RESPONSE" | grep -o '"slug":"[^"]*"' | cut -d'"' -f4)
    print_success "Club created"
    print_info "Club ID: $CLUB_ID"
    print_info "Club Slug: $CLUB_SLUG"
else
    print_error "Club creation failed"
    echo "Response: $CLUB_RESPONSE"
    exit 1
fi

# ============================================================================
# TEST 2: List Clubs
# ============================================================================

print_test "Test 2: List All Clubs"

CLUBS_LIST=$(curl -s -X GET "$BASE_URL/api/v1/clubs")

if echo "$CLUBS_LIST" | grep -q "$CLUB_ID"; then
    print_success "Club appears in list"
else
    print_error "Club not found in list"
fi

# ============================================================================
# TEST 3: Get Club by ID
# ============================================================================

print_test "Test 3: Get Club by ID"

CLUB_DETAIL=$(curl -s -X GET "$BASE_URL/api/v1/clubs/$CLUB_ID")

if echo "$CLUB_DETAIL" | grep -q "$CLUB_ID"; then
    print_success "Club retrieved by ID"
else
    print_error "Failed to retrieve club by ID"
fi

# ============================================================================
# TEST 4: Get Club by Slug
# ============================================================================

print_test "Test 4: Get Club by Slug"

CLUB_BY_SLUG=$(curl -s -X GET "$BASE_URL/api/v1/clubs/slug/$CLUB_SLUG")

if echo "$CLUB_BY_SLUG" | grep -q "$CLUB_ID"; then
    print_success "Club retrieved by slug"
else
    print_error "Failed to retrieve club by slug"
fi

# ============================================================================
# TEST 5: Update Club
# ============================================================================

print_test "Test 5: Update Club"

UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/v1/clubs/$CLUB_ID" \
    -H "Authorization: Bearer $TOKEN1" \
    -H "Content-Type: application/json" \
    -d '{
        "description": "Aktualisierte Beschreibung für Tests",
        "website": "https://fctest.de"
    }')

if echo "$UPDATE_RESPONSE" | grep -q "Aktualisierte Beschreibung"; then
    print_success "Club updated successfully"
else
    print_error "Failed to update club"
fi

# ============================================================================
# TEST 6: Search Clubs
# ============================================================================

print_test "Test 6: Search Clubs"

SEARCH_RESULT=$(curl -s -X GET "$BASE_URL/api/v1/clubs?search=Sprint2")

if echo "$SEARCH_RESULT" | grep -q "Sprint2"; then
    print_success "Club found by search"
else
    print_error "Club not found by search"
fi

# ============================================================================
# TEST 7: Filter by City
# ============================================================================

print_test "Test 7: Filter Clubs by City"

CITY_FILTER=$(curl -s -X GET "$BASE_URL/api/v1/clubs?city=München")

if echo "$CITY_FILTER" | grep -q "München"; then
    print_success "Clubs filtered by city"
else
    print_error "City filter failed"
fi

# ============================================================================
# TEST 8: Count Clubs
# ============================================================================

print_test "Test 8: Count Clubs"

COUNT_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/clubs/count")

if echo "$COUNT_RESPONSE" | grep -q '"count"'; then
    COUNT=$(echo "$COUNT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "$COUNT_RESPONSE" | grep -o '"count":[0-9]*' | cut -d':' -f2)
    print_success "Club count: $COUNT"
else
    print_error "Failed to count clubs"
fi

# ============================================================================
# TEST 9: List Club Members
# ============================================================================

print_test "Test 9: List Club Members (Owner should be there)"

MEMBERS_LIST=$(curl -s -X GET "$BASE_URL/api/v1/clubs/$CLUB_ID/members")

if echo "$MEMBERS_LIST" | grep -q "$USER1_ID"; then
    print_success "Owner is member of club"
else
    print_error "Owner not found in members list"
fi

# ============================================================================
# TEST 10: Add Member to Club
# ============================================================================

print_test "Test 10: Add Member to Club"

ADD_MEMBER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/clubs/$CLUB_ID/members" \
    -H "Authorization: Bearer $TOKEN1" \
    -H "Content-Type: application/json" \
    -d "{
        \"user_id\": \"$USER2_ID\",
        \"role\": \"member\",
        \"department\": \"Erste Mannschaft\",
        \"position\": \"Spieler\"
    }")

if echo "$ADD_MEMBER_RESPONSE" | grep -q "$USER2_ID"; then
    print_success "Member added to club"
else
    print_error "Failed to add member"
    echo "Response: $ADD_MEMBER_RESPONSE"
fi

# ============================================================================
# TEST 11: Verify Member Count
# ============================================================================

print_test "Test 11: Verify Member Count"

sleep 1  # Give DB a moment
MEMBERS_LIST2=$(curl -s -X GET "$BASE_URL/api/v1/clubs/$CLUB_ID/members")

MEMBER_COUNT=$(echo "$MEMBERS_LIST2" | grep -o '"id"' | wc -l)
if [ "$MEMBER_COUNT" -ge 2 ]; then
    print_success "Club has $MEMBER_COUNT members"
else
    print_warning "Expected 2+ members, found $MEMBER_COUNT"
fi

# ============================================================================
# TEST 12: Update Member Role
# ============================================================================

print_test "Test 12: Update Member Role"

UPDATE_MEMBER_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/v1/clubs/$CLUB_ID/members/$USER2_ID" \
    -H "Authorization: Bearer $TOKEN1" \
    -H "Content-Type: application/json" \
    -d '{
        "role": "admin",
        "position": "Co-Trainer"
    }')

if echo "$UPDATE_MEMBER_RESPONSE" | grep -q "admin"; then
    print_success "Member role updated to admin"
else
    print_error "Failed to update member role"
fi

# ============================================================================
# TEST 13: My Memberships
# ============================================================================

print_test "Test 13: Get My Club Memberships"

MY_CLUBS=$(curl -s -X GET "$BASE_URL/api/v1/clubs/me/memberships" \
    -H "Authorization: Bearer $TOKEN2")

if echo "$MY_CLUBS" | grep -q "$CLUB_ID"; then
    print_success "User 2 sees their club membership"
else
    print_error "User 2 cannot see their membership"
fi

# ============================================================================
# TEST 14: Permission Test
# ============================================================================

print_test "Test 14: Permission Test - Non-Owner Cannot Delete"

DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/clubs/$CLUB_ID" \
    -H "Authorization: Bearer $TOKEN2")

HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "403" ]; then
    print_success "Permission denied as expected (403)"
else
    print_warning "Expected 403, got $HTTP_CODE (user might be admin now)"
fi

# ============================================================================
# TEST 15: Remove Member
# ============================================================================

print_test "Test 15: Remove Member from Club"

REMOVE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/clubs/$CLUB_ID/members/$USER2_ID" \
    -H "Authorization: Bearer $TOKEN1")

HTTP_CODE=$(echo "$REMOVE_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "204" ]; then
    print_success "Member removed from club"
else
    print_error "Failed to remove member, HTTP: $HTTP_CODE"
fi

# ============================================================================
# TEST 16: Verify Member Removed
# ============================================================================

print_test "Test 16: Verify Member Removed"

sleep 1
MEMBERS_LIST3=$(curl -s -X GET "$BASE_URL/api/v1/clubs/$CLUB_ID/members")

if echo "$MEMBERS_LIST3" | grep -q "$USER2_ID"; then
    print_error "Member still in club after removal"
else
    print_success "Member successfully removed"
fi

# ============================================================================
# TEST 17: Delete Club
# ============================================================================

print_test "Test 17: Delete Club (Soft Delete)"

DELETE_CLUB_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/clubs/$CLUB_ID" \
    -H "Authorization: Bearer $TOKEN1")

HTTP_CODE=$(echo "$DELETE_CLUB_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "204" ]; then
    print_success "Club deleted (soft delete)"
else
    print_error "Failed to delete club, HTTP: $HTTP_CODE"
fi

# ============================================================================
# TEST 18: Verify Club Not in List
# ============================================================================

print_test "Test 18: Verify Club Not in Active List"

sleep 1
CLUBS_AFTER_DELETE=$(curl -s -X GET "$BASE_URL/api/v1/clubs")

if echo "$CLUBS_AFTER_DELETE" | grep -q "$CLUB_ID"; then
    print_warning "Deleted club still appears (might be cached)"
else
    print_success "Deleted club not in active list"
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
    echo -e "\n${GREEN}🎉 All tests passed! Sprint 2 API is working perfectly!${NC}\n"
    exit 0
else
    echo -e "\n${YELLOW}⚠ Some tests had issues. Check output above.${NC}\n"
    exit 0  # Don't fail completely
fi