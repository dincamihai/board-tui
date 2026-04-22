"""E2E tests for subtask subindentation under parent with collapse + counter."""

import pytest
from pathlib import Path
from textual.widgets import Label, ListView, Markdown

from board_tui.app import BoardApp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_PARENT_TASK_MD = """---
column: Backlog
order: 10
created: 2026-04-22
---

# Parent feature

Big umbrella task."""

_SUBTASK_A_MD = """---
column: Backlog
order: 11
created: 2026-04-22
parent: parent-feature
---

# Subtask A

First piece."""

_SUBTASK_B_MD = """---
column: Backlog
order: 12
created: 2026-04-22
parent: parent-feature
---

# Subtask B

Second piece."""

_ORPHAN_SUBTASK_MD = """---
column: Backlog
order: 15
created: 2026-04-22
parent: missing-parent
---

# Orphan subtask

Parent does not exist."""

_STANDALONE_MD = """---
column: Backlog
order: 20
created: 2026-04-22
---

# Standalone task

No parent."""

_PARENT_IN_PROGRESS_MD = """---
column: In Progress
order: 5
created: 2026-04-22
---

# In-progress parent

Active work."""

_SUBTASK_IP_MD = """---
column: In Progress
order: 6
created: 2026-04-22
parent: parent-feature
---

# IP subtask

Under parent-feature in different column."""


def _write_tasks(tasks_dir: Path, entries: list[tuple[str, str]]) -> None:
    for slug, content in entries:
        tasks_dir.joinpath(f"{slug}.md").write_text(content)


def _make_app(tasks_dir: Path, user: str = "alice") -> BoardApp:
    return BoardApp(
        tasks_dir=str(tasks_dir),
        columns=["Backlog", "In Progress", "Done"],
        user=user,
    )


def _get_list_items(lv: ListView) -> list[dict]:
    """Return list of {text: str, classes: str, indent: int} for each ListItem."""
    out = []
    for child in lv.children:
        if hasattr(child, "children") and child.children:
            label = child.children[0]
            text = str(label.content) if hasattr(label, "content") else str(label)
            raw_classes = child.classes if hasattr(child, "classes") else ""
            # classes may be frozenset or space-separated string
            class_list = list(raw_classes) if isinstance(raw_classes, frozenset) else str(raw_classes).split()
            # Indent class like "indent-1" tells us nesting level
            indent = 0
            for c in class_list:
                if c.startswith("indent-"):
                    indent = int(c.split("-")[1])
                    break
            out.append({"text": text, "classes": " ".join(class_list), "indent": indent})
    return out


def _slug_from_item(item: dict) -> str | None:
    """Extract slug from ListItem data if present."""
    # The item dict we build doesn't have data; in real tests we'd access child.data
    return None


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

async def test_parent_shows_collapse_indicator_and_counter(tmp_path: Path):
    """Parent shows ▸{n} or ▾{n} counter before title."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("parent-feature", _PARENT_TASK_MD),
        ("subtask-a", _SUBTASK_A_MD),
        ("subtask-b", _SUBTASK_B_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        items = _get_list_items(bg_lv)
        assert len(items) == 3

        # Parent first (order 10)
        parent = items[0]
        assert "Parent feature" in parent["text"]
        assert "▾2" in parent["text"] or "▸2" in parent["text"], (
            f"Parent should show collapse counter, got: {parent['text']}"
        )


async def test_subtasks_indented_under_parent(tmp_path: Path):
    """Subtasks rendered with indent class under parent in same column."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("parent-feature", _PARENT_TASK_MD),
        ("subtask-a", _SUBTASK_A_MD),
        ("subtask-b", _SUBTASK_B_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        items = _get_list_items(bg_lv)

        assert items[0]["indent"] == 0, "parent has no indent"
        assert items[1]["indent"] == 1, "subtask A indented 1 level"
        assert items[2]["indent"] == 1, "subtask B indented 1 level"

        assert "Subtask A" in items[1]["text"]
        assert "Subtask B" in items[2]["text"]


async def test_collapsing_parent_hides_subtasks(tmp_path: Path):
    """Pressing space (or similar) on parent toggles collapse."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("parent-feature", _PARENT_TASK_MD),
        ("subtask-a", _SUBTASK_A_MD),
        ("subtask-b", _SUBTASK_B_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)

        # Initially expanded
        items = _get_list_items(bg_lv)
        assert len(items) == 3
        assert "▾2" in items[0]["text"] or "▾" in items[0]["text"]

        # Press collapse key on parent (e.g. space)
        await pilot.press("space")
        await pilot.pause()

        items = _get_list_items(bg_lv)
        assert len(items) == 1, "collapsed parent hides subtasks"
        assert "▸2" in items[0]["text"] or "▸" in items[0]["text"]
        assert "Subtask" not in items[0]["text"]


async def test_expanding_collapsed_parent_shows_subtasks(tmp_path: Path):
    """Pressing space on collapsed parent expands and shows subtasks."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("parent-feature", _PARENT_TASK_MD),
        ("subtask-a", _SUBTASK_A_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Collapse
        await pilot.press("space")
        await pilot.pause()
        items = _get_list_items(bg_lv := app.query_one("#list-backlog", ListView))
        assert len(items) == 1

        # Expand
        await pilot.press("space")
        await pilot.pause()
        items = _get_list_items(bg_lv)
        assert len(items) == 2
        assert "Subtask A" in items[1]["text"]
        assert "▾1" in items[0]["text"] or "▾" in items[0]["text"]


async def test_missing_parent_shows_exclamation_and_suffix(tmp_path: Path):
    """Subtask with missing parent slug shows ! prefix and ↑missing-parent suffix."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("orphan-sub", _ORPHAN_SUBTASK_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        items = _get_list_items(bg_lv)
        assert len(items) == 1

        text = items[0]["text"]
        assert "!" in text, f"Missing parent should show '!': {text}"
        assert "↑missing-parent" in text, f"Missing parent suffix expected: {text}"
        assert "Orphan subtask" in text


async def test_detail_panel_explains_missing_parent(tmp_path: Path):
    """Detail panel for orphan subtask includes warning about missing parent."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("orphan-sub", _ORPHAN_SUBTASK_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Detail auto-updates for selected item
        body = app.query_one("#detail-body", Markdown)
        md_text = body._markdown if hasattr(body, "_markdown") else str(body.renderable)

        assert "missing-parent" in md_text, (
            f"Detail should mention missing parent slug: {md_text}"
        )
        assert "not found" in md_text.lower() or "orphan" in md_text.lower() or "warning" in md_text.lower(), (
            f"Detail should warn about missing parent: {md_text}"
        )


async def test_parent_and_standalone_mixed_in_column(tmp_path: Path):
    """Parent with subtasks and standalone tasks coexist in same column."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("parent-feature", _PARENT_TASK_MD),
        ("subtask-a", _SUBTASK_A_MD),
        ("standalone", _STANDALONE_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        items = _get_list_items(bg_lv)
        assert len(items) == 3

        # Order: parent (10), subtask-a (11), standalone (20)
        assert "Parent feature" in items[0]["text"]
        assert items[0]["indent"] == 0
        assert "Subtask A" in items[1]["text"]
        assert items[1]["indent"] == 1
        assert "Standalone task" in items[2]["text"]
        assert items[2]["indent"] == 0


async def test_subtask_in_different_column_from_parent(tmp_path: Path):
    """Subtask can live in different column from parent; shown in its own column."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("parent-feature", _PARENT_TASK_MD),  # Backlog
        ("subtask-ip", _SUBTASK_IP_MD),         # In Progress
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        bg_items = _get_list_items(bg_lv)
        assert len(bg_items) == 1
        assert "Parent feature" in bg_items[0]["text"]
        assert "▾" not in bg_items[0]["text"] and "▸" not in bg_items[0]["text"]

        ip_lv = app.query_one("#list-in-progress", ListView)
        ip_items = _get_list_items(ip_lv)
        assert len(ip_items) == 1
        assert "IP subtask" in ip_items[0]["text"]
        assert "↑parent-feature" in ip_items[0]["text"]


async def test_counter_updates_when_subtask_moved(tmp_path: Path):
    """Moving subtask to another column updates parent counter in original column."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("parent-feature", _PARENT_TASK_MD),
        ("subtask-a", _SUBTASK_A_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        items = _get_list_items(bg_lv)
        assert "▾1" in items[0]["text"] or "▾" in items[0]["text"]

        # Select subtask and move to In Progress
        await pilot.press("down")  # select subtask-a
        await pilot.pause()
        await pilot.press("m")     # enter move mode
        await pilot.pause()
        await pilot.press("right") # move to In Progress
        await pilot.press("enter")
        await pilot.pause()

        # Backlog parent has no children in this column — no indicator
        items = _get_list_items(bg_lv)
        assert len(items) == 1
        parent_text = items[0]["text"]
        assert "▾" not in parent_text and "▸" not in parent_text, (
            f"Parent with no children in column should not show indicator: {parent_text}"
        )


async def test_deep_nesting_not_supported(tmp_path: Path):
    """Subtasks of subtasks are treated as top-level (no indent > 1)."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    grandchild_md = """---
column: Backlog
order: 13
created: 2026-04-22
parent: subtask-a
---

# Grandchild

Nested under subtask."""

    _write_tasks(tasks_dir, [
        ("parent-feature", _PARENT_TASK_MD),
        ("subtask-a", _SUBTASK_A_MD),
        ("grandchild", grandchild_md),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        items = _get_list_items(bg_lv)
        # parent (0) → subtask-a (1) → grandchild (1, not 2)
        assert items[2]["indent"] == 1, "grandchild indent capped at 1"
        assert "Grandchild" in items[2]["text"]


async def test_expand_collapse_expand_cycle_keeps_highlight_and_state(tmp_path: Path):
    """Parent stays highlighted after expand > collapse > expand cycle."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    _write_tasks(tasks_dir, [
        ("parent-feature", _PARENT_TASK_MD),
        ("subtask-a", _SUBTASK_A_MD),
        ("subtask-b", _SUBTASK_B_MD),
    ])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)

        # Initially expanded, parent highlighted
        assert bg_lv.index == 0
        assert app._selected()["slug"] == "parent-feature"
        items = _get_list_items(bg_lv)
        assert len(items) == 3
        assert "▾2" in items[0]["text"] or "▾" in items[0]["text"]

        # Collapse
        await pilot.press("space")
        await pilot.pause()

        # Parent still highlighted at index 0
        assert bg_lv.index == 0
        assert app._selected()["slug"] == "parent-feature"
        items = _get_list_items(bg_lv)
        assert len(items) == 1
        assert "▸2" in items[0]["text"] or "▸" in items[0]["text"]

        # Expand again
        await pilot.press("space")
        await pilot.pause()

        # Parent still highlighted, subtasks visible again
        assert bg_lv.index == 0
        assert app._selected()["slug"] == "parent-feature"
        items = _get_list_items(bg_lv)
        assert len(items) == 3
        assert "▾2" in items[0]["text"] or "▾" in items[0]["text"]
        assert "Subtask A" in items[1]["text"]
        assert "Subtask B" in items[2]["text"]
