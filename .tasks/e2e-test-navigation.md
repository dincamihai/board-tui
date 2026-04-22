---
column: Done
order: 20
created: 2026-04-21
parent: board-tui-e2e-test-suite
updated: true
---

# E2E test: Navigation

Test keyboard navigation between columns and tasks.

## Test cases

- Right arrow moves to next column (wraps around)
- Left arrow moves to previous column (wraps around)
- Up/down arrows navigate tasks within column
- Selected task highlighted in ListView
- Detail panel updates on selection change

## Fixture

Multiple tasks per column to test vertical navigation.

## Result

18 E2E tests written to `tests/test_e2e_navigation.py`, all passing:

### Column navigation (right/left arrows)
- `test_right_arrow_moves_to_next_column` — verifies Backlog → In Progress → Done cycle
- `test_right_arrow_wraps_to_first_column` — wraps from last column back to first
- `test_left_arrow_moves_to_previous_column` — verifies Done → In Progress → Backlog cycle
- `test_left_arrow_wraps_to_last_column` — wraps from first column to last

### Task navigation (up/down arrows)
- `test_down_arrow_navigates_down_in_list` — moves down, stops at edge
- `test_up_arrow_navigates_up_in_list` — moves up, stops at edge
- `test_up_down_in_different_columns` — independent navigation per column
- `test_right_arrow_resets_list_index_in_new_column` — list index resets on column switch

### ListView highlighting
- `test_listview_index_changes_with_down_arrow` — index tracks highlight
- `test_listview_index_tracks_column_switch` — index correct across columns

### Detail panel updates
- `test_detail_panel_updates_on_down_navigation` — content changes with task navigation
- `test_detail_panel_updates_on_column_switch` — content changes on column switch
- `test_detail_panel_reflects_wrapped_column_navigation` — consistent across wrapped navigation
- `test_detail_panel_updates_on_left_navigation` — content updates on left arrow
- `test_detail_empty_when_no_selection` — shows placeholder for empty columns

### Combined / comprehensive
- `test_full_column_cycle_with_nesting` — full cycle of all navigation directions
- `test_column_title_active_state_follows_navigation` — title highlight follows navigation
- `test_column_counts_in_titles_follow_navigation` — counts remain correct
