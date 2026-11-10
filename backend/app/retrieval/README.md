# backend/app/retrieval/

Repository context for agents.

- `ingestion/`: load repository documents (e.g. `SECURITY.md`, policies, architecture docs), split them into chunks and attach metadata such as file paths.
- `search/`: retrieve relevant chunks for a query. Sprint 1 uses keyword search; hybrid and vector search come later.

Every result must include a file-path reference so findings can cite their evidence.

**Primary owners:** Yug + Nana (#4)

> **TODO (Sprint 1, Yug + Nana, #4: "Prototype Repository Context Ingestion and Retrieval"):** ingest a sample repository, add keyword retrieval with file-path references, and provide a reproducible demo.
