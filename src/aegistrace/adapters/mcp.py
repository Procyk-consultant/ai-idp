"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/adapters/mcp.py
Purpose: MCP (Model Context Protocol) adapter stub for AI-IDP trace events
Classification: adapter
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.

NOTE: This adapter implements the protocol surface required for evidence
collection from MCP tool invocations. Live integration with a production
MCP server is a documented future work item.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MCPCall:
    server: str
    tool: str
    arguments: dict[str, Any]
    result: dict[str, Any] | None
    error: str | None


class MCPAdapter:
    """Records MCP tool invocations as AegisTrace-compatible records."""

    def __init__(self) -> None:
        self.calls: list[MCPCall] = []

    def record_call(
        self,
        *,
        server: str,
        tool: str,
        arguments: dict[str, Any],
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> MCPCall:
        call = MCPCall(server=server, tool=tool, arguments=arguments, result=result, error=error)
        self.calls.append(call)
        return call

    def all_calls(self) -> list[MCPCall]:
        return list(self.calls)


__all__ = ["MCPAdapter", "MCPCall"]
