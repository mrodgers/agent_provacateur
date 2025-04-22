/**
 * Centralized logging utility for Agent Provocateur
 * Provides consistent logging across the application with configurable levels
 */

// Define log levels
const LogLevels = {
  ERROR: 0,   // Only critical errors
  WARN: 1,    // Warnings and errors
  INFO: 2,    // General information plus warnings and errors
  DEBUG: 3,   // Detailed debug information
  VERBOSE: 4  // All logging, very detailed
};

// Default configuration
const defaultConfig = {
  level: LogLevels.INFO,
  enableConsole: true,
  enableAPI: false,    // Whether to send logs to backend API
  enableStorage: true, // Whether to store logs in localStorage
  storageKey: 'ap_logs',
  maxStoredLogs: 1000,
  categories: {
    api: true,      // API interaction logs
    ui: true,       // UI interaction logs
    data: true,     // Data transformation logs
    performance: true // Performance measurements
  }
};

// Initialize logger
function createLogger(customConfig = {}) {
  // Merge custom config with defaults
  const config = { ...defaultConfig, ...customConfig };
  if (customConfig.categories) {
    config.categories = { ...defaultConfig.categories, ...customConfig.categories };
  }

  // Convert level from string to numeric value if needed
  if (typeof config.level === 'string') {
    const levelName = config.level.toUpperCase();
    config.level = LogLevels[levelName] !== undefined ? LogLevels[levelName] : LogLevels.INFO;
  }

  // Helper to format log entries
  function formatLogEntry(level, message, ...args) {
    const timestamp = new Date().toISOString();
    return {
      timestamp,
      level,
      message,
      args: args.length > 0 ? args : undefined
    };
  }

  // Save log to localStorage if enabled
  function storeLog(entry) {
    if (!config.enableStorage) return;
    
    try {
      let logs = JSON.parse(localStorage.getItem(config.storageKey) || '[]');
      logs.push(entry);
      
      // Trim logs if they exceed maximum
      if (logs.length > config.maxStoredLogs) {
        logs = logs.slice(-config.maxStoredLogs);
      }
      
      localStorage.setItem(config.storageKey, JSON.stringify(logs));
    } catch (e) {
      console.error('Error storing log:', e);
    }
  }

  // Send log to API if enabled
  function sendLogToAPI(entry) {
    if (!config.enableAPI) return;
    
    // Implementation for sending logs to backend can be added here
    // This could use fetch or axios to send logs to a backend endpoint
  }

  // Core logging function
  function log(level, levelName, message, ...args) {
    if (level > config.level) return;
    
    const entry = formatLogEntry(levelName, message, ...args);
    
    // Log to console if enabled
    if (config.enableConsole) {
      const consoleMethod = levelName.toLowerCase();
      if (console[consoleMethod]) {
        console[consoleMethod](`[AP ${levelName}] ${message}`, ...args);
      } else {
        console.log(`[AP ${levelName}] ${message}`, ...args);
      }
    }
    
    // Store log
    storeLog(entry);
    
    // Send to API if configured
    sendLogToAPI(entry);
  }

  // Create the logger object
  const logger = {
    // Standard log levels
    error: (message, ...args) => log(LogLevels.ERROR, 'ERROR', message, ...args),
    warn: (message, ...args) => log(LogLevels.WARN, 'WARN', message, ...args),
    info: (message, ...args) => log(LogLevels.INFO, 'INFO', message, ...args),
    debug: (message, ...args) => log(LogLevels.DEBUG, 'DEBUG', message, ...args),
    verbose: (message, ...args) => log(LogLevels.VERBOSE, 'VERBOSE', message, ...args),
    
    // Category-specific logging
    api: (message, ...args) => {
      if (!config.categories.api) return;
      log(LogLevels.INFO, 'API', message, ...args);
    },
    ui: (message, ...args) => {
      if (!config.categories.ui) return;
      log(LogLevels.INFO, 'UI', message, ...args);
    },
    data: (message, ...args) => {
      if (!config.categories.data) return;
      log(LogLevels.INFO, 'DATA', message, ...args);
    },
    performance: (message, ...args) => {
      if (!config.categories.performance) return;
      log(LogLevels.INFO, 'PERF', message, ...args);
    },
    
    // Performance measurement helper
    time: (label) => {
      if (config.categories.performance && config.level >= LogLevels.DEBUG) {
        console.time(`[AP PERF] ${label}`);
      }
    },
    timeEnd: (label) => {
      if (config.categories.performance && config.level >= LogLevels.DEBUG) {
        console.timeEnd(`[AP PERF] ${label}`);
      }
    },
    
    // Configuration methods
    getConfig: () => ({ ...config }), // Return copy of config
    setLevel: (level) => {
      if (typeof level === 'string') {
        const levelName = level.toUpperCase();
        config.level = LogLevels[levelName] !== undefined ? LogLevels[levelName] : config.level;
      } else if (typeof level === 'number') {
        config.level = level;
      }
      logger.info(`Log level set to ${config.level}`);
    },
    
    // Log management
    clearStoredLogs: () => {
      if (config.enableStorage) {
        localStorage.removeItem(config.storageKey);
        logger.info('Cleared stored logs');
      }
    },
    getStoredLogs: () => {
      if (!config.enableStorage) return [];
      
      try {
        return JSON.parse(localStorage.getItem(config.storageKey) || '[]');
      } catch (e) {
        logger.error('Error retrieving stored logs:', e);
        return [];
      }
    }
  };
  
  return logger;
}

// Export levels and initialize default logger on window
window.LogLevels = LogLevels;
window.createLogger = createLogger;

// Create the default application logger
window.apLogger = createLogger({
  level: window.AP_DEBUG?.level || 'info',
  categories: {
    api: window.AP_DEBUG?.api !== false,
    ui: window.AP_DEBUG?.ui !== false,
    data: window.AP_DEBUG?.data !== false
  }
});