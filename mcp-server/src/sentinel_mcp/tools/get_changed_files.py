from typing import Any

import httpx2
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel

from sentinel_mcp.app import AppContext, mcp
from sentinel_mcp.schema import ChangedFile


class ChangedFileResult(BaseModel):
    files: list[ChangedFile]


def validate_inputs(repository: str, pull_number: int) -> None:
    parts = repository.strip().split("/")
    if len(parts) != 2 or not all(parts):
        raise ToolError("repository must be in 'owner/repo' format")
    if pull_number < 1:
        raise ToolError("pull_number must be >= 1")

#already tested in backend
def _normalize_changed_file(raw_file: dict[str, Any]) -> ChangedFile:
    return ChangedFile(
        path=raw_file["filename"],
        status=raw_file["status"],
        additions=raw_file["additions"],
        deletions=raw_file["deletions"],
        patch=raw_file.get("patch"),
        previous_path=raw_file.get("previous_filename"),
    )


@mcp.tool()
async def get_changed_files(
    repository: str, pull_number: int, ctx: Context[AppContext]
) -> ChangedFileResult:
    """Return normalized changed files for a pull request ('owner/repo' format)."""

    validate_inputs(repository, pull_number)
    gh = ctx.request_context.lifespan_context.github

    # will consider switching to domain specific errors inside of the adapters instead of relying on httpx2 errors
    try:
        raw_files = await gh.get_pr_files(repository, pull_number)
    except httpx2.TimeoutException as ex:
        raise ToolError("github api request timed out.") from ex
    except httpx2.ConnectError as ex:
        raise ToolError("could not connect to github api.") from ex
    except httpx2.RequestError as ex:
        raise ToolError(f"gitHub api request failed: {ex}") from ex
    except httpx2.HTTPStatusError as ex:
        status = ex.response.status_code
        if status == 404:
            raise ToolError(
                f"pull request #{pull_number} in '{repository}' was not found"
            ) from ex
        if status in (401, 403):
            raise ToolError(
                f"github api rejected the request ({status}): check GITHUB_TOKEN or rate limits."
            ) from ex
        raise ToolError(f"github api returned http {status}.") from ex

    return ChangedFileResult(
        files=[_normalize_changed_file(item) for item in raw_files]
    )
