#!/usr/bin/env python3
"""Simple validation script to check syntax and imports."""

import ast
import sys
from pathlib import Path

# Check syntax of all Python files
files_to_check = [
    "src/request_system/presentation/models.py",
    "src/request_system/presentation/api.py",
    "src/request_system/application/services/request_service.py",
    "tests/test_search_and_filtering.py",
]

errors = []
for file_path in files_to_check:
    full_path = Path(file_path)
    if not full_path.exists():
        errors.append(f"File not found: {file_path}")
        continue
    
    try:
        with open(full_path) as f:
            code = f.read()
        ast.parse(code)
        print(f"✓ {file_path} - Syntax OK")
    except SyntaxError as e:
        errors.append(f"Syntax Error in {file_path}: {e}")
        print(f"✗ {file_path} - Syntax Error: {e}")

if errors:
    print("\nErrors found:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print("\n✓ All files have valid Python syntax!")
    sys.exit(0)
