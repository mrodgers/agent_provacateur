# API Client Testing Strategy

This document outlines the testing strategy for the Agent Provocateur API client implementation. It provides guidance on how to verify the API client functionality and ensure its reliability for both current and future development phases.

## Testing Approach

The API client testing is designed with the following goals:

1. **Verify API client structure and functionality** independently of backend implementation
2. **Test communication with the backend** when available
3. **Provide meaningful error feedback** when backend services are unavailable
4. **Support both automated and manual testing** to accommodate different development workflows
5. **Maintain test code that will be useful across all phases** of the implementation plan

## Test Components

### 1. Core API Client Tests

These tests verify the structure and functionality of the API client itself:

- Verify all API modules are properly initialized
- Check that error handling functions work correctly
- Ensure utility functions process data as expected
- Test the consistency of the API interface

### 2. Backend Integration Tests

These tests verify communication with the backend:

- Test connectivity to backend endpoints
- Verify the client can handle backend responses correctly
- Ensure error states are properly captured and formatted
- Test retry and fallback mechanisms

### 3. End-to-End Workflow Tests

These tests verify common usage patterns:

- Document upload and retrieval workflows
- Task creation and status monitoring
- Agent management operations
- Source attribution workflows

## Test Implementation

### Test Runner UI

The API client includes a browser-based test runner available at `/api-test` that provides:

- Visual feedback on test progress
- Real-time test results
- Ability to run specific test categories
- Option to skip backend-dependent tests

### Browser-Compatible API Client

A browser-compatible version of the API client is available at `/static/js/api-browser.js`. This version:

- Works directly in the browser without module bundling
- Makes all API modules available as global variables
- Is automatically loaded on all pages via the `index.html` and `fallback.html` templates
- Implements the same interface as the ES module version

### Test Suite Structure

The test suite is organized into modules:

1. **Basic Tests**: Verify API client initialization and connectivity
2. **Document API Tests**: Test document-related operations
3. **Task API Tests**: Test task creation and management
4. **Agent API Tests**: Test agent listing and control
5. **Source API Tests**: Test source attribution functionality

### Running Tests

There are multiple ways to run the tests:

#### 1. Browser-Based Testing

1. Start the frontend server:
   ```bash
   npm run start:dev
   ```

2. Navigate to the test page:
   ```
   http://localhost:3001/api-test
   ```

3. Select test options and click "Run Tests"

#### 2. Console-Based Testing

The tests can also be run directly from the browser console:

1. Open any page of the application
2. Open the browser console
3. Run tests with:
   ```javascript
   // Run all tests
   runApiTests();
   
   // Run specific test category
   runDocumentApiTests();
   ```

#### 3. Automated Testing

The test suite can be integrated with automated testing workflows:

1. Import the test modules:
   ```javascript
   import { runAllTests } from '../src/api/testing/apiTests';
   ```

2. Run tests with options:
   ```javascript
   const results = await runAllTests({
     skipBackend: process.env.SKIP_BACKEND === 'true',
     timeout: 10000
   });
   
   // Check results
   if (results.summary.failed > 0) {
     process.exit(1);
   }
   ```

## Handling Backend Dependencies

The test suite is designed to work even when the backend is unavailable:

1. **Skip Backend Option**: Tests can be run with `skipBackend: true` to skip tests that require a working backend.

2. **Automatic Backend Detection**: The test suite automatically detects if the backend is unavailable and adapts accordingly.

3. **Fallback Testing**: Even without a backend, the test suite verifies the API client structure and error handling.

## Testing During Development

### Phase 1: Core Document APIs

- Run basic connectivity tests to verify the API client structure
- Verify the client can handle backend endpoints that are implemented
- Skip tests for endpoints that are not yet implemented

### Phase 2: Agent System & Management

- Verify agent API client modules work as expected
- Test agent operations as they become available
- Continue to run document API tests to prevent regressions

### Phase 3: Source Attribution & Verification

- Test source attribution functionality
- Verify end-to-end workflows with document processing and source attribution
- Run comprehensive test suite to ensure all modules work together

## Interpreting Test Results

When running tests, you may encounter different outcomes:

- **Passed Tests**: Functionality is working as expected
- **Failed Tests**: Something is broken that needs to be fixed
- **Skipped Tests**: Tests that were intentionally skipped (either manually or due to backend unavailability)

### Common Failure Patterns

1. **Connectivity Failures**: Usually indicate the backend is unavailable
   ```
   ❌ Test failed: API health check - Health check failed: Failed to fetch
   ```

2. **Response Format Errors**: Indicate a mismatch between client expectations and backend responses
   ```
   ❌ Test failed: Get all documents - Documents response is not an array: object
   ```

3. **Missing Functionality**: Indicate the backend has not implemented a feature
   ```
   ❌ Test failed: Get agent logs - Logs response is null or undefined
   ```

## Next Steps

1. **Integrate with CI/CD Pipeline**: Set up automated testing in the CI/CD pipeline
2. **Extend Test Coverage**: Add more detailed tests for specific features
3. **Create Visual Regression Tests**: Add tests for UI components that use the API client
4. **Implement Performance Testing**: Add tests for API performance under load