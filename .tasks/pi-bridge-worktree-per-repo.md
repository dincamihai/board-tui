---
column: Done
updated: true
---

# pi_bridge: organize worktrees by repo name

## Problem

Current worktree path: `/tmp/pi-worktrees/pi/<slug>-<ts>`

No repo isolation. Multiple repos → worktrees mixed together. Hard to debug, cleanup.

## Solution

New path: `/tmp/pi-worktrees/<repo-name>/<slug>-<ts>`

## Repo name detection (priority order)

1. **Git remote origin** — parse from `git config --get remote.origin.url`
   - `github:mihai/local-agent.git` → `local-agent`
   - `https://github.com/mihai/local-agent.git` → `local-agent`
2. **Fallback: basename** — `basename(workspace)`
   - `/home/mihai/repos/local-agent` → `local-agent`

## Sanitization

```ts
function sanitizeRepoName(name: string): string {
  return name.replace(/[^a-zA-Z0-9_-]/g, "_");
}
```

## Changes

### pi-bridge-mcp.ts

Add helper function:
```ts
function getRepoName(workspace: string): string {
  try {
    const remote = execSync(`git -C ${workspace} config --get remote.origin.url`, { encoding: "utf-8" }).trim();
    // Handle SSH: git@github.com:mihai/local-agent.git
    const sshMatch = remote.match(/\/([^/]+?)(?:\.git)?$/);
    // Handle HTTPS: https://github.com/mihai/local-agent.git
    const httpsMatch = remote.match(/\/([^/]+?)(?:\.git)?$/);
    if (sshMatch?.[1]) return sanitizeRepoName(sshMatch[1]);
    if (httpsMatch?.[1]) return sanitizeRepoName(httpsMatch[1]);
  } catch {
    // Not a git repo or no remote
  }
  return sanitizeRepoName(basename(workspace));
}
```

Update worktree creation:
```ts
const repoName = getRepoName(workDir);
const branch = `pi/${name}-${Date.now()}`;
wtPath = `/tmp/pi-worktrees/${repoName}/${branch.replace(/\//g, "-")}`;
```

## Benefits

- `/tmp/pi-worktrees/local-agent/pi/test-123/`
- `/tmp/pi-worktrees/my-other-repo/pi/test-456/`
- Easy cleanup: `rm -rf /tmp/pi-worktrees/local-agent/`
- Clear which repo a worktree belongs to

## Acceptance

- Worktree path includes repo name
- Git remote parsed correctly (SSH and HTTPS URLs)
- Falls back to basename when no remote
- Existing tests updated
- Backwards compat: old flat paths still cleaned up
