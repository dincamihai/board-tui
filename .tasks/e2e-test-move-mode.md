---
column: Done
order: 50
created: 2026-04-21
parent: board-tui-e2e-test-suite
updated: true
---

# E2E test: Move mode

Test move mode for relocating and reordering tasks.

## Test cases

- 'm' toggles move mode (visible in detail header)
- Left/right arrows move task between columns
- Up/down arrows reorder task within column
- Task file updated with new column and timestamp
- Order values adjusted correctly (swaps or reindex)
- Escape exits move mode

## Assertions

- Verify task file content changes after move
- Verify column counts update after move

## Result

Created `tests/test_e2e_move_mode.py` with 7 E2E tests:

1. **test_m_toggles_move_mode** — 'm' toggles move mode, visible in detail header
2. **test_left_right_arrows_move_between_columns** — In move mode, left/right arrows move task between columns
3. **test_task_file_updated_with_column_and_timestamp** — Moving task updates file with new column and timestamp
4. **test_up_down_arrows_reorder_within_column** — In move mode, up/down arrows reorder task within column (swaps order values)
5. **test_escape_exits_move_mode** — Pressing escape exits move mode
6. **test_column_counts_update_after_move** — Column title counts update after moving task
7. **test_move_mode_with_empty_column** — Move mode works even when some columns are empty

All 7 tests pass.

Note: 'enter' key binding for toggle_move exists in app.py but is captured by ListView's enter handler before reaching app. Only 'm' works reliably.
