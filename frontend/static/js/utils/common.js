/**
 * Common utility functions for Agent Provocateur
 * Provides shared functionality across the application
 */

// Create namespace for utilities
window.APUtils = window.APUtils || {};

/**
 * Format a date string for display
 * @param {string|Date} dateString - Date string or Date object
 * @param {Object} options - Formatting options
 * @returns {string} Formatted date string
 */
function formatDate(dateString, options = {}) {
  const defaults = {
    format: 'medium', // short, medium, long, full
    includeTime: false,
    timeFormat: '24h'  // 12h, 24h
  };
  
  const config = { ...defaults, ...options };
  
  if (!dateString) return '';
  
  try {
    const date = dateString instanceof Date ? dateString : new Date(dateString);
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      return 'Invalid date';
    }
    
    // Format based on specified format
    let formattedDate = '';
    
    // Date formatting
    const formatOptions = { 
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
    };
    
    switch (config.format) {
      case 'short':
        formatOptions.year = 'numeric';
        formatOptions.month = 'numeric';
        formatOptions.day = 'numeric';
        break;
      case 'medium':
        formatOptions.year = 'numeric';
        formatOptions.month = 'short';
        formatOptions.day = 'numeric';
        break;
      case 'long':
        formatOptions.year = 'numeric';
        formatOptions.month = 'long';
        formatOptions.day = 'numeric';
        break;
      case 'full':
        formatOptions.year = 'numeric';
        formatOptions.month = 'long';
        formatOptions.day = 'numeric';
        formatOptions.weekday = 'long';
        break;
      default:
        formatOptions.year = 'numeric';
        formatOptions.month = 'short';
        formatOptions.day = 'numeric';
    }
    
    // Add time if requested
    if (config.includeTime) {
      formatOptions.hour = 'numeric';
      formatOptions.minute = '2-digit';
      
      if (config.timeFormat === '12h') {
        formatOptions.hour12 = true;
      } else {
        formatOptions.hour12 = false;
      }
    }
    
    formattedDate = new Intl.DateTimeFormat('en-US', formatOptions).format(date);
    
    return formattedDate;
  } catch (error) {
    console.error('Error formatting date:', error);
    return dateString;
  }
}

/**
 * Format XML content for display
 * @param {string} xml - XML content to format
 * @returns {string} HTML-escaped formatted XML
 */
function formatXml(xml) {
  if (!xml) return '';
  
  try {
    // First, check if the XML contains literal '\\n' strings 
    // (this happens when XML is passed through JSON or certain APIs)
    let cleanXml = xml;
    if (xml.includes('\\n')) {
      // Convert literal '\\n' to actual newlines
      cleanXml = xml.replace(/\\n/g, '\n')
                   .replace(/\\"/g, '"')
                   .replace(/\\t/g, '    ');
    }
    
    // Check if we need to unescape HTML entities
    let rawXml = cleanXml;
    if (cleanXml.includes('&lt;') && !cleanXml.includes('<')) {
      // Convert escaped HTML to raw XML
      rawXml = cleanXml
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&')
        .replace(/&quot;/g, '"')
        .replace(/&#039;/g, "'");
    }
    
    // Try to use vkBeautify library if available
    if (window.vkbeautify) {
      const prettyXml = window.vkbeautify.xml(rawXml);
      return escapeHtml(prettyXml);
    }
    
    // Fallback formatting if vkBeautify is not available
    // Basic indentation algorithm
    let formatted = '';
    let indent = '';
    const indentSize = 2;
    const lines = rawXml.trim().split(/>[\\s\\r\\n]*</);
    
    if (lines.length > 0) {
      formatted = lines[0].trim();
      
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        
        if (line.startsWith('/')) {
          // This is a closing tag, decrease indent
          indent = indent.substring(0, indent.length - indentSize);
        }
        
        // Add the properly indented line
        formatted += '>\n' + indent + '<' + line;
        
        if (!line.startsWith('/') && 
            !line.endsWith('/') && 
            !line.includes('</') && 
            line.indexOf('<') === 0) {
          // This is an opening tag and not self-closing, increase indent
          indent += ' '.repeat(indentSize);
        }
      }
    }
    
    // Re-escape for HTML display
    return escapeHtml(formatted);
  } catch (e) {
    console.error("Error formatting XML:", e);
    // Fall back to just escaping the input if formatting fails
    return escapeHtml(xml);
  }
}

/**
 * Escape HTML special characters
 * @param {string} html - String to escape
 * @returns {string} Escaped HTML string
 */
function escapeHtml(html) {
  if (!html) return '';
  
  return html
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Generate a unique ID
 * @param {string} prefix - Optional prefix for the ID
 * @returns {string} Unique ID
 */
function generateId(prefix = 'ap') {
  return `${prefix}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Format file size in human-readable format
 * @param {number} bytes - Size in bytes
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Check if a string is valid JSON
 * @param {string} str - String to check
 * @returns {boolean} True if valid JSON
 */
function isValidJson(str) {
  try {
    JSON.parse(str);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Parse URL parameters
 * @param {string} url - URL to parse (defaults to current URL)
 * @returns {Object} Object with URL parameters
 */
function parseUrlParams(url = window.location.href) {
  const params = {};
  
  try {
    const urlObj = new URL(url);
    const searchParams = new URLSearchParams(urlObj.search);
    
    for (const [key, value] of searchParams.entries()) {
      params[key] = value;
    }
  } catch (error) {
    console.error('Error parsing URL parameters:', error);
  }
  
  return params;
}

/**
 * Check if a system port is available
 * @param {number} port - Port number to check
 * @returns {Promise<boolean>} True if port is available
 */
async function checkPort(port) {
  try {
    const response = await fetch(`/api/check-port?port=${port}`);
    const data = await response.json();
    return data.available;
  } catch (error) {
    console.error('Error checking port:', error);
    return false;
  }
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<boolean>} True if copied successfully
 */
async function copyToClipboard(text) {
  try {
    if (navigator.clipboard) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.top = '0';
      textArea.style.left = '0';
      textArea.style.width = '2em';
      textArea.style.height = '2em';
      textArea.style.padding = '0';
      textArea.style.border = 'none';
      textArea.style.outline = 'none';
      textArea.style.boxShadow = 'none';
      textArea.style.background = 'transparent';
      
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      const successful = document.execCommand('copy');
      document.body.removeChild(textArea);
      
      return successful;
    }
  } catch (error) {
    console.error('Error copying to clipboard:', error);
    return false;
  }
}

/**
 * Validate an email address
 * @param {string} email - Email to validate
 * @returns {boolean} True if email is valid
 */
function isValidEmail(email) {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
}

/**
 * Truncate text to a specific length
 * @param {string} text - Text to truncate
 * @param {number} length - Maximum length
 * @param {string} suffix - Suffix to add if truncated
 * @returns {string} Truncated text
 */
function truncateText(text, length = 100, suffix = '...') {
  if (!text) return '';
  
  if (text.length <= length) {
    return text;
  }
  
  return text.substring(0, length).trim() + suffix;
}

/**
 * Check system ports status
 * @returns {Promise<Object>} Port status information
 */
async function checkSystemPorts() {
  try {
    const response = await fetch('/api/info');
    if (!response.ok) {
      throw new Error(`Failed to fetch system info: ${response.status}`);
    }
    
    const systemInfo = await response.json();
    return systemInfo;
  } catch (error) {
    console.error('Error checking system ports:', error);
    return {
      error: true,
      message: error.message,
      ports: {}
    };
  }
}

/**
 * Download a file
 * @param {Blob|string} content - File content (Blob or string)
 * @param {string} fileName - File name
 * @param {string} mimeType - MIME type (if content is string)
 */
function downloadFile(content, fileName, mimeType = 'text/plain') {
  try {
    // Create blob from content if it's a string
    const blob = typeof content === 'string' 
      ? new Blob([content], { type: mimeType }) 
      : content;
    
    // Create download URL
    const url = URL.createObjectURL(blob);
    
    // Create download link
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    
    // Trigger download
    a.click();
    
    // Clean up
    setTimeout(() => {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 100);
    
    return true;
  } catch (error) {
    console.error('Error downloading file:', error);
    return false;
  }
}

// Export the utility functions
window.APUtils = {
  formatDate,
  formatXml,
  escapeHtml,
  generateId,
  formatFileSize,
  isValidJson,
  parseUrlParams,
  checkPort,
  copyToClipboard,
  isValidEmail,
  truncateText,
  checkSystemPorts,
  downloadFile
};