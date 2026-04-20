---
column: Done
created: 2026-04-19
order: 5
---

# board-tui: fix dump/roundtrip test

`dump()` in `tasks.py` always appends a trailing `\n` via `body.rstrip() + "\n"`. The roundtrip test in `tests/test_tasks.py::test_parse_dump_roundtrip` uses a triple-quoted `original` string with no trailing newline, so `f.read_text() == original` will fail.

Fix options:
- (A) Make the test's `original` string end with `\n` (preferred — files should end with newline).
- (B) Change `dump()` to not force the trailing newline (worse — breaks convention).

Go with A: add `\n` at the end of the `original` string in the test.
