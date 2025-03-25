from typing import Any, List
import os

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
    # Helper function to get nested field value using dot notation
    def get_nested_value(obj: dict, path: str) -> Any:
        parts = path.split('.')
        current = obj
        for part in parts:
            if part == '*' and isinstance(current, list):
                return [get_nested_value(item, '.'.join(parts[parts.index('*')+1:])) 
                       for item in current]
            elif isinstance(current, dict):
                current = current.get(part, {})
            else:
                return None
        return current

    # Helper function to flatten nested lists
    def flatten(lst):
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(flatten(item))
            else:
                result.append(item)
        return result

    # Helper function to create overlapping chunks
    def create_chunks(text: str) -> List[str]:
        if not text:
            return []
        
        words = text.split(separator)
        if not words:
            return []

        chunk_words = chunk_size // (len(separator) + 1)  # Approximate words per chunk
        overlap_words = chunk_overlap // (len(separator) + 1)    # Approximate overlap in words
        
        chunks = []
        start = 0
        while start < len(words):
            chunks.append(separator.join(words[start:start + chunk_words]))
            start = start + chunk_words - overlap_words
            
        return chunks

    # Process each searchable field
    vectors_to_upsert = []
    doc_id = str(document.get('id', ''))

    for field_path in searchable_fields:
        field_values = get_nested_value(document, field_path)
        if not field_values:
            continue

        # Handle both single values and lists
        if not isinstance(field_values, list):
            field_values = [field_values]
        
        field_values = flatten(field_values)

        for value in field_values:
            if not isinstance(value, (str, int, float)):
                continue
                
            chunks = create_chunks(str(value))
            
            if embedding_model:
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_{field_path}_{i}"
                    metadata = {
                        'document_id': doc_id,
                        'field': field_path,
                        'chunk_index': i,
                        'text': chunk
                    }
                    vectors_to_upsert.append((chunk_id, embedding_model.embed_text(chunk), metadata))

    # Batch upsert to Pinecone (if we have vectors)
    if vectors_to_upsert:
        # Use standard import and initialize with API key
        from pinecone import Pinecone
        
        # Initialize Pinecone client (get API key from environment or use a placeholder)
        api_key = os.environ.get("PINECONE_API_KEY", "YOUR_API_KEY")
        pc = Pinecone(api_key=api_key)
        
        # Get the index
        index = pc.Index("default")
        
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            index.upsert(vectors=vectors_to_upsert[i:i + batch_size])
