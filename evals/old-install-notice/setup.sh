#!/bin/bash
# A leftover 0.2.x install in the run's Claude config folder. The eval keeps
# that folder next to the run's home ("$HOME/../config"); a normal machine
# uses ~/.claude.
set -e
for dir in "$HOME/../config" "$HOME/.claude"; do
  if [ "$dir" = "$HOME/.claude" ] || [ -d "$dir" ]; then
    mkdir -p "$dir"
    printf '{"name": "agent-company", "version": "0.2.5"}\n' > "$dir/.agent-company.json"
  fi
done
