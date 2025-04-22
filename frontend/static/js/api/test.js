/**
 * API Client Simple Tests
 * 
 * This file contains simple tests for the API client.
 * Run it in the browser console to verify the API client works.
 */

import api from './api';

/**
 * Simple test runner for the API client
 */
export async function runApiTests() {
  const results = {
    passed: 0,
    failed: 0,
    tests: []
  };
  
  // Helper function to run a test
  async function runTest(name, test) {
    console.log(`Running test: ${name}...`);
    try {
      await test();
      console.log(`✅ Test passed: ${name}`);
      results.passed++;
      results.tests.push({ name, passed: true });
      return true;
    } catch (error) {
      console.error(`❌ Test failed: ${name}`, error);
      results.failed++;
      results.tests.push({ name, passed: false, error });
      return false;
    }
  }
  
  // Test 1: API health check
  await runTest('API Health Check', async () => {
    const health = await api.healthCheck();
    if (health.status !== 'ok') {
      throw new Error(`Unexpected health status: ${health.status}`);
    }
  });
  
  // Test 2: Get system info
  await runTest('Get System Info', async () => {
    const info = await api.getSystemInfo();
    if (!info.version) {
      throw new Error('Missing version in system info');
    }
    if (!info.backend_url) {
      throw new Error('Missing backend_url in system info');
    }
  });
  
  // Test 3: Get documents
  await runTest('Get Documents', async () => {
    const documents = await api.documents.getAllDocuments();
    if (!Array.isArray(documents)) {
      throw new Error('Documents response is not an array');
    }
  });
  
  // Test 4: Handle errors properly
  await runTest('Error Handling', async () => {
    try {
      // Attempt to get a document that doesn't exist
      await api.documents.getDocumentById('nonexistent_doc_id');
      throw new Error('Should have thrown an error for nonexistent document');
    } catch (error) {
      // This is expected, so the test passes
      if (error.message.includes('nonexistent') || error.message.includes('not found')) {
        return true;
      }
      throw error; // Re-throw if it's a different error
    }
  });
  
  // Print summary
  console.log('-------------------');
  console.log(`Tests complete: ${results.passed} passed, ${results.failed} failed`);
  console.log('-------------------');
  
  return results;
}

// Export the test runner
export default runApiTests;

// Make test runner available globally for easy browser console testing
if (typeof window !== 'undefined') {
  window.runApiTests = runApiTests;
  console.log('API tests loaded. Run tests with: runApiTests()');
}