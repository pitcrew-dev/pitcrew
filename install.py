#!/usr/bin/env python3
"""Install, update or remove the agent company in ~/.claude.

    python install.py              install or update
    python install.py --dry-run    show what would change; write nothing
    python install.py --uninstall  remove everything this installer added
    python install.py --target DIR install somewhere else (for testing)

Safe by design:
  * Your own agents, skills, hooks, permission rules and CLAUDE.md are kept.
    Only same-named agents and skills are replaced, and you're told which.
  * Everything replaced or removed is backed up to ~/.claude/.backup/<time>/.
  * A manifest records exactly what was added, so an update or an uninstall
    removes that and nothing of yours.
  * If your settings.json isn't valid JSON, nothing is changed at all.

Needs Python 3.8+ (the hooks need it too). No other dependencies.
"""
import argparse
import datetime
import json
import os
import shutil
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(REPO, "home")
HOOKS_SUBDIR = os.path.join("hooks", "agent-company")
MANIFEST = ".agent-company.json"
LEGACY_HOOKS = ("guard_paths.py", "guard_bash.py", "scan_secrets.py")
START, END = "<!-- agent-company:start -->", "<!-- agent-company:end -->"
IMPORT_BLOCK = START + "\n@~/.claude/company/working-agreement.md\n" + END + "\n"
LEGACY_AGREEMENT = ("# Working agreement", "Loaded in every session, in every project.")


def read_version():
    try:
        with open(os.path.join(REPO, "VERSION"), encoding="utf-8") as handle:
            return handle.read().strip()
    except OSError:
        return "unknown"


class Installer:
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

    def copy(self, source, target):
        if self.dry:
            return
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if os.path.isdir(source):
            shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(source, target)

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

    def merge_settings(self, settings, fragment, old_added):
        self.strip_our_hooks(settings)
        self.strip_our_rules(settings, old_added)

        python = '"%s"' % sys.executable.replace("\\", "/")
        hooks_dir = self.path(HOOKS_SUBDIR).replace("\\", "/")
        hooks = settings.setdefault("hooks", {})
        for event, groups in fragment["hooks"].items():
            for group in groups:
                entries = [dict(h, command=h["command"].replace("__PYTHON__", python).replace("__HOOKS__", hooks_dir))
                           for h in group["hooks"]]
                hooks.setdefault(event, []).append(dict(group, hooks=entries))

        permissions = settings.setdefault("permissions", {})
        added = {}
        for kind, rules in fragment.get("permissions", {}).items():
            current = permissions.setdefault(kind, [])
            for rule in rules:
                if rule not in current:
                    current.append(rule)
                    added.setdefault(kind, []).append(rule)
        return added

    # ---- CLAUDE.md ---------------------------------------------------------

    def install_agreement(self):
        target = self.path("CLAUDE.md")
        text = self.read(target)
        if START in text:
            self.say("CLAUDE.md already imports the working agreement")
            return
        if text.lstrip().startswith(LEGACY_AGREEMENT[0]) and LEGACY_AGREEMENT[1] in text:
            self.backup(target)
            self.say("replacing the old copied working agreement in CLAUDE.md with one import line (backed up)")
            self.write(target, IMPORT_BLOCK)
        elif text.strip():
            self.backup(target)
            self.say("adding one import line to the end of your CLAUDE.md (your content is kept)")
            self.write(target, text.rstrip("\n") + "\n\n" + IMPORT_BLOCK)
        else:
            self.say("creating CLAUDE.md with one import line")
            self.write(target, IMPORT_BLOCK)

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

    # ---- install / uninstall -----------------------------------------------

    def install(self):
        fragment = self.load_json(os.path.join(SRC, "settings.fragment.json"))
        settings_path = self.path("settings.json")
        settings = self.load_json(settings_path)  # validate before touching anything
        manifest = self.load_json(self.path(MANIFEST))

        for name in ("company",):
            self.say("installing %s/" % name)
            self.remove(self.path(name))
            self.copy(os.path.join(SRC, name), self.path(name))

        self.say("installing hooks/agent-company/")
        self.remove(self.path(HOOKS_SUBDIR))
        self.copy(os.path.join(SRC, "hooks"), self.path(HOOKS_SUBDIR))
        for legacy in LEGACY_HOOKS:
            if os.path.exists(self.path("hooks", legacy)):
                self.say("removing old hooks/%s (moved to hooks/agent-company/)" % legacy)
                self.remove(self.path("hooks", legacy))

        installed = {}
        for kind in ("agents", "skills"):
            names = sorted(os.listdir(os.path.join(SRC, kind)))
            installed[kind] = names
            for name in names:
                target = self.path(kind, name)
                self.say(("replacing %s/%s (backed up)" if os.path.exists(target) else "adding    %s/%s") % (kind, name))
                self.remove(target)
                self.copy(os.path.join(SRC, kind, name), target)
            for name in manifest.get(kind, []):
                if name not in names:
                    self.say("removing  %s/%s (no longer part of the company)" % (kind, name))
                    self.remove(self.path(kind, name))
            if os.path.isdir(self.path(kind)):
                for name in sorted(os.listdir(self.path(kind))):
                    if name not in names and name not in manifest.get(kind, []):
                        self.say("keeping   %s/%s (yours, untouched)" % (kind, name))

        self.install_agreement()

        self.backup(settings_path)
        added = self.merge_settings(settings, fragment, manifest.get("permissions"))
        self.say("merging hooks and permission rules into settings.json (your other settings are kept)")
        for kind, rules in added.items():
            self.say("  %s: %s" % (kind, ", ".join(rules)))
        self.write(settings_path, json.dumps(settings, indent=2) + "\n")

        self.write(self.path(MANIFEST), json.dumps({
            "name": "agent-company",
            "version": read_version(),
            "installed_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "source": REPO,
            "agents": installed["agents"],
            "skills": installed["skills"],
            "permissions": added,
        }, indent=2) + "\n")

    def uninstall(self):
        settings_path = self.path("settings.json")
        settings = self.load_json(settings_path)
        manifest = self.load_json(self.path(MANIFEST))
        if not manifest:
            self.say("no install manifest found; removing the company's own files only")
        for kind in ("agents", "skills"):
            names = manifest.get(kind) or sorted(os.listdir(os.path.join(SRC, kind)))
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


def main():
    parser = argparse.ArgumentParser(description="Install, update or remove the agent company.")
    parser.add_argument("--dry-run", "--dry", action="store_true", help="show what would change; write nothing")
    parser.add_argument("--uninstall", action="store_true", help="remove everything this installer added")
    parser.add_argument("--target", default=os.path.join(os.path.expanduser("~"), ".claude"),
                        help="Claude Code config directory (default: ~/.claude)")
    args = parser.parse_args()

    if sys.version_info < (3, 8):
        sys.exit("error: Python 3.8+ is required.")
    if not os.path.isdir(SRC):
        sys.exit("error: %s not found. Run this from a full checkout of the repository." % SRC)

    installer = Installer(os.path.abspath(args.target), args.dry_run)
    action = "Uninstalling" if args.uninstall else "Installing"
    print("\n%s agent company %s\n  from  %s\n  to    %s%s\n" % (
        action, read_version(), SRC, installer.dest, "\n  (dry run: nothing will be written)" if args.dry_run else ""))

    installer.uninstall() if args.uninstall else installer.install()

    print()
    if args.dry_run:
        print("Dry run complete. Nothing was written.")
    else:
        print("Done. Restart Claude Code for the changes to take effect.")
        if installer.backed_up:
            print("Anything replaced was backed up to %s" % installer.backup_root)
    print()


if __name__ == "__main__":
    main()
