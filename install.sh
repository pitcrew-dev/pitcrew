#!/usr/bin/env bash
#
# Installs the agent company into ~/.claude so every project on this machine
# can use it. Re-run after editing anything under home/.
#
#   bash install.sh          install or update
#   bash install.sh --dry    show what would change, touch nothing
#
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/home"
DEST="${HOME}/.claude"
DRY=0
[ "${1:-}" = "--dry" ] && DRY=1

say() { printf '  %s\n' "$*"; }
run() { if [ "$DRY" = 1 ]; then say "would: $*"; else "$@"; fi; }

[ -d "$SRC" ] || { echo "error: $SRC not found — run this from the repo root"; exit 1; }

echo
echo "Installing agent company"
echo "  from  $SRC"
echo "  to    $DEST"
[ "$DRY" = 1 ] && echo "  (dry run — nothing will be written)"
echo

# --- back up anything we are about to replace -------------------------------
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="${DEST}/.backup/${STAMP}"
for item in CLAUDE.md agents skills hooks company settings.json; do
  if [ -e "${DEST}/${item}" ]; then
    say "backing up existing ${item}"
    run mkdir -p "$BACKUP"
    run cp -r "${DEST}/${item}" "${BACKUP}/"
  fi
done

# --- copy the tree ----------------------------------------------------------
run mkdir -p "$DEST"

# company/ and hooks/ are entirely ours — safe to replace wholesale.
for item in company hooks; do
  [ -e "${SRC}/${item}" ] || continue
  say "installing ${item}/"
  run rm -rf "${DEST:?}/${item}"
  run cp -r "${SRC}/${item}" "${DEST}/"
done

# CLAUDE.md is a single file (already backed up above).
if [ -e "${SRC}/CLAUDE.md" ]; then
  say "installing CLAUDE.md"
  run cp "${SRC}/CLAUDE.md" "${DEST}/CLAUDE.md"
fi

# agents/ and skills/ are SHARED with anything else you have installed.
# Merge per item so nothing of yours is deleted — only same-named items are
# overwritten, and you are told which.
for item in agents skills; do
  [ -d "${SRC}/${item}" ] || continue
  run mkdir -p "${DEST}/${item}"
  for entry in "${SRC}/${item}"/*; do
    [ -e "$entry" ] || continue
    name="$(basename "$entry")"
    if [ -e "${DEST}/${item}/${name}" ]; then
      say "replacing ${item}/${name} (backed up)"
    else
      say "adding    ${item}/${name}"
    fi
    run rm -rf "${DEST}/${item}/${name}"
    run cp -r "$entry" "${DEST}/${item}/"
  done
  # Report what we left untouched, so you can see nothing was lost.
  for entry in "${DEST}/${item}"/*; do
    [ -e "$entry" ] || continue
    name="$(basename "$entry")"
    [ -e "${SRC}/${item}/${name}" ] || say "keeping   ${item}/${name} (yours, untouched)"
  done
done

# --- merge hooks into settings.json without clobbering user settings --------
say "merging hooks into settings.json"
if [ "$DRY" = 0 ]; then
  python - "$DEST" "$SRC" <<'PY'
import json, os, sys

dest_dir, src_dir = sys.argv[1], sys.argv[2]
settings_path = os.path.join(dest_dir, "settings.json")
fragment_path = os.path.join(src_dir, "settings.hooks.json")

try:
    with open(settings_path, encoding="utf-8") as fh:
        settings = json.load(fh)
except (OSError, ValueError):
    settings = {}

with open(fragment_path, encoding="utf-8") as fh:
    fragment = json.load(fh)

# Hooks live globally, so they cannot use $CLAUDE_PROJECT_DIR (that points at
# whatever project is open). Rewrite to the installed location.
serialized = json.dumps(fragment["hooks"]).replace(
    "$CLAUDE_PROJECT_DIR/.claude/hooks", "$HOME/.claude/hooks"
)
settings["hooks"] = json.loads(serialized)

with open(settings_path, "w", encoding="utf-8") as fh:
    json.dump(settings, fh, indent=2)
    fh.write("\n")

kept = [k for k in settings if k != "hooks"]
print("    hooks installed; preserved existing keys: " + (", ".join(kept) or "none"))
PY
else
  say "would merge hooks into ${DEST}/settings.json (existing keys preserved)"
fi

echo
if [ "$DRY" = 1 ]; then
  echo "Dry run complete. Nothing was written."
else
  echo "Done. Restart Claude Code, then from any project directory:"
  echo
  echo "    \"I want to build a website for my business\"   ->  runs /new-project"
  echo "    \"go\"                                          ->  runs /next-story"
  echo
  [ -d "$BACKUP" ] && echo "Previous files backed up to ${BACKUP}"
fi
echo
