from __future__ import annotations

from typing import Any

from tools._shared import domain


def cite_source(title: str = "", url: str = "", source: str = "", date: str = "", style: str = "plain") -> dict[str, Any]:
    title, url, source, date = (str(v or "").strip() for v in (title, url, source, date))
    if not title and not url:
        return {"tool": "cite_source", "error": "missing_input", "message": "Need at least a title or a url."}
    if style not in ("plain", "markdown"):
        return {"tool": "cite_source", "error": "invalid_style", "message": f"style must be plain or markdown, got {style!r}"}
    source = source or domain(url)
    label = title or url
    if style == "markdown":
        head = f"[{label}]({url})" if url else label
        meta = ", ".join(x for x in (source, date) if x)
        citation = f"{head} - {meta}" if meta else head
    else:
        parts = [label, source, date] + ([url] if title and url else [])
        citation = ". ".join(x for x in parts if x)
    return {"tool": "cite_source", "style": style, "citation": citation}
