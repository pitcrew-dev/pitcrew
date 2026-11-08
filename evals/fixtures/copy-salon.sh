#!/bin/bash
# Copies the sample salon project into the run's empty workspace.
# Called by each case's setup.sh as: bash "<case dir>/../fixtures/copy-salon.sh"
set -e
cp -R "$(dirname "$0")/salon/." .
