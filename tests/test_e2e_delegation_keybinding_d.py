"""E2E tests for `d` keybinding — delegate task.

Press `d` in board-tui to mark selected task for delegation.
Only works in task list view for tasks in Backlog or In Progress.
Updates frontmatter `delegation_status: queued` and refreshes list.
"""

import pytest
from pathlib import Path
from textual.widgets import ListView

from board_tui.app import BoardApp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_TASK_BACKLOG = """---
column: Backlog
order: 10
created: 2026-04-21
---

# Backlog task

Body.
"""

_TASK_IN_PROGRESS = """---
column: In Progress
order: 10
created: 2026-04-21
---

# In Progress task

Body.
"""

_TASK_DONE = """---
column: Done
order: 10
created: 2026-04-21
---

# Done task

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

async def test_d_on_backlog_task_sets_delegation_status(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("backlog-task", _TASK_BACKLOG)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Press d
        await pilot.press("d")
        await pilot.pause()

        # File updated
        content = (tasks_dir / "backlog-task.md").read_text()
        assert "delegation_status: queued" in content

        # UI shows queued prefix
        lv = app.query_one("#list-backlog", ListView)
        titles = _get_list_titles(lv)
        assert titles[0].startswith("⏳")


async def test_d_on_in_progress_task_sets_delegation_status(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("ip-task", _TASK_IN_PROGRESS)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        # Navigate to In Progress
        await pilot.press("right")
        await pilot.pause()

        await pilot.press("d")
        await pilot.pause()

        content = (tasks_dir / "ip-task.md").read_text()
        assert "delegation_status: queued" in content

        lv = app.query_one("#list-in-progress", ListView)
        titles = _get_list_titles(lv)
        assert titles[0].startswith("⏳")


async def test_d_on_done_task_shows_error(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("done-task", _TASK_DONE)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        # Navigate to Done
        await pilot.press("right", "right")
        await pilot.pause()

        await pilot.press("d")
        await pilot.pause()

        # File unchanged
        content = (tasks_dir / "done-task.md").read_text()
        assert "delegation_status" not in content

        # UI still shows bullet
        lv = app.query_one("#list-done", ListView)
        titles = _get_list_titles(lv)
        assert titles[0].startswith("•")


async def test_d_with_no_selection_does_nothing(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        await pilot.press("d")
        await pilot.pause()

        # No crash
        assert app._selected() is None
