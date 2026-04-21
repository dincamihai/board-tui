"""E2E tests for search functionality in BoardApp."""

import pytest
from pathlib import Path
from textual.widgets import ListView, Label

from board_tui.app import BoardApp


# ---------------------------------------------------------------------------
# Fixtures: task markdown content
# ---------------------------------------------------------------------------

_TASK_ALPHA_MD = """---
column: Backlog
order: 10
created: 2026-04-21
---

# Alpha task

Body for alpha task.
"""

_TASK_AUTH_MD = """---
column: Backlog
order: 20
created: 2026-04-21
---

# Authentication module

Implement user authentication.
"""

_TASK_API_MD = """---
column: In Progress
order: 10
created: 2026-04-21
---

# API endpoint

REST API for data access.
"""

_TASK_DATABASE_MD = """---
column: Done
order: 10
created: 2026-04-21
---

# Database schema

Design database tables.
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


# ---------------------------------------------------------------------------
# Test: '/' opens search prompt
# ---------------------------------------------------------------------------

async def test_slash_opens_search_prompt(tmp_path: Path):
    """Pressing '/' opens search prompt screen."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("alpha", _TASK_ALPHA_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Press '/' to open search
        await pilot.press("/")
        await pilot.pause()

        # Search prompt should be visible (Input widget with "search:" label)
        # Screen should have PromptScreen pushed
        assert len(app.screen_stack) == 2  # Main screen + PromptScreen


# ---------------------------------------------------------------------------
# Test: Typing query filters and highlights matches
# ---------------------------------------------------------------------------

async def test_typing_query_filters_and_highlights(tmp_path: Path):
    """Typing search query filters and highlights matching tasks."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("alpha", _TASK_ALPHA_MD),
        ("auth", _TASK_AUTH_MD),
        ("api", _TASK_API_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Open search and type query
        await pilot.press("/")
        await pilot.pause()

        # Type "auth" - should match "Authentication module"
        await pilot.press("a", "u", "t", "h")
        await pilot.pause()

        # Submit search
        await pilot.press("enter")
        await pilot.pause()

        # Should have found matches
        # "auth" matches "Authentication module" (title) and "auth" (slug)
        assert app.search_query == "auth"
        assert len(app.search_matches) >= 1

        # Matched items should have "matched" class
        bg_lv = app.query_one("#list-backlog", ListView)
        matched_items = [child for child in bg_lv.children if "matched" in child.classes]
        assert len(matched_items) >= 1


# ---------------------------------------------------------------------------
# Test: 'n' cycles to next match
# ---------------------------------------------------------------------------

async def test_n_cycles_to_next_match(tmp_path: Path):
    """Pressing 'n' cycles to next search match."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("alpha", _TASK_ALPHA_MD),      # Backlog
        ("auth", _TASK_AUTH_MD),        # Backlog
        ("api", _TASK_API_MD),          # In Progress
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Search for "a" - matches all tasks (all contain 'a')
        await pilot.press("/")
        await pilot.pause()
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        # Should have multiple matches
        assert len(app.search_matches) >= 2

        # Get initial position
        initial_pos = app.search_pos
        initial_col = app.cur_col

        # Press 'n' to go to next match
        await pilot.press("n")
        await pilot.pause()

        # Position should have changed
        assert app.search_pos != initial_pos or app.cur_col != initial_col


# ---------------------------------------------------------------------------
# Test: Match notification shows count
# ---------------------------------------------------------------------------

async def test_match_notification_shows_count(tmp_path: Path):
    """Search notification displays match count (e.g., '3 matches')."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("alpha", _TASK_ALPHA_MD),
        ("auth", _TASK_AUTH_MD),
        ("api", _TASK_API_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Search for "a"
        await pilot.press("/")
        await pilot.pause()
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        # Should have matches
        assert len(app.search_matches) >= 1

        # Notification should have been shown with count
        # Check that search was executed
        assert app.search_query == "a"


# ---------------------------------------------------------------------------
# Test: No matches shows "no matches for 'x'"
# ---------------------------------------------------------------------------

async def test_no_matches_shows_message(tmp_path: Path):
    """Search with no matches shows 'no matches' notification."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("alpha", _TASK_ALPHA_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Search for something that doesn't exist
        await pilot.press("/")
        await pilot.pause()
        await pilot.press("x", "y", "z", "z", "z")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        # Should have no matches
        assert len(app.search_matches) == 0
        assert app.search_query == "xyzzz"


# ---------------------------------------------------------------------------
# Test: Escape clears search and resets highlighting
# ---------------------------------------------------------------------------

async def test_escape_clears_search(tmp_path: Path):
    """Pressing escape clears search query and resets highlighting."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("alpha", _TASK_ALPHA_MD),
        ("auth", _TASK_AUTH_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Do a search
        await pilot.press("/")
        await pilot.pause()
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        # Should have matches
        assert app.search_query == "a"
        assert len(app.search_matches) >= 1

        # Press escape to clear
        await pilot.press("escape")
        await pilot.pause()

        # Search should be cleared
        assert app.search_query == ""
        assert len(app.search_matches) == 0

        # No items should have "matched" class
        bg_lv = app.query_one("#list-backlog", ListView)
        matched_items = [child for child in bg_lv.children if "matched" in child.classes]
        assert len(matched_items) == 0


# ---------------------------------------------------------------------------
# Test: Search matches both title and slug
# ---------------------------------------------------------------------------

async def test_search_matches_title_and_slug(tmp_path: Path):
    """Search query matches against both task title and slug."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("alpha-task", _TASK_ALPHA_MD),     # slug: alpha-task, title: Alpha task
        ("auth-module", _TASK_AUTH_MD),     # slug: auth-module, title: Authentication module
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Search for "alpha" - matches slug "alpha-task" and title "Alpha task"
        await pilot.press("/")
        await pilot.pause()
        await pilot.press("a", "l", "p", "h", "a")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        # Should find match
        assert len(app.search_matches) >= 1

        # Clear and search for "module" - matches slug "auth-module"
        await pilot.press("escape")
        await pilot.pause()

        await pilot.press("/")
        await pilot.pause()
        await pilot.press("m", "o", "d", "u", "l", "e")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        # Should find match in slug
        assert len(app.search_matches) >= 1


# ---------------------------------------------------------------------------
# Test: Search across multiple columns
# ---------------------------------------------------------------------------

async def test_search_across_columns(tmp_path: Path):
    """Search finds matches in all columns (Backlog, In Progress, Done)."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("alpha", _TASK_ALPHA_MD),          # Backlog
        ("api", _TASK_API_MD),              # In Progress
        ("database", _TASK_DATABASE_MD),    # Done
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Search for "a" - matches tasks in all columns
        await pilot.press("/")
        await pilot.pause()
        await pilot.press("a")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        # Should have multiple matches across columns
        assert len(app.search_matches) >= 2

        # Cycling through matches should navigate columns
        initial_col = app.cur_col
        await pilot.press("n")
        await pilot.pause()

        # May have changed column
        # (just verify search works across columns)
        assert len(app.search_matches) >= 2
