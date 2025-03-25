import chromadb
from typing import Any, Dict, List, Union

def ingest_document(
    document: dict,
    searchable_fields: list[str],
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    separator: str = " ",
    embedding_model: Any = None
) -> None:
    """
    Split each searchable field's text into overlapping chunks using `separator`, 
    assign each chunk a unique identifier, embed with `embedding_model`, 
    and save to the target database without duplicates.
    """
    # Initialize ChromaDB client and get/create collection
    client = chromadb.Client()
    collection = client.get_or_create_collection(
        name=f"doc_{document['id']}_collection",
        embedding_function=embedding_model
    )
    
    # Extract text from nested fields using the searchable_fields patterns
    chunks_data = []
    
    def extract_field_value(obj: Union[Dict, List], path: List[str], current_path: str = "") -> List[tuple]:
        if not path:
            return []
        
        current, remaining = path[0], path[1:]
        
        if current == "*" and isinstance(obj, list):
            results = []
            for i, item in enumerate(obj):
                new_path = f"{current_path}[{i}]" if current_path else f"[{i}]"
                results.extend(extract_field_value(item, remaining, new_path))
            return results
        
        if isinstance(obj, dict):
            if not remaining and current in obj:
                value = obj[current]
                if isinstance(value, (str, list)):
                    if isinstance(value, list):
                        value = separator.join(str(v) for v in value)
                    return [(f"{current_path}.{current}" if current_path else current, value)]
            elif current in obj:
                new_path = f"{current_path}.{current}" if current_path else current
                return extract_field_value(obj[current], remaining, new_path)
        return []

    def create_chunk(text, field_path, chunk_index):
        return {
            "id": f"{document['id']}_{field_path}_chunk_{chunk_index}",
            "text": text,
            "metadata": {
                "document_id": document["id"],
                "field": field_path,
                "chunk_index": chunk_index
            }
        }

    # Process each searchable field pattern
    for field_pattern in searchable_fields:
        path = field_pattern.split(".")
        for field_path, text in extract_field_value(document, path):
            # Split text into chunks with overlap
            words = text.split(separator)
            current_chunk = []
            current_length = 0
            chunk_index = 0
            
            for word in words:
                word_length = len(word) + (len(separator) if current_chunk else 0)
                
                if current_length + word_length > chunk_size and current_chunk:
                    # Store current chunk
                    chunks_data.append(create_chunk(
                        separator.join(current_chunk), 
                        field_path, 
                        chunk_index
                    ))
                    chunk_index += 1
                    
                    # Handle overlap - keep words that fit within overlap size
                    overlap_words = []
                    overlap_length = 0
                    for w in reversed(current_chunk):
                        w_len = len(w) + len(separator)
                        if overlap_length + w_len > chunk_overlap:
                            break
                        overlap_words.insert(0, w)
                        overlap_length += w_len
                    
                    current_chunk = overlap_words
                    current_length = overlap_length
                
                current_chunk.append(word)
                current_length += word_length
            
            # Handle last chunk if any content remains
            if current_chunk:
                chunks_data.append(create_chunk(
                    separator.join(current_chunk),
                    field_path,
                    chunk_index
                ))
    
    # Batch upsert chunks to avoid duplicates
    if chunks_data:
        collection.upsert(
            ids=[chunk["id"] for chunk in chunks_data],
            documents=[chunk["text"] for chunk in chunks_data],
            metadatas=[chunk["metadata"] for chunk in chunks_data]
        )
