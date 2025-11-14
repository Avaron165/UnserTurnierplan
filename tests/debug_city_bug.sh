#!/bin/bash
# Debug script for city filter issue

BASE_URL="http://localhost:8000"

echo "======================================"
echo "City Filter Debug"
echo "======================================"
echo ""

# Get all tournaments and their cities
echo "1. All tournaments with their cities:"
echo "--------------------------------------"
curl -s "$BASE_URL/api/v1/tournaments" | jq '.[] | {id: .id, name: .name, city: .city}' | head -50

echo ""
echo "2. Direct database check:"
echo "--------------------------------------"
docker-compose exec -T db psql -U postgres -d unserturnierplan -c "SELECT id, name, city FROM tournaments WHERE is_active = true ORDER BY created_at DESC LIMIT 5;"

echo ""
echo "3. Test different city filter variations:"
echo "--------------------------------------"

# Test 1: Exact match with umlaut
echo "Testing: city=München"
RESULT1=$(curl -s "$BASE_URL/api/v1/tournaments?city=München")
COUNT1=$(echo "$RESULT1" | jq '. | length')
echo "Results: $COUNT1"
if [ "$COUNT1" -gt 0 ]; then
    echo "$RESULT1" | jq '.[] | {name: .name, city: .city}'
fi

echo ""
echo "Testing: city=Munchen (without umlaut)"
RESULT2=$(curl -s "$BASE_URL/api/v1/tournaments?city=Munchen")
COUNT2=$(echo "$RESULT2" | jq '. | length')
echo "Results: $COUNT2"
if [ "$COUNT2" -gt 0 ]; then
    echo "$RESULT2" | jq '.[] | {name: .name, city: .city}'
fi

echo ""
echo "Testing: city=Mün (partial)"
RESULT3=$(curl -s "$BASE_URL/api/v1/tournaments?city=Mün")
COUNT3=$(echo "$RESULT3" | jq '. | length')
echo "Results: $COUNT3"
if [ "$COUNT3" -gt 0 ]; then
    echo "$RESULT3" | jq '.[] | {name: .name, city: .city}'
fi

echo ""
echo "Testing: city=mün (lowercase)"
RESULT4=$(curl -s "$BASE_URL/api/v1/tournaments?city=mün")
COUNT4=$(echo "$RESULT4" | jq '. | length')
echo "Results: $COUNT4"
if [ "$COUNT4" -gt 0 ]; then
    echo "$RESULT4" | jq '.[] | {name: .name, city: .city}'
fi

echo ""
echo "4. URL encoding test:"
echo "--------------------------------------"
# München URL-encoded: M%C3%BCnchen
echo "Testing: city=M%C3%BCnchen (URL-encoded)"
RESULT5=$(curl -s "$BASE_URL/api/v1/tournaments?city=M%C3%BCnchen")
COUNT5=$(echo "$RESULT5" | jq '. | length')
echo "Results: $COUNT5"
if [ "$COUNT5" -gt 0 ]; then
    echo "$RESULT5" | jq '.[] | {name: .name, city: .city}'
fi

echo ""
echo "5. Raw SQL comparison:"
echo "--------------------------------------"
echo "SQL: SELECT city FROM tournaments WHERE city ILIKE '%München%';"
docker-compose exec -T db psql -U postgres -d unserturnierplan -c "SELECT id, name, city FROM tournaments WHERE city ILIKE '%München%' AND is_active = true;"

echo ""
echo "SQL: SELECT city FROM tournaments WHERE city ILIKE '%Mün%';"
docker-compose exec -T db psql -U postgres -d unserturnierplan -c "SELECT id, name, city FROM tournaments WHERE city ILIKE '%Mün%' AND is_active = true;"

echo ""
echo "======================================"
echo "Debug Complete"
echo "======================================"