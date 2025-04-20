# Phase 3: CLI Research Integration for XML Agent

This document outlines Phase 3 of the XML agent integration into the Agent Provocateur framework, adding a unified CLI interface for XML research workflows.

## Overview

Phase 3 extends the Agent Provocateur CLI with a new `research` command that integrates the XML agent's entity extraction and validation capabilities with the ResearchSupervisorAgent created in Phase 2. This provides an end-to-end workflow for extracting entities from XML documents, researching them, and generating enriched XML output.

## Implementation Details

### CLI Integration

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

## Usage Examples

### Basic Research Command

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

### Integration with Existing XML Workflows

The new research command integrates with existing XML verification capabilities:

1. Upload an XML document using the XML CLI
2. Run entity extraction and research using the research command
3. Review research results with detailed entity definitions
4. Save enriched XML for further processing or documentation

## Testing

The implementation includes comprehensive testing:

1. **Unit Tests**: Tests for the research command integration
2. **Integration Tests**: Tests for the full workflow from CLI to output
3. **Validation Tests**: Tests for XML output validation

Tests cover both happy paths and error handling scenarios to ensure robustness.

## Future Enhancements

Potential future enhancements to the research command include:

1. Advanced filtering options for entity types
2. Support for additional document types beyond XML
3. Integration with more research sources
4. Custom templates for research output
5. Batch processing of multiple documents

## Related Documentation

- [XML Agent Guide](../guides/xml_verification.md)
- [Research Supervisor Agent](../implementation/phase2_implementation.md)
- [XML Entity Extraction](../implementation/phase1_implementation.md)