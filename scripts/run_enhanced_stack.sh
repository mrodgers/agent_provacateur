#!/bin/bash
#
# Run the complete enhanced service stack using Docker Compose
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/utils.sh"

# Default values
ACTION="up"
DETACHED=false
REBUILD=false

print_usage() {
    echo "Usage: $0 [options] [action]"
    echo "Actions:"
    echo "  up       Start the services (default)"
    echo "  down     Stop the services"
    echo "  restart  Restart the services"
    echo "  logs     View service logs"
    echo "  status   Check service status"
    echo "Options:"
    echo "  -d, --detached    Run in detached mode"
    echo "  -r, --rebuild     Rebuild images before starting"
    echo "  -h, --help        Show this help message"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        up|down|restart|logs|status)
            ACTION="$1"
            shift
            ;;
        -d|--detached)
            DETACHED=true
            shift
            ;;
        -r|--rebuild)
            REBUILD=true
            shift
            ;;
        -h|--help)
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

# Change to project root directory
cd "$(dirname "${SCRIPT_DIR}")" || exit 1

# Define Docker Compose file
# Note: This also works great with non-Docker development using uv
# See run_enhanced_mcp_server.sh for the non-Docker version

COMPOSE_FILE="docker-compose.enhanced.yml"

if [ ! -f "${COMPOSE_FILE}" ]; then
    echo_error "Docker Compose file not found: ${COMPOSE_FILE}"
    exit 1
fi

case "${ACTION}" in
    up)
        echo_info "Starting enhanced service stack..."
        
        DOCKER_COMPOSE_CMD="docker-compose -f ${COMPOSE_FILE}"
        
        # Rebuild if requested
        if [ "${REBUILD}" = true ]; then
            echo_info "Rebuilding images..."
            ${DOCKER_COMPOSE_CMD} build
        fi
        
        # Start services
        if [ "${DETACHED}" = true ]; then
            ${DOCKER_COMPOSE_CMD} up -d
        else
            ${DOCKER_COMPOSE_CMD} up
        fi
        ;;
        
    down)
        echo_info "Stopping enhanced service stack..."
        docker-compose -f ${COMPOSE_FILE} down
        ;;
        
    restart)
        echo_info "Restarting enhanced service stack..."
        docker-compose -f ${COMPOSE_FILE} restart
        ;;
        
    logs)
        echo_info "Showing logs for enhanced service stack..."
        docker-compose -f ${COMPOSE_FILE} logs -f
        ;;
        
    status)
        echo_info "Checking status of enhanced service stack..."
        docker-compose -f ${COMPOSE_FILE} ps
        ;;
        
    *)
        echo_error "Unknown action: ${ACTION}"
        print_usage
        exit 1
        ;;
esac