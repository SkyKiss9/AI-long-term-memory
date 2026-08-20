#!/usr/bin/env python3
"""Check continuity structure without claiming source fidelity or business acceptance."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath


SKILL = "maintain-project-continuity"
START = f"<!-- {SKILL}:start -->"
END = f"<!-- {SKILL}:end -->"
BLOCK_PATH = Path(__file__).resolve().parent.parent / "assets" / "AGENTS.continuity.block.md"
STATES = {"registered", "bootstrapped", "handoff-pending", "cold-start-validated", "live-validated"}
LEGACY_STATES = {"installed"}
DAILY_RECORDS = ("timeline", "handoff")
READY_STATES = {"bootstrapped", "cold-start-validated", "live-validated"}
WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")
EVENT_ID = re.compile(r"\bT-\d{8}-\d{3,}\b")
TIMELINE_EVENT_START = re.compile(r"^\s*(?:[-*]\s*)?`?(T-\d{8}-\d{3,})\b")
HANDOFF_SECTIONS = ("Current:", "Boundary:", "Next authorized work:", "Basis:")


def resolve_record_path(project: Path, value: str) -> tuple[Path, str]:
    raw = value.strip()
    portable = raw.replace("\\", "/")
    if not portable or portable.startswith("/") or portable.startswith("//") or WINDOWS_DRIVE.match(portable):
        raise ValueError("path must stay inside project")
    logical = PurePosixPath(portable)
    if logical.is_absolute() or any(part == ".." for part in logical.parts):
        raise ValueError("path must stay inside project")
    parts = [part for part in logical.parts if part not in ("", ".")]
    if not parts:
        raise ValueError("path must name a file inside project")
    resolved_project = project.resolve()
    candidate = resolved_project.joinpath(*parts).resolve()
    try:
        candidate.relative_to(resolved_project)
    except ValueError as exc:
        raise ValueError("path escapes project") from exc
    return candidate, PurePosixPath(*parts).as_posix()


def section_body(text: str, heading: str) -> str | None:
    lines = text.splitlines()
    indices = {line.strip(): i for i, line in enumerate(lines) if line.strip() in HANDOFF_SECTIONS}
    if heading not in indices:
        return None
    start = indices[heading] + 1
    later = [index for name, index in indices.items() if index >= start and name != heading]
    end = min(later) if later else len(lines)
    return "\n".join(lines[start:end]).strip()


def validate_handoff(content: str, strict: bool, errors: list[str], warnings: list[str]) -> set[str]:
    refs: set[str] = set()
    updated = re.search(r"(?m)^Updated:\s*(\S.*?)\s*$", content)
    revision_matches = re.findall(r"(?m)^Revision:\s*(\d+)\s*$", content)
    revision = revision_matches[0] if len(revision_matches) == 1 else None
    if len(revision_matches) > 1:
        errors.append("handoff must contain exactly one Revision field")
    lines = [line.strip() for line in content.splitlines()]
    for heading in HANDOFF_SECTIONS:
        if lines.count(heading) > 1:
            errors.append(f"handoff section {heading} appears more than once")
    if strict and updated is None:
        errors.append("handoff must contain a non-empty Updated field")
    if strict and revision is None and len(revision_matches) <= 1:
        errors.append("handoff must contain a positive integer Revision field")
    elif revision is not None and int(revision) < 1:
        errors.append("handoff Revision must be at least 1")

    for heading in HANDOFF_SECTIONS:
        body = section_body(content, heading)
        if body is None:
            if strict:
                errors.append(f"handoff missing required section {heading}")
            else:
                warnings.append(f"handoff missing section {heading}")
            continue
        if strict and not body:
            errors.append(f"handoff section {heading} is empty")
        if heading == "Basis:":
            refs = set(EVENT_ID.findall(body))
            if strict and not refs:
                errors.append("handoff Basis must reference at least one timeline event ID")
    return refs


def validate_timeline(content: str, strict: bool, errors: list[str], warnings: list[str]) -> set[str]:
    event_lines: list[tuple[str, str]] = []
    for raw_line in content.splitlines():
        match = TIMELINE_EVENT_START.match(raw_line)
        if match:
            event_lines.append((match.group(1), raw_line.strip()))

    ids = [event_id for event_id, _ in event_lines]
    unique = set(ids)
    duplicates = sorted({event_id for event_id in ids if ids.count(event_id) > 1})
    if duplicates:
        errors.append(f"timeline event IDs must be unique: {', '.join(duplicates)}")
    if strict and not ids:
        errors.append("timeline must contain at least one event ID such as T-YYYYMMDD-001")

    for event_id, line in event_lines:
        if "Source:" not in line:
            if strict:
                errors.append(f"timeline event {event_id} is missing Source:")
            else:
                warnings.append(f"timeline event {event_id} is missing Source:")
            continue
        source = line.split("Source:", 1)[1].strip().strip("`")
        if not source:
            errors.append(f"timeline event {event_id} has an empty source locator")
    return unique


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--expect-clean", action="store_true")
    args = parser.parse_args()

    project = args.project_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    manifest_path = project / ".codex" / "project-continuity.json"
    agents_path = project / "AGENTS.md"

    if not manifest_path.is_file():
        errors.append("missing .codex/project-continuity.json")
        manifest = {}
    else:
        try:
            loaded_manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except Exception as exc:
            errors.append(f"invalid manifest: {exc}")
            manifest = {}
        else:
            if not isinstance(loaded_manifest, dict):
                errors.append("manifest root must be an object")
                manifest = {}
            else:
                manifest = loaded_manifest

    if manifest.get("schema_version") != 1:
        errors.append("manifest schema_version must be 1")
    if manifest.get("skill") != SKILL:
        errors.append("manifest skill does not match")
    if not isinstance(manifest.get("project"), str) or not manifest.get("project", "").strip():
        errors.append("manifest project must be a non-empty string")

    state = manifest.get("state")
    if state in LEGACY_STATES:
        warnings.append("manifest state installed is a legacy declaration")
    elif state not in STATES:
        errors.append(f"manifest state must be one of {sorted(STATES)}")

    if not agents_path.is_file():
        errors.append("missing AGENTS.md")
    else:
        try:
            agents = agents_path.read_text(encoding="utf-8-sig")
        except Exception as exc:
            errors.append(f"AGENTS.md is unreadable: {exc}")
            agents = ""
        if not agents:
            errors.append("AGENTS.md is empty")
        else:
            if f"${SKILL}" not in agents:
                errors.append("AGENTS.md does not invoke the skill")
            start_count = agents.count(START)
            end_count = agents.count(END)
            if start_count != 1 or end_count != 1:
                errors.append("AGENTS.md must contain exactly one complete continuity block")
            else:
                start_index = agents.index(START)
                end_index = agents.index(END)
                pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
                match = pattern.search(agents)
                if end_index < start_index or match is None:
                    errors.append("AGENTS.md continuity markers are reversed or malformed")
                else:
                    try:
                        expected_block = BLOCK_PATH.read_text(encoding="utf-8-sig").strip()
                    except Exception as exc:
                        errors.append(f"managed continuity block is unreadable: {exc}")
                    else:
                        if match.group(0).strip() != expected_block:
                            errors.append("AGENTS.md managed continuity block is out of date")

    raw_records = manifest.get("records")
    if not isinstance(raw_records, dict):
        errors.append("manifest records must be an object")
        records: dict[str, object] = {}
    else:
        records = raw_records

    if state not in {"registered", "installed", None}:
        for key in DAILY_RECORDS:
            if not records.get(key):
                errors.append(f"{key} is required for declared state {state}")

    seen_paths: dict[Path, str] = {}
    record_contents: dict[str, str] = {}
    normalized_paths: dict[str, str] = {}
    for key, value in records.items():
        if value is None:
            continue
        if not isinstance(key, str) or not isinstance(value, str) or not value.strip():
            errors.append(f"record {key!r} path must be a non-empty string or null")
            continue
        try:
            candidate, portable = resolve_record_path(project, value)
        except ValueError as exc:
            errors.append(f"record {key} {exc}")
            continue
        normalized_paths[key] = portable
        previous = seen_paths.get(candidate)
        if previous is not None:
            warnings.append(f"records {previous} and {key} share the same file; readers must deduplicate it")
        else:
            seen_paths[candidate] = key
        if not candidate.is_file():
            errors.append(f"record {key} does not exist: {value}")
            continue
        try:
            content = candidate.read_text(encoding="utf-8-sig")
        except Exception as exc:
            errors.append(f"record {key} is unreadable: {exc}")
            continue
        if not content.strip():
            errors.append(f"record {key} is empty: {value}")
            continue
        record_contents[key] = content

    strict = state in READY_STATES
    timeline_ids: set[str] = set()
    handoff_refs: set[str] = set()
    if "timeline" in record_contents:
        timeline_ids = validate_timeline(record_contents["timeline"], strict, errors, warnings)
    if "handoff" in record_contents:
        handoff_refs = validate_handoff(record_contents["handoff"], strict, errors, warnings)
    if handoff_refs and timeline_ids:
        missing_refs = sorted(handoff_refs - timeline_ids)
        if missing_refs:
            errors.append(f"handoff Basis references missing timeline events: {', '.join(missing_refs)}")

    if state == "registered":
        warnings.append("project is registered only; ordinary continuation is not ready until usable timeline and handoff records are registered")
    elif state == "handoff-pending":
        warnings.append("handoff is pending; ordinary continuation is not yet declared ready")

    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    global_skill = codex_home / "skills" / SKILL / "SKILL.md"
    if not global_skill.is_file():
        warnings.append(f"global skill not found at {global_skill}")

    git_branch = None
    git_dirty: list[str] = []
    try:
        branch = subprocess.run(
            ["git", "-C", str(project), "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=False,
        )
        if branch.returncode == 0:
            git_branch = branch.stdout.strip()
            status = subprocess.run(
                ["git", "-C", str(project), "status", "--short"],
                capture_output=True,
                text=True,
                check=False,
            )
            if status.returncode != 0:
                message = "Git worktree status could not be checked"
                if args.expect_clean:
                    errors.append(message)
                else:
                    warnings.append(message)
            else:
                git_dirty = [line for line in status.stdout.splitlines() if line]
                if args.expect_clean and git_dirty:
                    errors.append("project worktree is not clean")
        else:
            message = "project is not a Git checkout"
            if args.expect_clean:
                errors.append(message)
            else:
                warnings.append(message)
    except FileNotFoundError:
        if args.expect_clean:
            errors.append("Git is unavailable; cleanliness cannot be checked")
        else:
            warnings.append("Git is unavailable")

    continuation_ready = state in READY_STATES and not errors
    result = {
        "output_schema_version": 1,
        "scope": "structure_only",
        "structure_ok": not errors,
        "continuation_ready": continuation_ready,
        "project": manifest.get("project"),
        "declared_state": state,
        "git_branch": git_branch,
        "git_dirty_count": len(git_dirty),
        "normalized_record_paths": normalized_paths,
        "not_checked": [
            "source_fidelity",
            "memory_accuracy",
            "business_completion",
            "user_path",
        ],
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
