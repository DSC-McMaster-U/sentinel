from typing import Any, cast

import httpx2
import pytest
from mcp.server.context import ServerRequestContext
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.session import ServerSession
from mcp_types import CallToolResult
from sentinel_mcp.adapters.github import GitHubAdapter
from sentinel_mcp.app import AppContext, mcp
from sentinel_mcp.schema import FileChangeStatus
from sentinel_mcp.tools import get_changed_files
from sentinel_mcp.tools.get_changed_files import ChangedFileResult, validate_inputs


@pytest.fixture
def anyio_backend():
    return "asyncio"


class FakeGitHubAdapter:
    def __init__(self, response=None, error: Exception | None = None):
        self.response = response or []
        self.error = error
        self.calls: list[tuple[str, int]] = []

    async def get_pr_files(self, repo: str, pull_number: int):
        self.calls.append((repo, pull_number))
        if self.error is not None:
            raise self.error
        return self.response


def make_ctx(adapter: Any) -> Context[AppContext, Any]:
    req_ctx = ServerRequestContext(
        session=cast(ServerSession, None),
        lifespan_context=AppContext(github=cast(GitHubAdapter, adapter)),
        protocol_version="2025-11-25",
        method="tools/call",
    )
    return Context(request_context=req_ctx)


@pytest.mark.anyio
async def test_mcp_registers_get_changed_files():
    tools = await mcp.list_tools()
    assert any(tool.name == "get_changed_files" for tool in tools)


def test_validate_inputs_rejects_improper_inputs():
    try:
        with pytest.raises(ToolError, match="owner/repo"):
            validate_inputs("abc", 2)
        with pytest.raises(ToolError, match="pull_number"):
            validate_inputs("owner/repo", -1)
    finally:
        pass


@pytest.mark.anyio
async def test_get_changed_files_normalizes_files():
    fake_payload = [
        {
            "sha": "ignored",
            "filename": "abc/new.py",
            "previous_filename": "abc/old.py",
            "status": "renamed",
            "additions": 2,
            "deletions": 1,
        }
    ]

    fake_adapter = FakeGitHubAdapter(response=fake_payload)

    # act
    result = await get_changed_files("owner/repo", 2, make_ctx(fake_adapter))

    # assert
    assert isinstance(result, ChangedFileResult)
    assert fake_adapter.calls == [("owner/repo", 2)]
    assert len(result.files) == 1
    file = result.files[0]
    assert file.path == "abc/new.py"
    assert file.previous_path == "abc/old.py"
    assert file.status is FileChangeStatus.renamed
    assert file.patch is None


@pytest.mark.anyio
async def test_get_changed_files_via_mcp_call_tool():
    # arrange
    fake_adapter = FakeGitHubAdapter(
        response=[
            {
                "filename": "package.json",
                "status": "modified",
                "additions": 1,
                "deletions": 1,
                "patch": "@@ -1 +1 @@\n-old\n+new",
            }
        ]
    )

    # act
    res = await mcp.call_tool(
        "get_changed_files",
        {"repository": "DSC-McMaster-U/sentinel", "pull_number": 7},
        context=make_ctx(fake_adapter),
    )

    # assert
    assert isinstance(
        res, CallToolResult
    )  # mcp package allows has a tool result in a union which messes up types
    assert res.is_error is False
    assert res.structured_content == {
        "files": [
            {
                "path": "package.json",
                "status": "modified",
                "additions": 1,
                "deletions": 1,
                "patch": "@@ -1 +1 @@\n-old\n+new",
                "previous_path": None,
            }
        ]
    }


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("status_code", "expected_msg"),
    [
        (404, "not found"),
        (401, "GITHUB_TOKEN"),
        (403, "rate limits"),
        (500, "http 500"),
    ],
)

@pytest.mark.anyio
async def test_get_changed_files_maps_http_errors_to_tool_error(
    status_code, expected_msg
):
    request = httpx2.Request("GET", "https://api.github.com/repos/o/r/pulls/1/files")
    response = httpx2.Response(status_code, request=request)
    err = httpx2.HTTPStatusError("error", request=request, response=response)

    with pytest.raises(ToolError, match=expected_msg):
        await get_changed_files("o/r", 1, ctx=make_ctx(FakeGitHubAdapter(error=err)))
