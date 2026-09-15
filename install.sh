#!/usr/bin/env bash
# Thin wrapper kept for compatibility. The installer is install.py:
#
#   bash install.sh [--dry-run | --uninstall]
#
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

for py in python3 python; do
  if command -v "$py" >/dev/null 2>&1 && "$py" -c 'import sys; sys.exit(sys.version_info < (3, 8))' 2>/dev/null; then
    exec "$py" install.py "$@"
  fi
done

echo "error: Python 3.8+ is required (python3 or python on PATH)." >&2
exit 1
