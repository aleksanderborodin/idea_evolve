"""Quick test with small arrays only — no JAX imports."""

import numpy as np
import sys
import os
import time

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

from helpers.incremental_autoconv_update import incremental_update
from helpers.compute_c_f64 import compute_c_f64


def autoconvolve_np(f):
    """Simple autoconvolve without importing cross_convolution_f64 (avoids JAX)."""
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
    grid = []
    for e in range(-12, -1):
        grid.append(10.0 ** e)
        grid.append(-(10.0 ** e))
    return np.array(grid, dtype=np.float64)


DEFAULT_ABSOLUTE_DELTAS = _build_default_delta_grid()
DEFAULT_PROPORTIONAL_MULTS = np.array([0.0001, -0.0001, 0.001, -0.001, 0.01, -0.01, 0.1, -0.1])


def coordinate_descent_round(f, autoconv, dx, M_fft, delta_grid=None,
                              proportional_mults=None, zero_threshold=1e-6,
                              recompute_max_every=100, verbose=False):
    if delta_grid is None:
        delta_grid = DEFAULT_ABSOLUTE_DELTAS
    if proportional_mults is None:
        proportional_mults = DEFAULT_PROPORTIONAL_MULTS

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
    n_arr = np.arange(M_fft, dtype=np.int64)

    nonzero_indices = np.where(f_work > 0)[0]
    if verbose:
        print(f"  Round start: C={current_c:.13f}, {len(nonzero_indices)} nonzero")
        t0 = time.time()

    for count, i in enumerate(nonzero_indices):
        fi = f_work[i]
        i_int = int(i)

        # Build candidate deltas
        candidates = list(delta_grid)
        if fi > 1e-15:
            for m in proportional_mults:
                candidates.append(fi * m)
        if 0 < fi < zero_threshold:
            candidates.append(-fi)
        candidates = np.array(candidates, dtype=np.float64)

        # Filter valid candidates
        new_fi = fi + candidates
        valid = (new_fi >= 0.0) & (candidates != 0.0)
        new_integrals = integral_f + candidates * dx
        valid &= (new_integrals > 0.0)
        candidates = candidates[valid]
        if len(candidates) == 0:
            continue
        new_integrals = new_integrals[valid]

        # Shift pattern
        cross_indices = (n_arr - i_int) % M_fft
        shift_pattern = f_padded[cross_indices]
        self_idx = (2 * i_int) % M_fft

        # Vectorized: (n_cand, M_fft)
        new_ac_batch = ac[np.newaxis, :] + 2.0 * candidates[:, np.newaxis] * dx * shift_pattern[np.newaxis, :]
        new_ac_batch[:, self_idx] += candidates ** 2 * dx
        max_batch = np.max(new_ac_batch, axis=1)
        c_batch = max_batch / (new_integrals ** 2)

        best_idx = np.argmin(c_batch)
        if c_batch[best_idx] < current_c:
            best_delta = candidates[best_idx]
            ac = incremental_update(ac, f_padded, i_int, best_delta, dx, M_fft)
            f_padded[i_int] += best_delta
            f_work[i_int] += best_delta
            integral_f += best_delta * dx
            max_ac = np.max(ac)
            current_c = max_ac / (integral_f ** 2)
            n_improvements += 1
            accepts_since_recompute += 1

            if accepts_since_recompute >= recompute_max_every:
                ac_ref, f_pad_ref, _, _ = autoconvolve_np(f_work)
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

        if verbose and count > 0 and count % 2000 == 0:
            elapsed = time.time() - t0
            print(f"    {count}/{len(nonzero_indices)}, {n_improvements} impr, {elapsed:.1f}s")

    if verbose:
        elapsed = time.time() - t0
        print(f"  Round end: C={current_c:.13f}, {n_improvements} impr, {elapsed:.1f}s")

    return f_work, ac, n_improvements, current_c


print("=== Test 0: Small array (N=500) ===")
rng = np.random.default_rng(42)
f_small = np.abs(rng.standard_normal(500)) * 0.1
c0 = compute_c_f64(f_small)
print(f"Initial C: {c0:.10f}")

ac0, fp0, dx0, M0 = autoconvolve_np(f_small)
t0 = time.time()
f1, ac1, ni, c1 = coordinate_descent_round(f_small, ac0, dx0, M0, verbose=True)
t1 = time.time()
print(f"Time: {t1-t0:.1f}s, improvements: {ni}")

c_verify = compute_c_f64(f1)
print(f"C incremental: {c1:.13f}")
print(f"C verify:      {c_verify:.13f}")
print(f"Diff:          {abs(c1 - c_verify):.2e}")

# Round 2
print("\nRound 2:")
f2, ac2, ni2, c2 = coordinate_descent_round(f1, ac1, dx0, M0, verbose=True)
c_verify2 = compute_c_f64(f2)
print(f"Verify diff: {abs(c2 - c_verify2):.2e}")

print("\n=== Test 1: 30k best solution (1 round, expect ~0 improvements) ===")
import importlib.util
spec = importlib.util.spec_from_file_location("best", "/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen007/explore_1/sol01.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
f_best = mod.entrypoint()
c_best = compute_c_f64(f_best)
print(f"N={len(f_best)}, C={c_best:.13f}")
print(f"Nonzero: {np.sum(f_best > 0)}")

# Time estimate: try 100 elements first
ac_best, fp_best, dx_best, M_best = autoconvolve_np(f_best)
nz = np.where(f_best > 0)[0]

print(f"Timing 100 elements...")
t0 = time.time()
# Manual mini-test
n_arr = np.arange(M_best, dtype=np.int64)
for idx in nz[:100]:
    i_int = int(idx)
    cross_indices = (n_arr - i_int) % M_best
    shift_pattern = fp_best[cross_indices]
    # Simulate 30 candidates
    candidates = np.random.randn(30) * 0.001
    new_ac_batch = ac_best[np.newaxis, :] + 2.0 * candidates[:, np.newaxis] * dx_best * shift_pattern[np.newaxis, :]
    max_batch = np.max(new_ac_batch, axis=1)

t1 = time.time()
per_elem = (t1 - t0) / 100
est_total = per_elem * len(nz)
print(f"Per element: {per_elem*1000:.1f}ms, estimated total for {len(nz)} elements: {est_total:.0f}s")

if est_total < 600:
    print("Running full round...")
    f_out, ac_out, ni_out, c_out = coordinate_descent_round(f_best, ac_best, dx_best, M_best, verbose=True)
    c_v = compute_c_f64(f_out)
    print(f"Improvements: {ni_out}, verify diff: {abs(c_out - c_v):.2e}")
else:
    print(f"Would take ~{est_total:.0f}s, skipping full round")
