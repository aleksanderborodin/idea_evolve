## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen010/explore_2/sol01.py` → C = 1.5028628681165177
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen010/explore_1/sol01.py` → C = 1.5028628681659377

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_021.md` — incremental drift, FFT resync
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_022.md` — top-K screening algorithm
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_023.md` — no convergence at 1e-13
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen010/exploit_1.md` — drift discovery, top-K screening invention, geometric delta grid
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen010/explore_2.md` — fast_check pre-filter implementation
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/incremental_autoconv_update.py` — existing incremental update helper
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py` — existing float64 C computation
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/plateau_analyzer.py` — existing plateau analysis helper
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/README.md` — index of all helpers (NOTE: may be outdated — check actual files in problem/helpers/)

## Directive

**Build the `topk_screened_cd` shared helper.** This has been recommended by the system critic for 2+ consecutive generations (Priority 7 in gen 10 recommendations). It is now mandatory per architect rules.

**The question:** Can the three algorithmic discoveries from gen 10 (top-K screening, per-round FFT resync, geometric delta grid) be packaged into a reusable, validated helper that all future agents can import instead of reimplementing inline?

**Required deliverable:** `output/helpers/topk_screened_cd.py` containing:

```python
def topk_screened_cd(f, K=30, deltas=None, resync_interval=1,
                     max_rounds=200, deadline=None, verbose=False):
    """
    Coordinate descent with top-K screening and periodic FFT resync.

    Implements the best-known CD algorithm combining:
    1. Top-K screening (pattern_022): Only check K highest autoconv positions
       per trial as pre-filter. No false negatives. ~50x speedup.
    2. FFT resync (pattern_021): Recompute autoconv from scratch every
       `resync_interval` rounds to eliminate incremental drift (~1.4e-12/round).
    3. Geometric delta grid: Default np.geomspace(1e-14, 1e-1, 100) covering
       all productive scales.

    Args:
        f: 1D numpy array, non-negative function values on [-1/4, 1/4].
        K: Number of top autoconv positions for screening (default 30).
        deltas: Array of positive delta values to try. Default: geomspace(1e-14, 1e-1, 100).
        resync_interval: FFT resync every N rounds (default 1 = every round).
        max_rounds: Maximum number of full sweeps over all elements.
        deadline: Unix timestamp to stop by (time.time() + budget). None = no limit.
        verbose: If True, print per-round stats.

    Returns:
        dict with keys:
            'f': optimized array (numpy float64)
            'C': final verified C value (float64, from FFT — not incremental)
            'n_improvements': total accepted moves (int)
            'n_rounds': rounds completed (int)
            'round_log': list of dicts with per-round stats:
                {'round': int, 'improvements': int, 'C_verified': float, 'elapsed_s': float}
    """
```

**Implementation requirements:**
1. Import `incremental_autoconv_update.incremental_update` for O(N) per-element updates.
2. Import `compute_c_f64.compute_c` for verified C computation during resync.
3. Top-K screening: maintain sorted indices of K highest autoconv values. For each trial delta, only check these K positions. If trial_max_at_K >= best_C × integral², skip (no improvement possible). Otherwise, do full incremental update and verify.
4. Non-negativity enforcement: `f[i] + delta >= 0` required for each trial.
5. FFT resync: full recomputation of autoconv, integral, top-K indices.
6. Deadline support: check `time.time() > deadline` at start of each round.
7. Return dict, not tuple, for forward compatibility.

**Testing requirements:** Write comprehensive tests in `output/sandbox/scripts/test_topk_screened_cd.py`:
1. **Correctness:** Run on a small known array (N=100). Verify C decreases monotonically across rounds.
2. **Resync vs no-resync:** Run with resync_interval=1 and resync_interval=999 on same array. Verify resync version has lower verified C.
3. **Top-K no false negatives:** For a small array, verify that top-K screening accepts exactly the same moves as full-array screening (K=all).
4. **Deadline enforcement:** Set deadline=time.time()+2. Verify function returns within 3s.
5. **Non-negativity:** Verify no element in output is negative.
6. **Default deltas:** Verify default delta grid is geomspace(1e-14, 1e-1, 100).
7. **Round log format:** Verify round_log entries contain all required keys.
8. **Edge cases:** Empty array, all-zero array, single-element array.

Also update `output/helpers/README.md` to document ALL helpers including this new one. List every `.py` file in `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/` with a one-line description and import path.

**Methodology:** Build incrementally. Start with a minimal working version, run tests, then add optimizations. Do NOT skip testing.

**What NOT to do:**
- Do NOT modify any existing files in `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/` directly — write only to `output/helpers/`.
- Do NOT try to optimize solutions yourself — this is a helper-building task, not an optimization task.
