#!/usr/bin/env bash
# Standalone CLI wrapper for Omniscience

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

export PYTHONPATH="src"
exec uv run python -m omniscience.cli "$@"
