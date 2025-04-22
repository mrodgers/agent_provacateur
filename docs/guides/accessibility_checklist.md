# Accessibility Checklist for Agent Provocateur

This document provides a comprehensive checklist for ensuring that all UI elements in Agent Provocateur meet accessibility standards. Following these guidelines will help make the application more usable for people with disabilities and improve overall user experience.

## Keyboard Navigation

- [ ] All interactive elements (links, buttons, form controls) are keyboard accessible
- [ ] Keyboard focus order is logical and follows the visual layout
- [ ] Focus indicators are clearly visible on all interactive elements
- [ ] Custom components (dropdowns, modals, tabs) can be fully operated with keyboard only
- [ ] No keyboard traps exist (places where keyboard focus gets stuck)
- [ ] Skip links are provided for navigation and repeated content
- [ ] Modal dialogs trap focus correctly when open

## Screen Readers

- [ ] All images have appropriate alt text
- [ ] Form fields have proper labels that are programmatically associated with their controls
- [ ] ARIA attributes are correctly implemented when needed
- [ ] Dynamic content changes are announced via ARIA live regions
- [ ] Tab panels, accordions, and other components use correct ARIA roles
- [ ] Pages have proper headings with a logical hierarchy (h1, h2, h3, etc.)
- [ ] Tables have proper headers and captions
- [ ] Icons and visual indicators have text alternatives

## Visual Design

- [ ] Color is not the only means of conveying information
- [ ] Text has sufficient contrast against its background (4.5:1 for normal text, 3:1 for large text)
- [ ] Form fields have clear focus states
- [ ] Error states are indicated by multiple visual cues (color, icon, text)
- [ ] Interactive elements have appropriate hover and active states
- [ ] Content is readable when zoomed to 200%
- [ ] UI is responsive and works at various screen sizes

## Forms

- [ ] All form fields have visible labels
- [ ] Required fields are clearly indicated
- [ ] Error messages are clear and helpful
- [ ] Error messages are announced to screen readers
- [ ] Form validation occurs at appropriate times
- [ ] Form inputs have appropriate autocomplete attributes where applicable
- [ ] Groups of related form controls (e.g., radio buttons) are properly grouped

## Content

- [ ] Page has a clear, descriptive title
- [ ] Link text is descriptive and makes sense out of context
- [ ] Page language is properly defined
- [ ] Content is organized under descriptive headings
- [ ] Content is written in plain language
- [ ] Technical terms and abbreviations are explained

## Navigation

- [ ] Current page/location is clearly indicated in navigation
- [ ] Navigation is consistent across the application
- [ ] Menu items are properly grouped
- [ ] Breadcrumbs or other location indicators are provided where appropriate
- [ ] Skip link is provided to bypass navigation and go directly to main content

## Media

- [ ] Audio and video have proper controls
- [ ] Videos have captions or transcripts
- [ ] No content flashes more than three times per second
- [ ] Animations can be paused or disabled

## ARIA Implementation

- [ ] ARIA is only used when necessary (native HTML elements are preferred)
- [ ] ARIA roles are used correctly
- [ ] ARIA states and properties are updated dynamically when appropriate
- [ ] ARIA attributes don't conflict with native HTML semantics
- [ ] Required ARIA children are present for parent roles
- [ ] ARIA landmark roles are used appropriately

## Testing

- [ ] Automated accessibility testing has been performed
- [ ] Manual keyboard navigation testing has been performed
- [ ] Screen reader testing has been performed with at least one screen reader
- [ ] High contrast mode testing has been performed
- [ ] Testing has been performed at various zoom levels
- [ ] Testing has been performed on mobile devices

## Implementation with Component Library

Our component library includes built-in accessibility features. Here's how to use them:

### Keyboard Navigation

```javascript
// Make element keyboard focusable
const element = APa11y.makeFocusable(myElement);

// Create a skip link
const skipLink = APa11y.createSkipLink('main-content', 'Skip to main content');
document.body.prepend(skipLink);

// Create a focus trap for modal dialogs
const focusTrap = APa11y.createFocusTrap(modalElement);
// Activate when modal opens
focusTrap.activate();
// Deactivate when modal closes
focusTrap.deactivate();
```

### Screen Reader Support

```javascript
// Add ARIA attributes
APa11y.setARIA(element, {
  label: 'Close dialog',
  expanded: false,
  hidden: true,
  role: 'button'
});

// Add screen reader only text
const srText = APa11y.srOnly('Additional context for screen readers');
element.appendChild(srText);

// Create a live region for announcements
const liveRegion = APa11y.createLiveRegion({
  ariaLive: 'polite'
});
document.body.appendChild(liveRegion);

// Announce updates to screen readers
APa11y.announce('Form submitted successfully');
```

### Forms and Interactive Elements

```javascript
// Create an accessible form input with label
const input = APComponents.createFormInput({
  type: 'text',
  id: 'username',
  name: 'username',
  label: 'Username',
  required: true,
  errorMessage: 'Username is required',
  helpText: 'Enter your username or email'
});

// Create accessible tabs
const tabs = APa11y.createAccessibleTabs(tabContainer, {
  activeClass: 'active',
  inactiveClass: 'inactive',
  orientation: 'horizontal' // or 'vertical'
});
```

## Component-Specific Guidelines

### Buttons

- Always use `button` elements for clickable actions
- Provide descriptive text that indicates the button's purpose
- Use appropriate ARIA attributes for icon-only buttons

```javascript
// Creating an accessible button with an icon
const button = APComponents.createButton({
  text: 'Delete Item',
  type: 'danger',
  icon: '<svg aria-hidden="true">...</svg>'
});
```

### Modals

- Trap focus within modal when open
- Provide a visible close button
- Return focus to triggering element when closed
- Ensure modal is properly announced to screen readers

```javascript
// Creating an accessible modal
const modal = APComponents.createModal({
  title: 'Confirm Action',
  content: 'Are you sure you want to proceed?',
  closeOnOutsideClick: true,
  showClose: true,
  onClose: () => {
    // Return focus to trigger button
    triggerButton.focus();
  }
});
```

### Form Validation

- Provide clear error messages
- Associate error messages with appropriate form fields
- Announce errors to screen readers
- Use both color and text to indicate errors

```javascript
// Display form validation errors accessibly
errorHandler.displayError(
  'Please complete all required fields',
  'form-errors',
  {
    title: 'Validation Error',
    type: 'error'
  }
);
```

### Tables

- Use proper table markup with `<th>` for headers
- Provide caption or summary where appropriate
- Use scope attributes for header cells
- Avoid complex merged cells when possible

### Loading States

- Indicate loading states with both visual and text indicators
- Ensure loading spinners have appropriate text alternatives
- Announce loading and completion to screen readers

```javascript
// Create accessible loading spinner
const spinner = APComponents.createLoadingSpinner({
  size: 'medium',
  text: 'Loading documents...'
});

// Announce loading to screen readers
APa11y.announce('Loading documents...');

// When done loading
APa11y.announce('Documents loaded successfully');
```

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/TR/WCAG21/)
- [WAI-ARIA Authoring Practices](https://www.w3.org/TR/wai-aria-practices-1.1/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [ARIA Landmarks Example](https://www.w3.org/TR/wai-aria-practices/examples/landmarks/)