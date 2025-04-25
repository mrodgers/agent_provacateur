# Port Management System

## Overview
The port management system provides a flexible and maintainable way to handle service ports in the Agent Provocateur application. It distinguishes between core services required for basic functionality and optional services that enhance the application's capabilities.

## Core Services (Required)
These services are essential for the basic functionality of the application:

| Service | Port | Description | Container |
|---------|------|-------------|-----------|
| Frontend UI | 3001 | Main web interface | `frontend` |
| MCP Server | 8111 | Backend API server | `mcp-server` |
| Redis | 6111 | Caching and message broker | `redis` |

## Optional Services
These services provide additional functionality but are not required for basic operation:

| Service | Port | Description | Container | Required For |
|---------|------|-------------|-----------|--------------|
| Ollama | 7111 | LLM service | `ollama` | Advanced AI features |
| Entity Detector | 8082 | Entity extraction | `entity-detector` | Document analysis |
| Web Search | 8083 | Web search capabilities | `web-search` | External data integration |
| GraphRAG | 8084 | Graph-based RAG | `graphrag` | Advanced document processing |
| Grafana | 3111 | Monitoring dashboard | `grafana` | System monitoring |
| Prometheus | 9111 | Metrics collection | `prometheus` | System monitoring |
| Pushgateway | 9091 | Metrics push endpoint | `pushgateway` | System monitoring |

## Implementation Details

### Port Checking Logic
The system uses a two-tier approach to port checking:

1. **Core Port Check**
   - Verifies essential services are running
   - Fails tests if core ports are not available
   - Uses socket connection checks for reliability

2. **Optional Port Check**
   - Logs status of optional services
   - Doesn't fail tests for missing optional services
   - Can be configured to require specific optional services

### Configuration
Port requirements can be configured through:

1. Environment Variables
   ```bash
   FRONTEND_PORT=3001
   MCP_SERVER_PORT=8111
   REDIS_PORT=6111
   ```

2. Docker Compose
   ```yaml
   services:
     frontend:
       ports:
         - "3001:3001"
     mcp-server:
       ports:
         - "8111:8000"
     redis:
       ports:
         - "6111:6379"
   ```

3. API Configuration
   ```javascript
   const API_BASE_URL = window.BACKEND_URL || 'http://localhost:8111';
   ```

## Testing

### API Test Runner
The API test runner verifies port availability in two ways:

1. **Core Port Verification**
   ```javascript
   const corePorts = {
     3001: 'Frontend UI',
     [backendPort]: 'MCP Server API',
     6111: 'Redis'
   };
   ```

2. **Optional Port Logging**
   ```javascript
   const optionalPorts = {
     7111: 'Ollama',
     8082: 'Entity Detector MCP',
     // ...
   };
   ```

### Health Checks
Each service implements health checks that verify:
- Port availability
- Service responsiveness
- Basic functionality

## Containerization Considerations

### Current Setup
- Core services are containerized
- Frontend server runs locally for development
- Optional services can be started as needed

### Potential Improvements
1. **Frontend Containerization**
   Pros:
   - Consistent environment
   - Easier deployment
   - Better isolation
   
   Cons:
   - More complex development workflow
   - Additional resource usage
   - Potential performance impact

2. **Development vs Production**
   - Development: Local frontend for faster iteration
   - Production: Fully containerized for consistency

## Best Practices

1. **Port Management**
   - Use environment variables for configuration
   - Document all port assignments
   - Implement health checks
   - Use service discovery when possible

2. **Testing**
   - Test core functionality without optional services
   - Implement graceful degradation
   - Log service availability
   - Monitor port conflicts

3. **Development**
   - Use consistent port ranges
   - Document port requirements
   - Implement port conflict detection
   - Provide clear error messages

## Future Improvements

1. **Service Discovery**
   - Implement dynamic port assignment
   - Use service registry
   - Automate port conflict resolution

2. **Monitoring**
   - Add port availability metrics
   - Implement automatic recovery
   - Add port usage analytics

3. **Documentation**
   - Add port usage diagrams
   - Document service dependencies
   - Create troubleshooting guides

## Conclusion
The current port management system provides a good balance between flexibility and reliability. While containerizing the frontend server could provide benefits, the current setup allows for faster development iteration. The decision to containerize the frontend should be based on specific deployment requirements and development workflow preferences. 