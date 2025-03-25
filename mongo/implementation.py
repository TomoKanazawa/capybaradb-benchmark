from typing import Any
from pymongo import MongoClient, UpdateOne

def ingest_document(
    document: dict,
    searchable_fields: list[str],
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    separator: str = " ",
    embedding_model: Any = None
) -> None:
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['rag_benchmark']
    collection = db['documents']
    collection.create_index([("doc_id", 1), ("chunk_id", 1)], unique=True)

    def chunk_text(text: str) -> list[str]:
        words = text.split(separator)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_len = len(word)
            if current_length + word_len + 1 <= chunk_size:
                current_chunk.append(word)
                current_length += word_len + 1
            else:
                if current_chunk:
                    chunks.append(separator.join(current_chunk))
                current_chunk = [word]
                current_length = word_len + 1
        
        if current_chunk:
            chunks.append(separator.join(current_chunk))
        
        # Add overlapping chunks
        if chunk_overlap > 0 and len(chunks) > 1:
            overlapped_chunks = []
            for i, chunk in enumerate(chunks):
                if i > 0:
                    prev_chunk = chunks[i-1]
                    overlap_words = prev_chunk.split(separator)[-chunk_overlap:]
                    chunk = separator.join(overlap_words + chunk.split(separator))
                overlapped_chunks.append(chunk)
            return overlapped_chunks
            
        return chunks

    def extract_field_content(obj, field_parts):
        current = obj
        for part in field_parts:
            if not current:
                return ''
            
            if part == '*':
                if isinstance(current, list):
                    new_current = []
                    for item in current:
                        if isinstance(item, dict):
                            new_current.extend(item.values())
                        else:
                            new_current.append(item)
                    current = new_current
                continue
                
            if isinstance(current, dict):
                current = current.get(part, '')
            elif isinstance(current, list):
                current = ' '.join(str(item.get(part, '')) if isinstance(item, dict) else str(item) 
                                  for item in current if item)
        
        return str(current) if current else ''

    doc_id = document.get("id", str(document))
    bulk_operations = []

    for field in searchable_fields:
        content = extract_field_content(document, field.split('.'))
        if not content:
            continue

        chunks = chunk_text(content)
        
        bulk_operations.extend([
            UpdateOne(
                {"doc_id": doc_id, "chunk_id": f"{field}_chunk_{i+1}"},
                {"$set": {
                    "doc_id": doc_id,
                    "chunk_id": f"{field}_chunk_{i+1}",
                    "field": field,
                    "chunk_index": i + 1,
                    "text": chunk,
                    "embedding": embedding_model.embed_text(chunk) if embedding_model else None,
                    "metadata": {
                        "total_chunks": len(chunks),
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap
                    }
                }},
                upsert=True
            ) for i, chunk in enumerate(chunks)
        ])

    if bulk_operations:
        collection.bulk_write(bulk_operations)
