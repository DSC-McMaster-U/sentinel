import os
from typing import Any

import httpx2


class GitHubAdapter:
    http_client: httpx2.AsyncClient

    def __init__(
        self,
        token: str | None = None,
        transport: httpx2.AsyncBaseTransport | None = None,
    ) -> None:
        resolved_token = token if token is not None else os.environ.get("GITHUB_TOKEN")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        }
        if resolved_token:
            headers["Authorization"] = f"Bearer {resolved_token}"

        self.http_client = httpx2.AsyncClient(
            headers=headers,
            timeout=15.0,
            base_url="https://api.github.com",
            transport=transport,
        )

    async def get_pr_files(self, repo: str, pull_number: int) -> list[dict[str, Any]]:
        res = await self.http_client.get(f"/repos/{repo}/pulls/{pull_number}/files")
        res.raise_for_status()
        return res.json()

    async def aclose(self) -> None:
        """Closes the async http client"""
        await self.http_client.aclose()
