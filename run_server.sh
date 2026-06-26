#!/usr/bin/env bash
# Internal runner for MCP clients

# If WORKSPACE_DIR is not explicitly passed by the MCP client via env vars,
# default to the directory from which the client launched this script (the user's project).
export WORKSPACE_DIR="${WORKSPACE_DIR:-$PWD}"

# Change to the omniscience repository directory to ensure uv finds the correct .venv
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

export PYTHONPATH="src"

# Run the server
exec uv run python -m omniscience.server
