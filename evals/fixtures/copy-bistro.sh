#!/bin/bash
# Copies the sample bistro project (Next.js + Prisma + PostgreSQL) into the run's empty workspace.
# Called by a case's setup.sh as: bash "<case dir>/../fixtures/copy-bistro.sh" [with-project]
# With "with-project", the PitCrew project files (.claude/project/) are added too.
set -e
here="$(dirname "$0")"
cp -R "$here/bistro/." .
if [ "$1" = "with-project" ]; then
    cp -R "$here/bistro-project/." .
fi
