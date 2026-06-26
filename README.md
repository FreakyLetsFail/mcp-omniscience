# Project Omniscience (Dual-Brain MCP Server)

**Omniscience** is a highly optimized Model Context Protocol (MCP) server designed to give LLMs token-efficient, surgical access to your codebase. Instead of loading an entire repository into context, it uses a "Dual-Brain" architecture to find exactly what is needed and nothing more.

## The Dual-Brain Architecture
1. **Tree-sitter (Structural Brain)**: Parses the AST (Abstract Syntax Tree) of your codebase in real-time. It extracts exact file locations and code snippets for functions, and automatically maps out your **Call Graph** (Caller -> Callee relationships) into a local SQLite database.
2. **LanceDB & Voyage-4-nano (Semantic Brain)**: Stores embeddings of every symbol locally. Allows the LLM to search for concepts ("how does the auth routing work") using lightning-fast hybrid search (BM25 + Vectors).

## Exposed MCP Tools

- `semantic_search`: Finds relevant code symbols based on a natural language query or keywords.
- `graph_query`: Returns the blast radius/dependents of a specific code symbol based on the AST Call-Graph.
- `surgical_read`: Extracts only the exact code snippet for a single function or class, saving thousands of input tokens.
- `apply_surgical_patch`: Replaces an exact code symbol with new code. Ensures structural integrity and automatically triggers a background re-index.

## Installation

This project uses `uv` for ultra-fast dependency management.

```bash
# Clone the repository
# git clone <repo-url>
cd mcp

# Install dependencies and sync the environment
uv sync
```

## Running the Server

You can run the server directly or use the provided convenience script:

```bash
./start.sh
```

### Antigravity Integration
To use this server with Antigravity or any MCP-compatible IDE, add it to your `mcp_config.json`:

```json
{
  "mcpServers": {
    "omniscience": {
      "command": "/bin/bash",
      "args": ["-c", "cd /path/to/mcp && ./start.sh"]
    }
  }
}
```

## How It Saves You Money (Token Efficiency)
Instead of feeding an entire 1000-line file into an LLM context window (which costs money and pollutes the LLM's attention), you can use `semantic_search` to find the exact function ID, and `surgical_read` to extract *only* that function (e.g. 15 lines). 
Run `./scripts/test_token_savings.py` to see a real-world token cost comparison.
