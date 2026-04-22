---
column: Backlog
---

# Adversarial test: log tail buffer overflow
# Adversarial test: log tail buffer overflow

Test LOG_BUFFER (200 lines) with:

- Agent produces 10,000 log lines
- Verify ring buffer: oldest dropped, newest kept
- Memory doesn't grow unbounded
- Cleanup kills tail process, no orphan

**Verify:** buffer stays at 200 lines, no memory leak.

**File:** `pi-bridge-mcp.test.ts`
