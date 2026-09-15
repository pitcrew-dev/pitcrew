#!/usr/bin/env python3
"""PostToolUse secret scanner for Write/Edit.

Flags credentials in a file an agent has just written. It cannot un-write the
file, so the message tells the agent what to do next.

Two kinds of check:
  known formats  AWS, GitHub, Stripe, Slack, Google, Anthropic, OpenAI and
                 SendGrid keys, private key blocks, JWTs. Checked in every file.
  generic        password/secret/token assignments, env() and define()
                 defaults, URLs with an inline password. Skipped in tests,
                 fixtures and prose, where fake credentials are normal.

Only the VALUE is judged, never the whole line, so a real secret sitting next
to the word "true" or "example" is still caught, while placeholders
(your-key-here, xxx, <token>, ${VAR}) and validation rules
('required|min:8') are not flagged. A noisy scanner gets ignored, which is
worse than no scanner.

Fails OPEN and stays quiet on any internal error.
"""
import json
import re
import sys

KNOWN = [
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key id"),
    (re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY"), "private key block"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}"), "GitHub token"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}"), "GitHub token"),
    (re.compile(r"\b[sr]k_live_[A-Za-z0-9]{16,}"), "Stripe live key"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{35}"), "Google API key"),
    (re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}"), "Anthropic API key"),
    (re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_\-]{32,}"), "OpenAI API key"),
    (re.compile(r"\bSG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}\b"), "SendGrid API key"),
    (re.compile(r"\beyJ[A-Za-z0-9_\-]{20,}\.eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}"), "hardcoded JWT"),
]

SECRET_NAME = (r"[A-Za-z0-9_.\-]*(?:password|passwd|pwd|secret|token|api[_\-]?key|access[_\-]?key"
               r"|private[_\-]?key|client[_\-]?secret)[A-Za-z0-9_.\-]*")
DEFAULT_NAME = r"[A-Za-z0-9_]*(?:key|secret|token|password|pass|salt)[A-Za-z0-9_]*"

GENERIC = [
    (re.compile(r"(?i)\b" + SECRET_NAME + r"['\"]?\s*(?:=>|=|:)\s*['\"](?P<value>[^'\"\s]{8,})['\"]"),
     "hardcoded credential"),
    (re.compile(r"(?im)^\s*(?:export\s+)?" + SECRET_NAME + r"\s*[:=]\s*(?P<value>[^\s'\"#${][^\s'\"#]{7,})\s*$"),
     "hardcoded credential"),
    (re.compile(r"(?i)\benv\(\s*['\"]" + DEFAULT_NAME + r"['\"]\s*,\s*['\"](?P<value>[^'\"]{8,})['\"]"),
     "secret used as an env() default"),
    (re.compile(r"(?i)\bdefine\(\s*['\"]" + DEFAULT_NAME + r"['\"]\s*,\s*['\"](?P<value>[^'\"]{8,})['\"]"),
     "secret in define()"),
    (re.compile(r"(?i)\b[a-z][a-z0-9+.\-]*://[^/\s:@'\"]+:(?P<value>[^@\s/'\"]{3,})@"),
     "URL with an inline password"),
]

PLACEHOLDER = re.compile(
    r"(?i)(your[_\-]?|example|placeholder|change[_\-]?me|xxx|dummy|sample|fake|redacted|test[_\-]?key"
    r"|<[^>]*>|\.\.\.|\*{3,}|^\$|\$\{|%\w+%|\{\{|put your)"
)
COMMON_WORDS = {"password", "secret", "null", "none", "true", "false", "changeme", "passw0rd"}
LOOKS_LIKE_A_NAME = re.compile(r"[a-z_.\-:|,/ ]+")  # lowercase words: identifiers, rule strings

SKIP_FILE = re.compile(
    r"(?i)\.env\.(example|dist|sample|template)$|(^|/)(vendor|node_modules)/"
    r"|(^|/)(composer\.lock|package-lock\.json|yarn\.lock|pnpm-lock\.yaml)$|\.(min\.js|min\.css|map)$"
)
SKIP_GENERIC = re.compile(r"(?i)(^|/)(tests?|specs?|__tests__|fixtures?|stubs?)/|\.(md|txt|rst)$")


def is_placeholder(value):
    value = value.strip()
    return (value.lower() in COMMON_WORDS
            or bool(PLACEHOLDER.search(value))
            or len(set(value)) <= 2
            or "|" in value)


def scan(path, lines):
    check_generic = not SKIP_GENERIC.search(path)
    findings = []
    for number, line in enumerate(lines, start=1):
        if len(line) > 2000:
            continue
        label = None
        for pattern, name in KNOWN:
            match = pattern.search(line)
            if match and not is_placeholder(match.group(0)):
                label = name
                break
        if label is None and check_generic:
            for pattern, name in GENERIC:
                match = pattern.search(line)
                if not match:
                    continue
                value = match.group("value")
                if is_placeholder(value) or LOOKS_LIKE_A_NAME.fullmatch(value):
                    continue
                label = name
                break
        if label:
            findings.append("  %s:%d  possible %s" % (path, number, label))
    return findings


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    path = (payload.get("tool_input") or {}).get("file_path") or ""
    normalized = path.replace("\\", "/")
    if not path or SKIP_FILE.search(normalized):
        return 0
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            lines = handle.read().splitlines()
    except OSError:
        return 0

    findings = scan(normalized, lines)
    if not findings:
        return 0

    sys.stderr.write(
        "SECRET SCAN flagged the file you just wrote:\n\n%s\n\n"
        "Secrets never go in code, config defaults or docs; only in .env, which agents never write.\n"
        "1. If you added it: replace the value with config()/env('KEY') and no default, add KEY= to\n"
        "   .env.example, and tell the user which value to set.\n"
        "2. If it was there before your change: don't fix it in place. Report it as a security finding.\n"
        "3. If it's a false positive (test data, a placeholder): say so in your report and continue.\n"
        % "\n".join(findings[:10])
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
