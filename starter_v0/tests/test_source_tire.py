"""Offline source policy tests, including deceptive URLs and agent dispatch."""
from pathlib import Path

import pytest

from agent import ResearchAgent
from providers.base import ModelResponse, ToolCall
from tools import load_tool_declarations, to_openai_tools
from tools.source_tire.tool import source_tire


@pytest.mark.parametrize("url,category,tier,matched", [
    ("https://openai.com/news/", "official", "T1", "openai.com"),
    ("https://platform.openai.com/docs", "official", "T1", "openai.com"),
    ("https://www.nasa.gov/", "official", "T1", "nasa.gov"),
    ("https://moh.gov.vn/", "official", "T1", "gov.vn"),
    ("https://agency.gov/", "official", "T1", "gov"),
    ("https://www.reuters.com/", "news", "T2", "reuters.com"),
    ("https://vnexpress.net/", "news", "T2", "vnexpress.net"),
    ("https://www.bbc.co.uk/news", "news", "T2", "bbc.co.uk"),
    ("https://x.com/OpenAI/status/123", "social", "T3", "x.com"),
    ("https://m.facebook.com/post/123", "social", "T3", "facebook.com"),
    ("https://youtu.be/123", "social", "T3", "youtu.be"),
    ("https://example.org/", "unknown", "unrated", None),
    ("https://example.edu/", "unknown", "unrated", None),
    ("https://reuters.com.evil.example/", "unknown", "unrated", None),
    ("https://notopenai.com/", "unknown", "unrated", None),
    ("https://evil.example/gov.vn?url=https://reuters.com", "unknown", "unrated", None),
    ("https://gov.vn.evil.example/", "unknown", "unrated", None),
])
def test_classification_rules(url, category, tier, matched):
    result = source_tire(url)
    assert (result["category"], result["tier"], result["matched_domain"]) == (category, tier, matched)
    assert result["limitation"]


def test_normalizes_case_trailing_dot_and_outer_spaces():
    result = source_tire("  HTTPS://WWW.REUTERS.COM.:443/news  ")
    assert result["domain"] == "www.reuters.com"
    assert result["category"] == "news"
    assert result["rule"] == "news_domain_allowlist"


@pytest.mark.parametrize("url", [
    "", " ", None, 123, [], {}, "reuters.com", "//reuters.com",
    "ftp://reuters.com", "javascript:alert(1)", "https://", "https://localhost",
    "https://127.0.0.1", "https://[::1]", "https://[broken", "https://bad_domain.com",
    "https://-bad.com", "https://a..com", "https://reuters.com:abc",
    "https://reuters.com:65536", "https://reuters.com:0", "https://reuters.com:",
    "https://reuters.com@evil.example/", "https://user:pass@reuters.com/",
    "https://reuters.com/with space", "https://reuters.com/\nnews",
    "https://reuters.com\\@evil.example", "https://%72euters.com", "https://reuters.com..",
])
def test_invalid_url_returns_error_instead_of_raising(url):
    result = source_tire(url)
    assert result["error"] == "invalid_url"
    assert result["message"]
    assert "tier" not in result


def test_missing_argument_returns_error():
    assert source_tire()["error"] == "invalid_url"


def test_agent_dispatches_declared_source_tire():
    declarations = load_tool_declarations(Path(__file__).resolve().parents[1] / "artifacts/tools.yaml")
    class FakeProvider:
        def complete(self, messages, tools, **kwargs):
            assert any(t["function"]["name"] == "source_tire" for t in tools)
            return ModelResponse(text=None, tool_calls=[
                ToolCall("source_tire", {"url": "https://www.reuters.com/"}),
            ])
    run = ResearchAgent(FakeProvider(), system_prompt="test", tools=to_openai_tools(declarations)).run([
        {"role": "user", "content": "Phân loại nguồn https://www.reuters.com/"},
    ])
    assert run.tool_results[0]["tool"] == "source_tire"
    assert run.tool_results[0]["result"]["category"] == "news"
