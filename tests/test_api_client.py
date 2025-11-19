"""Smoke tests for the bot HTTP client."""
import asyncio

from httpx import MockTransport, Request, Response

from bot.api_client import ApiClient


def test_get_profile_smoke() -> None:
    """Ensure that ``get_profile`` hits the expected endpoint."""

    def handler(request: Request) -> Response:
        assert request.method == "GET"
        assert request.url.path == "/users/42"
        return Response(200, json={"username": "tester", "level": 1})

    async def run_test() -> None:
        transport = MockTransport(handler)
        client = ApiClient("http://example.com", transport=transport)
        try:
            data = await client.get_profile(42)
        finally:
            await client.close()
        assert data == {"username": "tester", "level": 1}

    asyncio.run(run_test())


def test_get_domains_uses_query_params() -> None:
    """The client forwards the ``telegram_id`` query parameter."""

    def handler(request: Request) -> Response:
        assert request.url.path == "/domains"
        assert request.url.params["telegram_id"] == "42"
        return Response(200, json=[{"title": "Health"}])

    async def run_test() -> None:
        transport = MockTransport(handler)
        client = ApiClient("http://example.com", transport=transport)
        try:
            domains = await client.get_domains(42)
        finally:
            await client.close()
        assert list(domains) == [{"title": "Health"}]

    asyncio.run(run_test())


def test_get_daily_logs_hits_endpoint() -> None:
    """Smoke test for ``/daily-logs`` endpoint."""

    def handler(request: Request) -> Response:
        assert request.url.path == "/daily-logs"
        assert request.url.params["telegram_id"] == "7"
        return Response(200, json=[{"date": "2024-01-01"}])

    async def run_test() -> None:
        transport = MockTransport(handler)
        client = ApiClient("http://example.com", transport=transport)
        try:
            logs = await client.get_daily_logs(7)
        finally:
            await client.close()
        assert list(logs) == [{"date": "2024-01-01"}]

    asyncio.run(run_test())


def test_get_finances_hits_endpoint() -> None:
    """Smoke test for ``/finances`` endpoint."""

    def handler(request: Request) -> Response:
        assert request.url.path == "/finances"
        assert request.url.params["telegram_id"] == "99"
        return Response(200, json=[{"amount": 100}])

    async def run_test() -> None:
        transport = MockTransport(handler)
        client = ApiClient("http://example.com", transport=transport)
        try:
            items = await client.get_finances(99)
        finally:
            await client.close()
        assert list(items) == [{"amount": 100}]

    asyncio.run(run_test())
