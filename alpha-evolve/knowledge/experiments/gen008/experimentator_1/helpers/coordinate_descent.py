"""Standardized coordinate descent for autocorrelation optimization.

Provides single-element coordinate descent using O(N) incremental autoconvolution
updates. Encapsulates the delta grid, accept/reject logic, non-negativity clamping,
and autoconv max tracking that were previously reimplemented by every exploit agent.

The standard delta grid is derived from the most successful run (gen007 exploit_1,
6551 improvements): logarithmic absolute deltas (1e-12 to 1e-2) plus proportional
deltas (0.01% to 10% of element value) plus zeroing for near-zero elements.

Performance: ~85s per round at N=30000 (25k nonzero elements, 24 delta trials each).
Convergence: typically 3-6 rounds to coordinate-wise local minimum.

Dependencies:
    - helpers.incremental_autoconv_update (incremental_update)
    - helpers.cross_convolution_f64 (autoconvolve)
    - helpers.compute_c_f64 (compute_c_f64, for periodic verification)
"""

import numpy as np

from helpers.incremental_autoconv_update import incremental_update
from helpers.cross_convolution_f64 import autoconvolve
from helpers.compute_c_f64 import compute_c_f64


# Standard delta grid: absolute deltas from 1e-12 to 1e-2 (positive and negative)
DEFAULT_DELTA_GRID = []
for _e in range(-12, -1):
    DEFAULT_DELTA_GRID.extend([10.0 ** _e, -(10.0 ** _e)])
DEFAULT_DELTA_GRID = np.array(DEFAULT_DELTA_GRID, dtype=np.float64)

# Proportional delta multipliers applied per-element: ±0.0001, ±0.001, ±0.01, ±0.1
_PROPORTIONAL_MULTIPLIERS = np.array(
    [0.0001, -0.0001, 0.001, -0.001, 0.01, -0.01, 0.1, -0.1],
    dtype=np.float64,
)


def coordinate_descent_round(f, autoconv=None, dx=None, M_fft=None,
                             delta_grid=None, skip_zero=True,
                             resync_interval=200):
    """One full-array pass of coordinate descent using incremental autoconv updates.

    For each nonzero element i, tries each delta in the delta grid plus
    proportional deltas (scaled by f[i]) and zeroing for small elements.
    Accepts the delta that gives the largest reduction in C = max(autoconv)/integral^2.

    Args:
        f: 1D numpy float64 array of non-negative function values, length N.
            Not modified in-place; a copy is made internally.
        autoconv: 1D numpy float64 array of length M_fft=2N, the current
            autoconvolution. If None, computed from f via autoconvolve().
        dx: Grid spacing (default 0.5/N).
        M_fft: FFT array length (default 2*N).
        delta_grid: 1D array of absolute delta values to try. Default:
            DEFAULT_DELTA_GRID (22 values from +-1e-12 to +-1e-2).
        skip_zero: If True (default), skip elements where f[i]==0.
        resync_interval: Recompute autoconv from FFT every this many accepted
            moves to prevent floating-point drift. Default 200.

    Returns:
        f_new: 1D numpy float64 array, the updated f.
        autoconv_new: 1D numpy float64 array, the updated autoconvolution.
        n_improvements: int, number of accepted moves.
        new_c: float, the C value after this round.

    Examples:
        >>> import numpy as np
        >>> rng = np.random.default_rng(42)
        >>> f = np.abs(rng.standard_normal(500)) * 0.1
        >>> f_new, ac_new, n_imp, c_new = coordinate_descent_round(f)
        >>> from helpers.compute_c_f64 import compute_c_f64
        >>> abs(c_new - compute_c_f64(f_new)) < 1e-10
        True
    """
    f = np.asarray(f, dtype=np.float64).copy()
    N = len(f)

    if dx is None:
        dx = 0.5 / N
    if M_fft is None:
        M_fft = 2 * N

    # Initialize autoconv if not provided
    if autoconv is None:
        autoconv, f_padded, dx, M_fft = autoconvolve(f)
    else:
        autoconv = np.asarray(autoconv, dtype=np.float64).copy()
        f_padded = np.pad(f, (0, N)).astype(np.float64)

    if delta_grid is None:
        delta_grid = DEFAULT_DELTA_GRID
    else:
        delta_grid = np.asarray(delta_grid, dtype=np.float64)

    current_max = np.max(autoconv)
    integral = np.sum(np.maximum(f, 0.0)) * dx
    current_c = current_max / (integral ** 2)
    n_improvements = 0

    for i in range(N):
        if skip_zero and f[i] == 0.0:
            continue

        fi = f[i]

        # Build candidate deltas for this element
        # 1) Absolute deltas from grid
        # 2) Proportional deltas: ±0.0001, ±0.001, ±0.01, ±0.1 times f[i]
        # 3) Zeroing: try setting f[i] = 0 for small elements
        candidates = list(delta_grid)

        if fi > 0:
            prop_deltas = _PROPORTIONAL_MULTIPLIERS * fi
            candidates.extend(prop_deltas)

        if fi > 0 and fi < 1e-6:
            candidates.append(-fi)  # try zeroing

        best_delta = 0.0
        best_c = current_c

        for delta in candidates:
            new_fi = fi + delta
            # Non-negativity: skip if result would be negative
            if new_fi < 0.0:
                continue
            # Skip no-ops
            if delta == 0.0:
                continue

            # Compute new autoconv via incremental update (doesn't modify arrays)
            new_autoconv = incremental_update(autoconv, f_padded, i, delta, dx, M_fft)
            new_max = np.max(new_autoconv)

            # C = max(autoconv) / integral^2; integral changes by delta*dx
            new_integral = integral + delta * dx
            if new_integral ** 2 < 1e-30:
                continue
            trial_c = new_max / (new_integral ** 2)

            if trial_c < best_c:
                best_delta = delta
                best_c = trial_c

        if best_delta != 0.0:
            # Accept the move
            autoconv = incremental_update(autoconv, f_padded, i, best_delta, dx, M_fft)
            f_padded[i] += best_delta
            f[i] += best_delta
            integral += best_delta * dx
            current_max = np.max(autoconv)
            current_c = best_c
            n_improvements += 1

            # Periodic resync to prevent drift
            if n_improvements % resync_interval == 0:
                autoconv_ref, f_padded_ref, _, _ = autoconvolve(f)
                autoconv = autoconv_ref
                f_padded = f_padded_ref
                current_max = np.max(autoconv)
                integral = np.sum(np.maximum(f, 0.0)) * dx
                current_c = current_max / (integral ** 2)

    new_c = current_c

    return f, autoconv, n_improvements, new_c


def run_coordinate_descent(f, n_rounds=10, delta_grid=None, verbose=True,
                           resync_interval=200):
    """Convenience wrapper: run multiple rounds of coordinate descent.

    Initializes autoconvolution via autoconvolve(), runs n_rounds of
    coordinate_descent_round, stops early if a round finds 0 improvements.

    Args:
        f: 1D array-like of non-negative function values. Not modified in-place.
        n_rounds: Maximum number of full-array passes. Default 10.
        delta_grid: Delta grid for coordinate_descent_round. Default: DEFAULT_DELTA_GRID.
        verbose: If True, print per-round statistics. Default True.
        resync_interval: FFT resync interval passed to each round. Default 200.

    Returns:
        f_final: 1D numpy float64 array, the optimized f.
        total_improvements: int, total accepted moves across all rounds.
        c_history: list of float, C value after each round (length = rounds run).

    Examples:
        >>> import numpy as np
        >>> rng = np.random.default_rng(42)
        >>> f = np.abs(rng.standard_normal(500)) * 0.1
        >>> f_final, total_imp, c_hist = run_coordinate_descent(f, n_rounds=3, verbose=False)
        >>> len(c_hist) <= 3
        True
        >>> all(c_hist[i] >= c_hist[i+1] - 1e-15 for i in range(len(c_hist)-1))
        True
    """
    f = np.asarray(f, dtype=np.float64).copy()
    N = len(f)
    dx = 0.5 / N
    M_fft = 2 * N

    # Initialize autoconvolution
    autoconv, f_padded, dx, M_fft = autoconvolve(f)

    c_history = []
    total_improvements = 0

    for r in range(n_rounds):
        f, autoconv, n_imp, c_val = coordinate_descent_round(
            f, autoconv=autoconv, dx=dx, M_fft=M_fft,
            delta_grid=delta_grid, resync_interval=resync_interval,
        )
        total_improvements += n_imp
        c_history.append(c_val)

        if verbose:
            print(f"  Round {r+1}: {n_imp} improvements, C = {c_val:.12f}")

        if n_imp == 0:
            if verbose:
                print(f"  Converged after {r+1} rounds (0 improvements)")
            break

    return f, total_improvements, c_history
