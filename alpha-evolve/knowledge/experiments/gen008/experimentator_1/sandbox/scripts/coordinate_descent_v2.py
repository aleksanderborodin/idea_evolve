"""Optimized coordinate descent v2 — vectorized candidate evaluation.

Key optimization: For each element i, compute all candidate deltas' effects
on C in a vectorized way, avoiding per-candidate full-array operations.

For element i with delta d, the new autoconv is:
    new_ac[n] = ac[n] + 2*d*dx*f_padded[(n-i)%M]  + d^2*dx*(n==2i%M)

The max of the new autoconv determines the new C. Instead of computing the
full new_ac for each candidate d, we:
1. Compute the "shift pattern" s[n] = f_padded[(n-i)%M] once per element (O(M))
2. For each candidate d: new_max = max(ac[n] + 2*d*dx*s[n]) + correction at 2i%M
   This is still O(M) per candidate, but we can vectorize across candidates.

Actually, the REAL optimization is: compute ac + 2*d*dx*s for ALL candidates
at once using broadcasting: shape (n_candidates, M). Then max along axis=1.
"""

import numpy as np
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'problem'))

from helpers.incremental_autoconv_update import incremental_update
from helpers.cross_convolution_f64 import autoconvolve
from helpers.compute_c_f64 import compute_c_f64


def _build_default_delta_grid():
    grid = []
    for e in range(-12, -1):
        grid.append(10.0 ** e)
        grid.append(-(10.0 ** e))
    return np.array(grid, dtype=np.float64)


DEFAULT_ABSOLUTE_DELTAS = _build_default_delta_grid()
DEFAULT_PROPORTIONAL_MULTS = np.array([0.0001, -0.0001, 0.001, -0.001, 0.01, -0.01, 0.1, -0.1], dtype=np.float64)


def coordinate_descent_round(f, autoconv, dx, M_fft, delta_grid=None,
                              proportional_mults=None, zero_threshold=1e-6,
                              recompute_max_every=100, verbose=False):
    """One full-array pass of coordinate descent using incremental autoconv update.

    Optimized: for each element, vectorize candidate evaluation across all deltas.
    """
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

    nonzero_indices = np.where(f_work > 0)[0]
    if verbose:
        print(f"  Round start: C={current_c:.13f}, {len(nonzero_indices)} nonzero elements")
        t0 = time.time()

    n_arr = np.arange(M_fft, dtype=np.int64)

    for count, i in enumerate(nonzero_indices):
        fi = f_work[i]
        i_int = int(i)

        # Build all candidate deltas for this element
        candidates = list(delta_grid)
        if fi > 1e-15:
            candidates.extend(fi * proportional_mults)
        if 0 < fi < zero_threshold:
            candidates.append(-fi)

        candidates = np.array(candidates, dtype=np.float64)

        # Filter: new_fi = fi + delta >= 0, delta != 0, new_integral > 0
        new_fi = fi + candidates
        valid = (new_fi >= 0.0) & (candidates != 0.0)
        new_integral = integral_f + candidates * dx
        valid &= (new_integral > 0.0)

        candidates = candidates[valid]
        if len(candidates) == 0:
            continue
        new_integral = integral_f + candidates * dx

        # Compute shift pattern once: s[n] = f_padded[(n - i) % M]
        cross_indices = (n_arr - i_int) % M_fft
        shift_pattern = f_padded[cross_indices]  # shape (M_fft,)

        # For each candidate d, new_ac[n] = ac[n] + 2*d*dx*shift_pattern[n]
        # The max of new_ac determines new C.
        # Self-term correction at index (2*i) % M_fft: += d^2*dx
        self_idx = (2 * i_int) % M_fft

        # Vectorized: compute max(ac + 2*d*dx*shift_pattern) for all d at once
        # Instead of materializing (n_cand, M_fft), iterate smartly
        # For each candidate, max_new_ac = max(ac + 2*d*dx*s)
        # = max over n of (ac[n] + 2*d*dx*s[n])
        # The self-term d^2*dx at self_idx is typically tiny, handle as correction

        best_delta = 0.0
        best_c = current_c

        # Group by sign to avoid redundant work: for d>0, max might be at
        # argmax(ac + 2*d*dx*s) which depends on s values.
        # Unfortunately we can't avoid O(M) per candidate without more structure.
        # But we can vectorize the inner loop with batched numpy operations.

        # Batch approach: process candidates in chunks to limit memory
        CHUNK = min(len(candidates), 64)
        for start in range(0, len(candidates), CHUNK):
            end = min(start + CHUNK, len(candidates))
            d_batch = candidates[start:end]  # shape (batch,)
            ni_batch = new_integral[start:end]  # shape (batch,)

            # new_ac_batch[b, n] = ac[n] + 2*d_batch[b]*dx*shift_pattern[n]
            # shape: (batch, M_fft) -- could be large for M_fft=60000
            # At 64 candidates * 60000 * 8 bytes = ~30MB per batch. Acceptable.
            new_ac_batch = ac[np.newaxis, :] + 2.0 * d_batch[:, np.newaxis] * dx * shift_pattern[np.newaxis, :]
            # Add self-term
            new_ac_batch[:, self_idx] += d_batch ** 2 * dx

            # Max along axis=1
            max_batch = np.max(new_ac_batch, axis=1)  # shape (batch,)
            c_batch = max_batch / (ni_batch ** 2)

            best_in_batch = np.argmin(c_batch)
            if c_batch[best_in_batch] < best_c:
                best_c = c_batch[best_in_batch]
                best_delta = d_batch[best_in_batch]

        if best_delta != 0.0:
            ac = incremental_update(ac, f_padded, i_int, best_delta, dx, M_fft)
            f_padded[i_int] += best_delta
            f_work[i_int] += best_delta
            integral_f += best_delta * dx
            max_ac = np.max(ac)
            current_c = max_ac / (integral_f ** 2)
            n_improvements += 1
            accepts_since_recompute += 1

            if accepts_since_recompute >= recompute_max_every:
                ac_ref, f_pad_ref, _, _ = autoconvolve(f_work)
                drift = np.max(np.abs(ac - ac_ref))
                if drift > 1e-12:
                    ac = ac_ref
                    f_padded = f_pad_ref
                    max_ac = np.max(ac)
                    integral_f = np.sum(f_work) * dx
                    current_c = max_ac / (integral_f ** 2)
                    if verbose:
                        print(f"    Resynced (drift={drift:.2e}), C={current_c:.13f}")
                accepts_since_recompute = 0

        if verbose and count > 0 and count % 5000 == 0:
            elapsed = time.time() - t0
            print(f"    {count}/{len(nonzero_indices)} elements, {n_improvements} impr, {elapsed:.0f}s")

    if verbose:
        elapsed = time.time() - t0
        print(f"  Round end: C={current_c:.13f}, {n_improvements} improvements, {elapsed:.0f}s")

    return f_work, ac, n_improvements, current_c


def run_coordinate_descent(f, n_rounds=10, delta_grid=None, proportional_mults=None,
                            zero_threshold=1e-6, recompute_max_every=100, verbose=True):
    """Convenience wrapper: initialize autoconv, run n_rounds, stop early if converged."""
    f = np.asarray(f, dtype=np.float64)
    N = len(f)
    f = np.maximum(f, 0.0)
    dx = 0.5 / N
    M_fft = 2 * N

    ac, _, _, _ = autoconvolve(f)
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
            verbose=verbose
        )
        total_improvements += n_impr
        c_history.append(c_val)
        if verbose:
            print(f"  -> C={c_val:.13f}, improvements={n_impr}, total={total_improvements}")
        if n_impr == 0:
            if verbose:
                print(f"Converged after {rnd} rounds (0 improvements)")
            break

    c_verify = compute_c_f64(f_current)
    if verbose:
        c_diff = abs(c_history[-1] - c_verify)
        print(f"Final C (incremental): {c_history[-1]:.13f}")
        print(f"Final C (FFT verify):  {c_verify:.13f}")
        print(f"Difference: {c_diff:.2e}")

    return f_current, total_improvements, c_history


if __name__ == "__main__":
    import importlib.util

    # Quick test with small array first
    print("=== Test 0: Small array sanity check ===")
    rng = np.random.default_rng(42)
    f_small = np.abs(rng.standard_normal(500)) * 0.1
    c0 = compute_c_f64(f_small)
    print(f"Initial C: {c0:.10f}")
    f_opt, nimpr, chist = run_coordinate_descent(f_small, n_rounds=3, verbose=True)
    c_final = compute_c_f64(f_opt)
    print(f"Verify diff: {abs(chist[-1] - c_final):.2e}")
    print()

    # Test with the 30k best solution (should find ~0 improvements)
    print("=== Test 1: Best solution (30k, should find ~0 improvements) ===")
    spec = importlib.util.spec_from_file_location("best", "population/gen007/explore_1/sol01.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    f_best = mod.entrypoint()
    print(f"N={len(f_best)}, C={compute_c_f64(f_best):.13f}")
    # Only run 1 round
    f_out, ni, ch = run_coordinate_descent(f_best, n_rounds=1, verbose=True)

    # Test with less-optimized 30k solution
    print("\n=== Test 2: Research_1 (30k, slightly less optimized) ===")
    spec2 = importlib.util.spec_from_file_location("res", "population/gen004/research_1/sol01.py")
    mod2 = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(mod2)
    f_res = mod2.entrypoint()
    print(f"N={len(f_res)}, C={compute_c_f64(f_res):.13f}")
    f_out2, ni2, ch2 = run_coordinate_descent(f_res, n_rounds=2, verbose=True)
