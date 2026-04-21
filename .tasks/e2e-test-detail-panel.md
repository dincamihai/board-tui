---
column: Done
order: 40
created: 2026-04-21
parent: board-tui-e2e-test-suite
---

# E2E test: Detail panel

Test detail panel displays task info correctly.

## Test cases

- Selected task shows title, slug, column in header
- Metadata list shows all frontmatter fields except column
- Task body renders as Markdown
- Comments section renders below body (if present)
- Empty selection shows "no selection"
- Move mode header changes to "MOVE" instruction
- Focus indicator shows when detail pane focused (▾ prefix)

## Assertions

- Markdown widget contains expected text
- Comments appear formatted correctly

## Result

Created `tests/test_e2e_detail_panel.py` with 9 E2E tests:

1. **test_detail_header_shows_title_slug_column** — Title, slug (`full-task`), and column (`_Backlog_`) appear in detail Markdown
2. **test_detail_metadata_shows_frontmatter_fields** — Frontmatter fields (created, assigned, priority, parent) render as `- **key**: value`; column excluded
3. **test_detail_body_renders_markdown** — Task body content with markdown formatting preserved
4. **test_detail_comments_render_below_body** — Comments section appears below body with author/date formatting
5. **test_detail_empty_selection_shows_placeholder** — Empty tasks dir shows `_no selection_` placeholder
6. **test_detail_move_mode_header_changes** — Setting `move_mode=True` updates header to "MOVE · arrows relocate · enter/esc done"
7. **test_detail_focus_indicator_shows_prefix** — Focus switch adds `▾` prefix to DETAIL header when detail pane focused
8. **test_navigation_updates_detail_panel** — Down arrow selects different task, detail updates accordingly
9. **test_markdown_widget_queryable_with_expected_content** — Markdown widget queryable, heading (###) and slug line verified

All 9 tests pass. Total E2E suite: 41 tests (12 focus + 9 parent + 9 detail + 11 rendering).
