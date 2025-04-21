/**
 * Agent Provocateur API Client
 * 
 * Core client for interacting with the backend API endpoints
 */

// Configure base client with defaults
const API_BASE_URL = window.BACKEND_URL || 'http://localhost:8000';

/**
 * Base client for making API requests
 */
export const apiClient = {
  /**
   * Make a GET request to the API
   * @param {string} endpoint - API endpoint path
   * @param {Object} params - URL parameters
   * @returns {Promise<Object>} - Response data
   */
  async get(endpoint, params = {}) {
    try {
      // Build URL with query parameters
      const url = new URL(`${API_BASE_URL}${endpoint}`);
      Object.keys(params).forEach(key => {
        url.searchParams.append(key, params[key]);
      });
      
      // Log API call if debugging is enabled
      if (window.apLogger?.api) {
        window.apLogger.api(`GET ${url.toString()}`, params);
      }
      
      // Make the request
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });
      
      // Handle non-2xx responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ 
          error: 'Unknown error',
          message: response.statusText
        }));
        
        throw new Error(errorData.message || `API error: ${response.status} ${response.statusText}`);
      }
      
      // Parse and return JSON response
      const data = await response.json();
      return data;
    } catch (error) {
      // Log error if logger is available
      if (window.apLogger?.error) {
        window.apLogger.error(`API GET error for ${endpoint}:`, error);
      } else {
        console.error(`API GET error for ${endpoint}:`, error);
      }
      
      // Re-throw for handling by caller
      throw error;
    }
  },
  
  /**
   * Make a POST request to the API
   * @param {string} endpoint - API endpoint path
   * @param {Object} data - Request payload
   * @returns {Promise<Object>} - Response data
   */
  async post(endpoint, data = {}) {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      
      // Log API call if debugging is enabled
      if (window.apLogger?.api) {
        window.apLogger.api(`POST ${url}`, { payload: data });
      }
      
      // Make the request
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      // Handle non-2xx responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ 
          error: 'Unknown error',
          message: response.statusText
        }));
        
        throw new Error(errorData.message || `API error: ${response.status} ${response.statusText}`);
      }
      
      // Parse and return JSON response
      const responseData = await response.json();
      return responseData;
    } catch (error) {
      // Log error if logger is available
      if (window.apLogger?.error) {
        window.apLogger.error(`API POST error for ${endpoint}:`, error);
      } else {
        console.error(`API POST error for ${endpoint}:`, error);
      }
      
      // Re-throw for handling by caller
      throw error;
    }
  },
  
  /**
   * Upload a file to the API
   * @param {string} endpoint - API endpoint path
   * @param {FormData} formData - Form data with file
   * @returns {Promise<Object>} - Response data
   */
  async uploadFile(endpoint, formData) {
    try {
      const url = `${API_BASE_URL}${endpoint}`;
      
      // Log API call if debugging is enabled
      if (window.apLogger?.api) {
        window.apLogger.api(`FILE UPLOAD ${url}`, { 
          fileCount: formData.getAll('file').length,
          fileName: formData.get('file')?.name
        });
      }
      
      // Make the request without Content-Type header (browser sets it with boundary)
      const response = await fetch(url, {
        method: 'POST',
        body: formData
      });
      
      // Handle non-2xx responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ 
          error: 'Unknown error',
          message: response.statusText
        }));
        
        throw new Error(errorData.message || `API error: ${response.status} ${response.statusText}`);
      }
      
      // Parse and return JSON response
      const responseData = await response.json();
      return responseData;
    } catch (error) {
      // Log error if logger is available
      if (window.apLogger?.error) {
        window.apLogger.error(`API upload error for ${endpoint}:`, error);
      } else {
        console.error(`API upload error for ${endpoint}:`, error);
      }
      
      // Re-throw for handling by caller
      throw error;
    }
  }
};

export default apiClient;