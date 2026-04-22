---
column: Backlog
---

# Adversarial test: JSONL reader edge cases
# Adversarial test: JSONL reader edge cases

Test `attachJsonlReader` with adversarial inputs:

- Empty stream
- Stream with no newlines (single massive line)
- CRLF line endings
- Unicode edge cases (U+2028, U+2029)
- Stream ends without final newline
- Cleanup called twice
- Cleanup after stream already ended

**Verify:** no memory leak, no crash, all data processed.

**File:** `pi-bridge-mcp.test.ts`
