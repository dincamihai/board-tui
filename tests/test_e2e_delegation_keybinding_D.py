"""E2E tests for `D` keybinding — cancel delegation.

Press `D` in board-tui to cancel a delegated task.
Only works in task list view for tasks with `delegation_status: queued|processing`.
Updates frontmatter `delegation_status: cancelled` and refreshes list.
"""

import pytest
from pathlib import Path
from textual.widgets import ListView

from board_tui.app import BoardApp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_TASK_QUEUED = """---
column: Backlog
order: 10
created: 2026-04-21
delegation_status: queued
---

# Queued task

Body.
"""

_TASK_PROCESSING = """---
column: In Progress
order: 10
created: 2026-04-21
delegation_status: processing
---

# Processing task

Body.
"""

_TASK_REGULAR = """---
column: Backlog
order: 10
created: 2026-04-21
---

# Regular task

Body.
"""

_TASK_DONE_DELEGATED = """---
column: Done
order: 10
created: 2026-04-21
delegation_status: done
---

# Done delegated task

Body.
"""


def _write_tasks(tasks_dir: Path, entries: list[tuple[str, str]]) -> None:
    for slug, content in entries:
        tasks_dir.joinpath(f"{slug}.md").write_text(content)


def _make_app(tasks_dir: Path, user: str = "alice") -> BoardApp:
    return BoardApp(
        tasks_dir=str(tasks_dir),
        columns=["Backlog", "In Progress", "Done"],
        user=user,
    )


def _get_list_titles(lv: ListView) -> list[str]:
    return [child.children[0].content for child in lv.children
            if hasattr(child, "children") and child.children]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

async def test_D_sets_cancelled_on_queued_task(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("queued-task", _TASK_QUEUED)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        await pilot.press("D")
        await pilot.pause()

        content = (tasks_dir / "queued-task.md").read_text()
        assert "delegation_status: cancelled" in content

        lv = app.query_one("#list-backlog", ListView)
        titles = _get_list_titles(lv)
        assert titles[0].startswith("•")


async def test_D_sets_cancelled_on_processing_task(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("processing-task", _TASK_PROCESSING)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        # Navigate to In Progress
        await pilot.press("right")
        await pilot.pause()

        await pilot.press("D")
        await pilot.pause()

        content = (tasks_dir / "processing-task.md").read_text()
        assert "delegation_status: cancelled" in content

        lv = app.query_one("#list-in-progress", ListView)
        titles = _get_list_titles(lv)
        assert titles[0].startswith("•")


async def test_D_ignored_on_non_delegated(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("regular-task", _TASK_REGULAR)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        await pilot.press("D")
        await pilot.pause()

        content = (tasks_dir / "regular-task.md").read_text()
        assert "delegation_status" not in content

        lv = app.query_one("#list-backlog", ListView)
        titles = _get_list_titles(lv)
        assert titles[0].startswith("•")


async def test_D_ignored_on_done_delegated(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("done-task", _TASK_DONE_DELEGATED)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        # Navigate to Done
        await pilot.press("right", "right")
        await pilot.pause()

        await pilot.press("D")
        await pilot.pause()

        content = (tasks_dir / "done-task.md").read_text()
        assert "delegation_status: done" in content
        assert "delegation_status: cancelled" not in content

        lv = app.query_one("#list-done", ListView)
        titles = _get_list_titles(lv)
        assert titles[0].startswith("✓")


async def test_D_ignored_in_detail_pane(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("queued-task", _TASK_QUEUED)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Switch to detail pane
        await pilot.press("tab")
        await pilot.pause()

        await pilot.press("D")
        await pilot.pause()

        content = (tasks_dir / "queued-task.md").read_text()
        assert "delegation_status: queued" in content
        assert "delegation_status: cancelled" not in content
