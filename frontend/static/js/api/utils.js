/**
 * API Utility Functions
 * 
 * Helper functions for API interactions
 */

/**
 * Format error responses from the API
 * @param {Error} error - The caught error
 * @param {string} defaultMessage - Default message if none found
 * @returns {Object} - Formatted error object
 */
export const formatApiError = (error, defaultMessage = 'An error occurred') => {
  // Check if error has a response property (from fetch/axios)
  if (error.response) {
    const { status, data } = error.response;
    return {
      status,
      message: data?.message || data?.error || defaultMessage,
      details: data
    };
  }
  
  // Handle network errors
  if (error.name === 'NetworkError' || error.message?.includes('Network') || error.message?.includes('Failed to fetch')) {
    return {
      status: 0,
      message: 'Network error: Could not connect to the server',
      isNetworkError: true
    };
  }
  
  // Handle timeout errors
  if (error.name === 'TimeoutError' || error.message?.includes('timeout')) {
    return {
      status: 408,
      message: 'Request timed out',
      isTimeoutError: true
    };
  }
  
  // Default error format
  return {
    status: 500,
    message: error.message || defaultMessage,
    error
  };
};

/**
 * Add pagination parameters to a request
 * @param {Object} params - Existing params
 * @param {Object} pagination - Pagination options
 * @param {number} pagination.page - Page number
 * @param {number} pagination.limit - Page size
 * @returns {Object} - Params with pagination
 */
export const withPagination = (params = {}, pagination = {}) => {
  const { page, limit } = pagination;
  return {
    ...params,
    ...(page !== undefined && { page }),
    ...(limit !== undefined && { limit })
  };
};

/**
 * Parse backend availability status from response headers
 * @param {Response} response - Fetch API response
 * @returns {Object} - Backend status
 */
export const parseBackendStatus = (response) => {
  if (!response || !response.headers) {
    return { available: false, reason: 'Invalid response' };
  }
  
  // Check for backend status headers
  const backendStatus = response.headers.get('X-Backend-Status');
  const localDocuments = response.headers.get('X-Local-Documents');
  
  return {
    available: backendStatus !== 'unavailable',
    usingLocalData: localDocuments === 'true',
    status: backendStatus || 'unknown'
  };
};

/**
 * Format XML content for display
 * @param {string} xml - Raw XML content
 * @returns {string} - Formatted XML
 */
export const formatXmlForDisplay = (xml) => {
  if (!xml) return '';
  
  try {
    // First, check for escaped XML
    let content = xml;
    
    // Handle escaped newlines that might be in JSON responses
    if (content.includes('\\n')) {
      content = content.replace(/\\n/g, '\n')
                      .replace(/\\"/g, '"')
                      .replace(/\\t/g, '    ');
    }
    
    // Handle HTML-escaped XML
    if (content.includes('&lt;') && !content.includes('<')) {
      content = content
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&')
        .replace(/&quot;/g, '"')
        .replace(/&#039;/g, "'");
    }
    
    // Use vkBeautify library if available in window
    if (window.vkbeautify) {
      return window.vkbeautify.xml(content);
    }
    
    // Basic formatting fallback
    return content.replace(/></g, '>\n<');
  } catch (e) {
    console.error('Error formatting XML:', e);
    return xml;
  }
};

/**
 * Log API performance metrics
 * @param {string} endpoint - API endpoint
 * @param {number} startTime - Start timestamp
 * @param {Object} options - Additional info
 */
export const logApiPerformance = (endpoint, startTime, options = {}) => {
  const endTime = performance.now();
  const duration = endTime - startTime;
  
  if (window.apLogger?.data) {
    window.apLogger.data('API Performance', {
      endpoint,
      duration: `${duration.toFixed(2)}ms`,
      ...options
    });
  }
};

export default {
  formatApiError,
  withPagination,
  parseBackendStatus,
  formatXmlForDisplay,
  logApiPerformance
};