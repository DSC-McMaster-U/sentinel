# backend/app/retrieval/

Repository context for agents.

- `ingestion/`: load repository documents (e.g. `SECURITY.md`, policies, architecture docs), split them into chunks and attach metadata such as file paths.
- `search/`: retrieve relevant chunks for a query. Sprint 1 uses keyword search; hybrid and vector search come later.

Every result must include a file-path reference so findings can cite their evidence.

**Primary owners:** Yug + Nana (#4)

> **TODO (Sprint 1, Yug + Nana, #4: "Prototype Repository Context Ingestion and Retrieval"):** ingest a sample repository, add keyword retrieval with file-path references, and provide a reproducible demo.

## Ingestion prototype

Run from `backend/` (Python 3.10+, no runtime dependencies):

```python
from app.retrieval.ingestion import ingest_repository

result = ingest_repository("tests/fixtures/sample-repo")
for chunk in result.chunks:
    print(f"{chunk.file_path}:{chunk.line_start}-{chunk.line_end} [{chunk.kind}]")
    print(chunk.content)
for skipped in result.skipped_files:
    print(f"Skipped {skipped.file_path}: {skipped.reason}")
```

The fixture's `SECURITY.md:1-4` includes the signing policy relevant to
“How must release artifacts be protected?” This demonstrates the source material
available to search; query ranking is in `search/` (below) and the LangGraph adapter is in `adapter.py`
(see "LangGraph retrieval adapter"). The fixture workflow is data, not an active
GitHub Actions workflow.

### Search handoff

`ingest_repository(root, *, chunk_lines=80, max_file_bytes=1_048_576)` returns an
immutable `IngestionResult`. Its `chunks` tuple contains `RepositoryChunk` values:

- `file_path`: repository-relative POSIX path, suitable for `Evidence.file_path`.
- `line_start`, `line_end`: inclusive, one-based source line references.
- `content`: original text with normalized newlines and an optional UTF-8 BOM removed.
- `kind`: `documentation`, `dependency`, `workflow`, or `configuration`.

Search can index `chunk.content` and carry the remaining fields unchanged into
results. Use `dataclasses.asdict(chunk)` when a dictionary is needed. These are
retrieval-local records, not additions to the shared schemas. Blank chunks are
omitted; chunks otherwise retain blank lines so references match the source.
Results are sorted by source path and line number for repeatable indexing.
`skipped_files` records selected files that could not be read, with a reason.
Invalid roots and invalid limits raise exceptions rather than returning an empty
success result.

### Selected sources and limits

The allowlist includes Markdown/reStructuredText docs, common Python/Node/Rust/Go/
Ruby/Java/PHP manifests and lockfiles, `.github/workflows/*.yml`/`*.yaml`, Docker and
Compose files, Make/Just/Jenkins files, GitLab CI, Terraform, TOML, INI and CFG files.
See `ingestion/pipeline.py` for the exact selection rules. Nested repositories and
monorepos use the same rules. Dependency/vendor directories, VCS internals, common
caches and build outputs are pruned; symlink files and directories are not followed.
Environment files and private key extensions are excluded.

- Only local UTF-8 text is supported. Files over the byte limit, binary content,
  unreadable files and invalid UTF-8 are skipped; empty files produce no chunks.
- Parsing preserves text rather than executing code or interpreting JSON/YAML/TOML.
  Malformed configurations can still provide useful evidence. Semantic extraction,
  token-aware chunks, overlap and vector/hybrid retrieval are future improvements.
- There is no clone/download, persistence, query ranking, API tool, or workflow
  integration in this portion. General source code and arbitrary YAML/JSON files
  are not selected yet. `.gitignore` is not interpreted; exclusions are explicit.
- This is not secret detection or redaction: selected documentation/configuration
  can contain sensitive data. It does not execute repository content. Scan a stable
  local checkout; concurrent hostile filesystem changes are outside this prototype.
- Limits apply per file, not to total repository size or chunk count. Large lockfiles
  can be skipped under the default 1 MiB cap; callers can adjust it explicitly.

Run the ingestion tests from `backend/`:

```bash
python -m pytest tests/unit/test_retrieval_ingestion.py -q
```

## Keyword search prototype

BM25 keyword retrieval over the ingested chunks, standard library only. From `backend/`:

```python
from app.retrieval.search import search_repository

for r in search_repository("tests/fixtures/sample-repo", "How must release artifacts be protected?"):
    print(f"{r.file_path}:{r.line_start}-{r.line_end} [{r.kind}] score={r.score}")
```

The top hit is `SECURITY.md:1-4` ("Release artifacts must be signed before publication").

- `search_repository(root, query, limit=5, *, kinds=None)`: ingest, index and search in one call.
- `KeywordIndex(chunks).search(query, limit=5, *, kinds=None)`: build the index once and reuse it.
  `kinds` limits results, e.g. `{"workflow"}` for the CI/CD agent or `{"dependency"}`.
- `SearchResult(file_path, line_start, line_end, content, kind, score)`: location fields match
  `Evidence` (inclusive, one-based) so a result can become finding evidence.
- Empty or all-stopword queries and queries with no matches return `[]`. Ties break by path then
  line, so output is repeatable. An invalid `limit` raises `ValueError`.

Run the tests from `backend/`:

```bash
python -m pytest tests/unit/test_retrieval.py -q
```

## LangGraph retrieval adapter

`adapter.py` lets workflow nodes ask for repository context. Send a `RetrievalRequest(query, limit, kinds)`
and receive a `RetrievalResponse` whose `RetrievalResult` items carry `file_path`, `line_start` and
`line_end` (usable as `Evidence`), plus `content`, `kind` and `score`.

```python
from app.retrieval.adapter import RetrievalAdapter, RetrievalRequest

adapter = RetrievalAdapter.from_repository("tests/fixtures/sample-repo")
response = adapter.retrieve(RetrievalRequest(query="release artifacts", kinds=["documentation"]))
```

`RetrievalAdapter(retriever)` accepts any object with `search(query, limit, *, kinds)`, so tests use a mock
retriever. It is not yet called from the graph; agents will receive it when real checks replace the placeholders.

```bash
python -m pytest tests/unit/test_retrieval_adapter.py -q
```

### Limitations

- Exact-term matching only: no stemming, synonyms or typo tolerance ("signing" does not match "signed").
- Identifiers are not split ("GITHUB_TOKEN" is one token, "release-artifacts" is two).
- The index is in memory and rebuilt per call; nothing is persisted.
- Chunks are fixed line windows, so a long file can dilute a match.
- Scores rank within one query and are not comparable across queries.

### Future RAG improvements

- Stemming and identifier splitting, then embeddings for semantic matches.
- Hybrid ranking that fuses BM25 with vector search, plus optional reranking.
- Structure-aware chunks (YAML jobs, Markdown headings) with overlap.
- Persisted indexes, and exposing retrieval as an MCP tool (#3).
