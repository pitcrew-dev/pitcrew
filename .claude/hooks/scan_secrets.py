#!/usr/bin/env python
"""PostToolUse scanner for Write/Edit.

GitGuardian's 2026 report found AI-assisted commits leak secrets at 3.2%,
roughly double the human baseline. coding-standards.md section 7 forbids secrets
in code; this makes the check deterministic rather than remembered.

Contract: exit 2 returns stderr to the model as context. It cannot un-write the
file, so the message tells the agent to remove the secret now.
Fails OPEN and stays quiet on any internal error.
"""
import json
import re
import sys

# High-confidence patterns only. A noisy scanner gets ignored, which is worse
# than no scanner.
PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY", "private key block"),
    (r"\bgh[pousr]_[A-Za-z0-9]{36,}", "GitHub token"),
    (r"\bsk_live_[A-Za-z0-9]{16,}", "Stripe live secret key"),
    (r"\bxox[abprs]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"\bAIza[0-9A-Za-z_\-]{35}", "Google API key"),
    (r"\beyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.", "hardcoded JWT"),
    (r"(?i)\b(api[_-]?key|secret|password|passwd|token|auth)\s*[=:]\s*[\"'][^\"'$\s{}]{12,}[\"']",
     "hardcoded credential"),
    (r"(?i)mysql://[^:\s]+:[^@\s]+@", "database URL with inline password"),
]

# Values that look like credentials but are obviously not.
PLACEHOLDERS = re.compile(
    r"(?i)(your[_-]?|example|placeholder|changeme|xxx+|<[a-z_ ]+>|\.\.\.|null|true|false"
    r"|dummy|sample|test[_-]?key|fake|redacted|\benv\(|\bgetenv\(|\bconfig\()"
)

SKIP_PATH = re.compile(r"(?i)\.env\.example$|(^|/)(vendor|node_modules)/")


def main() -> int:
    payload = json.loads(sys.stdin.read())

    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or ""
    if not path or SKIP_PATH.search(path.replace("\\", "/")):
        return 0

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return 0

    findings = []
    for number, line in enumerate(lines, start=1):
        if len(line) > 2000 or PLACEHOLDERS.search(line):
            continue
        for pattern, label in PATTERNS:
            if re.search(pattern, line):
                findings.append("  %s:%d  possible %s" % (path, number, label))
                break

    if not findings:
        return 0

    sys.stderr.write(
        "SECRET SCAN flagged the file you just wrote:\n\n%s\n\n"
        "coding-standards.md section 7: secrets never go in code or config, only in .env.\n"
        "Remove the value now, read it via config()/env() instead, add the key to .env.example,\n"
        "and tell the user which value they need to set. If this is a false positive, say so and continue.\n"
        % "\n".join(findings[:10])
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
