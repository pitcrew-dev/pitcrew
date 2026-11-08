#!/bin/bash
set -e
bash "$(dirname "$0")/../fixtures/copy-salon.sh"
# The story has used $21; lower its budget to $20 so the next agent is blocked.
sed -i.bak 's/^Story budget: \$25$/Story budget: $20/' .claude/project/budget.md && rm .claude/project/budget.md.bak
