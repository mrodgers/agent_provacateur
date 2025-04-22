/**
 * Core API Client for Agent Provocateur
 * Provides a standardized way to interact with the backend API
 */

// Create namespace for API
window.APApi = window.APApi || {};

/**
 * Create API client with consistent error handling and base URL
 * @param {Object} options - Configuration options
 * @returns {Object} API client methods
 */
function createApiClient(options = {}) {
  const defaults = {
    baseUrl: window.BACKEND_URL || 'http://localhost:8000',
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  };
  
  const config = { ...defaults, ...options };
  
  // Create axios instance
  const client = axios.create({
    baseURL: config.baseUrl,
    timeout: config.timeout,
    headers: config.headers
  });
  
  // Add request interceptor for logging
  client.interceptors.request.use(function (config) {
    if (window.apLogger) {
      window.apLogger.api(`Request: ${config.method.toUpperCase()} ${config.url}`);
    }
    return config;
  }, function (error) {
    if (window.apLogger) {
      window.apLogger.error('Request error:', error);
    }
    return Promise.reject(error);
  });
  
  // Add response interceptor for error handling
  client.interceptors.response.use(function (response) {
    // Any status code between 200 and 299 is a success
    if (window.apLogger) {
      window.apLogger.api(`Response: ${response.status} ${response.config.url}`);
    }
    return response.data;
  }, function (error) {
    // Any status codes outside the range of 2xx
    if (window.apLogger) {
      window.apLogger.error('API Error:', error);
    }
    
    // Format the error using the error handler if available
    if (window.errorHandler) {
      const formattedError = window.errorHandler.formatApiError(error);
      return Promise.reject(formattedError);
    }
    
    return Promise.reject(error);
  });
  
  /**
   * Perform a GET request
   * @param {string} url - URL to request
   * @param {Object} params - URL parameters
   * @param {Object} options - Additional axios options
   * @returns {Promise} - API response
   */
  async function get(url, params = {}, options = {}) {
    try {
      return await client.get(url, { 
        params, 
        ...options 
      });
    } catch (error) {
      handleApiError(error, 'GET', url);
      throw error;
    }
  }
  
  /**
   * Perform a POST request
   * @param {string} url - URL to request
   * @param {Object} data - Request body
   * @param {Object} options - Additional axios options
   * @returns {Promise} - API response
   */
  async function post(url, data = {}, options = {}) {
    try {
      return await client.post(url, data, options);
    } catch (error) {
      handleApiError(error, 'POST', url);
      throw error;
    }
  }
  
  /**
   * Perform a PUT request
   * @param {string} url - URL to request
   * @param {Object} data - Request body
   * @param {Object} options - Additional axios options
   * @returns {Promise} - API response
   */
  async function put(url, data = {}, options = {}) {
    try {
      return await client.put(url, data, options);
    } catch (error) {
      handleApiError(error, 'PUT', url);
      throw error;
    }
  }
  
  /**
   * Perform a DELETE request
   * @param {string} url - URL to request
   * @param {Object} options - Additional axios options
   * @returns {Promise} - API response
   */
  async function del(url, options = {}) {
    try {
      return await client.delete(url, options);
    } catch (error) {
      handleApiError(error, 'DELETE', url);
      throw error;
    }
  }
  
  /**
   * Handle API errors consistently
   * @param {Error} error - Error object
   * @param {string} method - HTTP method
   * @param {string} url - Request URL
   */
  function handleApiError(error, method, url) {
    // Log the error
    if (window.apLogger) {
      window.apLogger.error(`API ${method} ${url} failed:`, error);
    }
    
    // Check if we want to display the error globally
    if (config.displayGlobalErrors) {
      if (window.errorHandler && window.errorHandler.displayError) {
        const formattedError = window.errorHandler.formatApiError(error);
        window.errorHandler.displayError(
          formattedError.message,
          'error-container',
          {
            title: `API Error (${method} ${url})`,
            details: JSON.stringify(formattedError.details, null, 2)
          }
        );
      }
    }
  }
  
  /**
   * Upload a file
   * @param {string} url - URL to upload to
   * @param {File} file - File to upload
   * @param {Object} additionalData - Additional form data
   * @param {function} progressCallback - Progress callback
   * @returns {Promise} - API response
   */
  async function uploadFile(url, file, additionalData = {}, progressCallback = null) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Add additional data to form
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
      
      const options = {};
      
      // Add progress handler if provided
      if (progressCallback && typeof progressCallback === 'function') {
        options.onUploadProgress = (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          progressCallback(percentCompleted, progressEvent);
        };
      }
      
      return await client.post(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        ...options
      });
    } catch (error) {
      handleApiError(error, 'UPLOAD', url);
      throw error;
    }
  }
  
  /**
   * Check if API is available
   * @returns {Promise<boolean>} - True if API is available
   */
  async function checkHealth() {
    try {
      const response = await client.get('/health');
      return response.status === 'ok';
    } catch (error) {
      if (window.apLogger) {
        window.apLogger.warn('Health check failed:', error);
      }
      return false;
    }
  }
  
  /**
   * Create a resource API for a specific endpoint
   * @param {string} endpoint - API endpoint
   * @returns {Object} - Resource API
   */
  function createResourceApi(endpoint) {
    return {
      getAll: (params = {}) => get(`/${endpoint}`, params),
      getById: (id) => get(`/${endpoint}/${id}`),
      create: (data) => post(`/${endpoint}`, data),
      update: (id, data) => put(`/${endpoint}/${id}`, data),
      delete: (id) => del(`/${endpoint}/${id}`)
    };
  }
  
  // Return the API client
  return {
    get,
    post,
    put,
    delete: del,
    uploadFile,
    checkHealth,
    createResourceApi,
    client // Expose the axios instance for advanced usage
  };
}

// Create default API client
window.APApi.createClient = createApiClient;
window.APApi.client = createApiClient();

// Create resource APIs
window.APApi.documents = window.APApi.client.createResourceApi('documents');
window.APApi.agents = window.APApi.client.createResourceApi('agents');
window.APApi.tasks = window.APApi.client.createResourceApi('tasks');