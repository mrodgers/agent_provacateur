# Agent Provocateur

A Python library for developing, benchmarking, and deploying AI agents for research tasks. The system enables modular agents to collaboratively perform end-to-end research against structured and unstructured data sources.

## Features

- **MCP Server Mock**: Simulates tool interactions (JIRA, Document, PDF, Search) with configurable latency and error injection
- **MCP Client SDK**: Type-safe Python client for interacting with the MCP server
- **CLI Interface**: Command-line tools for interacting with the server
- **Agent-to-Agent (A2A) Communication**: Structured messaging system for agent coordination and task delegation with reliable deduplication
- **Agent Framework**: Base classes and utilities for building collaborative agent systems
- **LLM Integration**: Support for multiple LLM providers including local Ollama models and Cisco's BridgeIT platform
- **Document Types**: Support for multiple document types (text, PDF, image, code, structured data, XML)
- **Verification System**: Advanced verification for XML claims and statements with confidence scoring
- **Prometheus Metrics**: Built-in monitoring with Prometheus metrics and Grafana dashboards

## Installation

```bash
# Using the unified script (recommended)
./scripts/ap.sh setup

# Basic installation with pip
pip install -e ".[dev]"

# With LLM support (Ollama)
pip install -e ".[dev,llm]"

# With XML support
pip install -e ".[dev,xml]"

# With monitoring support (Prometheus)
pip install -e ".[dev,monitoring]"

# With BridgeIT support
pip install -e ".[dev,bridgeit]"

# With all features
pip install -e ".[dev,llm,bridgeit,redis,monitoring,xml]"
```

### LLM Provider Setup

Agent Provocateur supports multiple LLM providers that can be used interchangeably:

### Available Providers

| Provider | Description | Installation | Documentation |
|----------|-------------|--------------|---------------|
| Mock | Built-in fallback provider for testing | Default | N/A |
| Ollama | Local models with Ollama | `pip install -e ".[llm]"` | [Ollama API](docs/api/OLLAMA_API.md) |
| BridgeIT | Cisco's Azure OpenAI gateway | `pip install -e ".[bridgeit]"` | [BridgeIT API](docs/api/BRIDGEIT_API.md) |

### Ollama Setup

To use Ollama as an LLM provider:

1. Install Ollama from [ollama.com/download](https://ollama.com/download)
2. Pull a model: `ollama pull llama3`
3. Make sure Ollama is running: `ollama serve`
4. Install the Python package: `pip install -e ".[llm]"`

### BridgeIT Setup

To use Cisco's BridgeIT platform as an LLM provider:

1. Install the required dependencies: `pip install -e ".[bridgeit]"`
2. Create a `.env` file in your project root with the following environment variables:

```bash
# Required variables
AZURE_OPENAI_CLIENT_ID=your_client_id
AZURE_OPENAI_CLIENT_SECRET=your_client_secret
BRIDGEIT_APP_KEY=your_app_key

# Optional variables with defaults
BRIDGEIT_API_VERSION=2024-07-01-preview
BRIDGEIT_TOKEN_URL=https://id.cisco.com/oauth2/default/v1/token
BRIDGEIT_LLM_ENDPOINT=https://chat-ai.cisco.com
BRIDGEIT_DEPLOYMENT_NAME=gpt-4o-mini
```

> **Note on bridgeit.py**: The original `bridgeit.py` file in the root directory is a reference implementation. Its core functionality has been integrated into the Agent Provocateur architecture in `src/agent_provocateur/llm_service.py`. You may keep or remove the original file, as it's not used by the core system.

For detailed development instructions, see [Development Guide](docs/development/DEVELOPMENT.md).

## Project Structure

```
agent_provocateur/
├── docs/                       # Documentation
│   ├── architecture/           # Architecture docs
│   ├── api/                    # API docs
│   ├── development/            # Development guides
│   ├── guides/                 # User guides
│   ├── implementation/         # Implementation details
│   └── README.md               # Documentation index
├── examples/                   # Example files
│   ├── sample.xml              # Sample XML document
│   └── sample_rules.json       # Sample verification rules
├── scripts/                    # CLI and utility scripts
│   ├── ap.sh                   # Main CLI script
│   ├── xml_cli.py              # XML document CLI
│   └── xml_agent_cli.py        # XML agent CLI
├── src/                        # Source code
│   └── agent_provocateur/      # Package directory
├── tests/                      # Test directory
│   └── test_data/              # Test data
├── monitoring/                 # Monitoring configuration
└── README.md                   # This file
```

## Document Types

Agent Provocateur supports multiple document types:

### Text Documents (DocumentContent)
- Markdown and HTML content
- Text analysis capabilities
- Format: Markdown with optional HTML

### PDF Documents (PdfDocument)
- Page-by-page text extraction
- Metadata support
- URLs for source tracking

### Image Documents (ImageDocument)
- Image metadata (dimensions, format)
- Alt text and captions
- Source URL tracking

### Code Documents (CodeDocument)
- Source code with language identification
- Line counting and code metrics
- Support for syntax highlighting

### Structured Data Documents (StructuredDataDocument)
- JSON, YAML, and other structured formats
- Schema validation options
- Data exploration capabilities

### XML Documents (XmlDocument)
- XML content with namespace support
- Researchable node identification
- Verification planning and execution
- Confidence scoring for claims and statements

For more details on document types, see the [Document Types Guide](docs/guides/document_types.md).

## Development

```bash
# Run tests
pytest                     # Run all tests with pytest
pytest -v                  # Run with verbose output
python -m pytest --cov=src.agent_provocateur  # Run with coverage report

# Type checking
mypy src

# Linting
ruff check .
```

## Usage

### Running the MCP Server

```bash
# Start the MCP server
python -m agent_provocateur.main --host 127.0.0.1 --port 8000
# Or using entry point
ap-server --host 127.0.0.1 --port 8000

# Start with Prometheus metrics on port 8001
ap-server --metrics-port 8001

# Disable metrics
ap-server --no-metrics
```

### Using the CLI Client

```bash
# Fetch a JIRA ticket
python -m agent_provocateur.cli ticket AP-1
# Or using entry point
ap-client ticket AP-1

# Get document content
ap-client doc doc1

# Get PDF content
ap-client pdf pdf1

# Search web content
ap-client search "agent protocol"

# Configure server latency and error rate
ap-client config --min-latency 100 --max-latency 1000 --error-rate 0.1

# Output results as JSON
ap-client ticket AP-1 --json

# Connect to a different server
ap-client --server http://localhost:8008 ticket AP-1

# List all documents
ap-client list-documents

# List documents of a specific type
ap-client list-documents --type code
```

### Working with XML Documents

The XML Agent provides advanced capabilities for working with XML documents, identifying content that requires verification, planning verification tasks, and researching entities.

#### XML Document Handling

```bash
# Using the XML CLI tool
python scripts/xml_cli.py list               # List all XML documents
python scripts/xml_cli.py get xml1           # Get XML document details
python scripts/xml_cli.py get xml1 --content # Show XML content
python scripts/xml_cli.py get xml1 --nodes   # Show researchable nodes
python scripts/xml_cli.py upload examples/sample.xml --title "Product Catalog"  # Upload new XML document
```

#### XML Agent Capabilities

```bash
# Using the XML Agent CLI tool
python scripts/xml_agent_cli.py identify --file sample.xml --confidence 0.4 --evidence  # Identify researchable nodes
python scripts/xml_agent_cli.py identify --doc_id xml1 --rules-file sample_rules.json   # Use custom rules
python scripts/xml_agent_cli.py plan xml1                            # Create verification plan
python scripts/xml_agent_cli.py verify xml1 --search-depth high      # Test batch verification
```

#### XML Research

The system supports extracting entities from XML documents and researching them to generate enriched XML output:

```bash
# Research entities in an XML document
ap-client research xml1

# Customize research parameters
ap-client research xml1 --min-confidence 0.7 --max-entities 5 

# Generate enriched XML output
ap-client research xml1 --format xml --output enriched.xml

# Include search for external validation
ap-client research xml1 --with-search
```

For more details on XML verification and research, see:
- [XML Verification Guide](docs/guides/xml_verification.md)
- [XML Research Implementation](docs/implementation/phase3_implementation.md)

### Using the LLM CLI

The `ap-llm` command provides a convenient way to interact with any configured LLM provider:

```bash
# List all available and configured LLM providers
ap-llm --list-providers

# Basic usage with different providers
ap-llm --provider mock --prompt "Why is the sky blue?"
ap-llm --provider ollama --model llama3 --prompt "Why is the sky blue?"
ap-llm --provider bridgeit --prompt "Why is the sky blue?"

# Using chat format with system and user messages
ap-llm --provider ollama --model llama3 --messages "system:You are a helpful assistant,user:Why is the sky blue?"
ap-llm --provider bridgeit --messages "system:You are a research assistant,user:Explain quantum computing"

# Adjusting generation parameters
ap-llm --provider ollama --model llama3 --prompt "Why is the sky blue?" --temperature 0.3 --max-tokens 500
ap-llm --provider bridgeit --prompt "Why is the sky blue?" --temperature 0.7 --max-tokens 1000

# Output format control
ap-llm --provider ollama --model llama3 --prompt "Why is the sky blue?" --json
```

For more details on provider-specific options, see the documentation files:
- [Ollama API](docs/api/OLLAMA_API.md) - For Ollama integration details
- [BridgeIT API](docs/api/BRIDGEIT_API.md) - For BridgeIT integration details

### Working with Documents

```python
import asyncio
from agent_provocateur.mcp_client import McpClient

async def main():
    client = McpClient("http://localhost:8000")
    
    # List all available documents
    documents = await client.list_documents()
    for doc in documents:
        print(f"{doc.doc_id} ({doc.doc_type}): {doc.title}")
    
    # List documents of a specific type
    code_docs = await client.list_documents(doc_type="code")
    for doc in code_docs:
        print(f"Code document: {doc.doc_id} - {doc.title}")
    
    # Get a specific document
    doc = await client.get_document("code1")
    if doc.doc_type == "code":
        print(f"Language: {doc.language}")
        print(f"Line count: {doc.line_count}")
        print(f"Content sample: {doc.content[:100]}...")
    
    # Working with structured data documents
    data_doc = await client.get_document("data1")
    if data_doc.doc_type == "structured_data":
        print(f"Format: {data_doc.format}")
        print(f"Top-level keys: {list(data_doc.data.keys())}")
        
        # Process data based on format
        if data_doc.format == "json":
            config = data_doc.data.get("configuration", {})
            print(f"Configuration: {config}")

asyncio.run(main())
```

### Running the Document Sample Workflow

```bash
# Start the MCP server in one terminal
ap-server

# Run the sample document workflow in another terminal
python -m agent_provocateur.sample_document_workflow
```

### Monitoring with Prometheus and Grafana

The project includes Prometheus metrics integration with Pushgateway and a pre-configured Grafana dashboard.

```bash
# Install monitoring dependencies
pip install -e ".[monitoring]"

# Start the MCP server with metrics enabled (default port 8001)
ap-server --pushgateway localhost:9091

# Start Prometheus, Pushgateway, and Grafana with Docker/Podman
cd monitoring
docker-compose up -d
# or with podman
podman-compose up -d

# Access the dashboards
open http://localhost:3000  # Grafana (admin/agent_provocateur)
open http://localhost:9090  # Prometheus
open http://localhost:9091  # Pushgateway
```

Available metrics include:
- MCP client request counts and latencies
- A2A message counts and processing times
- Agent task counts, statuses, and durations
- LLM request statistics
- System information

For more details, see [Monitoring README](monitoring/README.md).

## Architecture and Design

The Agent Provocateur system is built on these key architectural concepts:

1. **Model-Context-Protocol (MCP)** - A standardized way for agents to interact with tools, data, and context
2. **Agent-to-Agent (A2A) Messaging** - Communication system for collaborative agent workflows
3. **Document Type System** - Unified representation of different document formats
4. **Verification Framework** - System for verifying information in documents

For more details on the architecture, see:
- [A2A and MCP Integration](docs/architecture/A2A_MCP.md)
- [Multi-Context Protocol](docs/architecture/MULTICONTEXTPROTOCOL.md)
- [Project Design Specification](docs/architecture/project_design_spec.md)

## Documentation

See the [Documentation Index](docs/README.md) for the full documentation, including:
- [Development Guides](docs/development/)
- [API Documentation](docs/api/)
- [User Guides](docs/guides/)
- [Implementation Details](docs/implementation/)

## License

MIT License. See the LICENSE file for details.