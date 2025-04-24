#!/bin/bash
#
# Enhanced MCP Server Startup Script
# This script starts the enhanced MCP server with improved API documentation
# and handles service discovery for Entity Detector and GraphRAG MCPs.
#

# Source the utility functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/utils.sh"

# Default ports
DEFAULT_MCP_PORT=8000
DEFAULT_ENTITY_DETECTOR_PORT=8082
DEFAULT_GRAPHRAG_PORT=8084
DEFAULT_GRAPHRAG_PY_PORT=9584

# Parse command line options
MCP_PORT=${DEFAULT_MCP_PORT}
ENTITY_DETECTOR_PORT=""
GRAPHRAG_PORT=""
HOST="127.0.0.1"

print_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --host HOST        Host to bind to (default: 127.0.0.1)"
    echo "  -p, --port PORT        Port for the MCP server (default: 8000)"
    echo "  -e, --entity-port PORT Port for the Entity Detector MCP (default: auto-detect)"
    echo "  -g, --graphrag-port PORT Port for the GraphRAG MCP (default: auto-detect)"
    echo "  --stop                 Stop the running Enhanced MCP server"
    echo "  --help                 Show this help message and exit"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            MCP_PORT="$2"
            shift 2
            ;;
        -e|--entity-port)
            ENTITY_DETECTOR_PORT="$2"
            shift 2
            ;;
        -g|--graphrag-port)
            GRAPHRAG_PORT="$2"
            shift 2
            ;;
        --stop)
            # Stop the server if it's running
            LOG_DIR="$(get_project_root)/logs"
            PID_FILE="${LOG_DIR}/enhanced_mcp.pid"
            if [ -f "${PID_FILE}" ]; then
                PID=$(cat "${PID_FILE}")
                if kill -0 "${PID}" 2>/dev/null; then
                    echo_info "Stopping Enhanced MCP server (PID: ${PID})..."
                    kill "${PID}"
                    sleep 1
                    if kill -0 "${PID}" 2>/dev/null; then
                        echo_warning "Server didn't stop gracefully, forcing..."
                        kill -9 "${PID}"
                    fi
                    rm -f "${PID_FILE}"
                    echo_success "Enhanced MCP server stopped"
                else
                    echo_warning "Enhanced MCP server not running (stale PID file)"
                    rm -f "${PID_FILE}"
                fi
            else
                echo_warning "No PID file found for Enhanced MCP server"
            fi
            exit 0
            ;;
        --help)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Check if the port is available
check_port_availability() {
    local port=$1
    if nc -z ${HOST} ${port} 2>/dev/null; then
        echo_error "Port ${port} is already in use."
        return 1
    fi
    return 0
}

# Check if MCP port is available
if ! check_port_availability ${MCP_PORT}; then
    echo_warning "Trying to find an alternative port..."
    for alt_port in {8001..8010}; do
        if check_port_availability ${alt_port}; then
            echo_info "Found available port: ${alt_port}"
            MCP_PORT=${alt_port}
            break
        fi
    done
    
    if [ ${MCP_PORT} -eq ${DEFAULT_MCP_PORT} ]; then
        echo_error "Could not find an available port. Please free up port ${DEFAULT_MCP_PORT} or specify an alternative port."
        exit 1
    fi
fi

# Detect Entity Detector MCP service
if [ -z "${ENTITY_DETECTOR_PORT}" ]; then
    # First try the default port
    if curl -s http://${HOST}:${DEFAULT_ENTITY_DETECTOR_PORT}/tools >/dev/null 2>&1; then
        ENTITY_DETECTOR_PORT=${DEFAULT_ENTITY_DETECTOR_PORT}
        echo_info "Found Entity Detector MCP on port ${ENTITY_DETECTOR_PORT}"
    else
        # Try alternative ports (entity detector might be running on 9585)
        alternative_port=9585
        if curl -s http://${HOST}:${alternative_port}/tools >/dev/null 2>&1; then
            ENTITY_DETECTOR_PORT=${alternative_port}
            echo_info "Found Entity Detector MCP on port ${ENTITY_DETECTOR_PORT}"
        else
            echo_warning "Entity Detector MCP not found. API endpoints requiring entity detection will return errors."
            # Default to the standard port anyway
            ENTITY_DETECTOR_PORT=${DEFAULT_ENTITY_DETECTOR_PORT}
        fi
    fi
fi

# Detect GraphRAG MCP service
if [ -z "${GRAPHRAG_PORT}" ]; then
    # First try the default TS implementation
    if curl -s http://${HOST}:${DEFAULT_GRAPHRAG_PORT}/api/info >/dev/null 2>&1; then
        GRAPHRAG_PORT=${DEFAULT_GRAPHRAG_PORT}
        echo_info "Found GraphRAG MCP TypeScript implementation on port ${GRAPHRAG_PORT}"
    # Then try the Python implementation
    elif curl -s http://${HOST}:${DEFAULT_GRAPHRAG_PY_PORT}/api/info >/dev/null 2>&1; then
        GRAPHRAG_PORT=${DEFAULT_GRAPHRAG_PY_PORT}
        echo_info "Found GraphRAG MCP Python implementation on port ${GRAPHRAG_PORT}"
    else
        echo_warning "GraphRAG MCP not found. API endpoints requiring research will return errors."
        # Default to the standard port anyway
        GRAPHRAG_PORT=${DEFAULT_GRAPHRAG_PORT}
    fi
fi

# Run the enhanced MCP server
echo_info "Starting Enhanced MCP server on ${HOST}:${MCP_PORT}"
echo_info "- Entity Detector URL: http://${HOST}:${ENTITY_DETECTOR_PORT}"
echo_info "- GraphRAG URL: http://${HOST}:${GRAPHRAG_PORT}"

# Set log file
LOG_DIR="$(get_project_root)/logs"
mkdir -p ${LOG_DIR}
LOG_FILE="${LOG_DIR}/enhanced_mcp_server.log"

# Set environment variables before running
ENTITY_DETECTOR_URL="http://${HOST}:${ENTITY_DETECTOR_PORT}"
GRAPHRAG_URL="http://${HOST}:${GRAPHRAG_PORT}"

# Run the server
PYTHONPATH="${PYTHONPATH}:$(pwd)/.." uv run -m agent_provocateur mcp --host ${HOST} --port ${MCP_PORT} --entity-detector ${ENTITY_DETECTOR_URL} --graphrag ${GRAPHRAG_URL} >${LOG_FILE} 2>&1 &

# Save PID
PID=$!
echo $PID > "${LOG_DIR}/enhanced_mcp.pid"
echo_info "Enhanced MCP server started with PID: $PID on port ${MCP_PORT}"
echo_info "Check logs at: ${LOG_FILE}"
echo_info "You can access the API documentation at: http://${HOST}:${MCP_PORT}/docs"