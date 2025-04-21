# GraphRAG Integration Plan for Phase 3A: Source Attribution

## Overview

This document outlines a detailed implementation plan for integrating Microsoft's GraphRAG library into Phase 3A of the Agent Provocateur project, focusing on source attribution. GraphRAG combines traditional Retrieval-Augmented Generation (RAG) with knowledge graphs to provide enhanced context retrieval and source attribution capabilities.

## 1. Background and Motivation

### Current Challenges

- Need for accurate attribution of information to sources
- Complex relationship tracking between entities and sources
- Efficient retrieval of relevant sources for context
- Explanation of source relevance to users

### GraphRAG Solution

[GraphRAG](https://github.com/microsoft/graphrag) is Microsoft's library that enhances retrieval-augmented generation by incorporating graph structures. Key capabilities include:

- Hybrid retrieval combining embedding similarity with graph structure
- Entity-centric knowledge organization
- Relationship-based context expansion
- Built-in attribution and provenance tracking
- Explanations for why sources are relevant

## 2. Integration Architecture

```
+--------------------+    +-------------------+    +--------------------+
| Document Processing|    | Web Search Agent  |    | Other Input Sources|
+--------+-----------+    +--------+----------+    +---------+----------+
         |                         |                         |
         v                         v                         v
+------------------------------------------------------+
|                  Source Extraction Layer             |
+------------------------------------------------------+
         |                         |                         |
         v                         v                         v
+------------------------------------------------------+
|               GraphRAG Integration Layer             |
|  +----------------+    +------------------+          |
|  | Entity Linking |    | Document Indexing|          |
|  +----------------+    +------------------+          |
|                                                      |
|  +----------------+    +------------------+          |
|  | Graph Storage  |    | Vector Embeddings|          |
|  +----------------+    +------------------+          |
+------------------------------------------------------+
         |                         |                         |
         v                         v                         v
+---------------+    +-------------------+    +----------------+
| Query         |    | Context           |    | Explanation    |
| Processing    |    | Generation        |    | Generation     |
+---------------+    +-------------------+    +----------------+
         |                         |                         |
         v                         v                         v
+------------------------------------------------------+
|                    Agent LLM Interface               |
+------------------------------------------------------+
         |                         |                         |
         v                         v                         v
+---------------+    +-------------------+    +----------------+
| Source UI     |    | Attribution       |    | Exploration    |
| Components    |    | Visualization     |    | Interface      |
+---------------+    +-------------------+    +----------------+
```

## 3. Implementation Plan

### Week 1: Foundation and Integration

#### Days 1-2: GraphRAG Setup & Configuration

1. **Environment Setup**
   - Install GraphRAG library and dependencies
   - Configure integration with our project structure
   - Set up test environment for validation

2. **Data Model Alignment**
   - Define entity schema compatible with GraphRAG
   - Create source metadata schema
   - Establish relationship types for the knowledge graph
   - Design attribution model for sources

3. **Configuration**
   - Select and configure embedding models
   - Set up graph database backend
   - Configure indexing parameters
   - Establish retrieval settings

#### Days 3-4: Source Extraction Enhancement

1. **Document Processing Pipeline**
   - Implement document parsers for entity extraction
   - Create metadata extractors for different source types
   - Build relationship extractors
   - Develop confidence scoring for sources

2. **Web Search Integration**
   - Enhance web search agent to extract structured data
   - Implement web content scraping with entity recognition
   - Create source validation for web content
   - Build caching mechanism for web sources

3. **Entity Recognition System**
   - Implement named entity recognition
   - Create concept extraction for abstract entities
   - Build entity disambiguation using context
   - Develop entity linking to existing knowledge

#### Days 5-6: GraphRAG Integration with Agents

1. **Context Generation API**
   - Create context building service using GraphRAG
   - Implement relevance-based source selection
   - Build prompt construction with attribution markers
   - Develop context pruning for length management

2. **Attribution Tracking**
   - Implement source reference format for prompts
   - Create reference extraction from responses
   - Build attribution consistency checks
   - Develop confidence scoring for attributions

3. **Agent-GraphRAG Interface**
   - Create query processing for agent requests
   - Implement source retrieval before LLM queries
   - Build attribution post-processing for responses
   - Develop explanation generation for source usage

### Week 2: UI Development and Extended Features

#### Days 1-3: Frontend Source Visualization

1. **Source Listing Component**
   - Create source card design
   - Implement filtering and sorting
   - Build pagination for large source collections
   - Develop search functionality

2. **Graph Visualization**
   - Implement interactive graph view of sources and entities
   - Create entity-centric exploration
   - Build relationship visualization
   - Develop drill-down capabilities

3. **Source Detail View**
   - Create comprehensive source information display
   - Implement citation formatting
   - Build confidence and reliability indicators
   - Develop related sources section

#### Days 4-5: Advanced Attribution Features

1. **Source Comparison**
   - Implement side-by-side source comparison
   - Create conflict detection between sources
   - Build consensus visualization
   - Develop source timeline for chronological context

2. **Source Quality Assessment**
   - Implement source reliability metrics
   - Create source type classification
   - Build validation status indicators
   - Develop completeness assessment

3. **Claim-Source Validation**
   - Implement claim extraction from content
   - Create claim-source linking interface
   - Build validation workflow for claims
   - Develop claim strength indicators

#### Days 6-7: Testing and Refinement

1. **Performance Testing**
   - Conduct load testing with large document collections
   - Implement performance optimizations
   - Create monitoring for system resources
   - Develop caching strategies

2. **User Experience Testing**
   - Conduct usability testing of source attribution UI
   - Implement UX refinements
   - Create accessibility improvements
   - Develop responsive design adaptations

3. **Documentation and Examples**
   - Create comprehensive API documentation
   - Build example notebooks for common use cases
   - Develop user guide for attribution features
   - Create technical architecture documentation

## 4. Technical Implementation Details

### Source Schema

```json
{
  "source_id": "string",
  "source_type": "web_page|document|scholarly_article|user_input|agent_generated",
  "title": "string",
  "content": "string",
  "url": "string?",
  "authors": ["string"],
  "publication_date": "datetime?",
  "retrieval_date": "datetime",
  "confidence_score": "float",
  "reliability_score": "float",
  "entity_mentions": [
    {
      "entity_id": "string",
      "entity_type": "string",
      "mentions": [{"start": "int", "end": "int", "text": "string"}]
    }
  ],
  "relationships": [
    {
      "source_entity_id": "string",
      "target_entity_id": "string", 
      "relation_type": "string"
    }
  ],
  "metadata": {
    "domain": "string?",
    "language": "string",
    "word_count": "int",
    "additional_fields": {}
  }
}
```

### GraphRAG Document Integration

```python
from graphrag import GraphRAGDocument, GraphRAGIndexer

def index_source_document(source):
    # Create a GraphRAG document with source attribution
    doc = GraphRAGDocument(
        content=source.content,
        metadata={
            "source_id": source.source_id,
            "source_type": source.source_type,
            "title": source.title,
            "url": source.url,
            "confidence_score": source.confidence_score,
            "retrieval_date": source.retrieval_date
        }
    )
    
    # Add entities from the source
    for entity_mention in source.entity_mentions:
        for mention in entity_mention.mentions:
            doc.add_entity(
                entity_mention.entity_id,
                entity_mention.entity_type,
                [(mention.start, mention.end)]
            )
    
    # Add relationships
    for rel in source.relationships:
        doc.add_relationship(
            rel.source_entity_id,
            rel.target_entity_id,
            rel.relation_type
        )
    
    # Index the document
    indexer = GraphRAGIndexer()
    indexer.add_document(doc)
    
    return doc
```

### Agent Source Attribution Integration

```python
from graphrag import GraphRAGRetriever

def get_sources_for_agent_context(query, focus_entities=None, max_sources=5):
    retriever = GraphRAGRetriever()
    
    # Configure retrieval options
    retrieval_config = {
        "max_sources": max_sources,
        "min_relevance": 0.7,
        "include_explanations": True,
        "traversal_depth": 2
    }
    
    # Retrieve sources with different strategies based on context
    if focus_entities:
        # Entity-centric retrieval
        results = retriever.retrieve_for_entities(
            focus_entities,
            config=retrieval_config
        )
    else:
        # Query-based retrieval
        results = retriever.retrieve(
            query,
            config=retrieval_config
        )
    
    # Format sources for agent consumption
    formatted_sources = []
    for result in results:
        formatted_sources.append({
            "content": result.content,
            "metadata": result.metadata,
            "relevance_score": result.relevance_score,
            "explanation": result.explanation,
            "entities": result.entities
        })
    
    return formatted_sources
```

### Prompt Construction with Attribution

```python
def build_attributed_prompt(query, sources):
    """Build a prompt with attribution markers."""
    prompt_parts = [
        "Answer the question based on these sources:\n\n"
    ]
    
    # Add each source with clear attribution markers
    for i, source in enumerate(sources):
        source_id = f"SOURCE_{i+1}"
        prompt_parts.append(
            f"[{source_id}: {source['metadata']['title']} "
            f"({source['metadata']['source_type']}, "
            f"confidence: {source['metadata']['confidence_score']:.2f})]\n"
        )
        prompt_parts.append(source["content"] + "\n")
        prompt_parts.append(f"[END {source_id}]\n\n")
    
    # Add instructions for attribution in the response
    prompt_parts.append(
        "\nQuestion: " + query + "\n\n"
        "Answer the question based on the sources provided. "
        "For each piece of information in your answer, indicate which "
        "source(s) it came from using source numbers [SOURCE_X]."
    )
    
    return "".join(prompt_parts)
```

### Attribution Extraction

```python
def extract_attributions(response):
    """Extract source attributions from a response."""
    # Pattern to find source references like [SOURCE_1]
    source_pattern = r'\[SOURCE_(\d+)\]'
    
    # Find all source references
    source_refs = re.findall(source_pattern, response)
    
    # Count references to each source
    attribution_counts = {}
    for ref in source_refs:
        source_id = int(ref)
        if source_id in attribution_counts:
            attribution_counts[source_id] += 1
        else:
            attribution_counts[source_id] = 1
    
    return attribution_counts
```

## 5. Source Types and Prioritization

### Priority 1: Web Search Results
- Implementation: Direct integration with web search agent
- Key fields: URL, title, snippet, retrieval date
- Entity extraction: NER on search snippets
- Confidence: Based on search ranking and source domain

### Priority 2: User-Provided Documents
- Implementation: Enhanced document processing pipeline
- Key fields: Content, title, upload date, user annotations
- Entity extraction: Full NER and concept extraction
- Confidence: High (user-selected content)

### Priority 3: Web Page Content
- Implementation: Content extraction from search results
- Key fields: Full text, HTML metadata, publication date
- Entity extraction: Comprehensive entity and relationship extraction
- Confidence: Based on domain authority and content quality

### Priority 4: Agent-Generated Content
- Implementation: Attribution tracking in agent outputs
- Key fields: Generated content, reasoning steps, source references
- Entity extraction: Preserved from input sources
- Confidence: Based on source confidence and reasoning quality

## 6. Frontend Components

### Source List View
- Filterable, sortable list of sources
- Source cards with key metadata
- Relevance indicators
- Quick actions (view details, export citation)

### Source Detail View
- Complete source metadata
- Content preview with entity highlighting
- Citation formats
- Related entities and sources
- Confidence and reliability metrics

### Entity-Source Graph Explorer
- Interactive visualization of entity-source relationships
- Filtering by entity types and source types
- Path exploration between entities
- Source clustering by topic or publication

### Attribution Sidebar
- Context-sensitive source attribution
- Highlighted text with source indicators
- Confidence visualization
- Conflict indicators for contradictory sources

## 7. Testing Strategy

### Unit Tests
- GraphRAG integration components
- Source extraction pipeline
- Entity recognition accuracy
- Attribution tracking

### Integration Tests
- End-to-end attribution flow
- Agent-GraphRAG interaction
- Frontend-backend communication
- Source retrieval performance

### Performance Tests
- Large document collection indexing
- Query response time
- Memory usage optimization
- Scaling characteristics

### User Experience Tests
- Attribution clarity evaluation
- Source exploration workflows
- Information finding efficiency
- User confidence in attributions

## 8. Risks and Mitigations

### Risk: GraphRAG Library Limitations
- **Mitigation**: Create abstraction layer for potential replacement
- **Fallback**: Implement critical features directly if needed

### Risk: Integration Complexity
- **Mitigation**: Incremental integration with continuous testing
- **Fallback**: Prioritize core functionality over advanced features

### Risk: Performance with Large Data
- **Mitigation**: Implement caching and pagination
- **Fallback**: Limit context size with prioritization

### Risk: Source Quality Variability
- **Mitigation**: Implement comprehensive source evaluation
- **Fallback**: Provide clear confidence indicators to users

## 9. Future Enhancements for Later Phases

1. **Advanced Source Verification**
   - Cross-source claim validation
   - Automated fact-checking
   - Temporal consistency verification

2. **Expanded Knowledge Integration**
   - Connection to external knowledge bases
   - Domain-specific knowledge integration
   - Multilingual source support

3. **Interactive Attribution Refinement**
   - User feedback on source quality
   - Collaborative source evaluation
   - Expert verification workflows

4. **Personalized Source Relevance**
   - User preference-based source prioritization
   - Domain expertise adaptation
   - Context-aware source selection

## 10. Success Metrics

1. **Attribution Accuracy**
   - >95% of statements correctly attributed to sources
   - <2% attribution errors in agent responses
   - >90% user confidence in attribution accuracy

2. **Source Quality Assessment**
   - >90% accuracy in source reliability classification
   - >85% correlation between predicted and actual source quality
   - <5% false positives for unreliable sources

3. **Performance**
   - <200ms average source retrieval time
   - <500ms for context generation with sources
   - <3s for complete graph exploration rendering

4. **User Experience**
   - >90% task completion rate for source-related tasks
   - <30s average time to find source for a given claim
   - >4.5/5 user satisfaction with attribution clarity

## Conclusion

This integration of Microsoft's GraphRAG library into Phase 3A provides a solid foundation for our source attribution system. By leveraging GraphRAG's hybrid retrieval capabilities and knowledge graph structure, we can deliver a more comprehensive and accurate attribution system with less development effort. The phased implementation approach ensures that we can progressively enhance the system while maintaining usability throughout the development process.