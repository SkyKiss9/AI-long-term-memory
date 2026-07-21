#!/usr/bin/env python3
"""Register the continuity trigger and manifest without claiming project activation."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path


SKILL = "maintain-project-continuity"
START = f"<!-- {SKILL}:start -->"
END = f"<!-- {SKILL}:end -->"
BLOCK_PATH = Path(__file__).resolve().parent.parent / "assets" / "AGENTS.continuity.block.md"
STATES = {"registered", "bootstrapped", "handoff-pending", "cold-start-validated", "live-validated"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content.rstrip() + "\n")


def relative_file(project: Path, value: str | None) -> str | None:
    if not value:
        return None
    candidate = Path(value.replace("/", "\\"))
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"record path must stay inside the project: {value}")
    resolved = (project / candidate).resolve()
    if project.resolve() not in resolved.parents and resolved != project.resolve():
        raise ValueError(f"record path escapes the project: {value}")
    return str(candidate).replace("\\", "/")


def update_agents(project: Path) -> Path:
    path = project / "AGENTS.md"
    content = read_text(path) if path.exists() else "# Codex Start Here\n"
    block = read_text(BLOCK_PATH).strip()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if pattern.search(content):
        content = pattern.sub(lambda _match: block, content, count=1)
    else:
        content = content.rstrip() + "\n\n" + block + "\n"
    write_text(path, content)
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--project-name")
    parser.add_argument("--state", choices=sorted(STATES), default="registered")
    parser.add_argument("--overview")
    parser.add_argument("--timeline")
    parser.add_argument("--handoff")
    parser.add_argument("--source-index")
    parser.add_argument("--acceptance")
    parser.add_argument("--installed-on", default=date.today().isoformat())
    parser.add_argument("--note", default="")
    parser.add_argument("--rules-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project = args.project_root.resolve()
    if not project.is_dir():
        raise SystemExit(f"project does not exist: {project}")
    agents = project / "AGENTS.md"
    manifest_path = project / ".codex" / "project-continuity.json"
    if args.rules_only:
        if not manifest_path.is_file():
            parser.error("--rules-only requires an existing project-continuity manifest")
        if args.dry_run:
            print(json.dumps({"agents": str(agents), "manifest": str(manifest_path), "rules_only": True}, ensure_ascii=False, indent=2))
            return 0
        update_agents(project)
        print(json.dumps({"agents": str(agents), "manifest_unchanged": True}, ensure_ascii=False))
        return 0
    if not args.project_name:
        parser.error("--project-name is required unless --rules-only is used")
    records = {
        "overview": relative_file(project, args.overview),
        "timeline": relative_file(project, args.timeline),
        "handoff": relative_file(project, args.handoff),
        "source_index": relative_file(project, args.source_index),
        "acceptance": relative_file(project, args.acceptance),
    }
    manifest = {
        "schema_version": 1,
        "skill": SKILL,
        "project": args.project_name,
        "state": args.state,
        "records": records,
        "installed_on": args.installed_on,
        "note": args.note,
    }
    if args.dry_run:
        print(json.dumps({"agents": str(agents), "manifest": str(manifest_path), "data": manifest}, ensure_ascii=False, indent=2))
        return 0
    update_agents(project)
    write_text(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2))
    print(
        json.dumps(
            {
                "project": args.project_name,
                "state": args.state,
                "activation_complete": args.state in {"cold-start-validated", "live-validated"},
                "agents": str(agents),
                "manifest": str(manifest_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
