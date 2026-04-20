"""Tests for board_tui.mcp_server tools."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# The MCP server module reads BOARD_TASKS_DIR at import time; we must set it
# before the module is loaded.  For every test we use a unique tmp_path dir.

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _setup_mcp_module(tasks_dir: Path) -> None:
    """Force-reload the mcp_server module against a specific tasks_dir."""
    os.environ["BOARD_TASKS_DIR"] = str(tasks_dir)
    if "board_tui.mcp_server" in sys.modules:
        del sys.modules["board_tui.mcp_server"]
    from board_tui.mcp_server import mcp, _tasks_dir

    return mcp, _tasks_dir


def _write_task(tasks_dir: Path, slug: str, column: str, body: str) -> None:
    fm_path = tasks_dir / f"{slug}.md"
    fm_path.write_text(f"---\ncolumn: {column}\n---\n\n# {slug}\n{body}\n")


# ---------------------------------------------------------------------------
# list_columns
# ---------------------------------------------------------------------------


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_list_columns(tmp_path: Path):
    """list_columns returns the column names found in tasks files."""
    mcp, _ = _setup_mcp_module(tmp_path)
    _write_task(tmp_path, "a", "Backlog", "body a")
    _write_task(tmp_path, "b", "In Progress", "body b")
    _write_task(tmp_path, "c", "Done", "body c")

    from board_tui.mcp_server import list_columns

    cols = list_columns()
    assert cols == ["Backlog", "In Progress", "Done"]


# ---------------------------------------------------------------------------
# list_tasks
# ---------------------------------------------------------------------------


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_list_tasks_all(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import list_tasks

    _write_task(tmp_path, "alpha", "Backlog", "first")
    _write_task(tmp_path, "beta", "In Progress", "second")

    tasks = list_tasks()
    assert len(tasks) == 2
    assert tasks[0]["slug"] == "alpha"
    assert tasks[1]["slug"] == "beta"


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_list_tasks_filtered(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import list_tasks

    _write_task(tmp_path, "x", "Backlog", "b")
    _write_task(tmp_path, "y", "In Progress", "ip")
    _write_task(tmp_path, "z", "Done", "d")

    tasks = list_tasks(column="Done")
    assert len(tasks) == 1
    assert tasks[0]["slug"] == "z"


# ---------------------------------------------------------------------------
# get_task
# ---------------------------------------------------------------------------


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_get_task_found(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import get_task

    _write_task(tmp_path, "my-task", "In Progress", "body content")
    result = get_task("my-task")
    assert result is not None
    assert result["slug"] == "my-task"
    assert result["title"] == "my-task"
    assert result["column"] == "In Progress"
    assert "body content" in result["body"]


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_get_task_not_found(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import get_task

    result = get_task("nonexistent")
    assert result is None


# ---------------------------------------------------------------------------
# move_task
# ---------------------------------------------------------------------------


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_move_task(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import list_tasks, move_task

    _write_task(tmp_path, "to-move", "Backlog", "move me")
    result = move_task("to-move", column="Done")
    assert result is not None
    assert result["column"] == "Done"

    tasks = list_tasks()
    assert tasks[0]["column"] == "Done"


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_move_task_not_found(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import move_task

    result = move_task("nope", column="Backlog")
    assert result is None


# ---------------------------------------------------------------------------
# create_task
# ---------------------------------------------------------------------------


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_create_task(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import create_task, get_task

    result = create_task("new-task", title="New Task", column="Review", body="desc")
    assert result["slug"] == "new-task"
    assert result["column"] == "Review"
    assert get_task("new-task") is not None
    # The file must exist on disk
    assert (tmp_path / "new-task.md").exists()


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_create_task_auto_slug(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import create_task, get_task

    result = create_task(slug="", title="Auto Title")
    assert result["slug"] == "auto-title"
    assert get_task("auto-title") is not None


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_create_task_duplicate_fails(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import create_task

    create_task("dup", title="First")
    with pytest.raises(FileExistsError):
        create_task("dup", title="Second")


# ---------------------------------------------------------------------------
# update_task
# ---------------------------------------------------------------------------


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_update_task(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import update_task

    _write_task(tmp_path, "upd", "Backlog", "original body")
    result = update_task("upd", title="Updated", column="In Progress", body="new body")
    assert result["title"] == "Updated"
    assert result["column"] == "In Progress"
    assert result["body"] == "new body"


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_update_task_body_only(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import update_task

    _write_task(tmp_path, "upd", "Backlog", "old body")
    result = update_task("upd", body="just body change", title="Kept Title")
    assert result["body"] == "just body change"
    assert result["slug"] == "upd"


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_update_task_not_found(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import update_task

    result = update_task("nope", body="stuff")
    assert result is None


# ---------------------------------------------------------------------------
# delete_task
# ---------------------------------------------------------------------------


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_delete_task_found(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import delete_task

    _write_task(tmp_path, "del", "Backlog", "bye")
    assert delete_task("del") is True
    assert not (tmp_path / "del.md").exists()


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_delete_task_not_found(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import delete_task

    assert delete_task("ghost") is False
