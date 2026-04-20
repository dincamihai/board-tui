---
name: task-cards
description: >
  How to create, read, update, and manage task cards across multiple repos.
  Use this skill whenever the user mentions tasks, cards, .tasks, backlog,
  a kanban board, wants to create a new task, check what's pending, move a card,
  or delegate work. Also use when creating task cards as part of planning work
  in any repo.
---

# Task Cards

Each repo tracks its own work in a `.tasks/` directory at the repo root. Cards are small, self-contained units of work — one clear outcome per card.

## Card format

```markdown
---
column: Backlog
created: YYYY-MM-DD
order: N
---

# <repo>: <short title>

<What needs to be done and why. Include enough context for someone (or an agent) to complete the task without asking questions.>

## Result
```

- `column`: `Backlog` | `In Progress` | `Done`
- `order`: integer, lower = higher priority within a column
- `## Result` section: empty until task completes — agent or human fills it in

## Slug naming

`<repo-name>-<kebab-description>.md`

Examples: `board-tui-fix-cli-tests.md`, `local-agent-auto-worktree.md`

## Creating a card

1. Pick the right repo — card lives where the work lives
2. Keep scope small: one outcome, a few files at most
3. Write enough context that the card is self-contained (no need to ask follow-up questions)
4. Set `column: Backlog`, `created: <today>`, assign `order` (check existing cards for next available number)
5. Leave `## Result` empty

## Moving a card

- **Starting work**: set `column: In Progress`
- **Delegating to agent**: set `column: In Progress` before calling `pi_start`
- **Done**: set `column: Done`, fill in `## Result` with what was done

## Checking tasks

Tasks are spread across repos. To find all cards in the workspace:
```bash
find ~/repos -name "*.md" -path "*/.tasks/*" | sort
```

To see a single repo's board, the `board-tui` CLI renders them as a kanban board:
```bash
board-tui --tasks-dir <repo>/.tasks/
```

When the user asks "what's pending" or "what should we work on", scan all repos.

## What makes a good card

- **Small**: completable in one agent session or one focused work block
- **Self-contained**: all context needed is in the card body
- **One outcome**: clear definition of done
- **Concrete**: says exactly what to change, not just "improve X"

If a task is too big, split it into smaller cards, add them to Backlog with appropriate `order` values, and delete the oversized card.

## Cross-repo work

Each repo manages its own `.tasks/`. When work spans repos, create one card per repo. Link them by mentioning the sibling card slug in each card's body.
