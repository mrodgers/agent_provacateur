# Source Attribution Guide

This guide explains how source attribution works in Agent Provocateur and how to use it effectively.

## Introduction

Source attribution is a critical feature that provides transparency and credibility for AI-generated content. In Agent Provocateur, every piece of information added by AI agents is linked to its source, allowing users to verify the quality and reliability of the content.

## Understanding Source Structure

### Source Types

Agent Provocateur supports various source types:

| Type | Description | Example |
|------|-------------|---------|
| `web` | Web pages and online articles | Wikipedia articles, news sites |
| `document` | Internal documents | PDFs, Word documents, code files |
| `database` | Database records | Internal knowledge bases |
| `api` | API responses | External service data |
| `knowledge_base` | Structured knowledge bases | Internal structured data |
| `calculation` | Calculated/derived data | Statistical analysis |
| `user_provided` | Information from users | System inputs |
| `other` | Miscellaneous sources | Any other source type |

### Source Confidence

Each source has a confidence score from 0.0 to 1.0:

- **0.9 - 1.0**: Highly trusted, verified sources
- **0.7 - 0.9**: Reliable sources with minor uncertainties
- **0.5 - 0.7**: Moderately reliable sources
- **0.3 - 0.5**: Somewhat questionable sources
- **0.0 - 0.3**: Low confidence, unverified sources

## Viewing Source Information

### In the Web UI

1. Open any entity in the results panel
2. Click the "Sources" dropdown to expand source information
3. View confidence scores, source types, and links when available
4. Check citations for proper attribution

### In XML Output

Sources are included in the enriched XML with this structure:

```xml
<entity name="Example Entity">
  <definition>An example entity definition.</definition>
  <sources>
    <source id="source-123" type="web" confidence="0.92">
      <title>Example Source</title>
      <citation>Example Citation (2023)</citation>
    </source>
  </sources>
</entity>
```

## Using Source Attribution in Research

### Filtering by Confidence

When conducting research, you can filter sources by confidence level:

```bash
# CLI: Filter for high-confidence sources only
ap-client research my-document --min-source-confidence 0.8
```

In the web UI, sources are sorted by confidence level with higher confidence sources listed first.

### Evaluating Source Quality

When reviewing AI-generated content, consider:

1. **Diversity of sources**: Multiple source types increase reliability
2. **Confidence scores**: Higher scores indicate greater reliability
3. **Source recency**: Check the `retrieved_at` timestamp
4. **Citation quality**: Well-formatted citations are easier to verify

## Implementing Source Attribution (For Developers)

### Using the Source Model

```python
from agent_provocateur.models import Source, SourceType

# Create a new source
source = Source(
    source_id="unique-id",
    source_type=SourceType.WEB,
    title="Example Source",
    url="https://example.com",
    confidence=0.85,
    citation="Example Citation (2023)"
)
```

### Adding Sources to XmlNodes

```python
from agent_provocateur.models import XmlNode, Source

# Create a source
source = Source(...)

# Add to node
node = XmlNode(...)
node.sources.append(source)
```

### Converting Between Formats

```python
# Convert dictionary to Source
source_dict = {
    "type": "web",
    "title": "Example Source",
    "url": "https://example.com"
}
source = Source.from_dict(source_dict)

# Convert Source to dictionary
source_dict = source.to_dict()
```

## Best Practices

1. **Always include sources** for any factual claim or definition
2. **Set appropriate confidence scores** based on source reliability
3. **Provide complete citations** whenever possible
4. **Include URLs** for web sources to enable verification
5. **Update source timestamps** when refreshing information

## Troubleshooting

### Missing Sources

If sources are missing in the UI or XML output:

1. Check that the entity was processed with source attribution enabled
2. Verify that the confidence threshold isn't filtering out low-confidence sources
3. Make sure the source format is compatible with the display mechanism

### Incorrect Confidence Scores

If confidence scores seem incorrect:

1. Review the source type and ensure it's appropriate
2. Check if multiple sources are being averaged incorrectly
3. Verify that the source evaluation logic is functioning correctly

## Implementation Examples

### Web Search Agent

The Web Search Agent demonstrates comprehensive source attribution:

```python
class WebSearchAgent(BaseAgent):
    # ... other methods ...
    
    async def _process_search_results(
        self, 
        search_results: List[SearchResult], 
        query: str,
        context_type: str = "search"
    ) -> Tuple[List[Dict[str, Any]], List[Source]]:
        """Process search results, adding comprehensive source attribution."""
        results_with_sources = []
        sources = []
        
        # Get confidence parameters from config
        base_confidence = self.search_config["base_confidence"]
        confidence_decay = self.search_config["confidence_decay"]
        min_confidence = self.search_config["min_confidence"]
        
        for i, result in enumerate(search_results):
            # Calculate confidence - higher ranked results get higher confidence
            confidence = max(min_confidence, base_confidence - (i * confidence_decay))
            
            # Create a proper Source object for this result
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
            
            # Add to sources list
            sources.append(source)
            
            # Create result dict with source reference
            result_dict = {
                "title": result.title,
                "snippet": result.snippet,
                "url": result.url,
                "rank": i + 1,
                "confidence": confidence,
                "source_id": source.source_id,
                "source_type": source.source_type.value
            }
            
            results_with_sources.append(result_dict)
        
        return results_with_sources, sources
```

This approach ensures all information provided by search results is properly attributed, traceable, and has an associated confidence level.

### Source Creation Helper Method

A reusable helper method for consistent source creation:

```python
def _create_source(
    self,
    title: str,
    source_type: SourceType,
    url: Optional[str] = None,
    confidence: float = 0.5,
    context: Optional[Dict[str, Any]] = None
) -> Source:
    """
    Create a Source object with consistent formatting.
    """
    # Create a unique ID for this source
    source_id = str(uuid.uuid4())
    
    # Get the current timestamp
    now = datetime.datetime.now()
    
    # Create metadata with any additional context
    metadata = {}
    if context:
        metadata.update(context)
    
    # Generate an appropriate citation based on type
    if source_type == SourceType.WEB and url:
        domain = url.split("//")[-1].split("/")[0]
        citation = f"\"{title}\" {domain}. Retrieved on {now.strftime('%Y-%m-%d')}."
    else:
        citation = f"\"{title}\". Retrieved on {now.strftime('%Y-%m-%d')}."
    
    # Create and return the Source object
    return Source(
        source_id=source_id,
        source_type=source_type,
        title=title,
        url=url,
        retrieved_at=now,
        confidence=confidence,
        metadata=metadata,
        citation=citation
    )
```

## Future Enhancements

Upcoming source attribution features:

1. Source validation tools
2. User-adjustable confidence scores
3. Automated source verification
4. Enhanced source visualization
5. Source quality metrics dashboard
6. Cross-source corroboration scoring
7. ML-based source reliability assessment