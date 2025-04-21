const fetch = require('node-fetch');

const API_URL = process.env.API_URL || 'http://localhost:8083';

/**
 * Simple test script for the GraphRAG MCP server
 */
async function testGraphRAG() {
  console.log('Testing GraphRAG MCP server...');
  
  try {
    // Test server info
    console.log('\n--- Testing server info ---');
    const infoResponse = await fetch(`${API_URL}/api/info`);
    const infoData = await infoResponse.json();
    console.log('Server info:', infoData);
    
    // Test entity extraction
    console.log('\n--- Testing entity extraction ---');
    const extractResponse = await fetch(`${API_URL}/api/tools/graphrag_extract_entities`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: 'Climate change is a significant challenge facing our planet. The United States and European Union have pledged to reduce emissions.'
      })
    });
    const extractData = await extractResponse.json();
    console.log(`Extracted ${extractData.entities?.length || 0} entities:`);
    console.log(JSON.stringify(extractData.entities, null, 2));
    
    // Test source indexing
    console.log('\n--- Testing source indexing ---');
    const indexResponse = await fetch(`${API_URL}/api/tools/graphrag_index_source`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source: {
          source_id: `test_${Date.now()}`,
          source_type: 'web',
          title: 'Test Source',
          content: 'Climate change is causing sea levels to rise and weather patterns to change.',
          url: 'https://example.com/test',
          confidence_score: 0.9,
          reliability_score: 0.8,
          retrieval_date: new Date().toISOString()
        }
      })
    });
    const indexData = await indexResponse.json();
    console.log('Source indexed:', indexData);
    
    // Test query
    console.log('\n--- Testing query ---');
    const queryResponse = await fetch(`${API_URL}/api/tools/graphrag_query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: 'What are the effects of climate change?'
      })
    });
    const queryData = await queryResponse.json();
    console.log(`Found ${queryData.sources?.length || 0} sources`);
    console.log('First source:', queryData.sources?.[0]);
    
    console.log('\n--- All tests completed successfully ---');
  } catch (error) {
    console.error('Error testing GraphRAG MCP server:', error);
    process.exit(1);
  }
}

testGraphRAG();