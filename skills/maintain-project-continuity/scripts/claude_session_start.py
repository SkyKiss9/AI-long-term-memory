#!/usr/bin/env python3
"""Claude Code SessionStart hook: put the registered project's current handoff in context.

Read-only. Projects without a continuity manifest get no output. Any failure exits 0
silently so a broken record never blocks a session; the validator reports structure.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


SKILL = "maintain-project-continuity"
MANIFEST = Path(".codex") / "project-continuity.json"
# Claude Code caps injected context at 10,000 characters; stay below it.
CONTEXT_LIMIT = 9000

SOURCE_NOTES = {
    "compact": (
        "The context was just compacted. The compaction summary is navigation, not evidence: "
        "before recording decisions or closing out, check this session's transcript for material "
        "decisions, reasons, acceptance or cancellations not yet in the timeline."
    ),
    "resume": "This session was resumed; the handoff may have changed since it was last read.",
    "fork": "This session was forked; reread the handoff before writing records to avoid duplicating the parent session.",
}


def read_payload() -> dict:
    # Claude Code sends UTF-8; the console code page (e.g. GBK) would garble non-ASCII paths.
    try:
        raw = sys.stdin.buffer.read().decode("utf-8-sig")
    except (OSError, ValueError, AttributeError):
        return {}
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def find_manifest(start: Path) -> Path | None:
    for directory in (start, *start.parents):
        candidate = directory / MANIFEST
        if candidate.is_file():
            return candidate
    return None


def build_context(payload: dict) -> str | None:
    start = Path(payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
    manifest_path = find_manifest(start)
    if manifest_path is None:
        return None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if not isinstance(manifest, dict) or manifest.get("skill") != SKILL:
        return None

    project_root = manifest_path.parent.parent
    records = manifest.get("records") if isinstance(manifest.get("records"), dict) else {}
    lines = [
        f"[{SKILL}] Registered long-running project: {manifest.get('project') or project_root.name}"
        f" (root: {project_root}).",
        f"Follow the project rules in AGENTS.md; `${SKILL}` there means the `{SKILL}` skill.",
        "Method: original conversations keep the facts, the timeline notebook keeps the origin, "
        "decisions with their reasons and later changes, and the handoff below is only the current bookmark.",
    ]
    timeline = records.get("timeline")
    overview = records.get("overview")
    if isinstance(overview, str) and overview.strip():
        lines.append(f"Why the project started and its intended outcome: {overview}.")
    if isinstance(timeline, str) and timeline.strip():
        lines.append(
            f"Timeline notebook: {timeline}. Look up the entries the handoff points to when a reason is missing, "
            "facts conflict, or a decision might be reversed. While working, append a dated two-or-three-sentence "
            "entry for each substantive conversation or decision (why it arose, what was decided and the known "
            "reason, actual result, direct source); rejections, cancellations and acceptance count. Append later "
            "changes; never rewrite earlier entries. Keep user decisions separate from assistant suggestions."
        )
    else:
        lines.append("The manifest names no timeline notebook; record decisions in the project's existing equivalent.")
    lines.append(
        "Ordinary start: do not load the full timeline or source history by default, and do not recite project history to the user."
    )
    session_id = payload.get("session_id")
    if session_id:
        lines.append(
            f"Source locator for this conversation's timeline entries: Claude Code 会话 {session_id}"
            + (f" (transcript: {payload['transcript_path']})." if payload.get("transcript_path") else ".")
        )
    note = SOURCE_NOTES.get(str(payload.get("source") or ""))
    if note:
        lines.append(note)

    handoff = records.get("handoff")
    if not isinstance(handoff, str) or not handoff.strip():
        lines.append("The manifest names no current handoff; recover the position from project evidence.")
        return "\n".join(lines)
    handoff_path = (project_root / handoff).resolve()
    if project_root.resolve() not in handoff_path.parents or not handoff_path.is_file():
        lines.append(f"The registered handoff is missing or outside the project: {handoff}.")
        return "\n".join(lines)

    header = "\n".join(lines) + f"\n\n--- current handoff: {handoff} ---\n"
    body = handoff_path.read_text(encoding="utf-8-sig").strip()
    room = CONTEXT_LIMIT - len(header)
    if len(body) > room:
        marker = f"\n…[handoff truncated at {room} characters; read the full file. A handoff this long should be trimmed.]"
        body = body[: max(room - len(marker), 0)] + marker
    return header + body


def main() -> int:
    try:
        context = build_context(read_payload())
    except Exception as exc:  # never block a session over continuity records
        print(f"{SKILL} hook skipped: {exc}", file=sys.stderr)
        return 0
    if context:
        output = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}
        # ASCII-escaped JSON survives any console code page.
        sys.stdout.write(json.dumps(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
