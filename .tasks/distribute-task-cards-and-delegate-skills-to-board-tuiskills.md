---
column: Done
updated: true
---

# Distribute task-cards and delegate skills to board-tui/skills/

## Result

Created `board-tui/skills/` with both skills:

- `skills/task-cards/SKILL.md` — task card management via board-tui MCP
- `skills/delegate/SKILL.md` — delegate to qwen agent via pi_bridge MCP
- `skills/README.md` — install instructions (symlink into ~/.claude/skills/)

Other machines install via:
```bash
ln -s ~/repos/board-tui/skills/<skill> ~/.claude/skills/<skill>
```
