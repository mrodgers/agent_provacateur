"""
Tests for the enhanced entity linking functionality.
"""

import os
import sys
import unittest
from typing import Dict, List

import pytest

# Add parent directory to path for relative imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import config
from src.entity_linking import (
    EntityLinker,
    LocalKnowledgeBase,
    WikidataKnowledgeBase,
    get_entity_linker
)
from src.graphrag import Entity, EntityType, Relationship, RelationType


class TestEntityLinker(unittest.TestCase):
    """Tests for the entity linker."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use a temporary knowledge base for testing
        config.LOCAL_KB_PATH = "./data/test_knowledge_base.json"
        config.WIKIDATA_CACHE_PATH = "./data/test_wikidata_cache.json"
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(config.LOCAL_KB_PATH), exist_ok=True)
        
        # Create a fresh entity linker for each test
        self.entity_linker = EntityLinker()
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove test files
        try:
            if os.path.exists(config.LOCAL_KB_PATH):
                os.remove(config.LOCAL_KB_PATH)
            if os.path.exists(config.WIKIDATA_CACHE_PATH):
                os.remove(config.WIKIDATA_CACHE_PATH)
        except:
            pass
    
    def test_extract_candidates(self):
        """Test extraction of candidate entities."""
        text = "The United Nations has been working with the European Union on climate change initiatives."
        candidates = self.entity_linker._extract_candidates(text)
        
        # Check that we extracted at least United Nations and European Union
        extracted_names = [candidate[0].lower() for candidate in candidates]
        self.assertIn("united nations", [name.lower() for name in extracted_names])
        self.assertIn("european union", [name.lower() for name in extracted_names])
        self.assertIn("climate change", [name.lower() for name in extracted_names])
    
    def test_entity_type_determination(self):
        """Test determination of entity types from context."""
        # Test for person
        text = "Dr. Jane Smith is a renowned scientist who works at the University of Technology."
        
        # Find position of Jane Smith
        start = text.find("Jane Smith")
        end = start + len("Jane Smith")
        
        entity_type = self.entity_linker._determine_entity_type_from_context(text, start, end)
        self.assertEqual(entity_type, EntityType.PERSON)
        
        # Test for organization
        text = "Microsoft Corporation is headquartered in Redmond, Washington."
        
        # Find position of Microsoft Corporation
        start = text.find("Microsoft Corporation")
        end = start + len("Microsoft Corporation")
        
        entity_type = self.entity_linker._determine_entity_type_from_context(text, start, end)
        self.assertEqual(entity_type, EntityType.ORGANIZATION)
    
    def test_relationship_determination(self):
        """Test determination of relationship types."""
        # Test for LOCATED_IN relationship
        text = "Google is headquartered in Mountain View, California."
        
        entity1 = Entity(name="Google", entity_type=EntityType.ORGANIZATION)
        entity2 = Entity(name="Mountain View", entity_type=EntityType.LOCATION)
        
        rel_type = self.entity_linker._determine_relationship_type(entity1, entity2, text)
        self.assertEqual(rel_type, RelationType.LOCATED_IN)
        
        # Test for CREATED_BY relationship
        text = "Tim Berners-Lee created the World Wide Web."
        
        entity1 = Entity(name="Tim Berners-Lee", entity_type=EntityType.PERSON)
        entity2 = Entity(name="World Wide Web", entity_type=EntityType.CONCEPT)
        
        rel_type = self.entity_linker._determine_relationship_type(entity1, entity2, text)
        self.assertEqual(rel_type, RelationType.CREATED_BY)
    
    def test_local_knowledge_base(self):
        """Test the local knowledge base functionality."""
        kb = LocalKnowledgeBase(data_path=config.LOCAL_KB_PATH)
        
        # Add test entity
        entity = Entity(
            name="Artificial Intelligence",
            entity_type=EntityType.CONCEPT,
            description="The simulation of human intelligence in machines",
            aliases=["AI", "Machine Learning"]
        )
        
        kb.add_entity(entity)
        
        # Look up by name
        result = kb.lookup_entity("Artificial Intelligence")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Artificial Intelligence")
        
        # Look up by alias
        result = kb.lookup_entity("AI")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Artificial Intelligence")
        
        # Test semantic matching (with a related term)
        result = kb.lookup_entity("Machine Intelligence")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Artificial Intelligence")
    
    @pytest.mark.skipif(not config.USE_WIKIDATA_KB, reason="Wikidata KB tests are skipped unless USE_WIKIDATA_KB is true")
    def test_wikidata_knowledge_base(self):
        """Test the Wikidata knowledge base functionality."""
        try:
            import requests
        except ImportError:
            pytest.skip("requests library not installed, skipping Wikidata test")
        
        kb = WikidataKnowledgeBase(cache_path=config.WIKIDATA_CACHE_PATH)
        
        # Create a fake entity for testing without network
        fake_entity = {
            "entity_id": "wikidata_Q937",
            "name": "Albert Einstein",
            "entity_type": "person",
            "description": "Theoretical physicist known for developing the theory of relativity",
            "aliases": ["Einstein"],
            "metadata": {
                "wikidata_id": "Q937",
                "source": "wikidata"
            }
        }
        
        # Manually add to cache to avoid network requests
        kb.cache[f"entity:albert einstein"] = fake_entity
        kb._save_cache()
        
        # Look up the entity from cache
        result = kb.lookup_entity("Albert Einstein")
        
        # Now test the cached result
        self.assertEqual(result["name"], "Albert Einstein")
        self.assertEqual(result["entity_type"], "person")
        self.assertTrue("physicist" in result.get("description", "").lower())
    
    def test_full_entity_extraction(self):
        """Test the full entity extraction pipeline."""
        text = """
        The Paris Agreement is an international treaty on climate change, adopted in 2015.
        It was negotiated by the United Nations Framework Convention on Climate Change (UNFCCC).
        Countries like the United States, China, and members of the European Union have committed
        to reducing greenhouse gas emissions to combat global warming.
        """
        
        entities = self.entity_linker.extract_entities(text)
        
        # Check that we extracted key entities
        entity_names = [entity.name.lower() for entity in entities]
        
        self.assertIn("paris agreement", [name.lower() for name in entity_names])
        self.assertIn("climate change", [name.lower() for name in entity_names])
        self.assertIn("united nations", [name.lower() for name in entity_names])
        self.assertIn("united states", [name.lower() for name in entity_names])
        self.assertIn("european union", [name.lower() for name in entity_names])
        self.assertIn("global warming", [name.lower() for name in entity_names])
        
        # Check that we have correct entity types
        entity_map = {entity.name.lower(): entity for entity in entities}
        
        if "paris agreement" in entity_map:
            self.assertEqual(entity_map["paris agreement"].entity_type, EntityType.CONCEPT)
        
        if "united nations" in entity_map:
            self.assertEqual(entity_map["united nations"].entity_type, EntityType.ORGANIZATION)
        
        if "united states" in entity_map:
            self.assertEqual(entity_map["united states"].entity_type, EntityType.LOCATION)
    
    def test_relationship_creation(self):
        """Test the relationship creation between entities."""
        text = """
        The Paris Agreement was negotiated by the United Nations.
        The United States, under President Joe Biden, rejoined the Paris Agreement in 2021.
        """
        
        entities = self.entity_linker.extract_entities(text)
        relationships = self.entity_linker._create_relationships(entities, text)
        
        # Check that we have created relationships
        self.assertGreater(len(relationships), 0)
        
        # Map entities by ID for relationship verification
        entity_map = {entity.entity_id: entity for entity in entities}
        
        # Check for specific relationships
        for rel in relationships:
            source = entity_map.get(rel.source_entity_id)
            target = entity_map.get(rel.target_entity_id)
            
            if source and target:
                if source.name == "United Nations" and target.name == "Paris Agreement":
                    self.assertEqual(rel.relation_type, RelationType.CREATED_BY)
                
                if source.name == "United States" and target.name == "Paris Agreement":
                    # This could be RELATED_TO or another appropriate type
                    self.assertIn(rel.relation_type, [RelationType.RELATED_TO, RelationType.PART_OF])
    
    def test_entity_disambiguation(self):
        """Test entity disambiguation."""
        # Create entities with the same name but different contexts
        entity1 = Entity(
            name="Paris",
            entity_type=EntityType.LOCATION,
            description="Capital city of France"
        )
        
        entity2 = Entity(
            name="Paris",
            entity_type=EntityType.PERSON,
            description="Character in Greek mythology"
        )
        
        # Text about Paris, France
        text = "Paris is the capital and most populous city of France. The Eiffel Tower is located in Paris."
        
        # Disambiguate entities
        entities = [entity1, entity2]
        disambiguated = self.entity_linker.disambiguate_entities(entities, text)
        
        # Check that the right entity was selected
        self.assertEqual(len(disambiguated), 2)
        
        # Since entity1 is about Paris the city, it should have a higher score in this context
        self.assertTrue(
            disambiguated[0].metadata.get("disambiguation_score", 0) > 
            disambiguated[1].metadata.get("disambiguation_score", 0) 
            if disambiguated[0].entity_type == EntityType.LOCATION 
            else disambiguated[1].metadata.get("disambiguation_score", 0) > 
            disambiguated[0].metadata.get("disambiguation_score", 0)
        )


if __name__ == "__main__":
    unittest.main()