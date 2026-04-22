"""Tests for list_delegated_tasks MCP tool."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


def _running_in_container() -> bool:
    return os.environ.get("PI_AGENT_CONTAINER") == "1"


# The MCP server module reads BOARD_TASKS_DIR at import time.


def _setup_mcp_module(tasks_dir: Path):
    os.environ["BOARD_TASKS_DIR"] = str(tasks_dir)
    if "board_tui.mcp_server" in sys.modules:
        del sys.modules["board_tui.mcp_server"]
    from board_tui.mcp_server import mcp, _tasks_dir
    return mcp, _tasks_dir


def _write_task(tasks_dir: Path, slug: str, column: str, body: str, extra_fm: str = ""):
    fm_path = tasks_dir / f"{slug}.md"
    fm_path.write_text(f"---\ncolumn: {column}{extra_fm}\n---\n\n# {slug}\n{body}\n")


pytestmark = pytest.mark.skipif(
    _running_in_container(),
    reason="mcp module not available in container"
)


# ---------------------------------------------------------------------------
# list_delegated_tasks
# ---------------------------------------------------------------------------


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_list_delegated_tasks_returns_queued(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import list_delegated_tasks

    _write_task(tmp_path, "delegated", "Backlog", "body", "\ndelegation_status: queued")
    _write_task(tmp_path, "regular", "Backlog", "body")

    tasks = list_delegated_tasks(status="queued")
    assert len(tasks) == 1
    assert tasks[0]["slug"] == "delegated"
    assert tasks[0]["delegation_status"] == "queued"


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_list_delegated_tasks_filters_by_status(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import list_delegated_tasks

    _write_task(tmp_path, "queued", "Backlog", "body", "\ndelegation_status: queued")
    _write_task(tmp_path, "processing", "Backlog", "body", "\ndelegation_status: processing")
    _write_task(tmp_path, "done", "Backlog", "body", "\ndelegation_status: done")

    assert len(list_delegated_tasks(status="queued")) == 1
    assert list_delegated_tasks(status="queued")[0]["slug"] == "queued"
    assert len(list_delegated_tasks(status="processing")) == 1
    assert len(list_delegated_tasks(status="done")) == 1


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_list_delegated_tasks_excludes_non_delegated(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import list_delegated_tasks

    _write_task(tmp_path, "regular", "Backlog", "body")
    _write_task(tmp_path, "another", "In Progress", "body")

    tasks = list_delegated_tasks()
    assert len(tasks) == 0


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_list_delegated_tasks_no_status_returns_all(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import list_delegated_tasks

    _write_task(tmp_path, "queued", "Backlog", "body", "\ndelegation_status: queued")
    _write_task(tmp_path, "processing", "Backlog", "body", "\ndelegation_status: processing")
    _write_task(tmp_path, "regular", "Backlog", "body")

    tasks = list_delegated_tasks()
    assert len(tasks) == 2
    slugs = {t["slug"] for t in tasks}
    assert slugs == {"queued", "processing"}


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_list_delegated_tasks_returns_body(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import list_delegated_tasks

    _write_task(tmp_path, "delegated", "Backlog", "Task body here", "\ndelegation_status: queued")

    tasks = list_delegated_tasks()
    assert len(tasks) == 1
    assert "Task body here" in tasks[0]["body"]


@patch.dict(os.environ, {"BOARD_TASKS_DIR": ""}, clear=True)
def test_list_delegated_tasks_returns_order_and_column(tmp_path: Path):
    _setup_mcp_module(tmp_path)
    from board_tui.mcp_server import list_delegated_tasks

    _write_task(tmp_path, "delegated", "In Progress", "body", "\norder: 10\ndelegation_status: queued")

    tasks = list_delegated_tasks()
    assert len(tasks) == 1
    assert tasks[0]["column"] == "In Progress"
    assert tasks[0]["order"] == 10
