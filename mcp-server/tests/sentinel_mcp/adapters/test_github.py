import httpx2
import pytest
from sentinel_mcp.adapters import GitHubAdapter


@pytest.fixture
def anyio_backend():
    return "asyncio"


def test_get_pr_files_uses_token_from_env(monkeypatch):
    # arrange
    fake_token = "fake-token"
    monkeypatch.setenv("GITHUB_TOKEN", fake_token)

    # act
    adapter = GitHubAdapter()
    # assert
    assert adapter.http_client.headers["Authorization"] == f"Bearer {fake_token}"


@pytest.mark.anyio
async def test_get_pr_files_sends_expected_request_and_returns_json(monkeypatch):
    # arrange
    captured: list[httpx2.Request] = []
    fake_payload = [
        {
            "filename": "package.json",
            "status": "modified",
            "additions": 1,
            "deletions": 1,
            "patch": '@@ -1 +1 @@\n- "a": "1"\n+ "a": "2"',
        }
    ]
    fake_repo = "johnny/test"

    def handler(request: httpx2.Request) -> httpx2.Response:
        captured.append(request)
        # forcing the payload response into the http response
        return httpx2.Response(200, json=fake_payload)

    transport = httpx2.MockTransport(handler)
    adapter = GitHubAdapter(token="", transport=transport)

    # act
    try:
        files = await adapter.get_pr_files(fake_repo, 1)
    finally:
        await adapter.aclose()

    # assert
    assert files == fake_payload
    assert len(captured) == 1

    req = captured[0]
    assert req.method == "GET"
    assert (
        str(req.url)
        == f"https://api.github.com/repos/{fake_repo}/pulls/1/files"
    )
    assert req.headers["Accept"] == "application/vnd.github+json"
    assert "Authorization" not in req.headers  # since token=""


@pytest.mark.anyio
async def test_get_pr_files_raises_http_status_error_on_404():
    # arrange
    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(404, json={"message": "Not Found"})

    adapter = GitHubAdapter(token="", transport=httpx2.MockTransport(handler))

    # act
    try:
        with pytest.raises(httpx2.HTTPStatusError) as exc_info:
            await adapter.get_pr_files("DSC-McMaster-U/sentinel", 999)
        assert exc_info.value.response.status_code == 404
    finally:
        await adapter.aclose()


@pytest.mark.anyio
async def test_get_pr_files_propagates_timeout():
    # arrange
    def handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ReadTimeout("timed out", request=request)

    adapter = GitHubAdapter(token="", transport=httpx2.MockTransport(handler))

    # act
    try:
        with pytest.raises(httpx2.TimeoutException):
            await adapter.get_pr_files("DSC-McMaster-U/sentinel", 42)
    finally:
        await adapter.aclose()
