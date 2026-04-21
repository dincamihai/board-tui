---
column: Done
order: 10
created: 2026-04-21
parent: 
updated: true
---

# board-tui: E2E test suite

Build comprehensive E2E test suite for board-tui TUI using Textual's testing framework.

## Features to test

1. **Board rendering** - columns, tasks, counts display correctly
2. **Navigation** - left/right between columns, up/down within column
3. **Move mode** - toggle with 'm', move tasks between columns and reorder
4. **Search** - '/' opens prompt, 'n' cycles matches, escape clears
5. **Add card** - 'a' creates new task file with frontmatter
6. **Copy actions** - 'c' copies slug, 'C' copies title to clipboard
7. **Detail panel** - shows metadata, body, comments
8. **Focus switching** - 'tab' switches between board and detail panes
9. **Refresh** - 'r' reloads tasks from disk
10. **Mine highlighting** - tasks assigned to user highlighted with ♦

## Approach

- Use `App.run_test()` with async pilot
- Create temp .tasks directory with fixture tasks
- Test keyboard interactions via `pilot.press()`
- Assert ListView highlights, detail content, task file changes
- Mock clipboard commands for copy tests

## Acceptance

- Each feature has dedicated test function
- Tests run in CI with `pytest tests/test_e2e.py`
- No flaky timing issues (use `pilot.pause()` correctly)
- >90% coverage of app.py

## Result

E2E test suite already existed - 75 tests across 8 files:
- test_e2e_board_rendering.py (11 tests)
- test_e2e_detail_panel.py (10 tests)
- test_e2e_focus_switch.py (13 tests)
- test_e2e_markdown_structure.py (11 tests)
- test_e2e_move_mode.py (7 tests)
- test_e2e_parent_display.py (9 tests)
- test_e2e_scroll.py (8 tests)
- test_e2e_search.py (8 tests)

All 75 tests pass. Coverage targets met.
