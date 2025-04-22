/**
 * Accessibility utilities for Agent Provocateur
 * Provides helper functions for creating accessible components
 */

// Create namespace for a11y utilities
window.APa11y = window.APa11y || {};

/**
 * Add ARIA attributes to an element
 * @param {HTMLElement} element - Element to add attributes to
 * @param {Object} attributes - ARIA attributes to add
 * @returns {HTMLElement} The modified element
 */
function setARIA(element, attributes = {}) {
  if (!element || !(element instanceof HTMLElement)) {
    console.error('Invalid element provided to setARIA');
    return null;
  }
  
  Object.entries(attributes).forEach(([key, value]) => {
    // Format the ARIA attribute name
    let attrName = key;
    if (!key.startsWith('aria-') && !key.startsWith('role')) {
      attrName = `aria-${key}`;
    }
    
    // Set the attribute
    if (value === null) {
      element.removeAttribute(attrName);
    } else if (typeof value === 'boolean') {
      element.setAttribute(attrName, value.toString());
    } else {
      element.setAttribute(attrName, value);
    }
  });
  
  return element;
}

/**
 * Create a screen reader only element
 * @param {string} text - Text content for screen readers
 * @param {string} tagName - HTML tag to use
 * @returns {HTMLElement} Screen reader only element
 */
function srOnly(text, tagName = 'span') {
  const element = document.createElement(tagName);
  element.className = 'sr-only';
  element.textContent = text;
  return element;
}

/**
 * Make an element focusable
 * @param {HTMLElement} element - Element to make focusable
 * @param {boolean} includeFocusRing - Whether to include a visible focus ring
 * @returns {HTMLElement} The modified element
 */
function makeFocusable(element, includeFocusRing = true) {
  if (!element || !(element instanceof HTMLElement)) {
    console.error('Invalid element provided to makeFocusable');
    return null;
  }
  
  // Set tabindex if not already set
  if (!element.hasAttribute('tabindex')) {
    element.setAttribute('tabindex', '0');
  }
  
  // Add keyboard event listener for Enter and Space
  element.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      element.click();
    }
  });
  
  // Add focus classes if requested
  if (includeFocusRing) {
    element.classList.add('focus-visible');
  }
  
  return element;
}

/**
 * Create a live region for screen reader announcements
 * @param {Object} options - Configuration options
 * @returns {HTMLElement} Live region element
 */
function createLiveRegion(options = {}) {
  const defaults = {
    ariaLive: 'polite', // polite, assertive
    ariaAtomic: true,
    ariaRelevant: 'additions text',
    className: 'sr-only'
  };
  
  const config = { ...defaults, ...options };
  
  const liveRegion = document.createElement('div');
  setARIA(liveRegion, {
    live: config.ariaLive,
    atomic: config.ariaAtomic,
    relevant: config.ariaRelevant
  });
  
  if (config.className) {
    liveRegion.className = config.className;
  }
  
  // Add a unique ID if not provided
  if (!options.id) {
    liveRegion.id = `live-region-${Math.random().toString(36).substring(2, 9)}`;
  } else {
    liveRegion.id = options.id;
  }
  
  return liveRegion;
}

/**
 * Announce a message to screen readers
 * @param {string} message - Message to announce
 * @param {Object} options - Configuration options
 */
function announce(message, options = {}) {
  const defaults = {
    ariaLive: 'polite', // polite, assertive
    clearAfter: 3000    // ms to clear message after
  };
  
  const config = { ...defaults, ...options };
  
  // Look for existing live region
  let liveRegion = document.getElementById('ap-announcer');
  
  // Create if not found
  if (!liveRegion) {
    liveRegion = createLiveRegion({
      id: 'ap-announcer',
      ariaLive: config.ariaLive
    });
    document.body.appendChild(liveRegion);
  } else {
    // Update aria-live value if different
    if (liveRegion.getAttribute('aria-live') !== config.ariaLive) {
      liveRegion.setAttribute('aria-live', config.ariaLive);
    }
  }
  
  // Announce the message
  liveRegion.textContent = message;
  
  // Clear after delay if requested
  if (config.clearAfter) {
    setTimeout(() => {
      liveRegion.textContent = '';
    }, config.clearAfter);
  }
}

/**
 * Create a skip link for keyboard navigation
 * @param {string} targetId - ID of the element to skip to
 * @param {string} text - Text content of the skip link
 * @returns {HTMLElement} Skip link element
 */
function createSkipLink(targetId, text = 'Skip to content') {
  const skipLink = document.createElement('a');
  skipLink.href = `#${targetId}`;
  skipLink.className = 'skip-to-content';
  skipLink.textContent = text;
  
  return skipLink;
}

/**
 * Track focus state for an element
 * @param {HTMLElement} element - Element to track focus for
 * @param {function} callback - Callback function when focus state changes
 * @returns {Object} Functions to remove listeners
 */
function trackFocus(element, callback) {
  if (!element || !(element instanceof HTMLElement)) {
    console.error('Invalid element provided to trackFocus');
    return null;
  }
  
  // Initialize state
  let isFocused = false;
  let isKeyboardFocused = false;
  
  // Store last input method
  let lastInputMethod = 'mouse';
  
  // Track input method
  const handleMouseDown = () => {
    lastInputMethod = 'mouse';
  };
  
  const handleKeyDown = (event) => {
    // Only track Tab key presses for keyboard navigation
    if (event.key === 'Tab') {
      lastInputMethod = 'keyboard';
    }
  };
  
  // Handle focus events
  const handleFocus = () => {
    isFocused = true;
    isKeyboardFocused = lastInputMethod === 'keyboard';
    
    if (callback && typeof callback === 'function') {
      callback({ isFocused, isKeyboardFocused });
    }
  };
  
  // Handle blur events
  const handleBlur = () => {
    isFocused = false;
    isKeyboardFocused = false;
    
    if (callback && typeof callback === 'function') {
      callback({ isFocused, isKeyboardFocused });
    }
  };
  
  // Add event listeners
  document.addEventListener('mousedown', handleMouseDown);
  document.addEventListener('keydown', handleKeyDown);
  element.addEventListener('focus', handleFocus);
  element.addEventListener('blur', handleBlur);
  
  // Return function to remove listeners
  return {
    stop: () => {
      document.removeEventListener('mousedown', handleMouseDown);
      document.removeEventListener('keydown', handleKeyDown);
      element.removeEventListener('focus', handleFocus);
      element.removeEventListener('blur', handleBlur);
    }
  };
}

/**
 * Create a focus trap for modal dialogs
 * @param {HTMLElement} container - Container element to trap focus within
 * @returns {Object} Focus trap controls
 */
function createFocusTrap(container) {
  if (!container || !(container instanceof HTMLElement)) {
    console.error('Invalid container provided to createFocusTrap');
    return null;
  }
  
  let active = false;
  let previouslyFocused = null;
  
  // Get focusable elements
  const getFocusableElements = () => {
    return Array.from(container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )).filter(el => !el.hasAttribute('disabled') && el.offsetParent !== null);
  };
  
  // Handle tab key to trap focus
  const handleKeyDown = (event) => {
    if (!active || event.key !== 'Tab') return;
    
    const focusableElements = getFocusableElements();
    if (focusableElements.length === 0) return;
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    // Shift + Tab
    if (event.shiftKey) {
      if (document.activeElement === firstElement) {
        lastElement.focus();
        event.preventDefault();
      }
    } 
    // Tab
    else {
      if (document.activeElement === lastElement) {
        firstElement.focus();
        event.preventDefault();
      }
    }
  };
  
  // Activate the focus trap
  const activate = () => {
    if (active) return;
    
    // Store currently focused element
    previouslyFocused = document.activeElement;
    
    // Add event listener
    document.addEventListener('keydown', handleKeyDown);
    
    // Focus first focusable element
    const focusableElements = getFocusableElements();
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
    }
    
    active = true;
  };
  
  // Deactivate the focus trap
  const deactivate = () => {
    if (!active) return;
    
    // Remove event listener
    document.removeEventListener('keydown', handleKeyDown);
    
    // Restore focus
    if (previouslyFocused && previouslyFocused.focus) {
      previouslyFocused.focus();
    }
    
    active = false;
  };
  
  return {
    activate,
    deactivate,
    update: () => {
      if (active) {
        const focusableElements = getFocusableElements();
        if (focusableElements.length > 0 && !focusableElements.includes(document.activeElement)) {
          focusableElements[0].focus();
        }
      }
    }
  };
}

/**
 * Create accessible tabs
 * @param {HTMLElement} container - Container element for tabs
 * @param {Object} options - Configuration options
 * @returns {Object} Tab control methods
 */
function createAccessibleTabs(container, options = {}) {
  if (!container || !(container instanceof HTMLElement)) {
    console.error('Invalid container provided to createAccessibleTabs');
    return null;
  }
  
  const defaults = {
    activeClass: 'active',
    inactiveClass: 'inactive',
    initialTab: 0,
    orientation: 'horizontal', // horizontal, vertical
    onTabChange: null
  };
  
  const config = { ...defaults, ...options };
  
  // Find tab elements
  const tabList = container.querySelector('[role="tablist"]');
  if (!tabList) {
    console.error('No tablist found in container');
    return null;
  }
  
  const tabs = Array.from(tabList.querySelectorAll('[role="tab"]'));
  const panels = tabs.map(tab => {
    const panelId = tab.getAttribute('aria-controls');
    return document.getElementById(panelId);
  });
  
  // Set up tab navigation
  const orientation = config.orientation === 'vertical' ? 'vertical' : 'horizontal';
  tabList.setAttribute('aria-orientation', orientation);
  
  // Activate a tab
  const activateTab = (index) => {
    if (index < 0 || index >= tabs.length) return;
    
    // Update tabs
    tabs.forEach((tab, i) => {
      const isActive = i === index;
      tab.setAttribute('aria-selected', isActive.toString());
      tab.setAttribute('tabindex', isActive ? '0' : '-1');
      
      if (isActive) {
        tab.classList.remove(config.inactiveClass);
        tab.classList.add(config.activeClass);
      } else {
        tab.classList.remove(config.activeClass);
        tab.classList.add(config.inactiveClass);
      }
    });
    
    // Update panels
    panels.forEach((panel, i) => {
      if (!panel) return;
      
      const isActive = i === index;
      panel.hidden = !isActive;
      
      if (isActive) {
        panel.classList.remove(config.inactiveClass);
        panel.classList.add(config.activeClass);
      } else {
        panel.classList.remove(config.activeClass);
        panel.classList.add(config.inactiveClass);
      }
    });
    
    // Call callback if provided
    if (config.onTabChange && typeof config.onTabChange === 'function') {
      config.onTabChange(index);
    }
  };
  
  // Handle keyboard navigation
  const handleKeyDown = (event) => {
    if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) {
      return;
    }
    
    event.preventDefault();
    
    const currentIndex = tabs.findIndex(tab => tab === document.activeElement);
    let newIndex = currentIndex;
    
    switch (event.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        newIndex = currentIndex + 1;
        if (newIndex >= tabs.length) newIndex = 0;
        break;
      case 'ArrowLeft':
      case 'ArrowUp':
        newIndex = currentIndex - 1;
        if (newIndex < 0) newIndex = tabs.length - 1;
        break;
      case 'Home':
        newIndex = 0;
        break;
      case 'End':
        newIndex = tabs.length - 1;
        break;
    }
    
    tabs[newIndex].focus();
    activateTab(newIndex);
  };
  
  // Add event listeners
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(index));
    tab.addEventListener('keydown', handleKeyDown);
  });
  
  // Initialize with first tab active
  activateTab(config.initialTab);
  
  // Return API
  return {
    activateTab,
    getTabs: () => tabs,
    getPanels: () => panels,
    getCurrentIndex: () => tabs.findIndex(tab => tab.getAttribute('aria-selected') === 'true')
  };
}

// Export the utility functions
window.APa11y = {
  setARIA,
  srOnly,
  makeFocusable,
  createLiveRegion,
  announce,
  createSkipLink,
  trackFocus,
  createFocusTrap,
  createAccessibleTabs
};