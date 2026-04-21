"""E2E tests for adding new task cards.

Uses Textual's App.run_test() with async pilots to exercise the full
add-card flow: pressing 'a', entering a title, creating the file, and
verifying the board updates.
"""

import re

import pytest
from pathlib import Path
from textual.widgets import Input, Label, ListView

from board_tui.app import BoardApp, PromptScreen


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

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


def _get_prompt_input(app: BoardApp) -> Input:
    """Get the Input widget from the currently active PromptScreen.

    When the prompt is pushed the modal PromptScreen becomes
    *app.screen*, so we query that screen rather than the root.
    """
    prompt = app.screen
    assert isinstance(prompt, PromptScreen), (
        f"Expected PromptScreen but got {type(prompt).__name__}"
    )
    return prompt.query_one("#prompt-input", Input)


# ---------------------------------------------------------------------------
# 1. 'a' opens add card prompt
# ---------------------------------------------------------------------------

async def test_a_opens_add_card_prompt(tmp_path: Path):
    """Pressing 'a' pushes a PromptScreen with an Input widget focused."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Prompt should *not* be mounted yet
        assert len(app.screen_stack) == 1

        # Press 'a' to open the prompt
        await pilot.press("a")
        await pilot.pause()

        # PromptScreen is now visible
        assert len(app.screen_stack) == 2
        prompt = app.screen
        assert isinstance(prompt, PromptScreen)

        input_widget = _get_prompt_input(app)
        assert input_widget.value == ""
        assert input_widget.has_focus


# ---------------------------------------------------------------------------
# 2. Typing title and pressing enter creates task
# ---------------------------------------------------------------------------

async def test_enter_creates_task(tmp_path: Path):
    """Entering a title and pressing enter creates a new .md task file."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        await pilot.press("a")
        await pilot.pause()

        input_widget = _get_prompt_input(app)
        input_widget.value = "Create e2e test"
        await pilot.pause()

        await pilot.press("enter")
        await pilot.pause()

        # Prompt should be dismissed — back to main screen
        assert len(app.screen_stack) == 1
        assert not isinstance(app.screen, PromptScreen)

        # File should have been created
        slug = _slugify("Create e2e test")
        task_file = tasks_dir / f"{slug}.md"
        assert task_file.exists(), f"Task file {slug}.md should exist"


# ---------------------------------------------------------------------------
# 3. Task created in current column
# ---------------------------------------------------------------------------

async def test_task_created_in_current_column(tmp_path: Path):
    """A new task is placed in the currently active column."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Move to In Progress column (currently on Backlog, cur_col=0)
        await pilot.press("right")
        await pilot.pause()

        ip_title = app.query_one("#title-in-progress", Label)
        assert "column-title-active" in ip_title.classes

        # Add a new task
        await pilot.press("a")
        await pilot.pause()

        input_widget = _get_prompt_input(app)
        input_widget.value = "Move to In Progress"
        await pilot.pause()

        await pilot.press("enter")
        await pilot.pause()

        # Backlog (0) / In Progress (1)
        bg_title = app.query_one("#title-backlog", Label)
        ip_title = app.query_one("#title-in-progress", Label)
        assert "(0)" in bg_title.content
        assert "(1)" in ip_title.content

        # Task file should have column: In Progress
        slug = _slugify("Move to In Progress")
        content = tasks_dir.joinpath(f"{slug}.md").read_text()
        assert "column: In Progress" in content


# ---------------------------------------------------------------------------
# 4. Frontmatter includes column and created date
# ---------------------------------------------------------------------------

async def test_frontmatter_includes_column_and_created_date(tmp_path: Path):
    """Created task file frontmatter includes *column* and *created*."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        await pilot.press("a")
        await pilot.pause()

        input_widget = _get_prompt_input(app)
        input_widget.value = "Frontmatter fields"
        await pilot.pause()

        await pilot.press("enter")
        await pilot.pause()

        slug = _slugify("Frontmatter fields")
        content = tasks_dir.joinpath(f"{slug}.md").read_text()

        assert "column: Backlog" in content
        assert "created:" in content
        assert re.search(r"created: \d{4}-\d{2}-\d{2}", content)


# ---------------------------------------------------------------------------
# 5. Slug generated correctly from title
# ---------------------------------------------------------------------------

async def test_slug_generated_correctly_from_title(tmp_path: Path):
    """Slug is derived from the title: lowercased, dash-separated."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # "Hello World" → hello-world
        await pilot.press("a")
        await pilot.pause()
        _get_prompt_input(app).value = "Hello World"
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        assert (tasks_dir / "hello-world.md").exists()

        # "Fix: Bug #42!" → fix-bug-42
        await pilot.press("a")
        await pilot.pause()
        _get_prompt_input(app).value = "Fix: Bug #42!"
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        assert (tasks_dir / "fix-bug-42.md").exists()

        # "Multi   Space   Title" → multi-space-title
        await pilot.press("a")
        await pilot.pause()
        _get_prompt_input(app).value = "Multi   Space   Title"
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        assert (tasks_dir / "multi-space-title.md").exists()


# ---------------------------------------------------------------------------
# 6. Duplicate slug shows error notification
# ---------------------------------------------------------------------------

async def test_duplicate_slug_shows_error(tmp_path: Path):
    """Creating a task with an existing slug shows an error notification."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    existing_task = """---
column: Backlog
order: 10
created: 2026-04-20
---

# Hello World

Already exists.
"""
    _write_tasks(tasks_dir, [("hello-world", existing_task)])

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        initial_titles = len(_get_list_titles(
            app.query_one("#list-backlog", ListView)
        ))

        # Try to create another "Hello World"
        await pilot.press("a")
        await pilot.pause()

        input_widget = _get_prompt_input(app)
        input_widget.value = "Hello World"
        await pilot.pause()

        await pilot.press("enter")
        await pilot.pause()

        # Prompt dismissed
        assert len(app.screen_stack) == 1

        # File content unchanged
        assert tasks_dir.joinpath("hello-world.md").read_text() == existing_task

        # ListView count hasn't changed
        new_count = len(_get_list_titles(
            app.query_one("#list-backlog", ListView)
        ))
        assert new_count == initial_titles


# ---------------------------------------------------------------------------
# 7. Empty input cancels creation
# ---------------------------------------------------------------------------

async def test_empty_input_cancels_creation(tmp_path: Path):
    """Submitting with empty text does not create a task file."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        await pilot.press("a")
        await pilot.pause()

        input_widget = _get_prompt_input(app)
        assert input_widget.value == ""
        await pilot.pause()

        await pilot.press("enter")
        await pilot.pause()

        # Prompt dismissed
        assert len(app.screen_stack) == 1

        # No files
        assert len(list(tasks_dir.glob("*.md"))) == 0


# ---------------------------------------------------------------------------
# 8. Escape cancels creation
# ---------------------------------------------------------------------------

async def test_escape_cancels_creation(tmp_path: Path):
    """Pressing escape while the prompt is open dismisses it."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        await pilot.press("a")
        await pilot.pause()

        input_widget = _get_prompt_input(app)
        input_widget.value = "Some title"
        await pilot.pause()

        await pilot.press("escape")
        await pilot.pause()

        # Prompt dismissed
        assert len(app.screen_stack) == 1

        # No files created
        assert len(list(tasks_dir.glob("*.md"))) == 0


# ---------------------------------------------------------------------------
# Assertion — board reloads with new task visible
# ---------------------------------------------------------------------------

async def test_board_reloads_with_new_task_visible(tmp_path: Path):
    """After creating a task the board reloads and task is visible."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        bg_lv = app.query_one("#list-backlog", ListView)
        assert len(bg_lv.children) == 0

        bg_title = app.query_one("#title-backlog", Label)
        assert "(0)" in bg_title.content

        # Create a task
        await pilot.press("a")
        await pilot.pause()

        _get_prompt_input(app).value = "Visible task"
        await pilot.pause()

        await pilot.press("enter")
        await pilot.pause()

        assert "(1)" in bg_title.content
        assert len(bg_lv.children) == 1

        titles = _get_list_titles(bg_lv)
        assert "Visible task" in titles[0]

        # File content correct
        slug = _slugify("Visible task")
        content = tasks_dir.joinpath(f"{slug}.md").read_text()
        assert "---" in content
        assert "column: Backlog" in content
        assert "created:" in content
        assert "# Visible task" in content


async def test_detail_panel_shows_new_task(tmp_path: Path):
    """After creation the detail panel displays the new task."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        await pilot.press("a")
        await pilot.pause()

        _get_prompt_input(app).value = "Detail visibility test"
        await pilot.pause()

        await pilot.press("enter")
        await pilot.pause()

        from textual.widgets import Markdown
        body = app.query_one("#detail-body", Markdown)
        md_text = body._markdown
        assert "Detail visibility test" in md_text


# ---------------------------------------------------------------------------
# Mixed — create multiple tasks in independent columns
# ---------------------------------------------------------------------------

async def test_create_multiple_tasks_independent_columns(tmp_path: Path):
    """Create tasks across different columns in one session."""
    tasks_dir = tmp_path / ".tasks"
    tasks_dir.mkdir()

    app = _make_app(tasks_dir)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()

        # Task 1 – Backlog
        await pilot.press("a")
        await pilot.pause()
        _get_prompt_input(app).value = "Task One"
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        # Move right → In Progress
        await pilot.press("right")
        await pilot.pause()

        # Task 2 – In Progress
        await pilot.press("a")
        await pilot.pause()
        _get_prompt_input(app).value = "Task Two"
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        # Move right → Done
        await pilot.press("right")
        await pilot.pause()

        # Task 3 – Done
        await pilot.press("a")
        await pilot.pause()
        _get_prompt_input(app).value = "Task Three"
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        # Verify counts
        assert "(1)" in app.query_one("#title-backlog", Label).content
        assert "(1)" in app.query_one("#title-in-progress", Label).content
        assert "(1)" in app.query_one("#title-done", Label).content

        # Verify files + column values
        for slug, expected_col in [
            ("task-one", "Backlog"),
            ("task-two", "In Progress"),
            ("task-three", "Done"),
        ]:
            assert (tasks_dir / f"{slug}.md").exists()
            content = tasks_dir.joinpath(f"{slug}.md").read_text()
            assert f"column: {expected_col}" in content
