---
column: Backlog
---

# Adversarial test: queue worker crash recovery
# Adversarial test: queue worker crash recovery

Test queue worker crash scenarios:

- Worker claimed task, then crashed before complete/fail
- Task stuck in "processing" forever
- New worker should requeue after timeout

**Verify:** timeout-based recovery, no orphaned tasks, idempotent claim.

**File:** `pi-bridge-mcp.test.ts`
