"""Tool schemas, handlers, and registry for the observability MCP server."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_obs.observability import ObservabilityClient


class NoArgs(BaseModel):
    """Empty input model for tools that only need server-side configuration."""


class LogsSearchQuery(BaseModel):
    query: str = Field(description="LogsQL query, e.g. '_time:10m service.name:\"backend\" severity:ERROR'")
    limit: int = Field(default=100, ge=1, le=1000, description="Max results to return (1-1000)")


class LogsErrorCountQuery(BaseModel):
    service: str = Field(description="Service name, e.g. 'Learning Management Service'")
    minutes: int = Field(default=60, ge=1, le=1440, description="Time window in minutes (default 60)")


class TracesListQuery(BaseModel):
    service: str = Field(description="Service name to filter traces")
    limit: int = Field(default=20, ge=1, le=100, description="Max traces to return (1-100)")


class TracesGetQuery(BaseModel):
    trace_id: str = Field(description="Trace ID to fetch")


ToolPayload = BaseModel | list | dict
ToolHandler = Callable[[ObservabilityClient, BaseModel], Awaitable[ToolPayload]]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    model: type[BaseModel]
    handler: ToolHandler

    def as_tool(self) -> Tool:
        schema = self.model.model_json_schema()
        schema.pop("$defs", None)
        schema.pop("title", None)
        return Tool(name=self.name, description=self.description, inputSchema=schema)


async def _logs_search(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    query = args if isinstance(args, LogsSearchQuery) else LogsSearchQuery.model_validate(args)
    return await client.logs_search(query.query, query.limit)


async def _logs_error_count(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    query = args if isinstance(args, LogsErrorCountQuery) else LogsErrorCountQuery.model_validate(args)
    return await client.logs_error_count(query.service, query.minutes)


async def _traces_list(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    query = args if isinstance(args, TracesListQuery) else TracesListQuery.model_validate(args)
    return await client.traces_list(query.service, query.limit)


async def _traces_get(client: ObservabilityClient, args: BaseModel) -> ToolPayload:
    query = args if isinstance(args, TracesGetQuery) else TracesGetQuery.model_validate(args)
    return await client.traces_get(query.trace_id)


TOOL_SPECS = (
    ToolSpec(
        "obs_logs_search",
        "Search VictoriaLogs using LogsQL. Use for finding errors, debugging issues, or exploring logs.",
        LogsSearchQuery,
        _logs_search,
    ),
    ToolSpec(
        "obs_logs_error_count",
        "Count errors for a service over a time window. Quick way to check if there are recent errors.",
        LogsErrorCountQuery,
        _logs_error_count,
    ),
    ToolSpec(
        "obs_traces_list",
        "List recent traces for a service from VictoriaTraces. Use to find traces for debugging.",
        TracesListQuery,
        _traces_list,
    ),
    ToolSpec(
        "obs_traces_get",
        "Fetch a specific trace by ID. Use trace_id from logs or traces_list to inspect full request flow.",
        TracesGetQuery,
        _traces_get,
    ),
)
TOOLS_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}
