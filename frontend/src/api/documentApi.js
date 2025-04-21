/**
 * Document API Module
 * 
 * Provides functions for interacting with document-related endpoints
 */

import apiClient from './index';

/**
 * Document API functions
 */
export const documentApi = {
  /**
   * Fetch all documents
   * @param {Object} options - Query options
   * @param {number} options.page - Page number for pagination
   * @param {number} options.limit - Page size
   * @param {string} options.type - Filter by document type
   * @returns {Promise<Object>} - Document list and metadata
   */
  async getAllDocuments(options = {}) {
    return apiClient.get('/documents', options);
  },
  
  /**
   * Get document details by ID
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} - Document details
   */
  async getDocumentById(documentId) {
    return apiClient.get(`/documents/${documentId}`);
  },
  
  /**
   * Get document XML content
   * @param {string} documentId - Document ID
   * @returns {Promise<Object>} - XML document content and metadata
   */
  async getDocumentXml(documentId) {
    return apiClient.get(`/documents/${documentId}/xml`);
  },
  
  /**
   * Get document XML raw content
   * @param {string} documentId - Document ID
   * @returns {Promise<string>} - Raw XML content
   */
  async getDocumentXmlContent(documentId) {
    // We need to handle text response, not JSON
    try {
      const url = `${window.BACKEND_URL}/documents/${documentId}/xml/content`;
      
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
  
  /**
   * Get document structure nodes
   * @param {string} documentId - Document ID
   * @returns {Promise<Array>} - Document nodes
   */
  async getDocumentNodes(documentId) {
    return apiClient.get(`/documents/${documentId}/xml/nodes`);
  },
  
  /**
   * Upload a new document
   * @param {Object} data - Upload data
   * @param {File} data.file - The file to upload
   * @param {string} data.title - Document title
   * @returns {Promise<Object>} - Upload result
   */
  async uploadDocument(data) {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('title', data.title);
    
    return apiClient.uploadFile('/xml/upload', formData);
  },
  
  /**
   * Search documents
   * @param {string} query - Search query
   * @param {Object} options - Search options
   * @returns {Promise<Object>} - Search results
   */
  async searchDocuments(query, options = {}) {
    return apiClient.get('/documents/search', {
      query,
      ...options
    });
  }
};

export default documentApi;