---
column: Done
---

# Subtask support: parent field + list_tasks(parent=) filter
## Goal

Support parent-child task relationships for delegation workflows where a parent task is split into subtasks delegated individually.

## Changes

### 1. Frontmatter convention fields

```markdown
---
column: Backlog
parent: local-agent-remote-execution   # slug of parent task
part: 2/4                              # position in sequence
depends_on: local-agent-remote-dockerfile  # slug this task blocks on
---
```

All fields optional. No schema enforcement — any string accepted.
- `parent` — used by `list_tasks(parent=)` filter and shown in TUI card label (`↑<slug>`)
- `part` — informational ordering within parent; shown in detail pane
- `depends_on` — informational dependency; shown in detail pane

### 2. `list_tasks`: add `parent` filter param

```python
list_tasks(parent="local-agent-remote-execution")  # only direct children
list_tasks()                                         # existing behavior unchanged
```

When `parent` is set:
- Return all tasks (any column, including Done) where frontmatter `parent == slug`
- Ignore `include_done` and `backlog_limit` — return all matching children unfiltered

### 3. `get_task`: show children

When returning a task, scan all tasks for `parent == this_slug` and include a `children` list in the response:

```json
{
  "slug": "local-agent-remote-execution",
  "title": "...",
  "children": [
    {"slug": "local-agent-remote-dockerfile", "title": "...", "column": "Done"},
    {"slug": "local-agent-remote-pi-start",   "title": "...", "column": "In Progress"},
    ...
  ]
}
```

### 4. TUI board view (optional / future)

- Show child count badge on parent card: `[3/4 done]`
- Collapse/expand children inline (stretch goal)

## File

`src/board_tui/mcp_server.py` — `list_tasks` and `get_task` tool handlers.
Frontmatter parsing already exists — add `parent` to the fields read.

## Non-goals

- No recursive subtasks (only one level of nesting)
- No auto-status rollup (parent doesn't auto-complete when all children done)

## Result

Made three changes to `/workspace/src/board_tui/mcp_server.py`:

1. **`list_tasks` — added `parent` parameter**: When `parent` is provided, the function filters all tasks to only those whose frontmatter `parent` field matches the given slug. This mode ignores `include_done` and `backlog_limit`, returning all matching children unfiltered regardless of column.

2. **`get_task` — added `children` to response**: After retrieving the requested task, the function scans all tasks for ones with `parent == this_slug` and includes a `children` list in the response, each entry containing `slug`, `title`, and `column`.

3. **No changes to `tasks.py`**: The existing `parse()` function already reads all frontmatter key-value pairs, and `load_tasks()` already includes `fm` in the task dict, so `parent` is automatically available as `t["fm"].get("parent")` without modifications.
