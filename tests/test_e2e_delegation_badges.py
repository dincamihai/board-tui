"""E2E tests for delegation status badges in BoardApp.

Tests delegation status prefix rendering in list view and detail panel.

* queued  → ⏳ prefix
* processing → ▶ prefix
* done → ✓ prefix
* absent → • or ♦ prefix (normal behavior)
"""

import pytest
from pathlib import Path
from textual.widgets import ListView, Markdown

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

Waiting for agent.
"""

_TASK_PROCESSING = """---
column: In Progress
order: 10
created: 2026-04-21
delegation_status: processing
---

# Processing task

Agent is running.
"""

_TASK_DONE = """---
column: Done
order: 10
created: 2026-04-21
delegation_status: done
---

# Done task

Agent completed.
"""

_TASK_NO_DELEGATION = """---
column: Backlog
order: 10
created: 2026-04-21
---

# Regular task

No delegation.
"""

_TASK_MINE_AND_QUEUED = """---
column: Backlog
order: 10
created: 2026-04-21
assigned: alice
delegation_status: queued
---

# Mine and queued

Both flags set.
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


def _get_markdown_text(md: Markdown) -> str:
    return md.markdown if hasattr(md, "markdown") else ""


# ---------------------------------------------------------------------------
# Tests: list view prefixes
# ---------------------------------------------------------------------------

async def test_queued_task_shows_clock_prefix(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("queued", _TASK_QUEUED)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        lv = app.query_one("#list-backlog", ListView)
        titles = _get_list_titles(lv)
        assert titles[0].startswith("⏳")


async def test_processing_task_shows_play_prefix(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("processing", _TASK_PROCESSING)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        lv = app.query_one("#list-in-progress", ListView)
        titles = _get_list_titles(lv)
        assert titles[0].startswith("▶")


async def test_done_task_shows_check_prefix(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("done", _TASK_DONE)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        lv = app.query_one("#list-done", ListView)
        titles = _get_list_titles(lv)
        assert titles[0].startswith("✓")


async def test_no_delegation_shows_bullet_prefix(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("regular", _TASK_NO_DELEGATION)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        lv = app.query_one("#list-backlog", ListView)
        titles = _get_list_titles(lv)
        assert titles[0].startswith("•")


async def test_delegation_status_wins_over_mine_prefix(tmp_path: Path):
    """When both mine and delegation_status set, delegation prefix wins."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("mine-queued", _TASK_MINE_AND_QUEUED)])

    app = _make_app(tasks_dir, user="alice")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        lv = app.query_one("#list-backlog", ListView)
        titles = _get_list_titles(lv)
        assert titles[0].startswith("⏳")


# ---------------------------------------------------------------------------
# Tests: detail panel shows delegation_status
# ---------------------------------------------------------------------------

async def test_detail_shows_delegation_status(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("queued", _TASK_QUEUED)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        body = app.query_one("#detail-body", Markdown)
        md_text = body._markdown
        assert "**delegation_status**: queued" in md_text


async def test_detail_shows_all_delegation_states(tmp_path: Path):
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("queued", _TASK_QUEUED),
        ("processing", _TASK_PROCESSING),
        ("done", _TASK_DONE),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Select each task and verify detail
        for slug, expected in [("queued", "queued"), ("processing", "processing"), ("done", "done")]:
            # Navigate to task (all in different columns)
            col_map = {"queued": "Backlog", "processing": "In Progress", "done": "Done"}
            col = col_map[slug]
            col_idx = app._columns.index(col)
            app._focus_column(col_idx)
            await pilot.pause()

            body = app.query_one("#detail-body", Markdown)
            md_text = body._markdown
            assert f"**delegation_status**: {expected}" in md_text
