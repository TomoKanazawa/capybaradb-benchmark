from typing import Any, Dict, List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.vectorstores import Chroma

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
    # Extract searchable content from document based on field patterns
    chunks = []
    doc_id = document.get("id", "")
    
    def extract_field_value(obj: Dict, path: List[str], current_path: List[str] = None) -> List[str]:
        if current_path is None:
            current_path = []
            
        if not path:
            return [str(obj)]
            
        current = path[0]
        remaining = path[1:]
        
        if current == "*":
            if isinstance(obj, list):
                results = []
                for i, item in enumerate(obj):
                    new_path = current_path + [str(i)]
                    results.extend(extract_field_value(item, remaining, new_path))
                return results
            return []
            
        if isinstance(obj, dict) and current in obj:
            new_path = current_path + [current]
            return extract_field_value(obj[current], remaining, new_path)
            
        return []

    # Process each searchable field pattern
    for field_pattern in searchable_fields:
        path = field_pattern.split(".")
        values = extract_field_value(document, path)
        
        for value in values:
            if not value:
                continue
                
            # Create text splitter with specified parameters
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=[separator]
            )
            
            # Split text into chunks
            split_texts = text_splitter.split_text(value)
            
            # Create Document objects with metadata
            for i, text in enumerate(split_texts):
                chunk_id = f"{doc_id}_{field_pattern}_{i+1}"
                chunks.append(
                    Document(
                        page_content=text,
                        metadata={
                            "doc_id": doc_id,
                            "field": field_pattern,
                            "chunk_index": i + 1,
                            "chunk_id": chunk_id
                        }
                    )
                )

    # Create or update vector store with chunks
    if chunks:
        # Use a persistent directory based on document ID to enable deduplication
        persist_directory = f"vectorstore_{doc_id}"
        
        # Create or update vector store
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embedding_model,
            persist_directory=persist_directory,
            ids=[chunk.metadata["chunk_id"] for chunk in chunks]  # Use chunk_id for deduplication
        )
        vectorstore.persist()
