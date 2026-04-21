"""E2E tests for move mode functionality in BoardApp."""

import pytest
from pathlib import Path
from textual.widgets import ListView, Label

from board_tui.app import BoardApp


# ---------------------------------------------------------------------------
# Fixtures: task markdown content
# ---------------------------------------------------------------------------

_TASK_SIMPLE_MD = """---
column: Backlog
order: 10
created: 2026-04-21
---

# Simple task

Task body for move mode testing.
"""

_TASK_WITH_TIMESTAMP_MD = """---
column: In Progress
order: 20
created: 2026-04-21
updated: 2026-04-21T10:00:00+00:00
---

# Task with timestamp

Has existing updated field.
"""


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


def _read_task_file(tasks_dir: Path, slug: str) -> str:
    """Read and return content of a task file."""
    return tasks_dir.joinpath(f"{slug}.md").read_text()


# ---------------------------------------------------------------------------
# Test: 'm' toggles move mode (visible in detail header)
# ---------------------------------------------------------------------------

async def test_m_toggles_move_mode(tmp_path: Path):
    """Pressing 'm' toggles move mode, visible in detail header."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("simple", _TASK_SIMPLE_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Initially not in move mode
        header = app.query_one("#detail-header", Label)
        assert "MOVE" not in header.content
        assert "DETAIL" in header.content
        assert app.move_mode is False

        # Toggle move mode with 'm'
        await pilot.press("m")
        await pilot.pause()

        header = app.query_one("#detail-header", Label)
        assert "MOVE" in header.content
        assert "DETAIL" not in header.content
        assert app.move_mode is True

        # Toggle back with 'm'
        await pilot.press("m")
        await pilot.pause()

        header = app.query_one("#detail-header", Label)
        assert "MOVE" not in header.content
        assert "DETAIL" in header.content
        assert app.move_mode is False


# ---------------------------------------------------------------------------
# Test: Left/right arrows move task between columns
# ---------------------------------------------------------------------------

async def test_left_right_arrows_move_between_columns(tmp_path: Path):
    """In move mode, left/right arrows move task between columns."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("mid", _TASK_SIMPLE_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Task starts in Backlog
        assert app.cur_col == 0  # Backlog
        assert app.tasks[0]["column"] == "Backlog"

        # Enter move mode
        await pilot.press("m")
        await pilot.pause()
        assert app.move_mode is True

        # Move right to In Progress
        await pilot.press("right")
        await pilot.pause()

        # Task should now be in In Progress
        assert app.cur_col == 1
        assert app.tasks[0]["column"] == "In Progress"

        # Move right to Done
        await pilot.press("right")
        await pilot.pause()

        assert app.cur_col == 2
        assert app.tasks[0]["column"] == "Done"

        # Move left back to In Progress
        await pilot.press("left")
        await pilot.pause()

        assert app.cur_col == 1
        assert app.tasks[0]["column"] == "In Progress"


# ---------------------------------------------------------------------------
# Test: Task file updated with new column and timestamp
# ---------------------------------------------------------------------------

async def test_task_file_updated_with_column_and_timestamp(tmp_path: Path):
    """Moving task updates task file with new column and timestamp."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("simple", _TASK_SIMPLE_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Enter move mode and move right
        await pilot.press("m")
        await pilot.pause()

        await pilot.press("right")
        await pilot.pause()

        # Exit move mode
        await pilot.press("m")
        await pilot.pause()

        # Read task file
        content = _read_task_file(tasks_dir, "simple")

        # Column should be updated
        assert "column: In Progress" in content

        # Timestamp should be added
        assert "updated:" in content


# ---------------------------------------------------------------------------
# Test: Up/down arrows reorder task within column
# ---------------------------------------------------------------------------

async def test_up_down_arrows_reorder_within_column(tmp_path: Path):
    """In move mode, up/down arrows reorder task within column."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    task_a = """---
column: Backlog
order: 10
created: 2026-04-21
---

# Task A

First task.
"""

    task_b = """---
column: Backlog
order: 20
created: 2026-04-21
---

# Task B

Second task.
"""

    task_c = """---
column: Backlog
order: 30
created: 2026-04-21
---

# Task C

Third task.
"""

    _write_tasks(tasks_dir, [
        ("task-a", task_a),
        ("task-b", task_b),
        ("task-c", task_c),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Initial order: task-a (10), task-b (20), task-c (30)
        lv = app.query_one("#list-backlog", ListView)
        assert lv.index == 0  # First task selected

        # Enter move mode
        await pilot.press("m")
        await pilot.pause()

        # Move down to swap with task-b
        await pilot.press("down")
        await pilot.pause()

        # After _reload(), tasks list is refreshed
        # task-b should now be first (order=10), task-a second (order=20)
        assert len(app.tasks) == 3
        # Find tasks by slug
        task_a_data = next(t for t in app.tasks if t["slug"] == "task-a")
        task_b_data = next(t for t in app.tasks if t["slug"] == "task-b")
        assert task_a_data["fm"]["order"] == "20"
        assert task_b_data["fm"]["order"] == "10"


# ---------------------------------------------------------------------------
# Test: Escape exits move mode
# ---------------------------------------------------------------------------

async def test_escape_exits_move_mode(tmp_path: Path):
    """Pressing escape exits move mode."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("simple", _TASK_SIMPLE_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Enter move mode
        await pilot.press("m")
        await pilot.pause()
        assert app.move_mode is True

        # Exit with escape
        await pilot.press("escape")
        await pilot.pause()

        assert app.move_mode is False
        header = app.query_one("#detail-header", Label)
        assert "MOVE" not in header.content
        assert "DETAIL" in header.content


# ---------------------------------------------------------------------------
# Test: Column counts update after move
# ---------------------------------------------------------------------------

async def test_column_counts_update_after_move(tmp_path: Path):
    """Column title counts update after moving task between columns."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("simple", _TASK_SIMPLE_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Initial counts: Backlog=1, In Progress=0, Done=0
        backlog_title = app.query_one("#title-backlog", Label)
        assert "(1)" in backlog_title.content

        ip_title = app.query_one("#title-in-progress", Label)
        assert "(0)" in ip_title.content

        # Enter move mode and move right
        await pilot.press("m")
        await pilot.pause()

        await pilot.press("right")
        await pilot.pause()

        # Counts should update: Backlog=0, In Progress=1
        backlog_title = app.query_one("#title-backlog", Label)
        assert "(0)" in backlog_title.content

        ip_title = app.query_one("#title-in-progress", Label)
        assert "(1)" in ip_title.content


# ---------------------------------------------------------------------------
# Test: Move mode requires selection (no crash on empty column)
# ---------------------------------------------------------------------------

async def test_move_mode_with_empty_column(tmp_path: Path):
    """Move mode works even when some columns are empty."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    # Only one task in Backlog, other columns empty
    _write_tasks(tasks_dir, [("only", _TASK_SIMPLE_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Enter move mode
        await pilot.press("m")
        await pilot.pause()
        assert app.move_mode is True

        # Move through empty columns
        await pilot.press("right")  # To In Progress (empty)
        await pilot.pause()
        assert app.cur_col == 1

        await pilot.press("right")  # To Done (empty)
        await pilot.pause()
        assert app.cur_col == 2

        # Task should follow
        assert app.tasks[0]["column"] == "Done"


