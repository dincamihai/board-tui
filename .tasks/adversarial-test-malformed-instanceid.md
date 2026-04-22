---
column: Backlog
---

# Adversarial test: empty/malformed instanceId
# Adversarial test: empty/malformed instanceId

Test acquireGlobalSlot and releaseGlobalSlot with adversarial inputs:

- Empty string instanceId
- Null/undefined
- Very long string (10KB)
- Unicode/emoji: "🔥test"
- Newlines: "test\ninjection"
- Null byte: "test\0injection"

**Verify:** no crash, graceful handling, slot file created safely or rejected.

**File:** `pi-bridge-mcp.test.ts`
