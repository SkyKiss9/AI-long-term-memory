#!/usr/bin/env python3
"""Check continuity file structure without claiming memory or business acceptance."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path


SKILL = "maintain-project-continuity"
START = f"<!-- {SKILL}:start -->"
END = f"<!-- {SKILL}:end -->"
BLOCK_PATH = Path(__file__).resolve().parent.parent / "assets" / "AGENTS.continuity.block.md"
STATES = {"registered", "bootstrapped", "handoff-pending", "cold-start-validated", "live-validated"}
LEGACY_STATES = {"installed"}
DAILY_RECORDS = ("timeline", "handoff")


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
        except Exception as exc:  # pragma: no cover - defensive diagnostic
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
    for key, value in records.items():
        if value is None:
            continue
        if not isinstance(key, str) or not isinstance(value, str) or not value.strip():
            errors.append(f"record {key!r} path must be a non-empty string or null")
            continue
        candidate = (project / value).resolve()
        if candidate != project and project not in candidate.parents:
            errors.append(f"record {key} escapes project")
            continue
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

    result = {
        "output_schema_version": 1,
        "scope": "structure_only",
        "structure_ok": not errors,
        "project": manifest.get("project"),
        "declared_state": state,
        "git_branch": git_branch,
        "git_dirty_count": len(git_dirty),
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
