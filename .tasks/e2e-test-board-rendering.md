---
column: Done
order: 10
created: 2026-04-21
parent: board-tui-e2e-test-suite
---

# E2E test: Board rendering

Test that board renders correctly with columns and tasks.

## Test cases

- [x] Empty .tasks dir shows empty columns with (0) counts
- [x] Tasks appear in correct columns based on frontmatter
- [x] Column counts update correctly
- [x] Task titles display with prefix (• or ♦ for mine)
- [x] Order is respected (lower order = higher in list)

## Fixture

Create 3-4 tasks with different columns and order values.

## Result

Wrote **11 E2E tests** in `tests/test_e2e_board_rendering.py` covering board rendering
using Textual's `App.run_test()` async context manager with a `pilot` object.

### Tests written

| # | Test name | Requirement covered |
|---|-----------|--------------------|
| 1 | `test_empty_tasks_dir_shows_zero_counts` | Empty .tasks dir → columns with (0) |
| 2 | `test_missing_tasks_dir_graceful` | Missing .tasks dir → still renders (0) |
| 3 | `test_tasks_in_correct_columns` | Tasks land in correct columns |
| 4 | `test_column_counts_update_after_add` | Column counts update after refresh |
| 5 | `test_task_titles_show_mine_prefix` | ✓ mine prefix (♦ / •) |
| 6 | `test_task_titles_no_mine_when_user_differs` | Non-mine tasks show • only |
| 7 | `test_assigned_tasks_prefix_for_other_user` | Cross-user mine prefix |
| 8 | `test_order_is_respected_within_column` | Lower order → higher in list |
| 9 | `test_multiple_tasks_backlog_order` | Multi-task ordering in Backlog |
| 10 | `test_order_across_columns_no_cross_contamination` | Order is per-column |
| 11 | `test_tab_navigation_updates_active_column` | Tab navigation + active styling |

### Key implementation details

- Uses **pytest-asyncio** (AUTO mode) for async test functions.
- Each test creates a **temp directory** via `tmp_path` fixture and populates it with
  markdown task files containing frontmatter (`column`, `order`, `assigned`, etc.).
- The `BoardApp` is instantiated with `tasks_dir`, `columns`, and `user` parameters.
- **`pilot.pause()`** is called after app mount and after each key press for timing.
- **`pilot.press("r")`**, **`pilot.press("tab")`** simulate keyboard actions.
- Helper `_get_list_titles()` walks `ListView.children` → `ListItem` → child `Label`
  to extract rendered task title strings for assertion.

### Verification

All **11 tests pass** (plus all 17 pre-existing tests for `cli` and `tasks`).
The 15 MCP tests fail due to a pre-existing missing `mcp` module dependency,
unrelated to these changes.
