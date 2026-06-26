import os
from typing import Tuple
from omniscience.ingestion.parser import extract_symbols, get_parser_and_query

def surgical_patch(file_path: str, symbol_name: str, new_code: str) -> Tuple[bool, str]:
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    content_bytes = content.encode("utf-8")
    symbols = extract_symbols(file_path, content_bytes)
    
    target = None
    for s in symbols:
        if s["name"] == symbol_name:
            target = s
            break
            
    if not target:
        return False, f"Symbol '{symbol_name}' not found in {file_path}"
        
    # Validation dry-run
    ext = os.path.splitext(file_path)[1]
    try:
        parser, _ = get_parser_and_query(ext)
        tree = parser.parse(new_code.encode("utf-8"))
        if tree.root_node.has_error:
            return False, "Syntax error detected in the new code. Patch aborted."
    except Exception as e:
        return False, f"Validation error: {e}"

    lines = content.split('\n')
    start_idx = target["start_line"]
    end_idx = target["end_line"]
    
    new_lines = new_code.split('\n')
    patched_lines = lines[:start_idx] + new_lines + lines[end_idx+1:]
    patched_content = "\n".join(patched_lines)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(patched_content)
        
    # Auto-sync will be triggered by watchdog in the main server loop
    return True, "Patch applied successfully."
