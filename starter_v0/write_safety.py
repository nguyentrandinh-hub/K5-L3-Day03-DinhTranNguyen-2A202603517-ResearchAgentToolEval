"""Host-side approval checks for tools with external write effects."""
from __future__ import annotations

import re
from typing import Any

from tools import TOOL_FUNCTIONS


WRITE_TOOLS = frozenset({"send", "save_digest"})
_YES = frozenset({"yes", "y", "có", "đồng ý", "xác nhận"})
_NO = frozenset({"no", "n", "không", "hủy", "cancel"})


def parse_explicit_confirmation(value: str) -> bool | None:
    """Return True/False only for a clear standalone yes/no; ambiguity is None."""
    normalized = re.sub(r"[.!?]+$", "", value.strip().casefold())
    if normalized in _YES:
        return True
    if normalized in _NO:
        return False
    return None


def invoke_tool(
    name: str,
    args: dict[str, Any],
    *,
    host_approved_write: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Execute a tool, requiring host authorization for write tools.

    The model-supplied `confirmed` value never authorizes a write. A host
    approval authorizes only this invocation's displayed arguments.
    """
    actual_args = dict(args)
    if name in WRITE_TOOLS:
        if not host_approved_write:
            actual_args["confirmed"] = False
            return actual_args, {
                "status": "confirmation_required",
                "message": "Host approval is required before executing this write.",
            }
        actual_args["confirmed"] = True
        actual_args["_host_approved"] = True

    function = TOOL_FUNCTIONS.get(name)
    reported_args = {key: value for key, value in actual_args.items() if key != "_host_approved"}
    if function is None:
        return reported_args, {"error": "unknown_tool", "message": f"No local implementation for {name}"}
    try:
        return reported_args, function(**actual_args)
    except Exception as exc:
        return reported_args, {"error": type(exc).__name__, "message": str(exc)}
