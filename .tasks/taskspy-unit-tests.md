---
column: Backlog
---

# tasks.py unit tests
# tasks.py unit tests

Zero test coverage for core module. Every function needs tests.

## What to test

- `slugify`: normal input, empty string, special chars, truncation at 70 chars, unicode, multiple spaces/hyphens collapsing
- `parse`: valid frontmatter+body, no frontmatter (raw markdown), empty file, values with colons (`title: A: B`), empty frontmatter (`---\n---\nbody`), missing closing `---`
- `dump`: basic roundtrip (dump then parse), empty frontmatter dict, empty body, trailing newlines normalized
- `load_tasks`: non-existent dir returns `[]`, empty dir, missing `order` defaults to 1000, non-numeric `order` (ValueError catch), missing title falls back to `p.stem`, missing `column` falls back to `columns[0]`, sorting stability
- `mine`: case-insensitive `assigned` match, `[human]` prefix, no match returns False, empty `assigned`
- `extract_comments`: body with valid comments section, no comments section, malformed lines, empty section
- `strip_comments_section`: strips section, no section returns body unchanged
- `set_frontmatter_field`: add new key, update existing key, roundtrip preserves body
- `add_comment`: first comment creates section, append preserves earlier comments, special chars
