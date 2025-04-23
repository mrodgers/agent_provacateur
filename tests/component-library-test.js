/**
 * Component Library Test Script
 * 
 * This script tests the functionality of the component library by simulating user interactions
 * and checking that components behave as expected. It's designed to be run in the browser
 * console while viewing the component-test page or via the test runner UI.
 * 
 * Usage:
 * 1. Open http://localhost:3002/component-test in your browser
 * 2. Open the browser console (F12 or Cmd+Option+I)
 * 3. Copy and paste this entire script into the console
 * 4. Press Enter to run the tests
 * 
 * Alternatively:
 * 1. Open http://localhost:3002/test-runner to use the graphical test runner
 * 2. Click "Run Tests" to execute all tests
 * 
 * Last updated: 2025/04/22 - Added improved promise handling, better cleanup,
 * additional utility tests, and more comprehensive a11y testing
 */

class ComponentTester {
  constructor() {
    this.testResults = {
      passed: 0,
      failed: 0,
      skipped: 0,
      pending: 0,
      details: []
    };
    
    this.startTime = new Date();
    
    // Resource tracking for cleanup
    this.timeouts = [];    // setTimeout references
    this.intervals = [];   // setInterval references
    this.listeners = [];   // Event listener tracking {element, event, listener}
    this.elements = [];    // Temporary DOM elements to remove
    this.spies = [];       // Function spies/mocks to restore
  }
  
  async runTests() {
    console.log('='.repeat(80));
    console.log('Starting Component Library Tests');
    console.log('-'.repeat(80));
    
    // Set unhandled rejection handler for better debugging
    const originalUnhandledRejection = window.onunhandledrejection;
    window.onunhandledrejection = (event) => {
      console.error('Unhandled Promise Rejection:', event.reason);
      event.preventDefault();
    };
    
    try {
      // Run setup before tests if it exists
      if (typeof this.setup === 'function') {
        await this.setup();
      }
      
      // Run each test category with error boundaries
      const testCategories = [
        this.testButtons,
        this.testSpinners,
        this.testAlerts,
        this.testForms,
        this.testCards,
        this.testModal,
        this.testLogging,
        this.testErrorHandling,
        this.testAccessibility,
        this.testCommonUtils,
        this.testResponsiveness,
        this.testPerformance
      ];
      
      // Execute each test category, continuing even if one fails
      for (const testCategory of testCategories) {
        if (typeof testCategory !== 'function') continue;
        
        try {
          await testCategory.call(this);
        } catch (categoryError) {
          console.error(`Error in test category ${testCategory.name}:`, categoryError);
          this.recordResult(`${testCategory.name} execution`, false, categoryError);
        }
      }
      
      // Wait for any pending async tests to complete
      const pendingCount = this.testResults.details.filter(d => d.status === 'pending').length;
      if (pendingCount > 0) {
        console.log(`Waiting for ${pendingCount} pending tests to complete...`);
        // Wait a bit longer for async tests
        await new Promise(resolve => {
          const timeout = setTimeout(resolve, 2000);
          this.timeouts.push(timeout);
        });
      }
      
      // Report results
      return this.reportResults();
    } catch (error) {
      console.error('Test execution failed:', error);
      // Clean up resources
      this.cleanup();
      
      return {
        passed: this.testResults.passed,
        failed: this.testResults.failed + 1, // Count the execution failure
        total: this.testResults.passed + this.testResults.failed + 1,
        passPercentage: 0
      };
    } finally {
      // Restore original unhandled rejection handler
      window.onunhandledrejection = originalUnhandledRejection;
    }
  }
  
  // Clean up all resources created during tests
  cleanup() {
    // Clear all timeouts
    this.timeouts.forEach(timeout => clearTimeout(timeout));
    this.timeouts = [];
    
    // Clear all intervals
    this.intervals.forEach(interval => clearInterval(interval));
    this.intervals = [];
    
    // Remove all event listeners
    this.listeners.forEach(({ element, event, listener }) => {
      if (element && typeof element.removeEventListener === 'function') {
        element.removeEventListener(event, listener);
      }
    });
    this.listeners = [];
    
    // Remove all created elements
    this.elements.forEach(element => {
      if (element && element.parentNode) {
        element.parentNode.removeChild(element);
      }
    });
    this.elements = [];
    
    // Restore all spied/mocked functions
    this.spies.forEach(({ obj, method, original }) => {
      if (obj && original) {
        obj[method] = original;
      }
    });
    this.spies = [];
    
    // Close any open modals
    try {
      const modal = document.querySelector('.ap-modal, [role="dialog"]');
      if (modal && !modal.classList.contains('hidden') && window.testModal) {
        window.testModal.hide();
      }
    } catch (e) {
      console.error('Error closing modal during cleanup:', e);
    }
    
    // Clear error and message containers
    try {
      const errorContainer = document.getElementById('error-container');
      const messageContainer = document.getElementById('message-container');
      if (errorContainer) errorContainer.innerHTML = '';
      if (messageContainer) messageContainer.innerHTML = '';
    } catch (e) {
      console.error('Error clearing message containers during cleanup:', e);
    }
  }
  
  // Helper for mocking/spying on functions during tests
  spyOn(obj, method, mockFn) {
    const original = obj[method];
    
    // Store original for restoration later
    this.spies.push({ obj, method, original });
    
    // Replace with spy/mock
    obj[method] = mockFn || function(...args) {
      obj[method].calls = obj[method].calls || [];
      obj[method].calls.push(args);
      return original.apply(this, args);
    };
    
    return obj[method];
  }
  
  async testButtons() {
    this.log('Testing Button Components');
    
    // Test that buttons exist
    this.test('Button container exists', () => {
      const container = document.getElementById('button-container');
      return !!container;
    });
    
    // Count buttons
    this.test('At least 5 buttons are rendered', () => {
      const container = document.getElementById('button-container');
      const buttons = container.querySelectorAll('button');
      return buttons.length >= 5;
    });
    
    // Test button click events
    this.test('Primary button click triggers logger', async () => {
      const container = document.getElementById('button-container');
      const primaryButton = Array.from(container.querySelectorAll('button')).find(
        btn => btn.textContent.includes('Primary')
      );
      
      if (!primaryButton) return false;
      
      // Create a promise that resolves when the logger is called
      const logPromise = new Promise(resolve => {
        const originalInfo = apLogger.ui;
        apLogger.ui = (msg, ...args) => {
          originalInfo(msg, ...args);
          if (msg.includes('Primary button clicked')) {
            // Restore original immediately to avoid affecting other tests
            apLogger.ui = originalInfo;
            resolve(true);
          }
        };
        
        // Restore original after 500ms in case of failure
        const timeout = setTimeout(() => {
          apLogger.ui = originalInfo;
          resolve(false);
        }, 500);
        this.timeouts.push(timeout);
      });
      
      // Click the button
      primaryButton.click();
      
      // Wait for the logger call
      return await logPromise;
    });
    
    // Test disabled button
    this.test('Disabled button has correct attributes', () => {
      const container = document.getElementById('button-container');
      const disabledButton = Array.from(container.querySelectorAll('button')).find(
        btn => btn.textContent.includes('Disabled')
      );
      
      if (!disabledButton) return false;
      
      return disabledButton.disabled === true && 
             disabledButton.classList.contains('opacity-50');
    });
    
    // Test button styling
    this.test('Buttons have distinct styling based on type', () => {
      const container = document.getElementById('button-container');
      const buttons = container.querySelectorAll('button');
      
      // Collect button background colors
      const bgColors = new Set();
      buttons.forEach(button => {
        const style = window.getComputedStyle(button);
        bgColors.add(style.backgroundColor);
      });
      
      // Different button types should have different background colors
      return bgColors.size > 1;
    });
  }
  
  async testSpinners() {
    this.log('Testing Loading Spinners');
    
    // Test spinner container
    this.test('Spinner container exists', () => {
      const container = document.getElementById('spinner-container');
      return !!container;
    });
    
    // Test spinner rendering
    this.test('3 spinners are rendered', () => {
      const container = document.getElementById('spinner-container');
      // Look for the spinner elements with animation
      const spinners = container.querySelectorAll('.animate-spin');
      return spinners.length === 3;
    });
    
    // Test spinner sizes
    this.test('Spinners have different sizes', () => {
      const container = document.getElementById('spinner-container');
      const spinners = container.querySelectorAll('.animate-spin');
      
      const sizes = new Set();
      spinners.forEach(spinner => {
        // Get the height which should differ by size
        const style = window.getComputedStyle(spinner);
        sizes.add(style.height);
      });
      
      return sizes.size > 1;
    });
    
    // Test spinner text
    this.test('Spinners have appropriate text labels', () => {
      const container = document.getElementById('spinner-container');
      const spinnerContainers = Array.from(container.children);
      
      // Each spinner should have a text label
      return spinnerContainers.every(spinnerContainer => {
        const text = spinnerContainer.textContent.trim();
        return text.length > 0;
      });
    });
  }
  
  async testAlerts() {
    this.log('Testing Alert Components');
    
    // Test alert container
    this.test('Alert container exists', () => {
      const container = document.getElementById('alert-container');
      return !!container;
    });
    
    // Test alert rendering
    this.test('4 alerts are rendered', () => {
      const container = document.getElementById('alert-container');
      const alerts = container.children;
      return alerts.length === 4;
    });
    
    // Test alert types
    this.test('Alerts have different types', () => {
      const container = document.getElementById('alert-container');
      const alerts = Array.from(container.children);
      
      // Collect alert background colors (different types should have different colors)
      const bgColors = new Set();
      alerts.forEach(alert => {
        const style = window.getComputedStyle(alert);
        bgColors.add(style.backgroundColor);
      });
      
      return bgColors.size > 1;
    });
    
    // Test alert dismissal
    this.test('Alerts can be dismissed', async () => {
      const container = document.getElementById('alert-container');
      const alerts = container.querySelectorAll('[role="alert"]');
      
      if (alerts.length === 0) return false;
      
      // Check if any alert has a close button
      let closeButton = null;
      for (const alert of alerts) {
        const button = alert.querySelector('button');
        if (button) {
          closeButton = button;
          break;
        }
      }
      
      if (!closeButton) return false;
      
      const alertCountBefore = container.querySelectorAll('[role="alert"]').length;
      
      // Click the close button
      closeButton.click();
      
      // Wait for animation
      await new Promise(resolve => {
        const timeout = setTimeout(resolve, 100);
        this.timeouts.push(timeout);
      });
      
      const alertCountAfter = container.querySelectorAll('[role="alert"]').length;
      
      return alertCountBefore > alertCountAfter;
    });
  }
  
  async testForms() {
    this.log('Testing Form Components');
    
    // Test form container
    this.test('Form container exists', () => {
      const form = document.getElementById('test-form');
      return !!form;
    });
    
    // Test input rendering
    this.test('Form has 4 inputs and 1 button', () => {
      const form = document.getElementById('test-form');
      const inputs = form.querySelectorAll('input');
      const buttons = form.querySelector('button');
      
      return inputs.length === 4 && !!buttons;
    });
    
    // Test input labels
    this.test('Form inputs have proper labels', () => {
      const form = document.getElementById('test-form');
      const inputs = form.querySelectorAll('input');
      
      // Check that each input has an associated label
      return Array.from(inputs).every(input => {
        if (!input.id) return false;
        
        const label = form.querySelector(`label[for="${input.id}"]`);
        return !!label;
      });
    });
    
    // Test form validation
    this.test('Form validation shows error on empty fields', async () => {
      const form = document.getElementById('test-form');
      const submitButton = form.querySelector('button');
      
      if (!submitButton) return false;
      
      // Clear any existing errors
      const errorContainer = document.getElementById('error-container');
      if (errorContainer) {
        errorContainer.innerHTML = '';
      }
      
      // Clear form fields
      form.querySelectorAll('input:not([disabled])').forEach(input => {
        input.value = '';
      });
      
      // Create a promise that resolves when the error handler is called
      const errorPromise = new Promise(resolve => {
        const originalDisplayError = errorHandler.displayError;
        errorHandler.displayError = (...args) => {
          originalDisplayError(...args);
          // Restore original immediately
          errorHandler.displayError = originalDisplayError;
          resolve(true);
        };
        
        // Restore original after 800ms in case of failure
        const timeout = setTimeout(() => {
          errorHandler.displayError = originalDisplayError;
          resolve(false);
        }, 800);
        this.timeouts.push(timeout);
      });
      
      // Submit the form
      submitButton.click();
      
      // Wait for the error handler call
      const errorDisplayed = await errorPromise;
      
      // Check if error container has content
      return errorDisplayed && errorContainer && errorContainer.innerHTML.trim() !== '';
    });
    
    // Test form submission with valid data
    this.test('Form submission shows success on valid data', async () => {
      const form = document.getElementById('test-form');
      const submitButton = form.querySelector('button');
      
      if (!submitButton) return false;
      
      // Fill in form fields
      const usernameInput = document.getElementById('username');
      const emailInput = document.getElementById('email');
      const passwordInput = document.getElementById('password');
      
      if (!usernameInput || !emailInput || !passwordInput) return false;
      
      usernameInput.value = 'testuser';
      emailInput.value = 'test@example.com';
      passwordInput.value = 'password123';
      
      // Create a promise that resolves when the success handler is called
      const successPromise = new Promise(resolve => {
        const originalDisplaySuccess = errorHandler.displaySuccess;
        errorHandler.displaySuccess = (...args) => {
          originalDisplaySuccess(...args);
          // Restore original immediately
          errorHandler.displaySuccess = originalDisplaySuccess;
          resolve(true);
        };
        
        // Restore original after 800ms in case of failure
        const timeout = setTimeout(() => {
          errorHandler.displaySuccess = originalDisplaySuccess;
          resolve(false);
        }, 800);
        this.timeouts.push(timeout);
      });
      
      // Submit the form
      submitButton.click();
      
      // Wait for the success handler call
      const successDisplayed = await successPromise;
      
      // Check if message container has content
      const messageContainer = document.getElementById('message-container');
      return successDisplayed && messageContainer && messageContainer.innerHTML.trim() !== '';
    });
  }
  
  async testCards() {
    this.log('Testing Card Components');
    
    // Test card container
    this.test('Card container exists', () => {
      const container = document.getElementById('card-container');
      return !!container;
    });
    
    // Test card rendering
    this.test('2 cards are rendered', () => {
      const container = document.getElementById('card-container');
      const cards = container.children;
      return cards.length === 2;
    });
    
    // Test card titles
    this.test('Cards have correct titles', () => {
      const container = document.getElementById('card-container');
      const cards = container.children;
      
      if (cards.length < 2) return false;
      
      const titles = Array.from(cards).map(card => {
        const title = card.querySelector('h3');
        return title ? title.textContent.trim() : '';
      });
      
      return titles.includes('Basic Card') && titles.includes('Card with Actions');
    });
    
    // Test card with actions
    this.test('Card with actions has action buttons', () => {
      const container = document.getElementById('card-container');
      const actionCard = Array.from(container.children).find(card => {
        const title = card.querySelector('h3');
        return title && title.textContent.includes('Actions');
      });
      
      if (!actionCard) return false;
      
      // Check for action buttons
      const actionButtons = actionCard.querySelectorAll('button');
      return actionButtons.length > 0;
    });
  }
  
  async testModal() {
    this.log('Testing Modal Components');
    
    // Test modal button
    this.test('Modal button exists', () => {
      const container = document.getElementById('modal-container');
      const button = container.querySelector('button');
      return !!button && button.textContent.includes('Open Modal');
    });
    
    // Test opening the modal
    this.test('Modal opens when button is clicked', async () => {
      const container = document.getElementById('modal-container');
      const button = container.querySelector('button');
      
      if (!button) return false;
      
      // Click the button to open modal
      button.click();
      
      // Wait for animation
      await new Promise(resolve => {
        const timeout = setTimeout(resolve, 200);
        this.timeouts.push(timeout);
      });
      
      // Check if modal is in the DOM and visible
      const modal = document.querySelector('.ap-modal, [role="dialog"]');
      
      return !!modal && !modal.classList.contains('hidden');
    });
    
    // Test modal buttons
    this.test('Modal has cancel and confirm buttons', () => {
      const modal = document.querySelector('.ap-modal, [role="dialog"]');
      
      if (!modal) return false;
      
      const buttons = modal.querySelectorAll('button');
      const buttonTexts = Array.from(buttons).map(btn => btn.textContent.trim());
      
      return buttonTexts.includes('Cancel') && buttonTexts.includes('Confirm');
    });
    
    // Test modal content
    this.test('Modal has appropriate title and content', () => {
      const modal = document.querySelector('.ap-modal, [role="dialog"]');
      
      if (!modal) return false;
      
      const title = modal.querySelector('h3');
      const content = modal.querySelector('p');
      
      return !!title && !!content && title.textContent.trim().length > 0 && content.textContent.trim().length > 0;
    });
    
    // Test closing the modal
    this.test('Modal closes when X button is clicked', async () => {
      const modal = document.querySelector('.ap-modal, [role="dialog"]');
      
      if (!modal) return false;
      
      // Find the close button (X)
      const closeButton = modal.querySelector('.ap-modal-close, [aria-label="Close"]');
      
      if (!closeButton) return false;
      
      // Click the close button
      closeButton.click();
      
      // Wait for animation
      await new Promise(resolve => {
        const timeout = setTimeout(resolve, 200);
        this.timeouts.push(timeout);
      });
      
      // Check if modal is hidden or removed
      const modalAfterClose = document.querySelector('.ap-modal:not(.hidden), [role="dialog"]:not(.hidden)');
      
      return !modalAfterClose;
    });
  }
  
  async testLogging() {
    this.log('Testing Logging Utilities');
    
    // Test logger existence
    this.test('Logger object exists', () => {
      return !!window.apLogger && 
             typeof window.apLogger.info === 'function' &&
             typeof window.apLogger.error === 'function';
    });
    
    // Test logger levels
    this.test('Logger has all required levels', () => {
      return typeof window.apLogger.error === 'function' &&
             typeof window.apLogger.warn === 'function' &&
             typeof window.apLogger.info === 'function' &&
             typeof window.apLogger.debug === 'function' &&
             typeof window.apLogger.verbose === 'function';
    });
    
    // Test category-specific logging
    this.test('Logger has category-specific methods', () => {
      return typeof window.apLogger.api === 'function' &&
             typeof window.apLogger.ui === 'function' &&
             typeof window.apLogger.data === 'function';
    });
    
    // Test performance logging
    this.test('Logger has performance timing methods', () => {
      return typeof window.apLogger.time === 'function' &&
             typeof window.apLogger.timeEnd === 'function';
    });
  }
  
  async testErrorHandling() {
    this.log('Testing Error Handling Utilities');
    
    // Test error handler existence
    this.test('Error handler object exists', () => {
      return !!window.errorHandler &&
             typeof window.errorHandler.displayError === 'function' &&
             typeof window.errorHandler.displaySuccess === 'function';
    });
    
    // Test error types
    this.test('Error handler has error types', () => {
      return !!window.errorHandler.ErrorTypes &&
             window.errorHandler.ErrorTypes.NETWORK &&
             window.errorHandler.ErrorTypes.API;
    });
    
    // Test error formatting
    this.test('Error handler can format errors', () => {
      const testError = new Error('Test error');
      const formatted = window.errorHandler.formatApiError(testError);
      
      return formatted.message === 'Test error' &&
             formatted.type && 
             formatted.originalError === testError;
    });
    
    // Test error display
    this.test('Error handler can display errors', async () => {
      const errorContainer = document.getElementById('error-container');
      errorContainer.innerHTML = '';
      
      window.errorHandler.displayError(
        'Test error message', 
        'error-container', 
        { title: 'Test Error' }
      );
      
      return errorContainer.innerHTML.includes('Test Error') &&
             errorContainer.innerHTML.includes('Test error message');
    });
    
    // Test success display
    this.test('Error handler can display success messages', async () => {
      const messageContainer = document.getElementById('message-container');
      messageContainer.innerHTML = '';
      
      window.errorHandler.displaySuccess(
        'Test success message', 
        'message-container', 
        { title: 'Test Success' }
      );
      
      return messageContainer.innerHTML.includes('Test Success') &&
             messageContainer.innerHTML.includes('Test success message');
    });
    
    // Test retry functionality
    this.test('Error handler supports retry functionality', async () => {
      const errorContainer = document.getElementById('error-container');
      errorContainer.innerHTML = '';
      
      let retryTriggered = false;
      
      window.errorHandler.displayError(
        'Test error with retry', 
        'error-container', 
        { 
          title: 'Test Error', 
          retry: () => { retryTriggered = true; }
        }
      );
      
      // Find and click the retry button
      const retryButton = errorContainer.querySelector('button');
      if (retryButton) {
        retryButton.click();
      }
      
      return !!retryButton && retryTriggered;
    });
  }
  
  async testAccessibility() {
    this.log('Testing Accessibility Utilities');
    
    // Test a11y existence
    this.test('Accessibility utilities exist', () => {
      return !!window.APa11y &&
             typeof window.APa11y.setARIA === 'function' &&
             typeof window.APa11y.announce === 'function';
    }, { category: 'a11y' });
    
    // Test ARIA attributes
    this.test('ARIA attributes can be set', () => {
      const testDiv = document.createElement('div');
      document.body.appendChild(testDiv);
      this.elements.push(testDiv); // Track for cleanup
      
      window.APa11y.setARIA(testDiv, {
        label: 'Test Label',
        expanded: false,
        role: 'button'
      });
      
      const hasAttributes = testDiv.getAttribute('aria-label') === 'Test Label' &&
                            testDiv.getAttribute('aria-expanded') === 'false' &&
                            testDiv.getAttribute('role') === 'button';
      
      return hasAttributes;
    }, { category: 'a11y' });
    
    // Test screen reader announcement
    this.test('Screen reader announcements work', () => {
      const announcer = document.getElementById('ap-announcer');
      
      if (!announcer) return false;
      
      announcer.textContent = '';
      
      window.APa11y.announce('Test announcement');
      
      // Wait for announcement to be processed
      return announcer.textContent === 'Test announcement';
    }, { category: 'a11y' });
    
    // Test focus management
    this.test('Focus utilities work', () => {
      const testDiv = document.createElement('div');
      document.body.appendChild(testDiv);
      this.elements.push(testDiv); // Track for cleanup
      
      window.APa11y.makeFocusable(testDiv);
      
      const hasFocusableAttributes = testDiv.getAttribute('tabindex') === '0';
      
      return hasFocusableAttributes;
    }, { category: 'a11y' });
    
    // Test skip link creation
    this.test('Skip link utilities work', () => {
      const skipLink = window.APa11y.createSkipLink('main-content', 'Skip Test');
      
      const isValid = skipLink.tagName === 'A' && 
                      skipLink.href.includes('#main-content') &&
                      skipLink.textContent === 'Skip Test';
      
      return isValid;
    }, { category: 'a11y' });
    
    // Test focus trap for modals
    this.test('Focus trap works for modals', () => {
      const modalContainer = document.createElement('div');
      modalContainer.innerHTML = `
        <div class="modal">
          <button id="first">First</button>
          <input type="text" id="middle">
          <button id="last">Last</button>
        </div>
      `;
      document.body.appendChild(modalContainer);
      this.elements.push(modalContainer); // Track for cleanup
      
      // Set up focus trap
      const focusTrap = window.APa11y.createFocusTrap(modalContainer);
      
      // Check trap methods exist
      const hasMethods = typeof focusTrap.activate === 'function' && 
                         typeof focusTrap.deactivate === 'function' &&
                         typeof focusTrap.update === 'function';
      
      return hasMethods;
    }, { category: 'a11y' });
    
    // Test accessible tabs
    this.test('Accessible tabs utility creates proper ARIA attributes', () => {
      // Create a test tab structure
      const tabContainer = document.createElement('div');
      tabContainer.innerHTML = `
        <div role="tablist">
          <button id="tab1" role="tab" aria-controls="panel1">Tab 1</button>
          <button id="tab2" role="tab" aria-controls="panel2">Tab 2</button>
        </div>
        <div id="panel1" role="tabpanel">Content 1</div>
        <div id="panel2" role="tabpanel">Content 2</div>
      `;
      document.body.appendChild(tabContainer);
      this.elements.push(tabContainer); // Track for cleanup
      
      // Try to create tabs if the utility exists
      if (typeof window.APa11y.createAccessibleTabs !== 'function') {
        return false;
      }
      
      const tabs = window.APa11y.createAccessibleTabs(tabContainer);
      
      // Check if tabs functionality exists
      const hasTabsAPI = typeof tabs.activateTab === 'function' && 
                         typeof tabs.getTabs === 'function';
      
      // Check ARIA attributes
      const tab1 = document.getElementById('tab1');
      const hasCorrectAttributes = tab1 && 
                                  tab1.getAttribute('aria-selected') === 'true' && 
                                  tab1.getAttribute('tabindex') === '0';
      
      return hasTabsAPI && hasCorrectAttributes;
    }, { category: 'a11y' });
    
    // Component specific accessibility tests
    
    // Test button accessibility
    this.test('Buttons have proper accessibility attributes', () => {
      const container = document.getElementById('button-container');
      if (!container) return false;
      
      const buttons = container.querySelectorAll('button');
      if (buttons.length === 0) return false;
      
      // Check that all buttons have proper accessibility features
      return Array.from(buttons).every(button => {
        // All buttons should be focusable and have proper role
        if (button.getAttribute('role') !== null && button.getAttribute('role') !== 'button') {
          return false;
        }
        
        // Disabled buttons should communicate their state
        if (button.disabled) {
          return button.getAttribute('aria-disabled') === 'true' || 
                 button.hasAttribute('disabled');
        }
        
        return true;
      });
    }, { category: 'a11y-components' });
    
    // Test form accessibility
    this.test('Form inputs have proper accessibility attributes', () => {
      const form = document.getElementById('test-form');
      if (!form) return false;
      
      const inputs = form.querySelectorAll('input');
      if (inputs.length === 0) return false;
      
      // Check that all inputs have associated labels and required state is communicated
      return Array.from(inputs).every(input => {
        // Check for label
        if (!input.id) return false;
        
        const label = form.querySelector(`label[for="${input.id}"]`);
        if (!label) return false;
        
        // Required inputs should indicate their state
        if (input.required && !label.textContent.includes('*')) {
          return false;
        }
        
        // Disabled inputs should have aria-disabled
        if (input.disabled && input.getAttribute('aria-disabled') !== 'true' && 
            !input.hasAttribute('disabled')) {
          return false;
        }
        
        return true;
      });
    }, { category: 'a11y-components' });
    
    // Test modal accessibility
    this.test('Modal dialogs have proper accessibility attributes', async () => {
      // Open the test modal
      const modalContainer = document.getElementById('modal-container');
      if (!modalContainer) return false;
      
      const openButton = modalContainer.querySelector('button');
      if (!openButton) return false;
      
      // Click to open modal
      openButton.click();
      
      // Wait for modal to open
      await new Promise(resolve => {
        const timeout = setTimeout(resolve, 200);
        this.timeouts.push(timeout);
      });
      
      // Check modal attributes
      const modal = document.querySelector('[role="dialog"]');
      if (!modal) return false;
      
      // Check for required ARIA attributes
      const hasRequiredAttributes = 
        modal.getAttribute('role') === 'dialog' && 
        modal.getAttribute('aria-modal') === 'true' || 
        modal.querySelector('[aria-labelledby]') ||
        modal.querySelector('[aria-label]');
      
      // Check that focus is trapped
      const focusIsWithinModal = document.activeElement && modal.contains(document.activeElement);
      
      // Close the modal after checking
      const closeButton = modal.querySelector('.modal-close, [aria-label="Close"]');
      if (closeButton) {
        closeButton.click();
        
        // Wait for modal to close
        await new Promise(resolve => {
          const timeout = setTimeout(resolve, 200);
          this.timeouts.push(timeout);
        });
      }
      
      return hasRequiredAttributes && focusIsWithinModal;
    }, { category: 'a11y-components' });
    
    // Test keyboard navigation
    this.test('Components are keyboard navigable', async () => {
      // Focus the first button in the button container
      const buttonContainer = document.getElementById('button-container');
      if (!buttonContainer) return false;
      
      const firstButton = buttonContainer.querySelector('button');
      if (!firstButton) return false;
      
      // Focus the button
      firstButton.focus();
      
      // Check if focus is set correctly
      const isFocused = document.activeElement === firstButton;
      
      // Simulate pressing Tab
      const tabEvent = new KeyboardEvent('keydown', {
        key: 'Tab',
        code: 'Tab',
        bubbles: true
      });
      
      firstButton.dispatchEvent(tabEvent);
      
      // Give browser time to process the event
      await new Promise(resolve => {
        const timeout = setTimeout(resolve, 50);
        this.timeouts.push(timeout);
      });
      
      // Check if focus moved to the next focusable element
      const focusMovedToNext = document.activeElement !== firstButton;
      
      return isFocused && focusMovedToNext;
    }, { category: 'a11y-keyboard' });
    
    // Test color contrast
    this.test('Components have sufficient color contrast', () => {
      // This is a simplified test - in a real application, you would use a color contrast
      // analysis library to check WCAG compliance. Here we just check for basic indicators.
      
      // Helper to check contrast
      const hasHighContrast = (element) => {
        if (!element) return false;
        
        const style = window.getComputedStyle(element);
        const bgColor = style.backgroundColor;
        const textColor = style.color;
        
        // Basic check - if either color is not specified, we can't test
        if (bgColor === 'rgba(0, 0, 0, 0)' || textColor === '') return true;
        
        // Check for pure black text on pure white bg (definitely good contrast)
        if (textColor === 'rgb(0, 0, 0)' && bgColor === 'rgb(255, 255, 255)') return true;
        
        // This is where you'd normally use a contrast calculation algorithm
        // For this test example, we'll just check that we're not using light gray on white
        // or dark gray on black - these are typical low contrast combinations
        if (textColor.includes('rgb(200, 200, 200)') && bgColor.includes('rgb(255, 255, 255)')) {
          return false;
        }
        
        if (textColor.includes('rgb(50, 50, 50)') && bgColor.includes('rgb(0, 0, 0)')) {
          return false;
        }
        
        return true;
      };
      
      // Check buttons
      const buttons = document.querySelectorAll('button');
      const buttonsHaveGoodContrast = Array.from(buttons).every(hasHighContrast);
      
      // Check form labels
      const labels = document.querySelectorAll('label');
      const labelsHaveGoodContrast = Array.from(labels).every(hasHighContrast);
      
      return buttonsHaveGoodContrast && labelsHaveGoodContrast;
    }, { category: 'a11y-visual' });
  }
  
  async testCommonUtils() {
    this.log('Testing Common Utilities');
    
    // Test date formatting
    this.test('Date formatting utility works', () => {
      if (!window.APUtils || !window.APUtils.formatDate) return false;
      
      const date = new Date('2025-01-15T12:30:00Z');
      const formatted = window.APUtils.formatDate(date, { format: 'short', includeTime: true });
      
      return formatted.includes('2025') && formatted.includes('1/15');
    }, { category: 'common-utils' });
    
    // Test XML formatting
    this.test('XML formatting utility works', () => {
      if (!window.APUtils || !window.APUtils.formatXml) return false;
      
      const xml = '<root><child>Test</child></root>';
      const formatted = window.APUtils.formatXml(xml);
      
      return formatted.includes('&lt;root&gt;') && 
             formatted.includes('&lt;child&gt;') &&
             formatted.includes('Test');
    }, { category: 'common-utils' });
    
    // Test file size formatting
    this.test('File size formatting utility works', () => {
      if (!window.APUtils || !window.APUtils.formatFileSize) return false;
      
      const size = window.APUtils.formatFileSize(1024 * 1024);
      
      return size.includes('1') && size.includes('MB');
    }, { category: 'common-utils' });
    
    // Test ID generation
    this.test('ID generation utility works', () => {
      if (!window.APUtils || !window.APUtils.generateId) return false;
      
      const id1 = window.APUtils.generateId('test');
      const id2 = window.APUtils.generateId('test');
      
      return id1.startsWith('test-') && id2.startsWith('test-') && id1 !== id2;
    }, { category: 'common-utils' });
    
    // Test text utilities
    this.test('Text utilities work', () => {
      if (!window.APUtils || !window.APUtils.truncateText || !window.APUtils.escapeHtml) return false;
      
      const truncated = window.APUtils.truncateText('This is a long text that should be truncated', 10);
      const escaped = window.APUtils.escapeHtml('<script>alert("test")</script>');
      
      return truncated.length <= 13 && // 10 chars + ellipsis
             escaped.includes('&lt;script&gt;');
    }, { category: 'common-utils' });
    
    // Test email validation
    this.test('Email validation utility works', () => {
      if (!window.APUtils || !window.APUtils.isValidEmail) return false;
      
      // Test valid emails
      const validEmails = [
        'test@example.com',
        'user.name@domain.co.uk',
        'user+tag@example.com'
      ];
      
      // Test invalid emails
      const invalidEmails = [
        'test',
        'test@',
        '@example.com',
        'test@example'
      ];
      
      const allValidPass = validEmails.every(email => window.APUtils.isValidEmail(email));
      const allInvalidFail = invalidEmails.every(email => !window.APUtils.isValidEmail(email));
      
      return allValidPass && allInvalidFail;
    }, { category: 'common-utils' });
    
    // Test JSON validation
    this.test('JSON validation utility works', () => {
      if (!window.APUtils || !window.APUtils.isValidJson) return false;
      
      const validJson = '{"name":"test","value":123}';
      const invalidJson = '{"name":"test",value:123}';
      
      return window.APUtils.isValidJson(validJson) && !window.APUtils.isValidJson(invalidJson);
    }, { category: 'common-utils' });
    
    // Test URL parameter parsing
    this.test('URL parameter parsing works', () => {
      if (!window.APUtils || !window.APUtils.parseUrlParams) return false;
      
      const testUrl = 'https://example.com/page?param1=value1&param2=value2';
      const params = window.APUtils.parseUrlParams(testUrl);
      
      return params.param1 === 'value1' && params.param2 === 'value2';
    }, { category: 'common-utils' });
  }
  
  /**
   * Test component responsiveness at different screen sizes
   */
  async testResponsiveness() {
    this.log('Testing Component Responsiveness');
    
    // Store original viewport size
    const originalWidth = window.innerWidth;
    const originalHeight = window.innerHeight;
    
    // Helper to simulate viewport size
    const setViewportSize = (width, height) => {
      Object.defineProperty(window, 'innerWidth', { configurable: true, value: width });
      Object.defineProperty(window, 'innerHeight', { configurable: true, value: height });
      
      // Dispatch resize event
      window.dispatchEvent(new Event('resize'));
    };
    
    try {
      // Test mobile viewport (small)
      this.test('Components render properly on mobile viewport', () => {
        setViewportSize(375, 667); // iPhone 8 size
        
        // Check button container layout
        const buttonContainer = document.getElementById('button-container');
        if (!buttonContainer) return false;
        
        // In mobile view, buttons should stack or wrap
        const style = window.getComputedStyle(buttonContainer);
        return style.display === 'flex' && style.flexWrap === 'wrap';
      }, { category: 'responsive' });
      
      // Test tablet viewport (medium)
      this.test('Components render properly on tablet viewport', () => {
        setViewportSize(768, 1024); // iPad size
        
        // Check card container layout
        const cardContainer = document.getElementById('card-container');
        if (!cardContainer) return false;
        
        // Cards should start to appear side-by-side on tablet
        const style = window.getComputedStyle(cardContainer);
        return style.display.includes('grid');
      }, { category: 'responsive' });
      
      // Test desktop viewport (large)
      this.test('Components render properly on desktop viewport', () => {
        setViewportSize(1440, 900); // Laptop size
        
        // Check overall layout
        const mainContent = document.getElementById('main-content');
        if (!mainContent) return false;
        
        // Main content should have a max width
        const style = window.getComputedStyle(mainContent);
        return style.maxWidth !== 'none';
      }, { category: 'responsive' });
      
    } finally {
      // Restore original viewport size
      setViewportSize(originalWidth, originalHeight);
    }
  }
  
  /**
   * Test component performance characteristics
   */
  async testPerformance() {
    this.log('Testing Component Performance');
    
    // Test component creation speed
    this.test('Button components render efficiently', () => {
      // Create multiple buttons and measure time
      const start = performance.now();
      const iterations = 50;
      const container = document.createElement('div');
      this.elements.push(container); // Track for cleanup
      
      for (let i = 0; i < iterations; i++) {
        const button = APComponents.createButton({
          text: `Test Button ${i}`,
          type: 'primary'
        });
        container.appendChild(button);
      }
      
      const end = performance.now();
      const timePerButton = (end - start) / iterations;
      
      // Clean up the test elements
      while (container.firstChild) {
        container.removeChild(container.firstChild);
      }
      
      console.log(`Average button creation time: ${timePerButton.toFixed(2)}ms`);
      
      // Check if performance is within acceptable range (adjust threshold as needed)
      return timePerButton < 10; // Less than 10ms per button is acceptable
    }, { category: 'performance' });
    
    // Test modal open/close performance
    this.test('Modal opens and closes efficiently', async () => {
      // Create a test modal
      const modal = APComponents.createModal({
        title: 'Performance Test Modal',
        content: 'This is a test of modal performance',
        buttons: [
          { text: 'Close', type: 'primary' }
        ]
      });
      
      // Measure open time
      const openStart = performance.now();
      modal.show();
      await new Promise(resolve => {
        const timeout = setTimeout(resolve, 50); // Wait for animation
        this.timeouts.push(timeout);
      });
      const openEnd = performance.now();
      
      // Measure close time
      const closeStart = performance.now();
      modal.hide();
      await new Promise(resolve => {
        const timeout = setTimeout(resolve, 50); // Wait for animation
        this.timeouts.push(timeout);
      });
      const closeEnd = performance.now();
      
      const openTime = openEnd - openStart;
      const closeTime = closeEnd - closeStart;
      
      console.log(`Modal open time: ${openTime.toFixed(2)}ms, close time: ${closeTime.toFixed(2)}ms`);
      
      // Check if performance is within acceptable range
      return openTime < 100 && closeTime < 100; // Less than 100ms is acceptable
    }, { category: 'performance' });
    
    // Test form input responsiveness
    this.test('Form inputs handle input efficiently', async () => {
      const form = document.getElementById('test-form');
      const usernameInput = document.getElementById('username');
      
      if (!form || !usernameInput) return false;
      
      // Create a function to simulate typing
      const typeText = async (input, text) => {
        const start = performance.now();
        
        // Break it up into individual characters
        for (let i = 0; i < text.length; i++) {
          input.value = text.substring(0, i + 1);
          
          // Dispatch input event
          const inputEvent = new Event('input', { bubbles: true });
          input.dispatchEvent(inputEvent);
          
          // Wait a tiny bit between "keypresses"
          await new Promise(resolve => {
            const timeout = setTimeout(resolve, 5);
            this.timeouts.push(timeout);
          });
        }
        
        const end = performance.now();
        return end - start;
      };
      
      // Measure typing performance
      const typingTime = await typeText(usernameInput, 'performance_test_user');
      
      console.log(`Typing 20 characters took: ${typingTime.toFixed(2)}ms`);
      
      // Clear the field after testing
      usernameInput.value = '';
      
      // Check if performance is within acceptable range
      return typingTime < 500; // Less than 500ms for 20 characters is acceptable
    }, { category: 'performance' });
  }
  
  // Enhanced test helper functions
  
  /**
   * Run a test and record the result
   * @param {string} name - Test name
   * @param {Function} testFn - Test function that returns boolean or Promise<boolean>
   * @param {Object} options - Additional test options
   */
  test(name, testFn, options = {}) {
    // Support for skipping tests
    if (options.skip) {
      this.recordResult(name, 'skipped', null, options);
      return;
    }
    
    // Support for tests that are expected to fail (for development)
    const expectToFail = options.expectToFail || false;
    
    try {
      const result = testFn();
      
      if (result instanceof Promise) {
        // Track pending test
        this.testResults.pending++;
        
        // For async tests, we need to wait for the promise to resolve
        result.then(
          (asyncResult) => {
            const passed = !!asyncResult;
            // Handle tests expected to fail
            if (expectToFail) {
              this.updatePendingResult(name, !passed, 
                passed ? new Error('Test passed but was expected to fail') : null, 
                options);
            } else {
              this.updatePendingResult(name, passed, null, options);
            }
          },
          (error) => {
            // For tests expected to fail, this is actually a pass
            if (expectToFail) {
              this.updatePendingResult(name, true, null, {
                ...options,
                message: `Expected failure: ${error.message}`
              });
            } else {
              this.updatePendingResult(name, false, error, options);
            }
          }
        );
        
        // Return a placeholder for now
        this.recordResult(name, 'pending', null, options);
        return;
      }
      
      // Handle synchronous test result
      const passed = !!result;
      
      // Handle tests expected to fail
      if (expectToFail) {
        this.recordResult(name, !passed, 
          passed ? new Error('Test passed but was expected to fail') : null, 
          options);
      } else {
        this.recordResult(name, passed, null, options);
      }
    } catch (error) {
      // For tests expected to fail, this is actually a pass
      if (expectToFail) {
        this.recordResult(name, true, null, {
          ...options,
          message: `Expected failure: ${error.message}`
        });
      } else {
        this.recordResult(name, false, error, options);
      }
    }
  }
  
  /**
   * Skip a test
   * @param {string} name - Test name
   * @param {Function} testFn - Test function (won't be executed)
   * @param {string} reason - Optional reason for skipping
   */
  skip(name, testFn, reason = '') {
    this.test(name, testFn, { skip: true, skipReason: reason });
  }
  
  /**
   * Record test result
   * @param {string} name - Test name
   * @param {boolean|string} passed - Whether test passed or status string
   * @param {Error} error - Optional error object
   * @param {Object} options - Additional options
   */
  recordResult(name, passed, error = null, options = {}) {
    const isStringStatus = typeof passed === 'string';
    const status = isStringStatus ? passed : (passed ? 'passed' : 'failed');
    const category = options.category || 'general';
    
    // Handle different status types
    if (status === 'pending') {
      this.testResults.details.push({
        name,
        status,
        error: null,
        category,
        timestamp: new Date().getTime()
      });
      return;
    }
    
    if (status === 'skipped') {
      this.testResults.skipped++;
      console.log(`⏭️ SKIP: ${name}${options.skipReason ? ` (${options.skipReason})` : ''}`);
    }
    // Update counters for pass/fail
    else if (status === 'passed') {
      this.testResults.passed++;
      console.log(`✅ PASS: ${name}${options.message ? ` - ${options.message}` : ''}`);
    } else {
      this.testResults.failed++;
      console.error(`❌ FAIL: ${name}${error ? ' - ' + error.message : ''}`);
      if (error) {
        console.error(error);
      }
    }
    
    // Record details
    this.testResults.details.push({
      name,
      status,
      category,
      error: error ? error.message : null,
      timestamp: new Date().getTime(),
      message: options.message || null
    });
  }
  
  /**
   * Update a pending test result
   * @param {string} name - Test name
   * @param {boolean} passed - Whether test passed
   * @param {Error} error - Optional error object
   * @param {Object} options - Additional options
   */
  updatePendingResult(name, passed, error = null, options = {}) {
    // Find the pending result and update it
    const pendingIndex = this.testResults.details.findIndex(
      result => result.name === name && result.status === 'pending'
    );
    
    if (pendingIndex >= 0) {
      // Decrement pending counter
      this.testResults.pending--;
      
      const result = this.testResults.details[pendingIndex];
      result.status = passed ? 'passed' : 'failed';
      result.error = error ? error.message : null;
      result.message = options.message || null;
      result.completedAt = new Date().getTime();
      
      // Update counters
      if (passed) {
        this.testResults.passed++;
        console.log(`✅ PASS: ${name}${options.message ? ` - ${options.message}` : ''}`);
      } else {
        this.testResults.failed++;
        console.error(`❌ FAIL: ${name}${error ? ' - ' + error.message : ''}`);
        if (error) {
          console.error(error);
        }
      }
    }
  }
  
  /**
   * Log a test category header
   * @param {string} message - Category name or message
   */
  log(message) {
    console.log(`\n📋 ${message}`);
  }
  
  /**
   * Generate test report with statistics and details
   * @returns {Object} Test report summary
   */
  reportResults() {
    const endTime = new Date();
    const duration = (endTime - this.startTime) / 1000;
    
    // Clean up all resources
    this.cleanup();
    
    // Calculate statistics
    const passed = this.testResults.passed;
    const failed = this.testResults.failed;
    const skipped = this.testResults.skipped;
    const pending = this.testResults.details.filter(d => d.status === 'pending').length;
    const total = passed + failed + skipped + pending;
    const passPercentage = total > 0 ? (passed / (passed + failed) * 100).toFixed(1) : 0;
    
    // Calculate category statistics
    const categories = {};
    this.testResults.details.forEach(detail => {
      const category = detail.category || 'unknown';
      if (!categories[category]) {
        categories[category] = { passed: 0, failed: 0, skipped: 0, pending: 0, total: 0 };
      }
      
      categories[category][detail.status]++;
      categories[category].total++;
    });
    
    // Print summary header
    console.log('\n' + '='.repeat(80));
    console.log(`Component Library Test Results (${duration.toFixed(2)}s)`);
    console.log('-'.repeat(80));
    
    // Print main statistics
    console.log(`Total Tests: ${total}`);
    console.log(`Passed: ${passed} (${passPercentage}%)`);
    console.log(`Failed: ${failed}`);
    console.log(`Skipped: ${skipped}`);
    if (pending > 0) {
      console.log(`Pending: ${pending} (still running)`);
    }
    
    // Print category statistics
    if (Object.keys(categories).length > 1) {
      console.log('\nCategory Results:');
      Object.entries(categories).forEach(([category, stats]) => {
        const catPassRate = stats.total > 0 ? 
          (stats.passed / (stats.passed + stats.failed) * 100).toFixed(1) : 0;
        console.log(`- ${category}: ${stats.passed}/${stats.total} passed (${catPassRate}%)`);
      });
    }
    
    // Log any failures details
    const failures = this.testResults.details.filter(d => d.status === 'failed');
    if (failures.length > 0) {
      console.log('\nFailure Details:');
      failures.forEach(failure => {
        console.error(`- ${failure.name}: ${failure.error || 'Test failed'}`);
      });
    }
    
    // Check for any pending async tests
    const pendingTests = this.testResults.details.filter(d => d.status === 'pending');
    if (pendingTests.length > 0) {
      console.warn(`\nWarning: ${pendingTests.length} async tests still pending. Results may be incomplete.`);
      pendingTests.forEach(p => {
        console.warn(`- Pending: ${p.name}`);
      });
    }
    
    // Print slowest tests if we have timing information
    const testsWithTiming = this.testResults.details.filter(d => d.completedAt && d.timestamp);
    if (testsWithTiming.length > 0) {
      const sortedByDuration = [...testsWithTiming].sort((a, b) => {
        const aDuration = a.completedAt - a.timestamp;
        const bDuration = b.completedAt - b.timestamp;
        return bDuration - aDuration;
      });
      
      const slowest = sortedByDuration.slice(0, 3);
      if (slowest.length > 0) {
        console.log('\nSlowest Tests:');
        slowest.forEach(test => {
          const duration = (test.completedAt - test.timestamp) / 1000;
          console.log(`- ${test.name}: ${duration.toFixed(2)}s`);
        });
      }
    }
    
    console.log('='.repeat(80));
    
    // Return report summary
    return {
      passed,
      failed,
      skipped,
      pending,
      total,
      duration,
      passPercentage: parseFloat(passPercentage),
      categories: Object.entries(categories).map(([name, stats]) => ({
        name,
        ...stats,
        passPercentage: stats.total > 0 ? 
          parseFloat((stats.passed / (stats.passed + stats.failed) * 100).toFixed(1)) : 0
      }))
    };
  }
}

// Set up the tests with initialization
const tester = new ComponentTester();

// Add a setup method to run before tests
tester.setup = async function() {
  console.log('Setting up test environment...');
  
  // Register event listener for unhandled errors
  const errorHandler = (event) => {
    console.error('Unhandled error during tests:', event.error);
    event.preventDefault();
  };
  window.addEventListener('error', errorHandler);
  
  // Register event listener for unhandled promise rejections
  const rejectionHandler = (event) => {
    console.error('Unhandled promise rejection during tests:', event.reason);
    event.preventDefault();
  };
  window.addEventListener('unhandledrejection', rejectionHandler);
  
  // Store event listeners for cleanup
  this.listeners.push(
    { element: window, event: 'error', listener: errorHandler },
    { element: window, event: 'unhandledrejection', listener: rejectionHandler }
  );
  
  // Check if page is ready
  if (!document.getElementById('button-container')) {
    console.warn('Test page DOM elements not found, component tests may fail');
  }
  
  // Check that all required utilities are loaded
  const requiredGlobals = ['APComponents', 'APUtils', 'APa11y', 'apLogger', 'errorHandler'];
  const missingGlobals = requiredGlobals.filter(name => !window[name]);
  
  if (missingGlobals.length > 0) {
    console.warn(`Missing required utilities: ${missingGlobals.join(', ')}`);
  }
};

// Run tests and handle the promise
tester.runTests()
  .then(results => {
    console.log('Tests completed successfully');
    return results;
  })
  .catch(error => {
    console.error('Test execution failed at top level:', error);
  });