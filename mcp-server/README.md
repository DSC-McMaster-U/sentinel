# mcp-server/

The Sentinel MCP server, built with the Model Context Protocol Python SDK. It gives agents structured, read-only tools for inspecting repositories and security data.

| Path                         | What goes here                                                                          |
| ---------------------------- | --------------------------------------------------------------------------------------- |
| `src/sentinel_mcp/tools/`    | One module per MCP tool (e.g. `get_changed_files`, `get_dependency_changes`)            |
| `src/sentinel_mcp/adapters/` | Wrappers for external sources (GitHub API, package registries, vulnerability databases) |
| `tests/`                     | Tool and adapter tests                                                                  |

Tools should return **structured facts** (normalized JSON), not raw data for the model to interpret. Tools call adapters and never make raw HTTP calls themselves.

**Primary owners:** Toheeb + Parmeet (#3)

## Local Setup

From the repository root, create and activate a virtual environment if not created already, then install `mcp-server` in editable mode:

```bash
uv venv
source .venv/bin/activate
uv pip install -e "./mcp-server[dev]"
```

_(Issue #5 tracks the shared repository-wide dependency setup.)_

## Running Tests

From `mcp-server/` with your virtual environment active:

```bash
cd mcp-server
python -m pytest -v
```

All tests mock external HTTP calls with `httpx2.MockTransport` and fake adapters, so they run completely offline without a live server or `GITHUB_TOKEN`.

## Running the MCP Server Manually

From `mcp-server/` with your virtual environment active, launch the interactive MCP Inspector:

```bash
# Recommended (with uv):
uv run mcp dev src/sentinel_mcp/server.py

# Or without uv (using npx from npm ecosystem):
npx @modelcontextprotocol/inspector python src/sentinel_mcp/server.py
```

This starts the server and opens the MCP Inspector in your browser:

1. Toggle the server connection on under **Servers**.
2. Open the **Tools** tab to inspect schemas and run tools such as `get_changed_files`.

> **Note:** Public GitHub repositories work without authentication (subject to GitHub's unauthenticated rate limit). Set `GITHUB_TOKEN` in your environment for higher rate limits or private repositories.
