---
column: Backlog
---

# board-tui: warn when parent slug does not exist
# board-tui: warn when parent slug does not exist

## Goal

When a task has `parent: some-slug` but no task file with that slug exists, show visual warning and explain in detail panel.

## Why

Orphan subtasks happen when parent is deleted or renamed. User should know parent is missing.

## Visual indicator

- Prefix `!` on ListItem label: `! • Orphan subtask ↑missing-parent`
- Keep `↑missing-parent` suffix for context
- Optional: `classes="orphan"` for CSS styling (red tint)

## Detail panel explanation

When orphan subtask selected, detail panel markdown includes:
```markdown
### Orphan subtask

`orphan-sub` · _Backlog_

- **parent**: missing-parent ⚠️ _(not found)_
- ... other fields ...

This task references a parent that does not exist.
Consider updating the `parent` frontmatter or creating the parent task.

Body text here.
```

## Implementation

In `_reload()`:
```python
all_slugs = {t["slug"] for t in self.tasks}
for t in self.by_col[col]:
    parent = t["fm"].get("parent")
    if parent and parent not in all_slugs:
        prefix = "! " + prefix  # prepend warning
```

In `_update_detail()`:
```python
for k, v in sel["fm"].items():
    if k == "parent":
        parent_slug = v
        if parent_slug not in all_slugs:
            md.append(f"- **{k}**: {v} ⚠️ _(not found)_")
            md.append("")
            md.append(f"> Task references parent `{parent_slug}` which does not exist.")
        else:
            md.append(f"- **{k}**: {v}")
    ...
```

## Files

- `src/board_tui/app.py` — `_reload()`, `_update_detail()`
- `tests/test_e2e_parent_subtasks.py` — TEST 5-6 cover this

## Part of
`board-tui-parent-subtask-display`
