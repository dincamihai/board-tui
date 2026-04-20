"""CLI entry point for board-tui."""

import argparse
import os
import sys

from board_tui.app import BoardApp


def resolve_config(argv=None) -> dict:
    """Parse CLI args and env vars, returning a config dict for BoardApp.

    This is a pure function and can be tested without launching the TUI.
    """
    parser = argparse.ArgumentParser(
        prog="board-tui",
        description="Kanban TUI for .tasks/*.md markdown files",
    )
    parser.add_argument(
        "--tasks-dir",
        default=None,
        help="Path to .tasks directory (defaults to CWD/.tasks or $BOARD_TUI_TASKS_DIR)",
    )
    parser.add_argument(
        "--columns",
        default=None,
        help='Comma-separated columns (default: "Backlog,In Progress,Done")',
    )
    parser.add_argument(
        "--user",
        default=None,
        help="User name for filter highlighting (default: $BOARD_TUI_USER or $USER)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__import__('board_tui').__version__}",
    )
    args = parser.parse_args(argv)

    tasks_dir_str = args.tasks_dir or os.environ.get(
        "BOARD_TUI_TASKS_DIR", str(os.path.join(os.getcwd(), ".tasks"))
    )
    tasks_dir = os.path.realpath(tasks_dir_str)

    columns_str = args.columns or os.environ.get(
        "BOARD_TUI_COLUMNS", "Backlog,In Progress,Done"
    )
    columns = [c.strip() for c in columns_str.split(",")]

    user = args.user or os.environ.get("BOARD_TUI_USER", os.environ.get("USER", "unknown"))

    return {
        "tasks_dir": tasks_dir,
        "columns": columns,
        "user": user,
    }


def main() -> None:
    BoardApp(**resolve_config()).run()


if __name__ == "__main__":
    main()
