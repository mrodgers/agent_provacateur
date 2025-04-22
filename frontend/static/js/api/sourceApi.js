/**
 * Source API Module
 * 
 * Provides functions for interacting with source-related endpoints
 * Used for source attribution and validation
 */

import apiClient from './index';

/**
 * Source API functions
 */
export const sourceApi = {
  /**
   * Get available source types
   * @returns {Promise<Array>} - List of available source types
   */
  async getSourceTypes() {
    return apiClient.get('/sources');
  },
  
  /**
   * Get source details
   * @param {string} sourceId - Source ID
   * @returns {Promise<Object>} - Source details
   */
  async getSourceById(sourceId) {
    return apiClient.get(`/sources/${sourceId}`);
  },
  
  /**
   * Validate a source
   * @param {Object} sourceData - Source data to validate
   * @returns {Promise<Object>} - Validation result
   */
  async validateSource(sourceData) {
    return apiClient.post('/sources/validate', sourceData);
  },
  
  /**
   * Get sources for an entity
   * @param {string} entityId - Entity ID
   * @returns {Promise<Array>} - List of sources for the entity
   */
  async getEntitySources(entityId) {
    return apiClient.get(`/entities/${entityId}/sources`);
  },
  
  /**
   * Get citations for a source
   * @param {string} sourceId - Source ID
   * @param {string} format - Citation format (e.g., 'apa', 'mla', 'chicago')
   * @returns {Promise<Object>} - Citation details
   */
  async getSourceCitation(sourceId, format = 'apa') {
    return apiClient.get(`/sources/${sourceId}/citation`, { format });
  }
};

export default sourceApi;