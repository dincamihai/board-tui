---
column: Done
order: 45
created: 2026-04-21
parent: board-tui-e2e-test-suite
updated: true
---

# E2E test: Scroll behavior

Test scrolling in ListView and detail panel.

## Test cases

- ListView scrolls when tasks exceed visible area
- Detail panel (VerticalScroll) scrolls for long content
- Keyboard navigation works while scrolled
- Scroll position preserved on re-render
- Arrow keys scroll to next item when at edge

## Fixture

- Column with 10+ tasks for ListView scroll
- Task with long body (50+ lines) for detail scroll

## Result

Created `tests/test_e2e_scroll.py` with 7 E2E tests:

1. **test_listview_scrolls_with_many_tasks** — ListView scrolls when column has more tasks than visible area
2. **test_detail_panel_scrolls_long_body** — Detail panel (VerticalScroll) scrolls for tasks with long body
3. **test_keyboard_navigation_while_scrolled** — Arrow key navigation works after scrolling ListView
4. **test_scroll_position_preserved** — Scroll index preserved when ListView re-renders (via refresh action)
5. **test_arrow_keys_scroll_to_next_item** — Pressing down at edge of visible area scrolls to next item
6. **test_scroll_in_multiple_columns** — Scrolling works independently in each column ListView
7. **test_detail_scroll_shows_all_sections** — Detail panel scroll allows viewing all markdown sections

All 7 tests pass.
