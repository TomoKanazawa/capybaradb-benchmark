import psycopg2
from pgvector.psycopg2 import register_vector
from typing import Any, Dict, List
import json

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
    with psycopg2.connect("postgresql://localhost/vector_db") as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            # Create table and index if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id serial PRIMARY KEY,
                    doc_id text,
                    field_name text,
                    chunk_index integer,
                    chunk_text text,
                    embedding vector(384),
                    metadata jsonb,
                    UNIQUE (doc_id, field_name, chunk_index)
                )
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
                ON document_chunks 
                USING hnsw (embedding vector_cosine_ops)
            """)

            # Process each searchable field
            doc_id = document.get("id", str(hash(json.dumps(document, sort_keys=True))))
            
            for field in searchable_fields:
                field_value = get_field_value(document, field)
                if field_value is None:
                    continue
                    
                # Handle nested fields with wildcards
                texts = flatten_list([field_value] if not isinstance(field_value, list) else field_value)
                
                for text in texts:
                    if not text:
                        continue
                        
                    chunks = create_chunks(text, chunk_size, chunk_overlap, separator)
                    
                    for i, chunk in enumerate(chunks):
                        # Generate chunk embedding
                        embedding = embedding_model.embed_text(chunk)
                        
                        # Store chunk with metadata
                        try:
                            cur.execute("""
                                INSERT INTO document_chunks 
                                (doc_id, field_name, chunk_index, chunk_text, embedding, metadata)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (doc_id, field_name, chunk_index) DO UPDATE
                                SET chunk_text = EXCLUDED.chunk_text,
                                    embedding = EXCLUDED.embedding,
                                    metadata = EXCLUDED.metadata
                            """, (
                                doc_id,
                                field,
                                i,
                                chunk,
                                embedding,
                                json.dumps({"document": document})
                            ))
                        except psycopg2.Error as e:
                            print(f"Error inserting chunk: {e}")

def get_field_value(doc: Dict, field_path: str) -> Any:
    parts = field_path.split(".")
    current = doc
    for part in parts:
        if part == "*":
            if isinstance(current, list):
                return [get_field_value(item, ".".join(parts[parts.index("*")+1:])) for item in current]
            return None
        elif isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current

def flatten_list(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        elif item is not None:
            result.append(str(item))
    return result

def create_chunks(text: str, chunk_size: int, overlap: int, sep: str) -> List[str]:
    words = text.split(sep)
    chunks = []
    start = 0
    
    while start < len(words):
        chunk = sep.join(words[start:])
        if len(chunk) <= chunk_size:
            chunks.append(chunk)
            break
            
        # Find the last separator within chunk_size
        end = start
        current_len = 0
        while end < len(words) and current_len + len(words[end]) + (1 if current_len > 0 else 0) <= chunk_size:
            current_len += len(words[end]) + (1 if current_len > 0 else 0)
            end += 1
            
        chunks.append(sep.join(words[start:end]))
        start = max(start, end - max(1, int(overlap / (len(sep) + sum(len(w) for w in words[end-1:end])))))
        
    return chunks
