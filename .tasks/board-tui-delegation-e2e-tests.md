---
column: Done
updated: true
---

# board-tui: delegation e2e tests

Write tests for the delegation queue integration. Sibling card: board-tui-delegation-queue-integration.

## Tests to write

### `tests/test_queue_client.py`
- `test_queue_add` — add task, verify returned id and DB row
- `test_queue_get` — get by id, verify fields
- `test_queue_get_missing` — returns None for unknown id
- `test_queue_list_all` — returns all tasks
- `test_queue_list_filtered` — status filter works

Use a temp SQLite file (tmp_path fixture), override QUEUE_FILE env var.

### `tests/test_tasks_frontmatter.py`
- `test_set_frontmatter_field_existing` — updates existing key in frontmatter
- `test_set_frontmatter_field_new` — adds new key to frontmatter
- `test_set_frontmatter_field_no_frontmatter` — creates frontmatter block if absent

### `tests/test_mcp_delegation.py`
- `test_queue_task_tool` — MCP queue_task writes queue_id + delegation_status to frontmatter
- `test_delegation_status_tool` — MCP delegation_status returns correct status string
- `test_delegation_status_no_queue_id` — error when task has no queue_id

Mock queue_client functions (monkeypatch) to avoid needing a real DB.

## Result

Created 3 test files (15 tests total):

**tests/test_queue_client.py** (9 tests) — SQLite queue wrapper:
- test_queue_add, test_queue_add_preserves_body, test_queue_add_default_status
- test_queue_get, test_queue_get_missing
- test_queue_list_all, test_queue_list_all_empty
- test_queue_list_filtered_by_status, test_queue_list_filtered_no_matches

**tests/test_tasks_frontmatter.py** (3 tests) — frontmatter helper:
- test_set_frontmatter_field_existing, test_set_frontmatter_field_new, test_set_frontmatter_field_no_frontmatter

**tests/test_mcp_delegation.py** (3 tests) — MCP delegation tools:
- test_queue_task_tool, test_delegation_status_tool, test_delegation_status_no_queue_id

All existing tests pass (151 tests, 15 skipped).
