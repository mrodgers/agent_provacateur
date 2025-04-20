#!/bin/bash
# Cleanup script for Agent Provocateur monitoring stack
# This script removes all monitoring containers and data

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Agent Provocateur Monitoring - Cleanup${NC}"
echo "This script will:"
echo "1. Stop and remove all monitoring containers (Prometheus, Pushgateway, Grafana)"
echo "2. Remove monitoring volumes (Grafana data)"
echo ""

# Confirm cleanup
read -p "Are you sure you want to clean up the monitoring stack? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cleanup cancelled.${NC}"
    exit 0
fi

# Check if Podman is available
if ! command -v podman &> /dev/null; then
    echo -e "${YELLOW}Podman not found. Using docker-compose instead.${NC}"
    COMPOSE_CMD="docker-compose"
else    
    COMPOSE_CMD="podman-compose"    
fi

# Stop and remove all containers
echo -e "${BLUE}Stopping and removing all monitoring containers...${NC}"
cd "$(dirname "$0")" # Make sure we're in the monitoring directory
$COMPOSE_CMD down -v

# Delete any Prometheus metrics pushed to Pushgateway
echo -e "${BLUE}Cleaning up any leftover Pushgateway metrics...${NC}"
if curl -s -X DELETE http://localhost:9091/metrics; then
    echo -e "${GREEN}Successfully deleted Pushgateway metrics.${NC}"
else
    echo -e "${YELLOW}No Pushgateway running, nothing to clean up.${NC}"
fi

echo ""
echo -e "${GREEN}Cleanup complete!${NC}"
echo "You can restart the monitoring stack with: ./start.sh"