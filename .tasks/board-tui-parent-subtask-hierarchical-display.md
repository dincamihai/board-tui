---
column: Backlog
---

# board-tui: parent-subtask hierarchical display
# board-tui: parent-subtask hierarchical display

## Goal

Render tasks with `parent` frontmatter as hierarchical subindented items under their parent in the kanban board. Support collapse/expand with counters, and warn when parent slug is missing.

## Why

Current flat list with `↑{parent}` suffix is hard to scan. Subtasks look like standalone tasks. Grouping under parent makes hierarchy obvious.

## Subtasks

1. `board-tui-render-subtasks-subindented-under-parent-with-collapse-count`
   - Indent subtasks under parent in same column
   - Parent shows ▾/▸ collapse indicator + subtask counter
   - Space key toggles collapse
   - Counter updates when subtasks moved across columns

2. `board-tui-warn-when-parent-slug-does-not-exist`
   - Orphan subtask shows `!` prefix
   - Detail panel warns that parent slug not found
   - Keep `↑missing-parent` suffix for context

## TDD tests

`tests/test_e2e_parent_subtasks.py` already written (10 tests):
- Parent shows counter + collapse indicator
- Subtasks indented
- Collapse/expand cycle
- Missing parent warning
- Detail panel orphan explanation
- Mixed parent + standalone
- Subtask in different column from parent
- Counter updates on move
- Deep nesting capped at indent 1

## Files

- `src/board_tui/app.py` — `_reload()`, `_update_detail()`, keybindings
- `tests/test_e2e_parent_subtasks.py` — new test file

## Suggested order

1. Add `self._collapsed_parents: set[str]` state to `BoardApp`
2. Modify `_reload()` to group subtasks under parent in each column
3. Add `action_toggle_collapse()` bound to `space`
4. Implement missing-parent warning in `_reload()` + `_update_detail()`
5. Run `pytest tests/test_e2e_parent_subtasks.py`
