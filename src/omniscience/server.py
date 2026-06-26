import os
import sys
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

from omniscience.ingestion.scanner import WorkspaceWatcher, scan_workspace
from omniscience.ingestion.parser import extract_symbols
from omniscience.memory.vector_db import VectorDB
from omniscience.memory.graph_db import GraphDB
from omniscience.updater.patcher import surgical_patch

mcp = FastMCP("Project Omniscience")

# Global instances (initialized in main)
vector_db = None
graph_db = None
workspace_dir = "."

def process_file(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        symbols, dependencies = extract_symbols(file_path, code.encode("utf-8"))
        vector_db.upsert_symbols(symbols)
        
        # Clear existing file dependencies and insert new ones
        graph_db.clear_file_dependencies(file_path)
        for caller_id, callee_name in dependencies:
            graph_db.add_dependency(caller_id, callee_name)
    except Exception as e:
        print(f"Error processing {file_path}: {e}", file=sys.stderr)

def initial_index():
    files = scan_workspace(workspace_dir)
    for f in files:
        process_file(f)

@mcp.tool()
def semantic_search(query: str) -> str:
    """Search the codebase semantically and via keyword (hybrid search)."""
    results = vector_db.hybrid_search(query)
    if not results:
        return "No results found."
    out = []
    for r in results:
        out.append(f"ID: {r['id']}\nFile: {r['file_path']}\nName: {r['name']}\nPreview:\n{r['code'][:200]}...\n")
    return "\n---\n".join(out)

@mcp.tool()
def graph_query(symbol_id: str) -> str:
    """Find the blast radius (which functions call this symbol)."""
    # symbol_id is typically "file_path::symbol_name"
    parts = symbol_id.split("::")
    symbol_name = parts[1] if len(parts) == 2 else symbol_id
    
    deps = graph_db.get_blast_radius(symbol_name)
    if not deps:
        return f"No dependents found calling '{symbol_name}'."
    return "The following functions call this symbol:\n" + "\n".join(deps)

@mcp.tool()
def surgical_read(symbol_id: str) -> str:
    """Read only the exact code lines of a specific symbol_id (e.g. 'src/app.py::main')."""
    # symbol_id is typically "file_path::symbol_name"
    parts = symbol_id.split("::")
    if len(parts) != 2:
        return "Invalid symbol_id format. Expected 'file_path::symbol_name'."
    file_path, symbol_name = parts[0], parts[1]
    
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
        
    with open(file_path, "r", encoding="utf-8") as f:
        code_bytes = f.read().encode("utf-8")
        
    symbols, _ = extract_symbols(file_path, code_bytes)
    for s in symbols:
        if s["name"] == symbol_name:
            return s["code"]
            
    return f"Symbol {symbol_name} not found in {file_path}."

@mcp.tool()
def apply_surgical_patch(symbol_id: str, new_code: str) -> str:
    """Replace an existing symbol with entirely new code. Re-indexing is automatic."""
    parts = symbol_id.split("::")
    if len(parts) != 2:
        return "Invalid symbol_id format. Expected 'file_path::symbol_name'."
    file_path, symbol_name = parts[0], parts[1]
    
    success, msg = surgical_patch(file_path, symbol_name, new_code)
    return msg

@mcp.tool()
def rebuild_index() -> str:
    """Manually trigger a complete re-indexing of the entire workspace."""
    try:
        initial_index()
        return "Workspace successfully re-indexed!"
    except Exception as e:
        return f"Failed to rebuild index: {e}"

import threading

def main():
    global vector_db, graph_db, workspace_dir
    workspace_dir = os.environ.get("WORKSPACE_DIR", ".")
    
    vector_db = VectorDB()
    graph_db = GraphDB()
    
    # Run initial indexing in background to avoid blocking MCP handshake
    threading.Thread(target=initial_index, daemon=True).start()
    
    # Start watcher for incremental updates
    watcher = WorkspaceWatcher(workspace_dir, process_file)
    watcher.start()
    
    try:
        # Run server using standard I/O
        mcp.run(transport="stdio")
    finally:
        watcher.stop()

if __name__ == "__main__":
    main()
