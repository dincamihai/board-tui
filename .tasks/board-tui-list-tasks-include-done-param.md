---
column: Backlog
order: 10
created: 2026-04-21
---

# board-tui: Add `include_done` param to `list_tasks()` MCP tool

## Problem

`list_tasks()` excludes Done/Superseded columns by default. Test `test_move_task` had to use `column="Done"` workaround.

## Solution

Add explicit `include_done: bool = False` param to `list_tasks()` tool.

## TDD Requirements

1. **Write test first:**
   ```python
   def test_list_tasks_include_done(tmp_path):
       # Setup: create tasks in Backlog, In Progress, Done
       # Assert: list_tasks() excludes Done by default
       # Assert: list_tasks(include_done=True) includes Done tasks
   ```

2. **Make test pass:**
   - Add `include_done` param to `list_tasks()` signature
   - When `include_done=True`, skip the `_DONE_COLUMNS` filter

3. **Refactor:**
   - Ensure backward compat (default `include_done=False`)
   - Update docstring

## Acceptance

- Test written before implementation
- `list_tasks(include_done=True)` returns tasks from all columns
- `list_tasks()` (default) excludes Done/Superseded
- Existing tests still pass
