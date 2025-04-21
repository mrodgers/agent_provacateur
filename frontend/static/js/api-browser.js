/**
 * Agent Provocateur API Client (Browser Version)
 * 
 * This is a bundled version of the API client for direct browser usage
 */

// Configure API client
(function(window) {
  // Configure base client with defaults
  const API_BASE_URL = window.BACKEND_URL || 'http://localhost:8000';
  
  // Base API client
  window.apiClient = {
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
  
  // Document API
  window.documentApi = {
    async getAllDocuments(options = {}) {
      return window.apiClient.get('/documents', options);
    },
    
    async getDocumentById(documentId) {
      return window.apiClient.get(`/documents/${documentId}`);
    },
    
    async getDocumentXml(documentId) {
      return window.apiClient.get(`/documents/${documentId}/xml`);
    },
    
    async getDocumentXmlContent(documentId) {
      try {
        const url = `${API_BASE_URL}/documents/${documentId}/xml/content`;
        
        // Log API call if debugging is enabled
        if (window.apLogger?.api) {
          window.apLogger.api(`GET ${url}`);
        }
        
        // Make the request
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Accept': 'application/xml, text/plain'
          }
        });
        
        // Handle non-2xx responses
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`API error: ${response.status} ${response.statusText} - ${errorText}`);
        }
        
        // Return as text
        const content = await response.text();
        return content;
      } catch (error) {
        // Log error if logger is available
        if (window.apLogger?.error) {
          window.apLogger.error(`API error getting XML content for ${documentId}:`, error);
        } else {
          console.error(`API error getting XML content for ${documentId}:`, error);
        }
        
        // Re-throw for handling by caller
        throw error;
      }
    },
    
    async getDocumentNodes(documentId) {
      return window.apiClient.get(`/documents/${documentId}/xml/nodes`);
    },
    
    async uploadDocument(data) {
      const formData = new FormData();
      formData.append('file', data.file);
      formData.append('title', data.title);
      
      return window.apiClient.uploadFile('/xml/upload', formData);
    },
    
    async searchDocuments(query, options = {}) {
      return window.apiClient.get('/documents/search', {
        query,
        ...options
      });
    }
  };
  
  // Task API
  window.taskApi = {
    async createTask(taskData) {
      // Generate task ID if not provided
      const taskId = taskData.task_id || `task_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
      
      // Prepare payload with defaults
      const payload = {
        task_id: taskId,
        source_agent: taskData.source_agent || 'frontend',
        target_agent: taskData.target_agent || 'xml_agent',
        intent: taskData.intent,
        payload: taskData.payload || {}
      };
      
      return window.apiClient.post('/task', payload);
    },
    
    async getTaskStatus(taskId) {
      return window.apiClient.get(`/task/${taskId}`);
    },
    
    async getTaskResult(taskId) {
      return window.apiClient.get(`/task/${taskId}/result`);
    },
    
    async extractEntities(documentId, options = {}) {
      return this.createTask({
        intent: 'extract_entities',
        target_agent: 'xml_agent',
        payload: {
          doc_id: documentId,
          ...options
        }
      });
    },
    
    async researchEntities(documentId, options = {}) {
      return this.createTask({
        intent: 'research_entities',
        target_agent: 'research_agent',
        payload: {
          doc_id: documentId,
          options: {
            use_web_search: options.use_web_search !== false,
            search_provider: options.search_provider || 'brave',
            max_entities: options.max_entities || 10
          }
        }
      });
    },
    
    async validateStructure(documentId) {
      return this.createTask({
        intent: 'validate_structure',
        target_agent: 'xml_agent',
        payload: {
          doc_id: documentId
        }
      });
    },
    
    async createVerificationPlan(documentId) {
      return this.createTask({
        intent: 'create_verification_plan',
        target_agent: 'xml_agent',
        payload: {
          doc_id: documentId
        }
      });
    }
  };
  
  // Agent API
  window.agentApi = {
    async getAllAgents() {
      return window.apiClient.get('/agents');
    },
    
    async getAgentById(agentId) {
      return window.apiClient.get(`/agents/${agentId}`);
    },
    
    async startAgent(agentId) {
      return window.apiClient.post(`/agents/${agentId}/start`);
    },
    
    async stopAgent(agentId) {
      return window.apiClient.post(`/agents/${agentId}/stop`);
    },
    
    async getAgentLogs(agentId, options = {}) {
      return window.apiClient.get(`/agents/${agentId}/logs`, options);
    },
    
    async getAgentConfig(agentId) {
      return window.apiClient.get(`/agents/${agentId}/config`);
    },
    
    async updateAgentConfig(agentId, config) {
      return window.apiClient.post(`/agents/${agentId}/config`, config);
    },
    
    async getSystemHealth() {
      return window.apiClient.get('/system/health');
    }
  };
  
  // Source API
  window.sourceApi = {
    async getSourceTypes() {
      return window.apiClient.get('/sources');
    },
    
    async getSourceById(sourceId) {
      return window.apiClient.get(`/sources/${sourceId}`);
    },
    
    async validateSource(sourceData) {
      return window.apiClient.post('/sources/validate', sourceData);
    },
    
    async getEntitySources(entityId) {
      return window.apiClient.get(`/entities/${entityId}/sources`);
    },
    
    async getSourceCitation(sourceId, format = 'apa') {
      return window.apiClient.get(`/sources/${sourceId}/citation`, { format });
    }
  };
  
  // Utils
  window.apiUtils = {
    formatApiError(error, defaultMessage = 'An error occurred') {
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
    },
    
    withPagination(params = {}, pagination = {}) {
      const { page, limit } = pagination;
      return {
        ...params,
        ...(page !== undefined && { page }),
        ...(limit !== undefined && { limit })
      };
    },
    
    parseBackendStatus(response) {
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
    },
    
    formatXmlForDisplay(xml) {
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
    }
  };
  
  // Combined API
  window.apApi = {
    client: window.apiClient,
    documents: window.documentApi,
    tasks: window.taskApi,
    agents: window.agentApi,
    sources: window.sourceApi,
    utils: window.apiUtils,
    
    // Initialize the API with configuration
    initialize(config = {}) {
      if (window.apLogger?.info) {
        window.apLogger.info('Initializing Agent Provocateur API client', config);
      }
      
      return this;
    },
    
    // System-wide endpoints
    async getSystemInfo() {
      return window.apiClient.get('/api/info');
    },
    
    async healthCheck() {
      return window.apiClient.get('/api/health');
    }
  };
  
  console.log('Agent Provocateur API client loaded successfully');
  
})(window);