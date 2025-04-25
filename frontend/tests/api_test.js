/**
 * API Test Script for Agent Provocateur
 * Tests all API endpoints and container health
 * 
 * Port Configuration:
 * - Frontend UI: 3001 (required)
 * - MCP Server: 8111 (required)
 * - Redis: 6111 (required)
 * - Ollama: 7111 (optional)
 * 
 * Optional Services:
 * - Entity Detector: 8082
 * - Web Search: 8083
 * - GraphRAG: 8084
 * - Grafana: 3111
 * - Prometheus: 9111
 * - Pushgateway: 9091
 */

const API_BASE_URL = window.BACKEND_URL || 'http://localhost:8111';
const FRONTEND_URL = window.location.origin;

// Test results storage
const testResults = {
    passed: 0,
    failed: 0,
    total: 0,
    details: []
};

// Helper function to run a test
async function runTest(name, testFn) {
    testResults.total++;
    try {
        await testFn();
        testResults.passed++;
        testResults.details.push({ name, status: 'PASSED' });
        console.log(`✅ ${name}: PASSED`);
    } catch (error) {
        testResults.failed++;
        testResults.details.push({ name, status: 'FAILED', error: error.message });
        console.error(`❌ ${name}: FAILED - ${error.message}`);
    }
}

// Test frontend health check
async function testFrontendHealth() {
    const response = await fetch(`${FRONTEND_URL}/api/health`);
    if (!response.ok) throw new Error(`Health check failed: ${response.status}`);
    const data = await response.json();
    if (data.status !== 'ok') throw new Error('Health check returned invalid status');
}

// Test backend health check
async function testBackendHealth() {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) throw new Error(`Backend health check failed: ${response.status}`);
    const data = await response.json();
    if (data.status !== 'ok') throw new Error('Backend health check returned invalid status');
}

// Test system info endpoint
async function testSystemInfo() {
    const response = await fetch(`${FRONTEND_URL}/api/info`);
    if (!response.ok) throw new Error(`System info failed: ${response.status}`);
    const data = await response.json();
    if (!data.version || !data.build_number) throw new Error('System info missing required fields');
}

// Test debug endpoint
async function testDebugInfo() {
    const response = await fetch(`${FRONTEND_URL}/api/debug`);
    if (!response.ok) throw new Error(`Debug info failed: ${response.status}`);
    const data = await response.json();
    if (!data.app_routes || !data.backend_url) throw new Error('Debug info missing required fields');
}

// Test document listing
async function testDocumentListing() {
    const response = await fetch(`${FRONTEND_URL}/api/documents`);
    if (!response.ok) throw new Error(`Document listing failed: ${response.status}`);
    const data = await response.json();
    if (!Array.isArray(data)) throw new Error('Document listing did not return an array');
}

// Test document upload
async function testDocumentUpload() {
    const testXml = `<?xml version="1.0" encoding="UTF-8"?>
        <test>
            <title>Test Document</title>
            <content>This is a test document</content>
        </test>`;
    
    const formData = new FormData();
    formData.append('file', new Blob([testXml], { type: 'application/xml' }), 'test.xml');
    formData.append('title', 'Test Document');

    const response = await fetch(`${FRONTEND_URL}/documents/upload`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) throw new Error(`Document upload failed: ${response.status}`);
    const data = await response.json();
    if (!data.id) throw new Error('Document upload did not return an ID');
}

// Test container ports
async function testContainerPorts() {
    const response = await fetch(`${FRONTEND_URL}/api/info`);
    if (!response.ok) throw new Error(`Container port check failed: ${response.status}`);
    const data = await response.json();
    
    // Extract port from API_BASE_URL
    const backendPort = new URL(API_BASE_URL).port;
    
    // Core ports that are always required
    const corePorts = {
        3001: 'Frontend UI',
        [backendPort]: 'MCP Server API',
        6111: 'Redis'
    };

    // Optional ports that may be required based on configuration
    const optionalPorts = {
        7111: 'Ollama',
        8082: 'Entity Detector MCP',
        8083: 'Web Search MCP',
        8084: 'GraphRAG MCP',
        3111: 'Grafana',
        9111: 'Prometheus',
        9091: 'Pushgateway'
    };

    // Check core ports first
    for (const [port, service] of Object.entries(corePorts)) {
        if (!data.ports[port]?.in_use) {
            throw new Error(`Required port ${port} (${service}) is not in use`);
        }
    }

    // Check optional ports and log their status
    for (const [port, service] of Object.entries(optionalPorts)) {
        const status = data.ports[port]?.in_use ? 'in use' : 'not in use';
        console.log(`Optional port ${port} (${service}) is ${status}`);
    }

    // Check if any required optional services are missing
    const missingRequiredServices = [];
    for (const [port, service] of Object.entries(optionalPorts)) {
        if (data.ports[port]?.required && !data.ports[port]?.in_use) {
            missingRequiredServices.push(`${service} (${port})`);
        }
    }

    if (missingRequiredServices.length > 0) {
        console.warn(`Warning: Some required optional services are not running: ${missingRequiredServices.join(', ')}`);
    }
}

// Run all tests
async function runAllTests() {
    console.log('Starting API tests...');
    
    await runTest('Frontend Health Check', testFrontendHealth);
    await runTest('Backend Health Check', testBackendHealth);
    await runTest('System Info', testSystemInfo);
    await runTest('Debug Info', testDebugInfo);
    await runTest('Document Listing', testDocumentListing);
    await runTest('Document Upload', testDocumentUpload);
    await runTest('Container Ports', testContainerPorts);

    // Print summary
    console.log('\nTest Summary:');
    console.log(`Total Tests: ${testResults.total}`);
    console.log(`Passed: ${testResults.passed}`);
    console.log(`Failed: ${testResults.failed}`);
    
    if (testResults.failed > 0) {
        console.log('\nFailed Tests:');
        testResults.details
            .filter(test => test.status === 'FAILED')
            .forEach(test => console.log(`- ${test.name}: ${test.error}`));
    }

    return testResults;
}

// Export the test runner
export { runAllTests }; 