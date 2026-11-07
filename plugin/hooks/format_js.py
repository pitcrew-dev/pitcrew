#!/usr/bin/env python3
"""PostToolUse formatter for JavaScript, TypeScript and stylesheet files.

Runs the project's OWN Prettier on the one file an agent just wrote, the way
format_php.py runs Pint, so formatting never fails a review. Prettier formats
a whole file, so to avoid a drive-by reformat of old code it only runs when:

  * the project already uses Prettier (a Prettier config file, or a
    "prettier" key in package.json) and has it installed locally
  * and the file is new, or its committed version was already Prettier-clean

In every other case it does nothing. It never installs Prettier and never
introduces it into a project that doesn't use it. The project wins.

Silent on success. Speaks only when Prettier fails (usually a syntax error).
Fails OPEN on any internal error.
"""
import json
import os
import shutil
import subprocess
import sys

EXTENSIONS = (".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".css", ".scss", ".json")
CONFIG_FILES = (
    ".prettierrc", ".prettierrc.json", ".prettierrc.yaml", ".prettierrc.yml", ".prettierrc.json5",
    ".prettierrc.js", ".prettierrc.cjs", ".prettierrc.mjs", ".prettierrc.ts", ".prettierrc.toml",
    "prettier.config.js", "prettier.config.cjs", "prettier.config.mjs", "prettier.config.ts",
)
SKIP_FILES = ("package-lock.json", "composer.json", "composer.lock")


def find_root(path):
    current = os.path.dirname(os.path.abspath(path))
    while True:
        if os.path.isfile(os.path.join(current, "package.json")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def uses_prettier(root):
    if any(os.path.isfile(os.path.join(root, name)) for name in CONFIG_FILES):
        return True
    try:
        with open(os.path.join(root, "package.json"), encoding="utf-8") as handle:
            return "prettier" in json.load(handle)
    except (OSError, ValueError):
        return False


def prettier_command(root):
    """[node, <prettier's own bin script>] from the project's node_modules, or None."""
    node = shutil.which("node")
    package = os.path.join(root, "node_modules", "prettier")
    try:
        with open(os.path.join(package, "package.json"), encoding="utf-8") as handle:
            binary = json.load(handle).get("bin")
    except (OSError, ValueError):
        return None
    if isinstance(binary, dict):
        binary = binary.get("prettier")
    script = os.path.join(package, binary) if isinstance(binary, str) else None
    if not node or not script or not os.path.isfile(script):
        return None
    return [node, script]


def run(command, root, stdin=None, timeout=90):
    return subprocess.run(command, cwd=root, input=stdin, capture_output=True, text=True,
                          encoding="utf-8", timeout=timeout)


def committed_version_is_clean(root, relative, prettier):
    """True if the file is new, or its HEAD version already matches Prettier's output."""
    tracked = run(["git", "ls-files", "--error-unmatch", relative], root, timeout=10)
    if tracked.returncode != 0:
        inside = run(["git", "rev-parse", "--is-inside-work-tree"], root, timeout=10)
        return inside.returncode == 0  # new file in a git repo: safe. No git at all: can't tell, skip.
    head = run(["git", "show", "HEAD:" + relative.replace(os.sep, "/")], root, timeout=10)
    if head.returncode != 0:
        return True  # tracked but never committed (e.g. only staged): treat as new
    # --stdin-filepath lets Prettier find the project's config and ignore file for this path.
    result = run(prettier + ["--stdin-filepath", relative], root, stdin=head.stdout)
    return result.returncode == 0 and result.stdout == head.stdout


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    path = (payload.get("tool_input") or {}).get("file_path") or ""
    name = os.path.basename(path).lower()
    if not name.endswith(EXTENSIONS) or name in SKIP_FILES or not os.path.isfile(path):
        return 0

    root = find_root(path)
    if not root:
        return 0
    relative = os.path.relpath(os.path.abspath(path), root)
    if relative.startswith("..") or "node_modules" in relative.split(os.sep):
        return 0
    if not uses_prettier(root):
        return 0
    prettier = prettier_command(root)
    if not prettier:
        return 0

    if not committed_version_is_clean(root, relative, prettier):
        return 0  # an old, un-formatted file: formatting it would touch lines the task never changed

    result = run(prettier + ["--write", relative], root)
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip().splitlines()[-15:]
        sys.stderr.write("Prettier could not format %s (often a syntax error):\n%s\n" % (relative, "\n".join(output)))
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
