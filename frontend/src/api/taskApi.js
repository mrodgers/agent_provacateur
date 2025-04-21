/**
 * Task API Module
 * 
 * Provides functions for interacting with task-related endpoints
 * Used for document processing, entity extraction, and research tasks
 */

import apiClient from './index';

/**
 * Task API functions
 */
export const taskApi = {
  /**
   * Create a new processing task
   * @param {Object} taskData - Task data
   * @param {string} taskData.task_id - Unique task ID (generated if not provided)
   * @param {string} taskData.source_agent - Source agent identifier
   * @param {string} taskData.target_agent - Target agent identifier
   * @param {string} taskData.intent - Task intent (e.g., "extract_entities")
   * @param {Object} taskData.payload - Task payload data
   * @returns {Promise<Object>} - Task result
   */
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
    
    return apiClient.post('/task', payload);
  },
  
  /**
   * Get task status
   * @param {string} taskId - Task ID
   * @returns {Promise<Object>} - Task status
   */
  async getTaskStatus(taskId) {
    return apiClient.get(`/task/${taskId}`);
  },
  
  /**
   * Get task result
   * @param {string} taskId - Task ID
   * @returns {Promise<Object>} - Task result
   */
  async getTaskResult(taskId) {
    return apiClient.get(`/task/${taskId}/result`);
  },
  
  /**
   * Extract entities from a document
   * @param {string} documentId - Document ID
   * @param {Object} options - Extraction options
   * @returns {Promise<Object>} - Extraction results
   */
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
  
  /**
   * Research entities in a document
   * @param {string} documentId - Document ID
   * @param {Object} options - Research options
   * @param {boolean} options.use_web_search - Whether to use web search
   * @param {string} options.search_provider - Web search provider
   * @returns {Promise<Object>} - Research results
   */
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
  
  /**
   * Validate document structure
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} - Validation results
   */
  async validateStructure(documentId) {
    return this.createTask({
      intent: 'validate_structure',
      target_agent: 'xml_agent',
      payload: {
        doc_id: documentId
      }
    });
  },
  
  /**
   * Create verification plan for document
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} - Verification plan
   */
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

export default taskApi;