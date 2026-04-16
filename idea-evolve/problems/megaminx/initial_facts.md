---
name: megaminx_puzzle_basics
type: domain
confidence: high
---

# Megaminx puzzle basics

- The puzzle is a dodecahedron (12 pentagonal faces, 11 cells each minus the
  center, encoded as a length-120 permutation of `0..119`).
- 24 named generators, declared in `helpers.core.GENERATOR_NAMES`:
  `U, -U, D, -D, F, -F, B, -B, L, -L, DR, -DR, BL, -BL, FR, -FR, BR, -BR, FL, -FL, R, -R, DL, -DL`.
- `-X` is the inverse of `X`. Kaggle's puzzle_info.json defines both as
  separate generators (so search graphs use 24-out branching, not 12).
- Solved (central) state is `(0, 1, 2, ..., 119)`.
- A path is a dot-joined string of move names: `"U.F.-R.D"`. Empty string =
  no moves applied.

---
name: kaggle_competition_facts
type: domain
confidence: high
---

# Kaggle competition `cayley-py-megaminx`

- 1001 test puzzles (`initial_state_id` 0..1000). Score = sum of path lengths.
- **Lower is better.**
- Public leaderboard top: **80,499** (Vladislav Kuznetsov, 2026-04-15) ≈
  80.4 moves/puzzle average. Top-3: 80499, 89670, 93606. Then a gap to
  ~413k (greedy/baseline tier), then ~500k (random-walk floor).
- Class A: test set is downloaded; metric is self-checking (apply path,
  compare to central state). Local score = Kaggle score perfectly.
- No pretrained predictor exists in cayleypy 0.1.0 for the Megaminx graph.
  `Predictor.pretrained(graph)` raises `KeyError`. Top scores were achieved
  with custom predictors trained on random-walk data, hand-tuned heuristics,
  or meet-in-the-middle.
- **cayleypy version pinning.** `requirements.txt` pins `cayleypy>=0.1,<1.0`.
  Helpers assume the 0.1.x API (`Puzzles.megaminx()` returns a `CayleyGraphDef`,
  `CayleyGraph(gdef).beam_search(...)` accepts the kwargs in `helpers.core.cayleypy_beam_solver`).
  If a 0.2.x release changes signatures, re-test before bumping.

---
name: search_complexity
type: theory
confidence: medium
---

# Search complexity

- Naive BFS branching factor: 24. Depth-D BFS visits ≤ 24^D states.
  D=10 ≈ 6e13. D=15 ≈ 2e20. Untenable past depth ~7.
- God's number for Megaminx is unknown. Conjectured upper bound ~45 in the
  half-turn metric (literature varies; treat as approximate).

(Solution approaches that exploit these limits — beam search, meet-in-the-middle,
pattern databases — live in `initial_ideas.md`, not here.)

---
name: scoring_and_sentinels
type: contract
confidence: high
---

# Scoring + sentinels

- Per-row score: `len(path.split("."))` if the path applied to `initial_state`
  reaches `solved_state`. Otherwise `SENTINEL_ROW_SCORE = 1_000_000`.
- Overall sentinel (whole solution failed): `1_000_000_000` (1e9). See
  `metrics.yaml:fitness.sentinel_value` and `docs/problem_design_guide.md` §13.10.
- `is_valid = 1` only if EVERY expected row had a valid solving path. One bad
  row → `is_valid = 0` AND fitness gets penalized per-row, NOT clamped to
  the overall sentinel.
- Auxiliaries: `avg_path_length`, `solved_count`, `expected_count`,
  `invalid_count`. All visible in `.score` sidecars and dashboard.

---
name: hardware_and_concurrency
type: contract
confidence: high
---

# Hardware

- Megaminx runs CPU-only with `concurrency: parallel`. Multiple agents can
  call `evaluate.py` simultaneously; no GPU lock.
- cayleypy requires torch; CPU torch is sufficient (verified 2026-04-16).
- Per-eval budget: keep entrypoint() under 5 minutes on the proxy subset.
  baseline_cayleypy with beam_width=512 averages ~30s on 100 puzzles.
- If/when a solution wants GPU-trained predictors, see DESIGN-18 in CLAUDE.md
  (resource-pool scheduling, not yet implemented).

---
name: external_resources
type: reference
confidence: high
---

# External resources for further research

The model is welcome to fetch any of these for deeper context. All links are
public Kaggle notebooks (Class A competition, freely viewable). Vote counts
recorded 2026-04-16; ranking is approximate quality signal.

## Megaminx-specific notebooks

| Notebook | Author | Votes | Why |
|---|---|---|---|
| [cayleypy-megaminx-base-litvinov-michael](https://www.kaggle.com/code/mitchell11/cayleypy-megaminx-base-litvinov-michael) | Michael Litvinov | 20 | Most-voted Megaminx base solver. Start here. |
| [cayleypy-megaminx-first-steps](https://www.kaggle.com/code/mitchell11/cayleypy-megaminx-first-steps) | Michael Litvinov | 13 | Beginner-friendly walkthrough of the puzzle + cayleypy. |
| [cayleypy-megaminx-research-litvinov-michael](https://www.kaggle.com/code/mitchell11/cayleypy-megaminx-research-litvinov-michael) | Michael Litvinov | 9 | Research notes — what worked / didn't on Megaminx. |
| [cayleypy-megaminx-ml-base-litvinov-michael](https://www.kaggle.com/code/mitchell11/cayleypy-megaminx-ml-base-litvinov-michael) | Michael Litvinov | 5 | ML-based Megaminx solver. Custom predictor pattern. |
| [cayleypy-megaminx-meetinthemiddle-bfs-solver](https://www.kaggle.com/code/alexandervc/cayleypy-megaminx-meetinthemiddle-bfs-solver) | Alexander Chervov | 4 | MeetInTheMiddle reference for Megaminx specifically. |
| [cayleypy-megaminx-bfs-solver](https://www.kaggle.com/code/alexandervc/cayleypy-megaminx-bfs-solver) | Alexander Chervov | 4 | Plain BFS reference for Megaminx (depth-bounded). |

## General CayleyPy / permutation-puzzle technique

| Notebook | Author | Votes | Why |
|---|---|---|---|
| [baseline-1-for-permutations](https://www.kaggle.com/code/alexandervc/baseline-1-for-permutations) | Alexander Chervov | 164 | Foundational baseline for permutation-puzzle competitions. |
| [cayleypy-demo](https://www.kaggle.com/code/fedimser/cayleypy-demo) | Dima Fedoriaka | 78 | Official cayleypy demo (BFS, beam, predictors). |
| [lrx-cayleypy-rl-mdqn](https://www.kaggle.com/code/alexandervc/lrx-cayleypy-rl-mdqn) | Alexander Chervov | 67 | RL approach (DQN) for permutation puzzles. |
| [beam-search-with-cayleypy](https://www.kaggle.com/code/fedimser/beam-search-with-cayleypy) | Dima Fedoriaka | 51 | Beam search tuning patterns. Width × depth × predictor tradeoffs. |
| [cayleypy-howto](https://www.kaggle.com/code/ivankolt/cayleypy-howto) | ivanKolt | 51 | How-to guide. API-reference style. |
| [cayleypy-cube-train-and-solve-smallmodel](https://www.kaggle.com/code/lilypilly/cayleypy-cube-train-and-solve-smallmodel) | LilyPilly | 51 | End-to-end: train a small model + use it in beam search. Megaminx-applicable. |

## Library / reference

- **CayleyPy GitHub:** https://github.com/cayleypy/cayleypy — source, generators, algorithm definitions.
- **CayleyPy API reference:** https://cayleypy.github.io/cayleypy-docs/api.html — symbol-level docs (terse).
- **Competition page:** https://www.kaggle.com/competitions/cayley-py-megaminx — overview, rules, leaderboard.
- **Sister competitions** (similar shape, transferable techniques):
  - https://www.kaggle.com/competitions/cayley-py-4x4x4-cube — 4×4 Rubik (10^55 states).
  - https://www.kaggle.com/competitions/cayley-py-6x6x6-cube — 6×6 Rubik (10^150).
  - https://www.kaggle.com/competitions/cayley-py-professor-tetraminx — Tetrahedron puzzle.

## How to fetch a notebook locally

```bash
set -a && source .env && set +a
kaggle kernels pull <notebook-ref> -p /tmp/notebook   # e.g. mitchell11/cayleypy-megaminx-first-steps
ls /tmp/notebook                                       # downloaded .ipynb
```

If a notebook is private or requires the competition's TOS, the same 403
applies as for `competitions download`.
