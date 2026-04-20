---
column: Done
---

# TUI: show parent slug on subtask cards
## Goal

When a task has `parent` in its frontmatter, show the parent slug on the card in the TUI board view.

## Change

File: `src/board_tui/app.py`

Find line ~122 where `label_text = t["title"]` is set. After that line, append the parent slug to the label if present:

```python
label_text = t["title"]
parent = t["fm"].get("parent")
if parent:
    label_text = f"{label_text}  ↑{parent}"
```

That's the only change needed. One file, three lines.

## Result

Added three lines in `/workspace/src/board_tui/app.py` after the `label_text = t["title"]` assignment in the `_reload` method. When a task has a `parent` key in its YAML frontmatter, the board card now displays an "↑parent-slug" suffix next to the title (e.g., "My Subtask  ↑parent-slug"). Tasks without a parent are unaffected.
