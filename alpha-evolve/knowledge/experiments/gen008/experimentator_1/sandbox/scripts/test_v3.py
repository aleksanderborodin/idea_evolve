"""Coordinate descent v3 — hot set for screening, full max for acceptance.

Fix: The hot set gives a LOWER BOUND on the new max. Use it to quickly
identify the most promising candidate, then verify with full np.max
before accepting. This is correct and fast: O(M) for hot set screening
of all candidates, plus O(M) for verification of the one best candidate.
"""

import numpy as np
import sys
import time

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

from helpers.incremental_autoconv_update import incremental_update
from helpers.compute_c_f64 import compute_c_f64


def autoconvolve_np(f):
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


def _build_hot_set(ac, epsilon_rel=1e-6):
    max_val = np.max(ac)
    threshold = max_val * (1.0 - epsilon_rel)
    return np.where(ac >= threshold)[0]


def coordinate_descent_round(f, autoconv, dx, M_fft, delta_grid=None,
                              proportional_mults=None, zero_threshold=1e-6,
                              recompute_max_every=200, hot_set_refresh=500,
                              verbose=False):
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
    accepts_since_hot_refresh = 0

    hot_set = _build_hot_set(ac)

    nonzero_indices = np.where(f_work > 0)[0]
    if verbose:
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

        new_ac_hot = ac_at_hot[None, :] + 2.0 * candidates[:, None] * dx * shift_at_hot[None, :]
        si = np.searchsorted(hot_set, self_idx)
        if si < len(hot_set) and hot_set[si] == self_idx:
            new_ac_hot[:, si] += candidates ** 2 * dx

        max_hot = np.max(new_ac_hot, axis=1)

        # Also check self_idx
        sc = (self_idx - i_int) % M_fft
        ac_self = ac[self_idx] + 2.0 * candidates * dx * f_padded[sc] + candidates ** 2 * dx
        max_hot = np.maximum(max_hot, ac_self)

        # Hot set C is a LOWER BOUND (true max >= hot max)
        c_hot = max_hot / (new_integrals ** 2)

        # Find best candidate by hot set screening
        best_hot_idx = np.argmin(c_hot)

        # Only proceed if hot-set C suggests improvement
        # (since hot max is a lower bound, if hot C >= current_c, true C >= current_c too)
        # Actually: hot max is a LOWER BOUND on true max, so hot C is a LOWER BOUND on true C.
        # If hot C >= current_c, true C >= current_c, so no improvement possible: SKIP.
        # If hot C < current_c, true C MIGHT be < current_c: VERIFY with full max.
        if c_hot[best_hot_idx] >= current_c:
            continue

        # Verify with full max
        best_delta = candidates[best_hot_idx]
        new_ac_full = incremental_update(ac, f_padded, i_int, best_delta, dx, M_fft)
        true_max = np.max(new_ac_full)
        new_int = new_integrals[best_hot_idx]
        true_c = true_max / (new_int ** 2)

        if true_c < current_c:
            # Accept
            ac = new_ac_full
            f_padded[i_int] += best_delta
            f_work[i_int] += best_delta
            integral_f = new_int
            max_ac = true_max
            current_c = true_c
            n_improvements += 1
            accepts_since_recompute += 1
            accepts_since_hot_refresh += 1

            if accepts_since_hot_refresh >= hot_set_refresh:
                hot_set = _build_hot_set(ac)
                accepts_since_hot_refresh = 0

            if accepts_since_recompute >= recompute_max_every:
                ac_ref, f_pad_ref, _, _ = autoconvolve_np(f_work)
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
    f = np.asarray(f, dtype=np.float64)
    N = len(f)
    f = np.maximum(f, 0.0)
    dx = 0.5 / N
    M_fft = 2 * N

    ac, _, _, _ = autoconvolve_np(f)
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


# === TESTS ===
print("=== Test 0: Small array correctness (3 rounds) ===")
rng = np.random.default_rng(42)
f_small = np.abs(rng.standard_normal(500)) * 0.1
c0 = compute_c_f64(f_small)
print(f"Initial C: {c0:.10f}")

f_opt, nimpr, chist = run_coordinate_descent(f_small, n_rounds=3, verbose=True)
# Verify C decreased monotonically
for i in range(1, len(chist)):
    assert chist[i] <= chist[i-1] + 1e-12, f"C increased: {chist[i-1]:.13f} -> {chist[i]:.13f}"
print("Monotonic decrease: PASS\n")

print("=== Test 1: 30k best solution ===")
import importlib.util
spec = importlib.util.spec_from_file_location("best", "/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen007/explore_1/sol01.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
f_best = mod.entrypoint()
print(f"N={len(f_best)}, C={compute_c_f64(f_best):.13f}")

f_out, ni, ch = run_coordinate_descent(f_best, n_rounds=1, verbose=True)
