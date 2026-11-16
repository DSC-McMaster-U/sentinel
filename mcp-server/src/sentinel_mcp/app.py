from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from mcp.server import MCPServer

from sentinel_mcp.adapters.github import GitHubAdapter


@dataclass
class AppContext:
    github: GitHubAdapter


@asynccontextmanager
async def app_lifespan(
    server: MCPServer[AppContext],
) -> AsyncIterator[AppContext]:
    github = GitHubAdapter()
    try:
        yield AppContext(github=github)
    finally:
        await github.aclose()


mcp = MCPServer("sentinel-mcp", lifespan=app_lifespan)
