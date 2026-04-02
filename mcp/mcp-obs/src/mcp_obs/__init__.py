"""MCP observability server for VictoriaLogs and VictoriaTraces."""

from mcp_obs.server import create_server, main
from mcp_obs.observability import ObservabilityClient
from mcp_obs.tools import TOOL_SPECS, TOOLS_BY_NAME

__all__ = [
    "create_server",
    "main",
    "ObservabilityClient",
    "TOOL_SPECS",
    "TOOLS_BY_NAME",
]
