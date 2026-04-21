"""E2E tests for parent task suffix display ("↑{parent}") in ListView items."""

import pytest
from pathlib import Path
from textual.widgets import Label, ListView

from board_tui.app import BoardApp


# ---------------------------------------------------------------------------
# Fixtures: task markdown content
# ---------------------------------------------------------------------------

_TASK_WITH_PARENT_MD = """---
column: In Progress
order: 10
created: 2026-04-21
parent: main-feature
---

# Subtask with parent

This is a subtask that belongs to main-feature."""

_TASK_WITH_PARENT_SHORT_SLUG_MD = """---
column: Backlog
order: 10
created: 2026-04-21
parent: feat-auth
---

# Login page auth

Authenticate user."""

_TASK_NO_PARENT_MD = """---
column: In Progress
order: 15
created: 2026-04-21
---

# Standalone task

This task has no parent."""

_TASK_EMPTY_PARENT_MD = """---
column: Backlog
order: 20
created: 2026-04-21
parent:
---

# Empty parent field

Explicitly set parent to empty."""

_TASK_WHITESPACE_PARENT_MD = """---
column: Done
order: 10
created: 2026-04-21
parent:     
---

# Whitespace-only parent

Parent field has only spaces."""

_TASK_MULTIPLE_FIELDS_MD = """---
column: Backlog
order: 30
created: 2026-04-21
parent: feature-x
assigned: bob
priority: high
---

# Task with parent and other fields

Has many frontmatter keys including parent."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def slugify(s: str) -> str:
    """Minimal slugify for test selectors (mirrors board_tui.tasks.slugify)."""
    import re
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s[:70]


def _get_list_titles(lv: ListView) -> list[str]:
    """Return the text content of each ListItem's inner Label in a ListView."""
    titles: list[str] = []
    for child in lv.children:
        if hasattr(child, "children") and child.children:
            titles.append(child.children[0].content)
    return titles


# ---------------------------------------------------------------------------
# Test cases from the task card
# ---------------------------------------------------------------------------

async def test_parent_frontmatter_shows_up_suffix(tmp_path: Path):
    """Tasks with `parent` frontmatter show "↑{parent}" suffix in ListView."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("subtask", _TASK_WITH_PARENT_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        ip_lv = app.query_one("#list-in-progress", ListView)
        titles = _get_list_titles(ip_lv)
        assert len(titles) == 1

        item_text = titles[0]
        assert "↑main-feature" in item_text, (
            f"Expected parent suffix '↑main-feature' in: {item_text}"
        )


async def test_parent_slug_displayed_after_title(tmp_path: Path):
    """Parent slug is displayed after the task title, not replacing it."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("login-auth", _TASK_WITH_PARENT_SHORT_SLUG_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        titles = _get_list_titles(bg_lv)
        item_text = titles[0]

        # Title still appears first
        assert "Login page auth" in item_text, (
            f"Title should still be present: {item_text}"
        )
        # Parent slug follows after
        assert "↑feat-auth" in item_text, (
            f"Parent slug should follow title: {item_text}"
        )
        # Full item should contain both title and suffix
        assert item_text.startswith("• Login page auth  ↑feat-auth"), (
            f"Expected prefix + title + parent suffix, got: {item_text}"
        )


async def test_no_suffix_when_parent_missing(tmp_path: Path):
    """No parent suffix when parent field is absent from frontmatter."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("standalone", _TASK_NO_PARENT_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        ip_lv = app.query_one("#list-in-progress", ListView)
        titles = _get_list_titles(ip_lv)
        item_text = titles[0]

        assert "↑" not in item_text, (
            f"No parent suffix expected, got: {item_text}"
        )
        assert item_text.startswith("• Standalone task"), (
            f"Plain prefix + title without parent suffix: {item_text}"
        )


async def test_no_suffix_when_parent_empty_string(tmp_path: Path):
    """No parent suffix when parent field is explicitly empty."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("empty-parent", _TASK_EMPTY_PARENT_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        titles = _get_list_titles(bg_lv)
        item_text = titles[0]

        assert "↑" not in item_text, (
            f"No parent suffix expected for empty parent, got: {item_text}"
        )
        assert item_text.startswith("• Empty parent field"), (
            f"Plain prefix + title without parent suffix: {item_text}"
        )


async def test_no_suffix_when_parent_whitespace_only(tmp_path: Path):
    """No parent suffix when parent field contains only whitespace."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("whitespace-parent", _TASK_WHITESPACE_PARENT_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        done_lv = app.query_one("#list-done", ListView)
        titles = _get_list_titles(done_lv)
        item_text = titles[0]

        assert "↑" not in item_text, (
            f"No parent suffix expected for whitespace-only parent, got: {item_text}"
        )


async def test_parent_with_other_frontmatter_fields(tmp_path: Path):
    """Task with parent + other frontmatter fields shows suffix correctly."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("multi-fields", _TASK_MULTIPLE_FIELDS_MD),
    ])

    app = _make_app(tasks_dir, user="bob")
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        titles = _get_list_titles(bg_lv)
        item_text = titles[0]

        assert "↑feature-x" in item_text, (
            f"Expected parent suffix '↑feature-x' in: {item_text}"
        )
        # Other fields should not interfere
        assert "Task with parent and other fields" in item_text
        # User=Bob, so assigned=bob → mine (♦)
        assert item_text.startswith("♦"), (
            f"Assigned to bob should show ♦: {item_text}"
        )


async def test_mixed_parent_and_no_parent_in_same_column(tmp_path: Path):
    """Tasks with and without parent coexist correctly in the same column."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    # Two In Progress tasks (one with parent, one without) + one Backlog task
    _write_tasks(tasks_dir, [
        ("sub", _TASK_WITH_PARENT_MD),          # In Progress, parent=main-feature
        ("standalone", _TASK_NO_PARENT_MD),     # In Progress, no parent
        ("another-sub", _TASK_WITH_PARENT_SHORT_SLUG_MD),  # Backlog, parent=feat-auth
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # In Progress column has two tasks — one with parent, one without
        ip_lv = app.query_one("#list-in-progress", ListView)
        ip_titles = _get_list_titles(ip_lv)
        assert len(ip_titles) == 2, f"In Progress should have 2 tasks: {ip_titles}"

        ip_has_parent = [t for t in ip_titles if "↑main-feature" in t]
        ip_no_parent = [t for t in ip_titles if "↑" not in t]
        assert len(ip_has_parent) == 1, f"Expected 1 with parent in In Progress: {ip_titles}"
        assert len(ip_no_parent) == 1, f"Expected 1 without parent in In Progress: {ip_titles}"

        # Backlog column has one task with parent suffix
        bg_lv = app.query_one("#list-backlog", ListView)
        bg_titles = _get_list_titles(bg_lv)
        assert len(bg_titles) == 1, f"Backlog should have 1 task: {bg_titles}"
        assert "↑feat-auth" in bg_titles[0], (
            f"Backlog task should show parent suffix: {bg_titles[0]}"
        )


async def test_parent_suffix_ordering(tmp_path: Path):
    """Parent suffix does not affect column ordering — order is still by `order`."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    # Three tasks: two with parent, one without — different order values
    task_low = """---
column: In Progress
order: 5
created: 2026-04-21
parent: parent-a
---

# Low order parent task

Body."""

    task_high_no_parent = """---
column: In Progress
order: 30
created: 2026-04-21
---

# High no parent

Body."""

    task_mid_parent = """---
column: In Progress
order: 15
created: 2026-04-21
parent: parent-b
---

# Middle parent task

Body."""

    _write_tasks(tasks_dir, [
        ("low-parent", task_low),
        ("high-noparent", task_high_no_parent),
        ("mid-parent", task_mid_parent),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        ip_lv = app.query_one("#list-in-progress", ListView)
        titles = _get_list_titles(ip_lv)
        assert len(titles) == 3

        # Order by `order` field: 5, 15, 30
        assert "Low order parent task" in titles[0], (
            f"Order 5 should be first: {titles}"
        )
        assert "↑parent-a" in titles[0]
        assert "Middle parent task" in titles[1], (
            f"Order 15 should be second: {titles}"
        )
        assert "↑parent-b" in titles[1]
        assert "High no parent" in titles[2], (
            f"Order 30 should be last: {titles}"
        )
        assert "↑" not in titles[2]


async def test_parent_suffix_visible_on_all_columns(tmp_path: Path):
    """Parent suffix appears regardless of which column the task is in."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    task_backlog = """---
column: Backlog
order: 10
created: 2026-04-21
parent: ep-1
---

# Backlog subtask

Body."""

    task_done = """---
column: Done
order: 10
created: 2026-04-21
parent: ep-2
---

# Done subtask

Body."""

    _write_tasks(tasks_dir, [
        ("bg-sub", task_backlog),
        ("done-sub", task_done),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        bg_titles = _get_list_titles(bg_lv)
        assert "↑ep-1" in bg_titles[0], (
            f"Backlog subtask should show parent: {bg_titles[0]}"
        )

        done_lv = app.query_one("#list-done", ListView)
        done_titles = _get_list_titles(done_lv)
        assert "↑ep-2" in done_titles[0], (
            f"Done subtask should show parent: {done_titles[0]}"
        )
