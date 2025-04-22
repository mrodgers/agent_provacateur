"""
Configuration management for GraphRAG MCP server.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class GraphRAGConfig:
    """Configuration for GraphRAG MCP server."""
    
    # Server settings
    PORT: int = int(os.environ.get("PORT", "8083"))
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    
    # Vector database settings
    VECTOR_DB_TYPE: str = os.environ.get("VECTOR_DB_TYPE", "faiss")  # "faiss", "qdrant", "pinecone"
    VECTOR_DB_URL: str = os.environ.get("VECTOR_DB_URL", "")  # For remote vector DBs
    VECTOR_DB_PATH: str = os.environ.get("VECTOR_DB_PATH", "./data/vectors")  # For local vector DBs
    VECTOR_DIMENSION: int = int(os.environ.get("VECTOR_DIMENSION", "384"))  # Default for MiniLM
    
    # Query settings
    MAX_RESULTS: int = int(os.environ.get("MAX_RESULTS", "10"))
    MIN_CONFIDENCE: float = float(os.environ.get("MIN_CONFIDENCE", "0.5"))
    TRAVERSAL_DEPTH: int = int(os.environ.get("TRAVERSAL_DEPTH", "2"))
    
    # Cache settings
    ENABLE_CACHE: bool = os.environ.get("ENABLE_CACHE", "true").lower() == "true"
    MAX_CACHE_SIZE: int = int(os.environ.get("MAX_CACHE_SIZE", "1000"))
    CACHE_TTL: int = int(os.environ.get("CACHE_TTL", "3600"))  # seconds
    
    # Rate limiting
    RATE_LIMIT_WINDOW: int = int(os.environ.get("RATE_LIMIT_WINDOW", "60000"))  # milliseconds
    RATE_LIMIT_MAX: int = int(os.environ.get("RATE_LIMIT_MAX", "100"))
    
    # Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "info").upper()
    LOG_FILE: str = os.environ.get("LOG_FILE", "logs/graphrag_mcp.log")
    
    # Embedding model
    EMBEDDING_MODEL: str = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Entity linking settings
    ENABLE_ENHANCED_ENTITY_LINKING: bool = os.environ.get("ENABLE_ENHANCED_ENTITY_LINKING", "true").lower() == "true"
    USE_WIKIDATA_KB: bool = os.environ.get("USE_WIKIDATA_KB", "true").lower() == "true"
    LOCAL_KB_PATH: str = os.environ.get("LOCAL_KB_PATH", "./data/knowledge_base.json")
    WIKIDATA_CACHE_PATH: str = os.environ.get("WIKIDATA_CACHE_PATH", "./data/wikidata_cache.json")
    ENTITY_LINKING_CONFIDENCE_THRESHOLD: float = float(os.environ.get("ENTITY_LINKING_CONFIDENCE_THRESHOLD", "0.7"))
    MAX_ENTITY_RELATIONSHIPS: int = int(os.environ.get("MAX_ENTITY_RELATIONSHIPS", "10"))
    CONTEXTUAL_DISAMBIGUATION: bool = os.environ.get("CONTEXTUAL_DISAMBIGUATION", "true").lower() == "true"


def load_config() -> GraphRAGConfig:
    """Load configuration from environment variables."""
    return GraphRAGConfig()


# Global config instance
config = load_config()