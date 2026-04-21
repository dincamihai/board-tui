---
column: Backlog
order: 60
created: 2026-04-21
parent: board-tui-e2e-test-suite
---

# E2E test: Search

Test search functionality for finding tasks.

## Test cases

- '/' opens search prompt
- Typing query filters and highlights matches
- 'n' cycles to next match
- Match notification shows count (e.g., "3 matches")
- No matches shows "no matches for 'x'"
- Escape clears search and resets highlighting
- Search matches both title and slug

## Fixture

Tasks with distinctive titles for searchable content.
