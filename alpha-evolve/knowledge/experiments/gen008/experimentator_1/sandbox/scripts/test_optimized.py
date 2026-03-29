"""Optimized coordinate descent — avoid full-array max per candidate.

Key insight: the autoconvolution of well-optimized solutions has a very flat
plateau (~15k positions within 1e-10 of max for the 30k TTT-Discover array).
The max can shift but only within this plateau region. We track a "hot set"
of positions and only evaluate those.

Even better optimization: for each candidate delta d at element i, the change
to autoconv at position n is: 2*d*dx*f_padded[(n-i)%M] + d^2*dx*(n==2i%M)
The max of the new autoconv is max over n of (ac[n] + delta_ac[n]).
We can compute this without materializing the full array by using the hot set.
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

HOT_SET_EPSILON = 1e-6  # Positions within this fraction of max are tracked


def _build_hot_set(ac, epsilon_rel=HOT_SET_EPSILON):
    """Find positions near the autoconv max."""
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
    elems_since_hot_refresh = 0

    # Build hot set: positions near the max of autoconv
    hot_set = _build_hot_set(ac)
    if verbose:
        print(f"  Hot set size: {len(hot_set)}")

    nonzero_indices = np.where(f_work > 0)[0]
    if verbose:
        print(f"  Round start: C={current_c:.13f}, {len(nonzero_indices)} nonzero")
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

        # Filter valid
        new_fi = fi + candidates
        valid = (new_fi >= 0.0) & (candidates != 0.0)
        new_integrals = integral_f + candidates * dx
        valid &= (new_integrals > 0.0)
        candidates = candidates[valid]
        if len(candidates) == 0:
            continue
        new_integrals = new_integrals[valid]

        # Compute shift pattern ONLY at hot set positions
        hot_cross = (hot_set - i_int) % M_fft
        shift_at_hot = f_padded[hot_cross]  # shape (n_hot,)
        ac_at_hot = ac[hot_set]  # shape (n_hot,)

        self_idx = (2 * i_int) % M_fft

        # For each candidate: new_ac_at_hot = ac_at_hot + 2*d*dx*shift_at_hot
        # Plus self-term if self_idx is in hot_set
        # shape: (n_cand, n_hot)
        new_ac_hot = ac_at_hot[np.newaxis, :] + 2.0 * candidates[:, np.newaxis] * dx * shift_at_hot[np.newaxis, :]

        # Self-term correction
        self_in_hot = np.searchsorted(hot_set, self_idx)
        if self_in_hot < len(hot_set) and hot_set[self_in_hot] == self_idx:
            new_ac_hot[:, self_in_hot] += candidates ** 2 * dx

        # Max within hot set for each candidate
        max_hot = np.max(new_ac_hot, axis=1)

        # Also check self_idx even if not in hot set (the d^2 term could push it up)
        # ac[self_idx] + 2*d*dx*f_padded[0 if self_idx==2i else ...] + d^2*dx
        # Actually need to check: new_ac at self_idx
        self_cross = (self_idx - i_int) % M_fft
        ac_at_self = ac[self_idx] + 2.0 * candidates * dx * f_padded[self_cross] + candidates ** 2 * dx
        max_hot = np.maximum(max_hot, ac_at_self)

        c_batch = max_hot / (new_integrals ** 2)

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

            # Refresh hot set periodically
            elems_since_hot_refresh += 1
            if elems_since_hot_refresh >= hot_set_refresh:
                hot_set = _build_hot_set(ac)
                elems_since_hot_refresh = 0

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


# === TESTS ===

print("=== Test 0: Small array (N=500) correctness ===")
rng = np.random.default_rng(42)
f_small = np.abs(rng.standard_normal(500)) * 0.1
c0 = compute_c_f64(f_small)
print(f"Initial C: {c0:.10f}")

ac0, fp0, dx0, M0 = autoconvolve_np(f_small)
f1, ac1, ni1, c1 = coordinate_descent_round(f_small, ac0, dx0, M0, verbose=True)
c_v1 = compute_c_f64(f1)
print(f"C incr: {c1:.13f}, C verify: {c_v1:.13f}, diff: {abs(c1-c_v1):.2e}")
assert abs(c1 - c_v1) < 1e-10, f"Drift too large: {abs(c1-c_v1)}"
print("PASS\n")

print("=== Test 0b: Round 2 ===")
f2, ac2, ni2, c2 = coordinate_descent_round(f1, ac1, dx0, M0, verbose=True)
c_v2 = compute_c_f64(f2)
print(f"C incr: {c2:.13f}, C verify: {c_v2:.13f}, diff: {abs(c2-c_v2):.2e}")
assert abs(c2 - c_v2) < 1e-10
print("PASS\n")

print("=== Test 1: 30k timing estimate ===")
import importlib.util
spec = importlib.util.spec_from_file_location("best", "/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen007/explore_1/sol01.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
f_best = mod.entrypoint()
c_best = compute_c_f64(f_best)
print(f"N={len(f_best)}, C={c_best:.13f}, nonzero={np.sum(f_best > 0)}")

ac_best, fp_best, dx_best, M_best = autoconvolve_np(f_best)
hot = _build_hot_set(ac_best)
print(f"Hot set size: {len(hot)} (of {M_best})")

# Time 200 elements
nz = np.where(f_best > 0)[0]
t0 = time.time()
for idx in nz[:200]:
    i_int = int(idx)
    hot_cross = (hot - i_int) % M_best
    shift_at_hot = fp_best[hot_cross]
    ac_at_hot = ac_best[hot]
    candidates = np.random.randn(30) * 0.001
    new_ac_hot = ac_at_hot[np.newaxis, :] + 2.0 * candidates[:, np.newaxis] * dx_best * shift_at_hot[np.newaxis, :]
    max_hot = np.max(new_ac_hot, axis=1)
t1 = time.time()
per_elem = (t1 - t0) / 200
est_total = per_elem * len(nz)
print(f"Per element: {per_elem*1000:.2f}ms, est total: {est_total:.0f}s")

if est_total < 300:
    print("\nRunning full round on best solution...")
    f_out, ac_out, ni_out, c_out = coordinate_descent_round(
        f_best, ac_best, dx_best, M_best, verbose=True)
    c_v = compute_c_f64(f_out)
    print(f"Improvements: {ni_out}")
    print(f"C verify diff: {abs(c_out - c_v):.2e}")
else:
    print(f"Est {est_total:.0f}s too long, testing with smaller subset...")
    # Test on first 1000 nonzero elements only
    f_test = f_best.copy()
    nz_test = nz[:1000]
    f_sub = f_test.copy()
    ac_sub = ac_best.copy()
    fp_sub = fp_best.copy()
    integral = np.sum(f_sub) * dx_best
    max_ac_sub = np.max(ac_sub)
    current_c = max_ac_sub / (integral ** 2)
    nimpr = 0
    t0 = time.time()
    for idx in nz_test:
        i_int = int(idx)
        fi = f_sub[i_int]
        cands = DEFAULT_ABSOLUTE_DELTAS.copy()
        prop = fi * DEFAULT_PROPORTIONAL_MULTS
        cands = np.concatenate([cands, prop])
        new_fi = fi + cands
        valid = (new_fi >= 0) & (cands != 0)
        ni_ = integral + cands * dx_best
        valid &= (ni_ > 0)
        cands = cands[valid]
        ni_ = ni_[valid]
        if len(cands) == 0:
            continue
        hot_cross = (hot - i_int) % M_best
        shift_hot = fp_sub[hot_cross]
        ac_hot = ac_sub[hot]
        new_ac = ac_hot[None, :] + 2.0 * cands[:, None] * dx_best * shift_hot[None, :]
        self_idx = (2 * i_int) % M_best
        si = np.searchsorted(hot, self_idx)
        if si < len(hot) and hot[si] == self_idx:
            new_ac[:, si] += cands ** 2 * dx_best
        max_h = np.max(new_ac, axis=1)
        sc = (self_idx - i_int) % M_best
        ac_self = ac_sub[self_idx] + 2.0 * cands * dx_best * fp_sub[sc] + cands ** 2 * dx_best
        max_h = np.maximum(max_h, ac_self)
        c_batch = max_h / (ni_ ** 2)
        bi = np.argmin(c_batch)
        if c_batch[bi] < current_c:
            bd = cands[bi]
            ac_sub = incremental_update(ac_sub, fp_sub, i_int, bd, dx_best, M_best)
            fp_sub[i_int] += bd
            f_sub[i_int] += bd
            integral += bd * dx_best
            max_ac_sub = np.max(ac_sub)
            current_c = max_ac_sub / (integral ** 2)
            nimpr += 1
    t1 = time.time()
    c_vv = compute_c_f64(f_sub)
    print(f"1000 elements: {nimpr} impr, {t1-t0:.1f}s, C diff: {abs(current_c-c_vv):.2e}")
    print(f"Rate: {(t1-t0)/1000*1000:.2f}ms/elem -> full round est: {(t1-t0)/1000*25144:.0f}s")
