"""Tests for board_tui.cli argument resolution."""

import os
import tempfile
from pathlib import Path
from board_tui.cli import resolve_config


def _create_temp_tasks_dir() -> Path:
    """Create a temporary directory that looks like a .tasks dir."""
    tmp = tempfile.mkdtemp()
    tasks = Path(tmp) / ".tasks"
    tasks.mkdir()
    f = tasks / "hello.md"
    f.write_text("""---
column: In Progress
---

# Hello Task
""")
    return tasks


def test_resolve_config_defaults(monkeypatch):
    """When no args and no env vars, returns sensible defaults."""
    from board_tui.cli import resolve_config

    monkeypatch.delenv("BOARD_TUI_TASKS_DIR", raising=False)
    monkeypatch.delenv("BOARD_TUI_COLUMNS", raising=False)
    monkeypatch.delenv("BOARD_TUI_USER", raising=False)
    monkeypatch.delenv("USER", raising=False)

    with tempfile.TemporaryDirectory() as tmp:
        monkeypatch.chdir(tmp)
        config = resolve_config([])

    assert config["tasks_dir"] == os.path.realpath(os.path.join(tmp, ".tasks"))
    assert config["columns"] == ["Backlog", "In Progress", "Done"]
    assert config["user"] == "unknown"


def test_resolve_config_args_override_defaults(monkeypatch):
    """CLI flags override defaults."""
    with tempfile.TemporaryDirectory() as tmp:
        config = resolve_config([
            "--tasks-dir", f"{tmp}/my-tasks",
            "--columns", "TODO, Review, Merge",
            "--user", "alice",
        ])

    assert config["tasks_dir"] == os.path.realpath(f"{tmp}/my-tasks")
    assert config["columns"] == ["TODO", "Review", "Merge"]
    assert config["user"] == "alice"


def test_resolve_config_args_take_precedence_over_env(monkeypatch):
    """CLI flags take precedence over environment variables."""
    monkeypatch.setenv("BOARD_TUI_TASKS_DIR", "/tmp/env-tasks")
    monkeypatch.setenv("BOARD_TUI_COLUMNS", "EnvCol A,B")
    monkeypatch.setenv("BOARD_TUI_USER", "bob")
    monkeypatch.setenv("USER", "charlie")

    config = resolve_config([
        "--tasks-dir", "/tmp/cli-tasks",
        "--columns", "CLI, Col, Split",
        "--user", "alice",
    ])

    assert config["tasks_dir"] == "/tmp/cli-tasks"
    assert config["columns"] == ["CLI", "Col", "Split"]
    assert config["user"] == "alice"


def test_resolve_config_env_tasks_dir(monkeypatch):
    """$BOARD_TUI_TASKS_DIR used when --tasks-dir not given."""
    monkeypatch.delenv("BOARD_TUI_TASKS_DIR", raising=False)
    monkeypatch.setenv("BOARD_TUI_TASKS_DIR", "/tmp/env-dir")

    config = resolve_config([])

    assert config["tasks_dir"] == "/tmp/env-dir"


def test_resolve_config_env_columns(monkeypatch):
    """$BOARD_TUI_COLUMNS used when --columns not given."""
    monkeypatch.delenv("BOARD_TUI_COLUMNS", raising=False)
    monkeypatch.setenv("BOARD_TUI_COLUMNS", "Ready, Testing, Released")

    config = resolve_config([])

    assert config["columns"] == ["Ready", "Testing", "Released"]


def test_resolve_config_user_priority(monkeypatch):
    """--user > $BOARD_TUI_USER > $USER > 'unknown' priority chain."""
    from board_tui.cli import resolve_config

    # No override -> $USER
    monkeypatch.delenv("BOARD_TUI_USER", raising=False)
    monkeypatch.setenv("USER", "user-env")
    config = resolve_config([])
    assert config["user"] == "user-env"

    # $BOARD_TUI_USER overrides $USER
    monkeypatch.setenv("BOARD_TUI_USER", "board-env")
    config = resolve_config([])
    assert config["user"] == "board-env"

    # --user overrides everything
    config = resolve_config(["--user", "cli-user"])
    assert config["user"] == "cli-user"


def test_resolve_config_columns_whitespace(monkeypatch):
    """--columns trims whitespace around split items."""
    monkeypatch.delenv("BOARD_TUI_COLUMNS", raising=False)

    config = resolve_config(["--columns", " A , B , C "])

    assert config["columns"] == ["A", "B", "C"]


def test_resolve_config_tasks_dir_resolved(monkeypatch):
    """--tasks-dir path is realpath'd."""
    monkeypatch.delenv("BOARD_TUI_TASKS_DIR", raising=False)

    with tempfile.TemporaryDirectory() as tmp:
        # Create symlink scenario
        real_dir = Path(tmp) / "real"
        real_dir.mkdir()
        link = Path(tmp) / "link"
        link.symlink_to(real_dir)

        config = resolve_config(["--tasks-dir", f"{link}/sub"])

    assert config["tasks_dir"] == os.path.realpath(f"{tmp}/real/sub")
