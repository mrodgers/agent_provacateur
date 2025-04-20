# Document Types in Agent Provocateur

This document describes the document type system implemented in the Agent Provocateur framework.

## Overview

Agent Provocateur supports multiple document types through a type hierarchy:

- `Document` (base class)
  - `DocumentContent` (text documents)
  - `PdfDocument` (PDF documents)
  - `ImageDocument` (image documents)
  - `CodeDocument` (code documents)
  - `StructuredDataDocument` (structured data)

## Document Base Class

All document types inherit from the `Document` base class, which provides common fields:

```python
class Document(BaseModel):
    """Base model for all document types."""
    
    doc_id: str                   # Unique identifier
    doc_type: str                 # Document type identifier
    title: str                    # Document title
    created_at: str               # Creation timestamp
    updated_at: Optional[str]     # Last update timestamp
    metadata: Dict[str, Any]      # Additional metadata
```

## Specialized Document Types

### Text Documents

Text documents (`DocumentContent`) store content in Markdown and optional HTML:

```python
class DocumentContent(Document):
    """Model for text document content."""
    
    markdown: str                 # Markdown content
    html: Optional[str]           # Optional HTML content
    doc_type: str = "text"        # Document type identifier
```

### PDF Documents

PDF documents (`PdfDocument`) include a URL and page-by-page text extraction:

```python
class PdfDocument(Document):
    """Model for PDF document content."""
    
    url: str                      # URL to the original PDF
    pages: List[PdfPage]          # List of extracted pages
    doc_type: str = "pdf"         # Document type identifier
```

### Image Documents

Image documents (`ImageDocument`) include metadata and references:

```python
class ImageDocument(Document):
    """Model for image document content."""
    
    url: str                      # URL to the image
    alt_text: str                 # Alternative text
    caption: Optional[str]        # Optional caption
    width: Optional[int]          # Image width in pixels
    height: Optional[int]         # Image height in pixels
    format: str                   # Image format (png, jpg, etc.)
    doc_type: str = "image"       # Document type identifier
```

### Code Documents

Code documents (`CodeDocument`) include source code with language and metrics:

```python
class CodeDocument(Document):
    """Model for code document content."""
    
    content: str                  # Source code content
    language: str                 # Programming language
    line_count: int               # Number of lines
    doc_type: str = "code"        # Document type identifier
```

### Structured Data Documents

Structured data documents (`StructuredDataDocument`) include format-specific data:

```python
class StructuredDataDocument(Document):
    """Model for structured data document content."""
    
    data: Dict[str, Any]          # Structured data content
    schema_def: Optional[Dict]    # Optional schema definition
    format: str                   # Data format (json, csv, etc.)
    doc_type: str = "structured_data" # Document type identifier
```

## Working with Documents

### API Endpoints

The MCP server provides unified document endpoints:

- `GET /documents` - List all documents with optional type filtering
- `GET /documents/{doc_id}` - Get a specific document by ID

### MCP Client

The MCP client provides methods for working with documents:

```python
# List all documents
documents = await client.list_documents()

# List documents of a specific type
text_docs = await client.list_documents(doc_type="text")

# Get a specific document
doc = await client.get_document("doc1")

# Type-specific processing
if doc.doc_type == "text":
    print(doc.markdown)
elif doc.doc_type == "code":
    print(f"Language: {doc.language}")
```

### Agent Handlers

Agents provide handlers for document operations:

```python
# List documents
doc_list = await doc_agent.handle_list_documents({"doc_type": "text"})

# Get a document
doc = await doc_agent.handle_get_document({"doc_id": "doc1"})

# Process document
summary = await doc_processing_agent.handle_summarize_document({"doc_id": "doc1"})
```

## Document Processing

The `DocumentProcessingAgent` provides type-specific document processing:

- Text documents: Extract word count, summarize content
- PDF documents: Count pages, analyze text extraction
- Image documents: Analyze metadata, dimensions
- Code documents: Analyze language, line count, structure
- Structured data: Parse format, analyze schema and content

## CLI Interface

The CLI includes document listing and filtering:

```bash
# List all documents
ap-client list-documents

# List documents of a specific type
ap-client list-documents --type code

# Get a specific document
ap-client doc doc1
```