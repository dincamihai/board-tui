---
column: Backlog
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
