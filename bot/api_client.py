"""HTTP client used by the Telegram bot to talk to the backend."""
from __future__ import annotations

from typing import Any, Iterable

import httpx


class ApiClientError(RuntimeError):
    """Raised when the backend responds with an error."""


class ApiClient:
    """A tiny wrapper above :class:`httpx.AsyncClient`."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            transport=transport,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = await self._client.request(method, url, params=params)
        except httpx.HTTPError as exc:  # pragma: no cover - network errors are rare in tests
            raise ApiClientError("Failed to talk to backend") from exc

        if response.status_code >= 400:
            raise ApiClientError(
                f"Backend responded with {response.status_code}: {response.text}"
            )

        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()

        return response.text

    async def get_profile(self, telegram_id: int) -> dict[str, Any]:
        """Return user profile by Telegram ID."""

        data = await self._request("GET", f"/users/{telegram_id}")
        if isinstance(data, dict):
            return data
        raise ApiClientError("Unexpected payload from /users endpoint")

    async def get_domains(self, telegram_id: int) -> Iterable[dict[str, Any]]:
        """Return a list of domains for the user."""

        data = await self._request("GET", "/domains", params={"telegram_id": telegram_id})
        if isinstance(data, list):
            return data
        raise ApiClientError("Unexpected payload from /domains endpoint")

    async def get_daily_logs(self, telegram_id: int) -> Iterable[dict[str, Any]]:
        """Return daily log entries for the user."""

        data = await self._request(
            "GET", "/daily-logs", params={"telegram_id": telegram_id}
        )
        if isinstance(data, list):
            return data
        raise ApiClientError("Unexpected payload from /daily-logs endpoint")

    async def get_finances(self, telegram_id: int) -> Iterable[dict[str, Any]]:
        """Return finance entries for the user."""

        data = await self._request("GET", "/finances", params={"telegram_id": telegram_id})
        if isinstance(data, list):
            return data
        raise ApiClientError("Unexpected payload from /finances endpoint")
