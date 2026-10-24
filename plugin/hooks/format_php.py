#!/usr/bin/env python3
"""PostToolUse formatter for PHP files.

Runs the project's OWN formatter (Laravel Pint) on the one PHP file an agent
just wrote, so formatting never fails a review. Pint formats a whole file,
which could turn a small edit into a drive-by reformat of an old file, so
this only runs when that can't happen:

  * the project already uses Pint (pint.json, or laravel/pint in composer.json)
  * and the file is new, or its committed version was already Pint-clean

In every other case it does nothing. It never introduces a formatter into a
project that doesn't have one. The project wins.

Silent on success. Speaks only when Pint fails (usually a PHP syntax error).
Fails OPEN on any internal error.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile


def find_root(path):
    current = os.path.dirname(os.path.abspath(path))
    while True:
        if os.path.isfile(os.path.join(current, "composer.json")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def uses_pint(root):
    if os.path.isfile(os.path.join(root, "pint.json")):
        return True
    try:
        with open(os.path.join(root, "composer.json"), encoding="utf-8") as handle:
            composer = json.load(handle)
    except (OSError, ValueError):
        return False
    return "laravel/pint" in (composer.get("require-dev") or {}) or "laravel/pint" in (composer.get("require") or {})


def run(command, root, timeout=90):
    return subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=timeout)


def committed_version_is_clean(root, relative, pint):
    """True if the file is new, or its HEAD version already passes Pint."""
    tracked = run(["git", "ls-files", "--error-unmatch", relative], root, 10)
    if tracked.returncode != 0:
        inside = run(["git", "rev-parse", "--is-inside-work-tree"], root, 10)
        return inside.returncode == 0  # new file in a git repo: safe. No git at all: can't tell, skip.
    head = run(["git", "show", "HEAD:" + relative.replace(os.sep, "/")], root, 10)
    if head.returncode != 0:
        return True  # tracked but never committed (e.g. only staged): treat as new
    folder = tempfile.mkdtemp(prefix="format-php-")
    try:
        copy = os.path.join(folder, os.path.basename(relative))
        with open(copy, "w", encoding="utf-8", newline="") as handle:
            handle.write(head.stdout)
        return run(pint + ["--test", copy], root).returncode == 0
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    path = (payload.get("tool_input") or {}).get("file_path") or ""
    if not path.lower().endswith(".php") or path.lower().endswith(".blade.php") or not os.path.isfile(path):
        return 0

    root = find_root(path)
    php = shutil.which("php")
    if not root or not php:
        return 0
    relative = os.path.relpath(os.path.abspath(path), root)
    if relative.startswith("..") or relative.split(os.sep)[0] == "vendor":
        return 0

    pint_script = os.path.join(root, "vendor", "bin", "pint")
    if not os.path.isfile(pint_script) or not uses_pint(root):
        return 0
    pint = [php, pint_script]

    if not committed_version_is_clean(root, relative, pint):
        return 0  # an old, un-formatted file: formatting it would touch lines the task never changed

    result = run(pint + [relative], root)
    if result.returncode != 0:
        output = (result.stdout + result.stderr).strip().splitlines()[-15:]
        sys.stderr.write("Pint could not format %s (often a PHP syntax error):\n%s\n" % (relative, "\n".join(output)))
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
