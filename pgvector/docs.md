# PGVector Python SDK Documentation

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Core Concepts](#core-concepts)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Vector Search Capabilities](#vector-search-capabilities)
- [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)
- [API Reference](#api-reference)
- [Examples](#examples)

## Introduction

PGVector is a powerful PostgreSQL extension that adds vector similarity search capabilities to your database. This documentation covers the Python SDK for PGVector, which allows you to seamlessly integrate vector operations into your Python applications.

### What is PGVector?

PGVector transforms PostgreSQL into a vector database, enabling:
- Storage of high-dimensional vectors
- Fast similarity searches
- Integration with machine learning workflows
- ACID compliance with vector operations
- Seamless combination of traditional and vector data

## Installation

```bash
# Install the Python package
pip install pgvector

# Install the PostgreSQL extension (on your database)
CREATE EXTENSION vector;
```

## Getting Started

### Basic Connection Setup

```python
import psycopg2
from pgvector.psycopg2 import register_vector

# Connect to your database
conn = psycopg2.connect(
    host="localhost",
    database="your_database",
    user="your_user",
    password="your_password"
)

# Register the vector type
register_vector(conn)
```

## Core Concepts

### Vector Types
PGVector introduces a new `vector` data type in PostgreSQL that can store arrays of floating-point numbers. These vectors can represent:
- Embeddings from language models
- Image features
- Audio fingerprints
- Any other high-dimensional data

### Distance Metrics
PGVector supports three distance metrics:
- Euclidean distance (L2 distance) - `<->` operator
- Inner product - `<#>` operator
- Cosine distance - `<=>` operator

## Basic Usage

### Creating Tables with Vector Columns

```python
cur = conn.cursor()

# Create a table with a vector column
cur.execute("""
    CREATE TABLE items (
        id serial PRIMARY KEY,
        embedding vector(384)  -- specify dimension size
    )
""")
```

### Inserting Vectors

```python
# Insert a single vector
vector_data = [1.0, 2.0, 3.0]  # Must match dimension size
cur.execute("INSERT INTO items (embedding) VALUES (%s)", (vector_data,))

# Batch insert
vectors = [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)]
cur.executemany("INSERT INTO items (embedding) VALUES (%s)", vectors)
```

## Advanced Features

### Indexing Methods

PGVector supports multiple indexing methods for optimized search:

1. **IVFFlat Index**
```sql
CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops)
```

2. **HNSW Index** (Hierarchical Navigable Small World)
```sql
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops)
```

### Index Parameters

```sql
-- IVFFlat with custom lists
CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- HNSW with custom parameters
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops) WITH (
    m = 16,
    ef_construction = 64
);
```

## Vector Search Capabilities

### Nearest Neighbor Search

```python
# Find the 5 nearest neighbors using L2 distance
query_vector = [1.0, 2.0, 3.0]
cur.execute("""
    SELECT id, embedding <-> %s as distance
    FROM items
    ORDER BY distance
    LIMIT 5
""", (query_vector,))

# Using inner product
cur.execute("""
    SELECT id, embedding <#> %s as distance
    FROM items
    ORDER BY distance
    LIMIT 5
""", (query_vector,))

# Using cosine distance
cur.execute("""
    SELECT id, embedding <=> %s as distance
    FROM items
    ORDER BY distance
    LIMIT 5
""", (query_vector,))
```

### Filtered Vector Search

```python
# Combine vector search with traditional filters
cur.execute("""
    SELECT id, embedding <-> %s as distance
    FROM items
    WHERE category = 'electronics'
    ORDER BY distance
    LIMIT 5
""", (query_vector,))
```

## Performance Optimization

### Index Selection
- Use IVFFlat for better build time and memory usage
- Use HNSW for faster search with more memory usage
- Consider table size and query patterns when choosing

### Tuning Parameters

```python
# Set effective search parameters for HNSW
cur.execute("SET hnsw.ef_search = 100;")

# Set probe lists for IVFFlat
cur.execute("SET ivfflat.probes = 10;")
```

## Best Practices

1. **Dimension Selection**
   - Choose appropriate dimensions based on your embedding model
   - Keep dimensions consistent within a column

2. **Index Management**
   - Rebuild indexes periodically for optimal performance
   - Monitor index size and search performance

3. **Error Handling**
```python
try:
    cur.execute("INSERT INTO items (embedding) VALUES (%s)", (vector_data,))
except psycopg2.Error as e:
    print(f"Error inserting vector: {e}")
```

## API Reference

### Vector Operations
- `<->`: Euclidean distance
- `<#>`: Negative inner product
- `<=>`: Cosine distance

### Index Types
- `vector_l2_ops`: L2 distance operations
- `vector_ip_ops`: Inner product operations
- `vector_cosine_ops`: Cosine distance operations

## Examples

### Complete Search Application Example

```python
import psycopg2
from pgvector.psycopg2 import register_vector

def setup_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="vector_db",
        user="user",
        password="password"
    )
    register_vector(conn)
    return conn

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id serial PRIMARY KEY,
                embedding vector(384),
                metadata jsonb
            )
        """)
        cur.execute("""
            CREATE INDEX ON items USING hnsw (embedding vector_l2_ops)
        """)

def insert_item(conn, embedding, metadata):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO items (embedding, metadata) VALUES (%s, %s)",
            (embedding, metadata)
        )
    conn.commit()

def search_similar(conn, query_vector, limit=5):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, metadata, embedding <-> %s as distance
            FROM items
            ORDER BY distance
            LIMIT %s
        """, (query_vector, limit))
        return cur.fetchall()

# Usage example
conn = setup_connection()
create_table(conn)

# Insert sample data
sample_vector = [0.1] * 384
sample_metadata = {"description": "Sample item"}
insert_item(conn, sample_vector, sample_metadata)

# Search
results = search_similar(conn, [0.1] * 384)
for id, metadata, distance in results:
    print(f"ID: {id}, Distance: {distance}, Metadata: {metadata}")
```

This documentation provides a comprehensive overview of the PGVector Python SDK. For specific use cases or additional information, please refer to the official documentation or reach out to the community. 