# Agent Provocateur API Client Guide

This guide documents the frontend API client implementation, which provides a clean interface for interacting with the Agent Provocateur backend services.

## Overview

The API client is organized into modules:

- **Base Client** (`apiClient`): Core request handling functionality
- **Document API** (`documentApi`): Document management endpoints
- **Task API** (`taskApi`): Document processing and entity extraction
- **Agent API** (`agentApi`): Agent management and monitoring
- **Source API** (`sourceApi`): Source attribution and validation

## Installation

The API client is part of the frontend codebase:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run start:dev
```

### Browser Usage

The API client is automatically included in all pages via:

```html
<script src="/static/js/api-browser.js"></script>
```

This makes the API available globally as `window.apApi` with all modules also accessible as global variables:

```javascript
// Access the API directly in browser console
apApi.documents.getAllDocuments().then(docs => console.log(docs));

// Individual modules are also available
documentApi.getDocumentById('doc123').then(doc => console.log(doc));
```

## Usage

### Basic Usage

```javascript
// Import the full API
import api from '../src/api/api';

// Use different API modules
const documents = await api.documents.getAllDocuments();
const agents = await api.agents.getAllAgents();
```

### Importing Specific Modules

```javascript
// Import specific API modules for better tree-shaking
import { documentApi } from '../src/api/documentApi';
import { taskApi } from '../src/api/taskApi';

// Use the modules directly
const document = await documentApi.getDocumentById('doc_123');
const result = await taskApi.extractEntities('doc_123');
```

## API Modules

### Document API

Handles document management operations:

```javascript
// Get all documents
const documents = await documentApi.getAllDocuments();

// Get document details
const document = await documentApi.getDocumentById('doc_123');

// Get document XML content
const xmlContent = await documentApi.getDocumentXmlContent('doc_123');

// Get document nodes (structure)
const nodes = await documentApi.getDocumentNodes('doc_123');

// Upload a document
const result = await documentApi.uploadDocument({
  file: fileObject,
  title: 'Document Title'
});

// Search documents
const searchResults = await documentApi.searchDocuments('keyword', {
  page: 1,
  limit: 10
});
```

### Task API

Handles document processing tasks:

```javascript
// Create a custom task
const task = await taskApi.createTask({
  intent: 'extract_entities',
  target_agent: 'xml_agent',
  payload: {
    doc_id: 'doc_123'
  }
});

// Extract entities from a document
const extraction = await taskApi.extractEntities('doc_123');

// Research entities in a document
const research = await taskApi.researchEntities('doc_123', {
  use_web_search: true,
  search_provider: 'brave'
});

// Validate document structure
const validation = await taskApi.validateStructure('doc_123');

// Create verification plan
const verificationPlan = await taskApi.createVerificationPlan('doc_123');

// Get task status
const status = await taskApi.getTaskStatus('task_123');

// Get task result
const result = await taskApi.getTaskResult('task_123');
```

### Agent API

Handles agent management:

```javascript
// Get all agents
const agents = await agentApi.getAllAgents();

// Get agent details
const agent = await agentApi.getAgentById('agent_123');

// Start an agent
await agentApi.startAgent('agent_123');

// Stop an agent
await agentApi.stopAgent('agent_123');

// Get agent logs
const logs = await agentApi.getAgentLogs('agent_123', {
  limit: 100,
  level: 'error'
});

// Get agent configuration
const config = await agentApi.getAgentConfig('agent_123');

// Update agent configuration
await agentApi.updateAgentConfig('agent_123', {
  web_search_enabled: true,
  max_tasks: 5
});

// Get system health
const health = await agentApi.getSystemHealth();
```

### Source API

Handles source attribution:

```javascript
// Get available source types
const sourceTypes = await sourceApi.getSourceTypes();

// Get source details
const source = await sourceApi.getSourceById('source_123');

// Validate a source
const validation = await sourceApi.validateSource({
  url: 'https://example.com',
  title: 'Example Source'
});

// Get sources for an entity
const sources = await sourceApi.getEntitySources('entity_123');

// Get citation for a source
const citation = await sourceApi.getSourceCitation('source_123', 'apa');
```

## Error Handling

The API client provides consistent error handling:

```javascript
import { formatApiError } from '../src/api/utils';

try {
  const document = await documentApi.getDocumentById('doc_123');
  // Process document...
} catch (error) {
  // Format the error for display
  const formattedError = formatApiError(error, 'Failed to load document');
  
  // Log the error
  console.error('Document error:', formattedError);
  
  // Display to user
  showError(formattedError.message);
}
```

## Utilities

The API client includes utility functions:

```javascript
import { 
  formatApiError,
  withPagination,
  parseBackendStatus,
  formatXmlForDisplay
} from '../src/api/utils';

// Add pagination to requests
const params = withPagination({
  type: 'xml'
}, {
  page: 2,
  limit: 10
});

// Parse backend status from response
const backendStatus = parseBackendStatus(response);
if (!backendStatus.available) {
  showOfflineMessage();
}

// Format XML for display
const formattedXml = formatXmlForDisplay(rawXml);
```

## Complete Example

Here's a complete workflow example:

```javascript
import api from '../src/api/api';
import { formatApiError } from '../src/api/utils';

async function processDocument(documentId) {
  try {
    // Step 1: Get document details
    const document = await api.documents.getDocumentById(documentId);
    console.log(`Processing document: ${document.title}`);
    
    // Step 2: Extract entities
    const extractionTask = await api.tasks.extractEntities(documentId);
    console.log(`Extraction task started: ${extractionTask.task_id}`);
    
    // Step 3: Poll for task completion
    const taskId = extractionTask.task_id;
    let taskComplete = false;
    let taskResult = null;
    
    while (!taskComplete) {
      // Wait between polls
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Check task status
      const status = await api.tasks.getTaskStatus(taskId);
      
      if (status.status === 'completed') {
        taskComplete = true;
        taskResult = await api.tasks.getTaskResult(taskId);
      } else if (status.status === 'failed') {
        throw new Error(`Task failed: ${status.error || 'Unknown error'}`);
      }
    }
    
    // Step 4: Display results
    console.log(`Found ${taskResult.entities.length} entities`);
    return taskResult.entities;
    
  } catch (error) {
    const formattedError = formatApiError(error);
    console.error('Processing error:', formattedError);
    throw formattedError;
  }
}
```

## Implementation Details

The API client is implemented with a focus on:

1. **Consistency**: All API modules follow the same patterns and error handling
2. **Performance**: Batch operations and optimized request handling
3. **Error Handling**: Comprehensive error formatting and reporting
4. **Debugging**: Built-in logging with performance metrics
5. **Extensibility**: Easy to add new endpoints and modules

## Testing

The API client can be tested with:

```javascript
// Test API availability
async function testApiConnection() {
  try {
    const health = await api.healthCheck();
    return health.status === 'ok';
  } catch (error) {
    return false;
  }
}
```