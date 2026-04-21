---
column: Done
order: 90
created: 2026-04-21
parent: board-tui-e2e-test-suite
updated: true
---

# E2E test: Copy actions

Test clipboard copy for slug and title.

## Test cases

- 'c' copies slug to clipboard
- 'C' copies title to clipboard
- Notification confirms what was copied
- Mock clipboard command (xclip/pbcopy) for testing

## Fixture

Task with known slug and title to verify copy content.

## Result

Created `tests/test_e2e_copy.py` with **13 E2E tests** covering copy actions using
Textual's `App.run_test()` async context manager with a `pilot` object.

### Tests written

| # | Test name | Requirement covered |
|---|----------|--------------------|
| 1 | `test_c_copies_slug_to_clipboard` | `'c'` copies the selected task's slug to the clipboard |
| 2 | `test_c_copies_correct_slug_with_dash` | Slugs with hyphens copy correctly |
| 3 | `test_c_upper_copies_title_to_clipboard` | `'C'` copies the selected task's title to the clipboard |
| 4 | `test_c_upper_copies_title_with_special_chars` | Titles with special characters and numbers copy correctly |
| 5 | `test_copy_slug_shows_notification` | Copying slug produces a "copied slug:" notification |
| 6 | `test_copy_title_shows_notification` | Copying title produces a "copied title:" notification |
| 7 | `test_notification_confirms_copied_content` | Notification message includes the actual copied value |
| 8 | `test_subprocess_run_called_with_xclip_on_linux` | Clipboard command uses `xclip` on Linux |
| 9 | `test_text_true_passed_to_subprocess` | `subprocess.run(text=True)` so input is a string |
| 10 | `test_check_false_passed_to_subprocess` | `subprocess.run(check=False)` doesn't crash on failure |
| 11 | `test_copy_with_no_task_selected_does_nothing` | No subprocess call when no task is selected |
| 12 | `test_copy_different_tasks_yields_different_content` | Selecting different tasks copies different slugs |
| 13 | `test_c_and_upper_c_produce_different_content` | `'c'` (slug) and `'C'` (title) produce different data |

### Key implementation details

- **Clipboard mock**: Patches `board_tui.app.subprocess.run` directly (where the import lives) with a side-effect function that captures the last `(args, kwargs)` call on a module-level attribute for inspection.
- **Test isolation**: Each test calls `_reset_mock()` at the start to ensure stale mock state from previous tests doesn't leak.
- **Fixture tasks**: Two task markdown blocks (`_TASK_SLUG_FIX_LOGIN`, `_TASK_TITLE_OAUTH2`) with known, distinct slugs and titles in the `Backlog` column so the default-focused column has a selection.
- **Notification capture**: Reads `app._notifications` after key presses to verify the correct "copied slug:" / "copied title:" messages are emitted.

All **13 tests pass** (bringing the total E2E suite to 131 tests, 15 skipped).
