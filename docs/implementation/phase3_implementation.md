# Phase 3: Technical Research Integration and Web UI

This document outlines Phase 3 of the XML agent integration into the Agent Provocateur framework, adding a unified CLI interface for XML research workflows and implementing a web-based user interface for XML document processing.

## Overview

Phase 3 consists of two major components:

1. **CLI Research Integration**: Extension of the Agent Provocateur CLI with a new `research` command that integrates the XML agent's entity extraction and validation capabilities.

2. **Web UI Implementation**: Development of an interactive web interface for XML document processing, providing a user-friendly alternative to the CLI.

## CLI Research Integration

### CLI Implementation Details

The main CLI (`cli.py`) has been enhanced with:

1. **New Research Command**: A dedicated `research` command with several options:
   - `doc_id`: Document ID to research
   - `--format`: Output format (text or XML)
   - `--output`: Output file for XML results
   - `--max-entities`: Maximum entities to research (default: 10)
   - `--min-confidence`: Minimum confidence threshold (default: 0.5)
   - `--with-search`: Option to include search agent for external validation
   - `--with-jira`: Option to include JIRA agent for internal context

2. **Agent Orchestration**: Creates and manages multiple agents in the research workflow:
   - ResearchSupervisorAgent: Coordinates the research process
   - XmlAgent: Handles XML parsing and entity extraction
   - DocAgent: Retrieves document content
   - DecisionAgent: Makes routing decisions
   - SynthesisAgent: Formats final output
   - Optional SearchAgent and JiraAgent for extended research

3. **Results Formatting**: The `format_research_results()` function provides human-readable output, including:
   - Research summary (document ID, entity counts)
   - Top entities with definitions and confidence scores
   - XML validation status

### Research Supervisor Enhancement

The ResearchSupervisorAgent has been updated to:

1. **Handle Format Options**: Pass format options from the CLI to the XML agent
2. **Support Output Formats**: Generate appropriate output based on the requested format
3. **Add Validation Information**: Include validation details in the research results

### XML Agent Interaction

The communication between CLI, Research Supervisor, and XML Agent now includes:

1. **Extended Payload**: XML agent receives both document ID and research options 
2. **Format-Aware Processing**: Entity extraction and XML generation respect format preferences
3. **Validation Integration**: Research results include schema validation information

## Web UI Implementation

### Web UI Implementation Details

The web-based user interface has been implemented with:

1. **FastAPI Server**: Provides a web server that serves both the frontend UI and API endpoints:
   - Handles document uploads and retrieval
   - Proxies requests to the backend API
   - Serves static assets and HTML templates

2. **Three-Panel Interface**:
   - Document Viewer (Left): Displays formatted XML with syntax highlighting
   - Supervisor Chat (Right): Provides interactive guidance through processing
   - Results Panel (Bottom): Shows processing outcomes and export options

3. **Document Management**:
   - Landing page with document listing
   - File upload with drag-and-drop support
   - Document preview and selection

4. **Processing Options**:
   - Multiple processing types (entity extraction, term research, validation)
   - Interactive supervisor guidance
   - Real-time processing updates

5. **Results Handling**:
   - Structured display of processing results
   - Download options for processed XML
   - Export options for JSON reports

### Technology Stack

The web UI is built using:

- **Backend**: FastAPI server (Python)
- **Frontend**: Vanilla JavaScript with dynamic DOM manipulation
- **Styling**: Tailwind CSS for responsive layout
- **Libraries**:
  - Prism.js for syntax highlighting
  - vkBeautify for XML formatting
  - React (loaded via CDN) for component structure

### API Integration

The web UI communicates with the backend API to:

1. **Fetch Documents**: Retrieve document lists and content
2. **Process Documents**: Send processing requests to the appropriate agents
3. **Download Results**: Retrieve and format processing results

The implementation includes fallback mechanisms when backend APIs are unavailable, allowing for demonstration and testing.

## Usage Examples

### CLI Research Command

```bash
# Research entities in an XML document with default settings
ap-client research xml1

# Research with custom confidence threshold
ap-client research xml1 --min-confidence 0.7 --max-entities 5

# Output enriched XML to a file
ap-client research xml1 --format xml --output enriched.xml

# Include search for external validation
ap-client research xml1 --with-search
```

### Web UI Usage

1. Start the frontend server:
   ```bash
   python frontend/server.py --backend-url=http://127.0.0.1:8000 --port 3000
   ```

2. Access the web interface at `http://localhost:3000`

3. Upload an XML document or select an existing one

4. Choose a processing type and follow the supervisor's guidance

5. View and download the processing results

## Testing

The implementation includes comprehensive testing:

1. **CLI Testing**:
   - Unit tests for the research command integration
   - Integration tests for the full workflow from CLI to output
   - Validation tests for XML output

2. **Web UI Testing**:
   - Server endpoint tests
   - Document upload and retrieval tests
   - Processing workflow tests

Tests cover both happy paths and error handling scenarios to ensure robustness.

## Source Attribution Implementation

Phase 3 introduces comprehensive source attribution for all AI-generated content in Agent Provocateur. This feature enhances transparency and credibility by clearly documenting where information comes from.

### Source Attribution Model

A standardized `Source` model has been implemented with these key components:

1. **Core Source Data**:
   - `source_id`: Unique identifier for each source
   - `source_type`: Categorization (web, document, database, API, etc.)
   - `title`: Source name or title
   - `url`: Optional link to original material
   - `doc_id`: Reference to internal documents

2. **Quality Metrics**:
   - `confidence`: Score (0.0-1.0) indicating reliability
   - `retrieved_at`: Timestamp for when information was sourced
   - `citation`: Properly formatted citation

3. **Extensibility**:
   - `metadata`: Flexible field for additional source-specific information

### GraphRAG Integration (Phase 3A)

Phase 3A extends the basic source attribution model with Microsoft's GraphRAG (Graph-based Retrieval-Augmented Generation) integration for more sophisticated source attribution:

1. **Enhanced Data Models**:
   - `Entity` model for knowledge graph entities
   - `Relationship` model for connections between entities
   - `EnhancedSource` with entity extraction capabilities
   - `KnowledgeGraph` for structured knowledge representation

2. **GraphRAG Service Implementation**:
   - Mock implementation of GraphRAG for development and testing
   - Entity extraction from text with NER capabilities
   - Source indexing and retrieval with relevance scoring
   - Attributed prompt generation for enhanced context

3. **XML-Specific Attribution**:
   - `XmlAttributionService` for processing XML documents
   - Node-level attribution with multiple sources
   - Entity extraction from XML content
   - Integration with web search results for enhanced attribution

4. **Integration with Entity Detection**:
   - Entity extraction from XML content
   - Relationship detection between entities
   - Confidence scoring based on source quality
   - Attribution metadata for entities and relationships

### GraphRAG MCP Server (Phase 3A Enhanced)

To improve flexibility and scalability, a GraphRAG MCP (Microservice Communication Protocol) Server has been implemented:

1. **Microservice Architecture**:
   - Standalone Node.js Express server for GraphRAG capabilities
   - RESTful API for accessing all GraphRAG functionality
   - Decoupled from the main Python application
   - Language-agnostic integration through HTTP

2. **Key API Endpoints**:
   - `/api/tools/graphrag_index_source`: Document ingestion
   - `/api/tools/graphrag_extract_entities`: Entity extraction
   - `/api/tools/graphrag_query`: Source retrieval
   - `/api/tools/graphrag_relationship_query`: Relationship querying
   - `/api/tools/graphrag_entity_lookup`: Entity information
   - `/api/tools/graphrag_concept_map`: Visualization generation

3. **Optimized Performance**:
   - Caching layer for frequent queries
   - Rate limiting for stability
   - Asynchronous processing
   - Vector database integration for semantic search

4. **Python Client Integration**:
   - `GraphRAGClient` for agent integration
   - `XmlGraphRAGAgent` extends XmlAgent with GraphRAG capabilities
   - Seamless fallback to built-in attribution if server is unavailable
   - Environment variable configuration

### Technical Implementation

The source attribution system is implemented across several components:

1. **Data Models**:
   - `Source` class in `models.py`
   - `SourceType` enum for standardized categorization
   - Extension of `XmlNode` to include sources
   - Extension of `TaskResult` to track attribution
   - GraphRAG-specific models in `source_model.py`

2. **Conversion Utilities**:
   - `from_dict()` method to create Sources from dictionaries
   - `to_dict()` method for serialization
   - GraphRAG indexing and retrieval methods

3. **Agent Integration**:
   - Helper methods in `XmlAgent` for source attribution
   - Support in `ResearchSupervisorAgent` for source enrichment
   - Enhanced XML generation with source elements
   - Entity extraction with GraphRAG source attribution

4. **Frontend Display**:
   - Collapsible source sections in the UI
   - Confidence visualization
   - Citation display and links to original sources
   - Entity relationship visualization

### XML Schema for Sources

Sources are represented in enriched XML using this structure:

```xml
<sources>
  <source id="source-123" type="web" confidence="0.92" url="https://example.com" retrieved_at="2023-05-01T14:30:00Z">
    <title>Example Reference Source</title>
    <citation>Example Reference (2023). Retrieved May 1, 2023.</citation>
    <metadata>
      <author>John Smith</author>
      <publisher>Example Press</publisher>
    </metadata>
  </source>
  <!-- Additional sources... -->
</sources>
```

### Testing

The source attribution implementation includes:
1. Unit tests for the Source model
2. Tests for attribution methods in the XmlAgent
3. Integration tests ensuring attribution flows through the system

## Web Search Agent Implementation

Phase 3 introduces a dedicated Web Search Agent to enhance research capabilities with external sources. This agent provides comprehensive source attribution for all web content.

### Web Search Agent Architecture

The WebSearchAgent extends BaseAgent with specialized capabilities:

1. **Core Functionalities**:
   - Web search using various search engines
   - Content fetching and processing
   - Entity research with source attribution
   - URL validation and content extraction

2. **Task Intents**:
   - `search`: Performs web searches with source attribution
   - `fetch_content`: Retrieves and analyzes content from specified URLs
   - `research_entity`: Conducts comprehensive research on a given entity

3. **Source Attribution**:
   - Automatic confidence scoring based on result rank
   - Rich metadata capture for each source
   - Standardized citation generation
   - URL extraction and validation

### Search Result Processing

The agent processes search results with consistent source attribution:

```python
async def _process_search_results(
    self, 
    search_results: List[SearchResult], 
    query: str,
    context_type: str = "search"
) -> Tuple[List[Dict[str, Any]], List[Source]]:
    """Process search results with source attribution."""
    results_with_sources = []
    sources = []
    
    # Dynamic confidence calculation
    for i, result in enumerate(search_results):
        # Calculate confidence (higher ranked results get higher confidence)
        confidence = max(0.3, 0.85 - (i * 0.05))
        
        # Create source object with proper attribution
        source = self._create_source(
            title=result.title,
            source_type=SourceType.WEB,
            url=result.url,
            confidence=confidence,
            context={
                "query": query,
                "context_type": context_type,
                "rank": i + 1,
                "snippet": result.snippet
            }
        )
        
        # Link result to source
        result_dict = {
            "title": result.title,
            "snippet": result.snippet,
            "url": result.url,
            "confidence": confidence,
            "source_id": source.source_id,
            "source_type": source.source_type.value
        }
        
        results_with_sources.append(result_dict)
        sources.append(source)
    
    return results_with_sources, sources
```

### Integration with Research Supervisor

The Web Search Agent integrates with the Research Supervisor to:

1. Enhance entity research with external sources
2. Provide alternative definitions and contexts
3. Validate information from internal documents
4. Generate properly attributed research results

When the `--with-search` option is specified, the Research Supervisor automatically includes the Web Search Agent in the research workflow.

### Source Attribution Quality

The Web Search Agent implements a sophisticated source attribution approach:

1. **Confidence Calculation**:
   - Base confidence (0.85) for top results
   - Linear decay (0.05 per rank) for lower-ranked results
   - Minimum confidence threshold (0.3) for all sources
   - Domain-based confidence adjustments based on reputation

2. **Metadata Enrichment**:
   - Query context preservation
   - Search rank tracking
   - Snippet content for context
   - Domain and content type classification

3. **Citation Generation**:
   - Structured citations with title, domain, and date
   - URL inclusion for direct verification
   - Proper escaping and formatting for XML output

## Future Enhancements

### CLI Enhancements

1. Advanced filtering options for entity types
2. Support for additional document types beyond XML
3. Integration with more research sources
4. Custom templates for research output
5. Batch processing of multiple documents
6. Confidence score filtering for sources

### Web UI Enhancements

1. Full React implementation with component architecture
2. Enhanced authentication and user management
3. Real-time collaborative features
4. Advanced visualization of entity relationships
5. Integration with external knowledge bases
6. Expanded source review and validation interfaces

### Web Search Agent Enhancements

1. Support for multiple search providers (Google, Bing, DuckDuckGo)
2. Deep content analysis for improved source quality assessment
3. Fact-checking against trusted knowledge bases
4. Integration with academic search engines and databases
5. Multi-source corroboration for improved confidence scoring
6. Domain reputation database for better source qualification

## Related Documentation

- [XML Agent Guide](../guides/xml_verification.md)
- [Web UI Guide](../guides/ui_guide.md)
- [Frontend Architecture](../architecture/frontend_architecture.md)
- [UX Design](../uxd/ux_design.md)