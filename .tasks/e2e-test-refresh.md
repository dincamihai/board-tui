---
column: Done
order: 80
created: 2026-04-21
parent: board-tui-e2e-test-suite
updated: true
---

# E2E test: Refresh

Test manual refresh functionality.

## Test cases

- 'r' reloads tasks from disk
- External changes to task files reflected in UI
- Notification shows "refreshed"
- Column counts update after refresh
- Selection preserved if task still exists

## Setup

Modify task file externally during test, then trigger refresh.

## Result

Created `/workspace/tests/test_e2e_refresh.py` with 8 E2E tests, all passing. Tests use
Textual's `App.run_test()` with async pilots and a temp `.tasks` directory populated with
fixture markdown files.

### Coverage

| # | Test | What it validates |
|---|------|-------------------|
| 1 | `test_r_key_reloads_tasks_from_disk` | Pressing **r** re-reads the filesystem; deleted tasks disappear |
| 2 | `test_external_changes_reflected_in_ui` | Renaming a task file on disk is reflected in both the list and the detail panel after refresh |
| 3 | `test_notification_shows_refreshed` | The `notify("refreshed")` call in `action_refresh` emits a notification capturing the message |
| 4 | `test_column_counts_update_after_refresh` | Removing and adding files on disk updates every column title paren count |
| 5 | `test_selection_preserved_if_task_still_exists` | If the currently selected item remains on disk, its index is preserved after reload |
| 6 | `test_selection_cleared_when_task_removed` | If the selected item is removed, fallback to index 0 works cleanly |
| 7 | `test_new_task_files_reflected_on_refresh` | Newly written `.md` files appear in the correct column after refresh |
| 8 | `test_multiple_refreshes` | Chained **r** presses keep producing correct, consistent state |

### Test data

Three fixture task blocks (`_TASK_A`, `_TASK_B`, `_TASK_C`) cover:
- **Backlog** column (α-order, assigned to alice)
- **In Progress** column (β-order, assigned to alice)
- **Backlog** column (γ-order, unassigned)

These are reused across all 8 tests with `tmp_path` giving each test an isolated filesystem.
