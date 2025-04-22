/**
 * Error handling utilities for Agent Provocateur
 * Provides standardized error handling across the application
 */

// Error types for consistent categorization
const ErrorTypes = {
  NETWORK: 'network_error',
  API: 'api_error',
  VALIDATION: 'validation_error',
  AUTHENTICATION: 'auth_error',
  PERMISSION: 'permission_error',
  NOT_FOUND: 'not_found',
  SERVER: 'server_error',
  UNKNOWN: 'unknown_error'
};

/**
 * Format API errors into a standardized structure
 * @param {Error|Object} error - The error object from API call
 * @param {string} defaultMessage - Default message if none can be extracted
 * @returns {Object} Formatted error with consistent properties
 */
function formatApiError(error, defaultMessage = 'An error occurred') {
  // Default error structure
  const formattedError = {
    message: defaultMessage,
    type: ErrorTypes.UNKNOWN,
    status: null,
    isNetworkError: false,
    details: null,
    originalError: error
  };

  // Handle axios errors
  if (error.isAxiosError) {
    formattedError.isNetworkError = !error.response;
    
    if (error.response) {
      formattedError.status = error.response.status;
      
      // Set error type based on status code
      if (error.response.status >= 400 && error.response.status < 500) {
        if (error.response.status === 401) {
          formattedError.type = ErrorTypes.AUTHENTICATION;
        } else if (error.response.status === 403) {
          formattedError.type = ErrorTypes.PERMISSION;
        } else if (error.response.status === 404) {
          formattedError.type = ErrorTypes.NOT_FOUND;
        } else if (error.response.status === 422) {
          formattedError.type = ErrorTypes.VALIDATION;
        } else {
          formattedError.type = ErrorTypes.API;
        }
      } else if (error.response.status >= 500) {
        formattedError.type = ErrorTypes.SERVER;
      }
      
      // Extract message from response if available
      if (error.response.data && (error.response.data.message || error.response.data.error)) {
        formattedError.message = error.response.data.message || error.response.data.error;
        formattedError.details = error.response.data.details || error.response.data.errors;
      }
    } else if (error.request) {
      // Request was made but no response received
      formattedError.type = ErrorTypes.NETWORK;
      formattedError.message = 'Network error. Please check your connection.';
    }
  } else if (error instanceof Error) {
    formattedError.message = error.message;
    formattedError.details = error.stack;
  } else if (typeof error === 'string') {
    formattedError.message = error;
  } else if (typeof error === 'object' && error !== null) {
    // Try to extract information from error object
    formattedError.message = error.message || error.error || defaultMessage;
    formattedError.details = error.details || error.errors || null;
    formattedError.status = error.status || error.statusCode || null;
  }

  return formattedError;
}

/**
 * Display an error message in the specified container
 * @param {string} message - Error message to display
 * @param {string} containerId - ID of HTML element to place error in
 * @param {Object} options - Additional options (title, details, etc)
 */
function displayError(message, containerId = 'error-container', options = {}) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`Error container #${containerId} not found`);
    return;
  }

  const errorTitle = options.title || 'Error';
  const errorDetails = options.details || '';
  const errorType = options.type || 'error'; // error, warning, info
  
  // Map type to color classes
  const colorMap = {
    error: 'bg-red-100 border-red-400 text-red-700',
    warning: 'bg-yellow-100 border-yellow-400 text-yellow-700',
    info: 'bg-blue-100 border-blue-400 text-blue-700'
  };
  const colorClass = colorMap[errorType] || colorMap.error;

  const errorHtml = `
    <div class="${colorClass} border-l-4 px-4 py-3 rounded relative" role="alert">
      <div class="flex">
        <div class="py-1">
          <svg class="h-6 w-6 mr-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
              d="${errorType === 'error' ? 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' : 
                 errorType === 'warning' ? 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' : 
                 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'}" />
          </svg>
        </div>
        <div>
          <p class="font-bold">${errorTitle}</p>
          <p class="text-sm">${message}</p>
          ${errorDetails ? `<pre class="mt-2 text-xs overflow-auto">${errorDetails}</pre>` : ''}
          ${options.retry ? `
            <div class="mt-3">
              <button id="${containerId}-retry" class="px-3 py-1 bg-white text-sm border border-current rounded hover:bg-gray-100">
                Retry
              </button>
            </div>` : ''
          }
        </div>
      </div>
    </div>
  `;

  container.innerHTML = errorHtml;
  
  // Add event listener for retry button if provided
  if (options.retry && typeof options.retry === 'function') {
    const retryButton = document.getElementById(`${containerId}-retry`);
    if (retryButton) {
      retryButton.addEventListener('click', options.retry);
    }
  }

  // Scroll to error if requested
  if (options.scrollTo) {
    container.scrollIntoView({ behavior: 'smooth' });
  }
}

/**
 * Display a success message in the specified container
 * @param {string} message - Success message to display
 * @param {string} containerId - ID of HTML element to place message in
 * @param {Object} options - Additional options (title, details, etc)
 */
function displaySuccess(message, containerId = 'message-container', options = {}) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`Message container #${containerId} not found`);
    return;
  }

  const title = options.title || 'Success';
  
  const successHtml = `
    <div class="bg-green-100 border-l-4 border-green-400 text-green-700 px-4 py-3 rounded relative" role="alert">
      <div class="flex">
        <div class="py-1">
          <svg class="h-6 w-6 mr-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="font-bold">${title}</p>
          <p class="text-sm">${message}</p>
        </div>
        ${options.dismissible ? `
          <button id="${containerId}-dismiss" class="absolute top-0 right-0 p-2">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>` : ''
        }
      </div>
    </div>
  `;

  container.innerHTML = successHtml;
  
  // Add dismiss button handler if requested
  if (options.dismissible) {
    const dismissButton = document.getElementById(`${containerId}-dismiss`);
    if (dismissButton) {
      dismissButton.addEventListener('click', () => {
        container.innerHTML = '';
      });
    }
  }
  
  // Auto-dismiss if requested
  if (options.autoDismiss) {
    const timeout = typeof options.autoDismiss === 'number' ? options.autoDismiss : 3000;
    setTimeout(() => {
      container.innerHTML = '';
    }, timeout);
  }
}

// Export the utility functions
window.errorHandler = {
  ErrorTypes,
  formatApiError,
  displayError,
  displaySuccess
};