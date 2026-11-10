from __future__ import annotations

from pathlib import Path

from agent import ResearchAgent
from chat import execute_tool_call, request_explicit_write_approval
from providers.base import ModelResponse, ToolCall
from tools.save_digest import tool as save_digest_tool
from tools.send import tool as send_tool
from write_safety import parse_explicit_confirmation


class OneCallProvider:
    def __init__(self, call: ToolCall) -> None:
        self.call = call

    def complete(self, *args, **kwargs) -> ModelResponse:
        return ModelResponse(tool_calls=[self.call])


def test_ambiguous_approval_is_not_consent() -> None:
    assert parse_explicit_confirmation("yes") is True
    assert parse_explicit_confirmation("No.") is False
    assert parse_explicit_confirmation("That sounds fine, I suppose.") is None
    assert parse_explicit_confirmation("maybe") is None


def test_prompt_covers_v3_intent_and_write_boundaries() -> None:
    prompt = (Path(__file__).resolve().parents[1] / "artifacts" / "system_prompt.md").read_text(encoding="utf-8")

    assert "Preserve source type" in prompt
    assert "Do not add social_search unless the user separately asks" in prompt
    assert "do not answer the unrelated request and do not call a tool" in prompt
    assert "do not call send or save_digest" in prompt
    assert "Treat hedged or ambiguous replies" in prompt
    assert "entire Markdown content verbatim" in prompt


def test_cli_asks_again_after_ambiguous_approval(monkeypatch, capsys) -> None:
    answers = iter(["That sounds fine, I suppose", "yes"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    assert request_explicit_write_approval("Approve this digest") is True
    assert "Please answer yes or no" in capsys.readouterr().out


def test_research_agent_blocks_model_confirmed_save_without_host_authority(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(save_digest_tool, "DIGEST_DIR", tmp_path)
    title = "Host Guard"
    content = "# Host Guard\n\n- Preserve every line."
    agent = ResearchAgent(
        OneCallProvider(ToolCall("save_digest", {"title": title, "content": content, "confirmed": True})),
        system_prompt="",
        tools=[],
    )

    blocked = agent.run([{"role": "user", "content": "Save it."}])
    assert blocked.tool_results[0]["result"]["status"] == "confirmation_required"
    assert not (tmp_path / "host-guard.md").exists()

    approved = agent.run(
        [{"role": "user", "content": "Save it."}],
        write_authorizer=lambda call: call.name == "save_digest" and call.args.get("content") == content,
    )
    assert approved.tool_results[0]["result"]["status"] == "saved"
    assert (tmp_path / "host-guard.md").read_text(encoding="utf-8") == content


def test_chat_tool_executor_requires_host_approval_for_send_and_save(tmp_path: Path, monkeypatch, fake_http) -> None:
    http_calls = fake_http({})
    monkeypatch.setattr(save_digest_tool, "DIGEST_DIR", tmp_path)

    blocked_send = execute_tool_call(ToolCall("send", {"text": "hello", "confirmed": True}))
    blocked_save = execute_tool_call(ToolCall("save_digest", {"title": "Blocked", "content": "# Blocked", "confirmed": True}))
    assert blocked_send["result"]["status"] == "confirmation_required"
    assert blocked_save["result"]["status"] == "confirmation_required"
    assert not (tmp_path / "blocked.md").exists()
    assert http_calls == []

    approved = execute_tool_call(
        ToolCall("save_digest", {"title": "Approved", "content": "# Approved", "confirmed": False}),
        approved_write=True,
    )
    assert approved["result"]["status"] == "saved"
    assert approved["args"]["confirmed"] is True


def test_write_implementations_reject_model_confirmation_without_host_approval(tmp_path: Path, monkeypatch, fake_http) -> None:
    http_calls = fake_http({})
    monkeypatch.setattr(save_digest_tool, "DIGEST_DIR", tmp_path)

    save_result = save_digest_tool.save_digest("Direct Call", "# Direct Call", confirmed=True)
    send_result = send_tool.send_telegram("Hello", confirmed=True)

    assert save_result["status"] == "confirmation_required"
    assert send_result["status"] == "host_approval_required"
    assert not (tmp_path / "direct-call.md").exists()
    assert http_calls == []
