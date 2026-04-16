"""CayleyPy beam-search baseline.

Uses cayleypy's `BeamSearchAlgorithm` (no pretrained predictor exists for
Megaminx) to solve each puzzle in the proxy subset. The search is unguided
heuristic, so it works well on shallow scrambles (the test set has many) and
fails on deep ones (which fall through to the empty path → sentinel).

Expected fitness on PROXY_SIZE=100: a few thousand moves total when the test
set leans easy; substantially worse when most scrambles are deep. The point
is to give agents a real `is_valid=1`-leaning baseline that beats
`baseline_random` and to demonstrate the cayleypy API.

NOTE: the cayleypy-supplied beam search has a hard ceiling on what unguided
search can do for Megaminx. The path forward is custom predictors, MITM, or
hand-tuned heuristics — see initial_ideas.md.
"""

from __future__ import annotations


def entrypoint() -> dict:
    from helpers.core import load_test, cayleypy_beam_solver

    tests = load_test(proxy=True)
    out: dict = {}
    for sid, init_state in tests.items():
        try:
            path = cayleypy_beam_solver(
                init_state, beam_width=512, max_steps=80
            )
        except Exception:
            path = None
        out[sid] = path or ""
    return out
