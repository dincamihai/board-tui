---
column: Done
---

# MCP: list_tasks(depends_on=) filter
## Goal

Add `depends_on` filter param to `list_tasks` so callers can find all tasks blocked on a given slug.

## Change

File: `src/board_tui/mcp_server.py`

Add `depends_on: str | None = None` param to `list_tasks`, parallel to existing `parent` param:

```python
def list_tasks(
    column: str | None = None,
    include_done: bool = False,
    backlog_limit: int = 3,
    parent: str | None = None,
    depends_on: str | None = None,
) -> list[dict]:
```

When `depends_on` is set, filter all tasks where `fm.get("depends_on") == depends_on`. Return all matches regardless of column, ignore `include_done` and `backlog_limit` — same pattern as `parent` filter.

Add to docstring:
```
When *depends_on* is set, returns all tasks whose frontmatter ``depends_on``
matches the given slug, across all columns unfiltered.
```

That's the only change needed. One file, ~10 lines.

## Result

Added the `depends_on: str | None = None` parameter to `list_tasks()` in `src/board_tui/mcp_server.py`. Three changes were made:

1. **Parameter** — added `depends_on` to the function signature after `parent`.
2. **Docstring** — added a paragraph describing the depends_on filter behavior.
3. **Filter logic** — added a new `if depends_on is not None:` block (placed after the `parent` block) that filters all tasks where `fm.get("depends_on") == depends_on`, returning them unfiltered across all columns — matching the same pattern as the existing `parent` filter.
