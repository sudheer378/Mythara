from pathlib import Path
import pytest
from backend.app.utils.security import ensure_child_path, non_overwriting_path, sanitize_text


def test_sanitize_text_removes_nulls_and_limits():
    assert sanitize_text("a\x00bc", 2) == "ab"


def test_ensure_child_path_blocks_escape(tmp_path):
    with pytest.raises(ValueError):
        ensure_child_path(tmp_path / "allowed", tmp_path / "elsewhere" / "x.json")


def test_non_overwriting_path_increments(tmp_path):
    first = non_overwriting_path(tmp_path, "Name", ".json")
    first.write_text("{}")
    second = non_overwriting_path(tmp_path, "Name", ".json")
    assert first != second
