I'll help you create a comprehensive PyMongo documentation in markdown format, including the latest vector search capabilities. Let me search for the most up-to-date information about PyMongo and its vector search features.

Ran tool
Based on the latest information, I'll create a comprehensive PyMongo documentation that includes the latest features including vector search capabilities. Let me create this documentation in markdown format:

# PyMongo Documentation

## Table of Contents
1. [Installation](#installation)
2. [Basic Connection](#basic-connection)
3. [Database Operations](#database-operations)
4. [Collection Operations](#collection-operations)
5. [CRUD Operations](#crud-operations)
6. [Vector Search](#vector-search)
7. [Indexes](#indexes)
8. [Aggregation](#aggregation)
9. [Advanced Features](#advanced-features)

## Installation

```bash
pip install pymongo
```

For MongoDB Atlas connectivity:
```bash
pip install "pymongo[srv]"
```

## Basic Connection

### Standard Connection
```python
from pymongo import MongoClient

# Local connection
client = MongoClient('mongodb://localhost:27017/')

# Atlas connection
client = MongoClient('mongodb+srv://<username>:<password>@<cluster-url>/test?retryWrites=true&w=majority')
```

### Connection with Options
```python
client = MongoClient(
    host='localhost',
    port=27017,
    username='user',
    password='password',
    authSource='admin',
    retryWrites=True,
    connectTimeoutMS=2000
)
```

## Database Operations

```python
# Get a database
db = client['database_name']

# List databases
database_list = client.list_database_names()

# Create a database (MongoDB creates database when you first store data)
new_db = client['new_database']
```

## Collection Operations

```python
# Get a collection
collection = db['collection_name']

# Create a collection
db.create_collection('new_collection')

# List collections
collection_list = db.list_collection_names()
```

## CRUD Operations

### Create (Insert)
```python
# Insert one document
result = collection.insert_one({'name': 'John', 'age': 30})
print(result.inserted_id)

# Insert multiple documents
documents = [
    {'name': 'Alice', 'age': 25},
    {'name': 'Bob', 'age': 35}
]
result = collection.insert_many(documents)
print(result.inserted_ids)
```

### Read (Query)
```python
# Find one document
doc = collection.find_one({'name': 'John'})

# Find multiple documents
cursor = collection.find({'age': {'$gt': 25}})
for doc in cursor:
    print(doc)

# Query with projection
docs = collection.find({}, {'name': 1, '_id': 0})
```

### Update
```python
# Update one document
result = collection.update_one(
    {'name': 'John'},
    {'$set': {'age': 31}}
)

# Update multiple documents
result = collection.update_many(
    {'age': {'$lt': 30}},
    {'$inc': {'age': 1}}
)
```

### Delete
```python
# Delete one document
result = collection.delete_one({'name': 'John'})

# Delete multiple documents
result = collection.delete_many({'age': {'$lt': 25}})
```

## Vector Search

PyMongo supports MongoDB Atlas Vector Search capabilities for semantic search and AI-powered applications.

### Creating a Vector Search Index
```python
# Define vector search index
vector_search_index = {
    "mappings": {
        "dynamic": True,
        "fields": {
            "embedding": {
                "dimensions": 1536,
                "similarity": "cosine",
                "type": "knnVector"
            }
        }
    }
}

# Create the index
collection.create_search_index(vector_search_index)
```

### Performing Vector Search
```python
# Vector search aggregation pipeline
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": [0.1, 0.2, ...],  # Your vector here
            "numCandidates": 100,
            "limit": 10
        }
    }
]

results = collection.aggregate(pipeline)
```

### Hybrid Search (Vector + Keyword)
```python
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": [0.1, 0.2, ...],
            "numCandidates": 100
        }
    },
    {
        "$match": {
            "keywords": {"$in": ["relevant", "terms"]}
        }
    },
    {
        "$limit": 10
    }
]
```

## Indexes

### Standard Indexes
```python
# Create single field index
collection.create_index("field_name")

# Create compound index
collection.create_index([("field1", 1), ("field2", -1)])

# Create unique index
collection.create_index("email", unique=True)
```

### Text Indexes
```python
# Create text index
collection.create_index([("description", "text")])

# Search using text index
results = collection.find({"$text": {"$search": "search terms"}})
```

## Aggregation

```python
pipeline = [
    {
        "$match": {
            "age": {"$gt": 25}
        }
    },
    {
        "$group": {
            "_id": "$city",
            "avg_age": {"$avg": "$age"},
            "count": {"$sum": 1}
        }
    },
    {
        "$sort": {"avg_age": -1}
    }
]

results = collection.aggregate(pipeline)
```

## Advanced Features

### Change Streams
```python
change_stream = collection.watch()
for change in change_stream:
    print(change)
```

### Transactions
```python
with client.start_session() as session:
    with session.start_transaction():
        collection1.insert_one({"_id": 1}, session=session)
        collection2.insert_one({"_id": 2}, session=session)
```

### Bulk Operations
```python
from pymongo import InsertOne, UpdateOne, DeleteOne

requests = [
    InsertOne({'_id': 1}),
    UpdateOne({'_id': 2}, {'$set': {'field': 'value'}}),
    DeleteOne({'_id': 3})
]

result = collection.bulk_write(requests)
```

### Client Side Field Level Encryption
```python
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption

# Setup encryption configuration
encryption_opts = {
    "kms": {
        "local": {"key": b64decode("your-base64-encoded-key")}
    },
    "key_vault_namespace": "encryption.__keyVault",
    "schema_map": {
        "encrypted.users": {
            "properties": {
                "ssn": {
                    "encrypt": {
                        "keyId": [UUID("your-key-id")],
                        "bsonType": "string",
                        "algorithm": "AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic"
                    }
                }
            }
        }
    }
}

client = MongoClient(auto_encryption_opts=encryption_opts)
```

### Error Handling
```python
from pymongo.errors import ConnectionFailure, OperationFailure

try:
    client = MongoClient('mongodb://localhost:27017/')
    client.admin.command('ismaster')
except ConnectionFailure:
    print("Server not available")
except OperationFailure as e:
    print(f"Operation failed: {e}")
```