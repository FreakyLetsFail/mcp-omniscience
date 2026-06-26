import os
import tiktoken
from pathlib import Path
import sys

def count_tokens(text: str, model_name: str = "cl100k_base") -> int:
    """Counts tokens using tiktoken (used by OpenAI models like GPT-4, and similar for Claude)."""
    enc = tiktoken.get_encoding(model_name)
    return len(enc.encode(text))

def main():
    # We will simulate the cost of reading the entire server.py vs extracting a single function.
    project_root = Path(__file__).parent.parent
    server_file_path = project_root / "src" / "omniscience" / "server.py"
    
    if not server_file_path.exists():
        print(f"Error: Could not find {server_file_path}")
        sys.exit(1)
        
    with open(server_file_path, "r", encoding="utf-8") as f:
        full_code = f.read()
        
    # Simulate the extract of a single function (semantic_search)
    # This is what omniscience would return via surgical_read
    surgical_extract = """def semantic_search(query: str) -> str:
    \"\"\"Search the codebase semantically and via keyword (hybrid search).\"\"\"
    results = vector_db.hybrid_search(query)
    if not results:
        return "No results found."
    out = []
    for r in results:
        out.append(f"ID: {r['id']}\\nFile: {r['file_path']}\\nName: {r['name']}\\nPreview:\\n{r['code'][:200]}...\\n")
    return "\\n---\\n".join(out)"""

    full_tokens = count_tokens(full_code)
    surgical_tokens = count_tokens(surgical_extract)
    
    savings = full_tokens - surgical_tokens
    percent_saved = (savings / full_tokens) * 100
    
    print("=" * 50)
    print("Token Cost Analysis: Omniscience MCP vs Traditional")
    print("=" * 50)
    print(f"Target File: {server_file_path.name}")
    print(f"Total Tokens (Entire File):      {full_tokens:,}")
    print(f"Total Tokens (Surgical Extract): {surgical_tokens:,}")
    print("-" * 50)
    print(f"Tokens Saved per Interaction:    {savings:,} tokens")
    print(f"Context Window Saved:            {percent_saved:.2f}%")
    print("=" * 50)
    print("Conclusion: By using Omniscience's `surgical_read`, the LLM only consumes a fraction of the context window.")

if __name__ == "__main__":
    main()
