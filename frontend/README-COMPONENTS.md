# Agent Provocateur UI Component Library

This directory contains the UI component library for Agent Provocateur. The library provides standardized, accessible components and utilities for building consistent interfaces.

## Directory Structure

```
frontend/
├── static/
│   ├── css/
│   │   ├── main.css              # Main stylesheet that imports all components
│   │   └── components/           # Component-specific styles
│   │       └── base.css          # Base component styles
│   └── js/
│       ├── components/           # UI components
│       │   └── ui-components.js  # Core UI component library
│       ├── utils/                # Utility functions
│       │   ├── a11y.js           # Accessibility utilities
│       │   ├── common.js         # Common utility functions
│       │   ├── errorHandler.js   # Error handling utilities
│       │   └── logger.js         # Logging utilities
│       └── api/                  # API clients
│           └── core-api.js       # Core API client
├── templates/
│   └── index-new.html           # New template incorporating component library
└── README-COMPONENTS.md         # This file
```

## Getting Started

### Including the Component Library

The component library is automatically included when using the standard application template (`index-new.html`). If you're creating a new page, include the necessary files:

```html
<!-- CSS -->
<link rel="stylesheet" href="/static/css/main.css">

<!-- Utilities -->
<script src="/static/js/utils/logger.js"></script>
<script src="/static/js/utils/errorHandler.js"></script>
<script src="/static/js/utils/common.js"></script>
<script src="/static/js/utils/a11y.js"></script>

<!-- Components -->
<script src="/static/js/components/ui-components.js"></script>

<!-- API Client -->
<script src="/static/js/api/core-api.js"></script>
```

### Using Components

All components are accessible through the `APComponents` namespace:

```javascript
// Create a button
const button = APComponents.createButton({
  text: 'Save Changes',
  type: 'primary',
  onClick: () => saveChanges()
});

// Add to the DOM
document.getElementById('buttonContainer').appendChild(button);

// Create a card
const card = APComponents.createCard({
  title: 'Document Information',
  content: '<p>This is the card content</p>'
});

// Add to the DOM
document.getElementById('cardContainer').appendChild(card);
```

## Available Components and Utilities

### UI Components

- **Buttons**: `APComponents.createButton(options)`
- **Loading Spinners**: `APComponents.createLoadingSpinner(options)`
- **Cards**: `APComponents.createCard(options)`
- **Alerts/Notifications**: `APComponents.createAlert(options)`
- **Form Inputs**: `APComponents.createFormInput(options)`
- **Modals**: `APComponents.createModal(options)`

### Utilities

- **Date Formatting**: `APUtils.formatDate(date, options)`
- **XML Formatting**: `APUtils.formatXml(xml)`
- **File Size Formatting**: `APUtils.formatFileSize(bytes, decimals)`
- **ID Generation**: `APUtils.generateId(prefix)`
- **Clipboard Operations**: `APUtils.copyToClipboard(text)`
- **Text Utilities**: `APUtils.truncateText(text, length, suffix)`
- **System Status Checking**: `APUtils.checkSystemPorts()`
- **File Download**: `APUtils.downloadFile(content, fileName, mimeType)`

### Accessibility Helpers

- **ARIA Attributes**: `APa11y.setARIA(element, attributes)`
- **Screen Reader Text**: `APa11y.srOnly(text, tagName)`
- **Focusable Elements**: `APa11y.makeFocusable(element, includeFocusRing)`
- **Live Regions**: `APa11y.createLiveRegion(options)`
- **Screen Reader Announcements**: `APa11y.announce(message, options)`
- **Skip Links**: `APa11y.createSkipLink(targetId, text)`
- **Focus Tracking**: `APa11y.trackFocus(element, callback)`
- **Focus Trap (for Modals)**: `APa11y.createFocusTrap(container)`
- **Accessible Tabs**: `APa11y.createAccessibleTabs(container, options)`

### Error Handling

- **Format API Errors**: `errorHandler.formatApiError(error, defaultMessage)`
- **Display Errors**: `errorHandler.displayError(message, containerId, options)`
- **Display Success Messages**: `errorHandler.displaySuccess(message, containerId, options)`

### Logging

- **Error Logs**: `apLogger.error(message, ...args)`
- **Warning Logs**: `apLogger.warn(message, ...args)`
- **Info Logs**: `apLogger.info(message, ...args)`
- **Debug Logs**: `apLogger.debug(message, ...args)`
- **Verbose Logs**: `apLogger.verbose(message, ...args)`
- **API Logs**: `apLogger.api(message, ...args)`
- **UI Logs**: `apLogger.ui(message, ...args)`
- **Data Logs**: `apLogger.data(message, ...args)`
- **Performance Measurement**: `apLogger.time(label)` and `apLogger.timeEnd(label)`

### API Clients

- **Core Client**: `APApi.client.get(url, params, options)`
- **Resource APIs**: `APApi.documents.getAll()`, `APApi.documents.getById(id)`, etc.
- **File Uploads**: `APApi.client.uploadFile(url, file, additionalData, progressCallback)`

## Detailed Documentation

For detailed documentation and examples, refer to:

- [Component Library Documentation](/docs/guides/component_library.md)
- [UI Improvement Plan](/docs/guides/ui_improvement_plan.md)

## CSS Classes

The component library comes with a set of CSS classes for styling elements. These are available in the main stylesheet and can be used directly in HTML.

```html
<!-- Card example -->
<div class="ap-card">
  <div class="ap-card-header">
    <h3 class="ap-card-title">Card Title</h3>
  </div>
  <div class="ap-card-body">
    Card content
  </div>
  <div class="ap-card-footer">
    <button class="ap-btn ap-btn-primary">Primary Action</button>
    <button class="ap-btn ap-btn-secondary">Secondary Action</button>
  </div>
</div>
```

See the [Component Library Documentation](/docs/guides/component_library.md) for a full list of available CSS classes.

## Best Practices

1. **Use Components**: Use the component library for all new UI elements
2. **Follow Accessibility Guidelines**: Ensure all components are keyboard accessible and screen reader friendly
3. **Standardize Error Handling**: Use the error handler for all error displays
4. **Centralize Logging**: Use the logger for all console output
5. **Structure API Calls**: Use the API client for all backend communication
6. **Document Changes**: Update documentation when adding or modifying components
7. **Test Across Devices**: Ensure components work on mobile, tablet, and desktop viewports