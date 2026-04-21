"""E2E tests for focus switching between board and detail panes."""

import pytest
from pathlib import Path
from textual.widgets import Label, ListView
from textual.containers import VerticalScroll

from board_tui.app import BoardApp

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

_TASK_A_MD = (
    "---\n"
    "column: Backlog\n"
    "order: 10\n"
    "created: 2026-04-21\n"
    "---\n"
    "\n"
    "# Write docs\n"
    "\n"
    "API documentation."
)

_TASK_B_MD = (
    "---\n"
    "column: In Progress\n"
    "order: 10\n"
    "created: 2026-04-21\n"
    "---\n"
    "\n"
    "# Build dashboard\n"
    "\n"
    "Main dashboard UI."
)

_TASK_C_MD = (
    "---\n"
    "column: Done\n"
    "order: 10\n"
    "created: 2026-04-21\n"
    "---\n"
    "\n"
    "# CI pipeline\n"
    "\n"
    "GitHub Actions config."
)


def _write_tasks(tasks_dir: Path, entries: list[tuple[str, str]]) -> None:
    """Write task markdown files into the given directory."""
    for slug, content in entries:
        tasks_dir.joinpath(f"{slug}.md").write_text(content)


def _make_app(tasks_dir: Path, user: str = "alice") -> BoardApp:
    """Create a BoardApp bound to a specific tasks directory."""
    return BoardApp(
        tasks_dir=str(tasks_dir),
        columns=["Backlog", "In Progress", "Done"],
        user=user,
    )


def _slugify(s: str) -> str:
    import re
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s[:70]


# ---------------------------------------------------------------------------
# Requirement 1: 'tab' switches focus from board to detail
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tab_board_to_detail(tmp_path: Path):
    """Pressing tab from board should move focus to the detail pane."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("task-a", _TASK_A_MD),
        ("task-b", _TASK_B_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Initially on the board
        assert app.focus_side == "board"

        # Press tab once
        await pilot.press("tab")
        await pilot.pause()

        # Focus should have switched to detail
        assert app.focus_side == "detail", (
            f"After first tab, expected focus_side='detail', got '{app.focus_side}'"
        )

        # The detail VerticalScroll should be the focused widget
        focused = app.focused
        assert focused is not None
        assert isinstance(focused, VerticalScroll), (
            f"Expected VerticalScroll after tab, got {type(focused).__name__}"
        )
        assert focused.id == "detail-scroll"


# ---------------------------------------------------------------------------
# Requirement 2: 'tab' switches focus from detail to board
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tab_detail_to_board(tmp_path: Path):
    """Pressing tab from detail should move focus back to the board."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("task-a", _TASK_A_MD),
        ("task-b", _TASK_B_MD),
        ("task-c", _TASK_C_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Move to detail
        await pilot.press("tab")
        await pilot.pause()
        assert app.focus_side == "detail"

        # Press tab again
        await pilot.press("tab")
        await pilot.pause()

        # Should be back on the board
        assert app.focus_side == "board", (
            f"After second tab, expected focus_side='board', got '{app.focus_side}'"
        )

        # The focused widget should be inside the board pane (a ListView)
        focused = app.focused
        assert focused is not None
        assert isinstance(focused, ListView), (
            f"Expected ListView after tab, got {type(focused).__name__}"
        )


# ---------------------------------------------------------------------------
# Requirement 3: Column titles show active state when board focused
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_column_title_active_state_when_board_focused(tmp_path: Path):
    """Column title should have column-title-active class when board is focused."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("task-a", _TASK_A_MD),
        ("task-b", _TASK_B_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Initially on board, so Backlog (first column) should be active
        bl_title = app.query_one("#title-backlog", Label)
        assert "column-title-active" in bl_title.classes, (
            f"Backlog title should have column-title-active class: {bl_title.classes}"
        )
        assert "column-title" not in bl_title.classes

        # In Progress title should NOT be active
        ip_title = app.query_one("#title-in-progress", Label)
        assert "column-title-active" not in ip_title.classes
        assert "column-title" in ip_title.classes


# ---------------------------------------------------------------------------
# Requirement 4: Detail header shows focus indicator when detail focused
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_detail_header_focus_indicator(tmp_path: Path):
    """Detail header should show carets (▾ ) when detail pane is focused."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("task-a", _TASK_A_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Initially on board, no carets
        header = app.query_one("#detail-header", Label)
        assert "▾ " not in header.content, (
            f"Header should not show carets when on board: '{header.content}'"
        )

        # Switch to detail
        await pilot.press("tab")
        await pilot.pause()

        # Now detail header should show focus indicator
        header = app.query_one("#detail-header", Label)
        assert "▾ " in header.content, (
            f"Header should show carets when detail is focused: '{header.content}'"
        )


@pytest.mark.asyncio
async def test_detail_header_caret_removed_when_board_focused(tmp_path: Path):
    """Detail header should remove the focus caret indicator when focus returns to board."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("task-b", _TASK_B_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Go to detail
        await pilot.press("tab")
        await pilot.pause()
        assert "▾ " in app.query_one("#detail-header", Label).content

        # Return to board
        await pilot.press("tab")
        await pilot.pause()
        assert app.focus_side == "board"

        # Caret should be gone again
        assert "▾ " not in app.query_one("#detail-header", Label).content, (
            "Header should not show carets when board is focused"
        )


# ---------------------------------------------------------------------------
# Requirement 5: ListView focusable only when board focused
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_listview_focusable_on_board(tmp_path: Path):
    """ListView in the current column should be focusable when board is focused."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("task-a", _TASK_A_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        assert app.focus_side == "board"

        # The first column's ListView should be the focused widget
        bg_lv = app.query_one("#list-backlog", ListView)
        assert bg_lv.has_focus, "Backlog ListView should have focus on mount"
        assert bg_lv.focusable, "Backlog ListView should be focusable"


@pytest.mark.asyncio
async def test_listview_not_focused_when_detail_view_active(tmp_path: Path):
    """ListView should not have focus when detail pane is focused."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("task-a", _TASK_A_MD),
        ("task-b", _TASK_B_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Verify ListView starts focused
        bg_lv = app.query_one("#list-backlog", ListView)
        assert bg_lv.has_focus

        # Switch to detail
        await pilot.press("tab")
        await pilot.pause()
        assert app.focus_side == "detail"

        # ListView should no longer be focused
        assert not bg_lv.has_focus, "ListView should lose focus when switching to detail"


# ---------------------------------------------------------------------------
# Requirement 6: VerticalScroll focusable only when detail focused
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_vertical_scroll_focusable_on_detail(tmp_path: Path):
    """VerticalScroll in detail should become focused when detail is active."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("task-a", _TASK_A_MD), ("task-b", _TASK_B_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        detail_scroll = app.query_one("#detail-scroll", VerticalScroll)
        assert not detail_scroll.has_focus, (
            "Detail scroll should not be focused on initially on board"
        )

        # Switch to detail
        await pilot.press("tab")
        await pilot.pause()

        # Now VerticalScroll should be the focused widget
        assert detail_scroll.has_focus, (
            "Detail VerticalScroll should become focused after tab"
        )


@pytest.mark.asyncio
async def test_vertical_scroll_not_focused_on_board(tmp_path: Path):
    """VerticalScroll should lose focus when board becomes active again."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("task-c", _TASK_C_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        detail_scroll = app.query_one("#detail-scroll", VerticalScroll)

        # Switch to detail (scroll gets focus)
        await pilot.press("tab")
        await pilot.pause()
        assert detail_scroll.has_focus

        # Switch back to board (scroll loses focus)
        await pilot.press("tab")
        await pilot.pause()
        assert app.focus_side == "board"
        assert not detail_scroll.has_focus, (
            "Detail VerticalScroll should lose focus when board is focused"
        )


# ---------------------------------------------------------------------------
# Additional: Tab cycling — round-trip consistency
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tab_cycle_board_to_detail_to_board(tmp_path: Path):
    """Full tab cycle: board → detail → board preserves state consistency."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("task-a", _TASK_A_MD),
        ("task-b", _TASK_B_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        bl_title = app.query_one("#title-backlog", Label)
        detail_scroll = app.query_one("#detail-scroll", VerticalScroll)
        header = app.query_one("#detail-header", Label)

        # Initial board state
        assert app.focus_side == "board"
        assert bg_lv.has_focus
        assert not detail_scroll.has_focus
        assert "column-title-active" in bl_title.classes
        assert "▾ " not in header.content

        # Tab → detail
        await pilot.press("tab")
        await pilot.pause()

        assert app.focus_side == "detail"
        assert not bg_lv.has_focus
        assert detail_scroll.has_focus
        assert "column-title-active" not in bl_title.classes
        assert "▾ " in header.content

        # Tab → back to board
        await pilot.press("tab")
        await pilot.pause()

        assert app.focus_side == "board"
        assert bg_lv.has_focus
        assert not detail_scroll.has_focus
        assert "column-title-active" in bl_title.classes
        assert "▾ " not in header.content


@pytest.mark.asyncio
async def test_multiple_tabs_cycle(tmp_path: Path):
    """Pressing tab multiple times cycles correctly through board↔detail."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [("task-a", _TASK_A_MD)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        header = app.query_one("#detail-header", Label)

        # Press 0: board, no caret
        assert app.focus_side == "board"
        assert "▾ " not in header.content

        # Press 1 → detail
        await pilot.press("tab")
        await pilot.pause()
        assert app.focus_side == "detail"
        assert "▾ " in header.content

        # Press 2 → board
        await pilot.press("tab")
        await pilot.pause()
        assert app.focus_side == "board"
        assert "▾ " not in header.content

        # Press 3 → detail
        await pilot.press("tab")
        await pilot.pause()
        assert app.focus_side == "detail"
        assert "▾ " in header.content

        # Press 4 → board
        await pilot.press("tab")
        await pilot.pause()
        assert app.focus_side == "board"
        assert "▾ " not in header.content

        # Press 5 → detail
        await pilot.press("tab")
        await pilot.pause()
        assert app.focus_side == "detail"
        assert "▾ " in header.content


@pytest.mark.asyncio
async def test_right_arrow_moves_column_under_board_focus(tmp_path: Path):
    """While board is focused, right arrow changes the active column."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()
    _write_tasks(tasks_dir, [
        ("task-a", _TASK_A_MD),
        ("task-b", _TASK_B_MD),
        ("task-c", _TASK_C_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Initially Backlog is active
        bl_title = app.query_one("#title-backlog", Label)
        assert "column-title-active" in bl_title.classes

        # Right arrow → In Progress
        await pilot.press("right")
        await pilot.pause()

        ip_title = app.query_one("#title-in-progress", Label)
        assert "column-title-active" in ip_title.classes
        assert "column-title-active" not in bl_title.classes

        # Right arrow → Done
        await pilot.press("right")
        await pilot.pause()

        done_title = app.query_one("#title-done", Label)
        assert "column-title-active" in done_title.classes

        # Right arrow wraps to Backlog
        await pilot.press("right")
        await pilot.pause()

        assert "column-title-active" in bl_title.classes
