from capybaradb import CapybaraDB, EmbText
from typing import Any

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
    collection = CapybaraDB().db("benchmark_db").collection("documents")
    doc_copy = document.copy()
    
    def process_field(obj: dict, field_path: str) -> None:
        parts = field_path.split(".")
        current = obj
        
        for i, part in enumerate(parts):
            if part == "*" and isinstance(current, list):
                remaining_path = ".".join(parts[i+1:])
                if remaining_path:
                    for item in current:
                        process_field(item, remaining_path)
                return
            elif i == len(parts) - 1:
                if part in current and isinstance(current[part], str):
                    current[part] = EmbText(
                        text=current[part],
                        emb_model=embedding_model,
                        max_chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        separators=[separator],
                        is_separator_regex=False,
                        keep_separator=True
                    )
            else:
                if part in current:
                    current = current[part]
                else:
                    return

    for field in searchable_fields:
        process_field(doc_copy, field)
    
    collection.insert([doc_copy])
