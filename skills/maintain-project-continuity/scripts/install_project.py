#!/usr/bin/env python3
"""Register continuity files safely without claiming memory or business acceptance."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path


SKILL = "maintain-project-continuity"
START = f"<!-- {SKILL}:start -->"
END = f"<!-- {SKILL}:end -->"
BLOCK_PATH = Path(__file__).resolve().parent.parent / "assets" / "AGENTS.continuity.block.md"
STATES = {"registered", "bootstrapped", "handoff-pending", "cold-start-validated", "live-validated"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(content)
            temporary = Path(handle.name)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def write_text(path: Path, content: str) -> None:
    write_bytes(path, (content.rstrip() + "\n").encode("utf-8"))


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


def render_agents(project: Path) -> tuple[Path, str]:
    path = project / "AGENTS.md"
    content = read_text(path) if path.exists() else "# Codex Start Here\n"
    block = read_text(BLOCK_PATH).strip()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    start_count = content.count(START)
    end_count = content.count(END)
    if start_count != end_count or start_count > 1:
        raise ValueError("AGENTS.md has duplicate or incomplete continuity markers; no files were changed")
    if start_count == 1:
        start_index = content.index(START)
        end_index = content.index(END)
        if end_index < start_index or pattern.search(content) is None:
            raise ValueError("AGENTS.md continuity markers are reversed or malformed; no files were changed")
        content = pattern.sub(lambda _match: block, content, count=1)
    else:
        content = content.rstrip() + "\n\n" + block + "\n"
    return path, content


def remove_empty_parent(path: Path, stop: Path) -> None:
    parent = path.parent
    if parent != stop and parent.exists():
        try:
            parent.rmdir()
        except OSError:
            pass


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

    agents_path = project / "AGENTS.md"
    manifest_path = project / ".codex" / "project-continuity.json"

    if args.rules_only:
        if not manifest_path.is_file():
            parser.error("--rules-only requires an existing project-continuity manifest")
        try:
            rendered_agents_path, rendered_agents = render_agents(project)
        except (ValueError, UnicodeError) as exc:
            parser.error(str(exc))
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "output_schema_version": 1,
                        "agents": str(rendered_agents_path),
                        "manifest": str(manifest_path),
                        "rules_only": True,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
        write_text(rendered_agents_path, rendered_agents)
        print(
            json.dumps(
                {
                    "output_schema_version": 1,
                    "agents": str(rendered_agents_path),
                    "manifest_unchanged": True,
                },
                ensure_ascii=False,
            )
        )
        return 0

    if manifest_path.exists():
        parser.error(
            "project-continuity manifest already exists; use --rules-only to update managed rules without overwriting records"
        )
    if not args.project_name:
        parser.error("--project-name is required unless --rules-only is used")

    try:
        rendered_agents_path, rendered_agents = render_agents(project)
        records = {
            "overview": relative_file(project, args.overview),
            "timeline": relative_file(project, args.timeline),
            "handoff": relative_file(project, args.handoff),
            "source_index": relative_file(project, args.source_index),
            "acceptance": relative_file(project, args.acceptance),
        }
    except (ValueError, UnicodeError) as exc:
        parser.error(str(exc))

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
        print(
            json.dumps(
                {
                    "output_schema_version": 1,
                    "agents": str(rendered_agents_path),
                    "manifest": str(manifest_path),
                    "data": manifest,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    original_agents = agents_path.read_bytes() if agents_path.exists() else None
    manifest_parent_existed = manifest_path.parent.exists()
    try:
        # Write the manifest first. If its directory is unavailable, AGENTS.md stays untouched.
        write_text(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2))
        write_text(rendered_agents_path, rendered_agents)
    except Exception:
        # Roll back both sides of the two-file registration.
        try:
            if original_agents is None:
                agents_path.unlink(missing_ok=True)
            else:
                write_bytes(agents_path, original_agents)
        finally:
            manifest_path.unlink(missing_ok=True)
            if not manifest_parent_existed:
                remove_empty_parent(manifest_path, project)
        raise

    print(
        json.dumps(
            {
                "output_schema_version": 1,
                "project": args.project_name,
                "declared_state": args.state,
                "scope": "registration_only",
                "agents": str(agents_path),
                "manifest": str(manifest_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
