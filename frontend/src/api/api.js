/**
 * Agent Provocateur API
 * 
 * Main export for all API modules
 */

import { apiClient } from './index';
import { documentApi } from './documentApi';
import { taskApi } from './taskApi';
import { agentApi } from './agentApi';
import { sourceApi } from './sourceApi';

// Export a combined API object with all modules
const api = {
  client: apiClient,
  documents: documentApi,
  tasks: taskApi,
  agents: agentApi,
  sources: sourceApi,
  
  // Initialize the API with configuration
  initialize(config = {}) {
    if (window.apLogger?.info) {
      window.apLogger.info('Initializing Agent Provocateur API client', config);
    }
    
    // Could handle any global initialization here
    return this;
  },
  
  // System-wide endpoints
  async getSystemInfo() {
    return apiClient.get('/api/info');
  },
  
  async healthCheck() {
    return apiClient.get('/api/health');
  }
};

// Make API globally available for debugging
if (typeof window !== 'undefined') {
  window.apApi = api;
}

export {
  apiClient,
  documentApi,
  taskApi,
  agentApi,
  sourceApi
};

export default api;