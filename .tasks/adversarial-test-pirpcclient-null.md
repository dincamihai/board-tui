---
column: Backlog
---

# Adversarial test: PiRpcClient null dereference
# Adversarial test: PiRpcClient null dereference

Test all pi_* tools with invalid instance_id:

- No instances running
- instance_id = null/undefined
- instance_id = non-existent string
- pi_state, pi_wait, pi_result, pi_steer, pi_set_model

**Verify:** graceful error message, no TypeError/null deref crash.

**File:** `pi-bridge-mcp.test.ts`
