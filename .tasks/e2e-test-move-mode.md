---
column: Backlog
order: 50
created: 2026-04-21
parent: board-tui-e2e-test-suite
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
