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

Each repo tracks its own work in a `.tasks/` directory at the repo root. Cards are small, self-contained units of work — one clear outcome per card. Rendered by the `board-tui` kanban tool (`~/Repos/board-tui`).

## Card format

```markdown
---
column: Backlog
created: 2026-04-23
order: 10
---

# <short title>

<What needs to be done and why. Self-contained context. Concrete
file paths, line numbers, code sketches where relevant.>
```

### Frontmatter — what `board-tui` reads

| Key | Required | Purpose |
|---|---|---|
| `column` | yes | `Backlog` \| `In Progress` \| `Done` (default columns; overridable via `--columns`) |
| `order` | recommended | integer; lower = higher priority within a column; default 1000 if missing |
| `parent` | optional | slug of another card → renders as subtask under parent (collapsible) |
| `assigned` | optional | username; used by `mine()` to filter "my cards" |
| `created` | optional | free-form text; tool does not parse — use `YYYY-MM-DD` for readability |

Any other frontmatter keys pass through unparsed. Add custom fields (e.g. `priority`, `estimate`) freely — tool ignores them.

### Body

- **Title**: first `# ` heading in the body. Becomes the card label.
- **Free markdown** under the title. No required sections.
- **`## Comments`** (optional): section with lines in format `- **YYYY-MM-DD @author**: text` — parsed by `add_comment()` / `extract_comments()` helpers.
- **`## Result`** (convention, not enforced): some repos use it; tool does not parse. Fill in when moving to Done if the repo convention uses it.

## Slug naming

`<prefix>-<kebab-description>.md`

Prefix should group related cards. Common patterns:
- `<repo-name>-...` for general work: `board-tui-fix-cli-tests.md`
- `<adr-id>-p<N>-...` for ADR phases: `adr-022-p2a-atomize-summarize-prompt-ga.md`
- `human-...` for human-only tasks: `human-triage-931-null-category-concepts.md`

## Creating a card

1. Pick the right repo — card lives where the work lives
2. Keep scope small: one outcome, few files
3. Self-contained body: file paths, line numbers, code sketches, gate criteria
4. Set `column: Backlog`, `order: <N>` (scan siblings for next number — lower = higher priority)
5. Optional: `parent: <slug>` for subtasks, `assigned: <user>`

## Moving a card

- **Starting work**: set `column: In Progress`
- **Delegating to agent**: set `column: In Progress` before handoff
- **Done**: set `column: Done`; if the repo convention uses `## Result`, fill it in with what shipped

## Checking tasks

Find all cards in the workspace:
```bash
find ~/Repos -name "*.md" -path "*/.tasks/*" | sort
```

Render a single repo's board:
```bash
board-tui --tasks-dir <repo>/.tasks/
# Or run from inside a repo; defaults to $PWD/.tasks
```

Environment override: `BOARD_TASKS_DIR`.

When the user asks "what's pending" or "what should we work on", scan all repos.

## Subtask hierarchy

A card with `parent: <slug>` renders indented under its parent in the same column. Parent is collapsible. Use subtasks to break a large phase into small cards without losing the grouping. Orphan children (parent slug not found) render with a marker.

## What makes a good card

- **Small**: completable in one agent session or one focused work block
- **Self-contained**: all context in the card body — no "ask user for clarification"
- **One outcome**: clear definition of done
- **Concrete**: exact files, lines, and changes; not "improve X"
- **Gate**: explicit pass/fail criteria when relevant

Split oversized tasks into smaller cards, order them, delete the parent.

## Cross-repo work

Each repo manages its own `.tasks/`. For cross-repo work, create one card per repo. Cross-link via slug mentions in each body.
