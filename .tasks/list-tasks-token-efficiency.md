---
column: Done
---

# list_tasks: exclude Done by default, limit Backlog to top N
# list_tasks: exclude Done by default, limit Backlog to top N

`list_tasks` returns all tasks including Done, flooding LLM context with stale data.

## Changes

### 1. Exclude Done by default

`list_tasks` without `column` filter should skip Done (and Superseded) columns.
Add optional param `include_done: bool = False` to opt back in.

### 2. Limit Backlog results

Add optional param `limit: int | None = None`.
When set, return only the first `limit` tasks by order from each non-Done column.
Default: `3` for Backlog, unlimited for In Progress / other active columns.

OR: simpler — single `backlog_limit: int = 3` param.

### Rationale

Full board dump (Done + all Backlog) costs hundreds of tokens per call. LLMs only need:
- What's active (In Progress)
- Top N upcoming (Backlog)
- Not what's already done

## Suggested API

```
list_tasks()                          # active + top 3 backlog, no Done
list_tasks(include_done=True)         # full board
list_tasks(backlog_limit=5)           # top 5 backlog
list_tasks(column="Done")            # explicit Done query still works
```

## File

MCP server implementation — find `list_tasks` tool handler.

## Result

Modified `src/board_tui/mcp_server.py` to implement two features in `list_tasks`:

1. **Exclude Done/Superseded by default** — Added a `_DONE_COLUMNS` set (`{"Done", "Superseded"}`). When `list_tasks()` is called without a column filter and `include_done=False` (default), tasks from those columns are filtered out. Setting `include_done=True` restores the previous behavior of returning all columns.

2. **Backlog limit** — Added `backlog_limit: int = 3` parameter. Only in default mode (no explicit column filter), Backlog tasks are capped to the first 3 (by order). In Progress and other active columns are returned in full regardless of this parameter.

The updated API matches the suggested interface:
- `list_tasks()` → active + top 3 backlog, no Done
- `list_tasks(include_done=True)` → full board
- `list_tasks(backlog_limit=5)` → top 5 backlog
- `list_tasks(column="Done")` → explicit Done query still works (unlimited, no filtering)

The backlog_limit is applied after the column filter so explicit column queries always return all matching tasks.
