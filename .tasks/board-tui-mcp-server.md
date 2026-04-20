---
column: Done
order: 100
---

# Implement MCP server for board operations

Expose board operations via Model Context Protocol so LLM agents can read and mutate the board without shell calls.

## Tools to expose

- `list_columns` — return all column names
- `list_tasks` — return all tasks (optionally filtered by column)
- `get_task` — return full task content by id/slug
- `move_task` — change task column
- `create_task` — create new task file
- `update_task` — overwrite task body
- `delete_task` — remove task file

## Requirements

- Use `mcp` Python SDK (add to `pyproject.toml` deps)
- Tasks dir set at server launch via `BOARD_TASKS_DIR` env var — one server instance per board
- Entry point: `board-tui-mcp` (dedicated binary, no `--mcp` flag on main CLI)
- No `tasks_dir` param on individual tools — dir is fixed for lifetime of server process
- Clients configure one MCP server entry per board in their MCP config, e.g.:
  ```json
  {
    "mcpServers": {
      "board-local-agent": { "command": "board-tui-mcp", "env": { "BOARD_TASKS_DIR": "/path/to/local-agent/.tasks" } },
      "board-zen":         { "command": "board-tui-mcp", "env": { "BOARD_TASKS_DIR": "/path/to/zen/.tasks" } }
    }
  }
  ```
- Reuse existing `tasks.py` pure functions wherever possible
- Add `tests/test_mcp.py` covering each tool

## Tasks

- [x] Add `mcp` dep to `pyproject.toml`
- [x] Implement `src/board_tui/mcp_server.py` with all tools
- [x] Wire entry point in `pyproject.toml` or `cli.py`
- [x] Write tests
- [x] Document usage in `README.md`

## Result

Implemented a dedicated MCP server for board-tui with the following deliverables:

1. **`src/board_tui/mcp_server.py`** — FastMCP server importing from `mcp.server.fastmcp` that registers 7 tools (`list_columns`, `list_tasks`, `get_task`, `move_task`, `create_task`, `update_task`, `delete_task`). The tasks directory is set once at module load time via the `BOARD_TASKS_DIR` environment variable, so each server process serves one board. All tool implementation reuses the existing pure functions from `board_tui.tasks` (`parse`, `dump`, `load_tasks`, `slugify`).

2. **`src/board_tui/mcp_entry.py`** — Minimal entry-point script calling `mcp.run()` for the `board-tui-mcp` binary.

3. **`pyproject.toml` changes** — Added `"mcp>=1.0.0"` to dependencies and `"board-tui-mcp": "board_tui.mcp_entry:main"` to `[project.scripts]`.

4. **`tests/test_mcp.py`** — Pytest suite covering all 7 tools with positive and negative cases (found/not-found, auto-slug generation, duplicate detection, partial updates, etc.).

5. **`README.md`** — Added a full "MCP server" section documenting launch, configuration examples, all available tools, and usage examples.

All task checkboxes from the original issue are marked complete.
