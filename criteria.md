We are designing a Document‑Ingestion Benchmark for RAG Databases, focused exclusively on measuring the ease of writing a single ingestion function that:
	1.	Accepts a structured JSON document
	2.	Splits specified text fields into sequential chunks (with configurable size, overlap, and separator)
	3.	Assigns each chunk a unique identifier (e.g., "chunk 5 of field 'body'")
	4.	Embeds those chunks using a chosen embedding model
	5.	Saves them into a target datastore without duplication
	6.	Indexes only selected fields for semantic search

Our metric of "ease of implementation" remains the number of non‑blank, non‑comment lines of code required inside the function body.

⸻

Benchmark Structure
	•	Task: Implement a single `ingest_document` function for different target databases to evaluate their usability.
	•	Function Prototype: The function, ingest_document, with six arguments:
	•	document: dict — the JSON object to store
	•	searchable_fields: list[str] — top‑level keys to index
	•	chunk_size: int — maximum characters per chunk
	•	chunk_overlap: int — number of overlapping characters between adjacent chunks
	•	separator: str — delimiter used to split text before chunking
	•	embedding_model: Any — an instantiated embedding model
	•	Provided Data: Each implementation uses the same set of sample documents and searchable fields for fair comparison.
	•	Modification Constraints: Implementers may only edit inside the body of ingest_document. No new top‑level definitions allowed.
	•	Deduplication Requirement: Must avoid inserting duplicate chunks if the same document is ingested multiple times.
	•	Chunk Identification: Each stored chunk must include metadata indicating its parent field name and chunk index (e.g., "body_chunk_5").
	•	Line‑Count Metric: Only non‑blank, non‑comment lines within ingest_document count.

⸻

Implementation Format

The implementation for each target database should be placed in its own directory with the database name. Each implementation should contain the ingest_document function with the same signature.

⸻

Example Implementation

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
    # Your implementation starts here

    # Your implementation ends here



⸻

Deliverables
	1.	Multiple implementations of the ingest_document function for different target databases
	2.	Scoring sheet - recording the line count for each database implementation

This benchmark objectively compares how concise and ergonomic it is to ingest, chunk (with overlap), embed, deduplicate, identify, and semantically index JSON documents across different RAG‑compatible datastores.