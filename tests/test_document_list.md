# Document Test Files for Agent Provocateur

This document lists the test files created to verify document handling functionality.

## Text Documents

| File | Description | Location |
|------|-------------|----------|
| `text_document.md` | Sample markdown document with multiple sections | `tests/test_data/documents/` |

## Code Documents

| File | Description | Location |
|------|-------------|----------|
| `code_document.py` | Python code file with classes and functions | `tests/test_data/documents/` |

## Structured Data Documents

| File | Description | Location |
|------|-------------|----------|
| `structured_data.json` | JSON file with agent configuration | `tests/test_data/documents/` |
| `sample_config.yaml` | YAML configuration file | `tests/test_data/documents/` |

## Image Documents (Placeholder)

In a real implementation, we would add:

| File | Description | Location |
|------|-------------|----------|
| `agent_diagram.png` | Diagram of agent communication | `tests/test_data/documents/` |
| `architecture.jpg` | System architecture | `tests/test_data/documents/` |

## PDF Documents (Placeholder)

In a real implementation, we would add:

| File | Description | Location |
|------|-------------|----------|
| `agent_manual.pdf` | PDF document with agent documentation | `tests/test_data/documents/` |
| `research_paper.pdf` | Sample research paper | `tests/test_data/documents/` |

## Using Documents in Tests

To use these documents in tests:

```python
# Load a text document
text_path = os.path.join(test_data_dir, "text_document.md")
with open(text_path, "r") as f:
    content = f.read()

doc = DocumentContent(
    doc_id="test_doc",
    doc_type="text",
    title="Sample Text Document",
    created_at=timestamp,
    markdown=content,
    html=f"<h1>Sample Document</h1><p>{content}</p>"
)

# Load a structured data document
json_path = os.path.join(test_data_dir, "structured_data.json")
with open(json_path, "r") as f:
    import json
    data = json.load(f)

doc = StructuredDataDocument(
    doc_id="test_json",
    doc_type="structured_data",
    title="Configuration",
    created_at=timestamp,
    data=data,
    format="json"
)
```

## Testing with the Document Processing Agent

The `DocumentProcessingAgent` can process these documents:

```python
# Create a document processing agent
agent = DocumentProcessingAgent(agent_id="doc_processor")

# Process a document
summary = await agent.handle_summarize_document({"doc_id": "test_doc"})

# Process different document types
text_summary = await agent._summarize_text_document(text_doc)
code_summary = await agent._summarize_code_document(code_doc)
data_summary = await agent._summarize_structured_data_document(json_doc)
```