"""Tests for install.py (uninstall-only), run against a throwaway config directory.

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
USER_HOOK = {"matcher": "Bash", "hooks": [{"type": "command", "command": "echo mine"}]}
AGENTS = ("backend-developer.md", "code-reviewer.md", "frontend-developer.md", "full-stack-developer.md", "qa-engineer.md")
SKILLS = ("new-project", "next-story")
BLOCK = "<!-- agent-company:start -->\n@~/.claude/company/working-agreement.md\n<!-- agent-company:end -->\n"


def run_installer(target, *args):
    return subprocess.run([sys.executable, INSTALLER, "--target", target, *args],
                          capture_output=True, text=True, timeout=120)


class UninstallTest(unittest.TestCase):
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

    def snapshot(self):
        found = {}
        for root, _, files in os.walk(self.target):
            for name in files:
                full = os.path.join(root, name)
                with open(full, "rb") as handle:
                    found[os.path.relpath(full, self.target)] = handle.read()
        return found

    def seed(self, manifest=True, claude_md=BLOCK):
        """Fake a 0.2.x install, plus a few things that belong to the user."""
        self.write("company/working-agreement.md", "# Working agreement\n")
        self.write("hooks/agent-company/guard_bash.py", "# hook\n")
        for name in AGENTS:
            self.write("agents/" + name, "agent\n")
        for name in SKILLS:
            self.write("skills/%s/SKILL.md" % name, "skill\n")
        self.write("agents/mine.md", "my own agent\n")
        ours = lambda name: {"matcher": "Bash", "hooks": [
            {"type": "command", "command": '"/usr/bin/python3" "/home/u/.claude/hooks/agent-company/%s"' % name}]}
        self.write("settings.json", json.dumps({
            "model": "opus",
            "hooks": {"PreToolUse": [USER_HOOK, ours("guard_bash.py")], "PostToolUse": [ours("scan_secrets.py")]},
            "permissions": {"deny": ["Read(**/.env)", "Read(./secrets/**)"], "ask": ["Bash(git push *)"]},
        }))
        if manifest:
            self.write(".agent-company.json", json.dumps({
                "name": "agent-company", "version": "0.2.0", "agents": list(AGENTS), "skills": list(SKILLS),
                "permissions": {"deny": ["Read(**/.env)"], "ask": ["Bash(git push *)"]},
            }))
        if claude_md:
            self.write("CLAUDE.md", claude_md)

    def uninstall(self, *args):
        result = run_installer(self.target, "--uninstall", *args)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result

    def assertGone(self, *names):
        for name in names:
            self.assertFalse(os.path.exists(self.path(name)), name)

    def test_uninstall_removes_ours_and_keeps_the_users(self):
        self.seed(claude_md="# My rules\n\n" + BLOCK)
        self.uninstall()
        self.assertGone("company", "hooks/agent-company", ".agent-company.json",
                        "agents/code-reviewer.md", "skills/next-story", "skills/new-project")
        self.assertEqual("my own agent\n", self.read("agents/mine.md"))
        settings = self.settings()
        self.assertEqual("opus", settings["model"])
        self.assertEqual(["echo mine"], self.commands(settings))
        self.assertEqual({"deny": ["Read(./secrets/**)"]}, settings["permissions"])
        self.assertEqual("# My rules\n", self.read("CLAUDE.md"))
        self.assertTrue(os.path.isdir(self.path(".backup")))

    def test_claude_md_with_only_the_block_is_removed(self):
        self.seed()
        self.uninstall()
        self.assertGone("CLAUDE.md")

    def test_legacy_top_level_hooks_are_removed(self):
        self.write("hooks/guard_bash.py", "# old hook\n")
        self.write("settings.json", json.dumps({"hooks": {"PreToolUse": [USER_HOOK, {"matcher": "Bash", "hooks": [
            {"type": "command", "command": 'python "$HOME/.claude/hooks/guard_bash.py"'}]}]}}))
        self.uninstall()
        self.assertGone("hooks/guard_bash.py")
        self.assertEqual(["echo mine"], self.commands(self.settings()))

    def test_without_a_manifest_known_names_go_and_user_rules_stay(self):
        self.seed(manifest=False)
        self.uninstall()
        self.assertGone("agents/qa-engineer.md", "skills/new-project", "company", "hooks/agent-company")
        self.assertTrue(os.path.exists(self.path("agents", "mine.md")))
        self.assertEqual({"deny": ["Read(**/.env)", "Read(./secrets/**)"], "ask": ["Bash(git push *)"]},
                         self.settings()["permissions"])
        self.assertEqual(["echo mine"], self.commands(self.settings()))

    def test_dry_run_changes_nothing(self):
        self.seed()
        before = self.snapshot()
        result = self.uninstall("--dry-run")
        self.assertEqual(before, self.snapshot())
        self.assertFalse(os.path.exists(self.path(".backup")))
        self.assertIn("Dry run", result.stdout)

    def test_invalid_settings_changes_nothing(self):
        self.seed()
        self.write("settings.json", "{ not json")
        before = self.snapshot()
        result = run_installer(self.target, "--uninstall")
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(before, self.snapshot())
        self.assertTrue(os.path.exists(self.path("company", "working-agreement.md")))

    def test_no_flags_writes_nothing_and_points_to_the_plugin(self):
        result = run_installer(self.target)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([], os.listdir(self.target))
        self.assertIn("/plugin install pit@pitcrew", result.stdout)
        self.assertIn("--uninstall", result.stdout)

    def test_uninstall_on_an_empty_target_is_harmless(self):
        self.uninstall()
        self.assertEqual([], os.listdir(self.target))


if __name__ == "__main__":
    unittest.main()
