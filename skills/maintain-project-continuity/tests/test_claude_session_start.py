from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HOOK = Path(__file__).resolve().parent.parent / "scripts" / "claude_session_start.py"


class ClaudeSessionStartHookTests(unittest.TestCase):
    def run_hook(self, payload: dict | str) -> subprocess.CompletedProcess[bytes]:
        raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
        # Claude Code pipes UTF-8 regardless of the console code page.
        return subprocess.run([sys.executable, str(HOOK)], input=raw.encode("utf-8"), capture_output=True, check=False)

    def make_project(self, root: Path, handoff_text: str, skill: str = "maintain-project-continuity") -> None:
        (root / ".codex").mkdir(parents=True)
        manifest = {
            "schema_version": 1,
            "skill": skill,
            "project": "接续样例",
            "records": {"overview": "项目总览.md", "timeline": "项目时间线.md", "handoff": "当前交接.md"},
        }
        (root / ".codex" / "project-continuity.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        (root / "当前交接.md").write_text(handoff_text, encoding="utf-8")

    def context_of(self, result: subprocess.CompletedProcess[bytes]) -> str:
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout.decode("ascii"))
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "SessionStart")
        return output["hookSpecificOutput"]["additionalContext"]

    def test_unregistered_folder_gets_no_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = self.run_hook({"cwd": temp, "source": "startup"})
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")

    def test_nested_non_ascii_cwd_injects_handoff_and_session_locator(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "长期 项目"
            self.make_project(root, "# 当前交接\n\n下一步：等待用户决定。\n")
            nested = root / "子目录" / "更深"
            nested.mkdir(parents=True)
            context = self.context_of(
                self.run_hook({"cwd": str(nested), "session_id": "s-123", "transcript_path": "t.jsonl", "source": "startup"})
            )
            self.assertIn("接续样例", context)
            self.assertIn("下一步：等待用户决定。", context)
            self.assertIn("Claude Code 会话 s-123", context)
            # The notebook is part of the method: its location and write-back duty must be visible at start.
            self.assertIn("Timeline notebook: 项目时间线.md", context)
            self.assertIn("known reason", context)
            self.assertIn("never rewrite earlier entries", context)
            self.assertIn("项目总览.md", context)
            self.assertNotIn("compacted", context)

    def test_compaction_reinjects_with_evidence_reminder(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_project(root, "handoff body")
            context = self.context_of(self.run_hook({"cwd": str(root), "source": "compact"}))
            self.assertIn("handoff body", context)
            self.assertIn("not evidence", context)

    def test_long_handoff_stays_under_claude_context_cap(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_project(root, "很长的交接。" * 5000)
            context = self.context_of(self.run_hook({"cwd": str(root), "source": "startup"}))
            self.assertLess(len(context), 10000)
            self.assertIn("handoff truncated", context)

    def test_broken_or_foreign_manifest_never_blocks_the_session(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_project(root, "x", skill="another-skill")
            self.assertEqual(self.run_hook({"cwd": str(root)}).stdout, b"")
            (root / ".codex" / "project-continuity.json").write_text("{not json", encoding="utf-8")
            result = self.run_hook({"cwd": str(root)})
            self.assertEqual((result.returncode, result.stdout), (0, b""))
            result = self.run_hook("not a payload")
            self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
