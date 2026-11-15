#!/bin/bash

# Remote Application Verification Script
# Verifies all API endpoints are functioning correctly on a remote server

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_IP=${1:-localhost}
API_PORT=${2:-8000}
BASE_URL="http://$SERVER_IP:$API_PORT"

# Counters
PASSED=0
FAILED=0
TOTAL=0

# Test helper function
test_endpoint() {
    local test_num=$1
    local test_name=$2
    local method=$3
    local endpoint=$4
    local data=$5
    
    TOTAL=$((TOTAL + 1))
    
    echo -e "\n${BLUE}Test $test_num: $test_name${NC}"
    echo "Method: $method $endpoint"
    
    if [ -z "$data" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint")
    else
        RESPONSE=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    echo "HTTP Status: $HTTP_CODE"
    
    if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
        echo -e "${GREEN}✅ PASSED${NC}"
        PASSED=$((PASSED + 1))
        
        # Try to pretty print JSON if available
        if command -v jq &> /dev/null; then
            echo "Response:"
            echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
        else
            echo "Response: $BODY"
        fi
    else
        echo -e "${RED}❌ FAILED${NC}"
        FAILED=$((FAILED + 1))
        echo "Response: $BODY"
    fi
}

# Start verification
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Remote Application Verification${NC}"
echo -e "${YELLOW}========================================${NC}"
echo "Server: $SERVER_IP"
echo "Port: $API_PORT"
echo "Base URL: $BASE_URL"
echo ""

# Check if server is reachable
echo -e "${BLUE}Checking server connectivity...${NC}"
if ! timeout 5 bash -c "echo >/dev/tcp/$SERVER_IP/$API_PORT" 2>/dev/null; then
    echo -e "${RED}❌ Cannot connect to $SERVER_IP:$API_PORT${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Server is reachable${NC}"

# Test 1: Health check
test_endpoint 1 "Health Check" GET "/health"

# Test 2: Ready check
test_endpoint 2 "Ready Check" GET "/ready"

# Test 3: List all requests (with seed data)
test_endpoint 3 "List All Requests" GET "/api/requests"

# Test 4: List requests with limit
test_endpoint 4 "List Requests (limit=5)" GET "/api/requests?limit=5&offset=0"

# Test 5: Filter by status
test_endpoint 5 "Filter by Status (submitted)" GET "/api/requests?status=submitted"

# Test 6: Search requests
test_endpoint 6 "Search Requests" GET "/api/requests?search=IT"

# Test 7: Sort by created_at
test_endpoint 7 "Sort by created_at (desc)" GET "/api/requests?sort_by=created_at&sort_order=desc&limit=5"

# Test 8: Filter by priority
test_endpoint 8 "Filter by Priority" GET "/api/requests?priority=3"

# Test 9: Create new request
REQUEST_DATA='{"user_id": 1, "category_id": 1, "title": "Remote Test Request", "description": "Test from verification script", "priority": 2}'
test_endpoint 9 "Create New Request (POST)" POST "/api/requests" "$REQUEST_DATA"

# Extract request ID from last response for subsequent tests
if echo "$BODY" | grep -q '"id"'; then
    if command -v jq &> /dev/null; then
        REQUEST_ID=$(echo "$BODY" | jq -r '.id' 2>/dev/null || echo "")
    else
        REQUEST_ID=$(echo "$BODY" | grep -oP '"id"\s*:\s*\K[^,}]+' | head -1 | tr -d '"')
    fi
fi

# Test 10: Get single request (if we have an ID)
if [ -n "$REQUEST_ID" ] && [ "$REQUEST_ID" != "null" ] && [ "$REQUEST_ID" != "" ]; then
    test_endpoint 10 "Get Single Request" GET "/api/requests/$REQUEST_ID"
    
    # Test 11: Update request
    UPDATE_DATA='{"title": "Updated Remote Test", "description": "Updated from verification"}'
    test_endpoint 11 "Update Request (PATCH)" PATCH "/api/requests/$REQUEST_ID" "$UPDATE_DATA"
    
    # Test 12: Change status
    STATUS_DATA='{"status_name": "in_progress"}'
    test_endpoint 12 "Change Request Status (PUT)" PUT "/api/requests/$REQUEST_ID/status" "$STATUS_DATA"
else
    echo -e "\n${YELLOW}⚠️  Skipping tests 10-12 (no valid request ID)${NC}"
fi

# Test 13: Swagger documentation
test_endpoint 13 "Swagger UI (docs)" GET "/docs"

# Test 14: ReDoc documentation
test_endpoint 14 "ReDoc (redoc)" GET "/redoc"

# Test 15: OpenAPI schema
test_endpoint 15 "OpenAPI Schema (openapi.json)" GET "/openapi.json"

# Summary
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}Verification Summary${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "Total Tests: ${BLUE}$TOTAL${NC}"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
    echo -e "\nAPI is ready for use:"
    echo -e "  Swagger UI: ${BLUE}$BASE_URL/docs${NC}"
    echo -e "  ReDoc: ${BLUE}$BASE_URL/redoc${NC}"
    echo -e "  API Base: ${BLUE}$BASE_URL/api${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please review the output above.${NC}"
    exit 1
fi
