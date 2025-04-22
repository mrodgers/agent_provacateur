"""
Vector database implementations for GraphRAG.
"""

import json
import os
import pickle
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from .config import config
from .utils import logger, timed_execution


class VectorDocument:
    """Document with vector embedding."""
    
    def __init__(
        self,
        content: str,
        metadata: Dict[str, Any],
        embedding: Optional[np.ndarray] = None,
        doc_id: Optional[str] = None
    ):
        self.doc_id = doc_id or f"doc_{uuid.uuid4().hex[:8]}"
        self.content = content
        self.metadata = metadata
        self.embedding = embedding
        self.entities: List[Dict[str, Any]] = []
        self.relationships: List[Dict[str, Any]] = []
    
    def add_entity(self, entity_id: str, entity_type: str, positions: List[Tuple[int, int]]) -> None:
        """Add an entity to the document."""
        self.entities.append({
            "entity_id": entity_id,
            "entity_type": entity_type,
            "positions": positions
        })
    
    def add_relationship(self, source_id: str, target_id: str, relation_type: str) -> None:
        """Add a relationship to the document."""
        self.relationships.append({
            "source_entity_id": source_id,
            "target_entity_id": target_id,
            "relation_type": relation_type
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "metadata": self.metadata,
            # Don't include embedding in the dict version
            "entities": self.entities,
            "relationships": self.relationships
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], embedding: Optional[np.ndarray] = None) -> 'VectorDocument':
        """Create from dictionary."""
        doc = cls(
            content=data["content"],
            metadata=data["metadata"],
            embedding=embedding,
            doc_id=data["doc_id"]
        )
        doc.entities = data.get("entities", [])
        doc.relationships = data.get("relationships", [])
        return doc


class VectorDB(ABC):
    """Abstract base class for vector databases."""
    
    @abstractmethod
    def add_document(self, document: VectorDocument) -> str:
        """Add a document to the vector DB."""
        pass
    
    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """Get a document by ID."""
        pass
    
    @abstractmethod
    def search(self, query_vector: np.ndarray, limit: int = 10, min_score: float = 0.5) -> List[Tuple[str, float]]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    def search_by_entity(self, entity_ids: List[str], limit: int = 10) -> List[Tuple[str, float]]:
        """Search for documents containing specific entities."""
        pass
    
    @abstractmethod
    def save(self) -> None:
        """Save the vector database to disk."""
        pass
    
    @abstractmethod
    def load(self) -> None:
        """Load the vector database from disk."""
        pass


class FAISSVectorDB(VectorDB):
    """FAISS implementation of vector database."""
    
    def __init__(self, dimension: int = config.VECTOR_DIMENSION, index_path: str = config.VECTOR_DB_PATH):
        self.dimension = dimension
        self.index_path = index_path
        self.documents: Dict[str, VectorDocument] = {}
        self.document_ids: List[str] = []
        
        # Create base directory if it doesn't exist
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        # Create the FAISS index
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity if vectors are normalized)
        
        # Try to load existing index
        try:
            self.load()
        except (FileNotFoundError, EOFError):
            logger.info(f"No existing index found at {index_path}, creating new one")
        
        # Initialize the embedding model
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        logger.info(f"Initialized FAISS vector DB with dimension {dimension}")
    
    def _encode_text(self, text: str) -> np.ndarray:
        """Encode text to vector using the embedding model."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding
    
    @timed_execution
    def add_document(self, document: VectorDocument) -> str:
        """Add a document to the vector DB."""
        # Generate embedding if not already present
        if document.embedding is None:
            document.embedding = self._encode_text(document.content)
        
        # Add to FAISS index
        if len(self.document_ids) == 0:
            # First document, add directly
            self.index.add(np.array([document.embedding], dtype=np.float32))
        else:
            # Add to existing index
            self.index.add(np.array([document.embedding], dtype=np.float32))
        
        # Store the document
        self.documents[document.doc_id] = document
        self.document_ids.append(document.doc_id)
        
        # Save after each addition
        self.save()
        
        logger.info(f"Added document {document.doc_id} to vector DB")
        return document.doc_id
    
    def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """Get a document by ID."""
        return self.documents.get(doc_id)
    
    @timed_execution
    def search(self, query_vector: Union[np.ndarray, str], limit: int = 10, min_score: float = 0.5) -> List[Tuple[str, float]]:
        """Search for similar documents."""
        # Handle string input by encoding it
        if isinstance(query_vector, str):
            query_vector = self._encode_text(query_vector)
        
        # Ensure the query vector is correctly shaped
        if len(query_vector.shape) == 1:
            query_vector = np.array([query_vector], dtype=np.float32)
        
        # Return empty list if no documents
        if len(self.document_ids) == 0:
            return []
        
        # Search in the index
        scores, indices = self.index.search(query_vector, min(limit, len(self.document_ids)))
        
        # Map indices to document IDs and filter by minimum score
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.document_ids) and 0 <= idx < len(self.document_ids):
                score = float(scores[0][i])
                if score >= min_score:
                    doc_id = self.document_ids[idx]
                    results.append((doc_id, score))
        
        logger.debug(f"Search returned {len(results)} results")
        return results
    
    @timed_execution
    def search_by_entity(self, entity_ids: List[str], limit: int = 10) -> List[Tuple[str, float]]:
        """Search for documents containing specific entities."""
        results = []
        
        for doc_id, doc in self.documents.items():
            # Check if document contains any of the target entities
            doc_entity_ids = [entity["entity_id"] for entity in doc.entities]
            matched_entities = [eid for eid in entity_ids if eid in doc_entity_ids]
            
            if matched_entities:
                # Calculate score based on number of matched entities
                score = min(0.95, 0.7 + (len(matched_entities) / len(entity_ids)) * 0.25)
                results.append((doc_id, score))
        
        # Sort by score and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
    
    def save(self) -> None:
        """Save the vector database to disk."""
        # Save FAISS index
        faiss.write_index(self.index, f"{self.index_path}.faiss")
        
        # Save document mappings (without embeddings)
        docs_to_save = {
            doc_id: doc.to_dict() for doc_id, doc in self.documents.items()
        }
        with open(f"{self.index_path}.json", "w") as f:
            json.dump({
                "document_ids": self.document_ids,
                "documents": docs_to_save
            }, f)
        
        logger.debug(f"Saved vector DB to {self.index_path}")
    
    def load(self) -> None:
        """Load the vector database from disk."""
        # Load FAISS index
        if os.path.exists(f"{self.index_path}.faiss"):
            self.index = faiss.read_index(f"{self.index_path}.faiss")
            
            # Load document mappings
            if os.path.exists(f"{self.index_path}.json"):
                with open(f"{self.index_path}.json", "r") as f:
                    data = json.load(f)
                    self.document_ids = data["document_ids"]
                    
                    # Create document objects
                    for doc_id, doc_dict in data["documents"].items():
                        self.documents[doc_id] = VectorDocument.from_dict(doc_dict)
                    
                logger.info(f"Loaded vector DB with {len(self.documents)} documents")
            else:
                raise FileNotFoundError(f"Document mappings not found at {self.index_path}.json")
        else:
            raise FileNotFoundError(f"FAISS index not found at {self.index_path}.faiss")


def get_vector_db() -> VectorDB:
    """Factory function to get the appropriate vector DB implementation."""
    vector_db_type = config.VECTOR_DB_TYPE.lower()
    
    if vector_db_type == "faiss":
        return FAISSVectorDB()
    else:
        logger.warning(f"Unsupported vector DB type '{vector_db_type}', falling back to FAISS")
        return FAISSVectorDB()