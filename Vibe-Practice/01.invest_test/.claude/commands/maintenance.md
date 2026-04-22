---
description: "Analyze periodic Hook system health check results and perform cleanup"
---

## Setup Maintenance Inspection Result Analysis

Read `.claude/hooks/setup.maintenance.log` and perform necessary cleanup tasks.

### Analysis Protocol:

**Step 1 — Read the log:**
Read `.claude/hooks/setup.maintenance.log` using the Read tool.
If the file does not exist, inform the user: "You must first run the Maintenance Hook with `claude --maintenance`."

**Step 2 — Analyze each item:**

| Item | Action on WARN/FAIL |
|------|------------------|
| **Session archives** | Present list of archives older than 30 days → confirm deletion via AskUserQuestion |
| **Knowledge index** | Identify malformed JSON line numbers → propose removing those lines |
| **Work log** | If over 1MB, propose trimming older logs (backup first then delete) |
| **Script syntax** | Read the erroring scripts → fix them |
| **Doc-code sync** | Code constants vs documentation value mismatch — check the file and value shown in WARN message, then update the documentation or code to match |
| **verification-logs/** | Propose cleanup of verification logs older than 30 days |
| **pacs-logs/** | Propose cleanup of pACS logs older than 30 days |
| **autopilot-logs/** | Propose cleanup of Decision Logs older than 30 days |

**Step 3 — Cleanup tasks (require user approval):**

⚠️ **NEVER DELETE:**
- `knowledge-index.jsonl` — RLM Knowledge Archive (cross-session knowledge)
- `latest.md` — Latest snapshot (session restore foundation)

Deletable (confirm with user first):
- `sessions/*.md` — Session archives older than 30 days
- `work_log.jsonl` — Abnormally large work log (backup first)

**Step 4 — Final report:**
```
## Maintenance Results

### Health Summary
- Total: N items
- Healthy: N
- Issues: N

### Cleanup Tasks Performed
- [Task description] → [Result]

### System Status
- Context Preservation System: [Healthy / Attention needed]
- Knowledge Archive: [N entries, NKB]
- Session Archives: [N files, NKB]
```

### Recommended Frequency:
- **Weekly**: For typical usage frequency
- **As needed**: After modifying Hook scripts, or when session restore behaves unexpectedly
