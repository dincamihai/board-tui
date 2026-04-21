---
column: Done
order: 60
created: 2026-04-21
parent: board-tui-e2e-test-suite
updated: true
---

# E2E test: Search

Test search functionality for finding tasks.

## Test cases

- '/' opens search prompt
- Typing query filters and highlights matches
- 'n' cycles to next match
- Match notification shows count (e.g., "3 matches")
- No matches shows "no matches for 'x'"
- Escape clears search and resets highlighting
- Search matches both title and slug

## Fixture

Tasks with distinctive titles for searchable content.

## Result

Created `tests/test_e2e_search.py` with 8 E2E tests:

1. **test_slash_opens_search_prompt** — Pressing '/' opens search prompt screen
2. **test_typing_query_filters_and_highlights** — Typing search query filters and highlights matching tasks
3. **test_n_cycles_to_next_match** — Pressing 'n' cycles to next search match
4. **test_match_notification_shows_count** — Search notification displays match count
5. **test_no_matches_shows_message** — Search with no matches shows 'no matches' notification
6. **test_escape_clears_search** — Pressing escape clears search query and resets highlighting
7. **test_search_matches_title_and_slug** — Search query matches against both task title and slug
8. **test_search_across_columns** — Search finds matches in all columns (Backlog, In Progress, Done)

All 8 tests pass.
