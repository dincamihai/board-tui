"""MCP server for board-tui board operations.

Reads BOARD_TASKS_DIR from the environment at startup. All tools operate on
that directory for the lifetime of the server process.
"""

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from board_tui.tasks import dump, load_tasks, parse, slugify
from board_tui.tasks import set_frontmatter_field

# BOARD_TASKS_DIR is read at server startup — one server per board.
_tasks_dir = Path(os.environ["BOARD_TASKS_DIR"])
DEFAULT_COLUMNS = ["Backlog", "In Progress", "Done"]

# Columns to exclude from default list_tasks calls (archived / closed states)
_DONE_COLUMNS = frozenset({"Done", "Superseded"})

mcp = FastMCP("board-tui")


@mcp.tool()
def list_columns() -> list[str]:
    """Return all column names defined by the current tasks directory."""
    tasks = load_tasks(_tasks_dir, DEFAULT_COLUMNS)
    seen = set()
    cols = []
    for t in tasks:
        col = t["column"]
        if col not in seen:
            seen.add(col)
            cols.append(col)
    return cols


@mcp.tool()
def list_tasks(
    column: str | None = None,
    include_done: bool = False,
    backlog_limit: int = 3,
    parent: str | None = None,
    depends_on: str | None = None,
) -> list[dict]:
    """Return tasks, optionally filtered by column. Optionally filter by parent.

    By default Done and Superseded columns are excluded.  Backlog entries are
    limited to *backlog_limit* (default 3).  Pass *include_done=True* or an
    explicit *column* to opt-in.

    When *parent* is set, returns all direct children (any column, including
    Done) whose frontmatter ``parent`` matches the given slug.  In this mode
    *include_done* and *backlog_limit* are ignored — all matching children are
    returned unfiltered.

    When *depends_on* is set, returns all tasks whose frontmatter ``depends_on``
    matches the given slug, across all columns unfiltered.
    """
    tasks = load_tasks(_tasks_dir, DEFAULT_COLUMNS)

    if parent is not None:
        # Parent filter mode: return all direct children, regardless of column.
        children = [t for t in tasks if t["fm"].get("parent", "") == parent]
        return [
            {
                "slug": t["slug"],
                "title": t["title"],
                "column": t["column"],
                "order": t["order"],
                "body": t["body"],
            }
            for t in children
        ]

    if depends_on is not None:
        # Depends-on filter mode: return all tasks blocked on a given slug,
        # regardless of column.
        dependents = [t for t in tasks if t["fm"].get("depends_on") == depends_on]
        return [
            {
                "slug": t["slug"],
                "title": t["title"],
                "column": t["column"],
                "order": t["order"],
                "body": t["body"],
            }
            for t in dependents
        ]

    if column:
        # Explicit column filter — honor it as-is (even for Done columns).
        tasks = [t for t in tasks if t["column"] == column]
    elif not include_done:
        # Default mode: exclude Done / Superseded columns.
        tasks = [t for t in tasks if t["column"] not in _DONE_COLUMNS]

    # Limit Backlog entries (only in default mode, i.e. no explicit column).
    if backlog_limit and not column:
        filtered = []
        backlog_count = 0
        for t in tasks:
            if t["column"] == "Backlog":
                if backlog_count < backlog_limit:
                    filtered.append(t)
                    backlog_count += 1
            else:
                filtered.append(t)
        tasks = filtered

    return [
        {
            "slug": t["slug"],
            "title": t["title"],
            "column": t["column"],
            "order": t["order"],
            "body": t["body"],
        }
        for t in tasks
    ]


@mcp.tool()
def get_task(slug: str) -> dict | None:
    """Return full task content by slug. Returns None if not found.

    The response includes a ``children`` list of direct subtasks (tasks whose
    frontmatter ``parent`` matches *slug*).
    """
    path = _tasks_dir / f"{slug}.md"
    if not path.exists():
        return None
    fm, body = parse(path)

    # Scan all tasks for children.
    all_tasks = load_tasks(_tasks_dir, DEFAULT_COLUMNS)
    children = [
        {"slug": t["slug"], "title": t["title"], "column": t["column"]}
        for t in all_tasks
        if t["fm"].get("parent", "") == slug
    ]

    return {
        "slug": slug,
        "title": fm.get("title", slug),
        "column": fm.get("column", "Backlog"),
        "order": fm.get("order", "1000"),
        "fm": fm,
        "body": body,
        "children": children,
    }


@mcp.tool()
def move_task(slug: str, column: str) -> dict | None:
    """Move a task to a different column. Returns the updated task."""
    path = _tasks_dir / f"{slug}.md"
    if not path.exists():
        return None
    fm, body = parse(path)
    fm["column"] = column
    fm["updated"] = "true"
    dump(path, fm, body)
    return {
        "slug": slug,
        "title": fm.get("title", slug),
        "column": column,
        "order": fm.get("order", "1000"),
        "body": body,
    }


@mcp.tool()
def create_task(slug: str = "", title: str = "", column: str | None = None, body: str = "") -> dict:
    """Create a new task file. slug is auto-generated from title if omitted."""
    if not slug:
        slug = slugify(title)
    path = _tasks_dir / f"{slug}.md"
    if path.exists():
        raise FileExistsError(f"Task '{slug}' already exists")
    if column is None:
        column = DEFAULT_COLUMNS[0]
    fm = {"column": column}
    dump(path, fm, f"# {title}\n{body}\n")
    return {
        "slug": slug,
        "title": title,
        "column": column,
        "order": "1000",
        "body": f"# {title}\n{body}",
    }


@mcp.tool()
def update_task(slug: str, body: str, title: str | None = None, column: str | None = None) -> dict | None:
    """Overwrite task body (and optionally title/column). Returns updated task."""
    path = _tasks_dir / f"{slug}.md"
    if not path.exists():
        return None
    fm, _ = parse(path)
    if title:
        fm["title"] = title
    if column:
        fm["column"] = column
    dump(path, fm, body)
    return {
        "slug": slug,
        "title": fm.get("title", slug),
        "column": fm.get("column", column or "Backlog"),
        "order": fm.get("order", "1000"),
        "body": body,
    }


@mcp.tool()
def delete_task(slug: str) -> bool:
    """Remove a task file. Returns True if deleted, False if not found."""
    path = _tasks_dir / f"{slug}.md"
    if not path.exists():
        return False
    path.unlink()
    return True


@mcp.tool()
def set_frontmatter(slug: str, key: str, value: str) -> dict | None:
    """Set or update a single frontmatter field in a task card."""
    path = _tasks_dir / f"{slug}.md"
    if not path.exists():
        return None
    set_frontmatter_field(path, key, value)
    fm, body = parse(path)
    return {"slug": slug, "key": key, "value": value, "column": fm.get("column", "")}


@mcp.tool()
def list_delegated_tasks(status: str | None = None) -> list[dict]:
    """Return tasks with delegation_status frontmatter.

    When *status* is set, filter by that status (queued/processing/done/failed/cancelled).
    Otherwise return all tasks that have any delegation_status.
    """
    tasks = load_tasks(_tasks_dir, DEFAULT_COLUMNS)
    out = []
    for t in tasks:
        ds = t["fm"].get("delegation_status")
        if ds is None:
            continue
        if status and ds != status:
            continue
        out.append({
            "slug": t["slug"],
            "title": t["title"],
            "column": t["column"],
            "order": t["order"],
            "delegation_status": ds,
            "body": t["body"],
        })
    return out
