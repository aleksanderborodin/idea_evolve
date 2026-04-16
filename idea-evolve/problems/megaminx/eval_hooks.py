"""Megaminx-specific failure-diagnosis hints.

`kill_eval` is intentionally NOT defined here — Megaminx runs CPU-only with
`concurrency: parallel`, so the orchestrator falls back to
`problems/_shared/eval_hooks_default.kill_eval` (SIGTERM → grace → SIGKILL).
"""

from __future__ import annotations


def diagnose_failure(error_class: str, error_message: str, context: dict) -> str:
    msg = (error_message or "").lower()
    cls = (error_class or "").lower()

    if "unknown move" in msg or "expected one of" in msg:
        return (
            "- A path contained a token outside the 24 Kaggle generator names.\n"
            "- Check `helpers.core.GENERATOR_NAMES` for the canonical list.\n"
            "- Sign convention: `-U` is the inverse of `U` (NOT `U_inv` or `U'`).\n"
            "- If you used cayleypy directly, translate via `_to_kaggle_name()`."
        )
    if "didn't solve" in msg or "not solved" in msg:
        return (
            "- The path applied cleanly but didn't reach the central state.\n"
            "- Most common bug: applying generators in cayleypy's index order\n"
            "  without converting to Kaggle move names. See cayleypy_beam_solver.\n"
            "- Sanity-check with `helpers.core.apply_path` + `is_solved`."
        )
    if "timeout" in msg or "timeout" in cls:
        return (
            "- Search exhausted its budget. Plain BFS at depth >= 25 explodes\n"
            "  (24^25 ≈ 10^34 states); use beam search or meet-in-the-middle.\n"
            "- For first-pass exploration, drop `beam_width` to ~500 and\n"
            "  `max_steps` to ~100 to bound wall-clock per state."
        )
    if "modulenotfound" in cls and "cayleypy" in msg:
        return (
            "- cayleypy isn't installed in this venv. `pip install cayleypy torch`\n"
            "  (use --index-url https://download.pytorch.org/whl/cpu for CPU-only)."
        )
    if "predictor" in msg and "pretrained" in msg:
        return (
            "- cayleypy has no pretrained predictor for the Megaminx graph.\n"
            "- Either run beam search without a predictor, or train a custom\n"
            "  predictor from random walks (see initial_ideas.md)."
        )
    return (
        "- Read the proc_log Timeline for the last successful step.\n"
        "- Sanity-test your solver on `tests[1]` (1 move from solved) and\n"
        "  `tests[2]` (2 moves from solved) before committing to the proxy run."
    )
