/**
 * Agent API Module
 * 
 * Provides functions for interacting with agent-related endpoints
 * Used for managing and monitoring agents
 */

import apiClient from './index';

/**
 * Agent API functions
 */
export const agentApi = {
  /**
   * Get all agents
   * @returns {Promise<Object>} - Agent list and stats
   */
  async getAllAgents() {
    return apiClient.get('/agents');
  },
  
  /**
   * Get agent details
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} - Agent details
   */
  async getAgentById(agentId) {
    return apiClient.get(`/agents/${agentId}`);
  },
  
  /**
   * Start an agent
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} - Operation result
   */
  async startAgent(agentId) {
    return apiClient.post(`/agents/${agentId}/start`);
  },
  
  /**
   * Stop an agent
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} - Operation result
   */
  async stopAgent(agentId) {
    return apiClient.post(`/agents/${agentId}/stop`);
  },
  
  /**
   * Get agent logs
   * @param {string} agentId - Agent ID
   * @param {Object} options - Log options
   * @param {number} options.limit - Max number of log entries
   * @param {string} options.level - Log level filter
   * @returns {Promise<Object>} - Agent logs
   */
  async getAgentLogs(agentId, options = {}) {
    return apiClient.get(`/agents/${agentId}/logs`, options);
  },
  
  /**
   * Get agent configuration
   * @param {string} agentId - Agent ID
   * @returns {Promise<Object>} - Agent configuration
   */
  async getAgentConfig(agentId) {
    return apiClient.get(`/agents/${agentId}/config`);
  },
  
  /**
   * Update agent configuration
   * @param {string} agentId - Agent ID
   * @param {Object} config - New configuration
   * @returns {Promise<Object>} - Updated configuration
   */
  async updateAgentConfig(agentId, config) {
    return apiClient.post(`/agents/${agentId}/config`, config);
  },
  
  /**
   * Get system health metrics
   * @returns {Promise<Object>} - System health metrics
   */
  async getSystemHealth() {
    return apiClient.get('/system/health');
  }
};

export default agentApi;