from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = SKILL_ROOT / "scripts" / "install_project.py"
VALIDATOR = SKILL_ROOT / "scripts" / "validate_project.py"
BLOCK = (SKILL_ROOT / "assets" / "AGENTS.continuity.block.md").read_text(encoding="utf-8-sig").strip()
START = "<!-- maintain-project-continuity:start -->"
END = "<!-- maintain-project-continuity:end -->"


class SkillContractTests(unittest.TestCase):
    def run_script(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_natural_start_and_closure_contract_is_explicit(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8-sig")
        self.assertIn("Storage model", skill)
        self.assertIn("belong inside that project's own repository", skill)
        self.assertIn("Activation contract", skill)
        self.assertIn("first project-related turn", skill)
        self.assertIn("merely wiring the skill is not activation", skill)
        self.assertIn("genuinely fresh task that does not name the skill", skill)
        self.assertIn("current fresh conversation is the cold-start acceptance task", skill)
        self.assertIn("handoff-pending", skill)
        self.assertIn("required second handoff", skill)
        self.assertIn("asking for a third fresh task fails", skill)
        self.assertIn("A one-sentence status reply", skill)
        self.assertIn("explicitly covers all nine items", skill)
        self.assertIn("exact authorization and prohibition boundary", skill)
        self.assertIn("this current conversation is performing the cold-start recovery now", skill)
        self.assertIn("Do not read global memory, old tasks, the internet", skill)
        self.assertIn("canonical global skill", skill)
        self.assertIn("inspect its actual tool/source trace", skill)
        self.assertIn("additional project business documents not named by the manifest", skill)
        self.assertIn("not \"preserve continuity\"", skill)
        self.assertIn("Never let the continuity mechanism replace the project's purpose", skill)
        self.assertIn("Natural-language trigger gate", skill)
        self.assertIn("does not need to name or select the skill", skill)
        self.assertIn("Match the user's intent, not a literal substring", skill)
        self.assertIn("first project-related turn in every conversation", BLOCK)
        self.assertIn("is not activation complete", BLOCK)
        self.assertIn("this fresh conversation is the cold-start test", BLOCK)
        self.assertIn("this fresh conversation is the required second handoff", BLOCK)
        self.assertIn("Do not restart the first test or ask for a third fresh task", BLOCK)
        self.assertIn("allowed process instructions, not factual sources", BLOCK)
        self.assertIn("actual tool/source trace", BLOCK)
        self.assertIn("explicitly check nine items", BLOCK)
        self.assertIn("this current conversation is performing the test now", BLOCK)
        self.assertIn("target project's domain goal and user-facing deliverables", BLOCK)
        self.assertIn("Invoke it automatically before the final response", BLOCK)
        self.assertIn("Match intent rather than a literal keyword", BLOCK)

    def test_rules_only_updates_block_and_preserves_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / "AGENTS.md").write_text("# Existing rules\n\nKeep this text.\n", encoding="utf-8")
            registered = self.run_script(
                INSTALLER,
                str(project),
                "--project-name",
                "Fixture",
                "--state",
                "registered",
                "--note",
                "preserve me",
            )
            self.assertEqual(registered.returncode, 0, registered.stderr)
            manifest_path = project / ".codex" / "project-continuity.json"
            original_manifest = manifest_path.read_bytes()

            agents_path = project / "AGENTS.md"
            agents = agents_path.read_text(encoding="utf-8-sig")
            stale = f"{START}\nold managed text\n{END}"
            agents = re.sub(re.escape(START) + r".*?" + re.escape(END), stale, agents, count=1, flags=re.DOTALL)
            agents_path.write_text(agents, encoding="utf-8", newline="\n")

            updated = self.run_script(INSTALLER, str(project), "--rules-only")
            self.assertEqual(updated.returncode, 0, updated.stderr)
            self.assertEqual(manifest_path.read_bytes(), original_manifest)
            updated_agents = agents_path.read_text(encoding="utf-8-sig")
            self.assertIn("Keep this text.", updated_agents)
            self.assertIn(BLOCK, updated_agents)
            self.assertEqual(updated_agents.count(START), 1)

            first_update = agents_path.read_bytes()
            repeated = self.run_script(INSTALLER, str(project), "--rules-only")
            self.assertEqual(repeated.returncode, 0, repeated.stderr)
            self.assertEqual(agents_path.read_bytes(), first_update)

            checked = self.run_script(VALIDATOR, str(project))
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertTrue(json.loads(checked.stdout)["ok"])

    def test_rules_only_rejects_an_unregistered_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            agents_path = project / "AGENTS.md"
            agents_path.write_text("# Existing rules\n", encoding="utf-8")
            original_agents = agents_path.read_bytes()
            result = self.run_script(INSTALLER, str(project), "--rules-only")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(agents_path.read_bytes(), original_agents)
            self.assertFalse((project / ".codex").exists())

    def test_cold_start_state_requires_complete_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            result = self.run_script(
                INSTALLER,
                str(project),
                "--project-name",
                "Fixture",
                "--state",
                "cold-start-validated",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            checked = self.run_script(VALIDATOR, str(project))
            self.assertNotEqual(checked.returncode, 0)
            errors = json.loads(checked.stdout)["errors"]
            self.assertTrue(any("source_index is required" in error for error in errors))
            self.assertTrue(any("acceptance is required" in error for error in errors))

    def test_handoff_pending_requires_acceptance_and_is_not_active(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            for name in ("overview.md", "timeline.md", "handoff.md", "sources.md", "acceptance.md"):
                (project / name).write_text(name, encoding="utf-8")
            result = self.run_script(
                INSTALLER,
                str(project),
                "--project-name",
                "Fixture",
                "--state",
                "handoff-pending",
                "--overview",
                "overview.md",
                "--timeline",
                "timeline.md",
                "--handoff",
                "handoff.md",
                "--source-index",
                "sources.md",
                "--acceptance",
                "acceptance.md",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(json.loads(result.stdout)["activation_complete"])
            checked = self.run_script(VALIDATOR, str(project))
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertFalse(json.loads(checked.stdout)["activation_complete"])


if __name__ == "__main__":
    unittest.main()
