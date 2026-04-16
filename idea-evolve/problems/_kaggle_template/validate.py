"""AST-level validity check for solutions.

Used by orchestrator preflight; intentionally cheap (no execution). Runs in
milliseconds. Heavier checks (does entrypoint actually return a dict?) belong
in evaluate.py — they require a Python execution that may import heavy deps.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def validate(solution_path: str) -> dict:
    """Return {'is_valid': 0|1, 'fitness': sentinel_on_invalid, 'error': str?}."""
    src = Path(solution_path).read_text()
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return {"is_valid": 0, "fitness": 0, "error": f"syntax: {e}"}

    has_entrypoint = any(
        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "entrypoint"
        for n in ast.walk(tree)
    )
    if not has_entrypoint:
        return {"is_valid": 0, "fitness": 0, "error": "missing def entrypoint()"}

    return {"is_valid": 1}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate.py <solution.py>", file=sys.stderr)
        sys.exit(1)
    import json
    print(json.dumps(validate(sys.argv[1])))
