#!/bin/bash
# Start script for Agent Provocateur monitoring stack
# Phase 1 implementation for metrics monitoring

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Agent Provocateur Monitoring - Phase 1${NC}"
echo "This script will:"
echo "1. Start Prometheus, Pushgateway, and Grafana using podman-compose"
echo "2. Run a simple test to verify Pushgateway connectivity"
echo ""

# Check if Podman is available
if ! command -v podman &> /dev/null; then
    echo -e "${YELLOW}Podman not found. Using docker-compose instead.${NC}"
    COMPOSE_CMD="docker-compose"
else    
    COMPOSE_CMD="podman-compose"    
fi

echo -e "${BLUE}Starting monitoring services...${NC}"
if $COMPOSE_CMD up -d; then
    echo -e "${GREEN}Monitoring services started successfully.${NC}"
else
    echo -e "${YELLOW}Warning: There was an issue starting the monitoring services.${NC}"
    echo "If you're using podman, try: podman-compose up -d"
    echo "If you're using Docker, try: docker-compose up -d"
fi

echo ""
echo -e "${BLUE}Services:${NC}"
echo "- Prometheus: http://localhost:9090"
echo "- Pushgateway: http://localhost:9091"
echo "- Grafana: http://localhost:3000 (login: admin/agent_provocateur)"

echo ""
echo -e "${BLUE}Running test metrics script...${NC}"
echo "This will send test metrics to the Pushgateway."

# Wait for services to start
echo "Waiting for services to start (5 seconds)..."
sleep 5

# Run the test metrics script
if python ../src/agent_provocateur/metrics_test.py --pushgateway localhost:9091 --iterations 3; then
    echo -e "${GREEN}Test metrics successfully sent to Pushgateway.${NC}"
else
    echo -e "${YELLOW}Warning: There was an issue running the test metrics script.${NC}"
    echo "Check if the Pushgateway is accessible at http://localhost:9091"
fi

echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Check the metrics in Prometheus: http://localhost:9090"
echo "   - Search for metrics starting with 'ap_test_'"
echo "2. View the Grafana dashboard: http://localhost:3000/d/dejfjfc93klc0a/agent-provocateur-test-dashboard"
echo "   - Login with admin/agent_provocateur"
echo "3. Run the server with metrics: ap-server --pushgateway localhost:9091"
echo "4. Test metrics with CLI: ap-client metrics --pushgateway localhost:9091"

echo ""
echo -e "${GREEN}Phase 1 setup complete!${NC}"