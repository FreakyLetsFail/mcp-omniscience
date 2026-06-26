import os
from pathlib import Path
from omniscience.ingestion.parser import extract_symbols

def main():
    project_root = Path(__file__).parent.parent
    test_file_path = str(project_root / "src" / "omniscience" / "server.py")
    
    with open(test_file_path, "r", encoding="utf-8") as f:
        code_bytes = f.read().encode("utf-8")
        
    symbols, dependencies = extract_symbols(test_file_path, code_bytes)
    
    print("=" * 50)
    print("Call-Graph Dependency Test")
    print("=" * 50)
    print(f"Total symbols found: {len(symbols)}")
    print(f"Total function calls found: {len(dependencies)}")
    print("-" * 50)
    
    print("Sample Dependencies Extracted:")
    # Print the first 10 dependencies
    for caller, callee in dependencies[:10]:
        print(f"[{caller}] calls -> '{callee}'")
        
    print("=" * 50)
    if len(dependencies) > 0:
        print("✅ Success! The AST parser successfully mapped function calls.")
    else:
        print("❌ Failed to find dependencies.")

if __name__ == "__main__":
    main()
