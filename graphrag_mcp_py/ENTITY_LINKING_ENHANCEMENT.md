# Enhanced Entity Linking for GraphRAG MCP (Python)

This document describes the implementation of enhanced entity linking capabilities in the GraphRAG MCP Python server.

## Overview

The enhanced entity linking system improves the quality of entity extraction, relationship detection, and knowledge integration in the GraphRAG MCP server. It provides the following key features:

1. **External Knowledge Base Integration**: Connect to Wikidata and other knowledge bases to enrich entity information
2. **Contextual Entity Disambiguation**: Resolve ambiguous entity mentions based on context
3. **Improved Relationship Detection**: Identify meaningful relationships between entities
4. **Local Knowledge Base**: Build and maintain a local knowledge graph for future entity linking
5. **Advanced Entity Type Classification**: Better determine entity types based on context

## Implementation Details

### Architecture

The implementation consists of the following components:

1. **EntityLinker**: The main class that coordinates entity extraction, disambiguation, and relationship creation
2. **KnowledgeBase**: Abstract base class for knowledge base implementations
3. **LocalKnowledgeBase**: Implementation of a local, file-based knowledge base
4. **WikidataKnowledgeBase**: Integration with the Wikidata knowledge graph via SPARQL

### Configuration

The enhanced entity linking system can be configured through environment variables:

```
# Entity linking settings
ENABLE_ENHANCED_ENTITY_LINKING=true
USE_WIKIDATA_KB=true
LOCAL_KB_PATH=./data/knowledge_base.json
WIKIDATA_CACHE_PATH=./data/wikidata_cache.json
ENTITY_LINKING_CONFIDENCE_THRESHOLD=0.7
MAX_ENTITY_RELATIONSHIPS=10
CONTEXTUAL_DISAMBIGUATION=true
```

These settings can also be overridden on a per-request basis through the API.

### Entity Extraction Process

The enhanced entity extraction process follows these steps:

1. **Candidate Extraction**: Identify potential entities using patterns, capitalization, and keyword matching
2. **Knowledge Base Lookup**: Look up entities in local and external knowledge bases
3. **Entity Type Classification**: Determine entity types based on context and knowledge base information
4. **Relationship Creation**: Identify relationships between entities
5. **Disambiguation**: Resolve ambiguous entity mentions using context
6. **Knowledge Integration**: Add new entities and relationships to the local knowledge base

### Entity Disambiguation Algorithm

The disambiguation algorithm uses the following approach:

1. For each ambiguous entity mention, identify candidate entities from knowledge bases
2. Calculate contextual similarity scores using the sentence transformer model
3. Select the entity with the highest similarity score (if above threshold)
4. Add disambiguation metadata to the selected entity

### Relationship Detection

Relationships between entities are detected using:

1. Co-occurrence patterns in text
2. Contextual clues from surrounding text
3. Entity type compatibility (e.g., PERSON to ORGANIZATION suggests employment relationship)
4. Knowledge base relationship lookups
5. Pattern matching for common relationship indicators

## API Extensions

The API has been extended to support the enhanced entity linking capabilities:

### Entity Extraction Request

Enhanced parameters for entity extraction:

```json
{
  "text": "The Paris Agreement was signed by the United Nations.",
  "use_enhanced_linking": true,
  "use_contextual_disambiguation": true,
  "use_external_kb": true
}
```

### Entity Extraction Response

Enhanced response including relationship information:

```json
{
  "success": true,
  "entities": [
    {
      "entity_id": "ent_1234abcd",
      "entity_type": "concept",
      "name": "Paris Agreement",
      "aliases": ["Paris Climate Agreement", "Paris Climate Accord"],
      "description": "International treaty on climate change mitigation",
      "metadata": {
        "confidence": 0.95,
        "source": "wikidata",
        "wikidata_id": "Q2980158"
      }
    },
    {
      "entity_id": "ent_5678efgh",
      "entity_type": "organization",
      "name": "United Nations",
      "aliases": ["UN"],
      "description": "Intergovernmental organization",
      "metadata": {
        "confidence": 0.97,
        "source": "wikidata",
        "wikidata_id": "Q1065"
      }
    }
  ],
  "relationships": [
    {
      "relationship_id": "rel_abcd1234",
      "source_entity_id": "ent_5678efgh",
      "target_entity_id": "ent_1234abcd",
      "relation_type": "created_by",
      "confidence": 0.9,
      "metadata": {
        "source": "text_analysis",
        "extraction_method": "pattern_matching"
      }
    }
  ],
  "sources": ["enhanced_entity_linking", "contextual_disambiguation", "wikidata_kb", "local_kb"],
  "disambiguation_applied": true
}
```

## Testing

The implementation includes unit tests for:

1. Entity extraction
2. Entity type determination
3. Relationship detection
4. Knowledge base operations
5. Disambiguation
6. Integration with the GraphRAG service

## Performance Considerations

The enhanced entity linking system includes several performance optimizations:

1. **Local Caching**: Results from Wikidata are cached locally to reduce API calls
2. **Embedding Memoization**: Entity embeddings are cached to avoid recomputation
3. **Progressive Enhancement**: Simple extractions are done first, with more expensive operations only if needed
4. **Confidence Thresholds**: Only high-confidence entities and relationships are returned

## Future Improvements

Potential future enhancements include:

1. **Additional Knowledge Base Integrations**: Support for DBpedia, ConceptNet, and domain-specific KBs
2. **Improved Multilingual Support**: Better handling of non-English text
3. **Entity Linking Feedback Loop**: Incorporate user feedback to improve entity linking accuracy
4. **Named Entity Recognition**: Integration with state-of-the-art NER models
5. **Domain Adaptation**: Fine-tuning for specific domains (medical, legal, etc.)

## Conclusion

The enhanced entity linking system significantly improves the quality of entity extraction, relationship detection, and knowledge integration in the GraphRAG MCP server. It enables more accurate source attribution, better query understanding, and richer knowledge graph construction.