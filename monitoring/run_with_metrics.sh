#!/bin/bash
# Script to run Agent Provocateur with metrics enabled
# Phase 1 implementation for metrics monitoring

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PUSHGATEWAY="localhost:9091"
METRICS_PORT=8001
SERVER_PORT=8000

# Check if Pushgateway is running
if ! curl -s "http://${PUSHGATEWAY}" > /dev/null; then
    echo -e "${YELLOW}Warning: Pushgateway does not appear to be running at ${PUSHGATEWAY}${NC}"
    echo "Make sure to start the monitoring stack first:"
    echo "  cd monitoring"
    echo "  ./start.sh"
    echo ""
    echo -e "${YELLOW}Continuing with metrics enabled, but they won't be pushed to Pushgateway...${NC}"
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --metrics-port)
            METRICS_PORT="$2"
            shift 2
            ;;
        --server-port)
            SERVER_PORT="$2"
            shift 2
            ;;
        --pushgateway)
            PUSHGATEWAY="$2"
            shift 2
            ;;
        --no-metrics)
            NO_METRICS=1
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --metrics-port PORT    Metrics server port (default: 8001)"
            echo "  --server-port PORT     MCP server port (default: 8000)"
            echo "  --pushgateway URL      Pushgateway URL (default: localhost:9091)"
            echo "  --no-metrics           Disable metrics"
            echo "  --help                 Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}Starting Agent Provocateur server with metrics enabled${NC}"
echo "Server port: ${SERVER_PORT}"

if [ -z "$NO_METRICS" ]; then
    echo "Metrics port: ${METRICS_PORT}"
    echo "Pushgateway: ${PUSHGATEWAY}"
    
    echo ""
    echo -e "${BLUE}Running ap-server:${NC}"
    ap-server --host 127.0.0.1 --port ${SERVER_PORT} --metrics-port ${METRICS_PORT} --pushgateway ${PUSHGATEWAY}
else
    echo "Metrics: Disabled"
    
    echo ""
    echo -e "${BLUE}Running ap-server:${NC}"
    ap-server --host 127.0.0.1 --port ${SERVER_PORT} --no-metrics
fi