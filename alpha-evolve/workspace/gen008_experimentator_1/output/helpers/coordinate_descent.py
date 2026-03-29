"""Standardized coordinate descent optimizer for autocorrelation solutions.

Provides a single-element coordinate descent loop using O(N) incremental
autoconvolution updates. Designed to be the canonical implementation used by
all exploit agents, eliminating the 40x improvement count discrepancy caused
by non-standardized delta grids (gen 7: 6551 vs 156 vs 257 improvements from
the same starting point).

Performance
-----------
- N=500: ~0.3s per round
- N=30000 (25k nonzero): ~220s per round
- Uses hot-set screening (positions near autoconv max) for fast candidate
  evaluation, with full-array verification before accepting any move.
- Periodic FFT resync (every 200 accepts) to bound accumulated drift.

Dependencies
------------
- helpers.incremental_autoconv_update (incremental_update)
- helpers.cross_convolution_f64 (autoconvolve) — for FFT resync
- helpers.compute_c_f64 (compute_c_f64) — for final verification
"""

import numpy as np


def _autoconvolve(f):
    """Compute autoconvolution via FFT. Internal helper to avoid circular imports."""
    f = np.asarray(f, dtype=np.float64)
    f = np.maximum(f, 0.0)
    N = len(f)
    dx = 0.5 / N
    M = 2 * N
    f_padded = np.pad(f, (0, N))
    fft_f = np.fft.fft(f_padded)
    ac = np.fft.ifft(fft_f * fft_f).real * dx
    return ac, f_padded, dx, M


def _build_default_delta_grid():
    """Standard delta grid from exploit_1 gen 7 (most successful: 6551 improvements).

    Absolute deltas: ±1e-12 through ±1e-2 (22 values).
    """
    grid = []
    for e in range(-12, -1):  # 1e-12 to 1e-2
        grid.append(10.0 ** e)
        grid.append(-(10.0 ** e))
    return np.array(grid, dtype=np.float64)


# Module-level constants (computed once at import time)
DEFAULT_ABSOLUTE_DELTAS = _build_default_delta_grid()
DEFAULT_PROPORTIONAL_MULTS = np.array(
    [0.0001, -0.0001, 0.001, -0.001, 0.01, -0.01, 0.1, -0.1],
    dtype=np.float64
)


def _build_hot_set(ac, epsilon_rel=1e-6):
    """Find autoconv positions within epsilon_rel of the maximum.

    These positions form the "hot set" used for fast candidate screening.
    For the TTT-Discover 30k array, this is ~14k of 60k positions.
    """
    max_val = np.max(ac)
    threshold = max_val * (1.0 - epsilon_rel)
    return np.where(ac >= threshold)[0]


def coordinate_descent_round(f, autoconv, dx, M_fft, delta_grid=None,
                              proportional_mults=None, zero_threshold=1e-6,
                              recompute_max_every=200, hot_set_refresh=500,
                              verbose=False):
    """One full-array pass of coordinate descent using incremental autoconv update.

    For each nonzero element i in f:
      - Try each delta in delta_grid (absolute) and proportional_mults * f[i]
      - Use hot-set screening to quickly identify the best candidate
      - Verify with full np.max before accepting
      - Accept the best delta that reduces C
      - If f[i] < zero_threshold, also try zeroing it out

    Uses O(N) incremental autoconvolution update from helpers.incremental_autoconv_update.

    Args:
        f: 1D numpy float64 array, length N. Current solution.
        autoconv: 1D numpy float64 array, length M_fft=2N. Current autoconvolution
            (from autoconvolve() or previous round).
        dx: float. Grid spacing = 0.5 / N.
        M_fft: int. FFT array length = 2*N.
        delta_grid: 1D array of float or None. Absolute deltas to try.
            Default: ±1e-12 through ±1e-2.
        proportional_mults: 1D array of float or None. Multipliers for
            proportional deltas (delta = f[i] * mult).
            Default: [±0.0001, ±0.001, ±0.01, ±0.1].
        zero_threshold: float. Elements below this can be zeroed. Default 1e-6.
        recompute_max_every: int. Full FFT resync frequency (by accepted moves).
            Default 200. Corrects accumulated floating-point drift.
        hot_set_refresh: int. Hot set rebuild frequency (by accepted moves).
            Default 500.
        verbose: bool. Print progress. Default False.

    Returns:
        f_new: 1D float64 array, length N. Updated solution.
        autoconv_new: 1D float64 array, length M_fft. Updated autoconvolution.
        n_improvements: int. Number of accepted moves.
        new_c: float. Final C value (verified against full autoconv max).

    Examples:
        >>> import numpy as np
        >>> from helpers.cross_convolution_f64 import autoconvolve
        >>> rng = np.random.default_rng(42)
        >>> f = np.abs(rng.standard_normal(500)) * 0.1
        >>> ac, fp, dx, M = autoconvolve(f)
        >>> f_new, ac_new, n_impr, c_new = coordinate_descent_round(
        ...     f, ac, dx, M, verbose=True)
        >>> n_impr > 0  # random array always has improvements
        True
    """
    from helpers.incremental_autoconv_update import incremental_update

    if delta_grid is None:
        delta_grid = DEFAULT_ABSOLUTE_DELTAS
    else:
        delta_grid = np.asarray(delta_grid, dtype=np.float64)
    if proportional_mults is None:
        proportional_mults = DEFAULT_PROPORTIONAL_MULTS
    else:
        proportional_mults = np.asarray(proportional_mults, dtype=np.float64)

    N = M_fft // 2
    f_work = np.array(f[:N], dtype=np.float64)
    f_padded = np.zeros(M_fft, dtype=np.float64)
    f_padded[:N] = f_work
    ac = np.array(autoconv, dtype=np.float64)

    integral_f = np.sum(f_work) * dx
    max_ac = np.max(ac)
    current_c = max_ac / (integral_f ** 2)

    n_improvements = 0
    accepts_since_recompute = 0
    accepts_since_hot_refresh = 0

    hot_set = _build_hot_set(ac)

    nonzero_indices = np.where(f_work > 0)[0]
    if verbose:
        import time
        print(f"  Hot set: {len(hot_set)}, nonzero: {len(nonzero_indices)}, C={current_c:.13f}")
        t0 = time.time()

    for count, i in enumerate(nonzero_indices):
        fi = f_work[i]
        i_int = int(i)

        # Build candidate deltas
        cand_list = list(delta_grid)
        if fi > 1e-15:
            for m in proportional_mults:
                cand_list.append(fi * m)
        if 0 < fi < zero_threshold:
            cand_list.append(-fi)
        candidates = np.array(cand_list, dtype=np.float64)

        # Filter: non-negativity, non-zero, positive integral
        new_fi = fi + candidates
        valid = (new_fi >= 0.0) & (candidates != 0.0)
        new_integrals = integral_f + candidates * dx
        valid &= (new_integrals > 0.0)
        candidates = candidates[valid]
        if len(candidates) == 0:
            continue
        new_integrals = new_integrals[valid]

        # Hot set screening: compute max within hot set for all candidates
        hot_cross = (hot_set - i_int) % M_fft
        shift_at_hot = f_padded[hot_cross]
        ac_at_hot = ac[hot_set]
        self_idx = (2 * i_int) % M_fft

        # Vectorized: (n_cand, n_hot)
        new_ac_hot = (ac_at_hot[None, :]
                      + 2.0 * candidates[:, None] * dx * shift_at_hot[None, :])
        si = np.searchsorted(hot_set, self_idx)
        if si < len(hot_set) and hot_set[si] == self_idx:
            new_ac_hot[:, si] += candidates ** 2 * dx

        max_hot = np.max(new_ac_hot, axis=1)

        # Also check self_idx (d^2 term could push it above hot set max)
        sc = (self_idx - i_int) % M_fft
        ac_self = (ac[self_idx]
                   + 2.0 * candidates * dx * f_padded[sc]
                   + candidates ** 2 * dx)
        max_hot = np.maximum(max_hot, ac_self)

        # Hot set C is a LOWER BOUND on true C
        c_hot = max_hot / (new_integrals ** 2)

        best_hot_idx = np.argmin(c_hot)

        # If hot-set C >= current_c, no candidate can improve (hot is lower bound)
        if c_hot[best_hot_idx] >= current_c:
            continue

        # Verify best candidate with full autoconv max
        best_delta = candidates[best_hot_idx]
        new_ac_full = incremental_update(ac, f_padded, i_int, best_delta, dx, M_fft)
        true_max = np.max(new_ac_full)
        true_c = true_max / (new_integrals[best_hot_idx] ** 2)

        if true_c < current_c:
            ac = new_ac_full
            f_padded[i_int] += best_delta
            f_work[i_int] += best_delta
            integral_f = new_integrals[best_hot_idx]
            max_ac = true_max
            current_c = true_c
            n_improvements += 1
            accepts_since_recompute += 1
            accepts_since_hot_refresh += 1

            if accepts_since_hot_refresh >= hot_set_refresh:
                hot_set = _build_hot_set(ac)
                accepts_since_hot_refresh = 0

            if accepts_since_recompute >= recompute_max_every:
                ac_ref, f_pad_ref, _, _ = _autoconvolve(f_work)
                drift = np.max(np.abs(ac - ac_ref))
                if drift > 1e-12:
                    ac = ac_ref
                    f_padded = f_pad_ref
                    max_ac = np.max(ac)
                    integral_f = np.sum(f_work) * dx
                    current_c = max_ac / (integral_f ** 2)
                    hot_set = _build_hot_set(ac)
                    if verbose:
                        print(f"    Resynced (drift={drift:.2e}), C={current_c:.13f}")
                accepts_since_recompute = 0

        if verbose and count > 0 and count % 5000 == 0:
            elapsed = time.time() - t0
            print(f"    {count}/{len(nonzero_indices)}, {n_improvements} impr, {elapsed:.1f}s")

    if verbose:
        elapsed = time.time() - t0
        print(f"  Round end: C={current_c:.13f}, {n_improvements} impr, {elapsed:.1f}s")

    return f_work, ac, n_improvements, current_c


def run_coordinate_descent(f, n_rounds=10, delta_grid=None, proportional_mults=None,
                            zero_threshold=1e-6, recompute_max_every=200,
                            hot_set_refresh=500, verbose=True):
    """Run multiple rounds of coordinate descent until convergence.

    Initializes autoconvolution via FFT, runs up to n_rounds full-array passes,
    stops early if a round produces 0 improvements. Verifies final C against
    FFT-based compute_c_f64.

    Args:
        f: 1D array-like. Starting solution. Converted to float64, clamped >= 0.
        n_rounds: int. Maximum full-array passes. Default 10.
        delta_grid: Absolute deltas. Default: standard grid (±1e-12 to ±1e-2).
        proportional_mults: Proportional deltas. Default: [±0.0001..±0.1].
        zero_threshold: float. Zeroing threshold. Default 1e-6.
        recompute_max_every: int. FFT resync frequency. Default 200.
        hot_set_refresh: int. Hot set rebuild frequency. Default 500.
        verbose: bool. Print per-round progress. Default True.

    Returns:
        f_final: 1D float64 array. Optimized solution.
        total_improvements: int. Total accepted moves across all rounds.
        c_history: list of float. C value after each round.

    Examples:
        >>> import numpy as np
        >>> rng = np.random.default_rng(42)
        >>> f = np.abs(rng.standard_normal(500)) * 0.1
        >>> f_opt, total, c_hist = run_coordinate_descent(f, n_rounds=3, verbose=False)
        >>> len(c_hist) <= 3
        True
        >>> all(c_hist[i] <= c_hist[i-1] + 1e-12 for i in range(1, len(c_hist)))
        True
    """
    from helpers.compute_c_f64 import compute_c_f64

    f = np.asarray(f, dtype=np.float64)
    N = len(f)
    f = np.maximum(f, 0.0)
    dx = 0.5 / N
    M_fft = 2 * N

    ac, _, _, _ = _autoconvolve(f)
    c_initial = compute_c_f64(f)
    if verbose:
        print(f"Coordinate descent: N={N}, initial C={c_initial:.13f}")

    f_current = f.copy()
    ac_current = ac.copy()
    total_improvements = 0
    c_history = []

    for rnd in range(1, n_rounds + 1):
        if verbose:
            print(f"Round {rnd}/{n_rounds}:")
        f_current, ac_current, n_impr, c_val = coordinate_descent_round(
            f_current, ac_current, dx, M_fft,
            delta_grid=delta_grid, proportional_mults=proportional_mults,
            zero_threshold=zero_threshold, recompute_max_every=recompute_max_every,
            hot_set_refresh=hot_set_refresh, verbose=verbose
        )
        total_improvements += n_impr
        c_history.append(c_val)
        if verbose:
            print(f"  -> C={c_val:.13f}, improvements={n_impr}, total={total_improvements}")
        if n_impr == 0:
            if verbose:
                print(f"Converged after {rnd} rounds")
            break

    c_verify = compute_c_f64(f_current)
    if verbose:
        print(f"Final (incr): {c_history[-1]:.13f}")
        print(f"Final (FFT):  {c_verify:.13f}")
        print(f"Diff: {abs(c_history[-1] - c_verify):.2e}")

    return f_current, total_improvements, c_history
