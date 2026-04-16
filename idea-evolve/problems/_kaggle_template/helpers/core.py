"""Problem-specific helpers for <PROBLEM_TITLE>.

All solution agents import from here. Keep the public API small and the
docstrings concrete — agents read this module before writing code.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Absolute path to this problem's data directory. Always valid because it's
# relative to the file's own location. Never hardcode absolute paths.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Proxy-vs-full test size (see docs/problem_design_guide.md §13.9).
# Solutions import these and pass them to load_test; evaluate.py does NOT read
# a CLI flag (that would break content-hash cache coherence).
PROXY_SIZE: int = 100
FULL_SIZE: int | None = None   # None = full dataset
DEFAULT_MODE: str = "proxy"

# Per-row sentinel (distinct from the overall-fitness sentinel in metrics.yaml).
# A single invalid prediction contributes this value to the sum; when fitness
# direction is lower-is-better, it should push the total above the realistic
# max so one bad row is clearly worse than any valid baseline.
SENTINEL_ROW_SCORE: int = 1_000_000


def load_test(proxy: bool = True) -> dict[Any, Any]:
    """Load the Kaggle test inputs as `{input_id: test_row}`.

    Deterministic: when `proxy=True`, return the first `PROXY_SIZE` items
    (sorted by input_id ascending) so the subset stays stable across runs.
    """
    # TODO: replace with real loader — parse DATA_DIR/<TEST_FILE>.
    raise NotImplementedError("Fill in load_test()")


def score_predictions(predictions: dict[Any, Any]) -> tuple[float, int, dict]:
    """Translate a solution's predictions into (fitness, is_valid, aux_metrics).

    Returns:
        fitness: the primary scalar. On any invalid row, return the
            sentinel_value declared in metrics.yaml.
        is_valid: 1 if all rows validated, 0 otherwise.
        aux_metrics: {name: value} for metrics.yaml auxiliaries. Missing
            auxiliaries render as "—" in the dashboard.
    """
    # TODO: implement domain-specific scoring.
    raise NotImplementedError("Fill in score_predictions()")
