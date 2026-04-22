---
column: Done
updated: true
---

# board-tui: delegation queue integration

Add delegation support so pressing `d` on a task card enqueues it to the local-agent queue. Badge in list shows queue status.

## Context

- local-agent queue DB: SQLite at `QUEUE_FILE` env or `/tmp/pi-bridge-queue.db`
- Queue schema (tasks table): `id`, `task_slug`, `workspace`, `task_file`, `prompt`, `status` (queued/processing/done/failed), `agent_id`, `queued_at`, `started_at`, `completed_at`, `result`, `error`
- board-tui repo: `/home/mihai/repos/board-tui`
- Source files: `src/board_tui/`

## Implementation

### 1. New file: `src/board_tui/queue_client.py`

Python `sqlite3` wrapper (no external deps):

```python
import sqlite3, os, uuid, time

QUEUE_FILE = os.environ.get("QUEUE_FILE", "/tmp/pi-bridge-queue.db")

def queue_add(task_slug, prompt, workspace=None, task_file=None) -> str:
    # Add task to queue, return task id

def queue_get(task_id) -> dict | None:
    # Get task by id

def queue_list(status=None) -> list[dict]:
    # List tasks, optionally filtered by status
```

### 2. `src/board_tui/tasks.py` — add helper

```python
def set_frontmatter_field(path: Path, key: str, value: str) -> None:
    # Set or update a single frontmatter field in a task file
```

### 3. `src/board_tui/app.py`

Add to BINDINGS:
```python
Binding("d", "delegate_card", "delegate"),
Binding("D", "delegation_status", "delegation status"),
```

`action_delegate_card()`: get selected task → queue_add → write `queue_id` + `delegation_status: queued` to frontmatter → reload + notify.

`action_delegation_status()`: read `queue_id` from frontmatter → queue_get → show status in notification.

`_reload()` badge prefix:
```python
ds = t["fm"].get("delegation_status")
if ds == "queued":       prefix = "⏳ "
elif ds == "processing": prefix = "▶ "
elif ds == "done":       prefix = "✓ "
else: prefix = "♦ " if mine(t, self._user) else "• "
```

### 4. `src/board_tui/mcp_server.py` — add tools

```python
@mcp.tool()
def queue_task(slug: str) -> str:
    # Delegate task card to local-agent queue

@mcp.tool()
def delegation_status(slug: str) -> str:
    # Get delegation queue status for task card
```

## Result

Implemented all 4 components:

1. **src/board_tui/queue_client.py** — SQLite queue wrapper with `queue_add()`, `queue_get()`, `queue_list()`
2. **src/board_tui/tasks.py** — Added `set_frontmatter_field()` helper
3. **src/board_tui/app.py** — Added delegation bindings (`d`, `D`), actions, badge prefixes (⏳/▶/✓)
4. **src/board_tui/mcp_server.py** — Added `queue_task` and `delegation_status` MCP tools

All 151 existing tests pass (15 skipped).
