---
column: Backlog
---

# Adversarial test: state file corruption
# Adversarial test: state file corruption

Test saveState() with adversarial conditions:

- Concurrent writes (2 agents end simultaneously)
- Disk full simulation (write to full tmpfs)
- Corrupt existing state file (invalid JSON)
- Missing state file directory

**Verify:** no data loss, graceful recovery, no crash.

**File:** `pi-bridge-mcp.test.ts`
