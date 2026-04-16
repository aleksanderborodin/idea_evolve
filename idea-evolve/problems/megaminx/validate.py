"""AST-level validity check for Megaminx solutions.

Runs in milliseconds — orchestrator preflight only. Does NOT execute the
solution; it just confirms there's a `def entrypoint()` so the more expensive
import + call in `evaluate.py` won't waste a slot on syntactically broken code.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def validate(solution_path: str) -> dict:
    src = Path(solution_path).read_text()
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return {"is_valid": 0, "fitness": 1_000_000_000, "error": f"syntax: {e}"}

    has_entrypoint = any(
        isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "entrypoint"
        for n in ast.walk(tree)
    )
    if not has_entrypoint:
        return {"is_valid": 0, "fitness": 1_000_000_000, "error": "missing def entrypoint()"}

    return {"is_valid": 1}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate.py <solution.py>", file=sys.stderr)
        sys.exit(1)
    import json
    print(json.dumps(validate(sys.argv[1])))
