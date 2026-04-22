---
column: Backlog
---

# Adversarial test: Docker/podman failures
# Adversarial test: Docker/podman failures

Test pi_start with podman failures:

- Docker daemon not running
- Image doesn't exist
- Out of disk space
- Container name collision (already exists)
- OOM killer during startup

**Verify:** error message includes podman logs, cleanup happens, no orphaned containers.

**File:** `pi-bridge-mcp.test.ts`
