"""sample_submission baseline.

Returns Kaggle's provided `sample_submission.csv` paths verbatim. Every
path is the inverse of the random walk that generated the scramble, so
every path is valid and has length == scramble depth == initial_state_id
(for ids 1..1000; id=0 is a 72-move outlier).

This is the **zero-search floor** — any real solution must beat it.
Expected on the stratified proxy (101 puzzles, every 10th id 0..1000):
fitness ≈ 50,572, is_valid = 1, compression_ratio = 1.0. On the full
set: fitness = 500,572.

Agents use `helpers.core.load_sample_submission_paths()` as a safety net:
when your search fails or produces a worse path, return the sample path
instead. See `initial_ideas.md` → `sample_submission_fallback`.
"""

from __future__ import annotations


def entrypoint() -> dict:
    from helpers.core import load_test, load_sample_submission_paths
    tests = load_test(proxy=True)
    sample = load_sample_submission_paths()
    return {sid: sample[sid] for sid in tests}
