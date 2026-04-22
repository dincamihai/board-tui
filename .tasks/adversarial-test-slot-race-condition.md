---
column: Backlog
---

# Adversarial test: stale slot file race conditions
# Adversarial test: stale slot file race conditions

Test concurrent slot acquisition:

- Spawn 10 processes simultaneously calling acquireGlobalSlot with PARALLEL_LIMIT=2
- Verify only 2 succeed, 8 rejected
- No race condition allowing >PARALLEL_LIMIT
- Test dead PID cleanup during concurrent access

**File:** `pi-bridge-mcp.test.ts`
