---
column: Backlog
order: 45
created: 2026-04-21
parent: board-tui-e2e-test-suite
---

# E2E test: Scroll behavior

Test scrolling in ListView and detail panel.

## Test cases

- ListView scrolls when tasks exceed visible area
- Detail panel (VerticalScroll) scrolls for long content
- Keyboard navigation works while scrolled
- Scroll position preserved on re-render
- Arrow keys scroll to next item when at edge

## Fixture

- Column with 10+ tasks for ListView scroll
- Task with long body (50+ lines) for detail scroll
