import sentinel_mcp.tools  # noqa: E402, F401
from sentinel_mcp.app import AppContext, app_lifespan, mcp

__all__ = ["AppContext", "mcp", "app_lifespan"]

if __name__ == "__main__":
    mcp.run(transport="stdio")
