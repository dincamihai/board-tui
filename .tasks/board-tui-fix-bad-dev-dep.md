---
column: Done
created: 2026-04-19
order: 6
---

# board-tui: fix bad dev dependency

`pyproject.toml` lists `pytest-textual` as a dev dep but that package does not exist on PyPI. The real package for Textual snapshot tests is `pytest-textual-snapshot`, but board-tui has no snapshot tests.

Fix: remove `pytest-textual` from `[project.optional-dependencies].dev`; keep only `pytest`.
