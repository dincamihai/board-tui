---
column: Backlog
order: 70
created: 2026-04-21
parent: board-tui-e2e-test-suite
---

# E2E test: Add card

Test adding new task cards.

## Test cases

- 'a' opens add card prompt
- Typing title and pressing enter creates task
- Task created in current column
- Frontmatter includes column and created date
- Slug generated correctly from title
- Duplicate slug shows error notification
- Empty input cancels creation
- Escape cancels creation

## Assertions

- Verify new .md file exists with correct content
- Verify board reloads with new task visible
