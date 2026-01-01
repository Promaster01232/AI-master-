#!/usr/bin/env bash
set -euo pipefail

# Run ShellCheck on tracked shell scripts. Uses local shellcheck if available,
# otherwise falls back to Docker image koalaman/shellcheck:stable.

SCRIPTS=$(git ls-files '*.sh' || true)
if [ -z "$SCRIPTS" ]; then
  echo "No shell scripts found"
  exit 0
fi

if command -v shellcheck >/dev/null 2>&1; then
  echo "Using local shellcheck"
  shellcheck -x $SCRIPTS
else
  if command -v docker >/dev/null 2>&1; then
    echo "Using Dockerized ShellCheck"
    # Prefix file paths with /mnt inside container
    MAPPED=$(echo "$SCRIPTS" | sed 's|^|/mnt/|')
    docker run --rm -v "$PWD":/mnt koalaman/shellcheck:stable -x $MAPPED
  else
    echo "ShellCheck not found and Docker missing. Install shellcheck or docker to run this script." >&2
    exit 2
  fi
fi
