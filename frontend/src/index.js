/**
 * Agent Provocateur Frontend
 * 
 * This is the main entry point for the frontend application.
 * It exports the API clients and utilities.
 */

// Import API modules
import api from './api/api';
import { 
  apiClient,
  documentApi,
  taskApi,
  agentApi,
  sourceApi
} from './api/api';

// Import utilities
import apiUtils from './api/utils';

// Export all API modules and utilities
export {
  api,
  apiClient,
  documentApi,
  taskApi,
  agentApi,
  sourceApi,
  apiUtils
};

// Export default API
export default api;

// Make API available globally for debugging
if (typeof window !== 'undefined') {
  window.apApi = api;
  
  // Log initialization if logger is available
  if (window.apLogger?.info) {
    window.apLogger.info('Agent Provocateur API client initialized');
  }
}