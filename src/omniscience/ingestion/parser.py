import os
from pathlib import Path
from typing import Dict, Any, List

from tree_sitter import Language, Parser, Query, QueryCursor
import tree_sitter_python as tspython
import tree_sitter_typescript as tstypescript

# Initialize languages
PY_LANGUAGE = Language(tspython.language())
TS_LANGUAGE = Language(tstypescript.language_typescript())

PY_QUERY_STR = """
(function_definition name: (identifier) @name) @def
(class_definition name: (identifier) @name) @def
"""

TS_QUERY_STR = """
(function_declaration name: (identifier) @name) @def
(class_declaration name: (type_identifier) @name) @def
(method_definition name: (property_identifier) @name) @def
(arrow_function) @def
"""

PY_QUERY = Query(PY_LANGUAGE, PY_QUERY_STR)
TS_QUERY = Query(TS_LANGUAGE, TS_QUERY_STR)

def get_parser_and_query(extension: str):
    if extension == ".py":
        return Parser(PY_LANGUAGE), PY_QUERY
    elif extension in (".ts", ".tsx"):
        return Parser(TS_LANGUAGE), TS_QUERY
    else:
        raise ValueError(f"Unsupported extension: {extension}")

def extract_symbols(file_path: str, code_bytes: bytes) -> List[Dict[str, Any]]:
    ext = os.path.splitext(file_path)[1]
    try:
        parser, query = get_parser_and_query(ext)
    except ValueError:
        return []

    tree = parser.parse(code_bytes)
    root_node = tree.root_node
    
    try:
        cursor = QueryCursor(query)
        matches = cursor.matches(root_node)
    except Exception:
        matches = []

    symbols = []
    
    for pattern_index, match_dict in matches:
        defs = match_dict.get("def", [])
        names = match_dict.get("name", [])
        for d in defs:
            name_val = f"anonymous_{d.start_point[0]}"
            for n in names:
                if n.parent == d or n.parent == d.parent:
                    name_val = n.text.decode('utf8')
                    break
            symbols.append({
                "id": f"{file_path}::{name_val}",
                "file_path": file_path,
                "name": name_val,
                "code": d.text.decode('utf8'),
                "start_line": d.start_point[0],
                "end_line": d.end_point[0]
            })

    return symbols
