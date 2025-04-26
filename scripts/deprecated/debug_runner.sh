#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Debug log file
DEBUG_LOG="debug_runner.log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Function to log messages
log() {
    local level=$1
    local message=$2
    echo -e "[$TIMESTAMP] [$level] $message" | tee -a $DEBUG_LOG
}

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
    log "INFO" "=== $1 ==="
}

# Function to check if a command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        log "ERROR" "$1 is not installed"
        return 1
    fi
    return 0
}

# Function to check if a port is in use
check_port() {
    local port=$1
    local service=$2
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if lsof -i :$port > /dev/null 2>&1; then
            log "WARN" "Port $port ($service) is in use, attempting to free it..."
            
            # Try to identify the process using the port
            local pid=$(lsof -ti :$port)
            if [ ! -z "$pid" ]; then
                log "INFO" "Found process $pid using port $port"
                kill -9 $pid 2>/dev/null || true
                sleep 2
            fi
            
            # Double check if port is still in use
            if lsof -i :$port > /dev/null 2>&1; then
                retry_count=$((retry_count + 1))
                if [ $retry_count -lt $max_retries ]; then
                    log "WARN" "Port $port still in use, retrying in 5 seconds..."
                    sleep 5
                else
                    log "ERROR" "Port $port ($service) is still in use after $max_retries attempts"
                    return 1
                fi
            else
                log "INFO" "Port $port ($service) is now free"
                return 0
            fi
        else
            log "INFO" "Port $port ($service) is available"
            return 0
        fi
    done
}

# Function to check container ports
check_container_ports() {
    print_section "Checking Container Ports"
    
    # Check if any containers are using the required ports
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        for port in 3001 8111 6111 7111 3111 9111; do
            if podman ps --format "{{.Ports}}" | grep -q ":$port->"; then
                log "WARN" "Container using port $port found, stopping all containers..."
                podman stop $(podman ps -q) 2>/dev/null || true
                sleep 5
            fi
        done
    else
        for port in 3001 8111 6111 7111 3111 9111; do
            if docker ps --format "{{.Ports}}" | grep -q ":$port->"; then
                log "WARN" "Container using port $port found, stopping all containers..."
                docker stop $(docker ps -q) 2>/dev/null || true
                sleep 5
            fi
        done
    fi
}

# Function to check container health
check_container_health() {
    local container=$1
    local max_retries=3
    local retry_count=0
    local health_status=""
    
    while [ $retry_count -lt $max_retries ]; do
        if [ "$CONTAINER_ENGINE" = "podman" ]; then
            health_status=$(podman healthcheck run $container 2>/dev/null)
            if [ $? -eq 0 ]; then
                log "INFO" "Container $container is healthy"
                return 0
            fi
        else
            health_status=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null)
            if [ "$health_status" = "healthy" ]; then
                log "INFO" "Container $container is healthy"
                return 0
            fi
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            log "WARN" "Container $container health check failed, retrying in 5 seconds..."
            sleep 5
        fi
    done
    
    log "ERROR" "Container $container health check failed after $max_retries attempts: $health_status"
    return 1
}

# Function to clean up environment
cleanup() {
    print_section "Cleaning Up Environment"
    
    # Stop all containers
    log "INFO" "Stopping all containers..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        # Stop all running containers
        podman stop $(podman ps -q) 2>/dev/null || true
        podman-compose down 2>/dev/null || true
    else
        # Stop all running containers
        docker stop $(docker ps -q) 2>/dev/null || true
        docker-compose down 2>/dev/null || true
    fi
    
    # Wait for containers to stop
    sleep 5
    
    # Remove all containers
    log "INFO" "Removing all containers..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman rm -f $(podman ps -aq) 2>/dev/null || true
        podman container prune -f 2>/dev/null || true
    else
        docker rm -f $(docker ps -aq) 2>/dev/null || true
        docker container prune -f 2>/dev/null || true
    fi
    
    # Wait for containers to be removed
    sleep 2
    
    # Remove all networks
    log "INFO" "Removing all networks..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman network prune -f 2>/dev/null || true
        podman network rm $(podman network ls -q) 2>/dev/null || true
    else
        docker network prune -f 2>/dev/null || true
        docker network rm $(docker network ls -q) 2>/dev/null || true
    fi
    
    # Wait for networks to be removed
    sleep 2
    
    # Remove all volumes
    log "INFO" "Removing all volumes..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman volume prune -f 2>/dev/null || true
        podman volume rm $(podman volume ls -q) 2>/dev/null || true
    else
        docker volume prune -f 2>/dev/null || true
        docker volume rm $(docker volume ls -q) 2>/dev/null || true
    fi
    
    # Wait for volumes to be removed
    sleep 2
    
    # Check if ports are still in use
    log "INFO" "Checking if ports are still in use..."
    for port in 3001 8111 6111 7111 3111 9111; do
        if lsof -i :$port > /dev/null 2>&1; then
            log "WARN" "Port $port is still in use, attempting to free it..."
            if [ "$CONTAINER_ENGINE" = "podman" ]; then
                podman stop $(podman ps -q) 2>/dev/null || true
            else
                docker stop $(docker ps -q) 2>/dev/null || true
            fi
            sleep 5
        fi
    done
    
    log "INFO" "Cleanup completed"
}

# Function to wait for service
wait_for_service() {
    local service=$1
    local port=$2
    local max_retries=30
    local retry_count=0
    local wait_time=2
    
    log "INFO" "Waiting for $service to be ready..."
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s http://localhost:$port/api/health > /dev/null; then
            log "INFO" "$service is ready"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            log "WARN" "$service not ready, retrying in $wait_time seconds... (Attempt $retry_count/$max_retries)"
            sleep $wait_time
        fi
    done
    
    log "ERROR" "$service failed to start after $max_retries attempts"
    return 1
}

# Function to wait for container
wait_for_container() {
    local container=$1
    local max_retries=30
    local retry_count=0
    local wait_time=2
    
    log "INFO" "Waiting for container $container to be ready..."
    
    while [ $retry_count -lt $max_retries ]; do
        if [ "$CONTAINER_ENGINE" = "podman" ]; then
            if podman ps | grep -q "$container"; then
                log "INFO" "Container $container is ready"
                return 0
            fi
        else
            if docker ps | grep -q "$container"; then
                log "INFO" "Container $container is ready"
                return 0
            fi
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            log "WARN" "Container $container not ready, retrying in $wait_time seconds... (Attempt $retry_count/$max_retries)"
            sleep $wait_time
        fi
    done
    
    log "ERROR" "Container $container failed to start after $max_retries attempts"
    return 1
}

# Function to start services
start_services() {
    print_section "Starting Services"
    
    # Double check cleanup
    cleanup
    
    # Check container ports
    check_container_ports
    
    # Check if ports are available with retries
    log "INFO" "Checking port availability..."
    for port in 3001 8111 6111 7111 3111 9111; do
        check_port $port "Service"
        if [ $? -ne 0 ]; then
            log "ERROR" "Failed to free port $port, aborting startup"
            return 1
        fi
    done
    
    # Start services
    log "INFO" "Starting services with $COMPOSE_CMD..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman-compose up --build -d
    else
        docker-compose up --build -d
    fi
    
    # Wait for containers to be ready
    wait_for_container "agent_provacateur_new_ui_frontend_1"
    wait_for_container "agent_provacateur_new_ui_mcp-server_1"
    wait_for_container "agent_provacateur_new_ui_redis_1"
    wait_for_container "agent_provacateur_new_ui_ollama_1"
    wait_for_container "agent_provacateur_new_ui_monitoring_1"
    wait_for_container "agent_provacateur_new_ui_grafana_1"
    
    # Wait for services to be ready
    wait_for_service "Frontend" 3001
    wait_for_service "Backend" 8111
    
    # Check container health with retries
    check_container_health agent_provacateur_new_ui_frontend_1
    check_container_health agent_provacateur_new_ui_mcp-server_1
    check_container_health agent_provacateur_new_ui_redis_1
}

# Function to test Redis connection
test_redis() {
    print_section "Testing Redis Connection"
    
    # Check Redis port
    if ! check_port 4003 "Redis"; then
        log "ERROR" "Redis port is not available"
        return 1
    fi
    
    # Test Redis connection with detailed error
    log "INFO" "Testing Redis connection..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        response=$(podman exec agent_provacateur_new_ui_mcp-server_1 redis-cli -h redis ping 2>&1)
    else
        response=$(docker exec agent_provacateur_new_ui_mcp-server_1 redis-cli -h redis ping 2>&1)
    fi
    
    if [ "$response" = "PONG" ]; then
        log "INFO" "Redis connection successful"
    else
        log "ERROR" "Redis connection failed: $response"
        
        # Check if container is running
        if [ "$CONTAINER_ENGINE" = "podman" ]; then
            if podman ps | grep -q "redis"; then
                log "INFO" "Redis container is running"
            else
                log "ERROR" "Redis container is not running"
            fi
        else
            if docker ps | grep -q "redis"; then
                log "INFO" "Redis container is running"
            else
                log "ERROR" "Redis container is not running"
            fi
        fi
        return 1
    fi
    
    # Test Redis operations with detailed error
    log "INFO" "Testing Redis operations..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        set_response=$(podman exec agent_provacateur_new_ui_mcp-server_1 redis-cli -h redis set test_key "test_value" 2>&1)
        get_response=$(podman exec agent_provacateur_new_ui_mcp-server_1 redis-cli -h redis get test_key 2>&1)
    else
        set_response=$(docker exec agent_provacateur_new_ui_mcp-server_1 redis-cli -h redis set test_key "test_value" 2>&1)
        get_response=$(docker exec agent_provacateur_new_ui_mcp-server_1 redis-cli -h redis get test_key 2>&1)
    fi
    
    if [ "$set_response" = "OK" ] && [ "$get_response" = "test_value" ]; then
        log "INFO" "Redis operations successful"
    else
        log "ERROR" "Redis operations failed"
        log "ERROR" "Set response: $set_response"
        log "ERROR" "Get response: $get_response"
        return 1
    fi
    
    # Check Redis logs
    log "INFO" "Checking Redis logs..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman logs agent_provacateur_new_ui_redis_1 --tail 50 2>/dev/null || log "WARN" "No Redis logs available"
    else
        docker logs agent_provacateur_new_ui_redis_1 --tail 50 2>/dev/null || log "WARN" "No Redis logs available"
    fi
    
    log "INFO" "Redis testing completed"
    return 0
}

# Function to test Ollama connection
test_ollama() {
    print_section "Testing Ollama Connection"
    
    # Check Ollama port
    if ! check_port 7111 "Ollama"; then
        log "WARN" "Ollama port is not available (optional service)"
        return 0
    fi
    
    # Test Ollama connection with detailed error
    log "INFO" "Testing Ollama connection..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        response=$(podman exec agent_provacateur_new_ui_mcp-server_1 curl -s -w "\n%{http_code}" http://ollama:11434/api/health)
    else
        response=$(docker exec agent_provacateur_new_ui_mcp-server_1 curl -s -w "\n%{http_code}" http://ollama:11434/api/health)
    fi
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        log "INFO" "Ollama connection successful"
    else
        log "WARN" "Ollama connection failed (optional service)"
        log "WARN" "HTTP Code: $http_code"
        log "WARN" "Response: $response_body"
        
        # Check if container is running
        if [ "$CONTAINER_ENGINE" = "podman" ]; then
            if podman ps | grep -q "ollama"; then
                log "INFO" "Ollama container is running"
            else
                log "WARN" "Ollama container is not running"
            fi
        else
            if docker ps | grep -q "ollama"; then
                log "INFO" "Ollama container is running"
            else
                log "WARN" "Ollama container is not running"
            fi
        fi
        return 0
    fi
    
    # Test Ollama model loading with detailed error
    log "INFO" "Testing Ollama model loading..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        response=$(podman exec agent_provacateur_new_ui_mcp-server_1 curl -s -w "\n%{http_code}" http://ollama:11434/api/tags)
    else
        response=$(docker exec agent_provacateur_new_ui_mcp-server_1 curl -s -w "\n%{http_code}" http://ollama:11434/api/tags)
    fi
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] && echo "$response_body" | grep -q "model"; then
        log "INFO" "Ollama model loading successful"
    else
        log "WARN" "Ollama model loading failed (optional service)"
        log "WARN" "HTTP Code: $http_code"
        log "WARN" "Response: $response_body"
        return 0
    fi
    
    # Check Ollama logs
    log "INFO" "Checking Ollama logs..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman logs agent_provacateur_new_ui_ollama_1 --tail 50 2>/dev/null || log "WARN" "No Ollama logs available"
    else
        docker logs agent_provacateur_new_ui_ollama_1 --tail 50 2>/dev/null || log "WARN" "No Ollama logs available"
    fi
    
    log "INFO" "Ollama testing completed"
    return 0
}

# Function to test Grafana connection
test_grafana() {
    print_section "Testing Grafana Connection"
    
    # Check Grafana port
    if ! check_port 3111 "Grafana"; then
        log "WARN" "Grafana port is not available (optional service)"
        return 0
    fi
    
    # Test Grafana connection with detailed error
    log "INFO" "Testing Grafana connection..."
    response=$(curl -s -w "\n%{http_code}" http://localhost:3111/api/health)
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        log "INFO" "Grafana connection successful"
    else
        log "WARN" "Grafana connection failed (optional service)"
        log "WARN" "HTTP Code: $http_code"
        log "WARN" "Response: $response_body"
        
        # Check if container is running
        if [ "$CONTAINER_ENGINE" = "podman" ]; then
            if podman ps | grep -q "grafana"; then
                log "INFO" "Grafana container is running"
            else
                log "WARN" "Grafana container is not running"
            fi
        else
            if docker ps | grep -q "grafana"; then
                log "INFO" "Grafana container is running"
            else
                log "WARN" "Grafana container is not running"
            fi
        fi
        return 0
    fi
    
    # Test Grafana API with detailed error
    log "INFO" "Testing Grafana API..."
    response=$(curl -s -w "\n%{http_code}" -u admin:agent_provocateur http://localhost:3111/api/datasources)
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        log "INFO" "Grafana API successful"
    else
        log "WARN" "Grafana API failed (optional service)"
        log "WARN" "HTTP Code: $http_code"
        log "WARN" "Response: $response_body"
        return 0
    fi
    
    # Check Grafana logs
    log "INFO" "Checking Grafana logs..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman logs agent_provacateur_new_ui_grafana_1 --tail 50 2>/dev/null || log "WARN" "No Grafana logs available"
    else
        docker logs agent_provacateur_new_ui_grafana_1 --tail 50 2>/dev/null || log "WARN" "No Grafana logs available"
    fi
    
    log "INFO" "Grafana testing completed"
    return 0
}

# Function to test Prometheus connection
test_prometheus() {
    print_section "Testing Prometheus Connection"
    
    # Check Prometheus port
    if ! check_port 9111 "Prometheus"; then
        log "WARN" "Prometheus port is not available (optional service)"
        return 0
    fi
    
    # Test Prometheus connection with detailed error
    log "INFO" "Testing Prometheus connection..."
    response=$(curl -s -w "\n%{http_code}" http://localhost:9111/-/healthy)
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        log "INFO" "Prometheus connection successful"
    else
        log "WARN" "Prometheus connection failed (optional service)"
        log "WARN" "HTTP Code: $http_code"
        log "WARN" "Response: $response_body"
        
        # Check if container is running
        if [ "$CONTAINER_ENGINE" = "podman" ]; then
            if podman ps | grep -q "prometheus"; then
                log "INFO" "Prometheus container is running"
            else
                log "WARN" "Prometheus container is not running"
            fi
        else
            if docker ps | grep -q "prometheus"; then
                log "INFO" "Prometheus container is running"
            else
                log "WARN" "Prometheus container is not running"
            fi
        fi
        return 0
    fi
    
    # Test Prometheus metrics with detailed error
    log "INFO" "Testing Prometheus metrics..."
    response=$(curl -s -w "\n%{http_code}" http://localhost:9111/metrics)
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] && echo "$response_body" | grep -q "prometheus"; then
        log "INFO" "Prometheus metrics successful"
    else
        log "WARN" "Prometheus metrics failed (optional service)"
        log "WARN" "HTTP Code: $http_code"
        log "WARN" "Response: $response_body"
        return 0
    fi
    
    # Check Prometheus logs
    log "INFO" "Checking Prometheus logs..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman logs agent_provacateur_new_ui_monitoring_1 --tail 50 2>/dev/null || log "WARN" "No Prometheus logs available"
    else
        docker logs agent_provacateur_new_ui_monitoring_1 --tail 50 2>/dev/null || log "WARN" "No Prometheus logs available"
    fi
    
    log "INFO" "Prometheus testing completed"
    return 0
}

# Function to test backend
test_backend() {
    print_section "Testing Backend"
    
    # Wait for backend to be ready
    wait_for_service "Backend" 8111
    if [ $? -ne 0 ]; then
        log "ERROR" "Backend failed to start"
        return 1
    fi
    
    # Check if backend is accessible
    log "INFO" "Checking backend accessibility..."
    if curl -s http://localhost:8111/api/health > /dev/null; then
        log "INFO" "Backend is accessible"
    else
        log "ERROR" "Backend is not accessible"
        return 1
    fi
    
    # Test backend API endpoints
    log "INFO" "Testing backend API endpoints..."
    
    # Test health endpoint
    response=$(curl -s http://localhost:8111/api/health)
    if [[ $response == *"ok"* ]]; then
        log "INFO" "Backend health check passed"
    else
        log "ERROR" "Backend health check failed: $response"
        return 1
    fi
    
    # Test Redis connection
    test_redis
    if [ $? -ne 0 ]; then
        log "ERROR" "Redis testing failed"
        return 1
    fi
    
    # Test Ollama connection
    test_ollama
    
    # Test Grafana connection
    test_grafana
    
    # Test Prometheus connection
    test_prometheus
    
    # Test backend logs
    log "INFO" "Checking backend logs..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman logs agent_provacateur_new_ui_mcp-server_1 --tail 50 2>/dev/null || log "WARN" "No backend logs available"
    else
        docker logs agent_provacateur_new_ui_mcp-server_1 --tail 50 2>/dev/null || log "WARN" "No backend logs available"
    fi
    
    log "INFO" "Backend testing completed"
    return 0
}

# Function to test frontend
test_frontend() {
    print_section "Testing Frontend"
    
    # Wait for frontend to be ready
    wait_for_service "Frontend" 3001
    if [ $? -ne 0 ]; then
        log "ERROR" "Frontend failed to start"
        return 1
    fi
    
    # Check if frontend is accessible
    log "INFO" "Checking frontend accessibility..."
    if curl -s http://localhost:3001/api/health > /dev/null; then
        log "INFO" "Frontend is accessible"
    else
        log "ERROR" "Frontend is not accessible"
        return 1
    fi
    
    # Test frontend API endpoints
    log "INFO" "Testing frontend API endpoints..."
    
    # Test health endpoint
    response=$(curl -s http://localhost:3001/api/health)
    if [[ $response == *"ok"* ]]; then
        log "INFO" "Frontend health check passed"
    else
        log "ERROR" "Frontend health check failed: $response"
        return 1
    fi
    
    # Test API test runner
    response=$(curl -s http://localhost:3001/api-test-runner)
    if [[ $response != *"Error response"* ]]; then
        log "INFO" "API test runner passed"
    else
        log "ERROR" "API test runner failed: $response"
        return 1
    fi
    
    # Test frontend logs
    log "INFO" "Checking frontend logs..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman logs agent_provacateur_new_ui_frontend_1 --tail 50 2>/dev/null || log "WARN" "No frontend logs available"
    else
        docker logs agent_provacateur_new_ui_frontend_1 --tail 50 2>/dev/null || log "WARN" "No frontend logs available"
    fi
    
    log "INFO" "Frontend testing completed"
    return 0
}

# Function to run API tests
run_api_tests() {
    print_section "Running API Tests"
    
    # Test frontend
    test_frontend
    if [ $? -ne 0 ]; then
        log "ERROR" "Frontend testing failed"
        return 1
    fi
    
    # Test backend
    test_backend
    if [ $? -ne 0 ]; then
        log "ERROR" "Backend testing failed"
        return 1
    fi
    
    # Run the API test suite with retries
    log "INFO" "Running API test suite..."
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        response=$(curl -s http://localhost:3001/api-test-runner)
        if [[ $response != *"Error response"* ]]; then
            log "INFO" "API test suite completed successfully"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            log "WARN" "API test suite failed, retrying in 5 seconds..."
            sleep 5
        fi
    done
    
    log "ERROR" "API test suite failed after $max_retries attempts: $response"
    return 1
}

# Function to check service dependencies
check_dependencies() {
    print_section "Checking Service Dependencies"
    
    # Check Redis
    if check_port 4003 "Redis"; then
        log "INFO" "Redis is running"
    else
        log "ERROR" "Redis is not running"
    fi
    
    # Check Ollama
    if check_port 7111 "Ollama"; then
        log "INFO" "Ollama is running"
    else
        log "WARN" "Ollama is not running (optional)"
    fi
    
    # Check Grafana
    if check_port 3111 "Grafana"; then
        log "INFO" "Grafana is running"
    else
        log "WARN" "Grafana is not running (optional)"
    fi
    
    # Check Prometheus
    if check_port 9111 "Prometheus"; then
        log "INFO" "Prometheus is running"
    else
        log "WARN" "Prometheus is not running (optional)"
    fi
}

# Function to check container status
check_container_status() {
    print_section "Checking Container Status"
    
    # Get container status
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman ps -a
    else
        docker ps -a
    fi
}

# Function to check logs
check_logs() {
    print_section "Checking Container Logs"
    
    # Check frontend logs
    log "INFO" "Checking frontend logs..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman logs agent_provacateur_new_ui_frontend_1 --tail 50 2>/dev/null || log "WARN" "No frontend logs available"
    else
        docker logs agent_provacateur_new_ui_frontend_1 --tail 50 2>/dev/null || log "WARN" "No frontend logs available"
    fi
    
    # Check backend logs
    log "INFO" "Checking backend logs..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman logs agent_provacateur_new_ui_mcp-server_1 --tail 50 2>/dev/null || log "WARN" "No backend logs available"
    else
        docker logs agent_provacateur_new_ui_mcp-server_1 --tail 50 2>/dev/null || log "WARN" "No backend logs available"
    fi
}

# Function to check network connectivity
check_network() {
    print_section "Checking Network Connectivity"
    
    # Check internal network
    log "INFO" "Checking internal network..."
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman network ls | grep agent_provacateur_new_ui_default || log "WARN" "Network not found"
    else
        docker network ls | grep agent_provacateur_new_ui_default || log "WARN" "Network not found"
    fi
    
    # Check container communication with retries
    log "INFO" "Testing container communication..."
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if [ "$CONTAINER_ENGINE" = "podman" ]; then
            if podman exec agent_provacateur_new_ui_frontend_1 curl -s http://mcp-server:8000/api/health > /dev/null 2>&1; then
                log "INFO" "Container communication successful"
                return 0
            fi
        else
            if docker exec agent_provacateur_new_ui_frontend_1 curl -s http://mcp-server:8000/api/health > /dev/null 2>&1; then
                log "INFO" "Container communication successful"
                return 0
            fi
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            log "WARN" "Container communication failed, retrying in 5 seconds..."
            sleep 5
        fi
    done
    
    log "ERROR" "Container communication failed after $max_retries attempts"
    return 1
}

# Function to check resource usage
check_resources() {
    print_section "Checking Resource Usage"
    
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman stats --no-stream 2>/dev/null || log "WARN" "Resource stats not available"
    else
        docker stats --no-stream 2>/dev/null || log "WARN" "Resource stats not available"
    fi
}

# Main function
main() {
    # Initialize debug log
    echo "=== Debug Runner Log ===" > $DEBUG_LOG
    echo "Started at: $TIMESTAMP" >> $DEBUG_LOG
    
    # Detect container engine
    if command -v podman &> /dev/null; then
        CONTAINER_ENGINE="podman"
        COMPOSE_CMD="podman-compose"
    elif command -v docker &> /dev/null; then
        CONTAINER_ENGINE="docker"
        COMPOSE_CMD="docker-compose"
    else
        log "ERROR" "Neither Docker nor Podman is installed"
        exit 1
    fi
    
    log "INFO" "Using container engine: $CONTAINER_ENGINE"
    
    # Parse command line arguments
    case "$1" in
        "start")
            cleanup
            start_services
            check_dependencies
            check_container_status
            check_network
            check_resources
            check_logs
            run_api_tests
            ;;
        "stop")
            cleanup
            ;;
        "test")
            check_dependencies
            check_container_status
            check_network
            check_resources
            check_logs
            run_api_tests
            ;;
        "cleanup")
            cleanup
            ;;
        "test-frontend")
            test_frontend
            ;;
        "test-backend")
            test_backend
            ;;
        "test-redis")
            test_redis
            ;;
        "test-ollama")
            test_ollama
            ;;
        "test-grafana")
            test_grafana
            ;;
        "test-prometheus")
            test_prometheus
            ;;
        *)
            echo "Usage: $0 {start|stop|test|cleanup|test-frontend|test-backend|test-redis|test-ollama|test-grafana|test-prometheus}"
            echo "  start          - Clean up, start services, and run tests"
            echo "  stop           - Stop and clean up all services"
            echo "  test           - Run tests on existing services"
            echo "  cleanup        - Clean up all containers and networks"
            echo "  test-frontend  - Test frontend services only"
            echo "  test-backend   - Test backend services only"
            echo "  test-redis     - Test Redis connection only"
            echo "  test-ollama    - Test Ollama connection only"
            echo "  test-grafana   - Test Grafana connection only"
            echo "  test-prometheus - Test Prometheus connection only"
            exit 1
            ;;
    esac
    
    print_section "Debug Summary"
    echo "Debug log available at: $DEBUG_LOG"
}

# Run the main function
main "$@" 