"""Tests for the Source model."""

import unittest
import datetime
import uuid
from pydantic import ValidationError

from agent_provocateur.models import Source, SourceType


class TestSourceModel(unittest.TestCase):
    """Test the Source model."""

    def test_source_creation(self):
        """Test creating a Source instance."""
        source = Source(
            source_id=str(uuid.uuid4()),
            source_type=SourceType.WEB,
            title="Test Source",
            url="https://example.com",
            confidence=0.9,
            citation="Example Citation (2023)"
        )
        
        self.assertEqual(source.source_type, SourceType.WEB)
        self.assertEqual(source.title, "Test Source")
        self.assertEqual(source.url, "https://example.com")
        self.assertEqual(source.confidence, 0.9)
        self.assertEqual(source.citation, "Example Citation (2023)")

    def test_source_validation(self):
        """Test validation of Source model."""
        # Missing required fields should raise ValidationError
        with self.assertRaises(ValidationError):
            Source(
                source_type=SourceType.WEB,
                title="Test Source"
            )
        
        # Invalid source_type should raise ValidationError
        with self.assertRaises(ValidationError):
            Source(
                source_id=str(uuid.uuid4()),
                source_type="invalid_type",
                title="Test Source"
            )

    def test_from_dict_conversion(self):
        """Test conversion from dictionary to Source."""
        source_dict = {
            "type": "web",
            "title": "Dict Source",
            "url": "https://example.com/dict",
            "confidence": 0.8
        }
        
        source = Source.from_dict(source_dict)
        
        self.assertEqual(source.source_type, SourceType.WEB)
        self.assertEqual(source.title, "Dict Source")
        self.assertEqual(source.url, "https://example.com/dict")
        self.assertEqual(source.confidence, 0.8)
        
        # Test handling of unknown source type
        unknown_dict = {
            "type": "unknown_type",
            "title": "Unknown Source"
        }
        
        unknown_source = Source.from_dict(unknown_dict)
        self.assertEqual(unknown_source.source_type, SourceType.OTHER)

    def test_to_dict_conversion(self):
        """Test conversion from Source to dictionary."""
        now = datetime.datetime.now()
        source = Source(
            source_id="test-id",
            source_type=SourceType.DOCUMENT,
            title="To Dict Test",
            doc_id="doc123",
            retrieved_at=now,
            confidence=0.75,
            citation="Test Citation"
        )
        
        source_dict = source.to_dict()
        
        self.assertEqual(source_dict["source_id"], "test-id")
        self.assertEqual(source_dict["type"], "document")
        self.assertEqual(source_dict["title"], "To Dict Test")
        self.assertEqual(source_dict["doc_id"], "doc123")
        self.assertEqual(source_dict["retrieved_at"], now.isoformat())
        self.assertEqual(source_dict["confidence"], 0.75)
        self.assertEqual(source_dict["citation"], "Test Citation")

    def test_roundtrip_conversion(self):
        """Test dictionary to Source to dictionary conversion."""
        original_dict = {
            "type": "api",
            "title": "API Source",
            "url": "https://api.example.com",
            "confidence": 0.95,
            "custom_field": "custom value"
        }
        
        # Convert dict to Source
        source = Source.from_dict(original_dict)
        
        # Convert Source back to dict
        result_dict = source.to_dict()
        
        # Check that important fields were preserved
        self.assertEqual(result_dict["type"], "api")
        self.assertEqual(result_dict["title"], "API Source")
        self.assertEqual(result_dict["url"], "https://api.example.com")
        self.assertEqual(result_dict["confidence"], 0.95)
        self.assertEqual(result_dict["custom_field"], "custom value")


if __name__ == "__main__":
    unittest.main()