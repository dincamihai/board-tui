---
column: Done
updated: true
---

# board-tui: add list_delegated_tasks MCP tool
# board-tui: add `list_delegated_tasks` MCP tool

Add MCP tool so local-agent can query board-tui for tasks with delegation_status.

## Changes

- Add `list_delegated_tasks(status)` MCP tool to `mcp_server.py`
- Returns tasks filtered by `delegation_status` frontmatter
- Include slug, title, column, order, delegation_status, body
- No status param = return all delegated tasks

## TDD

Write tests BEFORE implementation:
- `test_list_delegated_tasks_returns_queued` — finds queued tasks
- `test_list_delegated_tasks_filters_by_status` — status param works
- `test_list_delegated_tasks_excludes_non_delegated` — skips regular tasks
- `test_list_delegated_tasks_no_status_returns_all` — all delegated tasks
- `test_list_delegated_tasks_returns_body` — body included in response

## Files

- `board-tui/src/board_tui/mcp_server.py`
- `board-tui/tests/test_mcp.py`

## Result
