#!/usr/bin/env bash
# Start script for the Omniscience MCP Server

# Make sure we are in the correct directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Ensure the required environment variables are set
export PYTHONPATH="src"
export WORKSPACE_DIR="$DIR"

# Run the server using uv
exec uv run python -m omniscience.server
