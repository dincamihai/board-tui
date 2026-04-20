---
column: In Progress
order: 1
---

# board-tui repo scaffold

Created `~/repos/board-tui/` with full package structure.

## Done
- [x] `pyproject.toml` (hatchling build, textual dep, CLI entry point)
- [x] `README.md`, `LICENSE`, `CHANGELOG.md`
- [x] `src/board_tui/__init__.py` (v0.1.0)
- [x] `src/board_tui/__main__.py`
- [x] `src/board_tui/tasks.py` (pure functions)
- [x] `src/board_tui/app.py` (BoardApp + PromptScreen)
- [x] `src/board_tui/cli.py` (argparse + env vars)
- [x] `tests/test_tasks.py` (slugify, parse, dump)
- [x] `tests/test_cli.py` (CLI resolution)
- [x] `pip install -e .` succeeded
- [x] `board-tui --help` works
- [x] `board-tui --version` prints `board-tui 0.1.0`

## Remaining
- [ ] `git init` in board-tui repo
- [ ] Run tests: `pytest board-tui/tests/ -v`
- [ ] Delete `membrain/scripts/board.py`
- [ ] Delete `zen-color-studio/scripts/board.py`
- [ ] Update docs/README to reference `board-tui` instead
