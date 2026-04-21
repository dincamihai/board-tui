---
column: Done
order: 70
created: 2026-04-21
parent: board-tui-e2e-test-suite
updated: true
---

# E2E test: Add card

Test adding new task cards.

## Test cases

- 'a' opens add card prompt
- Typing title and pressing enter creates task
- Task created in current column
- Frontmatter includes column and created date
- Slug generated correctly from title
- Duplicate slug shows error notification
- Empty input cancels creation
- Escape cancels creation

## Assertions

- Verify new .md file exists with correct content
- Verify board reloads with new task visible

## Result

11 tests added in `tests/test_e2e_add_card.py`:
- test_a_opens_add_card_prompt
- test_enter_creates_task
- test_task_created_in_current_column
- test_frontmatter_includes_column_and_created_date
- test_slug_generated_correctly_from_title
- test_duplicate_slug_shows_error
- test_empty_input_cancels_creation
- test_escape_cancels_creation
- test_board_reloads_with_new_task_visible
- test_detail_panel_shows_new_task
- test_create_multiple_tasks_independent_columns

All 11 tests pass.
