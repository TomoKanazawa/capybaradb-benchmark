# ChromaDB Python SDK Documentation

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Client Configuration](#client-configuration)
- [Collections](#collections)
- [Adding Data](#adding-data)
- [Querying Data](#querying-data)
- [Updating and Deleting Data](#updating-and-deleting-data)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [API Reference](#api-reference)

## Installation

```bash
pip install chromadb
```

Requires Python 3.9 or later.

## Quick Start

```python
import chromadb

# Initialize client
client = chromadb.Client()

# Create a collection
collection = client.create_collection("my_collection")

# Add documents
collection.add(
    documents=["This is document1", "This is document2"],
    metadatas=[{"source": "notion"}, {"source": "google-docs"}],
    ids=["doc1", "doc2"]
)

# Query documents
results = collection.query(
    query_texts=["This is a query document"],
    n_results=2
)
```

## Core Concepts

### Client
The entry point for interacting with ChromaDB. Manages collections and provides database-level operations.

### Collections
A group of related documents and their embeddings. Collections are the primary way to organize and manage your data.

### Documents
Text or other data that you want to store and search. ChromaDB automatically handles tokenization and embedding generation.

### Embeddings
Vector representations of your documents. ChromaDB can generate these automatically or accept pre-computed embeddings.

### Metadata
Additional information associated with documents for filtering and organization.

## Client Configuration

```python
# In-memory client (for development)
client = chromadb.Client()

# Persistent client
client = chromadb.PersistentClient(path="/path/to/db")

# Client with custom settings
client = chromadb.HttpClient(
    host="localhost",
    port=8000,
    ssl=False,
    headers={"Authorization": "Bearer your_token"}
)
```

## Collections

### Creating Collections
```python
# Basic collection
collection = client.create_collection("my_collection")

# Collection with custom embedding function
collection = client.create_collection(
    name="my_collection",
    embedding_function=my_embedding_function,
    metadata={"description": "My custom collection"}
)

# Get existing collection
collection = client.get_collection("my_collection")

# Get or create collection
collection = client.get_or_create_collection("my_collection")
```

### Collection Operations
```python
# List all collections
collections = client.list_collections()

# Delete collection
client.delete_collection("my_collection")

# Modify collection metadata
collection.modify(metadata={"description": "Updated description"})
```

## Adding Data

### Basic Addition
```python
collection.add(
    documents=["Document 1", "Document 2"],
    metadatas=[{"source": "web"}, {"source": "pdf"}],
    ids=["id1", "id2"]
)
```

### Adding with Custom Embeddings
```python
collection.add(
    documents=["Document 1", "Document 2"],
    embeddings=[[1.1, 2.3, 3.2], [4.5, 6.7, 8.9]],
    metadatas=[{"source": "web"}, {"source": "pdf"}],
    ids=["id1", "id2"]
)
```

### Batch Addition
```python
collection.add(
    documents=["Doc1", "Doc2", "Doc3"],
    metadatas=[
        {"source": "web", "author": "Alice"},
        {"source": "pdf", "author": "Bob"},
        {"source": "doc", "author": "Charlie"}
    ],
    ids=["id1", "id2", "id3"]
)
```

## Querying Data

### Basic Queries
```python
results = collection.query(
    query_texts=["Search query"],
    n_results=5
)
```

### Advanced Queries
```python
# Query with metadata filtering
results = collection.query(
    query_texts=["Search query"],
    where={"source": "web"},
    where_document={"$contains": "specific text"},
    n_results=5
)

# Query with multiple texts
results = collection.query(
    query_texts=["Query 1", "Query 2"],
    n_results=3
)
```

### Query Results
The query results contain:
- `ids`: List of matching document IDs
- `distances`: Distance scores for each match
- `metadatas`: Metadata for each matching document
- `documents`: The actual document contents

## Updating and Deleting Data

### Updating Documents
```python
collection.update(
    ids=["id1"],
    documents=["Updated document"],
    metadatas=[{"source": "updated"}]
)
```

### Deleting Documents
```python
# Delete by IDs
collection.delete(ids=["id1", "id2"])

# Delete with where filter
collection.delete(where={"source": "web"})
```

## Advanced Features

### Filtering
```python
# Metadata filtering
results = collection.query(
    query_texts=["Query"],
    where={"source": {"$eq": "web"}}
)

# Document content filtering
results = collection.query(
    query_texts=["Query"],
    where_document={"$contains": "specific phrase"}
)
```

### Custom Embedding Functions
```python
from typing import List

class CustomEmbeddingFunction:
    def __call__(self, texts: List[str]) -> List[List[float]]:
        # Your embedding logic here
        return embeddings

collection = client.create_collection(
    "custom_embeddings",
    embedding_function=CustomEmbeddingFunction()
)
```

### Persistence and Backup
```python
# Create persistent client
client = chromadb.PersistentClient(path="/path/to/db")

# Backup collection
collection.persist()
```

## Best Practices

1. **Memory Management**
   - Use persistent storage for production
   - Batch operations for large datasets
   - Monitor embedding dimensions and collection size

2. **Performance Optimization**
   - Index properly sized chunks of text
   - Use appropriate n_results values
   - Implement efficient filtering strategies

3. **Error Handling**
   ```python
   try:
       collection.add(
           documents=["Document"],
           ids=["id1"]
       )
   except Exception as e:
       print(f"Error adding document: {e}")
   ```

4. **Security**
   - Use environment variables for sensitive data
   - Implement proper authentication
   - Regular backups of persistent storage

## API Reference

### Client Methods
- `create_collection(name, metadata, embedding_function)`
- `get_collection(name)`
- `list_collections()`
- `delete_collection(name)`
- `get_or_create_collection(name)`

### Collection Methods
- `add(documents, metadatas, embeddings, ids)`
- `query(query_texts, n_results, where, where_document)`
- `update(ids, documents, metadatas, embeddings)`
- `delete(ids, where, where_document)`
- `get(ids, where, where_document)`
- `count()`
- `modify(metadata)`
- `persist()`

### Query Operators
- `$eq`: Equal to
- `$ne`: Not equal to
- `$gt`: Greater than
- `$gte`: Greater than or equal to
- `$lt`: Less than
- `$lte`: Less than or equal to
- `$contains`: Contains string
- `$in`: In array
- `$nin`: Not in array

For more detailed information and updates, visit the [official ChromaDB documentation](https://docs.trychroma.com/). 