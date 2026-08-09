from pathlib import Path
import re

SAFE_NAME = re.compile(r"[^a-zA-Z0-9_.-]+")


def sanitize_text(value: str, max_length: int = 12000) -> str:
    cleaned = value.replace("\x00", "").strip()
    return cleaned[:max_length]


def safe_slug(value: str) -> str:
    slug = SAFE_NAME.sub("_", value.strip().lower()).strip("._")
    return slug or "item"


def ensure_child_path(base: Path, candidate: Path) -> Path:
    base_resolved = base.resolve()
    candidate_resolved = candidate.resolve()
    if candidate_resolved != base_resolved and base_resolved not in candidate_resolved.parents:
        raise ValueError(f"Path escapes allowed directory: {candidate}")
    return candidate_resolved


def non_overwriting_path(directory: Path, stem: str, suffix: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    clean_stem = safe_slug(stem)
    suffix = suffix if suffix.startswith(".") else f".{suffix}"
    path = directory / f"{clean_stem}{suffix}"
    counter = 1
    while path.exists():
        path = directory / f"{clean_stem}_{counter}{suffix}"
        counter += 1
    return path
