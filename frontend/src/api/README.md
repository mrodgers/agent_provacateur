# Agent Provocateur API Client

This directory contains the API client modules for communicating with the Agent Provocateur backend.

## Implementation Status

✅ **Phase 1: Core Document API Client** (Complete)
- Base API client with error handling and utilities
- Document API module for all document operations
- Task API module for processing documents
- Agent API module for managing agents
- Source API module for source attribution
- Comprehensive documentation and examples
- Test utilities

🟡 **Phase 2: UI Integration** (Next Steps)
- Replace direct fetch calls in landing.js
- Replace fetch calls in document_viewer.js
- Replace fetch calls in agent_management.js
- Add proper error handling throughout
- Add loading states and progress indicators

🟡 **Phase 3: Backend Integration** (Requires Backend Work)
- Ensure API endpoints match client expectations
- Test with real backend implementation
- Implement proper error responses
- Add pagination and filtering support

## Directory Contents

- `index.js` - Base API client for making requests
- `api.js` - Main export with all API modules
- `documentApi.js` - Document management endpoints
- `taskApi.js` - Document processing endpoints
- `agentApi.js` - Agent management endpoints
- `sourceApi.js` - Source attribution endpoints
- `utils.js` - Utility functions for API operations
- `example.js` - Example usage of the API client
- `test.js` - Simple test utilities
- `SETUP.md` - Integration guide for existing code
- `README.md` - This file

## Documentation

See the comprehensive [API Client Guide](../../../docs/development/api_client_guide.md) for detailed documentation.

## Integration

See the [SETUP.md](./SETUP.md) file for instructions on integrating the API client into existing code.

## Usage Example

```javascript
import api from './api';

// Get all documents
const documents = await api.documents.getAllDocuments();

// Extract entities from a document
const task = await api.tasks.extractEntities('doc_123');

// Get task result
const result = await api.tasks.getTaskResult(task.task_id);

// Get agent information
const agents = await api.agents.getAllAgents();
```

## Testing

Run the tests in the browser console:

```javascript
// First, import the API client
import api from './api/api';
import { runApiTests } from './api/test';

// Then run the tests
const results = await runApiTests();
console.log(`Tests: ${results.passed} passed, ${results.failed} failed`);
```