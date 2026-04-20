---
column: Done
created: 2026-04-19
order: 7
---

# board-tui: set up venv and run tests

No `.venv` exists in `~/repos/board-tui/`. System python3 has no pytest. Tests cannot run.

Steps:
```bash
cd ~/repos/board-tui
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest tests/ -v
```

Blocked on `board-tui-fix-bad-dev-dep` (bad dep causes install failure) and `board-tui-fix-dump-roundtrip-test` (test will fail otherwise).
