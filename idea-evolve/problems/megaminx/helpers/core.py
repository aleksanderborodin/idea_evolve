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
FULL_SIZE: int = 1001                # full Kaggle test set
PROXY_STRIDE: int = 10               # every Nth id → stratified proxy
PROXY_SIZE: int = 101                # len([0, 10, 20, ..., 1000]) — stratified 1/10 slice
DEFAULT_MODE: str = "proxy"

# Per-row sentinel: a single invalid path contributes this much to the sum.
# Stays well below the overall fitness sentinel (1e9 from metrics.yaml) so a
# few invalid rows still rank above an entirely-failed solution.
SENTINEL_ROW_SCORE: int = 1_000_000

# ---- Depth buckets --------------------------------------------------------

# scramble depth == initial_state_id for ids 1..1000 (id=0 is a 72-move outlier).
# Buckets expose per-regime diagnostics so agents can see where their search
# is working and where it isn't. Ranges chosen to mirror the full-set
# distribution; proxy (every 10th id) keeps the same shape at 1/10 scale.
BUCKETS: tuple[tuple[str, int, int], ...] = (
    ("special",   0,   1),     # id 0 only (72-move scramble)
    ("short",     1,   26),    # shallow scrambles
    ("medium",    26,  101),   # unguided beam's sweet spot
    ("hard",      101, 501),   # needs a learned predictor or MITM
    ("very_hard", 501, 1001),  # dominates score; Kaggle-top territory
)
BUCKET_NAMES: tuple[str, ...] = tuple(name for name, _, _ in BUCKETS)


def depth_bucket(sid: int) -> str:
    """Classify an initial_state_id into a depth bucket."""
    for name, lo, hi in BUCKETS:
        if lo <= sid < hi:
            return name
    return "very_hard"

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

    `proxy=True` returns a **stratified 1/10 slice** — every `PROXY_STRIDE`-th
    id, so ids `[0, 10, 20, ..., 1000]` (101 puzzles). This preserves the full
    depth distribution (depth == id for ids 1..1000), unlike a first-100 slice
    which would contain zero deep scrambles. Deterministic across runs so the
    content-hash cache stays coherent.

    `proxy=False` returns all 1001 rows (the actual Kaggle test set).
    """
    out: dict = {}
    with TEST_CSV_PATH.open() as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            sid = int(row[0])
            if proxy and sid % PROXY_STRIDE != 0:
                continue
            state = tuple(int(x) for x in row[1].split(","))
            out[sid] = state
    return out


@lru_cache(maxsize=1)
def load_sample_submission_lengths() -> dict:
    """Return `{sid: path_length}` for Kaggle's sample_submission.csv.

    By the competition generator's construction, `sample_submission[sid]` is
    the inverse of the random walk used to produce `test[sid]`. So path
    length == scramble depth, and for ids 1..1000 this equals the id itself.
    id 0 is a special 72-move scramble. Every sample_submission path is valid
    (i.e. reaches the solved state), so agents can use these paths as a
    guaranteed-valid fallback and compute `compression_ratio` against them.
    """
    out: dict = {}
    with SAMPLE_SUBMISSION_PATH.open() as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            sid = int(row[0])
            path = row[1]
            out[sid] = 0 if not path else len(path.split("."))
    return out


def load_sample_submission_paths() -> dict:
    """Return `{sid: dot_joined_path}` — the full Kaggle sample_submission.

    Same data as `load_sample_submission_lengths` but returns the actual move
    strings. Use this to bootstrap a solution (e.g. return these paths
    verbatim as a depth-N safety net, then try to improve specific ids).
    Not cached — ~1 MB of text; caller should memoize if calling repeatedly.
    """
    out: dict = {}
    with SAMPLE_SUBMISSION_PATH.open() as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            sid = int(row[0])
            out[sid] = row[1]
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
        aux:       dict with core counts, diagnostic distribution stats
                   (compression_ratio, improved_count, max/p50/p95 path length),
                   and per-bucket breakdowns (`bucket_<name>_{count,fitness,
                   solved,invalid}` for each of {special, short, medium, hard,
                   very_hard}).

    p50/p95/max_path_length are computed over **solved** paths only (including
    sentinels would dominate the distribution; `solved_count` already surfaces
    the failure rate). compression_ratio is `our_fitness / sample_submission_fitness`
    on the same test subset — sample_submission is a guaranteed-valid baseline,
    so compression_ratio < 1.0 means real optimization; == 1.0 means we're just
    echoing the freebie; > 1.0 means we're worse than doing nothing.
    """
    tests = load_test(proxy=proxy)
    sample_lens = load_sample_submission_lengths()

    # Per-bucket accumulators
    bucket_stats = {
        name: {"count": 0, "fitness": 0, "solved": 0, "invalid": 0}
        for name in BUCKET_NAMES
    }

    total = 0
    solved = 0
    invalid: list = []
    solved_path_lens: list = []
    improved = 0  # rows where our path is strictly shorter than sample_submission

    for sid, init_state in tests.items():
        b = depth_bucket(sid)
        bucket_stats[b]["count"] += 1

        path = predictions.get(sid)
        if path is None:
            total += SENTINEL_ROW_SCORE
            bucket_stats[b]["fitness"] += SENTINEL_ROW_SCORE
            bucket_stats[b]["invalid"] += 1
            invalid.append(sid)
            continue

        plen, ok = score_path(init_state, path)
        if ok:
            total += plen
            bucket_stats[b]["fitness"] += plen
            bucket_stats[b]["solved"] += 1
            solved += 1
            solved_path_lens.append(plen)
            sample_len = sample_lens.get(sid, 0)
            if sample_len > 0 and plen < sample_len:
                improved += 1
        else:
            total += SENTINEL_ROW_SCORE
            bucket_stats[b]["fitness"] += SENTINEL_ROW_SCORE
            bucket_stats[b]["invalid"] += 1
            invalid.append(sid)

    n = len(tests)
    is_valid = 1 if solved == n else 0

    # Distribution shape (solved-only — sentinels would dominate)
    if solved_path_lens:
        sorted_lens = sorted(solved_path_lens)
        m = len(sorted_lens)
        p50 = sorted_lens[m // 2]
        p95 = sorted_lens[min(m - 1, int(0.95 * m))]
        max_len = sorted_lens[-1]
    else:
        p50 = p95 = max_len = SENTINEL_ROW_SCORE

    # compression_ratio: how much did we compress the free sample_submission baseline?
    sample_fit = sum(sample_lens.get(sid, 0) for sid in tests)
    if sample_fit > 0:
        compression_ratio = round(total / sample_fit, 4)
    else:
        compression_ratio = 1.0

    aux = {
        "avg_path_length": round(total / max(1, n), 2),
        "solved_count": solved,
        "expected_count": n,
        "invalid_count": len(invalid),
        # Diagnostics
        "compression_ratio": compression_ratio,
        "improved_count": improved,
        "max_path_length": max_len,
        "p50_path_length": p50,
        "p95_path_length": p95,
    }
    # Flatten per-bucket stats
    for name, stats in bucket_stats.items():
        aux[f"bucket_{name}_count"] = stats["count"]
        aux[f"bucket_{name}_fitness"] = stats["fitness"]
        aux[f"bucket_{name}_solved"] = stats["solved"]
        aux[f"bucket_{name}_invalid"] = stats["invalid"]

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
    predictor=None,
):
    """Solve one state with cayleypy's beam search. Returns dot-joined Kaggle
    move names, or None if not found within `max_steps`.

    Lazy-imports cayleypy + torch — slow first call (~1s), fast thereafter.
    No pretrained predictor exists for Megaminx (verified 2026-04-16); the
    default search is unguided heuristic.

    `predictor`: optional `cayleypy.Predictor` to guide the search.
      - `cayleypy.Predictor(graph, 'hamming')` — zero-training Hamming-distance
        heuristic; a cheap baseline worth trying before training anything.
      - A custom trained predictor for real gains.
      - `None` (default) — unguided beam.
      Note: build the predictor from the SAME graph that the solver uses
      (`cayleypy.CayleyGraph(cayleypy.Puzzles.megaminx())`) so names/indices
      line up. See `helpers/README.md` for an end-to-end snippet.
    """
    import cayleypy  # type: ignore
    gdef = cayleypy.Puzzles.megaminx()
    graph = cayleypy.CayleyGraph(gdef)
    res = graph.beam_search(
        start_state=list(initial_state),
        beam_width=beam_width,
        max_steps=max_steps,
        return_path=True,
        predictor=predictor,
    )
    if not getattr(res, "path_found", False):
        return None
    cay_path = res.path or []
    moves: list = []
    for idx in cay_path:
        cname = gdef.generator_names[idx]
        moves.append(_to_kaggle_name(cname))
    return ".".join(moves)
