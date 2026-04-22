#!/usr/bin/env python3
"""Standalone entry point for the board-tui MCP server.

Sets up logging then starts the MCP server via stdio transport.
"""

import argparse
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--tasks-dir", default=None)
    args, _ = parser.parse_known_args()

    if args.tasks_dir:
        os.environ["BOARD_TASKS_DIR"] = args.tasks_dir
    elif "BOARD_TASKS_DIR" not in os.environ:
        os.environ["BOARD_TASKS_DIR"] = os.path.join(os.getcwd(), ".tasks")

    from board_tui.mcp_server import mcp
    mcp.run()


if __name__ == "__main__":
    main()
