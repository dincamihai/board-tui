---
column: Backlog
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
