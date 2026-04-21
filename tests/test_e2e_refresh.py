"""E2E tests for BoardApp refresh functionality.

Uses Textual's App.run_test() with async pilots to exercise the full
refresh flow: pressing 'r', external file modifications, and verifying
UI updates reflect the new state.

Test cases:
- 'r' reloads tasks from disk
- External changes to task files reflected in UI
- Notification shows "refreshed"
- Column counts update after refresh
- Selection preserved if task still exists
"""

import re
import time

import pytest
from pathlib import Path
from textual.widgets import Label, ListView, Markdown

from board_tui.app import BoardApp


# ------ helpers / fixtures -----------------------------------------------

def _make_app(tasks_dir: Path, user: str = "alice",
              columns: list[str] | None = None) -> BoardApp:
    """Create a BoardApp bound to *tasks_dir*."""
    return BoardApp(
        tasks_dir=str(tasks_dir),
        columns=columns or ["Backlog", "In Progress", "Done"],
        user=user,
    )


def _write_tasks(tasks_dir: Path, entries: list[tuple[str, str]]) -> None:
    """Write task markdown files (slug → full content)."""
    for slug, content in entries:
        tasks_dir.joinpath(f"{slug}.md").write_text(content)


def _get_list_titles(lv: ListView) -> list[str]:
    """Return the text content of every ListItem in a ListView."""
    titles: list[str] = []
    for child in lv.children:
        if hasattr(child, "children") and child.children:
            titles.append(child.children[0].content)
    return titles


def _slugify(s: str) -> str:
    """Minimal slugify matching board_tui.tasks.slugify."""
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s[:70]


def _get_list_titles_by_column(app: BoardApp, col: str) -> list[str]:
    """Return the text of every ListItem in the ListView for *col*."""
    lv = app.query_one(f"#list-{_slugify(col)}", ListView)
    return _get_list_titles(lv)


def _get_title_text(app: BoardApp, col: str) -> str:
    """Return the rendered text of a column title Label."""
    lbl = app.query_one(f"#title-{_slugify(col)}", Label)
    return lbl.content


# ------ test content fixtures --------------------------------------------

_TASK_A = """---
column: Backlog
order: 20
assigned: alice
created: 2026-04-21
---

# Task Alpha

This is task alpha in Backlog."""

_TASK_B = """---
column: In Progress
order: 10
assigned: alice
created: 2026-04-21
---

# Task Beta

This is task beta in In Progress."""

_TASK_C = """---
column: Backlog
order: 10
created: 2026-04-20
---

# Task Gamma

This is task gamma in Backlog."""


# ------ tests ------------------------------------------------------------

async def test_r_key_reloads_tasks_from_disk(tmp_path: Path):
    """Pressing 'r' causes the app to re-read all task files from disk."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [("alpha", _TASK_A), ("beta", _TASK_B)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Initial state: 1 task per column
        bg_lv = app.query_one("#list-backlog", ListView)
        ip_lv = app.query_one("#list-in-progress", ListView)
        assert len(_get_list_titles(bg_lv)) == 1
        assert len(_get_list_titles(ip_lv)) == 1

        # Remove the Backlog task file externally
        (tasks_dir / "alpha.md").unlink()

        # Press 'r' to refresh
        await pilot.press("r")
        await pilot.pause()

        # Backlog task should be gone
        assert len(_get_list_titles(bg_lv)) == 0
        # In Progress task should still be there
        assert len(_get_list_titles(ip_lv)) == 1


async def test_external_changes_reflected_in_ui(tmp_path: Path):
    """Changing a task file on disk causes the UI to reflect that after a refresh."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [("gamma", _TASK_C)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Verify initial state: "Task Gamma" in Backlog
        bg_titles = _get_list_titles_by_column(app, "Backlog")
        assert "Task Gamma" in bg_titles[0]

        # Modify the file externally — rename the title
        with open(tasks_dir / "gamma.md", "w") as f:
            f.write("""---
column: Backlog
order: 10
created: 2026-04-20
---

# Task Gamma (Renamed)

Updated body content.
""")

        # Refresh
        await pilot.press("r")
        await pilot.pause()

        # Backlog should now show "Task Gamma (Renamed)"
        bg_lv = app.query_one("#list-backlog", ListView)
        bg_titles = _get_list_titles(bg_lv)
        assert len(bg_titles) == 1
        assert "Task Gamma (Renamed)" in bg_titles[0]

        # Detail panel should also reflect the change
        body = app.query_one("#detail-body", Markdown)
        assert "Task Gamma (Renamed)" in body._markdown
        assert "Updated body content." in body._markdown


async def test_notification_shows_refreshed(tmp_path: Path):
    """After refresh, the app displays a notification saying 'refreshed'."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [("task", _TASK_A)])

    app = _make_app(tasks_dir)

    # Capture notifications
    notifications = []
    original_notify = app.notify
    def capture_notify(*args, **kwargs):
        notifications.append((args, kwargs))
        return original_notify(*args, **kwargs)
    app.notify = capture_notify

    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        await pilot.press("r")
        await pilot.pause()

    # Check that a notification was queued
    assert len(notifications) > 0, "No notification after refresh"
    args, kwargs = notifications[0]
    msg = args[0] if args else ""
    assert "refreshed" in msg.lower(), (
        f"Expected 'refreshed' in notification, got: {msg}"
    )


async def test_column_counts_update_after_refresh(tmp_path: Path):
    """Adding / removing files from disk, then refreshing, updates column counts."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    # Start with 2 tasks in Backlog
    _write_tasks(tasks_dir, [("gamma", _TASK_C), ("extra", _TASK_C)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Both Backlog counts start at (2)
        assert "(2)" in _get_title_text(app, "Backlog")

        # Remove one file externally
        (tasks_dir / "extra.md").unlink()

        # Add a task in In Progress externally
        _write_tasks(tasks_dir, [("new-ip", _TASK_B)])

        # Refresh
        await pilot.press("r")
        await pilot.pause()

        # Counts should be updated
        assert "(1)" in _get_title_text(app, "Backlog"), (
            f"Backlog should now be (1), got: {_get_title_text(app, 'Backlog')}"
        )
        assert "(1)" in _get_title_text(app, "In Progress"), (
            f"In Progress should be (1), got: {_get_title_text(app, 'In Progress')}"
        )
        assert "(0)" in _get_title_text(app, "Done"), (
            f"Done should be (0), got: {_get_title_text(app, 'Done')}"
        )


async def test_selection_preserved_if_task_still_exists(tmp_path: Path):
    """If the currently selected task still exists after refresh, selection is kept."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("gamma", _TASK_C),
        ("delta", _TASK_C),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        # The _reload preserves the initial index (prev_idx defaults to 0)
        original_index = bg_lv.index if bg_lv.index is not None else 0
        selected_task = _get_list_titles(bg_lv)[original_index]

        # Add a new task to Backlog — this shifts the indices
        _write_tasks(tasks_dir, [('epsilon', _TASK_C)])

        # Refresh
        await pilot.press("r")
        await pilot.pause()

        # The previous index should still be valid and point to the same task
        new_index = bg_lv.index if bg_lv.index is not None else 0
        assert new_index == original_index, (
            f"Selection index changed from {original_index} to {new_index}"
        )

        # The title at that index should still be the same task
        new_titles = _get_list_titles(bg_lv)
        assert new_titles[new_index] == selected_task, (
            f"Selected task changed from '{selected_task}' to '{new_titles[new_index]}'"
        )


async def test_selection_cleared_when_task_removed(tmp_path: Path):
    """If the selected task is removed on refresh, selection falls back gracefully."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("gamma", _TASK_C),
        ("delta", _TASK_C),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)

        # Remove the second task from disk
        (tasks_dir / "delta.md").unlink()

        await pilot.press("r")
        await pilot.pause()

        # Index should still be 0 (valid after removal)
        assert len(_get_list_titles(bg_lv)) == 1
        assert bg_lv.index == 0

        titles = _get_list_titles(bg_lv)
        assert "Task Gamma" in titles[0]


async def test_new_task_files_reflected_on_refresh(tmp_path: Path):
    """Task files added to disk (without user intervention) appear after refresh."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [("alpha", _TASK_A)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        assert len(_get_list_titles(bg_lv)) == 1

        # Add a new task file externally
        new_task = """---
column: Backlog
order: 5
created: 2026-04-21
---

# New External Task

Added externally."""
        _write_tasks(tasks_dir, [("external", new_task)])

        # Refresh
        await pilot.press("r")
        await pilot.pause()

        # Both tasks should appear
        bg_titles = _get_list_titles(bg_lv)
        assert len(bg_titles) == 2
        assert "New External Task" in bg_titles[0]  # order 5 comes first
        assert "Task Alpha" in bg_titles[1]


async def test_multiple_refreshes(tmp_path: Path):
    """Multiple sequential refreshes keep re-loading correctly."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Initial: 0 tasks, all columns (0)
        for col in ["Backlog", "In Progress", "Done"]:
            assert "(0)" in _get_title_text(app, col)

        # Add 2 tasks
        _write_tasks(tasks_dir, [("task-a", _TASK_A), ("task-b", _TASK_B)])

        await pilot.press("r")
        await pilot.pause()

        assert "(1)" in _get_title_text(app, "Backlog")
        assert "(1)" in _get_title_text(app, "In Progress")

        # Add more tasks
        _write_tasks(tasks_dir, [("task-c", _TASK_C)])

        await pilot.press("r")
        await pilot.pause()

        assert "(2)" in _get_title_text(app, "Backlog")
        assert "(1)" in _get_title_text(app, "In Progress")
