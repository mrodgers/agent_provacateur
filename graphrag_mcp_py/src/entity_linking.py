"""
Enhanced entity linking capabilities for GraphRAG MCP server.

This module provides advanced entity extraction and linking capabilities,
including integration with external knowledge bases and contextual disambiguation.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import requests
from sentence_transformers import SentenceTransformer, util

from .config import config
from .graphrag import Entity, EntityType, Relationship, RelationType
from .utils import logger, timed_execution


class KnowledgeBase:
    """Interface for external knowledge bases."""
    
    def lookup_entity(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Look up entity in the knowledge base."""
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_related_entities(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get entities related to the given entity."""
        raise NotImplementedError("Subclasses must implement this method")


class LocalKnowledgeBase(KnowledgeBase):
    """Simple local knowledge base implementation."""
    
    def __init__(self, data_path: str = "./data/knowledge_base.json"):
        self.data_path = data_path
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.entity_names: Dict[str, str] = {}  # Maps lowercase names to entity IDs
        self.entity_embeddings: Dict[str, np.ndarray] = {}
        self.relationships: Dict[str, List[Dict[str, Any]]] = {}
        
        # Load model for semantic matching
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        
        # Try to load existing knowledge base
        try:
            self.load()
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info(f"No existing knowledge base found at {data_path}, creating new one")
            self._create_default_knowledge_base()
    
    def _create_default_knowledge_base(self) -> None:
        """Create a default knowledge base with basic entities."""
        # Add some common entities
        entities = [
            {
                "name": "Climate Change",
                "entity_type": "concept",
                "description": "Long-term change in Earth's climate patterns",
                "aliases": ["global warming", "climate crisis", "climate emergency"],
                "metadata": {
                    "importance": "high",
                    "fields": ["environmental science", "politics", "economics"]
                }
            },
            {
                "name": "Artificial Intelligence",
                "entity_type": "concept",
                "description": "Simulation of human intelligence in machines",
                "aliases": ["AI", "machine learning", "deep learning"],
                "metadata": {
                    "importance": "high",
                    "fields": ["computer science", "robotics", "ethics"]
                }
            },
            {
                "name": "United Nations",
                "entity_type": "organization",
                "description": "Intergovernmental organization aiming to maintain peace",
                "aliases": ["UN"],
                "metadata": {
                    "founded": "1945",
                    "headquarters": "New York City"
                }
            },
            {
                "name": "Paris Agreement",
                "entity_type": "concept",
                "description": "International treaty on climate change mitigation",
                "aliases": ["Paris Climate Agreement", "Paris Climate Accord"],
                "metadata": {
                    "established": "2015",
                    "related_to": ["Climate Change", "United Nations"]
                }
            }
        ]
        
        # Add entities to knowledge base
        entity_ids = []
        for entity_data in entities:
            entity = Entity(
                name=entity_data["name"],
                entity_type=entity_data["entity_type"],
                description=entity_data.get("description"),
                aliases=entity_data.get("aliases", []),
                metadata=entity_data.get("metadata", {})
            )
            self.entities[entity.entity_id] = entity.to_dict()
            self.entity_names[entity.name.lower()] = entity.entity_id
            for alias in entity.aliases:
                self.entity_names[alias.lower()] = entity.entity_id
            
            # Create embedding
            self.entity_embeddings[entity.entity_id] = self.model.encode(
                entity.name + ". " + (entity.description or ""),
                normalize_embeddings=True
            )
            
            entity_ids.append(entity.entity_id)
        
        # Add some relationships
        relations = [
            {
                "source": "Climate Change",
                "target": "Paris Agreement",
                "relation_type": "related_to",
                "confidence": 0.95
            },
            {
                "source": "United Nations",
                "target": "Paris Agreement",
                "relation_type": "created_by",
                "confidence": 0.9
            },
            {
                "source": "Artificial Intelligence",
                "target": "Climate Change",
                "relation_type": "related_to",
                "confidence": 0.7,
                "metadata": {
                    "explanation": "AI is used to model climate change impacts"
                }
            }
        ]
        
        # Add relationships to knowledge base
        for rel_data in relations:
            source_id = self.entity_names.get(rel_data["source"].lower())
            target_id = self.entity_names.get(rel_data["target"].lower())
            
            if source_id and target_id:
                relationship = Relationship(
                    source_entity_id=source_id,
                    target_entity_id=target_id,
                    relation_type=rel_data["relation_type"],
                    confidence=rel_data.get("confidence", 0.8),
                    metadata=rel_data.get("metadata", {})
                )
                
                # Add to relationships map
                if source_id not in self.relationships:
                    self.relationships[source_id] = []
                self.relationships[source_id].append(relationship.to_dict())
        
        # Save the new knowledge base
        self.save()
    
    def lookup_entity(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Look up entity in the knowledge base by name."""
        # Direct lookup by name
        entity_id = self.entity_names.get(entity_name.lower())
        if entity_id:
            return self.entities.get(entity_id)
        
        # If not found directly, try semantic matching
        query_embedding = self.model.encode(entity_name, normalize_embeddings=True)
        best_match = None
        best_score = 0.0
        
        for entity_id, embedding in self.entity_embeddings.items():
            score = float(util.dot_score(query_embedding, embedding)[0][0])
            if score > best_score and score > 0.75:  # Threshold for semantic matching
                best_match = entity_id
                best_score = score
        
        if best_match:
            return self.entities.get(best_match)
        
        return None
    
    def get_related_entities(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get entities related to the given entity."""
        related_entities = []
        
        # Check if entity exists and has relationships
        if entity_id not in self.entities:
            return []
        
        # Get outgoing relationships
        for relationship in self.relationships.get(entity_id, []):
            target_entity_id = relationship["target_entity_id"]
            target_entity = self.entities.get(target_entity_id)
            if target_entity:
                related_entities.append({
                    "entity": target_entity,
                    "relationship": relationship,
                    "direction": "outgoing"
                })
        
        # Get incoming relationships
        for source_id, relationships in self.relationships.items():
            for relationship in relationships:
                if relationship["target_entity_id"] == entity_id:
                    source_entity = self.entities.get(source_id)
                    if source_entity:
                        related_entities.append({
                            "entity": source_entity,
                            "relationship": relationship,
                            "direction": "incoming"
                        })
        
        return related_entities
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the knowledge base."""
        # Add to entities dictionary
        self.entities[entity.entity_id] = entity.to_dict()
        self.entity_names[entity.name.lower()] = entity.entity_id
        
        # Add aliases
        for alias in entity.aliases:
            self.entity_names[alias.lower()] = entity.entity_id
        
        # Create and store embedding
        self.entity_embeddings[entity.entity_id] = self.model.encode(
            entity.name + ". " + (entity.description or ""),
            normalize_embeddings=True
        )
        
        # Save the updated knowledge base
        self.save()
    
    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the knowledge base."""
        # Check if source entity exists
        if relationship.source_entity_id not in self.entities:
            return
        
        # Ensure source entity has a relationships entry
        if relationship.source_entity_id not in self.relationships:
            self.relationships[relationship.source_entity_id] = []
        
        # Add relationship
        self.relationships[relationship.source_entity_id].append(relationship.to_dict())
        
        # Save the updated knowledge base
        self.save()
    
    def save(self) -> None:
        """Save the knowledge base to disk."""
        data = {
            "entities": self.entities,
            "relationships": self.relationships
        }
        with open(self.data_path, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.debug(f"Saved knowledge base to {self.data_path}")
    
    def load(self) -> None:
        """Load the knowledge base from disk."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Knowledge base file not found at {self.data_path}")
        
        with open(self.data_path, "r") as f:
            data = json.load(f)
        
        self.entities = data.get("entities", {})
        self.relationships = data.get("relationships", {})
        
        # Rebuild entity name mapping
        self.entity_names = {}
        for entity_id, entity in self.entities.items():
            self.entity_names[entity["name"].lower()] = entity_id
            for alias in entity.get("aliases", []):
                self.entity_names[alias.lower()] = entity_id
        
        # Build entity embeddings
        self.entity_embeddings = {}
        for entity_id, entity in self.entities.items():
            self.entity_embeddings[entity_id] = self.model.encode(
                entity["name"] + ". " + (entity.get("description") or ""),
                normalize_embeddings=True
            )
        
        logger.info(f"Loaded knowledge base with {len(self.entities)} entities and {sum(len(rels) for rels in self.relationships.values())} relationships")


class WikidataKnowledgeBase(KnowledgeBase):
    """Wikidata knowledge base implementation."""
    
    def __init__(self, cache_path: str = "./data/wikidata_cache.json"):
        self.cache_path = cache_path
        self.cache: Dict[str, Dict[str, Any]] = {}
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        
        # Try to load existing cache
        try:
            with open(cache_path, "r") as f:
                self.cache = json.load(f)
            logger.info(f"Loaded Wikidata cache with {len(self.cache)} entries")
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info(f"No existing Wikidata cache found at {cache_path}, creating new one")
            self.cache = {}
    
    def _save_cache(self) -> None:
        """Save the cache to disk."""
        with open(self.cache_path, "w") as f:
            json.dump(self.cache, f, indent=2)
        
        logger.debug(f"Saved Wikidata cache to {self.cache_path}")
    
    def lookup_entity(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """Look up entity in Wikidata."""
        # Check cache first
        cache_key = f"entity:{entity_name.lower()}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Perform SPARQL query to Wikidata
        try:
            # Use the Wikidata SPARQL endpoint
            url = "https://query.wikidata.org/sparql"
            headers = {
                "User-Agent": "GraphRAG Entity Linking/1.0",
                "Accept": "application/json"
            }
            
            # Query for entity by label
            query = f"""
            SELECT ?item ?itemLabel ?itemDescription ?itemAltLabel WHERE {{
              ?item rdfs:label "{entity_name}"@en.
              SERVICE wikibase:label {{ 
                bd:serviceParam wikibase:language "en". 
                ?item rdfs:label ?itemLabel.
                ?item schema:description ?itemDescription.
                OPTIONAL {{ ?item skos:altLabel ?itemAltLabel. FILTER(LANG(?itemAltLabel) = "en") }}
              }}
            }}
            LIMIT 1
            """
            
            # Make the request
            response = requests.get(
                url,
                headers=headers,
                params={"query": query, "format": "json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                bindings = data.get("results", {}).get("bindings", [])
                
                if bindings:
                    result = bindings[0]
                    entity_id = result["item"]["value"].split("/")[-1]
                    entity_data = {
                        "entity_id": f"wikidata_{entity_id}",
                        "name": result["itemLabel"]["value"],
                        "entity_type": self._determine_entity_type(result),
                        "description": result.get("itemDescription", {}).get("value", ""),
                        "aliases": [alt["value"] for alt in bindings if "itemAltLabel" in alt],
                        "metadata": {
                            "wikidata_id": entity_id,
                            "wikidata_url": result["item"]["value"]
                        }
                    }
                    
                    # Cache the result
                    self.cache[cache_key] = entity_data
                    self._save_cache()
                    
                    return entity_data
            
            # No entity found or error
            self.cache[cache_key] = None
            self._save_cache()
            return None
            
        except Exception as e:
            logger.error(f"Error querying Wikidata: {e}")
            return None
    
    def _determine_entity_type(self, wikidata_result: Dict[str, Any]) -> str:
        """Determine entity type from Wikidata result."""
        # This is a simplistic approach that could be improved
        description = wikidata_result.get("itemDescription", {}).get("value", "").lower()
        
        if any(term in description for term in ["person", "politician", "actor", "writer", "scientist"]):
            return "person"
        elif any(term in description for term in ["company", "organization", "organisation", "agency", "institution"]):
            return "organization"
        elif any(term in description for term in ["city", "country", "region", "place", "town", "village"]):
            return "location"
        elif any(term in description for term in ["concept", "theory", "idea", "principle"]):
            return "concept"
        elif any(term in description for term in ["product", "device", "tool", "application", "software"]):
            return "product"
        elif any(term in description for term in ["event", "incident", "occurrence", "happening"]):
            return "event"
        else:
            return "other"
    
    def get_related_entities(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get entities related to the given entity in Wikidata."""
        # Only process Wikidata entities
        if not entity_id.startswith("wikidata_"):
            return []
        
        # Check cache first
        cache_key = f"related:{entity_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        wikidata_id = entity_id[9:]  # Remove "wikidata_" prefix
        
        try:
            # Use the Wikidata SPARQL endpoint
            url = "https://query.wikidata.org/sparql"
            headers = {
                "User-Agent": "GraphRAG Entity Linking/1.0",
                "Accept": "application/json"
            }
            
            # Query for related entities
            query = f"""
            SELECT ?property ?propertyLabel ?item ?itemLabel ?itemDescription WHERE {{
              wd:{wikidata_id} ?p ?item.
              ?property wikibase:directClaim ?p.
              FILTER(STRSTARTS(STR(?item), "http://www.wikidata.org/entity/"))
              SERVICE wikibase:label {{ 
                bd:serviceParam wikibase:language "en". 
                ?property rdfs:label ?propertyLabel.
                ?item rdfs:label ?itemLabel.
                ?item schema:description ?itemDescription.
              }}
            }}
            LIMIT 10
            """
            
            # Make the request
            response = requests.get(
                url,
                headers=headers,
                params={"query": query, "format": "json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                bindings = data.get("results", {}).get("bindings", [])
                
                related_entities = []
                for result in bindings:
                    target_entity_id = result["item"]["value"].split("/")[-1]
                    
                    # Skip if the entity ID is the same as the input
                    if target_entity_id == wikidata_id:
                        continue
                    
                    # Create related entity entry
                    related_entity = {
                        "entity": {
                            "entity_id": f"wikidata_{target_entity_id}",
                            "name": result["itemLabel"]["value"],
                            "entity_type": self._determine_entity_type(result),
                            "description": result.get("itemDescription", {}).get("value", ""),
                            "metadata": {
                                "wikidata_id": target_entity_id,
                                "wikidata_url": result["item"]["value"]
                            }
                        },
                        "relationship": {
                            "relationship_id": f"wikidata_rel_{wikidata_id}_{target_entity_id}",
                            "source_entity_id": entity_id,
                            "target_entity_id": f"wikidata_{target_entity_id}",
                            "relation_type": self._map_relation_type(result["propertyLabel"]["value"]),
                            "confidence": 0.9,  # High confidence for Wikidata assertions
                            "metadata": {
                                "wikidata_property": result["property"]["value"],
                                "property_label": result["propertyLabel"]["value"]
                            }
                        },
                        "direction": "outgoing"
                    }
                    
                    related_entities.append(related_entity)
                
                # Cache the result
                self.cache[cache_key] = related_entities
                self._save_cache()
                
                return related_entities
            
            # Error or no results
            self.cache[cache_key] = []
            self._save_cache()
            return []
            
        except Exception as e:
            logger.error(f"Error querying Wikidata for related entities: {e}")
            return []
    
    def _map_relation_type(self, wikidata_property: str) -> str:
        """Map Wikidata property to GraphRAG relation type."""
        property_mapping = {
            "instance of": "is_a",
            "subclass of": "is_a",
            "part of": "part_of",
            "has part": "has_part",
            "located in": "located_in",
            "location": "located_in",
            "country": "located_in",
            "creator": "created_by",
            "created by": "created_by",
            "author": "created_by",
            "employer": "works_for",
            "owned by": "owned_by",
            "different from": "contradicts",
            "opposite of": "contradicts"
        }
        
        # Lowercase and look for exact match
        wikidata_property_lower = wikidata_property.lower()
        if wikidata_property_lower in property_mapping:
            return property_mapping[wikidata_property_lower]
        
        # Substring matching for partial matches
        for key, value in property_mapping.items():
            if key in wikidata_property_lower:
                return value
        
        # Default to related_to
        return "related_to"


class EntityLinker:
    """Advanced entity linking system with external KB integration."""
    
    def __init__(self):
        """Initialize the entity linker."""
        # Initialize knowledge bases
        self.local_kb = LocalKnowledgeBase()
        self.wikidata_kb = WikidataKnowledgeBase()
        
        # Initialize models
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        
        # Contextual patterns for entity type detection
        self.entity_patterns = {
            "person": [
                r"(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.) [A-Z][a-z]+(?: [A-Z][a-z]+)+",
                r"[A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)* (?:is|was) a (?:person|scientist|researcher|doctor|professor)"
            ],
            "organization": [
                r"(?:The |)[A-Z][a-z]+(?: [A-Z][a-z]+)* (?:Corporation|Company|Institute|University|Foundation|Association)",
                r"(?:The |)[A-Z][a-z]+(?: [A-Z][a-z]+)* (?:is|was) an? (?:organization|company|corporation|institution)"
            ],
            "location": [
                r"in (?:the |)[A-Z][a-z]+(?: [A-Z][a-z]+)*",
                r"(?:The |)[A-Z][a-z]+(?: [A-Z][a-z]+)* (?:is|was) a (?:country|city|state|region|place)"
            ],
            "date": [
                r"\d{1,2}/\d{1,2}/\d{2,4}",
                r"\d{1,2}-\d{1,2}-\d{2,4}",
                r"(?:January|February|March|April|May|June|July|August|September|October|November|December)(?: \d{1,2})?,? \d{4}"
            ],
            "concept": [
                r"concept of [A-Z][a-z]+(?: [A-Z][a-z]+)*",
                r"theory of [A-Z][a-z]+(?: [A-Z][a-z]+)*"
            ]
        }
    
    @timed_execution
    def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract entities from text with improved recognition and disambiguation.
        
        This method:
        1. Extracts candidate entities based on patterns
        2. Looks up entities in knowledge bases
        3. Performs contextual disambiguation
        4. Creates new entities for unknown mentions
        
        Args:
            text: The text to extract entities from
            
        Returns:
            List of extracted entities
        """
        entities: List[Entity] = []
        entity_mentions: Dict[str, List[Tuple[int, int]]] = {}
        processed_names: Set[str] = set()
        
        # Phase 1: Extract candidate entities using patterns
        candidates = self._extract_candidates(text)
        
        # Phase 2: Look up entities in knowledge bases and disambiguate
        for name, positions, candidate_type in candidates:
            # Skip if already processed
            if name.lower() in processed_names:
                continue
            processed_names.add(name.lower())
            
            # Initialize entity data with default values
            entity_id = None
            entity_type = candidate_type or EntityType.OTHER
            description = None
            aliases = []
            metadata = {}
            
            # Try to look up in local KB first
            local_entity = self.local_kb.lookup_entity(name)
            if local_entity:
                entity_id = local_entity["entity_id"]
                entity_type = local_entity["entity_type"]
                description = local_entity.get("description")
                aliases = local_entity.get("aliases", [])
                metadata = local_entity.get("metadata", {})
                metadata["source"] = "local_kb"
            else:
                # Try to look up in Wikidata
                wikidata_entity = self.wikidata_kb.lookup_entity(name)
                if wikidata_entity:
                    entity_id = wikidata_entity["entity_id"]
                    entity_type = wikidata_entity["entity_type"]
                    description = wikidata_entity.get("description")
                    aliases = wikidata_entity.get("aliases", [])
                    metadata = wikidata_entity.get("metadata", {})
                    metadata["source"] = "wikidata"
            
            # Create new entity if not found in any KB
            if not entity_id:
                entity = Entity(
                    name=name,
                    entity_type=entity_type,
                    description=f"Entity extracted from text: '{text[:100]}...'",
                    aliases=[],
                    metadata={"source": "extraction", "confidence": 0.7}
                )
            else:
                entity = Entity(
                    entity_id=entity_id,
                    name=name,
                    entity_type=entity_type,
                    description=description,
                    aliases=aliases,
                    metadata=metadata
                )
            
            # Add to entities list
            entities.append(entity)
            
            # Store mention positions
            entity_mentions[entity.entity_id] = positions
        
        # Phase 3: Enrich entities with additional information
        self._enrich_entities(entities, text)
        
        # Phase 4: Create relationships between entities
        relationships = self._create_relationships(entities, text)
        
        # Add entities and relationships to local KB for future use
        for entity in entities:
            # Only add new entities that aren't from external KBs
            if not entity.entity_id.startswith("wikidata_"):
                self.local_kb.add_entity(entity)
        
        for relationship in relationships:
            self.local_kb.add_relationship(relationship)
        
        logger.info(f"Extracted and enriched {len(entities)} entities with {len(relationships)} relationships")
        return entities
    
    def _extract_candidates(self, text: str) -> List[Tuple[str, List[Tuple[int, int]], Optional[str]]]:
        """Extract candidate entities from text."""
        candidates = []
        
        # Extract known entities using keyword mapping
        keyword_map: Dict[str, str] = {
            'climate change': 'concept',
            'global warming': 'concept',
            'artificial intelligence': 'concept',
            'united states': 'location',
            'european union': 'organization',
            'covid-19': 'concept',
            'paris agreement': 'concept',
        }
        
        # Check for known entities
        text_lower = text.lower()
        for keyword, entity_type in keyword_map.items():
            if keyword in text_lower:
                entity_name = ' '.join(word.capitalize() for word in keyword.split())
                positions = []
                
                # Find all occurrences
                start = 0
                while True:
                    pos = text_lower.find(keyword, start)
                    if pos == -1:
                        break
                    
                    positions.append((pos, pos + len(keyword)))
                    start = pos + 1
                
                if positions:
                    candidates.append((entity_name, positions, entity_type))
        
        # Extract entities based on capitalization patterns
        capitals_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        capitalized_matches = re.finditer(capitals_pattern, text)
        
        for match in capitalized_matches:
            name = match.group(0)
            # Skip common words that are capitalized
            if name.lower() in {'i', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                                'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                'september', 'october', 'november', 'december'}:
                continue
                
            # Skip if already added as a known entity
            if any(name.lower() == candidate[0].lower() for candidate in candidates):
                continue
            
            # Determine entity type based on context
            entity_type = self._determine_entity_type_from_context(text, match.start(), match.end())
            
            # Add to candidates
            positions = [(match.start(), match.end())]
            candidates.append((name, positions, entity_type))
        
        # Extract entities based on contextual patterns
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    name = match.group(0)
                    # Extract just the entity name from the context pattern
                    name = re.search(r'[A-Z][a-z]+(?: [A-Z][a-z]+)*', name)
                    if name:
                        name = name.group(0)
                        # Skip if already added
                        if any(name.lower() == candidate[0].lower() for candidate in candidates):
                            continue
                        
                        positions = [(match.start(), match.end())]
                        candidates.append((name, positions, entity_type))
        
        return candidates
    
    def _determine_entity_type_from_context(self, text: str, start: int, end: int) -> str:
        """Determine entity type based on surrounding context."""
        # Get context around the entity (up to 100 chars before and after)
        before = text[max(0, start - 100):start]
        after = text[end:min(len(text), end + 100)]
        context = before + " " + after
        
        # Check for type indicators in context
        type_indicators = {
            EntityType.PERSON: ["person", "who", "he", "she", "born", "died", "wrote", "said", "author", "researcher", "scientist", "professor", "Dr."],
            EntityType.ORGANIZATION: ["organization", "company", "institution", "corporation", "founded", "headquartered", "based in", "employees", "team"],
            EntityType.LOCATION: ["location", "city", "country", "region", "located", "capital", "north", "south", "east", "west", "in the"],
            EntityType.CONCEPT: ["concept", "idea", "theory", "approach", "method", "technique", "defined as", "refers to"],
            EntityType.PRODUCT: ["product", "device", "tool", "software", "platform", "technology", "released", "launched", "version"],
            EntityType.EVENT: ["event", "conference", "meeting", "took place", "occurred", "happened", "held on"],
            EntityType.DATE: ["date", "day", "month", "year", "century", "period", "era", "decade"],
        }
        
        # Count occurrences of each type's indicators
        type_scores = {entity_type: 0 for entity_type in EntityType}
        for entity_type, indicators in type_indicators.items():
            for indicator in indicators:
                if indicator.lower() in context.lower():
                    type_scores[entity_type] += 1
        
        # Return the type with the highest score
        if any(type_scores.values()):
            max_type = max(type_scores.items(), key=lambda x: x[1])[0]
            return max_type
        
        # Default to OTHER if no indicators found
        return EntityType.OTHER
    
    def _enrich_entities(self, entities: List[Entity], text: str) -> None:
        """Enrich entities with additional information from knowledge bases."""
        for entity in entities:
            # Skip if already has rich metadata
            if entity.metadata.get("source") in ["wikidata", "local_kb"]:
                continue
            
            # Try to get related entities from Wikidata
            if entity.name:
                wikidata_entity = self.wikidata_kb.lookup_entity(entity.name)
                if wikidata_entity:
                    # Update with richer information
                    entity.description = wikidata_entity.get("description") or entity.description
                    entity.aliases = wikidata_entity.get("aliases", [])
                    entity.metadata.update(wikidata_entity.get("metadata", {}))
                    entity.metadata["source"] = "wikidata"
                    entity.metadata["confidence"] = 0.9  # High confidence for Wikidata entities
    
    def _create_relationships(self, entities: List[Entity], text: str) -> List[Relationship]:
        """Create relationships between entities based on co-occurrence and knowledge bases."""
        relationships = []
        
        # Create relationships based on co-occurrence in text
        # (simple approach: entities mentioned close to each other are likely related)
        if len(entities) >= 2:
            # Create a graph of entities based on their proximity in text
            for i in range(len(entities) - 1):
                for j in range(i + 1, len(entities)):
                    entity1 = entities[i]
                    entity2 = entities[j]
                    
                    # Skip if identical
                    if entity1.entity_id == entity2.entity_id:
                        continue
                    
                    # Determine relationship type based on entity types
                    relation_type = self._determine_relationship_type(entity1, entity2, text)
                    
                    relationship = Relationship(
                        source_entity_id=entity1.entity_id,
                        target_entity_id=entity2.entity_id,
                        relation_type=relation_type,
                        confidence=0.7,  # Medium confidence for co-occurrence relationships
                        metadata={
                            "source": "co_occurrence",
                            "extraction_method": "proximity"
                        }
                    )
                    relationships.append(relationship)
        
        # Try to get additional relationships from knowledge bases
        for entity in entities:
            # Skip non-Wikidata entities to avoid too many API calls
            if entity.metadata.get("source") == "wikidata":
                related_entities = self.wikidata_kb.get_related_entities(entity.entity_id)
                
                for related in related_entities:
                    relationship = Relationship(
                        relationship_id=related["relationship"]["relationship_id"],
                        source_entity_id=related["relationship"]["source_entity_id"],
                        target_entity_id=related["relationship"]["target_entity_id"],
                        relation_type=related["relationship"]["relation_type"],
                        confidence=related["relationship"]["confidence"],
                        metadata=related["relationship"]["metadata"]
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _determine_relationship_type(self, entity1: Entity, entity2: Entity, text: str) -> str:
        """Determine relationship type based on entity types and context."""
        # Look for text indicators of relationships
        text_lower = text.lower()
        
        # Location relationships
        if entity1.entity_type == EntityType.LOCATION and entity2.entity_type == EntityType.ORGANIZATION:
            if "headquartered in" in text_lower or "based in" in text_lower:
                return RelationType.LOCATED_IN
        elif entity1.entity_type == EntityType.ORGANIZATION and entity2.entity_type == EntityType.LOCATION:
            if "headquartered in" in text_lower or "based in" in text_lower:
                return RelationType.LOCATED_IN
        
        # Creation relationships
        if entity1.entity_type == EntityType.PERSON and entity2.entity_type in [EntityType.CONCEPT, EntityType.PRODUCT]:
            if "created" in text_lower or "developed" in text_lower or "invented" in text_lower:
                return RelationType.CREATED_BY
        
        # Employment relationships
        if entity1.entity_type == EntityType.PERSON and entity2.entity_type == EntityType.ORGANIZATION:
            if "works for" in text_lower or "employed by" in text_lower or "works at" in text_lower:
                return RelationType.WORKS_FOR
        
        # Opposition relationships
        if "contradicts" in text_lower or "disagrees with" in text_lower or "opposes" in text_lower:
            return RelationType.CONTRADICTS
        
        # Support relationships
        if "supports" in text_lower or "agrees with" in text_lower or "confirms" in text_lower:
            return RelationType.SUPPORTS
        
        # Is-a relationships (taxonomy)
        if "is a" in text_lower or "is an" in text_lower or "is type of" in text_lower:
            return RelationType.IS_A
        
        # Part-of relationships
        if "part of" in text_lower or "component of" in text_lower or "belongs to" in text_lower:
            return RelationType.PART_OF
        
        # Default to related_to
        return RelationType.RELATED_TO
    
    @timed_execution
    def disambiguate_entities(self, entities: List[Entity], text: str) -> List[Entity]:
        """
        Disambiguate entities based on context and external knowledge bases.
        
        This method resolves ambiguous entity mentions by using contextual clues
        and information from knowledge bases.
        
        Args:
            entities: List of candidate entities to disambiguate
            text: The original text
            
        Returns:
            List of disambiguated entities
        """
        if not entities:
            return []
        
        # Calculate text embedding for context matching
        text_embedding = self.model.encode(text, normalize_embeddings=True)
        
        disambiguated_entities = []
        
        for entity in entities:
            # Skip if already disambiguated
            if entity.metadata.get("disambiguated", False):
                disambiguated_entities.append(entity)
                continue
            
            # Handle entities from knowledge bases
            if entity.metadata.get("source") in ["wikidata", "local_kb"]:
                entity.metadata["disambiguated"] = True
                disambiguated_entities.append(entity)
                continue
            
            # For ambiguous entities, try to disambiguate
            candidates = []
            
            # Try local KB
            local_entity = self.local_kb.lookup_entity(entity.name)
            if local_entity:
                candidates.append(Entity.from_dict(local_entity))
            
            # Try Wikidata
            wikidata_entity = self.wikidata_kb.lookup_entity(entity.name)
            if wikidata_entity:
                candidates.append(Entity.from_dict(wikidata_entity))
            
            # If no candidates, keep the original entity
            if not candidates:
                entity.metadata["disambiguated"] = True
                disambiguated_entities.append(entity)
                continue
            
            # Find the best match based on context
            best_match = None
            best_score = 0.0
            
            for candidate in candidates:
                # Create a description using entity info
                description = f"{candidate.name}. {candidate.description or ''}"
                if candidate.aliases:
                    description += f" Also known as: {', '.join(candidate.aliases)}."
                
                # Calculate similarity to text context
                candidate_embedding = self.model.encode(description, normalize_embeddings=True)
                score = float(util.dot_score(text_embedding, candidate_embedding)[0][0])
                
                if score > best_score:
                    best_score = score
                    best_match = candidate
            
            # Use the best match if found and score is high enough
            if best_match and best_score > 0.6:
                best_match.metadata["disambiguated"] = True
                best_match.metadata["disambiguation_score"] = best_score
                disambiguated_entities.append(best_match)
            else:
                # Otherwise use the original entity
                entity.metadata["disambiguated"] = True
                disambiguated_entities.append(entity)
        
        return disambiguated_entities


# Global entity linker instance
entity_linker = EntityLinker()


def get_entity_linker() -> EntityLinker:
    """Get the global entity linker instance."""
    return entity_linker