"""Optional per-problem failure-diagnosis hints + kill hook.

For Kaggle problems running `concurrency: parallel` on CPU, the default kill
hook (problems/_shared/eval_hooks_default.py) is sufficient — agents kill
their own stale evals via SIGTERM/SIGKILL. Override `kill_eval` here only if
the problem holds non-fcntl resources (GPU lock, named-port server, etc.).

`diagnose_failure` returns a markdown string embedded in proc_logs under
"What to try next." Keep hints actionable and problem-specific.
"""

from __future__ import annotations


def diagnose_failure(error_class: str, error_message: str, context: dict) -> str:
    msg = (error_message or "").lower()

    if "timeout" in msg or isinstance(error_class, str) and "Timeout" in error_class:
        return (
            "- The eval exceeded the budget. Inspect `solve_time_s` in the .score file.\n"
            "- If the bottleneck is search depth, swap to a beam/MITM helper from helpers.core."
        )
    if "module" in msg and "not found" in msg:
        return (
            "- Missing import. Add the package to requirements.txt and `pip install -r requirements.txt`.\n"
            "- For Kaggle competitions, additional libs go in the `# <problem>-specific` block."
        )
    return (
        "- Check the proc_log Timeline for the last successful step before the failure.\n"
        "- Compare against `helpers/README.md` to confirm the helper API hasn't drifted."
    )


# kill_eval is intentionally not defined here — the orchestrator falls back to
# problems/_shared/eval_hooks_default.kill_eval (SIGTERM → grace → SIGKILL).
