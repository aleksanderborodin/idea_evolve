# fitness: 1.5028628681659377
# Method: Minimax multi-element perturbation (idea_023) + ultra-fine CD polish
# Addresses the 13-plateau limitation of standard single-peak gradient perturbation
import numpy as np
import sys
import time
import importlib.util

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

from scipy.optimize import linprog
from helpers.incremental_autoconv_update import incremental_update
from helpers.compute_c_f64 import compute_c_f64
from helpers.cross_convolution_f64 import autoconvolve


def _load_best():
    best_path = "/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen009/exploit_1/sol01.py"
    spec = importlib.util.spec_from_file_location("best_sol", best_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return np.array(mod.entrypoint(), dtype=np.float64)


def _get_plateau(autoconv, eps=1e-12):
    max_ac = np.max(autoconv)
    return np.where(autoconv >= max_ac * (1 - eps))[0], max_ac


def _minimax_lp(plateau_pos, g_list, step_size, k):
    """
    Solve minimax LP for a k-plet.
    Variables: [t, d1, ..., d_{k-1}]  (dk = -(d1+...+d_{k-1}))
    g_list: list of k arrays, each shape (K,), where g_list[l][p] = f_padded[(p-il)%M]
    Returns: (t_star, deltas) or None if LP fails.
    """
    K = len(plateau_pos)
    n_free = k - 1  # free variables
    n_vars = 1 + n_free  # [t, d1, ..., d_{n_free}]

    # delta_ac[p] = 2*dx * sum_{l=0}^{k-2}(d_l*(g_list[l][p]-g_list[k-1][p]))
    # scaled: we fold dx into g
    gk = g_list[k - 1]  # shape (K,)
    h = np.array([g_list[l] - gk for l in range(k - 1)])  # (n_free, K)

    # Plateau constraints: h[:,p] . d - t <= 0  for all p
    # A_ub[p] = [-1, h[0,p], h[1,p], ...]
    A_plateau = np.column_stack([-np.ones(K), h.T])  # (K, n_vars)

    # Sum constraint: |d1+...+d_{n_free}| <= step_size (so dk is in range)
    sum_row_pos = np.zeros(n_vars); sum_row_pos[1:] = 1.0
    sum_row_neg = np.zeros(n_vars); sum_row_neg[1:] = -1.0
    A_sum = np.vstack([sum_row_pos, sum_row_neg])  # (2, n_vars)
    b_sum = np.array([step_size, step_size])

    A_ub = np.vstack([A_plateau, A_sum])
    b_ub = np.concatenate([np.zeros(K), b_sum])
    c_lp = np.zeros(n_vars); c_lp[0] = 1.0

    # Bounds: t unbounded above 0 (we want t<0), di in [-step_size, step_size]
    bounds = [(None, 0.0)] + [(-step_size, step_size)] * n_free

    res = linprog(c_lp, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    if res.status != 0 or res.x is None:
        return None

    t_star = res.x[0]
    d_free = res.x[1:]
    d_last = -np.sum(d_free)
    deltas = np.concatenate([d_free, [d_last]])
    return t_star, deltas


def _minimax_trials(f, autoconv, f_padded, dx, M_fft, integral_sq,
                    k, n_trials, step_sizes, rng, deadline):
    """Generic minimax k-plet perturbation trials."""
    N = M_fft // 2
    improvements = 0
    tried = 0
    plateau_pos, max_ac = _get_plateau(autoconv)
    K_cur = len(plateau_pos)
    current_C = max_ac / integral_sq

    for trial in range(n_trials):
        if time.time() > deadline:
            break
        tried += 1
        step_size = step_sizes[rng.integers(len(step_sizes))]

        # Sample k indices (mix S0/S1)
        if rng.random() < 0.5:
            probs = np.maximum(f, 0.0)
            s = probs.sum()
            if s < 1e-30:
                indices = rng.integers(0, N, size=k)
            else:
                probs = probs / s
                indices = rng.choice(N, size=k, p=probs, replace=False)
        else:
            indices = rng.integers(0, N, size=k)

        # Precompute gradients at plateau positions for each element
        g_list = [f_padded[(plateau_pos - indices[l]) % M_fft] for l in range(k)]

        result = _minimax_lp(plateau_pos, g_list, step_size, k)
        if result is None:
            continue
        t_star, deltas = result
        if t_star >= -1e-18:
            continue

        # Scale deltas by 2*dx (we passed raw f_padded values, need to include factor)
        # delta_ac[p] = 2*dx * h[p] . d  — factor already in h = g_list differences
        # But we forgot to include 2*dx in the LP! Fix: deltas from LP are in "2*dx" units
        # Actually let's recheck: we passed g = f_padded values directly without the 2*dx factor
        # The LP minimizes t s.t. h.T @ d <= t, where h = g_list diffs (no 2*dx)
        # But the actual delta_ac = 2*dx * h.T @ d
        # So LP t_star is in units where 2*dx is missing. True improvement:
        #   true_delta_max_ac = 2*dx * t_star
        # This means if t_star < 0, true delta < 0 only if 2*dx*t_star < 0, which is same sign.
        # OK so the improvement direction is still valid. But the actual deltas from LP
        # are the ones to apply (they satisfy the step_size box constraint as given).
        # The LP correctly minimizes t s.t. sum_p g_diff[p].d <= t with box constraints.
        # Actual delta_ac[p] = 2*dx * g_diff[p].d = 2*dx * t_star at optimum.
        # So t_star < 0 still means improvement. Good.

        # Non-negativity check
        if any(f[indices[l]] + deltas[l] < 0 for l in range(k)):
            continue

        # Exact incremental evaluation
        fp_tmp = f_padded.copy()
        new_ac = autoconv.copy()
        for l in range(k):
            new_ac = incremental_update(new_ac, fp_tmp, int(indices[l]), deltas[l], dx, M_fft)
            fp_tmp[int(indices[l])] += deltas[l]

        new_int = np.sum(fp_tmp[:N]) * dx
        if new_int < 1e-15:
            continue
        new_C = np.max(new_ac) / (new_int * new_int)

        if new_C < current_C:
            for l in range(k):
                f[int(indices[l])] += deltas[l]
                f_padded[int(indices[l])] += deltas[l]
            autoconv[:] = new_ac
            integral_sq = new_int * new_int
            current_C = new_C
            improvements += 1
            plateau_pos, _ = _get_plateau(autoconv)

    return f, autoconv, f_padded, integral_sq, improvements, tried


def _fast_cd_round(f, autoconv, f_padded, dx, M_fft, integral, deltas, deadline):
    """
    Fast coordinate descent using window-based evaluation (O(window) per trial).
    Returns (f, autoconv, f_padded, integral, n_improvements).
    """
    N = M_fft // 2
    window_half = 400  # ±400 positions around each tight index
    improvements = 0

    # Find tight indices and build evaluation window
    max_ac = np.max(autoconv)
    tight_eps = 1e-10
    tight_idx = np.where(autoconv >= max_ac * (1 - tight_eps))[0]
    off = np.arange(-window_half, window_half + 1, dtype=np.int64)
    win_candidates = (tight_idx[:, None] + off[None, :]).ravel()
    window = np.unique(np.clip(win_candidates, 0, M_fft - 1))
    ac_window = autoconv[window].copy()
    current_max = np.max(ac_window)
    integral_sq = integral * integral
    current_C = current_max / integral_sq

    perm = np.random.permutation(N)
    for idx in perm:
        if time.time() > deadline:
            break

        # Precompute cross values at window positions for this element
        cross_w = f_padded[(window - idx) % M_fft]  # shape (|window|,)
        self_w_mask = (window == (2 * idx) % M_fft)  # for self term

        best_delta = None
        best_C = current_C

        for d_mag in deltas:
            for sign in (1.0, -1.0):
                d = sign * d_mag
                new_val = f[idx] + d
                if new_val < 0:
                    continue

                # Window-based delta_ac
                dac_w = 2.0 * dx * d * cross_w
                dac_w[self_w_mask] += d * d * dx
                new_win = ac_window + dac_w
                new_max = np.max(new_win)

                new_int = integral + d * dx
                if new_int < 1e-15:
                    continue
                new_C_trial = new_max / (new_int * new_int)

                if new_C_trial < best_C:
                    best_C = new_C_trial
                    best_delta = d

        if best_delta is not None:
            # Exact verification
            new_ac_exact = incremental_update(autoconv, f_padded, idx, best_delta, dx, M_fft)
            new_int = integral + best_delta * dx
            exact_C = np.max(new_ac_exact) / (new_int * new_int)

            if exact_C < current_C:
                autoconv[:] = new_ac_exact
                f[idx] += best_delta
                f_padded[idx] += best_delta
                integral = new_int
                integral_sq = integral * integral
                current_C = exact_C
                improvements += 1

                # Refresh window
                max_ac = np.max(autoconv)
                tight_idx = np.where(autoconv >= max_ac * (1 - tight_eps))[0]
                win_candidates = (tight_idx[:, None] + off[None, :]).ravel()
                window = np.unique(np.clip(win_candidates, 0, M_fft - 1))
                ac_window = autoconv[window].copy()
                current_max = np.max(ac_window)

    return f, autoconv, f_padded, integral, improvements


def entrypoint():
    _DEADLINE = time.time() + 500
    rng = np.random.default_rng(42)

    # --- Load best solution ---
    print("Loading best solution...")
    f = _load_best()
    f = np.maximum(f, 0.0)

    N = len(f)
    autoconv, f_padded, dx, M_fft = autoconvolve(f)
    integral = np.sum(f_padded[:N]) * dx
    integral_sq = integral * integral
    C_start = np.max(autoconv) / integral_sq
    print(f"N={N}, Start C = {C_start:.16f}")

    # --- Analyze plateau structure ---
    plateau_pos, max_ac = _get_plateau(autoconv, eps=1e-12)
    K = len(plateau_pos)
    print(f"Plateau: K={K} positions within 1e-12 of max_ac={max_ac:.16f}")
    print(f"  Indices: {plateau_pos}")
    print(f"  Values: {autoconv[plateau_pos]}")

    # Also check with 1e-10 for context
    plateau_pos_10, _ = _get_plateau(autoconv, eps=1e-10)
    print(f"  K={len(plateau_pos_10)} positions within 1e-10 of max")

    # Use 1e-10 plateau for better minimax coverage
    plateau_pos = plateau_pos_10

    # --- Minimax triplet perturbation ---
    step_sizes_trip = np.array([1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6, 3e-7, 1e-7])
    trip_deadline = min(_DEADLINE - 100, time.time() + 220)

    print(f"\n--- Minimax triplet perturbation (~220s budget) ---")
    t0 = time.time()
    f, autoconv, f_padded, integral_sq, n_imp_trip, n_tried_trip = _minimax_trials(
        f, autoconv, f_padded, dx, M_fft, integral_sq,
        k=3, n_trials=200_000, step_sizes=step_sizes_trip, rng=rng, deadline=trip_deadline)
    t1 = time.time()
    integral = np.sqrt(integral_sq)
    C_after_trip = np.max(autoconv) / integral_sq
    print(f"Triplets: {n_imp_trip} improvements / {n_tried_trip} tried in {t1-t0:.1f}s")
    print(f"C after triplets: {C_after_trip:.16f}")

    # --- Minimax quadruplet perturbation ---
    quad_deadline = min(_DEADLINE - 50, time.time() + 120)
    if time.time() < quad_deadline - 10:
        step_sizes_quad = np.array([3e-4, 1e-4, 3e-5, 1e-5, 3e-6, 1e-6])
        print(f"\n--- Minimax quadruplet perturbation (~120s budget) ---")
        t0 = time.time()
        f, autoconv, f_padded, integral_sq, n_imp_quad, n_tried_quad = _minimax_trials(
            f, autoconv, f_padded, dx, M_fft, integral_sq,
            k=4, n_trials=100_000, step_sizes=step_sizes_quad, rng=rng, deadline=quad_deadline)
        t1 = time.time()
        integral = np.sqrt(integral_sq)
        C_after_quad = np.max(autoconv) / integral_sq
        print(f"Quadruplets: {n_imp_quad} improvements / {n_tried_quad} tried in {t1-t0:.1f}s")
        print(f"C after quads: {C_after_quad:.16f}")
    else:
        n_imp_quad, n_tried_quad = 0, 0
        print("Skipping quadruplets (time budget)")

    # --- Ultra-fine CD polish ---
    cd_deadline = _DEADLINE - 5
    integral = np.sqrt(integral_sq)
    total_cd = 0
    if time.time() < cd_deadline - 15:
        print(f"\n--- Ultra-fine CD polish ---")
        deltas_cd = np.geomspace(1e-11, 1e-3, 30)
        for rnd in range(4):
            if time.time() > cd_deadline:
                break
            t0 = time.time()
            f, autoconv, f_padded, integral, n_imp_cd = _fast_cd_round(
                f, autoconv, f_padded, dx, M_fft, integral, deltas_cd, cd_deadline)
            integral_sq = integral * integral
            t1 = time.time()
            total_cd += n_imp_cd
            print(f"  CD round {rnd+1}: {n_imp_cd} improvements in {t1-t0:.1f}s, C={np.max(autoconv)/integral_sq:.16f}")
            if n_imp_cd == 0:
                break

    # --- Final result ---
    f = np.maximum(f, 0.0)
    C_final = compute_c_f64(f)
    print(f"\nFinal C = {C_final:.16f}")
    print(f"Delta from start: {C_final - C_start:.4e}")
    print(f"Summary: triplets={n_imp_trip}/{n_tried_trip}, quads={n_imp_quad}/{n_tried_quad}, cd={total_cd}")

    return f
