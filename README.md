# CapybaraDB Benchmark

A straightforward benchmark designed to compare how easy it is to implement document ingestion for Retrieval‑Augmented Generation (RAG) across a variety of vector databases and libraries.

## Purpose

This project quantifies the conciseness and ergonomics of writing a single, standardized document‑ingestion function for different RAG‑compatible datastores. Its goal is to help developers select the most developer‑friendly solution for their RAG pipelines.

## Repository Structure

- Each datastore's implementation lives in its own directory (for example: `capybaradb/`, `chroma/`, `langchain/`, etc.).
- Every implementation exposes a single function called `ingest_document`, sharing an identical signature.
- `prototypes.py` provides sample documents and field‑pattern definitions.
- `line_counter.py` measures the number of non‑blank, non‑comment lines of code within the function body.
- `test_ingest.py` contains tests that validate each implementation.

## ingest_document Function Requirements

Each implementation must:

1. Accept a structured JSON document  
2. Split designated text fields into sequential chunks  
3. Assign each chunk a unique identifier  
4. Embed chunks using a supplied embedding model  
5. Persist chunks to the datastore without duplicating existing entries  
6. Index only the specified fields for semantic search  

## Measurement Methodology

We use **non‑blank, non‑comment lines of code** inside the `ingest_document` function as a proxy for implementation simplicity. Although developer experience is subjective, line count provides an objective, repeatable metric.

Our rationale:

1. A single, generalized function reflects real‑world ingestion needs.  
2. More lines typically correlate with more boilerplate and maintenance overhead.  
3. Fewer lines indicate a more concise API, which often translates to easier customization and refactoring.

## Running Tests

```bash
python test_ingest.py
```

## Measuring Complexity

- Single implementation:

```bash
python line_counter.py <path/to/implementation_file.py>
```

- All implementations at once:

```bash
python count_all_files.py
```

Results will be written to line_count_results.txt.

## Current Implementations

- CapybaraDB
- ChromaDB
- LangChain
- MongoDB
- pgvector
- Pinecone

## Scope & Limitations

This benchmark exclusively measures ingestion‑and‑storage ergonomics. It does not evaluate query performance, search accuracy, scalability, or other runtime characteristics. While developer experience is a critical factor in choosing a RAG solution, it should be balanced against other metrics relevant to your use case.

Future plans include expanding the benchmark to cover additional dimensions. Contributions and feedback are very welcome!