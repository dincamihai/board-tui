---
column: Backlog
order: 80
created: 2026-04-21
parent: board-tui-e2e-test-suite
---

# E2E test: Refresh

Test manual refresh functionality.

## Test cases

- 'r' reloads tasks from disk
- External changes to task files reflected in UI
- Notification shows "refreshed"
- Column counts update after refresh
- Selection preserved if task still exists

## Setup

Modify task file externally during test, then trigger refresh.
