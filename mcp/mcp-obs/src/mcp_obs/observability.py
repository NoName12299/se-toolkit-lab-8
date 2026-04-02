"""VictoriaLogs and VictoriaTraces client for observability tools."""

from __future__ import annotations

import os
from dataclasses import dataclass

import httpx


@dataclass
class ObservabilitySettings:
    """Configuration for observability services."""
    victorialogs_url: str = "http://victorialogs:9428"
    victoriatraces_url: str = "http://victoriatraces:10428"


def resolve_settings() -> ObservabilitySettings:
    """Resolve settings from environment variables."""
    return ObservabilitySettings(
        victorialogs_url=os.getenv("NANOBOT_VICTORIALOGS_URL", "http://victorialogs:9428"),
        victoriatraces_url=os.getenv("NANOBOT_VICTORIATRACES_URL", "http://victoriatraces:10428"),
    )


class ObservabilityClient:
    """Client for querying VictoriaLogs and VictoriaTraces."""

    def __init__(self, settings: ObservabilitySettings | None = None):
        self.settings = settings or resolve_settings()
        self._http_client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def close(self) -> None:
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self) -> ObservabilityClient:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def logs_search(self, query: str, limit: int = 100) -> list[dict]:
        """Search VictoriaLogs using LogsQL query."""
        client = await self._get_client()
        url = f"{self.settings.victorialogs_url}/select/logsql/query"
        params = {"query": query, "limit": limit}
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def logs_error_count(self, service: str, minutes: int = 60) -> dict:
        """Count errors for a service over a time window."""
        client = await self._get_client()
        query = f'_time:{minutes}m service.name:"{service}" severity:ERROR'
        url = f"{self.settings.victorialogs_url}/select/logsql/query"
        params = {"query": query, "limit": 1000}
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return {"service": service, "error_count": len(data) if isinstance(data, list) else 0, "window_minutes": minutes}

    async def traces_list(self, service: str, limit: int = 20) -> list[dict]:
        """List recent traces for a service from VictoriaTraces."""
        client = await self._get_client()
        url = f"{self.settings.victoriatraces_url}/select/jaeger/api/traces"
        params = {"service": service, "limit": limit}
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data if isinstance(data, list) else []

    async def traces_get(self, trace_id: str) -> dict:
        """Fetch a specific trace by ID from VictoriaTraces."""
        client = await self._get_client()
        url = f"{self.settings.victoriatraces_url}/select/jaeger/api/traces/{trace_id}"
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data
