"""E2E tests for mine highlighting in BoardApp.

Tests the ``mine()`` function and UI highlighting behaviour:

* Tasks with ``assigned=user`` show ♦ prefix and "mine" class.
* Tasks with a ``[human]`` title prefix are treated as mine.
* Other tasks show • prefix (no "mine" class).
* ``--user`` CLI flag changes which tasks are highlighted.
* ``BOARD_TUI_USER`` env var sets the user for highlighting.

Uses ``App.run_test()`` with async pilots like the other E2E tests.
"""

import os
import re
from pathlib import Path

import pytest
from textual.widgets import ListView

from board_tui.app import BoardApp
from board_tui.cli import resolve_config
from board_tui.tasks import mine


# ======================================================================
# Fixtures / task templates
# ======================================================================

_TASK_ASSIGNED_ALICE = """---
column: In Progress
order: 10
assigned: alice
created: 2026-04-21
---

# Build the dashboard

Design and implement the main dashboard view."""

_TASK_NO_ASSIGNMENT = """---
column: Backlog
order: 10
created: 2026-04-20
---

# Write documentation

Add API docs."""

_TASK_ASSIGNED_BOB = """---
column: Backlog
order: 20
assigned: bob
created: 2026-04-21
---

# Fix login bug

Users cannot log in with special chars."""

_TASK_HUMAN_PREFIX = """---
column: In Progress
order: 30
created: 2026-04-19
---

# [human] Manual testing

Needs manual QA before merging."""


def _make_app(tasks_dir: Path, user: str = "alice", **kwargs) -> BoardApp:
    """Create a BoardApp with default columns."""
    return BoardApp(
        tasks_dir=str(tasks_dir),
        columns=["Backlog", "In Progress", "Done"],
        user=user,
        **kwargs,
    )


def _write_tasks(tasks_dir: Path, entries: list[tuple[str, str]]) -> None:
    """Write task markdown files into the given directory."""
    tasks_dir.mkdir(parents=True, exist_ok=True)
    for slug, content in entries:
        tasks_dir.joinpath(f"{slug}.md").write_text(content)


def _slugify(s: str) -> str:
    """Minimal slugify matching board_tui.tasks.slugify."""
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s[:70]


def _get_list_titles(lv: ListView) -> list[str]:
    """Return the text content string of each ListItem in a ListView."""
    titles: list[str] = []
    for child in lv.children:
        if hasattr(child, "children") and child.children:
            titles.append(child.children[0].content)
    return titles


def _get_list_classes(lv: ListView) -> list[list[str]]:
    """Return the CSS classes of each ListItem in a ListView."""
    classes_set: list[list[str]] = []
    for child in lv.children:
        classes_set.append(list(child.classes))
    return classes_set


def _list_view_for_col(app: BoardApp, col: str) -> ListView:
    """Get the ListView widget for a column by human-readable name."""
    return app.query_one(f"#list-{_slugify(col)}", ListView)


# ======================================================================
# Tests — pure mine() function (no UI)
# ======================================================================

async def test_mine_function_assigned_matches_user():
    """:func:`mine()` returns True when task's assigned field matches user."""
    task = {
        "fm": {"assigned": "alice"},
        "title": "Build the dashboard",
    }
    assert mine(task, "alice") is True
    assert mine(task, "Alice") is True   # case-insensitive
    assert mine(task, "bob") is False


async def test_mine_function_human_prefix():
    """:func:`mine()` returns True for tasks whose title starts with [human]."""
    task_human = {"fm": {}, "title": "[human] Manual testing"}
    assert mine(task_human, "alice") is True
    assert mine(task_human, "bob") is True  # human prefix matches everyone

    task_regular = {"fm": {}, "title": "Manual testing"}
    assert mine(task_regular, "alice") is False
    assert mine(task_regular, "bob") is False


async def test_mine_function_neither_matches():
    """:func:`mine()` returns False when neither assigned nor [human] match."""
    task = {"fm": {}, "title": "Simple task"}
    assert mine(task, "anyone") is False

    task2 = {"fm": {"assigned": "charlie"}, "title": "Other task"}
    assert mine(task2, "alice") is False


# ======================================================================
# Tests — UI: ♦ prefix + "mine" class for assigned tasks
# ======================================================================

async def test_assigned_task_shows_diamond_prefix(tmp_path: Path):
    """A task with ``assigned: alice`` shown to ``alice`` gets a ♦ prefix."""
    tasks_dir = tmp_path / ".tasks"
    _write_tasks(tasks_dir, [("dashboard", _TASK_ASSIGNED_ALICE)])

    app = _make_app(tasks_dir, user="alice")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        ip_lv = _list_view_for_col(app, "In Progress")
        assert len(ip_lv.children) == 1
        titles = _get_list_titles(ip_lv)
        assert titles[0].startswith("♦")


async def test_assigned_task_shows_mine_class(tmp_path: Path):
    """A task with ``assigned: alice`` shown to ``alice`` carries the "mine" class."""
    tasks_dir = tmp_path / ".tasks"
    _write_tasks(tasks_dir, [("dashboard", _TASK_ASSIGNED_ALICE)])

    app = _make_app(tasks_dir, user="alice")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        ip_lv = _list_view_for_col(app, "In Progress")
        classes = _get_list_classes(ip_lv)
        assert "mine" in classes[0]


async def test_non_assigned_task_does_not_have_mine_class(tmp_path: Path):
    """A task without an ``assigned`` field has no "mine" class."""
    tasks_dir = tmp_path / ".tasks"
    _write_tasks(tasks_dir, [("docs", _TASK_NO_ASSIGNMENT)])

    app = _make_app(tasks_dir, user="alice")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = _list_view_for_col(app, "Backlog")
        assert len(bg_lv.children) == 1
        titles = _get_list_titles(bg_lv)
        classes = _get_list_classes(bg_lv)

        assert titles[0].startswith("•"), (
            f"Non-assigned task should use •: {titles[0]}"
        )
        assert "mine" not in classes[0]


# ======================================================================
# Tests — UI: [human] prefix treated as mine
# ======================================================================

async def test_human_prefix_shows_diamond(tmp_path: Path):
    """A task with a ``[human]`` title prefix shows ♦ when viewed."""
    tasks_dir = tmp_path / ".tasks"
    _write_tasks(tasks_dir, [("manual-test", _TASK_HUMAN_PREFIX)])

    app = _make_app(tasks_dir, user="alice")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        ip_lv = _list_view_for_col(app, "In Progress")
        titles = _get_list_titles(ip_lv)
        assert titles[0].startswith("♦"), (
            f"[human] task should be mine (♦): {titles[0]}"
        )


async def test_human_prefix_shows_mine_class(tmp_path: Path):
    """A task with a ``[human]`` title prefix carries the "mine" class."""
    tasks_dir = tmp_path / ".tasks"
    _write_tasks(tasks_dir, [("manual-test", _TASK_HUMAN_PREFIX)])

    app = _make_app(tasks_dir, user="alice")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        ip_lv = _list_view_for_col(app, "In Progress")
        classes = _get_list_classes(ip_lv)
        assert "mine" in classes[0]


async def test_human_prefix_matches_any_user(tmp_path: Path):
    """[human] tasks are mine regardless of the current user."""
    tasks_dir = tmp_path / ".tasks"
    _write_tasks(tasks_dir, [("manual-test", _TASK_HUMAN_PREFIX)])

    # Test with bob — still mine because of [human] prefix
    app = _make_app(tasks_dir, user="bob")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        ip_lv = _list_view_for_col(app, "In Progress")
        titles = _get_list_titles(ip_lv)
        classes = _get_list_classes(ip_lv)
        assert titles[0].startswith("♦")
        assert "mine" in classes[0]


# ======================================================================
# Tests — Mixed: some mine, some not in same view
# ======================================================================

async def test_mixed_tasks_some_mine_some_not(tmp_path: Path):
    """When multiple tasks exist, only the correct ones are highlighted."""
    tasks_dir = tmp_path / ".tasks"
    _write_tasks(
        tasks_dir,
        [
            ("dashboard", _TASK_ASSIGNED_ALICE),  # mine (assigned: alice)
            ("docs", _TASK_NO_ASSIGNMENT),        # not mine
            ("manual-test", _TASK_HUMAN_PREFIX),  # mine ([human])
            ("login-fix", _TASK_ASSIGNED_BOB),    # not mine to alice
        ],
    )

    app = _make_app(tasks_dir, user="alice")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        all_titles: list[str] = []
        all_classes: list[list[str]] = []
        for col in ["Backlog", "In Progress", "Done"]:
            lv = _list_view_for_col(app, col)
            all_titles.extend(_get_list_titles(lv))
            all_classes.extend(_get_list_classes(lv))

        # 4 tasks total across Backlog and In Progress
        assert len(all_titles) == 4

        # Titles starting with ♦ (mine)
        diamond_titles = [t for t in all_titles if t.startswith("♦")]
        # Titles starting with • (not mine)
        bullet_titles = [t for t in all_titles if t.startswith("•")]

        assert len(diamond_titles) == 2, (
            f"Expected 2 mine tasks, got {len(diamond_titles)}: {diamond_titles}"
        )
        assert len(bullet_titles) == 2, (
            f"Expected 2 non-mine tasks, got {len(bullet_titles)}: {bullet_titles}"
        )

        # Verify specific assignments:
        # "Build the dashboard" → mine
        dashboard = [t for t in diamond_titles if "Build the dashboard" in t]
        assert len(dashboard) == 1

        # "[human] Manual testing" → mine
        human = [t for t in diamond_titles if "Manual testing" in t]
        assert len(human) == 1

        # "Write documentation" → •
        docs = [t for t in bullet_titles if "Write documentation" in t]
        assert len(docs) == 1

        # "Fix login bug" (assigned bob) → • when viewed by alice
        login = [t for t in bullet_titles if "Fix login bug" in t]
        assert len(login) == 1

        # Verify classes
        mine_class_items = [c for c in all_classes if "mine" in c]
        no_mine_class_items = [c for c in all_classes if "mine" not in c]
        assert len(mine_class_items) == 2
        assert len(no_mine_class_items) == 2


# ======================================================================
# Tests — --user flag changes highlighting
# ======================================================================

async def test_user_flag_switches_mine_tasks(tmp_path: Path):
    """Passing ``--user`` flips which tasks are highlighted as mine."""
    tasks_dir = tmp_path / ".tasks"
    _write_tasks(
        tasks_dir,
        [
            ("dashboard", _TASK_ASSIGNED_ALICE),  # assigned: alice
            ("login-fix", _TASK_ASSIGNED_BOB),    # assigned: bob
        ],
    )

    # View as alice → dashboard is mine, login-fix is not
    app_alice = _make_app(tasks_dir, user="alice")
    async with app_alice.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        all_titles = _get_list_titles(app_alice.query_one("#list-in-progress", ListView))
        all_titles.extend(_get_list_titles(app_alice.query_one("#list-backlog", ListView)))

        assert any("♦" in t for t in all_titles)
        assert any("Build the dashboard" in t and t.startswith("♦") for t in all_titles)

    # View as bob → login-fix is mine, dashboard is not
    app_bob = _make_app(tasks_dir, user="bob")
    async with app_bob.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app_bob.query_one("#list-backlog", ListView)
        bp_lv = app_bob.query_one("#list-in-progress", ListView)

        bg_titles = _get_list_titles(bg_lv)
        bp_titles = _get_list_titles(bp_lv)
        all_titles = bg_titles + bp_titles

        # login-fix should now be ♦
        login_items = [t for t in all_titles if "Fix login bug" in t]
        assert len(login_items) == 1
        assert login_items[0].startswith("♦")

        # dashboard should now be •
        dash_items = [t for t in all_titles if "Build the dashboard" in t]
        assert len(dash_items) == 1
        assert dash_items[0].startswith("•")


# ======================================================================
# Tests — BOARD_TUI_USER env var
# ======================================================================

def test_board_tui_user_env_var_in_resolve_config(monkeypatch):
    """:func:`resolve_config` reads ``BOARD_TUI_USER`` when ``--user`` is not set."""
    monkeypatch.delenv("USER", raising=False)
    monkeypatch.setenv("BOARD_TUI_USER", "charlie")

    cfg = resolve_config([])
    assert cfg["user"] == "charlie"


def test_board_tui_user_ignored_when_user_flag_provided(monkeypatch):
    """:func:`resolve_config` prefers ``--user`` over ``BOARD_TUI_USER``."""
    monkeypatch.delenv("USER", raising=False)
    monkeypatch.setenv("BOARD_TUI_USER", "charlie")

    cfg = resolve_config(["--user", "diana"])
    assert cfg["user"] == "diana"


def test_board_tui_user_fallback_to_user_env(monkeypatch):
    """:func:`resolve_config` falls back to ``$USER`` when ``BOARD_TUI_USER`` is unset."""
    monkeypatch.delenv("BOARD_TUI_USER", raising=False)
    monkeypatch.setenv("USER", "eve")

    cfg = resolve_config([])
    assert cfg["user"] == "eve"


async def test_board_tui_user_env_affects_ui_highlighting(monkeypatch, tmp_path: Path):
    """``BOARD_TUI_USER`` env var correctly changes which tasks are highlighted in the UI."""
    monkeypatch.setenv("BOARD_TUI_USER", "frank")
    monkeypatch.delenv("USER", raising=False)

    tasks_dir = tmp_path / ".tasks"
    _write_tasks(
        tasks_dir,
        [
            ("dashboard", _TASK_ASSIGNED_ALICE),  # assigned: alice
        ],
    )

    # resolve_config via CLI picks up BOARD_TUI_USER
    cfg = resolve_config([])
    app = BoardApp(
        tasks_dir=cfg["tasks_dir"],
        columns=cfg["columns"],
        user=cfg["user"],
    )

    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        ip_lv = _list_view_for_col(app, "In Progress")
        titles = _get_list_titles(ip_lv)

        # Frank is not Alice, so the task should NOT be mine
        assert titles[0].startswith("•"), (
            f"Task for alice should not be mine to frank: {titles[0]}"
        )
        classes = _get_list_classes(ip_lv)
        assert "mine" not in classes[0]


# ======================================================================
# Tests — UI CSS class is applied (not just the prefix character)
# ======================================================================

async def test_non_mine_task_has_bullet_prefix(tmp_path: Path):
    """All non-mine tasks show the bullet (•) prefix character."""
    tasks_dir = tmp_path / ".tasks"
    _write_tasks(tasks_dir, [("docs", _TASK_NO_ASSIGNMENT)])

    app = _make_app(tasks_dir, user="alice")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = _list_view_for_col(app, "Backlog")
        titles = _get_list_titles(bg_lv)
        assert titles[0] == "• Write documentation"


async def test_mine_prefix_is_diamond_not_bullet(tmp_path: Path):
    """Mine tasks use the ♦ character, never •."""
    tasks_dir = tmp_path / ".tasks"
    _write_tasks(tasks_dir, [("dashboard", _TASK_ASSIGNED_ALICE)])

    app = _make_app(tasks_dir, user="alice")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        ip_lv = _list_view_for_col(app, "In Progress")
        titles = _get_list_titles(ip_lv)
        assert "•" not in titles[0], (
            f"Mine task should not contain bullet: {titles[0]}"
        )
        assert "♦ " in titles[0]


# ======================================================================
# Tests — edge cases: empty board, whitespace in assigned
# ======================================================================

async def test_whitespaper_in_assigned_field(tmp_path: Path):
    """Whitespace around the assigned value is stripped by the parser."""
    from board_tui.tasks import load_tasks

    tasks_dir = tmp_path / ".tasks"
    task_ws = """---
column: Backlog
order: 10
assigned: alice
created: 2026-04-21
---

# Trimmed assigned task

Body."""
    _write_tasks(tasks_dir, [("trimmed", task_ws)])
    tasks = load_tasks(tasks_dir, ["Backlog"])
    assigned_val = tasks[0]["fm"]["assigned"]
    assert assigned_val == "alice"  # parser strips whitespace
    assert mine(tasks[0], "alice") is True


async def test_no_tasks_empty_board(tmp_path: Path):
    """With no tasks, no ListView items exist and no mine/highlighting."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir, user="alice")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        for col in ["Backlog", "In Progress", "Done"]:
            lv = _list_view_for_col(app, col)
            assert len(lv.children) == 0


async def test_mine_case_insensitive_user_match(tmp_path: Path):
    """User matching in ``mine()`` is case-insensitive."""
    task = {"fm": {"assigned": "Alice"}, "title": "Case test"}

    assert mine(task, "alice") is True
    assert mine(task, "ALICE") is True
    assert mine(task, "AliCe") is True

    # UI test — task with "Alice" assigned shown to "alice"
    tasks_dir = tmp_path / ".tasks"
    task_md = """---
column: Backlog
order: 10
assigned: Alice
created: 2026-04-21
---

# Case test

Body."""
    _write_tasks(tasks_dir, [("case-test", task_md)])

    app = _make_app(tasks_dir, user="alice")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = _list_view_for_col(app, "Backlog")
        titles = _get_list_titles(bg_lv)
        assert titles[0].startswith("♦")
        classes = _get_list_classes(bg_lv)
        assert "mine" in classes[0]
