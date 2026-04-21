"""E2E tests for markdown structure validation in task files."""

import tempfile

import pytest
from pathlib import Path
from textual.widgets import ListView

from board_tui.app import BoardApp
from board_tui.tasks import parse, load_tasks


# ---------------------------------------------------------------------------
# Fixtures: task markdown content variations
# ---------------------------------------------------------------------------

_TASK_VALID_FULL = """---
column: Backlog
order: 10
created: 2026-04-21
assigned: alice
---

# Valid task with full frontmatter

This task has a complete frontmatter block and proper heading."""

_TASK_VALID_MINIMAL = """---
column: In Progress
---

# Minimal frontmatter task

Only column field in frontmatter."""

_TASK_NO_FRONTMATTER = """# No frontmatter task

This file has no frontmatter delimiters.
Just a heading and body."""

_TASK_NO_HEADING = """---
column: Done
order: 5
---

No heading here, just body text.
Should use slug as title."""

_TASK_INVALID_FRONTMATTER = """---
column: Backlog
  invalid: yaml: broken
---

# Invalid frontmatter task

Frontmatter has invalid YAML."""

_TASK_EMPTY_FRONTMATTER = """---
---

# Empty frontmatter task

Frontmatter block exists but is empty."""

_TASK_MULTIPLE_HEADINGS = """---
column: Backlog
---

# First heading

Body paragraph.

## Second heading

More content.

### Third heading

Even more."""


def _write_tasks(tasks_dir: Path, entries: list[tuple[str, str]]) -> None:
    """Write task markdown files into the given directory."""
    for slug, content in entries:
        tasks_dir.joinpath(f"{slug}.md").write_text(content)


def _make_app(tasks_dir: Path, user: str = "alice") -> BoardApp:
    """Create a BoardApp bound to the given tasks directory."""
    return BoardApp(
        tasks_dir=str(tasks_dir),
        columns=["Backlog", "In Progress", "Done"],
        user=user,
    )


# ---------------------------------------------------------------------------
# Test: Frontmatter block required (--- delimiters)
# ---------------------------------------------------------------------------

async def test_frontmatter_block_parsed_correctly(tmp_path: Path):
    """Frontmatter block with --- delimiters parsed correctly."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("valid-full", _TASK_VALID_FULL)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Task should load successfully
        assert len(app.tasks) == 1
        task = app.tasks[0]

        # Frontmatter fields extracted
        assert task["fm"]["column"] == "Backlog"
        assert task["fm"]["order"] == "10"
        assert task["fm"]["created"] == "2026-04-21"
        assert task["fm"]["assigned"] == "alice"

        # Body extracted after frontmatter
        assert "Valid task with full frontmatter" in task["body"]


# ---------------------------------------------------------------------------
# Test: column field required in frontmatter
# ---------------------------------------------------------------------------

async def test_column_field_in_frontmatter(tmp_path: Path):
    """Column field in frontmatter determines task placement."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("valid-minimal", _TASK_VALID_MINIMAL)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        task = app.tasks[0]
        assert task["column"] == "In Progress"
        assert task["fm"]["column"] == "In Progress"

        # Task appears in correct column ListView
        ip_lv = app.query_one("#list-in-progress", ListView)
        assert ip_lv.children[0].data["slug"] == "valid-minimal"


# ---------------------------------------------------------------------------
# Test: At least one heading in body
# ---------------------------------------------------------------------------

async def test_heading_extracted_from_body(tmp_path: Path):
    """First # heading in body extracted as task title."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("valid-full", _TASK_VALID_FULL)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        task = app.tasks[0]
        assert task["title"] == "Valid task with full frontmatter"


async def test_multiple_headings_uses_first(tmp_path: Path):
    """When multiple headings present, first # heading used as title."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("multi-heading", _TASK_MULTIPLE_HEADINGS)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        task = app.tasks[0]
        assert task["title"] == "First heading"
        # Body still contains all headings
        assert "## Second heading" in task["body"]
        assert "### Third heading" in task["body"]


# ---------------------------------------------------------------------------
# Test: File without frontmatter still loads (fallback behavior)
# ---------------------------------------------------------------------------

async def test_no_frontmatter_still_loads(tmp_path: Path):
    """File without frontmatter delimiters still loads with defaults."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("no-frontmatter", _TASK_NO_FRONTMATTER)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Task should load
        assert len(app.tasks) == 1
        task = app.tasks[0]

        # Title extracted from heading
        assert task["title"] == "No frontmatter task"

        # Default column (first in list)
        assert task["column"] == "Backlog"

        # Body contains all text
        assert "no frontmatter delimiters" in task["body"]


# ---------------------------------------------------------------------------
# Test: File without heading uses slug as title
# ---------------------------------------------------------------------------

async def test_no_heading_uses_slug_as_title(tmp_path: Path):
    """File without # heading uses filename slug as title."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("no-heading", _TASK_NO_HEADING)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        task = app.tasks[0]
        # Slug used as title when no heading
        assert task["title"] == "no-heading"
        assert task["slug"] == "no-heading"

        # Body still extracted
        assert "No heading here" in task["body"]


# ---------------------------------------------------------------------------
# Test: Invalid frontmatter handled gracefully
# ---------------------------------------------------------------------------

async def test_invalid_frontmatter_handled_gracefully(tmp_path: Path):
    """Invalid YAML in frontmatter handled without crashing."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("invalid-frontmatter", _TASK_INVALID_FRONTMATTER)])

    # parse function should handle invalid YAML
    path = tasks_dir / "invalid-frontmatter.md"
    fm, body = parse(path)

    # Should return empty dict or partial parse, not crash
    assert isinstance(fm, dict)
    assert isinstance(body, str)

    # App should still load
    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        # Task loads even with invalid frontmatter
        assert len(app.tasks) == 1


# ---------------------------------------------------------------------------
# Test: Empty frontmatter handled
# ---------------------------------------------------------------------------

async def test_empty_frontmatter_block(tmp_path: Path):
    """Empty frontmatter block (--- ---) handled correctly."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("empty-frontmatter", _TASK_EMPTY_FRONTMATTER)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        task = app.tasks[0]
        # Title from heading
        assert task["title"] == "Empty frontmatter task"
        # Empty frontmatter = empty dict
        assert task["fm"] == {}
        # Default column
        assert task["column"] == "Backlog"


# ---------------------------------------------------------------------------
# Test: Parser extracts frontmatter correctly (unit test)
# ---------------------------------------------------------------------------

def test_parse_function_extract_frontmatter():
    """parse() function correctly extracts frontmatter and body."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.md"
        path.write_text(_TASK_VALID_FULL)

        fm, body = parse(path)

        assert fm["column"] == "Backlog"
        assert fm["order"] == "10"
        assert fm["created"] == "2026-04-21"
        assert fm["assigned"] == "alice"
        assert "Valid task with full frontmatter" in body


def test_parse_function_no_frontmatter():
    """parse() handles file without frontmatter."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.md"
        path.write_text(_TASK_NO_FRONTMATTER)

        fm, body = parse(path)

        # Empty frontmatter dict
        assert fm == {}
        # Full content as body
        assert "# No frontmatter task" in body


# ---------------------------------------------------------------------------
# Test: load_tasks extracts title from heading
# ---------------------------------------------------------------------------

def test_load_tasks_title_from_heading():
    """load_tasks() extracts title from first # heading."""
    with tempfile.TemporaryDirectory() as tmp:
        tasks_dir = Path(tmp)
        path = tasks_dir / "test.md"
        path.write_text(_TASK_VALID_FULL)

        tasks = load_tasks(tasks_dir, ["Backlog", "In Progress", "Done"])

        assert len(tasks) == 1
        assert tasks[0]["title"] == "Valid task with full frontmatter"


def test_load_tasks_title_from_slug():
    """load_tasks() uses slug as title when no heading."""
    with tempfile.TemporaryDirectory() as tmp:
        tasks_dir = Path(tmp)
        path = tasks_dir / "custom-slug.md"
        path.write_text(_TASK_NO_HEADING)

        tasks = load_tasks(tasks_dir, ["Backlog", "In Progress", "Done"])

        assert len(tasks) == 1
        assert tasks[0]["title"] == "custom-slug"
        assert tasks[0]["slug"] == "custom-slug"
