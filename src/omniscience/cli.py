import argparse
import os
import sys
import time

from omniscience.ingestion.scanner import scan_workspace
from omniscience.ingestion.parser import extract_symbols
from omniscience.memory.vector_db import VectorDB
from omniscience.memory.graph_db import GraphDB

def process_file(file_path: str, vector_db: VectorDB, graph_db: GraphDB):
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

def main():
    parser = argparse.ArgumentParser(description="Omniscience CLI - The surgical dual-brain indexer")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    index_parser = subparsers.add_parser("index", help="Index a workspace directory")
    index_parser.add_argument("path", type=str, nargs="?", default=".", help="Path to the workspace to index (default: current directory)")
    
    args = parser.parse_args()
    
    if args.command == "index":
        workspace_dir = os.path.abspath(args.path)
        if not os.path.isdir(workspace_dir):
            print(f"Error: Directory {workspace_dir} does not exist.")
            sys.exit(1)
            
        print(f"🤖 Initializing Project Omniscience Indexer...")
        print(f"📂 Workspace: {workspace_dir}")
        
        start_time = time.time()
        
        # Store databases in the workspace directory so the MCP server finds them
        db_dir = os.path.join(workspace_dir, ".omniscience")
        vector_db_path = os.path.join(db_dir, "lancedb")
        graph_db_path = os.path.join(db_dir, "graph.db")
        
        vector_db = VectorDB(db_path=vector_db_path)
        graph_db = GraphDB(db_path=graph_db_path)
        
        files = scan_workspace(workspace_dir)
        total = len(files)
        
        print(f"🔍 Found {total} supported files to index.")
        print("⚙️ Processing files (AST parsing + Voyage-4-nano embeddings)...")
        
        for i, f in enumerate(files):
            # Simple progress display
            progress = (i + 1) / total * 100
            sys.stdout.write(f"\r[{progress:5.1f}%] Processing {i+1}/{total} files...")
            sys.stdout.flush()
            
            process_file(f, vector_db, graph_db)
            
        duration = time.time() - start_time
        print(f"\n✅ Indexing complete in {duration:.2f} seconds!")
        print("You can now start your MCP Client (Antigravity, Claude, Cursor) safely without lag.")

if __name__ == "__main__":
    main()
