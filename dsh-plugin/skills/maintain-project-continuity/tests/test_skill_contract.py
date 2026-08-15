from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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
            errors="replace",
            check=False,
        )

    def test_ordinary_start_is_lightweight_and_user_owned_work_stays_primary(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8-sig")
        handoff_template = (SKILL_ROOT / "assets" / "PROJECT_HANDOFF.template.md").read_text(encoding="utf-8-sig")
        timeline_template = (SKILL_ROOT / "assets" / "PROJECT_TIMELINE.template.md").read_text(encoding="utf-8-sig")
        self.assertIn("read only the current handoff", skill)
        self.assertIn("Do not begin an ordinary conversation with a project-history recital", skill)
        self.assertIn("never turns an ordinary start into a cold-start exam", skill)
        self.assertIn("The user does not need to request or supervise this bookkeeping", skill)
        self.assertIn("one or two lines", skill)
        self.assertIn("Replace stale handoff details", skill)
        self.assertIn("read only the current handoff", BLOCK)
        self.assertIn("do not give the user a recovery report unless asked", BLOCK)
        self.assertIn("append one short timeline note", BLOCK)
        self.assertEqual(
            [line for line in handoff_template.splitlines() if line.endswith(":")],
            ["Current:", "Boundary:", "Next authorized work:"],
        )
        self.assertIn("What materially changed", timeline_template)
        self.assertLessEqual(len(timeline_template.splitlines()), 3)
        self.assertNotIn("explicitly covers all nine items", skill)
        self.assertNotIn("current fresh conversation is the cold-start acceptance task", skill)
        self.assertNotIn("this fresh conversation is the cold-start test", BLOCK)

    def test_first_registration_and_rules_only_update_are_safe_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / "AGENTS.md").write_text("# Existing rules\n\nKeep this text.\n", encoding="utf-8")
            registered = self.run_script(
                INSTALLER,
                str(project),
                "--project-name",
                "Fixture",
                "--note",
                "preserve me",
            )
            self.assertEqual(registered.returncode, 0, registered.stderr)
            self.assertNotIn("activation_complete", registered.stdout)

            manifest_path = project / ".codex" / "project-continuity.json"
            original_manifest = manifest_path.read_bytes()
            agents_path = project / "AGENTS.md"
            first_agents = agents_path.read_bytes()

            updated = self.run_script(INSTALLER, str(project), "--rules-only")
            self.assertEqual(updated.returncode, 0, updated.stderr)
            self.assertEqual(manifest_path.read_bytes(), original_manifest)
            self.assertEqual(agents_path.read_bytes(), first_agents)
            self.assertIn("Keep this text.", agents_path.read_text(encoding="utf-8-sig"))
            self.assertEqual(agents_path.read_text(encoding="utf-8-sig").count(START), 1)

            checked = self.run_script(VALIDATOR, str(project))
            result = json.loads(checked.stdout)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertTrue(result["structure_ok"])
            self.assertEqual(result["scope"], "structure_only")
            self.assertEqual(result["output_schema_version"], 1)
            self.assertNotIn("activation_complete", result)

    def test_normal_rerun_cannot_overwrite_an_existing_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            first = self.run_script(INSTALLER, str(project), "--project-name", "Fixture", "--note", "keep")
            self.assertEqual(first.returncode, 0, first.stderr)
            agents_path = project / "AGENTS.md"
            manifest_path = project / ".codex" / "project-continuity.json"
            original_agents = agents_path.read_bytes()
            original_manifest = manifest_path.read_bytes()

            repeated = self.run_script(INSTALLER, str(project), "--project-name", "Changed")
            self.assertNotEqual(repeated.returncode, 0)
            self.assertEqual(agents_path.read_bytes(), original_agents)
            self.assertEqual(manifest_path.read_bytes(), original_manifest)

    def test_duplicate_or_incomplete_managed_blocks_are_not_silently_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            registered = self.run_script(INSTALLER, str(project), "--project-name", "Fixture")
            self.assertEqual(registered.returncode, 0, registered.stderr)
            agents_path = project / "AGENTS.md"
            agents_path.write_text(
                agents_path.read_text(encoding="utf-8-sig") + "\n" + BLOCK + "\n",
                encoding="utf-8",
            )
            duplicate_bytes = agents_path.read_bytes()

            checked = self.run_script(VALIDATOR, str(project))
            result = json.loads(checked.stdout)
            self.assertNotEqual(checked.returncode, 0)
            self.assertFalse(result["structure_ok"])
            self.assertTrue(any("exactly one complete continuity block" in error for error in result["errors"]))

            update = self.run_script(INSTALLER, str(project), "--rules-only")
            self.assertNotEqual(update.returncode, 0)
            self.assertEqual(agents_path.read_bytes(), duplicate_bytes)

    def test_reversed_markers_are_rejected_and_stale_blocks_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            registered = self.run_script(INSTALLER, str(project), "--project-name", "Fixture")
            self.assertEqual(registered.returncode, 0, registered.stderr)
            agents_path = project / "AGENTS.md"

            reversed_text = f"# Rules\n\n{END}\nold text\n{START}\n"
            agents_path.write_text(reversed_text, encoding="utf-8")
            reversed_bytes = agents_path.read_bytes()
            update = self.run_script(INSTALLER, str(project), "--rules-only")
            self.assertNotEqual(update.returncode, 0)
            self.assertEqual(agents_path.read_bytes(), reversed_bytes)
            checked = self.run_script(VALIDATOR, str(project))
            reversed_result = json.loads(checked.stdout)
            self.assertNotEqual(checked.returncode, 0)
            self.assertTrue(any("reversed or malformed" in error for error in reversed_result["errors"]))

            stale_text = f"# Rules\n\n{START}\nold managed rules\n{END}\n"
            agents_path.write_text(stale_text, encoding="utf-8")
            stale_check = self.run_script(VALIDATOR, str(project))
            stale_result = json.loads(stale_check.stdout)
            self.assertNotEqual(stale_check.returncode, 0)
            self.assertTrue(any("out of date" in error for error in stale_result["errors"]))

            repaired = self.run_script(INSTALLER, str(project), "--rules-only")
            self.assertEqual(repaired.returncode, 0, repaired.stderr)
            final_check = self.run_script(VALIDATOR, str(project))
            self.assertEqual(final_check.returncode, 0, final_check.stdout + final_check.stderr)

    def test_failed_manifest_creation_does_not_change_agents(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            agents_path = project / "AGENTS.md"
            agents_path.write_text("# Existing rules\n\nKeep exactly.\n", encoding="utf-8")
            original_agents = agents_path.read_bytes()
            (project / ".codex").write_text("this blocks directory creation", encoding="utf-8")

            result = self.run_script(INSTALLER, str(project), "--project-name", "Fixture")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(agents_path.read_bytes(), original_agents)
            self.assertTrue((project / ".codex").is_file())

    def test_registration_rollback_preserves_a_preexisting_empty_codex_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            agents_path = project / "AGENTS.md"
            agents_path.write_text("# Existing rules\n\nKeep exactly.\n", encoding="utf-8")
            original_agents = agents_path.read_bytes()
            codex_dir = project / ".codex"
            codex_dir.mkdir()

            spec = importlib.util.spec_from_file_location("installer_under_test", INSTALLER)
            assert spec is not None and spec.loader is not None
            installer = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(installer)
            real_write_text = installer.write_text
            write_count = 0

            def fail_second_write(path: Path, content: str) -> None:
                nonlocal write_count
                write_count += 1
                if write_count == 2:
                    raise OSError("simulated AGENTS write failure")
                real_write_text(path, content)

            argv = [str(INSTALLER), str(project), "--project-name", "Fixture"]
            with mock.patch.object(sys, "argv", argv), mock.patch.object(
                installer, "write_text", side_effect=fail_second_write
            ), self.assertRaises(OSError):
                installer.main()

            self.assertTrue(codex_dir.is_dir())
            self.assertEqual(list(codex_dir.iterdir()), [])
            self.assertEqual(agents_path.read_bytes(), original_agents)

    def test_declared_high_state_is_never_reported_as_memory_or_business_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            for name in ("timeline.md", "handoff.md"):
                (project / name).write_text(f"# {name}\n\nplaceholder\n", encoding="utf-8")
            registered = self.run_script(
                INSTALLER,
                str(project),
                "--project-name",
                "Fixture",
                "--state",
                "cold-start-validated",
                "--timeline",
                "timeline.md",
                "--handoff",
                "handoff.md",
            )
            self.assertEqual(registered.returncode, 0, registered.stderr)
            self.assertNotIn("activation_complete", registered.stdout)

            checked = self.run_script(VALIDATOR, str(project))
            result = json.loads(checked.stdout)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertTrue(result["structure_ok"])
            self.assertEqual(result["declared_state"], "cold-start-validated")
            self.assertEqual(result["output_schema_version"], 1)
            self.assertNotIn("activation_complete", result)
            self.assertEqual(
                result["not_checked"],
                ["source_fidelity", "memory_accuracy", "business_completion", "user_path"],
            )

    def test_shared_record_paths_warn_and_empty_records_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / "empty.md").write_text("", encoding="utf-8")
            registered = self.run_script(
                INSTALLER,
                str(project),
                "--project-name",
                "Fixture",
                "--state",
                "bootstrapped",
                "--timeline",
                "empty.md",
                "--handoff",
                "empty.md",
            )
            self.assertEqual(registered.returncode, 0, registered.stderr)

            checked = self.run_script(VALIDATOR, str(project))
            result = json.loads(checked.stdout)
            self.assertNotEqual(checked.returncode, 0)
            self.assertFalse(result["structure_ok"])
            self.assertTrue(any("is empty" in error for error in result["errors"]))
            self.assertTrue(any("share the same file" in warning for warning in result["warnings"]))

    def test_malformed_records_and_unreadable_agents_are_reported_as_structure_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            registered = self.run_script(INSTALLER, str(project), "--project-name", "Fixture")
            self.assertEqual(registered.returncode, 0, registered.stderr)
            manifest_path = project / ".codex" / "project-continuity.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["records"] = []
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            malformed = self.run_script(VALIDATOR, str(project))
            malformed_result = json.loads(malformed.stdout)
            self.assertNotEqual(malformed.returncode, 0)
            self.assertTrue(any("records must be an object" in error for error in malformed_result["errors"]))

            (project / "AGENTS.md").write_bytes(b"")
            empty = self.run_script(VALIDATOR, str(project))
            empty_result = json.loads(empty.stdout)
            self.assertNotEqual(empty.returncode, 0)
            self.assertTrue(any("AGENTS.md is empty" in error for error in empty_result["errors"]))

            (project / "AGENTS.md").write_bytes(b"\xff\xfe\x00")
            unreadable = self.run_script(VALIDATOR, str(project))
            unreadable_result = json.loads(unreadable.stdout)
            self.assertNotEqual(unreadable.returncode, 0)
            self.assertTrue(any("AGENTS.md is unreadable" in error for error in unreadable_result["errors"]))

    def test_manifest_root_and_project_name_must_be_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            registered = self.run_script(INSTALLER, str(project), "--project-name", "Fixture")
            self.assertEqual(registered.returncode, 0, registered.stderr)
            manifest_path = project / ".codex" / "project-continuity.json"

            manifest_path.write_text("[]", encoding="utf-8")
            array_result = self.run_script(VALIDATOR, str(project))
            array_data = json.loads(array_result.stdout)
            self.assertNotEqual(array_result.returncode, 0)
            self.assertTrue(any("root must be an object" in error for error in array_data["errors"]))

            manifest = {
                "schema_version": 1,
                "skill": "maintain-project-continuity",
                "project": "",
                "state": "registered",
                "records": {},
            }
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            blank_project = self.run_script(VALIDATOR, str(project))
            blank_data = json.loads(blank_project.stdout)
            self.assertNotEqual(blank_project.returncode, 0)
            self.assertTrue(any("project must be a non-empty string" in error for error in blank_data["errors"]))


if __name__ == "__main__":
    unittest.main()
