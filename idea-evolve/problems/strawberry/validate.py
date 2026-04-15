"""
Validate a solution module for the Strawberry Disease Segmentation problem.

Solutions are full Python training scripts — we can only validate syntax and
that entrypoint() exists. We cannot pre-validate what entrypoint() will do.

evaluate.py calls this before acquiring the GPU lock to fail fast on bad files.
"""

import importlib.util
import sys
from pathlib import Path


def validate_module(filepath: str) -> dict:
    """
    Validate a solution file.

    Checks:
    1. File is syntactically valid Python
    2. Module loads without error at import time
    3. entrypoint() function is defined and callable

    Returns:
        {"is_valid": 1} if valid
        {"is_valid": 0, "fitness": 0, ..., "error": "..."} if invalid
    """
    try:
        spec = importlib.util.spec_from_file_location("_validate_check", filepath)
        module = importlib.util.module_from_spec(spec)
        # Add problem root so 'from helpers.core import ...' resolves at import time
        problem_root = str(Path(__file__).parent)
        if problem_root not in sys.path:
            sys.path.insert(0, problem_root)
        spec.loader.exec_module(module)
    except SyntaxError as e:
        return _invalid(f"SyntaxError: {e}")
    except Exception as e:
        # Import-time errors are acceptable if they're due to missing ultralytics
        # (evaluate.py re-execs into the right venv before calling entrypoint)
        if "ultralytics" in str(e) or "torch" in str(e):
            pass  # will be available in the first_project venv
        else:
            return _invalid(f"Module import error: {e}")
        # Re-try by just parsing AST for entrypoint existence
        return _check_ast(filepath)

    if not hasattr(module, "entrypoint") or not callable(module.entrypoint):
        return _invalid("Solution must define a callable def entrypoint()")

    return {"is_valid": 1}


def _check_ast(filepath: str) -> dict:
    """Fallback: just check for def entrypoint using AST when imports fail."""
    import ast
    try:
        tree = ast.parse(Path(filepath).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "entrypoint":
                return {"is_valid": 1}
        return _invalid("Solution must define def entrypoint()")
    except SyntaxError as e:
        return _invalid(f"SyntaxError: {e}")
    except Exception as e:
        return _invalid(f"Cannot parse solution: {e}")


def _invalid(error: str) -> dict:
    return {
        "is_valid": 0,
        "fitness": 0,
        "mAP50": 0,
        "mAP50_95": 0,
        "F1": 0,
        "error": error,
    }


# Legacy compatibility: evaluate.py imports this module and may call validate()
# (kept as alias for the module-level validate function used in older problems)
def validate(config_or_path) -> dict:
    """Entry point called by evaluate.py. Accepts either a file path or dict."""
    if isinstance(config_or_path, str):
        return validate_module(config_or_path)
    # If someone passes a dict (shouldn't happen with new format), reject it
    return _invalid(
        "This problem uses full training scripts, not config dicts. "
        "entrypoint() should do training and return {mAP50: float, ...}"
    )
