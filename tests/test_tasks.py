"""Tests for board_tui.tasks pure functions."""

from pathlib import Path
from board_tui.tasks import slugify, parse, dump

# --- slugify ---

def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"

def test_slugify_special_chars():
    assert slugify("What's this?!") == "whats-this"

def test_slugify_uppercase():
    assert slugify("UPPER CASE") == "upper-case"

def test_slugify_max_length():
    assert len(slugify("a" * 200)) == 70

def test_slugify_preserves_existing_hyphens():
    assert slugify("foo-bar baz") == "foo-bar-baz"

def test_slugify_consecutive_spaces():
    assert slugify("one   two") == "one-two"

# --- parse / dump roundtrip ---

def test_parse_dump_roundtrip(tmp_path: Path):
    original = """---
column: In Progress
order: 10
---

# My Task

Some body text.\n"""
    f = tmp_path / "my-task.md"
    f.write_text(original)
    fm, body = parse(f)
    dump(f, fm, body)
    assert f.read_text() == original

def test_parse_no_frontmatter(tmp_path: Path):
    f = tmp_path / "nofm.md"
    f.write_text("# No frontmatter\n\nBody here.")
    fm, body = parse(f)
    assert fm == {}
    assert body == "# No frontmatter\n\nBody here."

def test_dump_multiline_body(tmp_path: Path):
    f = tmp_path / "test.md"
    dump(f, {"a": "1", "b": "2"}, "body line\n")
    text = f.read_text()
    assert "---" in text
    assert "a: 1" in text
    assert "b: 2" in text
    assert "body line\n" in text
