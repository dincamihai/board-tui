---
column: Backlog
---

# mcp_server.py tool tests
# mcp_server.py tool tests

Zero test coverage for MCP server tools.

## What to test

- `list_columns`: returns unique columns in order, empty dir, all tasks in one column
- `list_tasks`: default excludes Done/Superseded, `include_done=True`, explicit `column` filter, `parent` filter, `depends_on` filter, `backlog_limit=0` includes all, `backlog_limit` with explicit column doesn't apply limit, empty dir
- `get_task`: existing slug returns full dict with children, non-existent returns None, task without children
- `move_task`: successful move updates file on disk, non-existent returns None, **bug**: `fm["updated"] = "true"` stores literal string not timestamp (fix this)
- `create_task`: auto-slug from title, default column, duplicate slug raises `FileExistsError`, empty title
- `update_task`: update body only, update body+title+column, non-existent returns None, verify file on disk
- `delete_task`: existing returns True and removes file, non-existent returns False
- `set_frontmatter`: add new field, update existing field, non-existent slug returns None

## Bug to fix

`move_task` at line 163 stores `fm["updated"] = "true"` (literal string). Should be ISO timestamp like `app.py` does at line 320-322.

## Approach

Use `tmp_path` fixture for isolated task directories. Test each tool via direct function call.
