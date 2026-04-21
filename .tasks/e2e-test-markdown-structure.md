---
column: Done
order: 42
created: 2026-04-21
parent: board-tui-e2e-test-suite
updated: true
---

# E2E test: Markdown structure validation

Test that task files follow required markdown structure.

## Required structure

```markdown
---
column: <column-name>
order: <number>
[optional fields]
---

# Task title

Task body content.
```

## Test cases

- Frontmatter block required (--- delimiters)
- `column` field required in frontmatter
- At least one heading (# Task title) in body
- File without frontmatter still loads (fallback behavior)
- File without heading uses slug as title
- Invalid frontmatter handled gracefully

## Assertions

- Parser extracts frontmatter correctly
- Body content extracted after frontmatter
- Title extracted from first # heading

## Result

Created `tests/test_e2e_markdown_structure.py` with 12 tests (8 E2E + 4 unit):

1. **test_frontmatter_block_parsed_correctly** — Frontmatter block with --- delimiters parsed correctly
2. **test_column_field_in_frontmatter** — Column field determines task placement in correct ListView
3. **test_heading_extracted_from_body** — First # heading extracted as task title
4. **test_multiple_headings_uses_first** — When multiple headings present, first # heading used
5. **test_no_frontmatter_still_loads** — File without frontmatter delimiters still loads with defaults
6. **test_no_heading_uses_slug_as_title** — File without # heading uses filename slug as title
7. **test_invalid_frontmatter_handled_gracefully** — Invalid YAML in frontmatter handled without crashing
8. **test_empty_frontmatter_block** — Empty frontmatter block (--- ---) handled correctly
9. **test_parse_function_extract_frontmatter** — parse() extracts frontmatter fields correctly (unit)
10. **test_parse_function_no_frontmatter** — parse() handles file without frontmatter (unit)
11. **test_load_tasks_title_from_heading** — load_tasks() extracts title from first # heading (unit)
12. **test_load_tasks_title_from_slug** — load_tasks() uses slug as title when no heading (unit)

All 12 tests pass.
