# mcp-server/

The Sentinel MCP server, built with the Model Context Protocol Python SDK. It gives agents structured, read-only tools for inspecting repositories and security data.

| Path | What goes here |
| --- | --- |
| `src/sentinel_mcp/tools/` | One module per MCP tool (e.g. `get_changed_files`, `get_dependency_changes`) |
| `src/sentinel_mcp/adapters/` | Wrappers for external sources (GitHub API, package registries, vulnerability databases) |
| `tests/` | Tool and adapter tests |

Tools should return **structured facts** (normalized JSON), not raw data for the model to interpret. Tools call adapters and never make raw HTTP calls themselves.

**Primary owners:** Megh + Behzad

> **TODO (Sprint 1, Megh + Behzad: "Set Up FastAPI Backend and Initial MCP Tool Integration"):** one read-only repository/diff tool with tests, and packaging (`pyproject.toml`) for this server.
