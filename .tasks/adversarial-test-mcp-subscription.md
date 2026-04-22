---
column: Backlog
---

# Adversarial test: MCP subscription edge cases
# Adversarial test: MCP subscription edge cases

Test resource subscription with:

- Subscribe to same resource twice
- Unsubscribe without subscribing first
- Subscribe to invalid URI
- Notification sent to unsubscribed client

**Verify:** no duplicate notifications, no crash, idempotent subscribe/unsubscribe.

**File:** `pi-bridge-mcp.test.ts`
