# board-tui

Textual-based TUI kanban board for `.tasks/*.md` markdown files with YAML frontmatter.

![demo](demo.gif)

Pairs with [local-agent](https://github.com/dincamihai/local-agent) — delegate a card to a local LLM that updates it when done.

## Install

```bash
pipx install git+https://github.com/dincamihai/board-tui
```

Or install from source:

```bash
pip install -e .
```

## Usage

```bash
# Read .tasks/ in CWD
board-tui

# Read from a specific directory
board-tui --tasks-dir ~/projects/myproject/.tasks

# Custom columns
board-tui --columns Backlog,Review,Done

# Filter by user
board-tui --user alice
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `BOARD_TUI_TASKS_DIR` | `CWD/.tasks` | Path to .tasks directory |
| `BOARD_TUI_COLUMNS` | `Backlog,In Progress,Done` | Comma-separated column names |
| `BOARD_TUI_USER` | `$USER` | Username for card highlighting |

CLI flags take precedence over env vars.

## Key bindings

| Key | Action |
|---|---|
| `← →` | Navigate columns |
| `↑ ↓` | Navigate cards / scroll detail |
| `tab` | Switch focus between board and detail |
| `enter` / `m` | Toggle move mode |
| `/` | Search |
| `n` | Next search match |
| `a` | Add new card |
| `c` | Copy slug to clipboard |
| `C` | Copy title to clipboard |
| `r` | Force refresh |
| `q` | Quit |

## MCP server

board-tui ships a built-in MCP (Model Context Protocol) server that exposes board operations as tools. LLM agents can call these tools to read and mutate board tasks without needing direct shell access.

### Launch

```bash
board-tui-mcp
```

The server reads the `BOARD_TASKS_DIR` environment variable at startup to determine which `.tasks` directory to serve. Configure one server instance per board in your MCP client config:

```json
{
  "mcpServers": {
    "board-local-agent": {
      "command": "board-tui-mcp",
      "env": { "BOARD_TASKS_DIR": "/path/to/local-agent/.tasks" }
    },
    "board-zen": {
      "command": "board-tui-mcp",
      "env": { "BOARD_TASKS_DIR": "/path/to/zen/.tasks" }
    }
  }
}
```

### Available tools

| Tool | Description |
|---|---|
| `list_columns` | Return all column names currently in use |
| `list_tasks` | Return all tasks (optionally filter by `column`) |
| `get_task` | Return full task content by slug |
| `move_task` | Move a task to a different column |
| `create_task` | Create a new task file |
| `update_task` | Overwrite task body/title/column |
| `delete_task` | Remove a task file |

### Examples

```python
# List all columns
list_columns()

# List tasks in Backlog
list_tasks(column="Backlog")

# Get a specific task
get_task(slug="my-feature")

# Move a task to Done
move_task(slug="my-feature", column="Done")

# Create a new task
create_task(slug="new-feature", title="New feature", column="Backlog", body="Description here")

# Update task body
update_task(slug="my-feature", body="Updated description", title="New title")

# Delete a task
delete_task(slug="old-task")
```

## File format

Cards are `.md` files in `.tasks/` with YAML frontmatter:

```markdown
---
column: In Progress
order: 10
assigned: alice
created: 2026-04-19
---

# My task title

Task body content here.
```
