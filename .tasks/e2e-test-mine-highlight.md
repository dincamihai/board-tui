---
column: Done
order: 100
created: 2026-04-21
parent: board-tui-e2e-test-suite
updated: true
---

# E2E test: Mine highlighting

Test task highlighting for assigned user.

## Test cases

- Tasks with assigned=user show ♦ prefix and "mine" class
- Tasks with [human] prefix treated as mine
- Other tasks show • prefix
- --user flag changes which tasks are highlighted
- BOARD_TUI_USER env var sets user for highlighting

## Fixture

Tasks with various assigned values and [human] prefix.

## Result

Created `/workspace/tests/test_e2e_mine_highlight.py` with **20 passing tests** covering all five test cases:

### Pure `mine()` function tests
- `test_mine_function_assigned_matches_user` — assigned field matches user (case-insensitive).
- `test_mine_function_human_prefix` — `[human]` prefix matches any user.
- `test_mine_function_neither_matches` — returns `False` when neither condition matches.

### UI: assigned tasks → ♦ + `mine` class
- `test_assigned_task_shows_diamond_prefix` — visible `♦` character in list item text.
- `test_assigned_task_shows_mine_class` — CSS class `"mine"` applied to ListItem.
- `test_non_assigned_task_does_not_have_mine_class` — no `mine` class, uses `•` prefix.

### UI: `[human]` prefix → mine
- `test_human_prefix_shows_diamond` — visible `♦` character.
- `test_human_prefix_shows_mine_class` — `mine` CSS class applied.
- `test_human_prefix_matches_any_user` — mine regardless of which user is active.

### Mixed view
- `test_mixed_tasks_some_mine_some_not` — multiple tasks across columns with correct diamond/bullet distribution.

### `--user` flag
- `test_user_flag_switches_mine_tasks` — flipping `--user` between alice/bob swaps which tasks are highlighted.

### `BOARD_TUI_USER` env var
- `test_board_tui_user_env_var_in_resolve_config` — picks up env var.
- `test_board_tui_user_ignored_when_user_flag_provided` — `--user` takes precedence.
- `test_board_tui_user_fallback_to_user_env` — falls back to `$USER`.
- `test_board_tui_user_env_affects_ui_highlighting` — end-to-end: env var changes the UI highlighting.

### Edge cases
- `test_non_mine_task_has_bullet_prefix` — verifies exact `• Title` format.
- `test_mine_prefix_is_diamond_not_bullet` — confirms no `•` in mine items.
- `test_whitespaper_in_assigned_field` — parser strips whitespace from assigned.
- `test_no_tasks_empty_board` — empty state renders cleanly.
- `test_mine_case_insensitive_user_match` — "Alice" / "alice" / "ALICE" all match.
