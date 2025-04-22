/**
 * UI Components for Agent Provocateur
 * Shared components for consistent UI across the application
 */

// Create namespace for components
window.APComponents = window.APComponents || {};

/**
 * Create a loading spinner component
 * @param {Object} options - Configuration options
 * @returns {HTMLElement} The loading spinner element
 */
function createLoadingSpinner(options = {}) {
  const defaults = {
    size: 'medium', // small, medium, large
    color: 'blue',  // blue, green, indigo, purple
    text: '',       // Optional loading text
    inline: false   // Whether to display inline or as a centered div
  };
  
  const config = { ...defaults, ...options };
  
  // Map size to classes
  const sizeMap = {
    small: { spinner: 'h-4 w-4 border-2', text: 'text-xs' },
    medium: { spinner: 'h-8 w-8 border-2', text: 'text-sm' },
    large: { spinner: 'h-12 w-12 border-3', text: 'text-base' }
  };
  
  // Map color to classes
  const colorMap = {
    blue: 'border-blue-500',
    green: 'border-green-500',
    indigo: 'border-indigo-500',
    purple: 'border-purple-500'
  };
  
  const sizeClass = sizeMap[config.size] || sizeMap.medium;
  const colorClass = colorMap[config.color] || colorMap.blue;
  
  // Create container element
  const container = document.createElement('div');
  container.className = config.inline ? 'inline-flex items-center' : 'flex justify-center items-center';
  
  // Create spinner element
  const spinner = document.createElement('div');
  spinner.className = `animate-spin rounded-full ${sizeClass.spinner} border-t-transparent border-b-transparent ${colorClass}`;
  container.appendChild(spinner);
  
  // Add text if provided
  if (config.text) {
    const textEl = document.createElement('span');
    textEl.className = `ml-3 ${sizeClass.text}`;
    textEl.textContent = config.text;
    container.appendChild(textEl);
  }
  
  return container;
}

/**
 * Create a card container component
 * @param {Object} options - Configuration options
 * @returns {HTMLElement} The card element
 */
function createCard(options = {}) {
  const defaults = {
    title: '',
    content: '',
    padding: 'normal', // none, small, normal, large
    shadow: 'normal',  // none, small, normal, large
    rounded: true,
    headerActions: null // HTML content for header actions
  };
  
  const config = { ...defaults, ...options };
  
  // Map padding to classes
  const paddingMap = {
    none: 'p-0',
    small: 'p-2',
    normal: 'p-4',
    large: 'p-6'
  };
  
  // Map shadow to classes
  const shadowMap = {
    none: '',
    small: 'shadow-sm',
    normal: 'shadow',
    large: 'shadow-md'
  };
  
  const paddingClass = paddingMap[config.padding] || paddingMap.normal;
  const shadowClass = shadowMap[config.shadow] || shadowMap.normal;
  const roundedClass = config.rounded ? 'rounded-lg' : '';
  
  // Create card element
  const card = document.createElement('div');
  card.className = `bg-white ${shadowClass} ${roundedClass} ${paddingClass}`;
  
  // Add title if provided
  if (config.title) {
    const header = document.createElement('div');
    header.className = 'flex justify-between items-center mb-4';
    
    const title = document.createElement('h3');
    title.className = 'text-lg font-medium text-gray-900';
    title.textContent = config.title;
    header.appendChild(title);
    
    // Add header actions if provided
    if (config.headerActions) {
      const actions = document.createElement('div');
      if (typeof config.headerActions === 'string') {
        actions.innerHTML = config.headerActions;
      } else if (config.headerActions instanceof HTMLElement) {
        actions.appendChild(config.headerActions);
      }
      header.appendChild(actions);
    }
    
    card.appendChild(header);
  }
  
  // Add content
  if (config.content) {
    if (typeof config.content === 'string') {
      const content = document.createElement('div');
      content.innerHTML = config.content;
      card.appendChild(content);
    } else if (config.content instanceof HTMLElement) {
      card.appendChild(config.content);
    }
  }
  
  return card;
}

/**
 * Create a button component
 * @param {Object} options - Configuration options
 * @returns {HTMLElement} The button element
 */
function createButton(options = {}) {
  const defaults = {
    text: 'Button',
    type: 'primary', // primary, secondary, danger, success, outline
    size: 'medium',  // small, medium, large
    disabled: false,
    onClick: null,
    icon: null      // Optional icon HTML
  };
  
  const config = { ...defaults, ...options };
  
  // Map type to classes
  const typeMap = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    success: 'bg-green-600 hover:bg-green-700 text-white',
    outline: 'bg-white border border-gray-300 hover:bg-gray-50 text-gray-700'
  };
  
  // Map size to classes
  const sizeMap = {
    small: 'px-2 py-1 text-xs',
    medium: 'px-4 py-2 text-sm',
    large: 'px-6 py-3 text-base'
  };
  
  const typeClass = typeMap[config.type] || typeMap.primary;
  const sizeClass = sizeMap[config.size] || sizeMap.medium;
  const disabledClass = config.disabled ? 'opacity-50 cursor-not-allowed' : '';
  
  // Create button element
  const button = document.createElement('button');
  button.className = `${typeClass} ${sizeClass} ${disabledClass} rounded font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition duration-150 ease-in-out`;
  button.disabled = config.disabled;
  
  // Add icon if provided
  if (config.icon) {
    button.innerHTML = `
      <span class="flex items-center">
        ${config.icon}
        ${config.text ? `<span class="${config.icon ? 'ml-2' : ''}">${config.text}</span>` : ''}
      </span>
    `;
  } else {
    button.textContent = config.text;
  }
  
  // Add click handler if provided
  if (config.onClick && typeof config.onClick === 'function') {
    button.addEventListener('click', config.onClick);
  }
  
  return button;
}

/**
 * Create an alert/notification component
 * @param {Object} options - Configuration options
 * @returns {HTMLElement} The alert element
 */
function createAlert(options = {}) {
  const defaults = {
    type: 'info',   // info, success, warning, error
    title: '',      // Optional title
    message: '',    // Required message
    dismissible: false,
    icon: true,
    onDismiss: null
  };
  
  const config = { ...defaults, ...options };
  
  // Map type to classes and icons
  const typeMap = {
    info: {
      classes: 'bg-blue-100 border-blue-400 text-blue-700',
      icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />'
    },
    success: {
      classes: 'bg-green-100 border-green-400 text-green-700',
      icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />'
    },
    warning: {
      classes: 'bg-yellow-100 border-yellow-400 text-yellow-700',
      icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />'
    },
    error: {
      classes: 'bg-red-100 border-red-400 text-red-700',
      icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />'
    }
  };
  
  const alertType = typeMap[config.type] || typeMap.info;
  
  // Create alert element
  const alert = document.createElement('div');
  alert.className = `${alertType.classes} border-l-4 px-4 py-3 rounded relative`;
  alert.setAttribute('role', 'alert');
  
  // Create inner content
  let innerHTML = `
    <div class="flex">
      ${config.icon ? `
        <div class="py-1">
          <svg class="h-6 w-6 mr-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            ${alertType.icon}
          </svg>
        </div>
      ` : ''}
      <div>
        ${config.title ? `<p class="font-bold">${config.title}</p>` : ''}
        <p class="text-sm">${config.message}</p>
      </div>
    </div>
  `;
  
  // Add dismiss button if dismissible
  if (config.dismissible) {
    innerHTML += `
      <button class="absolute top-0 right-0 p-2">
        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    `;
  }
  
  alert.innerHTML = innerHTML;
  
  // Add dismiss handler if dismissible
  if (config.dismissible) {
    const dismissButton = alert.querySelector('button');
    dismissButton.addEventListener('click', () => {
      alert.remove();
      if (config.onDismiss && typeof config.onDismiss === 'function') {
        config.onDismiss();
      }
    });
  }
  
  return alert;
}

/**
 * Create a basic form input component
 * @param {Object} options - Configuration options
 * @returns {HTMLElement} The input container element
 */
function createFormInput(options = {}) {
  const defaults = {
    type: 'text',     // text, email, password, number, etc.
    id: '',           // Required for label association
    name: '',         // Input name attribute
    label: '',        // Label text
    placeholder: '',
    value: '',
    required: false,
    disabled: false,
    errorMessage: '', // Error message to display
    helpText: '',     // Help text below input
    onChange: null,   // Change callback
    className: ''     // Additional class names
  };
  
  const config = { ...defaults, ...options };
  
  if (!config.id) {
    console.error('Form input requires an id attribute');
    return null;
  }
  
  // Create container
  const container = document.createElement('div');
  container.className = 'mb-4';
  
  // Add label if provided
  if (config.label) {
    const label = document.createElement('label');
    label.setAttribute('for', config.id);
    label.className = 'block text-sm font-medium text-gray-700 mb-1';
    
    // Add required indicator
    if (config.required) {
      label.innerHTML = `${config.label} <span class="text-red-500">*</span>`;
    } else {
      label.textContent = config.label;
    }
    
    container.appendChild(label);
  }
  
  // Create input element
  const input = document.createElement('input');
  input.type = config.type;
  input.id = config.id;
  input.className = `block w-full px-3 py-2 border ${config.errorMessage ? 'border-red-300' : 'border-gray-300'} rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${config.className}`;
  
  // Set attributes
  if (config.name) input.name = config.name;
  if (config.placeholder) input.placeholder = config.placeholder;
  if (config.value) input.value = config.value;
  if (config.required) input.required = true;
  if (config.disabled) input.disabled = true;
  
  // Add event listener if provided
  if (config.onChange && typeof config.onChange === 'function') {
    input.addEventListener('change', config.onChange);
  }
  
  container.appendChild(input);
  
  // Add error message if provided
  if (config.errorMessage) {
    const error = document.createElement('p');
    error.className = 'mt-1 text-xs text-red-600';
    error.textContent = config.errorMessage;
    container.appendChild(error);
  }
  
  // Add help text if provided
  if (config.helpText) {
    const help = document.createElement('p');
    help.className = 'mt-1 text-xs text-gray-500';
    help.textContent = config.helpText;
    container.appendChild(help);
  }
  
  return container;
}

/**
 * Create a basic modal dialog
 * @param {Object} options - Configuration options
 * @returns {Object} Modal object with show and hide methods
 */
function createModal(options = {}) {
  const defaults = {
    title: 'Modal Title',
    content: '',
    size: 'medium',      // small, medium, large, full
    closeOnOutsideClick: true,
    showClose: true,
    onClose: null,
    buttons: []          // Array of button configs
  };
  
  const config = { ...defaults, ...options };
  
  // Map size to width class
  const sizeMap = {
    small: 'max-w-md',
    medium: 'max-w-lg',
    large: 'max-w-2xl',
    full: 'max-w-full mx-4'
  };
  
  const sizeClass = sizeMap[config.size] || sizeMap.medium;
  
  // Create modal elements
  const modalId = `modal-${Math.random().toString(36).substr(2, 9)}`;
  
  const modalHTML = `
    <div id="${modalId}" class="fixed inset-0 z-50 overflow-y-auto hidden" role="dialog" aria-modal="true">
      <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity modal-backdrop"></div>
        
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle ${sizeClass} w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <div class="flex justify-between items-center">
                  <h3 class="text-lg leading-6 font-medium text-gray-900" id="${modalId}-title">
                    ${config.title}
                  </h3>
                  ${config.showClose ? `
                    <button type="button" class="modal-close">
                      <span class="sr-only">Close</span>
                      <svg class="h-6 w-6 text-gray-400 hover:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  ` : ''}
                </div>
                <div class="mt-4 modal-content">
                  ${typeof config.content === 'string' ? config.content : ''}
                </div>
              </div>
            </div>
          </div>
          ${config.buttons.length > 0 ? `
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              ${config.buttons.map((btn, index) => `
                <button type="button" class="modal-btn mt-3 w-full inline-flex justify-center rounded-md border ${btn.type === 'primary' 
                  ? 'border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500' 
                  : btn.type === 'danger'
                    ? 'border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500'
                    : 'border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                } sm:ml-3 sm:w-auto sm:text-sm" data-btn-index="${index}">
                  ${btn.text}
                </button>
              `).join('')}
            </div>
          ` : ''}
        </div>
      </div>
    </div>
  `;
  
  // Create modal object
  const modalObj = {
    id: modalId,
    
    // Show the modal
    show: function() {
      // Create the modal if it doesn't exist
      if (!document.getElementById(modalId)) {
        const temp = document.createElement('div');
        temp.innerHTML = modalHTML;
        document.body.appendChild(temp.firstElementChild);
        
        const modal = document.getElementById(modalId);
        
        // Set up event listeners
        if (config.showClose) {
          const closeBtn = modal.querySelector('.modal-close');
          closeBtn.addEventListener('click', this.hide.bind(this));
        }
        
        // Set up button event listeners
        const buttons = modal.querySelectorAll('.modal-btn');
        buttons.forEach(button => {
          button.addEventListener('click', (e) => {
            const index = parseInt(button.getAttribute('data-btn-index'), 10);
            const btnConfig = config.buttons[index];
            
            if (btnConfig && btnConfig.onClick) {
              btnConfig.onClick(e);
            }
            
            if (btnConfig && btnConfig.closeModal !== false) {
              this.hide();
            }
          });
        });
        
        // Set up outside click listener
        if (config.closeOnOutsideClick) {
          const backdrop = modal.querySelector('.modal-backdrop');
          backdrop.addEventListener('click', this.hide.bind(this));
        }
        
        // Insert custom content element if provided
        if (config.content instanceof HTMLElement) {
          const contentContainer = modal.querySelector('.modal-content');
          contentContainer.innerHTML = '';
          contentContainer.appendChild(config.content);
        }
      }
      
      // Show the modal
      const modal = document.getElementById(modalId);
      modal.classList.remove('hidden');
      
      // Prevent body scrolling
      document.body.style.overflow = 'hidden';
      
      // Focus first focusable element
      setTimeout(() => {
        const focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusable.length) {
          focusable[0].focus();
        }
      }, 100);
      
      return this;
    },
    
    // Hide the modal
    hide: function() {
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.add('hidden');
        
        // Restore body scrolling
        document.body.style.overflow = '';
        
        // Call onClose callback if provided
        if (config.onClose && typeof config.onClose === 'function') {
          config.onClose();
        }
      }
      
      return this;
    },
    
    // Update modal content
    setContent: function(content) {
      const modal = document.getElementById(modalId);
      if (modal) {
        const contentContainer = modal.querySelector('.modal-content');
        
        if (typeof content === 'string') {
          contentContainer.innerHTML = content;
        } else if (content instanceof HTMLElement) {
          contentContainer.innerHTML = '';
          contentContainer.appendChild(content);
        }
      }
      
      return this;
    },
    
    // Update modal title
    setTitle: function(title) {
      const modal = document.getElementById(modalId);
      if (modal) {
        const titleElement = modal.querySelector(`#${modalId}-title`);
        titleElement.textContent = title;
      }
      
      return this;
    }
  };
  
  return modalObj;
}

// Assign components to namespace
window.APComponents = {
  createButton,
  createLoadingSpinner,
  createCard,
  createAlert,
  createFormInput,
  createModal
};