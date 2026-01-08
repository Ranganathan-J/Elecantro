/**
 * Frontend logging utility for monitoring and debugging
 */

class Logger {
  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.logLevel = this.getLogLevel();
    this.logs = [];
    this.maxLogs = 1000; // Keep last 1000 logs in memory
  }

  getLogLevel() {
    const levels = ['ERROR', 'WARN', 'INFO', 'DEBUG'];
    const envLevel = process.env.REACT_APP_LOG_LEVEL?.toUpperCase();
    return levels.includes(envLevel) ? envLevel : 'INFO';
  }

  shouldLog(level) {
    const levels = ['ERROR', 'WARN', 'INFO', 'DEBUG'];
    const currentLevelIndex = levels.indexOf(this.logLevel);
    const messageLevelIndex = levels.indexOf(level);
    return messageLevelIndex <= currentLevelIndex;
  }

  formatMessage(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      data,
      url: window.location.href,
      userAgent: navigator.userAgent,
      userId: this.getCurrentUserId(),
    };

    // Store in memory for debugging
    this.logs.push(logEntry);
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    return logEntry;
  }

  getCurrentUserId() {
    // Try to get user ID from localStorage or context
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      return user.id || user.username || 'anonymous';
    } catch {
      return 'anonymous';
    }
  }

  error(message, data = null) {
    if (!this.shouldLog('ERROR')) return;
    
    const logEntry = this.formatMessage('ERROR', message, data);
    
    // Console output
    console.error(`[ERROR] ${message}`, data);
    
    // Send to backend for logging
    this.sendToBackend(logEntry);
  }

  warn(message, data = null) {
    if (!this.shouldLog('WARN')) return;
    
    const logEntry = this.formatMessage('WARN', message, data);
    
    // Console output
    console.warn(`[WARN] ${message}`, data);
    
    // Send to backend for logging
    this.sendToBackend(logEntry);
  }

  info(message, data = null) {
    if (!this.shouldLog('INFO')) return;
    
    const logEntry = this.formatMessage('INFO', message, data);
    
    // Console output
    console.info(`[INFO] ${message}`, data);
    
    // Send to backend for logging
    this.sendToBackend(logEntry);
  }

  debug(message, data = null) {
    if (!this.shouldLog('DEBUG')) return;
    
    const logEntry = this.formatMessage('DEBUG', message, data);
    
    // Console output
    console.debug(`[DEBUG] ${message}`, data);
    
    // Don't send debug logs to backend in production
    if (this.isDevelopment) {
      this.sendToBackend(logEntry);
    }
  }

  // Performance logging
  performance(metricName, duration, data = null) {
    const logEntry = this.formatMessage('PERFORMANCE', `${metricName}: ${duration}ms`, {
      metricName,
      duration,
      ...data
    });

    console.log(`[PERF] ${metricName}: ${duration}ms`, data);
    this.sendToBackend(logEntry);
  }

  // User action logging
  userAction(action, details = null) {
    const logEntry = this.formatMessage('USER_ACTION', action, details);
    this.sendToBackend(logEntry);
  }

  // API request logging
  apiRequest(method, url, status, duration, error = null) {
    const logEntry = this.formatMessage('API_REQUEST', `${method} ${url}`, {
      method,
      url,
      status,
      duration,
      error: error ? error.message : null
    });

    if (status >= 400) {
      console.error(`[API] ${method} ${url} -> ${status}`, error);
    } else {
      console.log(`[API] ${method} ${url} -> ${status} (${duration}ms)`);
    }

    this.sendToBackend(logEntry);
  }

  // Send logs to backend
  async sendToBackend(logEntry) {
    try {
      // Don't send logs in development if disabled
      if (this.isDevelopment && process.env.REACT_APP_DISABLE_BACKEND_LOGGING === 'true') {
        return;
      }

      await fetch('/api/logs/frontend/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logEntry),
      });
    } catch (error) {
      // Silently fail to avoid infinite loops
      console.warn('Failed to send log to backend:', error);
    }
  }

  // Get stored logs for debugging
  getLogs(level = null) {
    if (level) {
      return this.logs.filter(log => log.level === level);
    }
    return this.logs;
  }

  // Clear stored logs
  clearLogs() {
    this.logs = [];
  }

  // Export logs for debugging
  exportLogs() {
    const dataStr = JSON.stringify(this.logs, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `frontend-logs-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }
}

// Create singleton instance
const logger = new Logger();

// Performance monitoring utilities
export const performanceMonitor = {
  // Measure function execution time
  measure: async (name, fn) => {
    const start = performance.now();
    try {
      const result = await fn();
      const duration = performance.now() - start;
      logger.performance(name, duration);
      return result;
    } catch (error) {
      const duration = performance.now() - start;
      logger.performance(`${name} (failed)`, duration, { error: error.message });
      throw error;
    }
  },

  // Measure React component render time
  measureRender: (componentName, renderFn) => {
    const start = performance.now();
    const result = renderFn();
    const duration = performance.now() - start;
    logger.performance(`Render ${componentName}`, duration);
    return result;
  }
};

// Error boundary logging
export const logError = (error, errorInfo = null) => {
  logger.error('React Error Boundary', {
    error: error.message,
    stack: error.stack,
    componentStack: errorInfo?.componentStack,
  });
};

export default logger;
