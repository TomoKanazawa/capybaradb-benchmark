# CapybaraDB Python SDK Documentation

## Installation

To install the CapybaraDB Python SDK, use pip:

```bash
pip install capybaradb
```

## Getting Started

### Authentication

To use CapybaraDB, you need an API key and project ID.

1. Sign up at [CapybaraDB Sign Up](https://capybaradb.co).
2. Create an API key from the API Key page in the developer console.
3. Get your project ID from the welcome or collection page of the console.

For local development, you can set the credentials directly:

```python
CAPYBARA_API_KEY = "your_api_key"
CAPYBARA_PROJECT_ID = "your_project_id"
```

For production, it's recommended to use environment variables:

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access credentials
api_key = os.getenv("CAPYBARA_API_KEY")
project_id = os.getenv("CAPYBARA_PROJECT_ID")
```

### Initializing Client

Initialize the SDK client to start interacting with CapybaraDB:

```python
from capybaradb import CapybaraDB, EmbText

# Initialize client
client = CapybaraDB()

# Access a database
db = client.db("your_db_name")

# Access a collection
collection = db.collection("your_collection_name")
```

## Core Concepts

### CapybaraDB Client

The `CapybaraDB` class is the main entry point for interacting with CapybaraDB. It provides methods for authenticating and accessing databases.

```python
from capybaradb import CapybaraDB

# Initialize with default settings (uses env variables)
client = CapybaraDB()

# Initialize with specific parameters
client = CapybaraDB(api_key="your_api_key", project_id="your_project_id")
```

### Databases

The `db` method of the CapybaraDB client lets you access a database:

```python
db = client.db("your_db_name")
```

### Collections

Databases contain collections, which store documents:

```python
collection = db.collection("your_collection_name")
```

## Document Operations

### Insert Documents

Insert one or more documents into a collection:

```python
from capybaradb import EmbText

# Create document with embedded text
docs = [{
    "name": "John Doe",
    "email": "johndoe@example.com",
    "age": 30,
    "bio": EmbText("John is a software engineer with expertise in AI.")
}]

# Insert document
response = collection.insert(docs)

# Process the response
inserted_ids = response["inserted_ids"]
task_id = response.get("task_id")  # Might be None if processing completed synchronously
```

Response format:
```json
{
  "inserted_ids": [
    "64d2f8f01234abcd5678ef90",
    "64d2f8f01234abcd5678ef91",
    "64d2f8f01234abcd5678ef92"
  ],
  "task_id": "abc123xyz"
}
```

### Find Documents

Retrieve documents from a collection based on a filter:

```python
# Filter to match documents
filter_criteria = {
    "age": {"$gt": 25}
}

# Optional projection, sort, limit, and skip parameters
projection = {
    "name": 1,
    "age": 1,
    "_id": 0  # Exclude _id
}

sort = {
    "age": -1  # Sort by age in descending order
}

limit = 5
skip = 0

# Retrieve documents
response = collection.find(filter_criteria, projection, sort, limit, skip)

# Process the results
documents = response["docs"]
```

Response format:
```json
{
  "docs": [
    {
      "name": "Alice Smith",
      "age": 29
    },
    {
      "name": "Bob Johnson",
      "age": 40
    }
  ]
}
```

### Update Documents

Update existing documents in a collection based on a filter:

```python
# Filter to match documents to update
filter_criteria = {
    "name": "Alice Smith"
}

# Update operations to apply
update_operations = {
    "$set": {
        "age": 30,
        "email": "alice.smith@example.com"
    },
    "$inc": {
        "login_count": 1
    }
}

# Optional upsert parameter (default: False)
upsert = True

# Update documents
response = collection.update(filter_criteria, update_operations, upsert)

# Process the response
matched_count = response["matched_count"]
modified_count = response["modified_count"]
upserted_id = response.get("upserted_id")  # Will be None if no new document created
```

Response format:
```json
{
  "matched_count": 1,
  "modified_count": 1,
  "upserted_id": null
}
```

### Delete Documents

Remove documents from a collection based on a filter:

```python
# Filter to match documents to delete
filter_criteria = {
    "name": "Alice Smith"
}

# Delete documents
response = collection.delete(filter_criteria)

# Process the response
deleted_count = response["deleted_count"]
```

Response format:
```json
{
  "deleted_count": 1
}
```

### Query Documents

The `query` operation is similar to `find` but with additional functionality:

```python
# Query to find documents with age greater than 25
query = {
    "age": {"$gt": 25}
}

# Optional projection to include only specific fields
projection = {
    "name": 1,
    "age": 1,
    "_id": 0  # Exclude _id
}

# Optional sort order
sort = {
    "age": -1  # Sort by age in descending order
}

# Optional pagination parameters
limit = 5
skip = 0

# Perform query
response = collection.query(query, projection, sort, limit, skip)

# Process the results
documents = response["docs"]
```

## EmbJSON Features

CapybaraDB supports EmbJSON (CapybaraDB Extended JSON) which allows automatic embedding of text and images.

### EmbText

`EmbText` is used to embed text content for semantic search.

#### EmbText Basic Usage

```python
from capybaradb import EmbText

# Create a document with embedded text
document = {
    "title": "Example Document",
    "content": EmbText("This is an example document with embedded text that will be vectorized.")
}
```

#### EmbText Advanced Parameters

```python
from capybaradb import EmbText, EmbModels

# Create EmbText with custom parameters
document = {
    "field_name": EmbText(
        text="This is text to be embedded for semantic search...",
        emb_model=EmbModels.TEXT_EMBEDDING_3_LARGE,  # Change the default model
        max_chunk_size=200,                          # Configure chunk sizes
        chunk_overlap=20,                            # Overlap between chunks
        is_separator_regex=False,                    # Are separators plain strings or regex?
        separators=[
            "\\n\\n",
            "\\n",
        ],
        keep_separator=False,                        # Keep or remove the separator in chunks
    )
}
```

| Parameter | Description |
|-----------|-------------|
| `text` | The core content for `EmbText`. This text is automatically chunked and embedded for semantic search. |
| `emb_model` | Embedding model to use. Defaults to `text-embedding-3-small`. |
| `max_chunk_size` | Maximum character length of each chunk. |
| `chunk_overlap` | Overlapping character count between consecutive chunks. |
| `is_separator_regex` | Whether to treat each separator as a regular expression. |
| `separators` | A list of separator strings (or regex patterns) used to split the text. |
| `keep_separator` | If `True`, separators remain in the chunked text. |
| `chunks` | Auto-generated by the database after the text is processed. |

### EmbImage

`EmbImage` is used to embed image content for semantic search.

#### EmbImage Basic Usage

```python
from capybaradb import EmbImage

# Create a document with embedded image
document = {
    "title": "Example Image Document",
    "image": EmbImage("https://example.com/image.jpg", mime_type="image/jpeg")
}
```

#### EmbImage Advanced Parameters

```python
from capybaradb import EmbImage, EmbModels, VisionModels

# Create EmbImage with custom parameters
document = {
    "field_name": EmbImage(
        url="https://example.com/image.jpg",  # URL to the image
        mime_type="image/jpeg",                # Required: specify the image format
        emb_model=EmbModels.TEXT_EMBEDDING_3_LARGE,  # Optionally specify an embedding model
        vision_model=VisionModels.GPT_4O,             # Optionally specify a vision model
        max_chunk_size=200,                           # Configure chunk sizes
        chunk_overlap=20,                             # Overlap between chunks
        is_separator_regex=False,                     # Are separators plain strings or regex?
        separators=[
            "\\n\\n",
            "\\n",
        ],
        keep_separator=False                          # Keep or remove the separator in chunks
    )
}
```

| Parameter | Description |
|-----------|-------------|
| `url` | The URL to the image. |
| `mime_type` | The MIME type of the image (required). |
| `emb_model` | Embedding model to use (optional). |
| `vision_model` | Vision model to use for processing the image (optional). |
| `max_chunk_size` | Maximum size for each chunk. |
| `chunk_overlap` | Overlapping size between consecutive chunks. |
| `is_separator_regex` | Whether to treat each separator as a regular expression. |
| `separators` | A list of separator strings (or regex patterns). |
| `keep_separator` | If `True`, separators remain in the processed data. |
| `chunks` | Auto-generated by the database after processing the image. |

## Semantic Search

Perform semantic searches on embedded text:

```python
# Semantic search parameters
data = {
    "query": "How to implement vector search?",
    "embedding_model": "text-embedding-3-small",
    "top_k": 5,
    "include_values": True
}

# Perform semantic search
response = collection.query(**data)

# Process the matches
matches = response["matches"]
for match in matches:
    print(f"Score: {match['score']}")
    print(f"Matching text: {match['chunk']}")
    print(f"Document ID: {match['document']['_id']}")
```

## Reference

### Constants

The SDK provides various constants for embedding models and vision models.

### Enumerations

#### EmbModels

Enumeration of supported embedding models:

```python
from capybaradb import EmbModels

# Available embedding models
EmbModels.TEXT_EMBEDDING_3_SMALL  # "text-embedding-3-small"
EmbModels.TEXT_EMBEDDING_3_LARGE  # "text-embedding-3-large"
EmbModels.TEXT_EMBEDDING_ADA_002  # "text-embedding-ada-002"
```

#### VisionModels

Enumeration of supported vision models:

```python
from capybaradb import VisionModels

# Available vision models
VisionModels.GPT_4O_MINI   # "gpt-4o-mini"
VisionModels.GPT_4O        # "gpt-4o"
VisionModels.GPT_4O_TURBO  # "gpt-4o-turbo"
VisionModels.GPT_O1        # "gpt-o1"
``` 