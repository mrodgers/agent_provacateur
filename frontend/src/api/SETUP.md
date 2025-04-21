# API Client Integration Guide

This guide explains how to integrate the new API client into the existing frontend JavaScript files.

## Step 1: Import the API Client

Add this import to your JavaScript file:

```javascript
// Import the full API
import api from '../src/api/api';

// Or import specific modules for better performance
import { documentApi } from '../src/api/documentApi';
import { taskApi } from '../src/api/taskApi';
```

## Step 2: Replace Direct Fetch Calls

### Before:

```javascript
async function loadDocuments() {
  try {
    const response = await fetch(`${window.BACKEND_URL}/documents`);
    if (!response.ok) {
      throw new Error(`Failed to fetch documents: ${response.status}`);
    }
    const documents = await response.json();
    return documents;
  } catch (error) {
    console.error('Error loading documents:', error);
    throw error;
  }
}
```

### After:

```javascript
async function loadDocuments() {
  try {
    const documents = await api.documents.getAllDocuments();
    return documents;
  } catch (error) {
    console.error('Error loading documents:', error);
    throw error;
  }
}
```

## Step 3: Replace Document Operations

### Document Retrieval

Before:
```javascript
const response = await fetch(`${window.BACKEND_URL}/documents/${documentId}`);
const document = await response.json();
```

After:
```javascript
const document = await api.documents.getDocumentById(documentId);
```

### Document Content

Before:
```javascript
const response = await fetch(`${window.BACKEND_URL}/documents/${documentId}/xml/content`);
const content = await response.text();
```

After:
```javascript
const content = await api.documents.getDocumentXmlContent(documentId);
```

### File Upload

Before:
```javascript
const formData = new FormData();
formData.append('file', fileObject);
formData.append('title', title);

const response = await fetch(`${window.BACKEND_URL}/xml/upload`, {
  method: 'POST',
  body: formData
});
const result = await response.json();
```

After:
```javascript
const result = await api.documents.uploadDocument({
  file: fileObject,
  title: title
});
```

## Step 4: Replace Task Processing

### Entity Extraction

Before:
```javascript
const response = await fetch(`${window.BACKEND_URL}/task`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    task_id: `task_${Date.now()}`,
    source_agent: 'frontend',
    target_agent: 'xml_agent',
    intent: 'extract_entities',
    payload: { doc_id: documentId }
  })
});
const result = await response.json();
```

After:
```javascript
const result = await api.tasks.extractEntities(documentId);
```

## Step 5: Handle Errors Consistently

```javascript
import { formatApiError } from '../src/api/utils';

try {
  const documents = await api.documents.getAllDocuments();
  displayDocuments(documents);
} catch (error) {
  const formattedError = formatApiError(error, 'Failed to load documents');
  showErrorMessage(formattedError.message);
}
```

## Example Integration with document_viewer.js

```javascript
// Add to the top of document_viewer.js:
import api from '../src/api/api';
import { formatApiError, formatXmlForDisplay } from '../src/api/utils';

// Then replace the loadDocument function:
async function loadDocument(docId) {
  const documentViewer = document.getElementById('documentViewer');
  
  try {
    // Show loading state
    documentViewer.innerHTML = '<p>Loading document...</p>';
    addSupervisorMessage(`I'm loading document "${docId}" for analysis...`);
    
    // Get document info and content in parallel
    const [docInfo, xmlContent] = await Promise.all([
      api.documents.getDocumentById(docId),
      api.documents.getDocumentXmlContent(docId)
    ]);
    
    // Format and display the XML
    const formattedXml = formatXmlForDisplay(xmlContent);
    documentViewer.innerHTML = `
      <pre class="language-xml" style="max-height: 400px; overflow: auto; white-space: pre-wrap; word-wrap: break-word; tab-size: 2;"><code>${formattedXml}</code></pre>
    `;
    
    // Apply syntax highlighting
    Prism.highlightAllUnder(documentViewer);
    
    // Get researchable nodes
    let nodes = [];
    try {
      nodes = await api.documents.getDocumentNodes(docId);
    } catch (nodeError) {
      console.error("Error fetching researchable nodes:", nodeError);
    }
    
    // Continue with remaining functionality...
    
  } catch (error) {
    const formattedError = formatApiError(error, `Error loading document ${docId}`);
    documentViewer.innerHTML = `<p class="text-red-500">Error: ${formattedError.message}</p>`;
    addSupervisorMessage(`I encountered an error: ${formattedError.message}`);
  }
}
```

## Next Steps

1. Update all fetch calls in the following files:
   - `landing.js`
   - `document_viewer.js`
   - `agent_management.js`

2. Add error handling with `formatApiError`

3. Run tests with the `runApiTests()` function in the browser console