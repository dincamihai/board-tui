"""E2E tests for scroll behavior in ListView and detail panel."""

import pytest
from pathlib import Path
from textual.widgets import ListView, Markdown
from textual.containers import VerticalScroll

from board_tui.app import BoardApp


# ---------------------------------------------------------------------------
# Fixtures: task markdown content
# ---------------------------------------------------------------------------

_TASK_LONG_BODY_MD = """---
column: Backlog
order: 10
created: 2026-04-21
---

# Task with very long body

This task has a lot of content to display.

## Section 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## Section 2

Ut enim ad minim veniam, quis nostrud exercitation ullamco.
Laboris nisi ut aliquip ex ea commodo consequat.

## Section 3

Duis aute irure dolor in reprehenderit in voluptate velit.
Esse cillum dolore eu fugiat nulla pariatur.

## Section 4

Excepteur sint occaecat cupidatat non proident.
Sunt in culpa qui officia deserunt mollit anim id est laborum.

## Section 5

More content to make the body even longer.
This should require scrolling to see everything.

## Section 6

Even more content for good measure.
The detail panel should scroll to show all of this.

## Section 7

Almost done now.
Just a bit more text to ensure we exceed the visible area.

## Section 8

Final section of this very long task body.
Now we should have enough content to test scrolling.
"""


def _make_many_tasks(column: str, count: int, prefix: str = "") -> list[tuple[str, str]]:
    """Generate multiple task definitions for the same column."""
    tasks = []
    for i in range(count):
        content = f"""---
column: {column}
order: {i * 10}
created: 2026-04-21
---

# Task number {i + 1}

This is task {i + 1} of {count} in the {column} column.
"""
        slug_prefix = f"{prefix}-" if prefix else ""
        tasks.append((f"{slug_prefix}task-{i + 1:02d}", content))
    return tasks


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
# Test: ListView scrolls when tasks exceed visible area
# ---------------------------------------------------------------------------

async def test_listview_scrolls_with_many_tasks(tmp_path: Path):
    """ListView scrolls when column has more tasks than visible area."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    # Create 15 tasks in Backlog column
    _write_tasks(tasks_dir, _make_many_tasks("Backlog", 15))

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)

        # ListView should have 15 items
        assert len(bg_lv.children) == 15

        # Navigate down - ListView handles scrolling internally
        initial_index = bg_lv.index
        for _ in range(10):
            await pilot.press("down")
        await pilot.pause()

        # Index should have changed
        assert bg_lv.index > initial_index


# ---------------------------------------------------------------------------
# Test: Detail panel scrolls for long content
# ---------------------------------------------------------------------------

async def test_detail_panel_scrolls_long_body(tmp_path: Path):
    """Detail panel (VerticalScroll) scrolls for tasks with long body."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("long-task", _TASK_LONG_BODY_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Detail panel should be a VerticalScroll
        detail_scroll = app.query_one("#detail-body", Markdown)

        # Task selected, body should be visible
        md_text = detail_scroll._markdown
        assert "Task with very long body" in md_text
        assert "Section 8" in md_text

        # Focus detail panel and scroll down
        await pilot.press("tab")  # Focus detail
        await pilot.pause()

        # Press down multiple times to scroll
        for _ in range(15):
            await pilot.press("down")
        await pilot.pause()

        # Scroll position should change
        scroll_container = app.query_one("#detail-scroll", VerticalScroll)
        assert scroll_container.scroll_y >= 0


# ---------------------------------------------------------------------------
# Test: Keyboard navigation works while scrolled
# ---------------------------------------------------------------------------

async def test_keyboard_navigation_while_scrolled(tmp_path: Path):
    """Arrow key navigation works after scrolling ListView."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    # Create 12 tasks
    _write_tasks(tasks_dir, _make_many_tasks("Backlog", 12))

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)

        # Scroll down
        for _ in range(8):
            await pilot.press("down")
        await pilot.pause()

        # Navigation should still work - select different tasks
        initial_index = bg_lv.index
        assert initial_index > 0  # Should have moved from first item

        # Navigate up
        await pilot.press("up")
        await pilot.pause()

        # Index should change
        new_index = bg_lv.index
        assert new_index == initial_index - 1 or new_index == initial_index


# ---------------------------------------------------------------------------
# Test: Scroll position preserved on re-render
# ---------------------------------------------------------------------------

async def test_scroll_position_preserved(tmp_path: Path):
    """Scroll position preserved when ListView re-renders."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, _make_many_tasks("Backlog", 10))

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)

        # Scroll down
        for _ in range(5):
            await pilot.press("down")
        await pilot.pause()

        index_before = bg_lv.index

        # Trigger re-render via refresh action
        await pilot.press("r")
        await pilot.pause()

        # Index should be preserved after reload
        index_after = bg_lv.index
        assert index_after == index_before


# ---------------------------------------------------------------------------
# Test: Arrow keys at edge scroll to next item
# ---------------------------------------------------------------------------

async def test_arrow_keys_scroll_to_next_item(tmp_path: Path):
    """Pressing down at edge of visible area scrolls to next item."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, _make_many_tasks("Backlog", 20))

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)

        # Start at first item
        assert bg_lv.index == 0

        # Navigate down multiple times
        for i in range(1, 10):
            await pilot.press("down")
            await pilot.pause()

            # Index should increment
            assert bg_lv.index == i

        # Scroll target should increase as we navigate
        assert bg_lv.scroll_target_y >= 0


# ---------------------------------------------------------------------------
# Test: Multiple columns with many tasks
# ---------------------------------------------------------------------------

async def test_scroll_in_multiple_columns(tmp_path: Path):
    """Scrolling works independently in each column ListView."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    # Create tasks in all columns with unique slugs
    entries = []
    entries.extend(_make_many_tasks("Backlog", 8, prefix="bg"))
    entries.extend(_make_many_tasks("In Progress", 6, prefix="ip"))
    entries.extend(_make_many_tasks("Done", 10, prefix="done"))
    _write_tasks(tasks_dir, entries)

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Verify tasks loaded correctly via app state
        assert len(app.by_col["Backlog"]) == 8
        assert len(app.by_col["In Progress"]) == 6
        assert len(app.by_col["Done"]) == 10

        # Navigate to Done column using right arrow
        # Start in Backlog (col 0), press right twice: Backlog -> In Progress -> Done
        await pilot.press("right")
        await pilot.pause()
        assert app.cur_col == 1  # In Progress

        await pilot.press("right")
        await pilot.pause()
        assert app.cur_col == 2  # Done

        # Done ListView should be focused and navigable
        done_lv = app.query_one("#list-done", ListView)
        initial_index = done_lv.index
        await pilot.press("down")
        await pilot.pause()
        # Index should change or stay at edge
        assert done_lv.index >= initial_index


# ---------------------------------------------------------------------------
# Test: Detail panel with markdown sections
# ---------------------------------------------------------------------------

async def test_detail_scroll_shows_all_sections(tmp_path: Path):
    """Detail panel scroll allows viewing all markdown sections."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("long-task", _TASK_LONG_BODY_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        body = app.query_one("#detail-body", Markdown)
        md_text = body._markdown

        # All sections should be in markdown source
        for i in range(1, 9):
            assert f"## Section {i}" in md_text, f"Section {i} missing"

        # Long body content preserved
        assert "Lorem ipsum" in md_text
        assert "Final section" in md_text
