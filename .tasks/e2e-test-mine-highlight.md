---
column: Backlog
order: 100
created: 2026-04-21
parent: board-tui-e2e-test-suite
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
