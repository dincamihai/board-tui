"""E2E tests for BoardApp rendering via Textual's App.run_test() framework."""

import os
import pytest
from pathlib import Path
from textual.widgets import Label, ListView

from board_tui.app import BoardApp


# ---------------------------------------------------------------------------
# Fixtures: Task markdown content with proper # headings
# ---------------------------------------------------------------------------

_TASK_A_MD = """---
column: In Progress
order: 20
assigned: alice
created: 2026-04-21
---

# Build the dashboard

Design and implement the main dashboard view."""

_TASK_B_MD = """---
column: Backlog
order: 10
created: 2026-04-20
---

# Write documentation

Add API docs."""

_TASK_C_MD = """---
column: Backlog
order: 30
created: 2026-04-19
---

# Set up CI pipeline

Configure GitHub Actions."""

_TASK_D_MD = """---
column: In Progress
order: 10
created: 2026-04-18
---

# Fix login bug

Users cannot log in with special chars."""


def _make_app(tasks_dir: Path, user: str = "alice") -> BoardApp:
    """Create a BoardApp bound to the given tasks directory."""
    return BoardApp(
        tasks_dir=str(tasks_dir),
        columns=["Backlog", "In Progress", "Done"],
        user=user,
    )


def slugify(s: str) -> str:
    """Minimal slugify for test assertions."""
    import re
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s[:70]


def _write_tasks(tasks_dir: Path, entries: list[tuple[str, str]]) -> None:
    """Write multiple task markdown files.

    Each *entries* item is ``(slug, content)`` where *content* is the full
    markdown text with frontmatter.
    """
    for slug, content in entries:
        tasks_dir.joinpath(f"{slug}.md").write_text(content)


def _get_list_titles(lv: ListView) -> list[str]:
    """Return the text content string of each ListItem in a ListView."""
    titles: list[str] = []
    for child in lv.children:
        if hasattr(child, "children") and child.children:
            titles.append(child.children[0].content)
    return titles


def _get_title_text(app: BoardApp, col: str) -> str:
    """Return the rendered text of a column title widget."""
    lbl = app.query_one(f"#title-{slugify(col)}", Label)
    return lbl.content


# ---------------------------------------------------------------------------
# Test: Empty .tasks dir shows empty columns with (0) counts
# ---------------------------------------------------------------------------

async def test_empty_tasks_dir_shows_zero_counts(tmp_path: Path):
    """An empty .tasks directory should render every column with a (0) count."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    # No .md files inside

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Check each column title has "(0)"
        for col in ["Backlog", "In Progress", "Done"]:
            title_text = _get_title_text(app, col)
            assert "(0)" in title_text, f"Column {col} should show (0) count, got: {title_text}"

        # Verify each ListView has zero items
        for col in ["Backlog", "In Progress", "Done"]:
            lv = app.query_one(f"#list-{slugify(col)}", ListView)
            assert len(lv.children) == 0, f"ListView for {col} should be empty"


# ---------------------------------------------------------------------------
# Test: Tasks appear in correct columns based on frontmatter
# ---------------------------------------------------------------------------

async def test_tasks_in_correct_columns(tmp_path: Path):
    """Tasks with different frontmatter columns land in the right ListView."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(
        tasks_dir,
        [
            ("fix-login", _TASK_D_MD),
            ("dashboard", _TASK_A_MD),
            ("docs", _TASK_B_MD),
            ("ci", _TASK_C_MD),
        ],
    )

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Backlog: docs, ci (order 10 before 30)
        backlog_lv = app.query_one("#list-backlog", ListView)
        backlog_titles = _get_list_titles(backlog_lv)
        assert len(backlog_titles) == 2, f"Backlog should have 2 tasks, got: {backlog_titles}"
        assert "Write documentation" in backlog_titles[0]
        assert "Set up CI pipeline" in backlog_titles[1]

        # In Progress: fix-login, dashboard (order 10 before 20)
        ip_lv = app.query_one("#list-in-progress", ListView)
        ip_titles = _get_list_titles(ip_lv)
        assert len(ip_titles) == 2, "In Progress should have exactly 2 tasks"
        assert "Fix login bug" in ip_titles[0]
        assert "Build the dashboard" in ip_titles[1]


# ---------------------------------------------------------------------------
# Test: Column counts update correctly
# ---------------------------------------------------------------------------

async def test_column_counts_update_after_add(tmp_path: Path):
    """Adding a task file should increase the column count on next load."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    # Start with one task in Backlog
    _write_tasks(tasks_dir, [("doc", _TASK_B_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Verify initial count is (1)
        assert "(1)" in _get_title_text(app, "Backlog"), (
            "Initial Backlog count should be (1)"
        )

        # Add a second task also in Backlog
        _write_tasks(tasks_dir, [("ci", _TASK_C_MD)])

        # Simulate a refresh key press
        await pilot.press("r")
        await pilot.pause()

        # After reload, Backlog should show (2)
        assert "(2)" in _get_title_text(app, "Backlog"), (
            f"Backlog count should update to (2)"
        )


# ---------------------------------------------------------------------------
# Test: Task titles display with prefix (• or ♦ for mine)
# ---------------------------------------------------------------------------

async def test_task_titles_show_mine_prefix(tmp_path: Path):
    """Tasks assigned to the current user show ♦ prefix; others show •."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(
        tasks_dir,
        [
            ("mine", _TASK_A_MD),  # assigned: alice
            ("yours", _TASK_B_MD),  # no assigned field
        ],
    )

    # User = alice → alice's task gets ♦, others get •
    app = _make_app(tasks_dir, user="alice")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        all_titles = _get_list_titles(app.query_one("#list-backlog", ListView))
        all_titles.extend(
            _get_list_titles(app.query_one("#list-in-progress", ListView))
        )

        # "mine" task (assigned: alice, user=alice) should have ♦
        mine_item = [t for t in all_titles if "Build the dashboard" in t]
        assert len(mine_item) == 1
        assert mine_item[0].startswith("♦"), (
            f"Mine task should start with ♦: {mine_item[0]}"
        )

        # "yours" task (no assigned) should have •
        yours_items = [t for t in all_titles if "Write documentation" in t]
        assert len(yours_items) == 1
        assert yours_items[0].startswith("•"), (
            f"Non-mine task should start with •: {yours_items[0]}"
        )


async def test_task_titles_no_mine_when_user_differs(tmp_path: Path):
    """When no tasks are assigned to the user, ALL tasks show • (not ♦)."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(
        tasks_dir,
        [
            ("alice-task", _TASK_A_MD),  # assigned: alice
            ("bob-task", _TASK_B_MD),     # no assigned
        ],
    )

    # User = bob → nobody's task is "mine"
    app = _make_app(tasks_dir, user="bob")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        all_titles = _get_list_titles(app.query_one("#list-backlog", ListView))
        all_titles.extend(
            _get_list_titles(app.query_one("#list-in-progress", ListView))
        )

        for item in all_titles:
            assert item.startswith("•"), (
                f"Item '{item}' should start with • when user is bob"
            )
            assert not item.startswith("♦"), (
                f"Item '{item}' should not have ♦ when user is bob"
            )


# ---------------------------------------------------------------------------
# Test: Order is respected (lower order = higher in list)
# ---------------------------------------------------------------------------

async def test_order_is_respected_within_column(tmp_path: Path):
    """Tasks in the same column are ordered by `order` ascending (lower = higher)."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    # Three tasks all in In Progress with different order values
    task1 = """---
column: In Progress
order: 50
created: 2026-04-21
---

# Old task

Body of the old task."""

    task2 = """---
column: In Progress
order: 10
created: 2026-04-20
---

# First task

Body of the first task."""

    task3 = """---
column: In Progress
order: 30
created: 2026-04-19
---

# Middle task

Body of the middle task."""

    _write_tasks(
        tasks_dir,
        [
            ("old-task", task1),     # order 50, should be last
            ("first-task", task2),   # order 10, should be first
            ("middle-task", task3),  # order 30, should be second
        ],
    )

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        ip_lv = app.query_one("#list-in-progress", ListView)
        titles = _get_list_titles(ip_lv)
        assert len(titles) == 3, "In Progress should have 3 tasks"

        # Lower order = higher in the list
        assert "First task" in titles[0], (
            f"First task (order=10) should be at index 0, got: {titles}"
        )
        assert "Middle task" in titles[1], (
            f"Middle task (order=30) should be at index 1, got: {titles}"
        )
        assert "Old task" in titles[2], (
            f"Old task (order=50) should be at index 2, got: {titles}"
        )


async def test_order_across_columns_no_cross_contamination(tmp_path: Path):
    """Order only applies within a single column — columns are independent."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    high_order_in_backlog = """---
column: Backlog
order: 100
created: 2026-04-21
---

# High order backlog

This is backlog."""

    low_order_in_done = """---
column: Done
order: 5
created: 2026-04-20
---

# Low order done

This is done."""

    _write_tasks(
        tasks_dir,
        [
            ("high-bg", high_order_in_backlog),
            ("low-done", low_order_in_done),
        ],
    )

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        done_lv = app.query_one("#list-done", ListView)

        # Each column has exactly one task
        assert len(bg_lv.children) == 1
        assert len(done_lv.children) == 1

        # The single items should be correct regardless of order
        bg_titles = _get_list_titles(bg_lv)
        done_titles = _get_list_titles(done_lv)
        assert "High order backlog" in bg_titles[0]
        assert "Low order done" in done_titles[0]


# ---------------------------------------------------------------------------
# Test: Navigation keys change columns and update counts
# ---------------------------------------------------------------------------

async def test_tab_navigation_updates_active_column(tmp_path: Path):
    """Pressing Tab switches focus and updates active column title styling."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [("task1", _TASK_B_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # The first column (Backlog) should have the active class
        bl_title = app.query_one("#title-backlog", Label)
        assert "column-title-active" in bl_title.classes

        # Press Tab to move to detail pane
        await pilot.press("tab")
        await pilot.pause()

        # Detail pane should now be focused
        detail_header = app.query_one("#detail-header", Label)
        assert "▾ " in detail_header.content, (
            "Should show active caret in detail mode"
        )


# ---------------------------------------------------------------------------
# Test: Assigned tasks show correct prefix for other user
# ---------------------------------------------------------------------------

async def test_assigned_tasks_prefix_for_other_user(tmp_path: Path):
    """A task assigned to alice should show • when viewed as bob."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [("alice-task", _TASK_A_MD)])

    app = _make_app(tasks_dir, user="bob")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        ip_lv = app.query_one("#list-in-progress", ListView)
        assert len(ip_lv.children) == 1
        titles = _get_list_titles(ip_lv)
        assert titles[0].startswith("•"), (
            f"Task assigned to alice should show • when user is bob: {titles[0]}"
        )
        assert "Build the dashboard" in titles[0]


# ---------------------------------------------------------------------------
# Test: Multiple tasks in same backlogged column respect order
# ---------------------------------------------------------------------------

async def test_multiple_tasks_backlog_order(tmp_path: Path):
    """Multiple tasks in the Backlog column are ordered by `order`."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    t1 = """---
column: Backlog
order: 50
created: 2026-04-21
---

# Task Zeta

Body."""

    t2 = """---
column: Backlog
order: 10
created: 2026-04-20
---

# Task Alpha

Body."""

    t3 = """---
column: Backlog
order: 30
created: 2026-04-19
---

# Task Beta

Body."""

    _write_tasks(
        tasks_dir,
        [
            ("task-zeta", t1),
            ("task-alpha", t2),
            ("task-beta", t3),
        ],
    )

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        titles = _get_list_titles(bg_lv)
        assert len(titles) == 3

        assert "Task Alpha" in titles[0]
        assert "Task Beta" in titles[1]
        assert "Task Zeta" in titles[2]


# ---------------------------------------------------------------------------
# Test: No .tasks directory at all — graceful empty state
# ---------------------------------------------------------------------------

async def test_missing_tasks_dir_graceful(tmp_path: Path):
    """If the .tasks directory doesn't exist, the app should still render empty columns."""
    tasks_dir = tmp_path / ".tasks"  # Don't mkdir — directory does not exist

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        for col in ["Backlog", "In Progress", "Done"]:
            title_text = _get_title_text(app, col)
            assert "(0)" in title_text, (
                f"Column {col} should show (0) when dir is missing"
            )

            lv = app.query_one(f"#list-{slugify(col)}", ListView)
            assert len(lv.children) == 0, f"ListView for {col} should be empty"
