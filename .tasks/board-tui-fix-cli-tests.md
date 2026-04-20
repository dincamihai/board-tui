---
column: Done
created: 2026-04-19
order: 8
---

# board-tui: fix CLI tests — they assert nothing

All tests in `tests/test_cli.py` call `main()` which immediately tries to launch the Textual TUI (a real terminal app). They wrap this in try/except SystemExit but have no assertions — they pass vacuously regardless of what the CLI does.

Fix: refactor CLI so the argument-resolution logic is a pure function (returns a config dict) that can be tested without launching the app. Test that function instead. Keep `main()` as a thin wrapper that calls `BoardApp(**config).run()`.

Example:
```python
# cli.py
def resolve_config(argv=None) -> dict:
    ...  # parse args, env vars, return {tasks_dir, columns, user}

def main():
    BoardApp(**resolve_config()).run()
```
Then `test_cli.py` tests `resolve_config()` directly.

## Result

**`src/board_tui/cli.py`** — Added `resolve_config(argv=None)` function that extracts the argument parsing and env var resolution into a pure function returning `{tasks_dir, columns, user}`. Moved the argparse/env logic from `main()` into this function. `main()` is now a thin wrapper: `BoardApp(**resolve_config()).run()`.

**`tests/test_cli.py`** — Replaced all vacuous tests (which called `main()` with no assertions) with 8 targeted tests for `resolve_config()`:
1. `test_resolve_config_defaults` — verifies default values for tasks_dir, columns, and user
2. `test_resolve_config_args_override_defaults` — verifies CLI flags set config when no env vars present
3. `test_resolve_config_args_take_precedence_over_env` — verifies CLI flags beat env vars
4. `test_resolve_config_env_tasks_dir` — verifies `$BOARD_TUI_TASKS_DIR` fallback
5. `test_resolve_config_env_columns` — verifies `$BOARD_TUI_COLUMNS` fallback
6. `test_resolve_config_user_priority` — verifies the full --user > $BOARD_TUI_USER > $USER > "unknown" priority chain
7. `test_resolve_config_columns_whitespace` — verifies comma-split whitespace trimming
8. `test_resolve_config_tasks_dir_resolved` — verifies `os.path.realpath` is called (symlink handling)

All tests now assert specific config dict values rather than silently passing.
