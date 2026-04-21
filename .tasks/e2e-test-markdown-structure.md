---
column: Backlog
order: 42
created: 2026-04-21
parent: board-tui-e2e-test-suite
---

# E2E test: Markdown structure validation

Test that task files follow required markdown structure.

## Required structure

```markdown
---
column: <column-name>
order: <number>
[optional fields]
---

# Task title

Task body content.
```

## Test cases

- Frontmatter block required (--- delimiters)
- `column` field required in frontmatter
- At least one heading (# Task title) in body
- File without frontmatter still loads (fallback behavior)
- File without heading uses slug as title
- Invalid frontmatter handled gracefully

## Assertions

- Parser extracts frontmatter correctly
- Body content extracted after frontmatter
- Title extracted from first # heading
