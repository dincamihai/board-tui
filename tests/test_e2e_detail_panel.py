"""E2E tests for the detail panel display in BoardApp."""

import pytest
from pathlib import Path
from textual.widgets import Markdown, Label
from textual.containers import VerticalScroll

from board_tui.app import BoardApp


# ---------------------------------------------------------------------------
# Fixtures: task markdown content
# ---------------------------------------------------------------------------

_TASK_FULL_MD = """---
column: Backlog
order: 10
created: 2026-04-21
assigned: alice
priority: high
parent: main-feature
---

# Task with full metadata

This is the task body with **markdown** content.

## Comments

- **2026-04-21 @alice**: First comment
"""

_TASK_NO_PARENT_MD = """---
column: In Progress
order: 10
created: 2026-04-21
---

# Standalone task

No parent reference here."""


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


def _get_markdown_text(md: Markdown) -> str:
    """Extract source markdown text from Markdown widget."""
    return md.markdown if hasattr(md, "markdown") else ""


# ---------------------------------------------------------------------------
# Test: Header shows title, slug, column
# ---------------------------------------------------------------------------

async def test_detail_header_shows_title_slug_column(tmp_path: Path):
    """Selected task shows title, slug, and column in detail header area."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("full-task", _TASK_FULL_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Select the task (it's already highlighted by default)
        body = app.query_one("#detail-body", Markdown)
        md_text = body._markdown

        # Header content includes title, slug, column
        assert "Task with full metadata" in md_text
        assert "`full-task`" in md_text
        assert "_Backlog_" in md_text


# ---------------------------------------------------------------------------
# Test: Metadata list shows frontmatter fields except column
# ---------------------------------------------------------------------------

async def test_detail_metadata_shows_frontmatter_fields(tmp_path: Path):
    """Metadata list displays all frontmatter fields except column."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("full-task", _TASK_FULL_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        body = app.query_one("#detail-body", Markdown)
        md_text = body._markdown

        # Should show metadata fields
        assert "**created**:" in md_text
        assert "**assigned**:" in md_text
        assert "**priority**:" in md_text
        assert "**parent**:" in md_text
        # Column should NOT appear in metadata (it's in header line)
        assert "**column**:" not in md_text


# ---------------------------------------------------------------------------
# Test: Task body renders as Markdown
# ---------------------------------------------------------------------------

async def test_detail_body_renders_markdown(tmp_path: Path):
    """Task body content renders as Markdown with formatting."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("full-task", _TASK_FULL_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        body = app.query_one("#detail-body", Markdown)
        md_text = body._markdown

        # Body text should be present
        assert "This is the task body" in md_text
        # Markdown bold syntax preserved
        assert "**markdown**" in md_text


# ---------------------------------------------------------------------------
# Test: Comments section renders below body
# ---------------------------------------------------------------------------

async def test_detail_comments_render_below_body(tmp_path: Path):
    """Comments section appears below task body when present."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("full-task", _TASK_FULL_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        body = app.query_one("#detail-body", Markdown)
        md_text = body._markdown

        # Comments should be present
        assert "## Comments" in md_text
        assert "First comment" in md_text
        assert "@alice" in md_text


# ---------------------------------------------------------------------------
# Test: Empty selection shows "no selection"
# ---------------------------------------------------------------------------

async def test_detail_empty_selection_shows_placeholder(tmp_path: Path):
    """When no task selected, detail shows '_no selection_' placeholder."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    # No tasks = nothing selected

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        body = app.query_one("#detail-body", Markdown)
        md_text = body._markdown

        assert "_no selection_" in md_text


# ---------------------------------------------------------------------------
# Test: Move mode header changes to MOVE instruction
# ---------------------------------------------------------------------------

async def test_detail_move_mode_header_changes(tmp_path: Path):
    """In move mode, header displays MOVE instruction instead of DETAIL."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("no-parent", _TASK_NO_PARENT_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Normal mode: header shows DETAIL
        header = app.query_one("#detail-header", Label)
        assert "DETAIL" in header.content
        assert "MOVE" not in header.content

        # Toggle move mode directly (action_toggle_move requires board focus + selection)
        app.move_mode = True
        app._update_detail()
        await pilot.pause()

        header = app.query_one("#detail-header", Label)
        assert "MOVE" in header.content
        assert "arrows relocate" in header.content


# ---------------------------------------------------------------------------
# Test: Focus indicator shows when detail pane focused
# ---------------------------------------------------------------------------

async def test_detail_focus_indicator_shows_prefix(tmp_path: Path):
    """When detail pane has focus, header shows ▾ prefix."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("no-parent", _TASK_NO_PARENT_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Initially board focused
        header = app.query_one("#detail-header", Label)
        assert "▾" not in header.content

        # Switch focus to detail
        await pilot.press("tab")
        await pilot.pause()

        header = app.query_one("#detail-header", Label)
        assert "▾" in header.content
        assert "▾ DETAIL" in header.content

        # Switch back to board - prefix removed
        await pilot.press("tab")
        await pilot.pause()

        header = app.query_one("#detail-header", Label)
        assert "▾" not in header.content


# ---------------------------------------------------------------------------
# Test: Navigation updates detail panel
# ---------------------------------------------------------------------------

async def test_navigation_updates_detail_panel(tmp_path: Path):
    """Selecting different tasks updates detail panel content."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    # Both tasks in same column for navigation test
    task_a = _TASK_FULL_MD.replace("column: Backlog", "column: Backlog")
    task_b = _TASK_NO_PARENT_MD.replace("column: In Progress", "column: Backlog")
    _write_tasks(tasks_dir, [
        ("task-a", task_a),
        ("task-b", task_b),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # First task selected (task-a sorted first alphabetically)
        body = app.query_one("#detail-body", Markdown)
        assert "Task with full metadata" in body._markdown

        # Move to second task
        await pilot.press("down")
        await pilot.pause()

        body = app.query_one("#detail-body", Markdown)
        assert "Standalone task" in body._markdown
        assert "No parent reference" in body._markdown


# ---------------------------------------------------------------------------
# Test: Markdown widget is queryable and contains expected text
# ---------------------------------------------------------------------------

async def test_markdown_widget_queryable_with_expected_content(tmp_path: Path):
    """Markdown widget can be queried and contains expected structured content."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("full-task", _TASK_FULL_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Can query the Markdown widget
        body = app.query_one("#detail-body", Markdown)
        assert body is not None

        # Content structure: heading, slug line, metadata, body
        md_text = body._markdown
        lines = md_text.split("\n")

        # Should have heading (### Title)
        heading_lines = [l for l in lines if l.startswith("###")]
        assert len(heading_lines) >= 1
        assert "Task with full metadata" in heading_lines[0]

        # Should have slug line with backticks
        slug_lines = [l for l in lines if "`" in l]
        assert len(slug_lines) >= 1
        assert "full-task" in slug_lines[0]
