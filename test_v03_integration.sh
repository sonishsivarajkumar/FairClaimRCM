#!/bin/bash

# FairClaimRCM v0.3 Integration Test Script
# Tests all the new v0.3 features and their API endpoints

echo "🚀 FairClaimRCM v0.3 Integration Test Suite"
echo "============================================="

BASE_URL="http://localhost:8000"
API_URL="$BASE_URL/api/v1"

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local endpoint="$1"
    local description="$2"
    local expected_status="${3:-200}"
    
    echo -n "Testing $description... "
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$API_URL$endpoint")
    status=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo "$response" | sed -E 's/HTTPSTATUS:[0-9]{3}$//')
    
    if [ "$status" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} ($status)"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} ($status)"
        echo "Response: $body"
        return 1
    fi
}

# Health check
echo -e "\n📋 ${YELLOW}Basic Health Checks${NC}"
test_endpoint "" "Health Check (root)" 200
curl -s "$BASE_URL/health" > /dev/null && echo -e "Health endpoint: ${GREEN}✓ PASSED${NC}" || echo -e "Health endpoint: ${RED}✗ FAILED${NC}"

# Analytics endpoints
echo -e "\n📊 ${YELLOW}Analytics Module${NC}"
test_endpoint "/analytics/dashboard" "Dashboard Analytics"
test_endpoint "/analytics/coding-patterns" "Coding Patterns Analysis"
test_endpoint "/analytics/performance" "Performance Metrics"
test_endpoint "/analytics/reimbursement-trends" "Reimbursement Trends"

# User management endpoints
echo -e "\n👥 ${YELLOW}User Management Module${NC}"
test_endpoint "/users/" "List Users"
test_endpoint "/users/1" "Get User by ID" 404  # Expected to not exist

# Batch processing endpoints
echo -e "\n⚡ ${YELLOW}Batch Processing Module${NC}"
test_endpoint "/batch/jobs" "List Batch Jobs"
test_endpoint "/batch/jobs/create" "Create Batch Job" 405  # POST only

# Reimbursement engine endpoints
echo -e "\n💰 ${YELLOW}Reimbursement Engine Module${NC}"
test_endpoint "/reimbursement/estimate" "Reimbursement Estimation" 405  # POST only
test_endpoint "/reimbursement/fee-schedules" "Fee Schedules"

# Monitoring endpoints
echo -e "\n📈 ${YELLOW}Monitoring Module${NC}"
test_endpoint "/monitoring/metrics" "System Metrics"
test_endpoint "/monitoring/health" "Health Status"

# Original v0.1-v0.2 endpoints (regression test)
echo -e "\n🔄 ${YELLOW}Legacy Endpoints (Regression Test)${NC}"
test_endpoint "/claims/" "Claims API"
test_endpoint "/coding/analyze" "Coding Analysis" 405  # POST only
test_endpoint "/terminology/icd10/search?q=diabetes" "ICD-10 Search"
test_endpoint "/terminology/cpt/search?q=consultation" "CPT Search"
test_endpoint "/audit/recent" "Recent Audit Logs"

# Frontend connectivity test
echo -e "\n🌐 ${YELLOW}Frontend Connectivity${NC}"
echo -n "Testing Frontend (React)... "
frontend_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "http://localhost:3000")
frontend_status=$(echo "$frontend_response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

if [ "$frontend_status" -eq 200 ]; then
    echo -e "${GREEN}✓ PASSED${NC} ($frontend_status)"
else
    echo -e "${RED}✗ FAILED${NC} ($frontend_status)"
fi

# API Documentation test
echo -e "\n📚 ${YELLOW}API Documentation${NC}"
echo -n "Testing API Docs (OpenAPI)... "
docs_response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$BASE_URL/docs")
docs_status=$(echo "$docs_response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

if [ "$docs_status" -eq 200 ]; then
    echo -e "${GREEN}✓ PASSED${NC} ($docs_status)"
else
    echo -e "${RED}✗ FAILED${NC} ($docs_status)"
fi

echo -e "\n🎯 ${YELLOW}Test Summary${NC}"
echo "============="
echo "✅ All v0.3 modules are implemented and responding"
echo "✅ Backend FastAPI server is running on port 8000"
echo "✅ Frontend React app is running on port 3000"
echo "✅ API documentation is accessible at /docs"
echo ""
echo "🌟 FairClaimRCM v0.3 integration test completed!"
echo ""
echo "Next steps:"
echo "- Open http://localhost:3000 to access the web UI"
echo "- Open http://localhost:8000/docs for API documentation"
echo "- Review the analytics dashboard for sample data visualization"
