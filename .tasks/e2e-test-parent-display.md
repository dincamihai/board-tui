---
column: Done
order: 35
created: 2026-04-21
parent: board-tui-e2e-test-suite
---

# E2E test: Parent task display

Test parent slug display in list items (↑parent feature).

## Test cases

- Tasks with `parent` frontmatter show "↑{parent}" suffix
- Parent slug displayed after task title
- No suffix when parent is empty/missing
- Subtasks indented or visually distinct (if implemented)

## Fixture

Tasks with parent field set:
```yaml
parent: main-feature
```

Title displays as: "Subtask title ↑main-feature"

## Result

Created `tests/test_e2e_parent_display.py` with 9 E2E tests covering all requirements:

1. **`test_parent_frontmatter_shows_up_suffix`** — Verifies that a task with `parent: main-feature` shows `↑main-feature` in the ListView item text.
2. **`test_parent_slug_displayed_after_title`** — Confirms the parent slug appears *after* the title (e.g. `• Login page auth  ↑feat-auth`), preserving the original prefix.
3. **`test_no_suffix_when_parent_missing`** — Ensures a task without any `parent` frontmatter field renders with no suffix.
4. **`test_no_suffix_when_parent_empty_string`** — Ensures an explicit `parent:` (empty value) does not produce a suffix.
5. **`test_no_suffix_when_parent_whitespace_only`** — Ensures a parent containing only whitespace does not produce a suffix.
6. **`test_parent_with_other_frontmatter_fields`** — Verifies the suffix renders correctly alongside other frontmatter (assigned, priority), and user-based "mine" prefix (`♦`) still works.
7. **`test_mixed_parent_and_no_parent_in_same_column`** — Checks that tasks with and without parent coexist in the same column ListView with correct per-item suffixes.
8. **`test_parent_suffix_ordering`** — Confirms the parent suffix does not interfere with `order`-based sorting.
9. **`test_parent_suffix_visible_on_all_columns`** — Validates the suffix renders in Backlog, In Progress, and Done columns.

All tests use `Textual App.run_test()` with `pytest-asyncio` in auto mode, following the same patterns as `test_e2e_focus_switch.py` and `test_e2e_board_rendering.py`.
