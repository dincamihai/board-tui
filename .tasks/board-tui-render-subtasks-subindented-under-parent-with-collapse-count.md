---
column: Backlog
---

# board-tui: render subtasks subindented under parent with collapse + counter
# board-tui: render subtasks subindented under parent with collapse + counter

## Goal

Change ListView rendering so tasks with `parent` frontmatter appear indented under their parent task in the same column. Parent shows collapse indicator (▾/▸) and subtask counter.

## Current behavior

All tasks flat in column. Subtasks show `↑{parent}` suffix but no nesting.

## Desired behavior

### Parent row
```
▾2 Parent feature
```
- `▾` = expanded, `▸` = collapsed
- `2` = number of subtasks in this column

### Subtask rows (indented)
```
  • Subtask A
  • Subtask B
```
- Indent level 1 (2 spaces or CSS class `indent-1`)
- No `↑parent` suffix when shown under parent (redundant)
- Keep `↑parent` suffix when subtask in different column from parent

### Collapse behavior
- Press `space` on parent → toggle collapse/expand
- Collapsed parent hides subtasks, shows `▸{n}`
- Expanded parent shows subtasks, shows `▾{n}`
- Persist collapse state? Optional — per-session OK

## Implementation notes

### Data structure
- `load_tasks()` already returns `parent` in `fm`
- Need to group by parent within each column
- Build nested list: `[parent, child, child, parent, ...]` with indent metadata

### Rendering changes in `_reload()`
```python
for t in self.by_col[col]:
    if is_parent(t):
        # render parent with counter + collapse state
        prefix = "▾" if expanded else "▸"
        count = len(subtasks_in_column(t.slug, col))
        label_text = f"{prefix}{count} {t['title']}"
        item = ListItem(Label(prefix_char + label_text), classes="parent")
    elif is_child(t) and parent_expanded_in_column(t, col):
        label_text = t['title']
        item = ListItem(Label("  " + prefix + label_text), classes="indent-1")
    else:
        # standalone or child of collapsed parent — skip child, render standalone
        ...
```

### Keybinding
- `space` on parent ListItem → toggle expand/collapse
- Need `action_toggle_collapse` or handle `on_key` on ListView

### State
- `self._collapsed_parents: set[str]` — parent slugs collapsed
- Persist in memory only (no disk)

## Files

- `src/board_tui/app.py` — `_reload()` rendering, keybinding
- `tests/test_e2e_parent_subtasks.py` — TDD tests already written

## Tests

10 tests in `tests/test_e2e_parent_subtasks.py`:
1. Parent shows collapse indicator + counter
2. Subtasks indented under parent
3. Collapsing parent hides subtasks
4. Expanding collapsed parent shows subtasks
5. Missing parent shows `!` prefix + suffix
6. Detail panel explains missing parent
7. Parent + standalone mixed in column
8. Subtask in different column from parent
9. Counter updates when subtask moved
10. Deep nesting capped at indent 1

## Part of
`board-tui-parent-subtask-display`
