#!/bin/bash
# Test script for Entity Detector MCP service

set -e  # Exit on error

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Config
ENTITY_DETECTOR_DIR="$(pwd)/entity_detector_mcp"
PORT=8082
TEST_TIMEOUT=30  # seconds
REQUIRED_COVERAGE=80  # Minimum coverage percentage required to pass

echo "=== Entity Detector MCP Service Test Script ==="

# Check if entity detector directory exists
if [ ! -d "$ENTITY_DETECTOR_DIR" ]; then
  echo -e "${RED}Error: Entity Detector directory not found at $ENTITY_DETECTOR_DIR${NC}"
  exit 1
fi

cd "$ENTITY_DETECTOR_DIR"

# Ensure dependencies are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
npm install --quiet

# Run linting
echo -e "${YELLOW}Running linter...${NC}"
if [ -f "package.json" ] && grep -q "\"lint\"" "package.json"; then
  npm run lint || { echo -e "${RED}Linting failed${NC}"; exit 1; }
else
  echo -e "${YELLOW}No lint script found, skipping.${NC}"
fi

# Build the project
echo -e "${YELLOW}Building project...${NC}"
npm run build || { echo -e "${RED}Build failed${NC}"; exit 1; }

# Run unit tests
echo -e "${YELLOW}Running unit tests with coverage...${NC}"
npm test -- --coverage || { echo -e "${RED}Tests failed${NC}"; exit 1; }

# Check coverage threshold
COVERAGE_RESULT=$(cat ./coverage/lcov-report/index.html | grep -o 'strong>[0-9]*\.[0-9]*%' | head -1 | grep -o '[0-9]*\.[0-9]*')
COVERAGE_INT=${COVERAGE_RESULT%.*}

echo -e "${YELLOW}Test coverage: ${GREEN}$COVERAGE_RESULT%${NC}"

if [ "$COVERAGE_INT" -lt "$REQUIRED_COVERAGE" ]; then
  echo -e "${RED}Coverage is below required threshold of $REQUIRED_COVERAGE%${NC}"
  exit 1
else
  echo -e "${GREEN}Coverage meets required threshold of $REQUIRED_COVERAGE%${NC}"
fi

# Start the service for integration testing
echo -e "${YELLOW}Starting Entity Detector service for integration tests...${NC}"
node dist/index.js &
SERVICE_PID=$!

# Wait for service to start
echo -e "${YELLOW}Waiting for service to start...${NC}"
TRIES=0
MAX_TRIES=$TEST_TIMEOUT
while ! curl -s "http://localhost:$PORT/tools" > /dev/null; do
  sleep 1
  TRIES=$((TRIES+1))
  if [ "$TRIES" -ge "$MAX_TRIES" ]; then
    echo -e "${RED}Service failed to start within $TEST_TIMEOUT seconds${NC}"
    kill $SERVICE_PID
    exit 1
  fi
done

echo -e "${GREEN}Service started successfully${NC}"

# Run basic API test
echo -e "${YELLOW}Testing API endpoints...${NC}"
API_TEST_RESULT=$(curl -s -X POST \
  "http://localhost:$PORT/tools/extract_entities/run" \
  -H "Content-Type: application/json" \
  -d '{"text":"Test entity extraction with example@email.com and https://example.com"}')

# Check if entities were found in the response
if echo "$API_TEST_RESULT" | grep -q "\"entities\""; then
  echo -e "${GREEN}API test successful. Found entities in response.${NC}"
else
  echo -e "${RED}API test failed. No entities found in response:${NC}"
  echo "$API_TEST_RESULT"
  kill $SERVICE_PID
  exit 1
fi

# Test detector info endpoint
DETECTOR_INFO=$(curl -s -X POST \
  "http://localhost:$PORT/tools/detector_info/run" \
  -H "Content-Type: application/json" \
  -d '{}')

if echo "$DETECTOR_INFO" | grep -q "\"availableDetectors\""; then
  echo -e "${GREEN}Detector info endpoint test successful.${NC}"
else
  echo -e "${RED}Detector info endpoint test failed:${NC}"
  echo "$DETECTOR_INFO"
  kill $SERVICE_PID
  exit 1
fi

# Test XML-specific entity extraction
echo -e "${YELLOW}Testing XML entity extraction...${NC}"
XML_TEST_RESULT=$(curl -s -X POST \
  "http://localhost:$PORT/tools/extract_entities/run" \
  -H "Content-Type: application/json" \
  -d '{"text":"<document><price>$99.99</price><author>John Doe</author><title>Test Document</title></document>"}')

# Check if XML-specific entities were found
if echo "$XML_TEST_RESULT" | grep -q "\"xmlElement\""; then
  echo -e "${GREEN}XML entity extraction test successful.${NC}"
else
  echo -e "${RED}XML entity extraction test failed:${NC}"
  echo "$XML_TEST_RESULT"
  kill $SERVICE_PID
  exit 1
fi

# Cleanup
echo -e "${YELLOW}Stopping service...${NC}"
kill $SERVICE_PID

echo -e "${GREEN}All tests passed successfully!${NC}"
exit 0