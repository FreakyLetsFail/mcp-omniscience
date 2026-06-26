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

indexing_status = "idle"
indexing_progress = ""

def background_index():
    global indexing_status, indexing_progress
    indexing_status = "indexing"
    indexing_progress = "Scanning files..."
    try:
        files = scan_workspace(workspace_dir)
        total = len(files)
        for i, f in enumerate(files):
            indexing_progress = f"Processing {i+1}/{total}..."
            process_file(f)
        indexing_status = "ready"
        indexing_progress = f"Finished processing {total} files."
    except Exception as e:
        indexing_status = "error"
        indexing_progress = str(e)

@mcp.tool()
def get_index_status() -> str:
    """Check the status of the background indexing process."""
    return f"Status: {indexing_status}\nProgress: {indexing_progress}"

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

watcher = None

@mcp.tool()
def rebuild_index(path: str = None) -> str:
    """Manually trigger a complete re-indexing. Provide a 'path' to change the workspace directory."""
    global workspace_dir, watcher
    
    if path:
        if not os.path.isdir(path):
            return f"Error: Directory {path} does not exist."
        workspace_dir = path
        
        # Re-initialize DB paths for the new workspace
        db_dir = os.path.join(workspace_dir, ".omniscience")
        vector_db.db = __import__("lancedb").connect(os.path.join(db_dir, "lancedb"))
        graph_db.conn = __import__("sqlite3").connect(os.path.join(db_dir, "graph.db"), check_same_thread=False)
        
        if watcher:
            watcher.stop()
        watcher = WorkspaceWatcher(workspace_dir, process_file)
        watcher.start()
        
    threading.Thread(target=background_index, daemon=True).start()
    return f"Started re-indexing workspace {workspace_dir} in the background. Use get_index_status() to check progress."

import threading

def main():
    global vector_db, graph_db, workspace_dir, watcher
    workspace_dir = os.environ.get("WORKSPACE_DIR", ".")
    
    db_dir = os.path.join(workspace_dir, ".omniscience")
    vector_db_path = os.path.join(db_dir, "lancedb")
    graph_db_path = os.path.join(db_dir, "graph.db")
    
    vector_db = VectorDB(db_path=vector_db_path)
    graph_db = GraphDB(db_path=graph_db_path)
    
    # Start watcher for incremental updates only.
    # Heavy indexing is now delegated to the CLI tool `omniscience index .` or explicit `rebuild_index` calls.
    watcher = WorkspaceWatcher(workspace_dir, process_file)
    watcher.start()
    
    try:
        # Run server using standard I/O
        mcp.run(transport="stdio")
    finally:
        if watcher:
            watcher.stop()

if __name__ == "__main__":
    main()
