# fitness: 1.5028628681165177
# Strategy: skip std CD (already converged) → fast triplets (200k) → quads (50k) → ultra-fine CD
# Fast check uses precomputed high-autoconv positions (O(W*k) per trial)
# Exact update only when fast check passes (O(M*k) per trial)
# Start: gen009_exploit_1 C=1.5028628682228971
import importlib.util
import time
import numpy as np


_DEADLINE = time.time() + 490


def _load_best():
    path = "/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen009/exploit_1/sol01.py"
    spec = importlib.util.spec_from_file_location("best_sol", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return np.array(mod.entrypoint(), dtype=np.float64)


def entrypoint():
    import sys
    sys.path.insert(0, "/home/sasha/Desktop/project_alpha/alpha-evolve/problem")
    from helpers.incremental_autoconv_update import incremental_update

    f = _load_best()
    f = np.maximum(f, 0.0)
    N = len(f)
    dx = 0.5 / N
    M = 2 * N

    f_padded = np.zeros(M, dtype=np.float64)
    f_padded[:N] = f
    fft_f = np.fft.fft(f_padded)
    autoconv = np.fft.ifft(fft_f * fft_f).real * dx

    integral = np.sum(f_padded[:N]) * dx
    integral_sq = integral * integral
    best_c = np.max(autoconv) / integral_sq
    print(f"[init] N={N}, C={best_c:.16f}", flush=True)

    n_arr = np.arange(M, dtype=np.int64)  # precomputed once

    def get_high_positions(eps_rel=1e-7):
        """Positions where autoconv is within eps_rel of max."""
        mv = np.max(autoconv)
        return np.where(autoconv >= mv * (1.0 - eps_rel))[0]

    def fast_check(high_pos, idx, d, k):
        """O(W*k) check: compute predicted new max at high_pos only."""
        ac_window = autoconv[high_pos].copy()
        for pi in range(k):
            cross = (high_pos - int(idx[pi])) % M
            ac_window += 2.0 * dx * d[pi] * f_padded[cross]
            self_i = (2 * int(idx[pi])) % M
            matches = (high_pos == self_i)
            if np.any(matches):
                ac_window[matches] += d[pi] * d[pi] * dx
        return np.max(ac_window)

    def apply_move(idx, d, k):
        """Apply k-element move in-place. Returns autoconv_save for revert."""
        nonlocal autoconv, f_padded
        autoconv_save = autoconv.copy()
        for pi in range(k):
            i = int(idx[pi])
            di = d[pi]
            cross = (n_arr - i) % M
            autoconv = autoconv + 2.0 * di * f_padded[cross] * dx
            autoconv[(2 * i) % M] += di * di * dx
            f_padded[i] += di
        return autoconv_save

    def revert_move(autoconv_save, idx, d, k):
        nonlocal autoconv, f_padded
        autoconv = autoconv_save
        for pi in range(k):
            f_padded[int(idx[pi])] -= d[pi]

    # ── Phase 1: Standard CD (quick check) ───────────────────────────────
    # Check a coarse sweep to confirm no CD improvements (warm-up)
    t0 = time.time()
    std_impr = 0
    high_pos = get_high_positions(1e-7)
    for delta in np.geomspace(1e-4, 1e-1, 10):
        if time.time() > _DEADLINE:
            break
        for sign in (+1.0, -1.0):
            for i in range(N):
                d_val = sign * delta
                if f_padded[i] + d_val < 0:
                    continue
                pred_max = fast_check(high_pos, [i], [d_val], 1)
                new_int = integral + d_val * dx
                if new_int <= 0:
                    continue
                if pred_max / (new_int * new_int) < best_c:
                    # Exact verify
                    ac_save = apply_move([i], [d_val], 1)
                    true_c = np.max(autoconv) / (new_int * new_int)
                    if true_c < best_c:
                        integral = new_int
                        integral_sq = integral * integral
                        best_c = true_c
                        std_impr += 1
                        high_pos = get_high_positions(1e-7)
                    else:
                        revert_move(ac_save, [i], [d_val], 1)
    print(f"[coarse CD] impr={std_impr}, C={best_c:.16f}, t={time.time()-t0:.1f}s", flush=True)

    # ── Phase 2: Triplet search ───────────────────────────────────────────
    rng = np.random.default_rng(42)
    step_sizes = np.geomspace(1e-6, 1e-1, 9)
    high_pos = get_high_positions(1e-7)  # W≈6760 positions
    nonzero_idx = np.where(f_padded[:N] > 1e-12)[0]
    k = 3
    triplet_impr = 0
    t0 = time.time()
    n_trials = 0
    n_exact = 0

    sorted_nz = nonzero_idx[np.argsort(f_padded[nonzero_idx])[::-1]]
    median_v = np.median(f_padded[nonzero_idx])
    small_pool = nonzero_idx[f_padded[nonzero_idx] < median_v]
    if len(small_pool) == 0:
        small_pool = nonzero_idx

    N_TRIPLET_TRIALS = 200000

    for trial in range(N_TRIPLET_TRIALS):
        if time.time() > _DEADLINE:
            break
        n_trials += 1
        alpha = step_sizes[rng.integers(len(step_sizes))]
        strategy = trial % 3

        if strategy == 0 or len(nonzero_idx) < k:
            idx = rng.choice(nonzero_idx if len(nonzero_idx) >= k else np.arange(N, dtype=np.int64),
                             size=k, replace=False)
        elif strategy == 1:
            i0 = int(sorted_nz[rng.integers(min(20, len(sorted_nz)))])
            i1 = int(small_pool[rng.integers(len(small_pool))])
            i2 = int(rng.integers(N))
            idx = np.array([i0, i1, i2], dtype=np.int64)
        else:
            i01 = rng.choice(nonzero_idx, size=2, replace=False)
            i2 = rng.integers(N)
            idx = np.array([i01[0], i01[1], i2], dtype=np.int64)

        d = rng.standard_normal(k) * alpha
        d -= d.mean()
        for pi in range(k):
            if f_padded[int(idx[pi])] + d[pi] < 0:
                d[pi] = -f_padded[int(idx[pi])] * 0.5

        # Fast check (adaptive eps based on alpha)
        eps = min(1e-5, max(1e-8, alpha * 1e-5))
        hp = high_pos  # use cached; refresh periodically

        pred_max = fast_check(hp, idx, d, k)
        if pred_max / integral_sq >= best_c:
            continue

        # Exact verify
        n_exact += 1
        ac_save = apply_move(idx, d, k)
        new_c = np.max(autoconv) / integral_sq
        if new_c < best_c:
            best_c = new_c
            triplet_impr += 1
            high_pos = get_high_positions(1e-7)
            nonzero_idx = np.where(f_padded[:N] > 1e-12)[0]
            if len(nonzero_idx) >= k:
                sorted_nz = nonzero_idx[np.argsort(f_padded[nonzero_idx])[::-1]]
                median_v = np.median(f_padded[nonzero_idx])
                small_pool = nonzero_idx[f_padded[nonzero_idx] < median_v]
                if len(small_pool) == 0:
                    small_pool = nonzero_idx
        else:
            revert_move(ac_save, idx, d, k)

        if trial % 10000 == 9999:
            elapsed = time.time() - t0
            rate = n_trials / elapsed
            print(f"[triplets] trial={trial+1}, impr={triplet_impr}, C={best_c:.16f}, "
                  f"rate={rate:.0f}/s, exact_frac={n_exact/n_trials:.3f}, t={elapsed:.1f}s", flush=True)
            # Refresh high_pos periodically
            high_pos = get_high_positions(1e-7)

    elapsed = time.time() - t0
    rate = n_trials / elapsed if elapsed > 0 else 0
    print(f"[triplets done] trials={n_trials}, impr={triplet_impr}, C={best_c:.16f}, "
          f"rate={rate:.0f}/s, t={elapsed:.1f}s", flush=True)

    # ── Phase 3: Quadruplet follow-up ────────────────────────────────────
    k = 4
    quad_impr = 0
    nonzero_idx = np.where(f_padded[:N] > 1e-12)[0]
    high_pos = get_high_positions(1e-7)
    t0 = time.time()
    n_quad = 0
    N_QUAD = 50000

    for trial in range(N_QUAD):
        if time.time() > _DEADLINE:
            break
        n_quad += 1
        alpha = step_sizes[rng.integers(len(step_sizes))]
        nz = nonzero_idx if len(nonzero_idx) >= k else np.arange(N, dtype=np.int64)
        idx = rng.choice(nz, size=k, replace=False)
        d = rng.standard_normal(k) * alpha
        d -= d.mean()
        for pi in range(k):
            if f_padded[int(idx[pi])] + d[pi] < 0:
                d[pi] = -f_padded[int(idx[pi])] * 0.5

        pred_max = fast_check(high_pos, idx, d, k)
        if pred_max / integral_sq >= best_c:
            continue

        ac_save = apply_move(idx, d, k)
        new_c = np.max(autoconv) / integral_sq
        if new_c < best_c:
            best_c = new_c
            quad_impr += 1
            high_pos = get_high_positions(1e-7)
            nonzero_idx = np.where(f_padded[:N] > 1e-12)[0]
        else:
            revert_move(ac_save, idx, d, k)

        if trial % 10000 == 9999:
            high_pos = get_high_positions(1e-7)

    print(f"[quads done] trials={n_quad}, impr={quad_impr}, C={best_c:.16f}, t={time.time()-t0:.1f}s", flush=True)

    # ── Phase 4: Ultra-fine CD ────────────────────────────────────────────
    integral = np.sum(f_padded[:N]) * dx
    integral_sq = integral * integral
    best_c = np.max(autoconv) / integral_sq
    high_pos = get_high_positions(1e-7)
    t0 = time.time()
    uf_impr = 0

    for delta in np.geomspace(1e-11, 1e-1, 50):
        if time.time() > _DEADLINE:
            break
        improved = True
        while improved and time.time() < _DEADLINE:
            improved = False
            for i in range(N):
                for sign in (+1.0, -1.0):
                    d_val = sign * delta
                    if f_padded[i] + d_val < 0:
                        continue
                    pred_max = fast_check(high_pos, [i], [d_val], 1)
                    new_int = integral + d_val * dx
                    if new_int <= 0:
                        continue
                    if pred_max / (new_int * new_int) < best_c:
                        ac_save = apply_move([i], [d_val], 1)
                        true_c = np.max(autoconv) / (new_int * new_int)
                        if true_c < best_c:
                            integral = new_int
                            integral_sq = integral * integral
                            best_c = true_c
                            uf_impr += 1
                            improved = True
                            high_pos = get_high_positions(1e-7)
                        else:
                            revert_move(ac_save, [i], [d_val], 1)

    print(f"[ultra-fine CD] impr={uf_impr}, C={best_c:.16f}, t={time.time()-t0:.1f}s", flush=True)
    print(f"[FINAL] C={best_c:.16f}", flush=True)

    return np.array(f_padded[:N], dtype=np.float64)
