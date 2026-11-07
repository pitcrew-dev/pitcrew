#!/usr/bin/env python3
"""Remove the old (0.2.x) agent company install from ~/.claude.

Agent Company is now a Claude Code plugin. This script only uninstalls the
old copy-into-~/.claude version:

    python install.py --uninstall            remove the old install
    python install.py --uninstall --dry-run  show what would change; write nothing
    python install.py --target DIR           use another config directory (for testing)

Safe by design:
  * Your own agents, skills, hooks, permission rules and CLAUDE.md are kept.
  * Everything removed is backed up to ~/.claude/.backup/<time>/.
  * A manifest records exactly what was added, so only that is removed.
  * If your settings.json isn't valid JSON, nothing is changed at all.

Needs Python 3.8+. No other dependencies.
"""
import argparse
import datetime
import json
import os
import shutil
import sys

HOOKS_SUBDIR = os.path.join("hooks", "agent-company")
MANIFEST = ".agent-company.json"
LEGACY_HOOKS = ("guard_paths.py", "guard_bash.py", "scan_secrets.py")
START, END = "<!-- agent-company:start -->", "<!-- agent-company:end -->"
KNOWN_AGENTS = ("backend-developer.md", "code-reviewer.md", "frontend-developer.md", "full-stack-developer.md", "qa-engineer.md")
KNOWN_SKILLS = ("new-project", "next-story")


class Uninstaller:
    def __init__(self, dest, dry_run):
        self.dest = dest
        self.dry = dry_run
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.backup_root = os.path.join(dest, ".backup", stamp)
        self.backed_up = False

    # ---- small helpers -----------------------------------------------------

    def say(self, message):
        print("  " + message)

    def path(self, *parts):
        return os.path.join(self.dest, *parts)

    def backup(self, target):
        if self.dry or not os.path.exists(target):
            return
        copy = os.path.join(self.backup_root, os.path.relpath(target, self.dest))
        os.makedirs(os.path.dirname(copy), exist_ok=True)
        if os.path.isdir(target):
            shutil.copytree(target, copy, dirs_exist_ok=True)
        else:
            shutil.copy2(target, copy)
        self.backed_up = True

    def remove(self, target):
        if not os.path.exists(target):
            return
        self.backup(target)
        if self.dry:
            return
        if os.path.isdir(target):
            shutil.rmtree(target)
        else:
            os.remove(target)

    def read(self, target):
        try:
            with open(target, encoding="utf-8") as handle:
                return handle.read()
        except OSError:
            return ""

    def write(self, target, text):
        if self.dry:
            return
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)

    def load_json(self, target):
        text = self.read(target)
        if not text.strip():
            return {}
        try:
            return json.loads(text)
        except ValueError as error:
            sys.exit("error: %s is not valid JSON (%s).\nFix it first. Nothing was changed." % (target, error))

    # ---- settings.json -----------------------------------------------------

    @staticmethod
    def is_our_hook(command):
        command = command.replace("\\", "/")
        return "hooks/agent-company/" in command or any("/.claude/hooks/" + name in command for name in LEGACY_HOOKS)

    def strip_our_hooks(self, settings):
        hooks = settings.get("hooks") or {}
        for event in list(hooks):
            groups = []
            for group in hooks[event]:
                kept = [h for h in group.get("hooks", []) if not self.is_our_hook(h.get("command", ""))]
                if kept:
                    groups.append(dict(group, hooks=kept))
            if groups:
                hooks[event] = groups
            else:
                del hooks[event]
        if hooks:
            settings["hooks"] = hooks
        else:
            settings.pop("hooks", None)

    def strip_our_rules(self, settings, added):
        permissions = settings.get("permissions") or {}
        for kind, rules in (added or {}).items():
            if kind in permissions:
                permissions[kind] = [r for r in permissions[kind] if r not in rules]
                if not permissions[kind]:
                    del permissions[kind]
        if permissions:
            settings["permissions"] = permissions
        else:
            settings.pop("permissions", None)

    # ---- CLAUDE.md ---------------------------------------------------------

    def uninstall_agreement(self):
        target = self.path("CLAUDE.md")
        text = self.read(target)
        if START not in text:
            return
        before, _, rest = text.partition(START)
        _, _, after = rest.partition(END)
        remaining = (before.rstrip("\n") + "\n" + after.lstrip("\n")).strip()
        self.backup(target)
        if remaining:
            self.say("removing the import line from CLAUDE.md (your content is kept)")
            self.write(target, remaining + "\n")
        else:
            self.say("removing CLAUDE.md (it only held the import line)")
            if not self.dry:
                os.remove(target)

    # ---- uninstall -----------------------------------------------

    def uninstall(self):
        settings_path = self.path("settings.json")
        settings = self.load_json(settings_path)
        manifest = self.load_json(self.path(MANIFEST))
        if not manifest:
            self.say("no install manifest found; removing the company's own files only")
        for kind in ("agents", "skills"):
            names = manifest.get(kind) or (KNOWN_AGENTS if kind == "agents" else KNOWN_SKILLS)
            for name in names:
                if os.path.exists(self.path(kind, name)):
                    self.say("removing %s/%s" % (kind, name))
                    self.remove(self.path(kind, name))
        for target in ("company", HOOKS_SUBDIR) + tuple(os.path.join("hooks", n) for n in LEGACY_HOOKS):
            if os.path.exists(self.path(target)):
                self.say("removing %s" % target.replace(os.sep, "/"))
                self.remove(self.path(target))
        if settings:
            self.backup(settings_path)
            self.strip_our_hooks(settings)
            self.strip_our_rules(settings, manifest.get("permissions"))
            self.say("removing the company's hooks and permission rules from settings.json")
            self.write(settings_path, json.dumps(settings, indent=2) + "\n")
        self.uninstall_agreement()
        self.remove(self.path(MANIFEST))


MESSAGE = """
Agent Company is now a Claude Code plugin. Install it inside Claude Code:

    /plugin marketplace add kasshif01/vide_coding
    /plugin install pit@pitcrew

To remove the old 0.2.x install first, run:

    python install.py --uninstall

(add --dry-run to see what would be removed without changing anything)
"""


def main():
    parser = argparse.ArgumentParser(description="Remove the old (0.2.x) agent company install. "
                                                 "The company is now a Claude Code plugin.")
    parser.add_argument("--dry-run", "--dry", action="store_true", help="show what would change; write nothing")
    parser.add_argument("--uninstall", action="store_true", help="remove the old 0.2.x install")
    parser.add_argument("--target", default=os.path.join(os.path.expanduser("~"), ".claude"),
                        help="Claude Code config directory (default: ~/.claude)")
    args = parser.parse_args()

    if sys.version_info < (3, 8):
        sys.exit("error: Python 3.8+ is required.")
    if not args.uninstall:
        print(MESSAGE)
        return

    uninstaller = Uninstaller(os.path.abspath(args.target), args.dry_run)
    print("\nUninstalling the old agent company\n  from  %s%s\n" % (
        uninstaller.dest, "\n  (dry run: nothing will be written)" if args.dry_run else ""))

    uninstaller.uninstall()

    print()
    if args.dry_run:
        print("Dry run complete. Nothing was written.")
    else:
        print("Done. Restart Claude Code for the changes to take effect.")
        if uninstaller.backed_up:
            print("Anything removed was backed up to %s" % uninstaller.backup_root)
    print()


if __name__ == "__main__":
    main()
