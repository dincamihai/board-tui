---
column: Cancelled
order: 99
---

# Implement --jsonl CLI flag

~~Superseded by MCP server implementation (`board-tui-mcp-server`). Agent access via MCP tools is a better interface than `--jsonl`.~~

Add `--jsonl` flag to output board data as newline-delimited JSON to stdout, one object per line.

## Requirements

- Flag: `--jsonl` (no value, boolean)
- When set, print JSON lines and exit (no TUI launch)
- Output format: one JSON object per line
  - Line 1: columns array — `{"type": "columns", "columns": ["Backlog", "In Progress", "Done"]}`
  - Line N+: one task per line — `{"type": "task", "id": "slug", "column": "Backlog", "subject": "...", "order": 1}`
- Read from same `.tasks/` dir as normal run (respects `--tasks-dir` / `BOARD_TASKS_DIR`)
- Exit code 0 on success

## Tasks

- [ ] Add `--jsonl` arg to argparse in `cli.py`
- [ ] Implement `dump_jsonl(tasks_dir)` in `tasks.py`
- [ ] Wire flag in `__main__.py` / `cli.py` (print + exit before launching app)
- [ ] Add tests in `tests/test_cli.py` for `--jsonl` output
