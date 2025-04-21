/**
 * API Client Comprehensive Test Suite
 * 
 * This file contains automated tests for the Agent Provocateur API client.
 * These tests are designed to verify functionality and detect regressions.
 */

import api from '../api';
import { formatApiError } from '../utils';

// Test runner utility
export class ApiTestRunner {
  constructor(options = {}) {
    this.results = {
      passed: 0,
      failed: 0,
      skipped: 0,
      tests: []
    };
    
    this.options = {
      stopOnFail: false,
      timeout: 5000, // 5 second timeout for tests
      verbose: true,
      skipBackend: false,
      ...options
    };
    
    this.onTestComplete = options.onTestComplete || (() => {});
  }
  
  /**
   * Run a test case
   * @param {string} name - Test name
   * @param {Function} testFn - Test function to run
   * @param {Object} options - Test specific options
   */
  async test(name, testFn, options = {}) {
    const testOptions = {
      timeout: this.options.timeout,
      skip: false,
      category: 'general',
      ...options
    };
    
    // Skip tests if specified
    if (testOptions.skip || (testOptions.requiresBackend && this.options.skipBackend)) {
      console.log(`⏭️ Skipping test: ${name}`);
      this.results.skipped++;
      this.results.tests.push({
        name,
        passed: null,
        skipped: true,
        category: testOptions.category
      });
      this.onTestComplete({ name, passed: null, skipped: true });
      return;
    }
    
    console.log(`🧪 Running test: ${name}...`);
    const startTime = performance.now();
    
    try {
      // Create a timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error(`Test timed out after ${testOptions.timeout}ms`)), 
          testOptions.timeout);
      });
      
      // Race the test against the timeout
      await Promise.race([
        testFn(),
        timeoutPromise
      ]);
      
      const duration = performance.now() - startTime;
      console.log(`✅ Test passed: ${name} (${duration.toFixed(2)}ms)`);
      this.results.passed++;
      this.results.tests.push({
        name,
        passed: true,
        duration,
        category: testOptions.category
      });
      this.onTestComplete({ name, passed: true, duration });
      return true;
    } catch (error) {
      const duration = performance.now() - startTime;
      console.error(`❌ Test failed: ${name} (${duration.toFixed(2)}ms)`, error);
      this.results.failed++;
      this.results.tests.push({
        name,
        passed: false,
        error: error.message || String(error),
        duration,
        category: testOptions.category
      });
      this.onTestComplete({ name, passed: false, error, duration });
      
      if (this.options.stopOnFail) {
        throw new Error(`Test failed: ${name} - ${error.message}`);
      }
      return false;
    }
  }
  
  /**
   * Get test statistics by category
   */
  getStatsByCategory() {
    const categories = {};
    
    this.results.tests.forEach(test => {
      const category = test.category || 'uncategorized';
      
      if (!categories[category]) {
        categories[category] = {
          total: 0,
          passed: 0,
          failed: 0,
          skipped: 0
        };
      }
      
      categories[category].total++;
      
      if (test.skipped) {
        categories[category].skipped++;
      } else if (test.passed) {
        categories[category].passed++;
      } else {
        categories[category].failed++;
      }
    });
    
    return categories;
  }
  
  /**
   * Print test report to console
   */
  printReport() {
    console.log('\n-------------------');
    console.log(`🧪 Test Results: ${this.results.passed} passed, ${this.results.failed} failed, ${this.results.skipped} skipped`);
    
    // Print category stats
    const categories = this.getStatsByCategory();
    console.log('\nResults by category:');
    Object.entries(categories).forEach(([category, stats]) => {
      console.log(`  ${category}: ${stats.passed}/${stats.total} passed, ${stats.failed} failed, ${stats.skipped} skipped`);
    });
    
    // Print failed tests
    if (this.results.failed > 0) {
      console.log('\nFailed tests:');
      this.results.tests
        .filter(test => !test.skipped && !test.passed)
        .forEach(test => {
          console.log(`  ❌ ${test.name}: ${test.error}`);
        });
    }
    
    console.log('-------------------');
  }
}

/**
 * Basic API Connectivity Tests
 */
export async function runBasicTests() {
  const runner = new ApiTestRunner({
    stopOnFail: false,
    verbose: true
  });
  
  // Test API client initialization
  await runner.test('API client is properly initialized', () => {
    if (!api) throw new Error('API client is not initialized');
    if (!api.documents) throw new Error('Documents API module is missing');
    if (!api.tasks) throw new Error('Tasks API module is missing');
    if (!api.agents) throw new Error('Agents API module is missing');
    if (!api.sources) throw new Error('Sources API module is missing');
    return true;
  }, { category: 'initialization' });
  
  // Test health check endpoint
  await runner.test('API health check', async () => {
    try {
      const health = await api.healthCheck();
      if (!health || health.status !== 'ok') {
        throw new Error(`Invalid health response: ${JSON.stringify(health)}`);
      }
      return true;
    } catch (error) {
      throw new Error(`Health check failed: ${error.message}`);
    }
  }, { category: 'connectivity', requiresBackend: true });
  
  // Test system info endpoint
  await runner.test('API system info', async () => {
    try {
      const info = await api.getSystemInfo();
      if (!info || !info.version) {
        throw new Error(`Invalid system info response: ${JSON.stringify(info)}`);
      }
      return true;
    } catch (error) {
      throw new Error(`System info check failed: ${error.message}`);
    }
  }, { category: 'connectivity', requiresBackend: true });
  
  // Test error handling with intentionally invalid request
  await runner.test('Error handling', async () => {
    try {
      await api.documents.getDocumentById('nonexistent_id_' + Date.now());
      // If we get here without error, the test failed
      throw new Error('Expected error for nonexistent document ID');
    } catch (error) {
      // This is expected, but make sure it's formatted properly
      const formattedError = formatApiError(error);
      if (!formattedError.message) {
        throw new Error('Formatted error is missing message property');
      }
      return true;
    }
  }, { category: 'error_handling', requiresBackend: true });
  
  runner.printReport();
  return runner.results;
}

/**
 * Document API Tests
 */
export async function runDocumentTests() {
  const runner = new ApiTestRunner({
    stopOnFail: false,
    verbose: true
  });
  
  let testDocumentId = null;
  
  // Test document listing
  await runner.test('Get all documents', async () => {
    const documents = await api.documents.getAllDocuments();
    if (!Array.isArray(documents)) {
      throw new Error(`Documents response is not an array: ${typeof documents}`);
    }
    // If we have documents, save the first ID for later tests
    if (documents.length > 0) {
      testDocumentId = documents[0].doc_id;
    }
    return true;
  }, { category: 'document_api', requiresBackend: true });
  
  // Skip the remaining tests if we don't have a document ID
  if (!testDocumentId) {
    console.log('⚠️ No documents found, skipping document detail tests');
  } else {
    // Test document retrieval
    await runner.test('Get document by ID', async () => {
      const document = await api.documents.getDocumentById(testDocumentId);
      if (!document || !document.doc_id) {
        throw new Error(`Invalid document response: ${JSON.stringify(document)}`);
      }
      if (document.doc_id !== testDocumentId) {
        throw new Error(`Document ID mismatch: ${document.doc_id} !== ${testDocumentId}`);
      }
      return true;
    }, { category: 'document_api', requiresBackend: true, skip: !testDocumentId });
    
    // Test XML content retrieval
    await runner.test('Get document XML content', async () => {
      const content = await api.documents.getDocumentXmlContent(testDocumentId);
      if (!content || typeof content !== 'string') {
        throw new Error(`Invalid XML content: ${typeof content}`);
      }
      if (!content.includes('<?xml') && !content.includes('<')) {
        throw new Error('XML content does not appear to be valid XML');
      }
      return true;
    }, { category: 'document_api', requiresBackend: true, skip: !testDocumentId });
    
    // Test document nodes retrieval
    await runner.test('Get document nodes', async () => {
      const nodes = await api.documents.getDocumentNodes(testDocumentId);
      if (!Array.isArray(nodes)) {
        throw new Error(`Nodes response is not an array: ${typeof nodes}`);
      }
      return true;
    }, { category: 'document_api', requiresBackend: true, skip: !testDocumentId });
  }
  
  runner.printReport();
  return runner.results;
}

/**
 * Task API Tests
 */
export async function runTaskTests() {
  const runner = new ApiTestRunner({
    stopOnFail: false,
    verbose: true
  });
  
  let testDocumentId = null;
  let testTaskId = null;
  
  // First get a document ID to use for tests
  try {
    const documents = await api.documents.getAllDocuments();
    if (Array.isArray(documents) && documents.length > 0) {
      testDocumentId = documents[0].doc_id;
    }
  } catch (error) {
    console.log('⚠️ Could not get documents for task tests, some tests will be skipped');
  }
  
  // Test task creation
  await runner.test('Create task', async () => {
    if (!testDocumentId) {
      throw new Error('No document ID available for testing');
    }
    
    const task = await api.tasks.createTask({
      intent: 'analyze_xml',
      target_agent: 'xml_agent',
      payload: {
        doc_id: testDocumentId
      }
    });
    
    if (!task || !task.task_id) {
      throw new Error(`Invalid task response: ${JSON.stringify(task)}`);
    }
    
    testTaskId = task.task_id;
    return true;
  }, { category: 'task_api', requiresBackend: true, skip: !testDocumentId });
  
  // Skip remaining tests if task creation failed
  if (!testTaskId) {
    console.log('⚠️ Task creation failed, skipping task status/result tests');
  } else {
    // Test task status retrieval
    await runner.test('Get task status', async () => {
      const status = await api.tasks.getTaskStatus(testTaskId);
      if (!status || !status.status) {
        throw new Error(`Invalid task status response: ${JSON.stringify(status)}`);
      }
      return true;
    }, { category: 'task_api', requiresBackend: true, skip: !testTaskId });
    
    // Note: We don't test task results because tasks may take time to complete
    // and we don't want to block the test suite
  }
  
  // Test entity extraction shorthand
  await runner.test('Extract entities shorthand', async () => {
    if (!testDocumentId) {
      throw new Error('No document ID available for testing');
    }
    
    const result = await api.tasks.extractEntities(testDocumentId);
    if (!result || !result.task_id) {
      throw new Error(`Invalid extraction response: ${JSON.stringify(result)}`);
    }
    
    return true;
  }, { category: 'task_api', requiresBackend: true, skip: !testDocumentId });
  
  runner.printReport();
  return runner.results;
}

/**
 * Agent API Tests
 */
export async function runAgentTests() {
  const runner = new ApiTestRunner({
    stopOnFail: false,
    verbose: true
  });
  
  let testAgentId = null;
  
  // Test agent listing
  await runner.test('Get all agents', async () => {
    const agentData = await api.agents.getAllAgents();
    
    if (!agentData || !agentData.agents) {
      throw new Error(`Invalid agent response: ${JSON.stringify(agentData)}`);
    }
    
    if (!Array.isArray(agentData.agents)) {
      throw new Error(`Agents is not an array: ${typeof agentData.agents}`);
    }
    
    // Save an agent ID for later tests
    if (agentData.agents.length > 0) {
      testAgentId = agentData.agents[0].id;
    }
    
    return true;
  }, { category: 'agent_api', requiresBackend: true });
  
  // Skip remaining tests if no agent ID
  if (!testAgentId) {
    console.log('⚠️ No agents found, skipping agent detail tests');
  } else {
    // Test agent details retrieval
    await runner.test('Get agent by ID', async () => {
      const agent = await api.agents.getAgentById(testAgentId);
      if (!agent || !agent.id) {
        throw new Error(`Invalid agent response: ${JSON.stringify(agent)}`);
      }
      if (agent.id !== testAgentId) {
        throw new Error(`Agent ID mismatch: ${agent.id} !== ${testAgentId}`);
      }
      return true;
    }, { category: 'agent_api', requiresBackend: true, skip: !testAgentId });
    
    // Test agent log retrieval
    await runner.test('Get agent logs', async () => {
      const logs = await api.agents.getAgentLogs(testAgentId);
      if (!logs) {
        throw new Error('Logs response is null or undefined');
      }
      return true;
    }, { category: 'agent_api', requiresBackend: true, skip: !testAgentId });
  }
  
  runner.printReport();
  return runner.results;
}

/**
 * Source API Tests
 */
export async function runSourceTests() {
  const runner = new ApiTestRunner({
    stopOnFail: false,
    verbose: true
  });
  
  // Test source types listing
  await runner.test('Get source types', async () => {
    const sourceTypes = await api.sources.getSourceTypes();
    if (!Array.isArray(sourceTypes)) {
      throw new Error(`Source types response is not an array: ${typeof sourceTypes}`);
    }
    return true;
  }, { category: 'source_api', requiresBackend: true });
  
  // Test source validation
  await runner.test('Validate source', async () => {
    const validation = await api.sources.validateSource({
      url: 'https://example.com',
      title: 'Example Source'
    });
    
    if (!validation) {
      throw new Error('Validation response is null or undefined');
    }
    
    return true;
  }, { category: 'source_api', requiresBackend: true });
  
  runner.printReport();
  return runner.results;
}

/**
 * Comprehensive Test Suite Runner
 */
export async function runAllTests(options = {}) {
  console.log('🧪 Starting comprehensive API test suite...');
  
  const testOptions = {
    stopOnFail: false,
    skipBackend: false,
    ...options
  };
  
  const results = {
    basic: null,
    documents: null,
    tasks: null,
    agents: null,
    sources: null,
    summary: {
      passed: 0,
      failed: 0,
      skipped: 0,
      total: 0
    }
  };
  
  try {
    // Run the basic tests first
    results.basic = await runBasicTests();
    
    // If basic connectivity tests fail and we're not skipping backend,
    // mark backend as skipped for remaining tests
    if (results.basic.failed > 0 && results.basic.tests.some(t => 
        t.category === 'connectivity' && !t.passed && !t.skipped)) {
      console.log('⚠️ Basic connectivity tests failed, marking backend as unavailable');
      testOptions.skipBackend = true;
    }
    
    // Run document API tests
    results.documents = await runDocumentTests();
    
    // Run task API tests
    results.tasks = await runTaskTests();
    
    // Run agent API tests
    results.agents = await runAgentTests();
    
    // Run source API tests
    results.sources = await runSourceTests();
    
    // Compile summary
    const allCategories = [
      results.basic, results.documents, results.tasks, 
      results.agents, results.sources
    ];
    
    allCategories.forEach(categoryResult => {
      if (!categoryResult) return;
      
      results.summary.passed += categoryResult.passed;
      results.summary.failed += categoryResult.failed;
      results.summary.skipped += categoryResult.skipped;
      results.summary.total += categoryResult.passed + categoryResult.failed + categoryResult.skipped;
    });
    
    // Print overall summary
    console.log('\n====================');
    console.log(`🧪 Test Suite Complete`);
    console.log(`Overall: ${results.summary.passed}/${results.summary.total} passed, ${results.summary.failed} failed, ${results.summary.skipped} skipped`);
    console.log('====================');
    
    return results;
  } catch (error) {
    console.error('❌ Test suite execution error:', error);
    throw error;
  }
}

// Export a simple function for browser usage
export default async function runTests(options = {}) {
  return runAllTests(options);
}

// Make test runner available globally for easy browser console testing
if (typeof window !== 'undefined') {
  window.runApiTests = runAllTests;
  window.runBasicApiTests = runBasicTests;
  window.runDocumentApiTests = runDocumentTests;
  window.runTaskApiTests = runTaskTests;
  window.runAgentApiTests = runAgentTests;
  window.runSourceApiTests = runSourceTests;
  
  console.log('API test suite loaded. Run tests with: runApiTests()');
}