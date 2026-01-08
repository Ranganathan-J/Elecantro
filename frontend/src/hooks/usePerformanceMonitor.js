import { useEffect, useRef, useCallback } from 'react';
import logger from '../utils/logger';

/**
 * Hook for monitoring component performance and user interactions
 */
export const usePerformanceMonitor = (componentName) => {
  const renderStartTime = useRef(performance.now());
  const interactionCount = useRef(0);

  // Log component render performance
  useEffect(() => {
    const renderTime = performance.now() - renderStartTime.current;
    logger.performance(`Component Render: ${componentName}`, renderTime);
    
    // Reset for next render
    renderStartTime.current = performance.now();
  });

  // Track user interactions
  const trackInteraction = useCallback((action, details = {}) => {
    interactionCount.current += 1;
    logger.userAction(`${componentName}: ${action}`, {
      interactionNumber: interactionCount.current,
      component: componentName,
      ...details
    });
  }, [componentName]);

  // Track API calls
  const trackApiCall = useCallback(async (apiCall, actionName = null) => {
    const start = performance.now();
    const name = actionName || `${componentName} API Call`;
    
    try {
      const result = await apiCall();
      const duration = performance.now() - start;
      logger.performance(name, duration, { success: true });
      return result;
    } catch (error) {
      const duration = performance.now() - start;
      logger.performance(`${name} (failed)`, duration, { 
        success: false, 
        error: error.message 
      });
      throw error;
    }
  }, [componentName]);

  return {
    trackInteraction,
    trackApiCall,
    interactionCount: interactionCount.current
  };
};

/**
 * Hook for monitoring page load performance
 */
export const usePageLoadMonitor = () => {
  useEffect(() => {
    // Log navigation timing
    if ('performance' in window && 'getEntriesByType' in performance) {
      const navigationEntries = performance.getEntriesByType('navigation');
      if (navigationEntries.length > 0) {
        const nav = navigationEntries[0];
        logger.performance('Page Load Time', nav.loadEventEnd - nav.loadEventStart, {
          domContentLoaded: nav.domContentLoadedEventEnd - nav.domContentLoadedEventStart,
          firstPaint: nav.responseStart - nav.requestStart,
          type: nav.type
        });
      }
    }

    // Log resource loading
    const resourceEntries = performance.getEntriesByType('resource');
    const slowResources = resourceEntries.filter(entry => entry.duration > 1000);
    
    if (slowResources.length > 0) {
      logger.warn('Slow resources detected', {
        resources: slowResources.map(r => ({
          name: r.name,
          duration: r.duration,
          size: r.transferSize
        }))
      });
    }
  }, []);
};

/**
 * Hook for monitoring API response times
 */
export const useApiMonitor = () => {
  const trackApiResponse = useCallback((method, url, status, duration, error = null) => {
    logger.apiRequest(method, url, status, duration, error);
    
    // Log slow API calls
    if (duration > 2000) {
      logger.warn(`Slow API call: ${method} ${url}`, {
        duration,
        status
      });
    }
  }, []);

  return { trackApiResponse };
};

/**
 * Hook for monitoring user engagement
 */
export const useEngagementMonitor = () => {
  const sessionStartTime = useRef(Date.now());
  const lastActivityTime = useRef(Date.now());
  const isActive = useRef(true);

  useEffect(() => {
    const handleActivity = () => {
      lastActivityTime.current = Date.now();
      if (!isActive.current) {
        isActive.current = true;
        logger.userAction('Session Resumed', {
          awayDuration: Date.now() - lastActivityTime.current
        });
      }
    };

    const handleVisibilityChange = () => {
      if (document.hidden) {
        isActive.current = false;
        logger.userAction('Session Paused', {
          sessionDuration: Date.now() - sessionStartTime.current
        });
      } else {
        handleActivity();
      }
    };

    // Track user activity
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
    events.forEach(event => document.addEventListener(event, handleActivity, true));
    
    // Track page visibility
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Log session start
    logger.userAction('Session Started', {
      userAgent: navigator.userAgent,
      screenResolution: `${screen.width}x${screen.height}`,
      viewportSize: `${window.innerWidth}x${window.innerHeight}`
    });

    return () => {
      events.forEach(event => document.removeEventListener(event, handleActivity, true));
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      
      // Log session end
      logger.userAction('Session Ended', {
        totalDuration: Date.now() - sessionStartTime.current
      });
    };
  }, []);

  const trackEngagement = useCallback((action, details = {}) => {
    logger.userAction(action, {
      sessionDuration: Date.now() - sessionStartTime.current,
      ...details
    });
  }, []);

  return { trackEngagement };
};
