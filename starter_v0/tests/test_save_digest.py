from tools.save_digest import tool as module


def test_save_success(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "DIGEST_DIR", tmp_path)

    result = module.save_digest(
        "AI News",
        "# AI News",
        confirmed=True,
        _host_approved=True,
    )

    assert result["status"] == "saved"
    assert (tmp_path / "ai-news.md").exists()


def test_requires_confirmation(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "DIGEST_DIR", tmp_path)

    result = module.save_digest(
        "AI News",
        "# AI News",
        confirmed=False
    )

    assert result["status"] == "confirmation_required"
    assert list(tmp_path.iterdir()) == []


def test_no_overwrite(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "DIGEST_DIR", tmp_path)

    module.save_digest("AI News", "First", True, _host_approved=True)
    result = module.save_digest("AI News", "Second", True, _host_approved=True)

    assert result["status"] == "error"
    assert (tmp_path / "ai-news.md").read_text() == "First"
