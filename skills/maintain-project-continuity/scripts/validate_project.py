#!/usr/bin/env python3
"""Validate installation structure and report, without changing a project."""

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
REQUIRED_AFTER_BOOTSTRAP = ("overview", "timeline", "handoff", "source_index")
REQUIRED_AFTER_COLD_START = ("acceptance",)


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
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except Exception as exc:  # pragma: no cover - defensive diagnostic
            errors.append(f"invalid manifest: {exc}")
            manifest = {}
    if manifest.get("schema_version") != 1:
        errors.append("manifest schema_version must be 1")
    if manifest.get("skill") != SKILL:
        errors.append("manifest skill does not match")
    state = manifest.get("state")
    if state in LEGACY_STATES:
        warnings.append("manifest state installed is legacy wiring-only; migrate it to registered or complete activation")
    elif state not in STATES:
        errors.append(f"manifest state must be one of {sorted(STATES)}")
    if not agents_path.is_file():
        errors.append("missing AGENTS.md")
        agents = ""
    else:
        agents = agents_path.read_text(encoding="utf-8-sig")
    if f"${SKILL}" not in agents:
        errors.append("AGENTS.md does not invoke the skill")
    if START not in agents or END not in agents:
        errors.append("AGENTS.md managed markers are incomplete")
    else:
        expected_block = BLOCK_PATH.read_text(encoding="utf-8-sig").strip()
        match = re.search(re.escape(START) + r".*?" + re.escape(END), agents, re.DOTALL)
        if match and match.group(0).strip() != expected_block:
            errors.append("AGENTS.md managed continuity block is out of date")
    records = manifest.get("records") if isinstance(manifest.get("records"), dict) else {}
    if state in {"bootstrapped", "handoff-pending", "cold-start-validated", "live-validated"}:
        for key in REQUIRED_AFTER_BOOTSTRAP:
            if not records.get(key):
                errors.append(f"{key} is required for state {state}")
    if state in {"handoff-pending", "cold-start-validated", "live-validated"}:
        for key in REQUIRED_AFTER_COLD_START:
            if not records.get(key):
                errors.append(f"{key} is required for state {state}")
    for key, value in records.items():
        if value is None:
            continue
        candidate = (project / str(value)).resolve()
        if project not in candidate.parents:
            errors.append(f"record {key} escapes project")
        elif not candidate.is_file():
            errors.append(f"record {key} does not exist: {value}")
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    global_skill = codex_home / "skills" / SKILL / "SKILL.md"
    if not global_skill.is_file():
        warnings.append(f"global skill not found at {global_skill}")
    git_branch = None
    git_dirty: list[str] = []
    try:
        branch = subprocess.run(["git", "-C", str(project), "branch", "--show-current"], capture_output=True, text=True, check=False)
        if branch.returncode == 0:
            git_branch = branch.stdout.strip()
            status = subprocess.run(["git", "-C", str(project), "status", "--short"], capture_output=True, text=True, check=False)
            git_dirty = [line for line in status.stdout.splitlines() if line]
            if args.expect_clean and git_dirty:
                errors.append("project worktree is not clean")
        else:
            warnings.append("project is not a Git checkout")
    except FileNotFoundError:
        warnings.append("Git is unavailable")
    result = {
        "ok": not errors,
        "project": manifest.get("project"),
        "state": state,
        "activation_complete": state in {"cold-start-validated", "live-validated"},
        "git_branch": git_branch,
        "git_dirty_count": len(git_dirty),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
