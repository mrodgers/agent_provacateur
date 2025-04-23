# Entity Detector MCP Tests

This directory contains comprehensive tests for the Entity Detector MCP service. The tests cover various components of the service, ensuring reliability and correctness.

## Test Coverage Summary

Current test coverage: **81.89%** statement coverage

```
-----------------------|---------|----------|---------|---------|--------------------
File                   | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s  
-----------------------|---------|----------|---------|---------|--------------------
All files              |   81.89 |    67.34 |   81.25 |   81.93 |                    
 src                   |   44.44 |       50 |       0 |   44.44 |                    
  config.ts            |     100 |       50 |     100 |     100 | 24-35              
  logger.ts            |       0 |      100 |       0 |       0 | 1-24               
 src/detectors         |   74.78 |    61.01 |      75 |   75.42 |                    
  detector-factory.ts  |   56.66 |    28.57 |      50 |   56.66 | 31-32,38,51-74     
  nlp-detector.ts      |      70 |    57.14 |      80 |      70 | 37,77-78,87,99-118 
  regex-detector.ts    |   84.84 |       80 |   83.33 |    87.5 | 37,89-90,99        
  types.ts             |     100 |      100 |     100 |     100 |                    
 src/routes            |   76.66 |      100 |      75 |   76.66 |                    
  index.ts             |       0 |      100 |       0 |       0 | 1-14               
  tools.ts             |     100 |      100 |     100 |     100 |                    
 src/tools             |     100 |    91.66 |     100 |     100 |                    
  entity-extraction.ts |     100 |    91.66 |     100 |     100 | 23                 
 src/utils             |     100 |       90 |     100 |     100 |                    
  cache.ts             |     100 |       90 |     100 |     100 | 16                 
-----------------------|---------|----------|---------|---------|--------------------
```

## Test Files

### Entity Extraction Tests
- **entity-extraction.test.ts**: Tests the core entity extraction functionality
  - Extraction using different detector models
  - Caching functionality
  - XML-specific entity detection
  - Error handling

### Detector Implementation Tests
- **detectors.test.ts**: Tests the individual detector implementations
  - RegexDetector tests for pattern-based entity detection
  - NlpDetector tests for NLP-based entity detection
  - Confidence threshold handling
  - Type filtering
  - Custom patterns support

### API Routes Tests
- **tools-routes.test.ts**: Tests the REST API endpoints
  - GET /tools endpoint
  - POST /tools/extract_entities/run endpoint
  - POST /tools/detector_info/run endpoint
  - Error handling for various scenarios

### Frontend Integration Tests
- **frontend-integration.test.ts**: Tests integration with the frontend
  - Direct API fallback mechanism
  - Service status checking
  - XML document processing
  - Error handling for frontend workflows

### Utility Tests
- **cache.test.ts**: Tests the caching mechanism
  - Store and retrieve values
  - Custom TTL settings
  - Cache eviction
  - Disabled cache behavior

- **logger.test.ts**: Tests logging functionality
  - Log level handling
  - Message formatting

## Running the Tests

To run all tests with coverage reporting:

```bash
npm test -- --coverage
```

Or use the provided test script:

```bash
./scripts/test.sh
```

## Improving Test Coverage

Areas that could benefit from additional test coverage:

1. **detector-factory.ts**: Add tests for error handling in initialization and fallback logic
2. **nlp-detector.ts**: Add more tests for language detection and entity mapping
3. **router/index.ts**: Add tests for router setup

## Frontend Integration

The tests include specific scenarios for frontend integration, particularly focusing on the fallback mechanism implemented in `document_viewer.js` that allows direct communication with the entity detector service when the MCP server fails.