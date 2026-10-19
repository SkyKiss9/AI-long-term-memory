# Claude Code setup

The same skill directory serves Codex, Claude Code and DeepSeek Harness. Keep one source and link to it; do not maintain a separate Claude copy.

## Install once per machine

1. Link the skill into the Claude Code personal skills directory (`~/.claude/skills/maintain-project-continuity`, or under `CLAUDE_CONFIG_DIR`). On Windows a directory junction works without administrator rights.
2. Add one user-level SessionStart hook to `~/.claude/settings.json`, merging with any existing `hooks`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact|fork",
        "hooks": [
          {
            "type": "command",
            "command": "python \"<skill-dir>/scripts/claude_session_start.py\"",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

Use forward slashes in `<skill-dir>`. The hook is user-level so registered projects need no per-project change; folders without `.codex/project-continuity.json` get no output.

## What the hook does

- Finds the nearest continuity manifest from the session's working directory and injects the project name, the method (sources keep facts, the timeline keeps origins, decisions, reasons and changes, the handoff is the bookmark), the overview and timeline locations with the duty to append dated entries, the current handoff, and this session's id as the source locator for those entries. Ordinary starts no longer depend on the model deciding to read the handoff or remembering the notebook.
- After compaction (`compact`), it re-injects the handoff and reminds that the compaction summary is not evidence; unrecorded decisions are recovered from the session transcript.
- Read-only. It never writes records, commits, or blocks a session; failures exit silently and structure problems remain the validator's job.
- Injected context is capped below Claude Code's 10,000-character limit. A truncation notice means the handoff is too long and should be trimmed, not that history should move into it.

PreCompact is deliberately unused: it cannot add context, and blocking compaction can fail the request. Closeout stays with the skill when the user asks for it; no Stop hook turns every turn into a closeout check.

## Boundaries in Claude Code

- AGENTS.md keeps `$maintain-project-continuity`; in Claude Code it means this skill. If a Claude Code build does not load AGENTS.md, add a CLAUDE.md that only imports it (`@AGENTS.md`) instead of copying rules.
- Claude Code auto memory may hold user preferences, never project state or decisions. Project facts still come from the project's own records and sources.
- Session transcripts under `~/.claude/projects/` are original sources for Claude Code conversations; cite the session id, not a summary.
