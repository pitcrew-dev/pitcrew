"""Tests for install.py, run against a throwaway config directory.

    python -m unittest discover -s tests -v
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALLER = os.path.join(REPO, "install.py")
IMPORT_LINE = "@~/.claude/company/working-agreement.md"
USER_HOOK = {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo mine"}]}


def run_installer(target, *args):
    return subprocess.run([sys.executable, INSTALLER, "--target", target, *args],
                          capture_output=True, text=True, timeout=120)


class InstallerTest(unittest.TestCase):
    def setUp(self):
        self.target = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.target, ignore_errors=True)

    def path(self, *parts):
        return os.path.join(self.target, *parts)

    def write(self, name, text):
        os.makedirs(os.path.dirname(self.path(name)), exist_ok=True)
        with open(self.path(name), "w", encoding="utf-8") as handle:
            handle.write(text)

    def read(self, name):
        with open(self.path(name), encoding="utf-8") as handle:
            return handle.read()

    def settings(self):
        return json.loads(self.read("settings.json"))

    @staticmethod
    def commands(settings):
        return [h["command"] for groups in (settings.get("hooks") or {}).values() for g in groups for h in g["hooks"]]

    def install(self, *args):
        result = run_installer(self.target, *args)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result

    def test_fresh_install(self):
        self.install()
        for name in ("company/working-agreement.md", "hooks/agent-company/guard_bash.py",
                     "agents/code-reviewer.md", "skills/next-story/SKILL.md", ".agent-company.json"):
            self.assertTrue(os.path.exists(self.path(name)), name)
        self.assertIn(IMPORT_LINE, self.read("CLAUDE.md"))
        settings = self.settings()
        self.assertIn("Read(**/.env)", settings["permissions"]["deny"])
        self.assertEqual(4, sum("hooks/agent-company/" in c for c in self.commands(settings)))

    def test_keeps_user_settings_and_is_idempotent(self):
        self.write("settings.json", json.dumps({
            "model": "opus",
            "hooks": {"PreToolUse": [USER_HOOK]},
            "permissions": {"allow": ["Bash(npm test)"], "deny": ["Read(./secrets/**)"]},
        }))
        self.install()
        self.install()
        settings = self.settings()
        self.assertEqual("opus", settings["model"])
        self.assertEqual(1, self.commands(settings).count("echo mine"))
        self.assertEqual(["Bash(npm test)"], settings["permissions"]["allow"])
        deny = settings["permissions"]["deny"]
        self.assertIn("Read(./secrets/**)", deny)
        self.assertEqual(len(deny), len(set(deny)))
        self.assertEqual(4, sum("hooks/agent-company/" in c for c in self.commands(settings)))

    def test_upgrades_a_legacy_install(self):
        self.write("settings.json", json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": 'python "$HOME/.claude/hooks/guard_bash.py"'}]},
        ]}}))
        self.write("CLAUDE.md", "# Working agreement\n\nLoaded in every session, in every project. Old copy.\n")
        self.write("hooks/guard_bash.py", "# old hook\n")
        self.install()
        self.assertNotIn(".claude/hooks/guard_bash.py", json.dumps(self.settings()))
        self.assertFalse(os.path.exists(self.path("hooks", "guard_bash.py")))
        claude = self.read("CLAUDE.md")
        self.assertIn(IMPORT_LINE, claude)
        self.assertNotIn("Old copy", claude)
        self.assertTrue(os.path.isdir(self.path(".backup")))

    def test_appends_to_a_personal_claude_md(self):
        self.write("CLAUDE.md", "# My rules\n\nUse tabs.\n")
        self.install()
        claude = self.read("CLAUDE.md")
        self.assertTrue(claude.startswith("# My rules\n\nUse tabs.\n"))
        self.assertIn(IMPORT_LINE, claude)

    def test_uninstall_restores_the_user_state(self):
        self.write("settings.json", json.dumps({"hooks": {"PreToolUse": [USER_HOOK]},
                                                "permissions": {"deny": ["Read(./secrets/**)"]}}))
        self.write("CLAUDE.md", "# My rules\n")
        self.install()
        self.install("--uninstall")
        settings = self.settings()
        self.assertEqual(["echo mine"], self.commands(settings))
        self.assertEqual(["Read(./secrets/**)"], settings["permissions"]["deny"])
        self.assertNotIn("ask", settings["permissions"])
        self.assertEqual("# My rules\n", self.read("CLAUDE.md"))
        for name in ("company", "agents/code-reviewer.md", "hooks/agent-company", ".agent-company.json"):
            self.assertFalse(os.path.exists(self.path(name)), name)

    def test_invalid_settings_changes_nothing(self):
        self.write("settings.json", "{ not json")
        result = run_installer(self.target)
        self.assertNotEqual(0, result.returncode)
        self.assertEqual("{ not json", self.read("settings.json"))
        self.assertFalse(os.path.exists(self.path("company")))

    def test_dry_run_writes_nothing(self):
        self.install("--dry-run")
        self.assertEqual([], os.listdir(self.target))


if __name__ == "__main__":
    unittest.main()
