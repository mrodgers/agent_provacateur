# Plan to Replace Simulated Data with Live Data

This document outlines a systematic approach to replacing the simulated/mock data in the frontend with real backend implementations. It provides a prioritized roadmap for backend development to support the frontend features that previously relied on simulated data.

## 1. API Endpoint Implementation Priority

| Feature | Previous State | Required Backend Work | Priority |
|---------|---------------|----------------------|----------|
| Document Listing | Simulated fallback | Implement `/documents` API endpoint | High |
| Entity Extraction | Simulated results | Implement `/task` endpoint for entity processing | High |
| Agent Management | Fully simulated | Create `/agents` endpoints for listing and control | Medium |
| Source Attribution | Mock sources | Implement source retrieval and validation | Medium |
| Verification Plans | Simulated tasks | Create verification plan generation endpoint | Low |

## 2. Detailed Implementation Plan

### Phase 1: Core Document APIs (Week 1) - IN PROGRESS

1. **Document API Enhancements** - ✅ COMPLETED
   - Update `/documents` endpoint to include metadata and status information
   - Implement proper error handling and response codes
   - Add pagination support for large document collections
   - Create document search capability by title/content
   - ✅ Added frontend API client implementation with comprehensive documentation

2. **XML Processing Pipeline** - 🟡 IN PROGRESS
   - Enhance XML parsing with better error handling
   - Implement document validation before processing
   - Add processing status tracking
   - Build proper processing time measurement

3. **Entity Extraction Implementation** - 🟡 IN PROGRESS
   - Create real entity extraction logic in backend
   - Implement confidence scoring based on context
   - Add entity categorization (claims, facts, statements)
   - Support XPath resolution for entity locations

### Phase 2: Agent System & Management (Week 2)

1. **Agent Status API**
   - Implement `/agents` endpoint for listing available agents
   - Create agent status tracking (active, inactive, busy)
   - Add agent performance metrics collection
   - Build agent log access API

2. **Agent Control Interface**
   - Implement start/stop functionality for agents
   - Add configuration management for agent parameters
   - Create agent task queue monitoring
   - Implement agent resource usage tracking

3. **Task Distribution System**
   - Build task assignment logic for document processing
   - Implement priority-based task queue
   - Add task status reporting
   - Create task history tracking

### Phase 3: Source Attribution & Verification (Week 3)

1. **Source Retrieval System**
   - Implement proper source tracking for entities
   - Connect to web search agent for external validation
   - Add source confidence scoring
   - Create source deduplication logic

2. **Verification Workflow**
   - Build verification plan generation for documents
   - Implement verification task assignment to appropriate agents
   - Add progress tracking for verification tasks
   - Create verification report generation

3. **Enhanced Reporting**
   - Implement exportable report format with live data
   - Add downloadable XML with proper source attribution
   - Create JSON report generation with full metadata
   - Build visualization data endpoints for dashboard displays

## 3. Technical Implementation Details

### Backend API Structure

```
/api/
  /documents/
    GET / - List all documents
    GET /{id} - Get document details
    POST /upload - Upload new document
    GET /{id}/xml - Get document XML content
    GET /{id}/nodes - Get document structure
    GET /search - Search documents
  /tasks/
    POST / - Create processing task
    GET /{id} - Get task status
    GET /{id}/result - Get task results
  /agents/
    GET / - List all agents and status
    POST /{id}/start - Start an agent
    POST /{id}/stop - Stop an agent
    GET /{id}/logs - Get agent logs
    GET /{id}/config - Get agent configuration
    PUT /{id}/config - Update agent configuration
  /sources/
    GET / - List available source types
    GET /{id} - Get source details
    POST /validate - Validate a source
    GET /entities/{id}/sources - Get sources for an entity
```

### Frontend API Client Structure

```
src/api/
  index.js         - Base API client
  api.js           - Main API export
  documentApi.js   - Document API endpoints
  taskApi.js       - Task/Processing API endpoints
  agentApi.js      - Agent API endpoints
  sourceApi.js     - Source API endpoints
  utils.js         - API utilities
  example.js       - Usage examples
  testing/
    apiTests.js    - Comprehensive API tests
```

### API Client Browser Version

```
static/js/
  api-browser.js   - Browser-compatible API bundle
  apiTests.js      - Browser test suite
```

See the [API Client Guide](../development/api_client_guide.md) for complete documentation.

### Database Schema Enhancements

1. **Documents Collection**
   - Add processing_status field
   - Add last_processed timestamp
   - Include entity_count for quick reference
   - Add metadata object for custom properties

2. **Entities Collection**
   - Create proper source references
   - Add confidence scoring fields
   - Include context snippets
   - Store XPath location information

3. **Agents Collection**
   - Track status and health metrics
   - Store configuration preferences
   - Include performance statistics
   - Log task history and results

4. **Sources Collection**
   - Store source validation status
   - Include confidence scoring
   - Track usage across entities
   - Store retrieval timestamps

## 4. Testing Strategy

1. **Unit Tests** - ✅ FRONTEND API CLIENT TESTED
   - ✅ Test API client modules independently
   - ✅ Verify data structures match expectations
   - ✅ Ensure proper error handling for edge cases
   - Test performance under load
   - ✅ Created browser-based test runner at `/api-test`

2. **Integration Tests**
   - ✅ Added tests for frontend-backend communication
   - Test agent messaging system
   - Check source attribution workflow
   - Validate end-to-end document processing
   - ✅ Added features to run tests with or without backend dependency

3. **User Acceptance Testing**
   - Create scenarios for common user workflows
   - Test with large document collections
   - Verify performance with concurrent users
   - Validate UI feedback matches backend state
   
See the [API Client Testing Strategy](./api_client_testing.md) document for detailed information on the API client testing approach.

## 5. Implementation Approach

1. ✅ Start with essential API endpoints that remove dependency on simulated data
   - Frontend API client implementation completed
   - API interface fully documented
   
2. ✅ Add proper error handling for each endpoint
   - Comprehensive error handling in frontend API client
   - Consistent error response formats

3. 🟡 Implement real data processing logic to replace simulations
   - Frontend API client ready to connect to real backend
   - Backend implementation in progress

4. 🟡 Enhance frontend with better loading states and error handling
   - API client includes robust error handling
   - UI components need to be updated to use API client

5. 🟡 Add progress indicators for long-running processes
   - Task status tracking API endpoints designed
   - UI implementation pending

6. 🟡 Implement proper backend validation for all inputs
   - API client sends properly formatted requests
   - Backend validation to be implemented

7. Plan for next steps:
   - Create background workers for processing-intensive tasks
   - Add API documentation for each new endpoint

## 6. Backend-Frontend Communication

1. **API Contract**
   - Define consistent response formats for all endpoints
   - Document expected error states and codes
   - Create schema validation for request/response payloads
   - Implement versioning strategy for APIs

2. **Real-time Updates**
   - Add WebSocket support for long-running processes
   - Implement SSE (Server-Sent Events) for status updates
   - Create notification system for completed tasks
   - Add progress reporting for multi-stage processes

3. **Performance Considerations**
   - Implement request throttling for intensive operations
   - Add caching for frequently accessed data
   - Create batch operations for multiple item processing
   - Support pagination and filtering for large datasets

## 7. Security Enhancements

1. **API Security**
   - Add proper authentication for all endpoints
   - Implement rate limiting to prevent abuse
   - Create input validation to prevent injection attacks
   - Add logging for security-relevant operations

2. **Data Protection**
   - Implement proper data sanitization for user inputs
   - Add encryption for sensitive document contents
   - Create access control for document operations
   - Support data redaction for sensitive information

## 8. Monitoring and Operations

1. **System Health**
   - Implement health check endpoints
   - Add performance metrics collection
   - Create alerting for system issues
   - Support diagnostic endpoints for troubleshooting

2. **Operational Tools**
   - Build admin dashboard for system status
   - Add task management for backend processes
   - Create maintenance mode for system updates
   - Implement backup and recovery procedures

By following this implementation plan, we can systematically replace all simulated data with real, live data from the backend. This will improve the application's reliability, functionality, and user experience while ensuring that the system provides accurate information to users.