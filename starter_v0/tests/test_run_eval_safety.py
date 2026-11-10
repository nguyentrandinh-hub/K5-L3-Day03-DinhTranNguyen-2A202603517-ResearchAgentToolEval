from __future__ import annotations

from pathlib import Path

import pytest

from run_eval import evaluate_phase_b, isolated_tool_outputs, safe_send_stub, validate_expected_tools
from tools import TOOL_FUNCTIONS, load_tool_declarations
from tools.paper_text import tool as paper_text_tool
from tools.save_digest import tool as save_digest_tool
from write_safety import invoke_tool


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("forbidden_tool", ["send", "save_digest"])
def test_forbidden_only_case_allows_format_but_rejects_forbidden_calls(forbidden_tool: str) -> None:
    case = {
        "failure_type": "unnecessary_tool",
        "expect": {"forbidden_tools": ["send", "save_digest"]},
    }

    allowed = evaluate_phase_b(
        case,
        [{"name": "format", "args": {"headline": "Draft"}}],
        None,
    )
    rejected = evaluate_phase_b(
        case,
        [
            {"name": "format", "args": {"headline": "Draft"}},
            {"name": forbidden_tool, "args": {"confirmed": True}},
        ],
        None,
    )

    assert allowed["passed"] is True
    assert rejected["passed"] is False
    assert rejected["observed_mismatch"] == "forbidden_tool_call"
    assert rejected["failures"] == [f"forbidden tool call {forbidden_tool}"]


def test_forbidden_tool_is_checked_alongside_expected_calls() -> None:
    case = {
        "failure_type": "wrong_boundary",
        "expect": {
            "tool_calls": [{"name": "clarify", "args": {"response_type": "yes_no"}}],
            "forbidden_tools": ["save_digest"],
        },
    }
    result = evaluate_phase_b(
        case,
        [
            {"name": "clarify", "args": {"response_type": "yes_no"}},
            {"name": "save_digest", "args": {"confirmed": True}},
        ],
        None,
    )

    assert result["passed"] is False
    assert result["observed_mismatch"] == "forbidden_tool_call"
    assert result["failures"] == ["forbidden tool call save_digest"]


def test_forbidden_tool_names_are_validated_against_declarations() -> None:
    case = {
        "id": "SD03_draft_only",
        "expect": {"forbidden_tools": ["send", "save_digest"]},
    }
    validate_expected_tools([case], load_tool_declarations(ROOT / "artifacts" / "tools.yaml"), ROOT / "data/eval_group.json")


def test_local_tool_writes_use_isolated_directories_and_are_restored(tmp_path: Path) -> None:
    original_digest_dir = save_digest_tool.DIGEST_DIR
    original_arxiv_dir = paper_text_tool.ARXIV_DIR
    sandbox = tmp_path / "tool-output"

    with isolated_tool_outputs(sandbox):
        assert save_digest_tool.DIGEST_DIR == sandbox.resolve() / "digests"
        assert paper_text_tool.ARXIV_DIR == sandbox.resolve() / "arxiv_papers"
        _, result = invoke_tool(
            "save_digest",
            {"title": "Offline Test", "content": "# Offline Test", "confirmed": True},
            host_approved_write=True,
        )
        assert result["status"] == "saved"
        saved_path = Path(result["file_path"])
        assert saved_path == sandbox.resolve() / "digests" / "offline-test.md"
        assert saved_path.read_text(encoding="utf-8") == "# Offline Test"

    assert save_digest_tool.DIGEST_DIR == original_digest_dir
    assert paper_text_tool.ARXIV_DIR == original_arxiv_dir
    assert saved_path.exists()


def test_temporary_tool_outputs_are_removed_after_context() -> None:
    with isolated_tool_outputs() as sandbox:
        _, result = invoke_tool(
            "save_digest",
            {"title": "Temporary Test", "content": "# Temporary Test", "confirmed": True},
            host_approved_write=True,
        )
        saved_path = Path(result["file_path"])
        assert saved_path.is_relative_to(sandbox)
        assert saved_path.exists()

    assert not sandbox.exists()


def test_tool_output_dir_cannot_overlap_production_tool_paths() -> None:
    production_tools_dir = Path(save_digest_tool.DIGEST_DIR).resolve().parent

    with pytest.raises(ValueError, match="must not overlap"):
        with isolated_tool_outputs(production_tools_dir):
            pass


def test_send_is_stubbed_and_restored_during_evaluation(tmp_path: Path, fake_http) -> None:
    original_send = TOOL_FUNCTIONS["send"]
    http_calls = fake_http({})
    assert safe_send_stub("message", confirmed=True)["status"] == "blocked_in_eval"

    with isolated_tool_outputs(tmp_path / "safe-send"):
        result = TOOL_FUNCTIONS["send"]("message", confirmed=True)
        assert result["status"] == "blocked_in_eval"

    assert TOOL_FUNCTIONS["send"] is original_send
    assert http_calls == []
