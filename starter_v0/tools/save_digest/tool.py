"""Save a confirmed AI news digest as a Markdown file.

The host application must independently verify user consent before passing
``confirmed=True``. A model-generated boolean is not proof of consent.
"""

from pathlib import Path
import re
import unicodedata

DIGEST_DIR = Path(__file__).resolve().parent.parent / "digests"


def _slugify(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title)
    ascii_title = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")
    return slug[:80].rstrip("-")


def save_digest(title: str, content: str, confirmed: bool = False, _host_approved: bool = False) -> dict:
    """Persist a Markdown digest without overwriting existing files."""
    if confirmed is not True or _host_approved is not True:
        return {"status": "confirmation_required", "file_path": None,
                "message": "Explicit user confirmation and host approval are required before saving."}

    if not isinstance(title, str) or not title.strip():
        return {"status": "error", "file_path": None, "message": "A nonempty title is required."}
    if not isinstance(content, str) or not content.strip():
        return {"status": "error", "file_path": None, "message": "Nonempty Markdown content is required."}

    slug = _slugify(title)
    if not slug:
        return {"status": "error", "file_path": None,
                "message": "Title cannot be converted to a safe filename."}

    try:
        DIGEST_DIR.mkdir(parents=True, exist_ok=True)
        path = DIGEST_DIR / f"{slug}.md"
        with path.open("x", encoding="utf-8", newline="\n") as file:
            file.write(content)
    except FileExistsError:
        return {"status": "error", "file_path": None,
                "message": "Digest already exists; existing files are never overwritten."}
    except OSError:
        return {"status": "error", "file_path": None,
                "message": "Unable to write digest to disk."}

    return {"status": "saved", "file_path": str(path), "message": "Digest saved successfully."}
