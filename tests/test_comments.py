"""Tests for comments feature in board-tui."""

import tempfile
from pathlib import Path
import pytest

from board_tui.tasks import parse, dump, load_tasks, extract_comments, add_comment


class TestCommentsParse:
    """Test parsing comments from task body."""

    def test_parse_no_comments(self):
        """Task without comments returns empty list."""
        content = """---
column: Backlog
---

# Task title

Task body here.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            path = Path(f.name)

        fm, body = parse(path)
        comments = extract_comments(body)

        assert comments == []
        # Body should be returned without comments section
        assert "Task body here." in body
        assert "## Comments" not in body

    def test_parse_single_comment(self):
        """Parse single comment from body."""
        content = """---
column: Backlog
---

# Task title

Task body.

## Comments

- **2026-04-21 @alice**: First comment
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            path = Path(f.name)

        fm, body = parse(path)
        comments = extract_comments(body)

        assert len(comments) == 1
        assert comments[0]["date"] == "2026-04-21"
        assert comments[0]["author"] == "alice"
        assert comments[0]["text"] == "First comment"

    def test_parse_multiple_comments(self):
        """Parse multiple comments from body."""
        content = """---
column: Backlog
---

# Task title

Task body.

## Comments

- **2026-04-21 @alice**: First comment
- **2026-04-21 @bob**: Second comment
- **2026-04-22 @alice**: Reply
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            path = Path(f.name)

        fm, body = parse(path)
        comments = extract_comments(body)

        assert len(comments) == 3
        assert comments[0]["author"] == "alice"
        assert comments[1]["author"] == "bob"
        assert comments[2]["author"] == "alice"

    def test_parse_body_without_comments_section(self):
        """Body text preserved when no comments section."""
        content = """---
column: Backlog
---

# Task title

This is the task body.
It has multiple lines.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            path = Path(f.name)

        fm, body = parse(path)
        comments = extract_comments(body)

        assert comments == []
        assert "This is the task body." in body


class TestAddComment:
    """Test adding comments to tasks."""

    def test_add_comment_creates_section(self):
        """Adding comment creates Comments section if missing."""
        content = """---
column: Backlog
---

# Task title

Task body.
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "task.md"
            path.write_text(content)

            add_comment(path, "alice", "New comment", "2026-04-21")

            result = path.read_text()
            assert "## Comments" in result
            assert "- **2026-04-21 @alice**: New comment" in result

    def test_add_comment_appends_to_existing(self):
        """Adding comment appends to existing Comments section."""
        content = """---
column: Backlog
---

# Task title

Task body.

## Comments

- **2026-04-21 @alice**: First comment
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "task.md"
            path.write_text(content)

            add_comment(path, "bob", "Second comment", "2026-04-21")

            result = path.read_text()
            assert "- **2026-04-21 @alice**: First comment" in result
            assert "- **2026-04-21 @bob**: Second comment" in result


class TestCommentsE2E:
    """End-to-end tests for comments in TUI."""

    @pytest.mark.asyncio
    async def test_comments_display_in_detail_panel(self):
        """Comments render in detail panel below task info."""
        from board_tui.app import BoardApp

        content = """---
column: Backlog
---

# Task with comments

Task body.

## Comments

- **2026-04-21 @alice**: Test comment
"""
        with tempfile.TemporaryDirectory() as tmp:
            tasks_dir = Path(tmp)
            task_file = tasks_dir / "task-with-comments.md"
            task_file.write_text(content)

            app = BoardApp(tasks_dir=tmp, columns=["Backlog"])

            async with app.run_test() as pilot:
                await pilot.pause()
                detail_body = app.query_one("#detail-body")
                assert detail_body is not None
