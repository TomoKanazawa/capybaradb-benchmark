"""
Minimal test file to verify each implementation of ingest_document works without errors.
"""

import unittest
from typing import Any, Callable, Dict, List
import importlib
import sys
from unittest.mock import MagicMock

# Simple test document and fields for testing all implementations
TEST_DOCUMENT = {
    "id": "test_doc_001",
    "title": "Test Document",
    "body": "This is a simple test document for testing purposes.",
    "metadata": {"author": "Tester", "date": "2024-03-25"}
}
TEST_SEARCHABLE_FIELDS = ["title", "body"]

class MockEmbeddingModel:
    """Mock embedding model that returns random embeddings."""
    def embed_documents(self, texts):
        # Return a mock embedding vector for each text
        return [[0.1, 0.2, 0.3, 0.4] for _ in texts]
    
    def embed_query(self, text):
        # Return a mock embedding vector for the query
        return [0.1, 0.2, 0.3, 0.4]
    
    def embed_text(self, text):
        # Support embed_text method used by some implementations
        if isinstance(text, str):
            return [0.1, 0.2, 0.3, 0.4]
        return [[0.1, 0.2, 0.3, 0.4] for _ in text]
    
    def __call__(self, texts):
        # Support callable interface
        if isinstance(texts, str):
            return [0.1, 0.2, 0.3, 0.4]
        return [[0.1, 0.2, 0.3, 0.4] for _ in texts]

class TestIngestDocument(unittest.TestCase):
    """Test cases for ingest_document implementations."""

    def setUp(self):
        """Set up test environment."""
        self.embedding_model = MockEmbeddingModel()
        
        # Create mock modules for pgvector and its sub-modules
        pgvector_mock = MagicMock()
        pgvector_psycopg2_mock = MagicMock()
        pgvector_mock.psycopg2 = pgvector_psycopg2_mock
        pgvector_psycopg2_mock.register_vector = MagicMock()
        
        # Mock commonly used database libraries
        sys.modules['chromadb'] = MagicMock()
        sys.modules['pinecone'] = MagicMock()
        sys.modules['pymongo'] = MagicMock()
        sys.modules['psycopg2'] = MagicMock()
        sys.modules['capybaradb'] = MagicMock()
        sys.modules['pgvector'] = pgvector_mock
        sys.modules['pgvector.psycopg2'] = pgvector_psycopg2_mock
        sys.modules['langchain'] = MagicMock()
        sys.modules['langchain.text_splitter'] = MagicMock()
        sys.modules['langchain.vectorstores'] = MagicMock()
        sys.modules['langchain.schema'] = MagicMock()
        
    def _test_implementation(self, module_name: str):
        """Helper to test an implementation by module name."""
        try:
            module = importlib.import_module(module_name)
            ingest_document = getattr(module, 'ingest_document')
            
            # Call the function with test data
            ingest_document(
                document=TEST_DOCUMENT,
                searchable_fields=TEST_SEARCHABLE_FIELDS,
                chunk_size=100,
                chunk_overlap=20,
                separator=" ",
                embedding_model=self.embedding_model
            )
            
            # If we reach here without exceptions, the test passes
            return True
        except Exception as e:
            self.fail(f"Testing {module_name} failed with error: {str(e)}")
            return False

    def test_capybaradb(self):
        """Test CapybaraDB implementation."""
        self._test_implementation('capybaradb')
        
    def test_chroma(self):
        """Test ChromaDB implementation."""
        self._test_implementation('chroma')
        
    def test_langchain(self):
        """Test Langchain implementation."""
        self._test_implementation('langchain')
        
    def test_mongo(self):
        """Test MongoDB implementation."""
        self._test_implementation('mongo')
        
    def test_pgvector(self):
        """Test pgvector implementation."""
        self._test_implementation('pgvector')
        
    def test_pinecone(self):
        """Test Pinecone implementation."""
        self._test_implementation('pinecone')
        
if __name__ == '__main__':
    unittest.main() 