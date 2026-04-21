---
column: Done
order: 30
created: 2026-04-21
parent: board-tui-e2e-test-suite
---

# E2E test: Focus switching

Test switching focus between board and detail panes.

## Test cases

- 'tab' switches focus from board to detail
- 'tab' switches focus from detail to board
- Column titles show active state when board focused
- Detail header shows focus indicator when detail focused
- ListView focusable only when board focused
- VerticalScroll focusable only when detail focused

## Result

Created **12 E2E tests** at `tests/test_e2e_focus_switch.py` using Textual's `App.run_test()`
framework with `pytest-asyncio`.

Each test creates a temporary `.tasks` directory via `tmp_path` fixture and populates it with
fixture task markdown files before launching the app inside `async with app.run_test(size=...)` as
`pilot`.

**What was tested:**

| # | Test | Requirement Covered |
|---|------|--------------------|
| 1 | `test_tab_board_to_detail` | Tab from board → detail; VerticalScroll becomes focused |
| 2 | `test_tab_detail_to_board` | Tab from detail → board; ListView becomes focused |
| 3 | `test_column_title_active_state_when_board_focused` | `column-title-active` class on active column |
| 4 | `test_detail_header_focus_indicator` | `▾` caret appears in detail header when focused |
| 5 | `test_detail_header_caret_removed_when_board_focused` | Caret removed when switching back to board |
| 6 | `test_listview_focusable_on_board` | ListView `has_focus` + `focusable` on board |
| 7 | `test_listview_not_focused_when_detail_view_active` | ListView loses focus when detail active |
| 8 | `test_vertical_scroll_focusable_on_detail` | VerticalScroll `has_focus` after tab |
| 9 | `test_vertical_scroll_not_focused_on_board` | VerticalScroll loses focus when board active |
| 10 | `test_tab_cycle_board_to_detail_to_board` | Full round-trip: board → detail → board state consistency |
| 11 | `test_multiple_tabs_cycle` | Odd/even tab presses correctly alternate board↔detail |
| 12 | `test_right_arrow_moves_column_under_board_focus` | Right arrow shifts active column under board focus |

All **12 new tests pass**, and all **11 existing E2E rendering tests** continue to pass.
