# Agent Provocateur Documentation

This directory contains documentation for the Agent Provocateur project, organized into the following sections:

## Architecture

Documentation related to the overall architecture and design of the system:

- [A2A Messaging and MCP Integration](architecture/A2A_MCP.md): Agent-to-Agent messaging integration with MCP
- [Multi-Context Protocol](architecture/MULTICONTEXTPROTOCOL.md): Detailed explanation of the Multi-Context Protocol
- [Project Design Specification](architecture/project_design_spec.md): Technical design specifications
- [Project Requirements](architecture/project_prd.md): Product requirements document
- [Frontend Architecture](architecture/frontend_architecture.md): Frontend architecture and implementation

## API Documentation

Documentation for external APIs and integrations:

- [BridgeIT API](api/BRIDGEIT_API.md): Integration with Cisco's BridgeIT platform
- [Ollama API](api/OLLAMA_API.md): Integration with Ollama for local LLM support
- [Web Search Integration](api/web_search_integration.md): Web search with multiple provider support
- [Brave Search API](api/brave_web_search.md): Integration with Brave Search API
- [GraphRAG MCP API](api/graphrag_mcp_api.md): GraphRAG microservice API for source attribution

## Guides

User and developer guides for specific features:

- [Document Types](guides/document_types.md): Overview of the document type system
- [XML Verification](guides/xml_verification.md): Guide to XML document verification features
- [Web UI Guide](guides/ui_guide.md): Guide to using the XML processing web interface
- [Source Attribution](guides/source_attribution.md): Guide to the source attribution system

## Development

Development guidelines and tooling:

- [Development Plan 2025](development/development_plan_2025.md): Current roadmap and priorities
- [Claude AI Guide](development/CLAUDE.md): Instructions for Claude AI when working with this codebase
- [Coding Guidelines](development/coding_guidelines.md): Coding standards and best practices
- [Development Setup](development/DEVELOPMENT.md): Environment setup and development workflow
- [GraphRAG MCP Guide](development/graphrag_mcp_guide.md): Guide to using GraphRAG for enhanced source attribution

## Implementation Details

Documentation of implementation phases and specific components:

- [Phase 1 Implementation](implementation/phase1_implementation.md): MCP Tools development details ✅
- [Phase 2 Implementation](implementation/phase2_implementation.md): A2A Communication development details ✅
- [Phase 2 XML Implementation](implementation/PHASE2_XML_IMPLEMENTATION.md): XML Analysis Agent implementation details ✅
- [Phase 3 Implementation](implementation/phase3_implementation.md): Research integration, web UI, and source attribution 🔄

### Current Implementation Status

- **Completed**: DocBook XML validation, Web Search integration, basic UI
- **In Progress**: GraphRAG Python implementation (75%), Entity Linking (40%)
- **Upcoming**: Advanced entity relationship detection, UI visualization enhancements

See [Development Plan 2025](development/development_plan_2025.md) for detailed roadmap.

## Components

Documentation of specific system components:

- [XML Verification Component](components/xml_verification.md): XML document analysis and verification engine

## Frontend Components

Documentation for the web user interface:

- [Frontend Architecture](architecture/frontend_architecture.md): Web UI design and implementation
- [UX Design](uxd/ux_design.md): User experience design specifications
- [Web UI Guide](guides/ui_guide.md): User guide for the Writer's Research Assistant XML processing interface

## Other Resources

- [Main README](../README.md): Project overview and general information
- [Monitoring](../monitoring/README.md): Monitoring setup and configuration