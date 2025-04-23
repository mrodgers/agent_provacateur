# Entity Detector MCP Server

A Model Context Protocol (MCP) server for entity detection, designed to be used with Agent Provocateur. This server provides a standardized interface for detecting and extracting entities from text using multiple detection methods.

## Features

- **Multiple Detection Models**: Supports multiple entity detection methods (regex patterns and NLP)
- **Extensible Architecture**: Easily add new detection models
- **Entity Type Detection**: Identifies entities like people, organizations, locations, dates, and more
- **Configurable Confidence Scoring**: Filter entities by confidence threshold
- **Caching**: In-memory caching to improve performance
- **MCP Standard Interface**: Follows the Model Context Protocol for easy integration

## Prerequisites

- Node.js 18+ (for development)
- npm (for dependency management)

## Quick Start

### Development Setup

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd entity_detector_mcp
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   # Edit .env to configure the server
   ```

4. Build the TypeScript code:
   ```bash
   npm run build
   ```

5. Start the server in development mode:
   ```bash
   npm run dev
   ```

### Quick Start with Scripts

The repository includes helper scripts for common operations:

1. Build the project:
   ```bash
   ./scripts/build.sh
   ```

2. Start the server:
   ```bash
   ./scripts/start.sh
   ```

3. Run tests:
   ```bash
   ./scripts/test.sh
   ```

## Configuration

The server is configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8082` |
| `HOST` | Server host | `0.0.0.0` |
| `ENABLE_CACHE` | Enable result caching | `true` |
| `CACHE_TTL_SECONDS` | Seconds to cache results | `3600` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `*` |
| `LOG_LEVEL` | Logging level | `info` |
| `DEFAULT_MODEL` | Default entity detection model | `regex` |
| `NLP_LANGUAGE` | Language for NLP model | `en` |

## Available Tools

### Entity Extraction

- **Tool name**: `extract_entities`
- **Parameters**:
  - `text` (string, required): Text to extract entities from
  - `types` (array, optional): Entity types to extract (if not specified, all types are extracted)
  - `minConfidence` (number, optional): Minimum confidence threshold (default: 0.5)
  - `includeMetadata` (boolean, optional): Include additional metadata (default: false)
  - `model` (string, optional): Detection model to use (default: config.defaultModel)

### Detector Information

- **Tool name**: `detector_info`
- **Parameters**: None
- **Returns**: Information about available entity detection models

## Supported Entity Types

The server can detect various entity types, including:

- `PERSON`: Names of people
- `ORGANIZATION`: Company, agency, institution names
- `LOCATION`: Geographical locations
- `DATETIME`: Dates and times
- `MONEY`: Currency values
- `PERCENT`: Percentage values
- `EMAIL`: Email addresses
- `PHONE`: Phone numbers
- `URL`: Web URLs
- `PRODUCT`: Product names
- `EVENT`: Event names
- `WORK_OF_ART`: Titles of books, songs, etc.
- `CONCEPT`: Abstract concepts
- `CUSTOM`: User-defined entity types

## Integration with Agent Provocateur

To integrate this MCP server with Agent Provocateur, follow these steps:

1. Start the Entity Detector MCP server.

2. Connect from an Agent Provocateur agent:
   ```python
   # In your agent code
   entity_detector_url = os.environ.get("ENTITY_DETECTOR_MCP_URL", "http://localhost:8082")
   entity_detector = McpClient(entity_detector_url)
   
   # Extract entities from text
   result = await entity_detector.call_tool("extract_entities", {"text": text_content})
   ```

3. Process the detected entities:
   ```python
   entities = result.get("entities", [])
   for entity in entities:
       entity_text = entity.get("text")
       entity_type = entity.get("type")
       confidence = entity.get("confidence")
       # Process entity...
   ```

## Testing

### Unit and Integration Tests

The Entity Detector MCP includes a comprehensive test suite covering core functionality, API endpoints, and frontend integration:

```bash
# Run all tests with coverage reporting
npm test -- --coverage

# Or use the test script
./scripts/test.sh
```

Current test coverage: **81.89%** statement coverage

For detailed test documentation, see [TESTING.md](./TESTING.md) and [tests/README.md](./tests/README.md).

### Manual Integration Testing

Run the included test script to verify the integration with Agent Provocateur:

```bash
python scripts/test_entity_detector.py --text "Microsoft was founded by Bill Gates and Paul Allen on April 4, 1975."
```

### Automated Testing Script

For CI/CD environments, use the automated test script:

```bash
../scripts/test_entity_detector.sh
```

This script:
1. Runs all unit tests
2. Verifies test coverage meets the minimum threshold (80%)
3. Starts the service and performs API integration tests
4. Tests XML-specific entity extraction

## Extending with New Detection Models

To add a new entity detection model:

1. Create a new file in `src/detectors/` implementing the `EntityDetector` interface.
2. Update the `DetectorFactory` to initialize the new model.
3. Add configuration options to `config.ts`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.