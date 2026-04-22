---
column: Backlog
---

# Adversarial test: worktree merge conflicts
# Adversarial test: worktree merge conflicts

Test mergeWorktree() with:

- Worktree already deleted externally
- Git merge conflict (same file modified in base and worktree)
- Non-git workspace
- Worktree on read-only filesystem

**Verify:** worktree preserved for manual review, error message helpful, no crash.

**File:** `pi-bridge-mcp.test.ts`
