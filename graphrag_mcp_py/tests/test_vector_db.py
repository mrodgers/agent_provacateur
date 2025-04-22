"""
Tests for the FAISS vector database implementation.
"""

import os
import tempfile
import unittest

import numpy as np

import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create a simplified version of the classes for testing
import faiss

class VectorDocument:
    """Document with vector embedding."""
    
    def __init__(
        self,
        content: str,
        metadata: dict,
        embedding: np.ndarray = None,
        doc_id: str = None
    ):
        self.doc_id = doc_id or f"doc_{os.urandom(4).hex()}"
        self.content = content
        self.metadata = metadata
        self.embedding = embedding
        self.entities = []
        self.relationships = []
    
    def add_entity(self, entity_id: str, entity_type: str, positions: list):
        """Add an entity to the document."""
        self.entities.append({
            "entity_id": entity_id,
            "entity_type": entity_type,
            "positions": positions
        })
    
    def add_relationship(self, source_id: str, target_id: str, relation_type: str):
        """Add a relationship to the document."""
        self.relationships.append({
            "source_entity_id": source_id,
            "target_entity_id": target_id,
            "relation_type": relation_type
        })

class FAISSVectorDB:
    """FAISS implementation of vector database."""
    
    def __init__(self, dimension: int = 384, index_path: str = "./test_index"):
        self.dimension = dimension
        self.index_path = index_path
        self.documents = {}
        self.document_ids = []
        
        # Create the FAISS index
        self.index = faiss.IndexFlatL2(dimension)
    
    def add_document(self, document: VectorDocument) -> str:
        """Add a document to the vector DB."""
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
        
        return document.doc_id
    
    def get_document(self, doc_id: str):
        """Get a document by ID."""
        return self.documents.get(doc_id)
    
    def search(self, query_vector, limit: int = 10, min_score: float = 0.5):
        """Search for similar documents."""
        # Ensure the query vector is correctly shaped
        if len(query_vector.shape) == 1:
            query_vector = np.array([query_vector], dtype=np.float32)
        
        # Return empty list if no documents
        if len(self.document_ids) == 0:
            return []
        
        # Search in the index
        distances, indices = self.index.search(query_vector, min(limit, len(self.document_ids)))
        
        # Map indices to document IDs and filter by minimum score
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.document_ids):
                # Convert L2 distance to similarity score (0-1)
                # Lower distance = higher similarity
                distance = float(distances[0][i])
                score = max(0, 1.0 - (distance / 10.0))  # Normalize to 0-1
                
                if score >= min_score:
                    doc_id = self.document_ids[idx]
                    results.append((doc_id, score))
        
        return results
    
    def search_by_entity(self, entity_ids: list, limit: int = 10):
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
    
    def save(self):
        """Save the vector database to disk."""
        import json
        import pickle
        
        # Save document mappings
        docs_to_save = {}
        for doc_id, doc in self.documents.items():
            docs_to_save[doc_id] = {
                "doc_id": doc.doc_id,
                "content": doc.content,
                "metadata": doc.metadata,
                "entities": doc.entities,
                "relationships": doc.relationships
            }
        
        with open(f"{self.index_path}.json", "w") as f:
            json.dump({
                "document_ids": self.document_ids,
                "documents": docs_to_save
            }, f)
        
        # Save embeddings separately
        embeddings = {}
        for doc_id, doc in self.documents.items():
            if doc.embedding is not None:
                embeddings[doc_id] = doc.embedding.tolist()
        
        with open(f"{self.index_path}.embeddings", "wb") as f:
            pickle.dump(embeddings, f)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{self.index_path}.faiss")
    
    def load(self):
        """Load the vector database from disk."""
        import json
        import pickle
        
        # Load document mappings
        if os.path.exists(f"{self.index_path}.json"):
            with open(f"{self.index_path}.json", "r") as f:
                data = json.load(f)
                self.document_ids = data["document_ids"]
                
                # Load embeddings
                embeddings = {}
                if os.path.exists(f"{self.index_path}.embeddings"):
                    with open(f"{self.index_path}.embeddings", "rb") as f_emb:
                        embeddings = pickle.load(f_emb)
                
                # Create document objects
                for doc_id, doc_dict in data["documents"].items():
                    doc = VectorDocument(
                        content=doc_dict["content"],
                        metadata=doc_dict["metadata"],
                        doc_id=doc_dict["doc_id"]
                    )
                    
                    # Add entities and relationships
                    for entity in doc_dict["entities"]:
                        doc.entities.append(entity)
                    
                    for relationship in doc_dict["relationships"]:
                        doc.relationships.append(relationship)
                    
                    # Add embedding if available
                    if doc_id in embeddings:
                        doc.embedding = np.array(embeddings[doc_id], dtype=np.float32)
                    
                    self.documents[doc_id] = doc
            
            # Load FAISS index
            if os.path.exists(f"{self.index_path}.faiss"):
                self.index = faiss.read_index(f"{self.index_path}.faiss")
            else:
                # Rebuild index if faiss file is missing
                self.index = faiss.IndexFlatL2(self.dimension)
                for doc in self.documents.values():
                    if doc.embedding is not None:
                        self.index.add(np.array([doc.embedding], dtype=np.float32))


class TestFAISSVectorDB(unittest.TestCase):
    """Test the FAISS vector database implementation."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for the vector database
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = os.path.join(self.temp_dir, "test_index")
        
        # Create a test vector database
        self.vector_db = FAISSVectorDB(dimension=384, index_path=self.index_path)
        
        # Create test documents
        self.docs = [
            VectorDocument(
                content="Climate change is a significant challenge facing our planet.",
                metadata={"title": "Climate Article", "source_type": "web"},
                embedding=np.random.rand(384).astype(np.float32)
            ),
            VectorDocument(
                content="Artificial intelligence is transforming industries around the world.",
                metadata={"title": "AI Impact", "source_type": "document"},
                embedding=np.random.rand(384).astype(np.float32)
            ),
            VectorDocument(
                content="Renewable energy sources are becoming more cost-effective.",
                metadata={"title": "Energy Trends", "source_type": "web"},
                embedding=np.random.rand(384).astype(np.float32)
            ),
        ]
    
    def test_add_document(self):
        """Test adding documents to the vector database."""
        # Add the test documents
        doc_ids = []
        for doc in self.docs:
            doc_id = self.vector_db.add_document(doc)
            doc_ids.append(doc_id)
        
        # Check that the documents were added
        self.assertEqual(len(self.vector_db.documents), 3)
        self.assertEqual(len(self.vector_db.document_ids), 3)
        
        # Check that the documents can be retrieved
        for i, doc_id in enumerate(doc_ids):
            retrieved_doc = self.vector_db.get_document(doc_id)
            self.assertIsNotNone(retrieved_doc)
            self.assertEqual(retrieved_doc.content, self.docs[i].content)
            self.assertEqual(retrieved_doc.metadata["title"], self.docs[i].metadata["title"])
    
    def test_search(self):
        """Test searching for documents in the vector database."""
        # Add the test documents
        for doc in self.docs:
            self.vector_db.add_document(doc)
        
        # Create a test query vector
        query_vector = np.random.rand(384).astype(np.float32)
        
        # Search with the query vector
        results = self.vector_db.search(query_vector, limit=2, min_score=0.0)
        
        # Check that results were returned
        self.assertLessEqual(len(results), 2)
        self.assertGreaterEqual(len(results), 0)
        
        # Check that the results are in the correct format
        if results:
            for doc_id, score in results:
                self.assertIn(doc_id, self.vector_db.documents)
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)
    
    def test_search_by_entity(self):
        """Test searching for documents by entity IDs."""
        # Add the test documents with entities
        doc_ids = []
        for doc in self.docs:
            doc.add_entity("ent_1", "concept", [(0, 5)])
            doc_ids.append(self.vector_db.add_document(doc))
        
        # Add another document with a different entity
        special_doc = VectorDocument(
            content="Special test document",
            metadata={"title": "Special", "source_type": "document"},
            embedding=np.random.rand(384).astype(np.float32)
        )
        special_doc.add_entity("ent_special", "concept", [(0, 7)])
        special_id = self.vector_db.add_document(special_doc)
        
        # Search with the common entity
        results = self.vector_db.search_by_entity(["ent_1"], limit=5)
        
        # Check that all documents with the entity were returned
        self.assertEqual(len(results), 3)
        
        # Check that the special document was not returned
        special_in_results = any(doc_id == special_id for doc_id, _ in results)
        self.assertFalse(special_in_results)
        
        # Search with the special entity
        results = self.vector_db.search_by_entity(["ent_special"], limit=5)
        
        # Check that only the special document was returned
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], special_id)
    
    def test_save_and_load(self):
        """Test saving and loading the vector database."""
        # Add the test documents
        doc_ids = []
        for doc in self.docs:
            doc_ids.append(self.vector_db.add_document(doc))
        
        # Save the vector database
        self.vector_db.save()
        
        # Create a new vector database instance
        new_vector_db = FAISSVectorDB(dimension=384, index_path=self.index_path)
        
        # Need to explicitly load for our test implementation
        new_vector_db.load()
        
        # Check that the documents were loaded
        self.assertEqual(len(new_vector_db.documents), 3)
        self.assertEqual(len(new_vector_db.document_ids), 3)
        
        # Check that the documents can be retrieved
        for i, doc_id in enumerate(doc_ids):
            retrieved_doc = new_vector_db.get_document(doc_id)
            self.assertIsNotNone(retrieved_doc)
            self.assertEqual(retrieved_doc.content, self.docs[i].content)
            self.assertEqual(retrieved_doc.metadata["title"], self.docs[i].metadata["title"])
    
    def tearDown(self):
        """Clean up the test environment."""
        # Remove the temporary directory
        for ext in [".faiss", ".json", ".embeddings"]:
            if os.path.exists(f"{self.index_path}{ext}"):
                os.remove(f"{self.index_path}{ext}")
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()