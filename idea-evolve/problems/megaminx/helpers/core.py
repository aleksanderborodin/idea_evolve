"""Megaminx puzzle helpers.

Solutions import from this module to load the puzzle definition, apply moves,
score paths, and (optionally) call cayleypy's beam search. The module is
cheap to import — heavy libraries (cayleypy, torch) are imported lazily inside
the functions that need them.

Kaggle competition: https://www.kaggle.com/competitions/cayley-py-megaminx
"""

from __future__ import annotations

import csv
import json
from functools import lru_cache
from pathlib import Path
from typing import Iterable

# ---- Paths ----------------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PUZZLE_INFO_PATH = DATA_DIR / "puzzle_info.json"
TEST_CSV_PATH = DATA_DIR / "test.csv"
SAMPLE_SUBMISSION_PATH = DATA_DIR / "sample_submission.csv"

# ---- Sizing ---------------------------------------------------------------

STATE_SIZE: int = 120                # length of the permutation that encodes a Megaminx state
PROXY_SIZE: int = 100                # proxy subset for fast iteration
FULL_SIZE: int = 1001                # full Kaggle test set
DEFAULT_MODE: str = "proxy"

# Per-row sentinel: a single invalid path contributes this much to the sum.
# Stays well below the overall fitness sentinel (1e9 from metrics.yaml) so a
# few invalid rows still rank above an entirely-failed solution.
SENTINEL_ROW_SCORE: int = 1_000_000

# ---- Generator names ------------------------------------------------------

# The 24 named moves in the Kaggle puzzle_info.json. Order matches Kaggle.
GENERATOR_NAMES: tuple[str, ...] = (
    "U", "-U", "D", "-D", "F", "-F", "B", "-B",
    "L", "-L", "DR", "-DR", "BL", "-BL", "FR", "-FR",
    "BR", "-BR", "FL", "-FL", "R", "-R", "DL", "-DL",
)
GENERATOR_SET: frozenset[str] = frozenset(GENERATOR_NAMES)


# Map between Kaggle names and cayleypy names (for cayleypy_beam_solver).
# Kaggle "X"  ↔  cayleypy "M_X"
# Kaggle "-X" ↔  cayleypy "M_X_inv"
def _to_cayleypy_name(kname: str) -> str:
    if kname.startswith("-"):
        return f"M_{kname[1:]}_inv"
    return f"M_{kname}"


def _to_kaggle_name(cname: str) -> str:
    s = cname[2:] if cname.startswith("M_") else cname
    if s.endswith("_inv"):
        return f"-{s[:-4]}"
    return s


# ---- Puzzle data loading --------------------------------------------------

@lru_cache(maxsize=1)
def load_puzzle_info() -> dict:
    """Return parsed puzzle_info.json: {'central_state': [...], 'generators': {name: perm}}."""
    return json.loads(PUZZLE_INFO_PATH.read_text())


@lru_cache(maxsize=1)
def _generators_tuple() -> dict:
    """Generators as immutable tuples for fast `apply_move`."""
    info = load_puzzle_info()
    return {name: tuple(perm) for name, perm in info["generators"].items()}


@lru_cache(maxsize=1)
def solved_state() -> tuple:
    """The solved (central) state — what every path must reach."""
    return tuple(load_puzzle_info()["central_state"])


def load_test(proxy: bool = True) -> dict:
    """Return `{initial_state_id: state_tuple}` for the Kaggle test set.

    `proxy=True` returns the first `PROXY_SIZE` rows by id ASC — deterministic
    across runs so the content-hash cache stays coherent.
    """
    n = PROXY_SIZE if proxy else FULL_SIZE
    out: dict = {}
    with TEST_CSV_PATH.open() as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            sid = int(row[0])
            state = tuple(int(x) for x in row[1].split(","))
            out[sid] = state
            if len(out) >= n:
                break
    return out


# ---- Path manipulation ----------------------------------------------------

def apply_move(state: tuple, move_name: str) -> tuple:
    """Apply a single named generator to `state`. Raises on unknown name."""
    perm = _generators_tuple().get(move_name)
    if perm is None:
        raise ValueError(f"unknown move {move_name!r}; expected one of {sorted(GENERATOR_SET)}")
    return tuple(state[perm[i]] for i in range(len(perm)))


def apply_path(state: tuple, path: str) -> tuple:
    """Apply a dot-separated path string (e.g. 'U.F.-R') to `state`."""
    if not path:
        return state
    s = state
    for move in path.split("."):
        s = apply_move(s, move)
    return s


def is_solved(state: tuple) -> bool:
    return state == solved_state()


def score_path(initial_state: tuple, path: str):
    """Return (path_length, valid).

    `valid=False` when any move is unknown OR the final state is not solved.
    Caller decides whether to use SENTINEL_ROW_SCORE for the length.
    """
    if not isinstance(path, str):
        return SENTINEL_ROW_SCORE, False
    try:
        moves = [m for m in path.split(".") if m]
        for m in moves:
            if m not in GENERATOR_SET:
                return SENTINEL_ROW_SCORE, False
        final = apply_path(initial_state, path)
        if not is_solved(final):
            return SENTINEL_ROW_SCORE, False
        return len(moves), True
    except Exception:
        return SENTINEL_ROW_SCORE, False


def score_predictions(predictions: dict, proxy: bool = True):
    """Score a {sid: path} dict against the Kaggle test set.

    Returns:
        fitness:   sum of path lengths across all expected rows. Missing or
                   invalid rows contribute SENTINEL_ROW_SCORE each.
        is_valid:  1 iff EVERY expected row had a valid path.
        aux:       {avg_path_length, solved_count, expected_count, invalid_count}
    """
    tests = load_test(proxy=proxy)
    expected_ids = set(tests)
    total = 0
    solved = 0
    invalid: list = []
    for sid, init_state in tests.items():
        path = predictions.get(sid)
        if path is None:
            total += SENTINEL_ROW_SCORE
            invalid.append(sid)
            continue
        plen, ok = score_path(init_state, path)
        total += plen
        if ok:
            solved += 1
        else:
            invalid.append(sid)
    is_valid = 1 if solved == len(expected_ids) else 0
    aux = {
        "avg_path_length": round(total / max(1, len(expected_ids)), 2),
        "solved_count": solved,
        "expected_count": len(expected_ids),
        "invalid_count": len(invalid),
    }
    return total, is_valid, aux


# ---- Submission writer (used by scripts/submit_to_kaggle.py) -------------

def write_submission(predictions: dict, path: Path) -> None:
    """Write Kaggle-format submission.csv at `path`. Class A problems don't
    use this during evaluation — only for opt-in real-leaderboard scoring."""
    path = Path(path)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["initial_state_id", "path"])
        # Kaggle expects all 1001 rows; include even missing ones with empty path.
        for sid in range(FULL_SIZE):
            w.writerow([sid, predictions.get(sid, "")])


# ---- Optional: cayleypy beam search wrapper -------------------------------

def cayleypy_beam_solver(
    initial_state: Iterable[int],
    beam_width: int = 1000,
    max_steps: int = 200,
):
    """Solve one state with cayleypy's beam search. Returns dot-joined Kaggle
    move names, or None if not found within `max_steps`.

    Lazy-imports cayleypy + torch — slow first call (~1s), fast thereafter.
    No pretrained predictor exists for Megaminx (verified 2026-04-16); the
    search is unguided heuristic.
    """
    import cayleypy  # type: ignore
    gdef = cayleypy.Puzzles.megaminx()
    graph = cayleypy.CayleyGraph(gdef)
    res = graph.beam_search(
        start_state=list(initial_state),
        beam_width=beam_width,
        max_steps=max_steps,
        return_path=True,
    )
    if not getattr(res, "path_found", False):
        return None
    cay_path = res.path or []
    moves: list = []
    for idx in cay_path:
        cname = gdef.generator_names[idx]
        moves.append(_to_kaggle_name(cname))
    return ".".join(moves)
