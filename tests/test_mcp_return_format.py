"""Tests for MCP server return format.

All tools must return JSON strings so that content[0].text is always parseable.
"""

import json
from pathlib import Path

import pytest

from board_tui.mcp_server import (
    list_columns,
    list_tasks,
    get_task,
    move_task,
    create_task,
    update_task,
    delete_task,
    set_frontmatter,
    list_delegated_tasks,
)


def _assert_json_list(text: str) -> list:
    """Parse text as JSON and assert it's a list."""
    assert isinstance(text, str), f"Expected string, got {type(text)}"
    parsed = json.loads(text)
    assert isinstance(parsed, list), f"Expected list, got {type(parsed)}"
    return parsed


def _assert_json_dict(text: str) -> dict:
    """Parse text as JSON and assert it's a dict."""
    assert isinstance(text, str), f"Expected string, got {type(text)}"
    parsed = json.loads(text)
    assert isinstance(parsed, dict), f"Expected dict, got {type(parsed)}"
    return parsed


def _assert_json_bool(text: str) -> bool:
    """Parse text as JSON and assert it's a bool."""
    assert isinstance(text, str), f"Expected string, got {type(text)}"
    parsed = json.loads(text)
    assert isinstance(parsed, bool), f"Expected bool, got {type(parsed)}"
    return parsed


# ---------------------------------------------------------------------------
# list_columns
# ---------------------------------------------------------------------------

def test_list_columns_returns_json_list():
    result = list_columns()
    cols = _assert_json_list(result)
    assert isinstance(cols, list)


# ---------------------------------------------------------------------------
# list_tasks
# ---------------------------------------------------------------------------

def test_list_tasks_returns_json_list():
    result = list_tasks()
    tasks = _assert_json_list(result)
    assert isinstance(tasks, list)


def test_list_tasks_parent_filter_returns_json_list():
    result = list_tasks(parent="nonexistent")
    tasks = _assert_json_list(result)
    assert tasks == []


def test_list_tasks_depends_on_filter_returns_json_list():
    result = list_tasks(depends_on="nonexistent")
    tasks = _assert_json_list(result)
    assert tasks == []


# ---------------------------------------------------------------------------
# get_task
# ---------------------------------------------------------------------------

def test_get_task_missing_returns_json_null():
    result = get_task("does-not-exist")
    assert isinstance(result, str)
    assert json.loads(result) is None


# ---------------------------------------------------------------------------
# move_task
# ---------------------------------------------------------------------------

def test_move_task_missing_returns_json_null():
    result = move_task("does-not-exist", "Done")
    assert isinstance(result, str)
    assert json.loads(result) is None


# ---------------------------------------------------------------------------
# create_task
# ---------------------------------------------------------------------------

def test_create_task_returns_json_dict(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("BOARD_TASKS_DIR", str(tmp_path))
    # Re-import to pick up new env
    import importlib
    import board_tui.mcp_server as mcp_mod
    importlib.reload(mcp_mod)
    result = mcp_mod.create_task(title="Test Task")
    task = _assert_json_dict(result)
    assert task["slug"] == "test-task"
    assert task["title"] == "Test Task"


# ---------------------------------------------------------------------------
# update_task
# ---------------------------------------------------------------------------

def test_update_task_missing_returns_json_null():
    result = update_task("does-not-exist", "new body")
    assert isinstance(result, str)
    assert json.loads(result) is None


# ---------------------------------------------------------------------------
# delete_task
# ---------------------------------------------------------------------------

def test_delete_task_missing_returns_json_false():
    result = delete_task("does-not-exist")
    assert _assert_json_bool(result) is False


def test_delete_task_returns_json_true(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("BOARD_TASKS_DIR", str(tmp_path))
    import importlib
    import board_tui.mcp_server as mcp_mod
    importlib.reload(mcp_mod)
    mcp_mod.create_task(title="To Delete")
    result = mcp_mod.delete_task("to-delete")
    assert _assert_json_bool(result) is True


# ---------------------------------------------------------------------------
# set_frontmatter
# ---------------------------------------------------------------------------

def test_set_frontmatter_missing_returns_json_null():
    result = set_frontmatter("does-not-exist", "key", "value")
    assert isinstance(result, str)
    assert json.loads(result) is None


# ---------------------------------------------------------------------------
# list_delegated_tasks
# ---------------------------------------------------------------------------

def test_list_delegated_tasks_returns_json_list():
    result = list_delegated_tasks()
    tasks = _assert_json_list(result)
    assert isinstance(tasks, list)


def test_list_delegated_tasks_queued_returns_json_list():
    result = list_delegated_tasks(status="queued")
    tasks = _assert_json_list(result)
    assert isinstance(tasks, list)
