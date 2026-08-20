from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_ROOT.parents[2] if SKILL_ROOT.parents[1].name == "dsh-plugin" else SKILL_ROOT.parents[1]
PACKAGE_ROOT = SKILL_ROOT.parents[1] if SKILL_ROOT.parents[1].name == "dsh-plugin" else REPO_ROOT / "dsh-plugin"
CANONICAL_SKILL_ROOT = REPO_ROOT / "skills" / "maintain-project-continuity"
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

    def make_ready_records(self, project: Path, basis: str = "T-20260820-001") -> None:
        (project / "timeline.md").write_text(
            "# Project Timeline\n\n"
            "T-20260820-001 | 2026-08-20 | Initial usable continuity point. | Source: conversation:session-001\n",
            encoding="utf-8",
        )
        (project / "handoff.md").write_text(
            "# Project Handoff\n\n"
            "Updated: 2026-08-20\n"
            "Revision: 1\n\n"
            "Current:\nReady to continue.\n\n"
            "Boundary:\nStay inside this project.\n\n"
            "Next authorized work:\nContinue the requested task.\n\n"
            f"Basis:\n- {basis}\n",
            encoding="utf-8",
        )

    def test_ordinary_start_has_traceable_basis_bounded_reconstruction_and_concurrency_rule(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8-sig")
        handoff = (SKILL_ROOT / "assets" / "PROJECT_HANDOFF.template.md").read_text(encoding="utf-8-sig")
        timeline = (SKILL_ROOT / "assets" / "PROJECT_TIMELINE.template.md").read_text(encoding="utf-8-sig")
        self.assertIn("Basis", skill)
        self.assertIn("bounded batches", skill)
        self.assertIn("Only the coordinating/main agent writes", skill)
        self.assertIn("Revision:", handoff)
        self.assertIn("Basis:", handoff)
        self.assertRegex(timeline, r"T-YYYYMMDD-001")
        self.assertIn("Source:", timeline)
        self.assertIn("Basis", BLOCK)

    def test_cross_platform_path_validation_rejects_escape_and_normalizes_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            bad_values = ["../outside.md", "/tmp/outside.md", r"C:\outside.md", r"..\outside.md", "//server/share.md"]
            for value in bad_values:
                result = self.run_script(
                    INSTALLER,
                    str(project),
                    "--project-name",
                    "Fixture",
                    "--handoff",
                    value,
                )
                self.assertNotEqual(result.returncode, 0, value)
                self.assertFalse((project / ".codex" / "project-continuity.json").exists(), value)

        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            result = self.run_script(
                INSTALLER,
                str(project),
                "--project-name",
                "Fixture",
                "--handoff",
                r"records\handoff.md",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((project / ".codex" / "project-continuity.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["records"]["handoff"], "records/handoff.md")

    def test_non_registered_state_requires_timeline_and_handoff_at_registration(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            result = self.run_script(
                INSTALLER,
                str(project),
                "--project-name",
                "Fixture",
                "--state",
                "bootstrapped",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires both --timeline and --handoff", result.stderr)

    def test_registered_is_structurally_valid_but_explicitly_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            install = self.run_script(INSTALLER, str(project), "--project-name", "Fixture")
            self.assertEqual(install.returncode, 0, install.stderr)
            checked = self.run_script(VALIDATOR, str(project))
            data = json.loads(checked.stdout)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertTrue(data["structure_ok"])
            self.assertFalse(data["continuation_ready"])
            self.assertTrue(any("registered only" in warning for warning in data["warnings"]))

    def test_valid_ready_records_pass_and_basis_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.make_ready_records(project)
            install = self.run_script(
                INSTALLER,
                str(project),
                "--project-name",
                "Fixture",
                "--state",
                "bootstrapped",
                "--timeline",
                "timeline.md",
                "--handoff",
                "handoff.md",
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            checked = self.run_script(VALIDATOR, str(project))
            data = json.loads(checked.stdout)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertTrue(data["structure_ok"])
            self.assertTrue(data["continuation_ready"])
            self.assertEqual(data["output_schema_version"], 1)

    def test_missing_handoff_basis_or_missing_timeline_target_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.make_ready_records(project, basis="T-20260820-999")
            install = self.run_script(
                INSTALLER,
                str(project),
                "--project-name",
                "Fixture",
                "--state",
                "live-validated",
                "--timeline",
                "timeline.md",
                "--handoff",
                "handoff.md",
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            checked = self.run_script(VALIDATOR, str(project))
            data = json.loads(checked.stdout)
            self.assertNotEqual(checked.returncode, 0)
            self.assertTrue(any("missing timeline events" in error for error in data["errors"]))

    def test_timeline_event_requires_source_and_unique_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.make_ready_records(project)
            (project / "timeline.md").write_text(
                "# Project Timeline\n\n"
                "T-20260820-001 | 2026-08-20 | First.\n"
                "T-20260820-001 | 2026-08-20 | Duplicate. | Source: commit:abc\n",
                encoding="utf-8",
            )
            install = self.run_script(
                INSTALLER,
                str(project),
                "--project-name",
                "Fixture",
                "--state",
                "bootstrapped",
                "--timeline",
                "timeline.md",
                "--handoff",
                "handoff.md",
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            checked = self.run_script(VALIDATOR, str(project))
            data = json.loads(checked.stdout)
            self.assertNotEqual(checked.returncode, 0)
            self.assertTrue(any("must be unique" in error for error in data["errors"]))
            self.assertTrue(any("missing Source" in error for error in data["errors"]))

    def test_rules_only_update_is_idempotent_and_preserves_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / "AGENTS.md").write_text("# Existing\n\nKeep me.\n", encoding="utf-8")
            first = self.run_script(INSTALLER, str(project), "--project-name", "Fixture", "--note", "keep")
            self.assertEqual(first.returncode, 0, first.stderr)
            manifest = (project / ".codex" / "project-continuity.json").read_bytes()
            agents = (project / "AGENTS.md").read_bytes()
            second = self.run_script(INSTALLER, str(project), "--rules-only")
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual((project / ".codex" / "project-continuity.json").read_bytes(), manifest)
            self.assertEqual((project / "AGENTS.md").read_bytes(), agents)
            self.assertIn("Keep me.", (project / "AGENTS.md").read_text(encoding="utf-8"))

    def test_duplicate_managed_blocks_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            first = self.run_script(INSTALLER, str(project), "--project-name", "Fixture")
            self.assertEqual(first.returncode, 0, first.stderr)
            agents_path = project / "AGENTS.md"
            agents_path.write_text(agents_path.read_text(encoding="utf-8") + "\n" + BLOCK + "\n", encoding="utf-8")
            checked = self.run_script(VALIDATOR, str(project))
            data = json.loads(checked.stdout)
            self.assertNotEqual(checked.returncode, 0)
            self.assertTrue(any("exactly one complete continuity block" in error for error in data["errors"]))

    def test_openai_yaml_short_description_is_within_current_constraint(self) -> None:
        text = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        match = next(line for line in text.splitlines() if "short_description:" in line)
        value = match.split(":", 1)[1].strip().strip('"')
        self.assertGreaterEqual(len(value), 25)
        self.assertLessEqual(len(value), 64)
        default_prompt = next(line for line in text.splitlines() if "default_prompt:" in line)
        self.assertIn("$maintain-project-continuity", default_prompt)

    def test_dsh_packaged_skill_matches_canonical_skill(self) -> None:
        packaged = PACKAGE_ROOT / "skills" / "maintain-project-continuity"
        for source in CANONICAL_SKILL_ROOT.rglob("*"):
            if not source.is_file() or "__pycache__" in source.parts:
                continue
            rel = source.relative_to(CANONICAL_SKILL_ROOT)
            target = packaged / rel
            self.assertTrue(target.is_file(), rel)
            self.assertEqual(source.read_bytes(), target.read_bytes(), rel)

    @unittest.skipUnless(shutil.which("node"), "node is required for dsh installer test")
    def test_dsh_installer_replaces_whole_directory_and_removes_stale_files(self) -> None:
        installer = PACKAGE_ROOT / "scripts" / "install.mjs"
        with tempfile.TemporaryDirectory() as temp:
            dsh_home = Path(temp) / "dsh-home"
            target = dsh_home / "skills" / "maintain-project-continuity"
            target.mkdir(parents=True)
            (target / "stale-from-old-version.txt").write_text("old", encoding="utf-8")
            env = os.environ.copy()
            env["DSH_HOME"] = str(dsh_home)
            result = subprocess.run(
                ["node", str(installer)],
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((target / "SKILL.md").is_file())
            self.assertFalse((target / "stale-from-old-version.txt").exists())
            leftovers = list((dsh_home / "skills").glob(".maintain-project-continuity.*"))
            self.assertEqual(leftovers, [])


    def test_normal_rerun_cannot_overwrite_existing_manifest(self) -> None:
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

    def test_stale_or_reversed_managed_blocks_are_detected_and_repairable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            registered = self.run_script(INSTALLER, str(project), "--project-name", "Fixture")
            self.assertEqual(registered.returncode, 0, registered.stderr)
            agents_path = project / "AGENTS.md"
            reversed_text = f"# Rules\n\n{END}\nold text\n{START}\n"
            agents_path.write_text(reversed_text, encoding="utf-8")
            checked = self.run_script(VALIDATOR, str(project))
            data = json.loads(checked.stdout)
            self.assertNotEqual(checked.returncode, 0)
            self.assertTrue(any("reversed or malformed" in error for error in data["errors"]))

            stale_text = f"# Rules\n\n{START}\nold managed rules\n{END}\n"
            agents_path.write_text(stale_text, encoding="utf-8")
            stale = self.run_script(VALIDATOR, str(project))
            stale_data = json.loads(stale.stdout)
            self.assertNotEqual(stale.returncode, 0)
            self.assertTrue(any("out of date" in error for error in stale_data["errors"]))
            repaired = self.run_script(INSTALLER, str(project), "--rules-only")
            self.assertEqual(repaired.returncode, 0, repaired.stderr)
            final = self.run_script(VALIDATOR, str(project))
            self.assertEqual(final.returncode, 0, final.stdout + final.stderr)

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

    def test_registration_rollback_preserves_preexisting_empty_codex_directory(self) -> None:
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

    def test_ready_state_never_claims_memory_or_business_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.make_ready_records(project)
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
            checked = self.run_script(VALIDATOR, str(project))
            data = json.loads(checked.stdout)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertTrue(data["structure_ok"])
            self.assertTrue(data["continuation_ready"])
            self.assertEqual(
                data["not_checked"],
                ["source_fidelity", "memory_accuracy", "business_completion", "user_path"],
            )
            self.assertNotIn("activation_complete", data)

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
                "handoff-pending",
                "--timeline",
                "empty.md",
                "--handoff",
                "empty.md",
            )
            self.assertEqual(registered.returncode, 0, registered.stderr)
            checked = self.run_script(VALIDATOR, str(project))
            data = json.loads(checked.stdout)
            self.assertNotEqual(checked.returncode, 0)
            self.assertFalse(data["structure_ok"])
            self.assertFalse(data["continuation_ready"])
            self.assertTrue(any("is empty" in error for error in data["errors"]))
            self.assertTrue(any("share the same file" in warning for warning in data["warnings"]))

    def test_malformed_manifest_and_unreadable_agents_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            registered = self.run_script(INSTALLER, str(project), "--project-name", "Fixture")
            self.assertEqual(registered.returncode, 0, registered.stderr)
            manifest_path = project / ".codex" / "project-continuity.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["records"] = []
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            malformed = self.run_script(VALIDATOR, str(project))
            data = json.loads(malformed.stdout)
            self.assertNotEqual(malformed.returncode, 0)
            self.assertTrue(any("records must be an object" in error for error in data["errors"]))

            (project / "AGENTS.md").write_bytes(b"")
            empty = self.run_script(VALIDATOR, str(project))
            empty_data = json.loads(empty.stdout)
            self.assertNotEqual(empty.returncode, 0)
            self.assertTrue(any("AGENTS.md is empty" in error for error in empty_data["errors"]))

            (project / "AGENTS.md").write_bytes(b"\xff\xfe\x00")
            unreadable = self.run_script(VALIDATOR, str(project))
            unreadable_data = json.loads(unreadable.stdout)
            self.assertNotEqual(unreadable.returncode, 0)
            self.assertTrue(any("AGENTS.md is unreadable" in error for error in unreadable_data["errors"]))

    @unittest.skipIf(os.name == "nt", "symlink creation may require elevated privileges on Windows")
    def test_symlink_escape_is_rejected_at_install_time(self) -> None:
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            project = Path(temp)
            (project / "records").symlink_to(Path(outside), target_is_directory=True)
            result = self.run_script(
                INSTALLER,
                str(project),
                "--project-name",
                "Fixture",
                "--handoff",
                "records/handoff.md",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("escapes the project", result.stderr)


    def test_timeline_can_reference_older_event_without_creating_false_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / "timeline.md").write_text(
                "# Project Timeline\n\n"
                "T-20260819-001 | 2026-08-19 | Chose route A. | Source: conversation:session-a\n"
                "T-20260820-001 | 2026-08-20 | Replaced T-20260819-001 with route B. | Source: conversation:session-b\n",
                encoding="utf-8",
            )
            (project / "handoff.md").write_text(
                "# Project Handoff\n\nUpdated: 2026-08-20\nRevision: 2\n\n"
                "Current:\nRoute B is current.\n\nBoundary:\nDo not restore route A.\n\n"
                "Next authorized work:\nContinue route B.\n\nBasis:\n- T-20260820-001\n",
                encoding="utf-8",
            )
            install = self.run_script(
                INSTALLER, str(project), "--project-name", "Fixture", "--state", "bootstrapped",
                "--timeline", "timeline.md", "--handoff", "handoff.md"
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            checked = self.run_script(VALIDATOR, str(project))
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_duplicate_handoff_sections_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.make_ready_records(project)
            with (project / "handoff.md").open("a", encoding="utf-8") as handle:
                handle.write("\nBasis:\n- T-20260820-001\n")
            install = self.run_script(
                INSTALLER, str(project), "--project-name", "Fixture", "--state", "bootstrapped",
                "--timeline", "timeline.md", "--handoff", "handoff.md"
            )
            self.assertEqual(install.returncode, 0, install.stderr)
            checked = self.run_script(VALIDATOR, str(project))
            data = json.loads(checked.stdout)
            self.assertNotEqual(checked.returncode, 0)
            self.assertTrue(any("appears more than once" in error for error in data["errors"]))


if __name__ == "__main__":
    unittest.main()
