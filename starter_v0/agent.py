from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from providers.base import Provider, ToolCall
from write_safety import WRITE_TOOLS, invoke_tool


@dataclass
class AgentRun:
    text: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)


class ResearchAgent:
    def __init__(
        self,
        provider: Provider,
        *,
        system_prompt: str,
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
    ) -> None:
        self.provider = provider
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model = model

    def run(
        self,
        user_messages: list[dict[str, str]],
        *,
        tool_choice: Any | None = None,
        write_authorizer: Callable[[ToolCall], bool] | None = None,
    ) -> AgentRun:
        messages = [{"role": "system", "content": self.system_prompt}, *user_messages]
        response = self.provider.complete(
            messages,
            self.tools,
            model=self.model,
            temperature=0.0,
            tool_choice=tool_choice,
        )
        results: list[dict[str, Any]] = []
        for call in response.tool_calls:
            host_approved = bool(write_authorizer and write_authorizer(call)) if call.name in WRITE_TOOLS else False
            actual_args, result = invoke_tool(call.name, call.args, host_approved_write=host_approved)
            if result.get("error") == "unknown_tool":
                results.append({"tool": call.name, "error": "unknown_tool"})
                continue
            results.append({"tool": call.name, "args": actual_args, "result": result})
        return AgentRun(text=response.text, tool_calls=response.tool_calls, tool_results=results)
