# Agent Provocateur Component Library

This guide documents the standardized UI components and utilities available in the Agent Provocateur application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [UI Components](#ui-components)
3. [Utilities](#utilities)
4. [Accessibility Helpers](#accessibility-helpers)
5. [Error Handling](#error-handling)
6. [Logging](#logging)
7. [API Clients](#api-clients)
8. [CSS Library](#css-library)

## Getting Started

All components and utilities are loaded automatically when using the standard application template. The components are accessible through global JavaScript namespaces:

```javascript
// UI Components
window.APComponents

// Utilities
window.APUtils

// Accessibility Helpers
window.APa11y

// Error Handling
window.errorHandler

// Logging
window.apLogger

// API Clients
window.APApi
```

## UI Components

UI components provide consistent, accessible interface elements. Access them through the `APComponents` namespace.

### Buttons

Create standardized buttons with proper styling and accessibility features:

```javascript
const button = APComponents.createButton({
  text: 'Save Changes',
  type: 'primary', // primary, secondary, danger, success, outline
  size: 'medium',  // small, medium, large
  disabled: false,
  onClick: () => saveChanges(),
  icon: '<svg class="h-4 w-4 mr-1">...</svg>'
});

// Add to the DOM
document.getElementById('buttonContainer').appendChild(button);
```

### Loading Spinners

Create loading indicators with consistent styling:

```javascript
const spinner = APComponents.createLoadingSpinner({
  size: 'medium', // small, medium, large
  color: 'blue',  // blue, green, indigo, purple
  text: 'Loading data...',
  inline: false
});

// Add to the DOM
document.getElementById('loadingContainer').appendChild(spinner);
```

### Cards

Create card containers for content:

```javascript
const card = APComponents.createCard({
  title: 'Document Information',
  content: '<p>This is the card content</p>',
  padding: 'normal', // none, small, normal, large
  shadow: 'normal',  // none, small, normal, large
  rounded: true,
  headerActions: '<button class="ap-btn ap-btn-sm">Edit</button>'
});

// Add to the DOM
document.getElementById('cardContainer').appendChild(card);
```

### Alerts

Create notifications and alerts:

```javascript
const alert = APComponents.createAlert({
  type: 'success', // info, success, warning, error
  title: 'Changes Saved',
  message: 'Your changes have been saved successfully.',
  dismissible: true,
  icon: true,
  onDismiss: () => console.log('Alert dismissed')
});

// Add to the DOM
document.getElementById('alertContainer').appendChild(alert);
```

### Form Inputs

Create form inputs with labels and validation:

```javascript
const input = APComponents.createFormInput({
  type: 'text',
  id: 'username',
  name: 'username',
  label: 'Username',
  placeholder: 'Enter your username',
  value: '',
  required: true,
  disabled: false,
  errorMessage: '', // Add error message if validation fails
  helpText: 'Must be at least 3 characters',
  onChange: (e) => validateUsername(e.target.value)
});

// Add to the DOM
document.getElementById('formContainer').appendChild(input);
```

### Modals

Create modal dialogs:

```javascript
const modal = APComponents.createModal({
  title: 'Confirm Action',
  content: '<p>Are you sure you want to delete this document?</p>',
  size: 'medium',      // small, medium, large, full
  closeOnOutsideClick: true,
  showClose: true,
  onClose: () => console.log('Modal closed'),
  buttons: [
    {
      text: 'Cancel',
      type: 'secondary',
      onClick: () => console.log('Cancelled')
    },
    {
      text: 'Delete',
      type: 'danger',
      onClick: () => deleteDocument(docId)
    }
  ]
});

// Show the modal
modal.show();

// Hide the modal
modal.hide();

// Update content
modal.setContent('<p>New content</p>');

// Update title
modal.setTitle('New Title');
```

## Utilities

Common utility functions are available through the `APUtils` namespace.

### Date Formatting

```javascript
const formattedDate = APUtils.formatDate('2023-01-15T12:30:00Z', {
  format: 'medium', // short, medium, long, full
  includeTime: true,
  timeFormat: '12h'  // 12h, 24h
});
// Output: Jan 15, 2023, 12:30 PM
```

### XML Formatting

```javascript
const formattedXml = APUtils.formatXml(xmlString);
// Returns properly indented, HTML-escaped XML
```

### File Size Formatting

```javascript
const size = APUtils.formatFileSize(1024 * 1024 * 3.5);
// Output: 3.5 MB
```

### ID Generation

```javascript
const id = APUtils.generateId('button');
// Output: button-a1b2c3d
```

### Clipboard Operations

```javascript
APUtils.copyToClipboard('Text to copy').then(success => {
  if (success) {
    // Show success message
  }
});
```

### Text Utilities

```javascript
// Truncate text
const truncated = APUtils.truncateText('This is a long text that needs to be truncated', 20);
// Output: This is a long text...

// HTML escaping
const escaped = APUtils.escapeHtml('<script>alert("XSS")</script>');
// Output: &lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;
```

### URL Parameter Parsing

```javascript
const params = APUtils.parseUrlParams('https://example.com?id=123&type=document');
// Output: { id: '123', type: 'document' }
```

### System Status Checking

```javascript
APUtils.checkSystemPorts().then(status => {
  console.log('Backend status:', status.backend_status);
  console.log('Ports:', status.ports);
});
```

### File Download

```javascript
APUtils.downloadFile(xmlContent, 'document.xml', 'application/xml');
```

## Accessibility Helpers

Accessibility utilities are available through the `APa11y` namespace.

### ARIA Attributes

```javascript
APa11y.setARIA(element, {
  label: 'Close dialog',
  expanded: false,
  hidden: true,
  role: 'button'
});
// Sets aria-label, aria-expanded, aria-hidden, and role
```

### Screen Reader Text

```javascript
const srText = APa11y.srOnly('Additional information for screen readers');
element.appendChild(srText);
```

### Focusable Elements

```javascript
const focusableElement = APa11y.makeFocusable(element, true);
// Makes the element focusable with keyboard and adds focus styles
```

### Live Regions

```javascript
const liveRegion = APa11y.createLiveRegion({
  ariaLive: 'polite', // polite, assertive
  ariaAtomic: true,
  ariaRelevant: 'additions text'
});
document.body.appendChild(liveRegion);
```

### Screen Reader Announcements

```javascript
APa11y.announce('File successfully uploaded', {
  ariaLive: 'polite',
  clearAfter: 3000
});
```

### Skip Links

```javascript
const skipLink = APa11y.createSkipLink('main-content', 'Skip to content');
document.body.prepend(skipLink);
```

### Focus Tracking

```javascript
const tracker = APa11y.trackFocus(button, ({ isFocused, isKeyboardFocused }) => {
  if (isKeyboardFocused) {
    // Add extra visible focus indication for keyboard users
  }
});

// Stop tracking when no longer needed
tracker.stop();
```

### Focus Trap (for Modals)

```javascript
const focusTrap = APa11y.createFocusTrap(modalElement);

// Activate when modal opens
focusTrap.activate();

// Deactivate when modal closes
focusTrap.deactivate();

// Update when modal content changes
focusTrap.update();
```

### Accessible Tabs

```javascript
const tabs = APa11y.createAccessibleTabs(tabContainer, {
  activeClass: 'active',
  inactiveClass: 'inactive',
  initialTab: 0,
  orientation: 'horizontal',
  onTabChange: (index) => console.log(`Tab ${index} activated`)
});

// Activate a specific tab
tabs.activateTab(2);
```

## Error Handling

Standardized error handling is available through the `errorHandler` namespace.

### Error Types

```javascript
const ErrorTypes = errorHandler.ErrorTypes;
// Available types: NETWORK, API, VALIDATION, AUTHENTICATION, PERMISSION, NOT_FOUND, SERVER, UNKNOWN
```

### Format API Errors

```javascript
try {
  await APApi.documents.getById('invalid-id');
} catch (error) {
  const formattedError = errorHandler.formatApiError(error, 'Failed to load document');
  console.log(formattedError.type);       // ErrorTypes.NOT_FOUND
  console.log(formattedError.message);    // Error message
  console.log(formattedError.status);     // HTTP status code
  console.log(formattedError.details);    // Additional error details
}
```

### Display Errors

```javascript
errorHandler.displayError(
  'Unable to connect to the server',
  'error-container',
  {
    title: 'Connection Error',
    details: 'Check that the backend server is running.',
    type: 'error', // error, warning, info
    retry: () => retryConnection()
  }
);
```

### Display Success Messages

```javascript
errorHandler.displaySuccess(
  'Document saved successfully',
  'message-container',
  {
    title: 'Success',
    dismissible: true,
    autoDismiss: 3000 // ms
  }
);
```

## Logging

A central logging system is available through the `apLogger` namespace.

### Log Levels

```javascript
// Standard log levels
apLogger.error('Critical error occurred:', errorObj);
apLogger.warn('Warning: approach with caution');
apLogger.info('Information: process completed');
apLogger.debug('Debug info for troubleshooting');
apLogger.verbose('Very detailed diagnostics');

// Category-specific logs
apLogger.api('API request sent to /documents');
apLogger.ui('User clicked the save button');
apLogger.data('Data transformed:', transformedData);

// Performance measurement
apLogger.time('document-processing');
// ... perform operations
apLogger.timeEnd('document-processing');
```

### Configuration

```javascript
// Set log level
apLogger.setLevel('debug');
// or
apLogger.setLevel(LogLevels.DEBUG);

// Get current configuration
const config = apLogger.getConfig();

// Clear stored logs
apLogger.clearStoredLogs();

// Retrieve stored logs
const logs = apLogger.getStoredLogs();
```

## API Clients

Standardized API clients are available through the `APApi` namespace.

### Core Client

```javascript
// Using the default client
APApi.client.get('/documents')
  .then(documents => console.log(documents))
  .catch(error => console.error(error));

// Create a custom client
const customClient = APApi.createClient({
  baseUrl: 'https://api.example.com',
  timeout: 60000,
  headers: {
    'Authorization': 'Bearer token123'
  },
  displayGlobalErrors: true
});
```

### Resource APIs

```javascript
// Documents API
APApi.documents.getAll()
  .then(documents => console.log(documents));

APApi.documents.getById('doc123')
  .then(document => console.log(document));

APApi.documents.create({
  title: 'New Document',
  content: '...'
})
  .then(newDocument => console.log(newDocument));

APApi.documents.update('doc123', {
  title: 'Updated Title'
})
  .then(updatedDocument => console.log(updatedDocument));

APApi.documents.delete('doc123')
  .then(() => console.log('Document deleted'));

// File uploads
APApi.client.uploadFile(
  '/documents/upload',
  fileObject,
  { title: 'My Document' },
  (progress) => console.log(`Upload progress: ${progress}%`)
)
  .then(response => console.log('Upload complete:', response));
```

## CSS Library

The CSS library provides consistent styling for all UI elements.

### CSS Classes

#### Layout

```html
<div class="container"><!-- Centered, max-width container --></div>
<div class="flex"><!-- Flexbox container --></div>
<div class="flex-col"><!-- Column flexbox --></div>
<div class="items-center"><!-- Center items vertically --></div>
<div class="justify-between"><!-- Space between items --></div>
<div class="gap-4"><!-- Gap between flex items --></div>
<div class="grid grid-cols-3"><!-- 3-column grid --></div>
```

#### Typography

```html
<h1 class="text-xl font-bold">Heading 1</h1>
<p class="text-gray-700">Normal text</p>
<p class="text-sm text-gray-500">Smaller, lighter text</p>
```

#### Cards

```html
<div class="ap-card">
  <div class="ap-card-header">
    <h3 class="ap-card-title">Card Title</h3>
  </div>
  <div class="ap-card-body">
    Card content goes here
  </div>
  <div class="ap-card-footer">
    Footer actions
  </div>
</div>
```

#### Buttons

```html
<button class="ap-btn ap-btn-primary">Primary Button</button>
<button class="ap-btn ap-btn-secondary">Secondary Button</button>
<button class="ap-btn ap-btn-danger">Danger Button</button>
<button class="ap-btn ap-btn-success">Success Button</button>
<button class="ap-btn ap-btn-sm">Small Button</button>
<button class="ap-btn ap-btn-lg">Large Button</button>
```

#### Alerts

```html
<div class="ap-alert ap-alert-info">
  <div class="ap-alert-title">Information</div>
  <p>This is an informational alert.</p>
</div>

<div class="ap-alert ap-alert-success">
  <div class="ap-alert-title">Success</div>
  <p>Operation completed successfully.</p>
</div>

<div class="ap-alert ap-alert-warning">
  <div class="ap-alert-title">Warning</div>
  <p>This action cannot be undone.</p>
</div>

<div class="ap-alert ap-alert-error">
  <div class="ap-alert-title">Error</div>
  <p>An error occurred while processing your request.</p>
</div>
```

#### Badges

```html
<span class="ap-badge ap-badge-blue">New</span>
<span class="ap-badge ap-badge-green">Active</span>
<span class="ap-badge ap-badge-yellow">Pending</span>
<span class="ap-badge ap-badge-red">Error</span>
<span class="ap-badge ap-badge-gray">Inactive</span>
```

#### Forms

```html
<label class="form-label" for="username">Username</label>
<input id="username" class="form-input" type="text">
<p class="form-help-text">Must be at least 3 characters.</p>

<label class="form-label" for="password">Password</label>
<input id="password" class="form-input error" type="password">
<p class="form-error-text">Password is required.</p>
```

#### Tables

```html
<table class="ap-table">
  <thead>
    <tr>
      <th>Name</th>
      <th>Email</th>
      <th>Role</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>John Doe</td>
      <td>john@example.com</td>
      <td>Admin</td>
    </tr>
  </tbody>
</table>
```

#### Loading Indicators

```html
<div class="ap-spinner"></div>
<div class="ap-spinner ap-spinner-sm"></div>
<div class="ap-spinner ap-spinner-lg"></div>

<div class="ap-loading-container">
  <div class="ap-spinner"></div>
  <p class="ap-loading-text">Loading documents...</p>
</div>
```

#### Accessibility

```html
<span class="sr-only">Text only for screen readers</span>
<a href="#main-content" class="skip-to-content">Skip to content</a>
```

#### Modals

```html
<div class="ap-modal-backdrop">
  <div class="ap-modal">
    <div class="ap-modal-header">
      <h3 class="ap-modal-title">Modal Title</h3>
      <button class="ap-modal-close">&times;</button>
    </div>
    <div class="ap-modal-body">
      Modal content goes here
    </div>
    <div class="ap-modal-footer">
      <button class="ap-btn ap-btn-secondary">Cancel</button>
      <button class="ap-btn ap-btn-primary">Confirm</button>
    </div>
  </div>
</div>
```