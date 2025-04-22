/**
 * API Client Example Usage
 * 
 * This file demonstrates how to use the Agent Provocateur API client.
 * It's meant as an example and documentation, not to be used in production.
 */

// Import the main API client
import api from './api';

// Example: Initializing the application with the API client
async function initializeApp() {
  try {
    // Check system health and connection
    const healthResult = await api.healthCheck();
    console.log('System health:', healthResult);
    
    // Get all documents
    const documents = await api.documents.getAllDocuments();
    console.log('Available documents:', documents);
    
    return {
      ready: true,
      documents
    };
  } catch (error) {
    console.error('Failed to initialize:', error);
    return {
      ready: false,
      error
    };
  }
}

// Example: Document workflow
async function documentWorkflow(documentId) {
  try {
    // Step 1: Get document details
    const documentDetails = await api.documents.getDocumentById(documentId);
    console.log('Document details:', documentDetails);
    
    // Step 2: Get document XML content
    const xmlContent = await api.documents.getDocumentXmlContent(documentId);
    
    // Step 3: Extract entities from the document
    const extractionTask = await api.tasks.extractEntities(documentId);
    console.log('Entity extraction task started:', extractionTask);
    
    // Step 4: Poll for task completion
    const taskId = extractionTask.task_id;
    let taskComplete = false;
    let taskResult = null;
    
    while (!taskComplete) {
      // Wait a short time between polls
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Check task status
      const status = await api.tasks.getTaskStatus(taskId);
      console.log('Task status:', status);
      
      if (status.status === 'completed') {
        taskComplete = true;
        taskResult = await api.tasks.getTaskResult(taskId);
      } else if (status.status === 'failed') {
        throw new Error(`Task failed: ${status.error || 'Unknown error'}`);
      }
    }
    
    console.log('Task result:', taskResult);
    return taskResult;
  } catch (error) {
    console.error('Document workflow error:', error);
    throw error;
  }
}

// Example: Upload a new document
async function uploadDocument(file, title) {
  try {
    const result = await api.documents.uploadDocument({
      file,
      title: title || file.name
    });
    
    console.log('Upload result:', result);
    return result;
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
}

// Example: Agent management
async function manageAgents() {
  try {
    // Get all agents
    const agentData = await api.agents.getAllAgents();
    console.log('Agent data:', agentData);
    
    // Find inactive agents
    const inactiveAgents = agentData.agents.filter(agent => agent.status !== 'active');
    
    // Start inactive agents
    for (const agent of inactiveAgents) {
      console.log(`Starting agent ${agent.id}...`);
      await api.agents.startAgent(agent.id);
    }
    
    // Get updated agent status
    const updatedAgentData = await api.agents.getAllAgents();
    console.log('Updated agent data:', updatedAgentData);
    
    return updatedAgentData;
  } catch (error) {
    console.error('Agent management error:', error);
    throw error;
  }
}

// Export example functions
export {
  initializeApp,
  documentWorkflow,
  uploadDocument,
  manageAgents
};

// Usage example (commented out)
/*
document.addEventListener('DOMContentLoaded', async () => {
  // Initialize the application
  const initResult = await initializeApp();
  
  if (initResult.ready) {
    console.log('App initialized with documents:', initResult.documents);
    
    // Set up event listeners for file upload
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
      uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById('fileUpload');
        const titleInput = document.getElementById('documentTitle');
        
        if (fileInput.files.length > 0) {
          const result = await uploadDocument(
            fileInput.files[0],
            titleInput.value
          );
          
          if (result.doc_id) {
            alert(`Document uploaded successfully: ${result.doc_id}`);
          }
        }
      });
    }
    
    // Handle document processing
    const processBtn = document.getElementById('processDocumentBtn');
    if (processBtn) {
      processBtn.addEventListener('click', async () => {
        const documentId = document.getElementById('documentSelect').value;
        if (documentId) {
          const result = await documentWorkflow(documentId);
          displayResults(result);
        }
      });
    }
    
    // Handle agent management
    const agentBtn = document.getElementById('manageAgentsBtn');
    if (agentBtn) {
      agentBtn.addEventListener('click', async () => {
        const result = await manageAgents();
        displayAgentStatus(result);
      });
    }
  } else {
    console.error('Failed to initialize app:', initResult.error);
    document.getElementById('errorDisplay').textContent = 
      'Failed to connect to the backend. Please check the server status.';
  }
});

// Helper functions for displaying results
function displayResults(result) {
  const container = document.getElementById('resultsContainer');
  if (!container) return;
  
  if (result.entities && result.entities.length > 0) {
    let html = '<h3>Extracted Entities</h3><ul>';
    result.entities.forEach(entity => {
      html += `<li><strong>${entity.name}</strong> (${Math.round((entity.confidence || 0) * 100)}%)</li>`;
    });
    html += '</ul>';
    container.innerHTML = html;
  } else {
    container.innerHTML = '<p>No entities found.</p>';
  }
}

function displayAgentStatus(agentData) {
  const container = document.getElementById('agentContainer');
  if (!container) return;
  
  let html = `
    <h3>Agent Status</h3>
    <p>Total Agents: ${agentData.totalAgents}</p>
    <p>Active Agents: ${agentData.activeAgents}</p>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Status</th>
          <th>Type</th>
        </tr>
      </thead>
      <tbody>
  `;
  
  agentData.agents.forEach(agent => {
    html += `
      <tr>
        <td>${agent.id}</td>
        <td>${agent.name}</td>
        <td>${agent.status}</td>
        <td>${agent.type}</td>
      </tr>
    `;
  });
  
  html += '</tbody></table>';
  container.innerHTML = html;
}
*/