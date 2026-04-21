---
column: Backlog
order: 90
created: 2026-04-21
parent: board-tui-e2e-test-suite
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
