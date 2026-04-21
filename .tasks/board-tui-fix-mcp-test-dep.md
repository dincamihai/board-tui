---
column: Backlog
order: 5
created: 2026-04-21
---

# board-tui: Fix MCP test dependency (missing `mcp` module)

## Problem

Running `pytest tests/test_mcp.py` fails with:

```
ModuleNotFoundError: No module named 'mcp'
```

15 MCP tests fail due to missing `mcp` package in test environment.

## Root cause

`mcp` package listed in `pyproject.toml` dependencies but not installed in test environment.

## Fix options

1. **Install mcp in test env**
   ```bash
   pip install mcp
   ```

2. **Add mcp to dev dependencies** in `pyproject.toml`:
   ```toml
   [project.optional-dependencies]
   dev = ["pytest", "mcp"]
   ```
   Then: `pip install -e ".[dev]"`

3. **Skip MCP tests** if mcp not available:
   ```python
   @pytest.mark.skipif(not HAS_MCP, reason="mcp not installed")
   ```

## Acceptance

- `pytest tests/test_mcp.py` passes
- Or: tests gracefully skipped with clear message
