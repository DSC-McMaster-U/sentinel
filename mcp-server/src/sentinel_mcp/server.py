import sentinel_mcp.tools  # noqa: F401
from sentinel_mcp.app import AppContext, app_lifespan, mcp

__all__ = ["AppContext", "app_lifespan", "mcp"]

if __name__ == "__main__":
    mcp.run(transport="stdio")
