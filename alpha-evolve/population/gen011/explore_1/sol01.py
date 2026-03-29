# fitness: 1.5028628677925082
# Strategy: load gen009 inline array → Phase 2 non-IP pair search → Phase 3 ultra-fine CD
# Base: gen009/exploit_1 C=1.5028628682228971 (inline array, no chain loading overhead)
# Phase 2: non-integral-preserving 2-element moves (10k+ pair trials)
# Phase 3: ultra-fine CD geomspace(1e-14, 1e-1, 100), multiple rounds, FFT resync every 3 rounds
import sys
import time
import importlib.util
import numpy as np

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/alpha-evolve/problem')

_DEADLINE = time.time() + 490


def _load_base():
    """Load gen009/exploit_1 inline array (no chain overhead)."""
    path = "/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen009/exploit_1/sol01.py"
    spec = importlib.util.spec_from_file_location("base_sol", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return np.array(mod.entrypoint(), dtype=np.float64)


def _fft_resync(f_padded, dx):
    """Recompute autoconv from scratch via FFT to avoid incremental drift."""
    fft_f = np.fft.fft(f_padded)
    return np.fft.ifft(fft_f * fft_f).real * dx


def entrypoint():
    f = _load_base()
    f = np.maximum(f, 0.0)
    N = len(f)
    dx = 0.5 / N
    M = 2 * N

    f_padded = np.zeros(M, dtype=np.float64)
    f_padded[:N] = f

    # Initial FFT-based autoconv
    autoconv = _fft_resync(f_padded, dx)
    integral = np.sum(f_padded[:N]) * dx
    integral_sq = integral * integral
    best_c = np.max(autoconv) / integral_sq
    print(f"[init] N={N}, C={best_c:.16f}", flush=True)

    n_arr = np.arange(M, dtype=np.int64)

    def get_high_pos(eps_rel=1e-7):
        mv = np.max(autoconv)
        return np.where(autoconv >= mv * (1.0 - eps_rel))[0]

    def fast_check_1(high_pos, i, d_val):
        """O(W) fast check for single element change."""
        cross = (high_pos - i) % M
        ac_win = autoconv[high_pos] + 2.0 * dx * d_val * f_padded[cross]
        self_mask = (high_pos == (2 * i) % M)
        if np.any(self_mask):
            ac_win[self_mask] += d_val * d_val * dx
        return float(np.max(ac_win))

    def apply_single(i, d_val):
        nonlocal autoconv, f_padded
        cross = (n_arr - i) % M
        autoconv = autoconv + 2.0 * dx * d_val * f_padded[cross]
        autoconv[(2 * i) % M] += d_val * d_val * dx
        f_padded[i] += d_val

    def apply_pair_inplace(i, j, di, dj):
        """Apply 2-element move in-place. Returns nothing (use revert to undo)."""
        nonlocal autoconv, f_padded
        # Apply di to element i first
        cross_i = (n_arr - i) % M
        autoconv = autoconv + 2.0 * dx * di * f_padded[cross_i]
        autoconv[(2 * i) % M] += di * di * dx
        f_padded[i] += di
        # Apply dj to element j (f_padded now reflects di at i)
        cross_j = (n_arr - j) % M
        autoconv = autoconv + 2.0 * dx * dj * f_padded[cross_j]
        autoconv[(2 * j) % M] += dj * dj * dx
        f_padded[j] += dj

    def revert_pair_inplace(i, j, di, dj):
        """Revert pair move by applying negatives in reverse order."""
        nonlocal autoconv, f_padded
        # Undo dj at j first
        f_padded[j] -= dj
        cross_j = (n_arr - j) % M
        autoconv = autoconv - 2.0 * dx * dj * f_padded[cross_j]
        autoconv[(2 * j) % M] -= dj * dj * dx
        # Undo di at i
        f_padded[i] -= di
        cross_i = (n_arr - i) % M
        autoconv = autoconv - 2.0 * dx * di * f_padded[cross_i]
        autoconv[(2 * i) % M] -= di * di * dx

    def fast_check_pair(high_pos, i, j, di, dj):
        """O(W) fast check for 2-element change (ignores di*dj cross term)."""
        ac_win = autoconv[high_pos].copy()
        cross_i = (high_pos - i) % M
        ac_win += 2.0 * dx * di * f_padded[cross_i]
        self_i = (2 * i) % M
        mask_i = (high_pos == self_i)
        if np.any(mask_i):
            ac_win[mask_i] += di * di * dx
        cross_j = (high_pos - j) % M
        ac_win += 2.0 * dx * dj * f_padded[cross_j]
        self_j = (2 * j) % M
        mask_j = (high_pos == self_j)
        if np.any(mask_j):
            ac_win[mask_j] += dj * dj * dx
        return float(np.max(ac_win))

    # ── Phase 1: Standard CD (warm-up to improve from gen009 base) ───────
    print("[Phase 1] Standard CD warm-up", flush=True)
    t0 = time.time()
    high_pos = get_high_pos(1e-7)
    std_impr = 0

    # Coarse passes first
    for delta in np.geomspace(1e-4, 1e-1, 8):
        if time.time() > _DEADLINE:
            break
        for sign in (+1.0, -1.0):
            for i in range(N):
                d_val = sign * delta
                if f_padded[i] + d_val < 0:
                    continue
                pred_max = fast_check_1(high_pos, i, d_val)
                new_int = integral + d_val * dx
                if new_int <= 0:
                    continue
                if pred_max / (new_int * new_int) < best_c:
                    apply_single(i, d_val)
                    true_c = np.max(autoconv) / (new_int * new_int)
                    if true_c < best_c:
                        integral = new_int
                        integral_sq = integral * integral
                        best_c = true_c
                        std_impr += 1
                        high_pos = get_high_pos(1e-7)
                    else:
                        apply_single(i, -d_val)  # revert

    elapsed = time.time() - t0
    print(f"[Phase 1 done] impr={std_impr}, C={best_c:.16f}, t={elapsed:.1f}s", flush=True)

    # ── Phase 2: Non-integral-preserving 2-element moves ─────────────────
    # Test pairs (i,j) where both di,dj can have same sign (changes integral)
    # Key: CD can only move one element at a time; coupled 2-element moves
    # can traverse saddle points in C landscape that CD cannot.
    print("[Phase 2] Non-integral-preserving 2-element pair search", flush=True)
    t0 = time.time()

    # FFT resync before Phase 2
    autoconv = _fft_resync(f_padded, dx)
    integral = np.sum(f_padded[:N]) * dx
    integral_sq = integral * integral
    best_c = np.max(autoconv) / integral_sq
    high_pos = get_high_pos(1e-7)

    rng = np.random.default_rng(456)
    delta_vals = np.geomspace(1e-13, 1e-6, 20)
    pair_impr = 0
    pair_trials = 0

    # Phase 2a: Neighboring element pairs (i, i+1) with small deltas
    # These share autoconv cross-terms and may have correlated improvements
    print("[Phase 2a] Neighboring pairs", flush=True)
    neighbor_impr = 0
    neighbor_budget = min(N - 1, 10000)
    for i in range(neighbor_budget):
        if time.time() > _DEADLINE:
            break
        j = i + 1
        for delta_mag in delta_vals[::3]:  # 7 values
            for si in (+1.0, -1.0):
                for sj in (+1.0, -1.0):
                    di = si * delta_mag
                    dj = sj * delta_mag
                    if f_padded[i] + di < 0 or f_padded[j] + dj < 0:
                        continue
                    new_int = integral + (di + dj) * dx
                    if new_int <= 0:
                        continue
                    pred_max = fast_check_pair(high_pos, i, j, di, dj)
                    if pred_max / (new_int * new_int) < best_c:
                        ac_save = autoconv.copy()
                        fi_save = f_padded[i]
                        fj_save = f_padded[j]
                        apply_pair_inplace(i, j, di, dj)
                        true_c = np.max(autoconv) / (new_int * new_int)
                        if true_c < best_c:
                            best_c = true_c
                            integral = new_int
                            integral_sq = integral * integral
                            neighbor_impr += 1
                            pair_impr += 1
                            high_pos = get_high_pos(1e-7)
                        else:
                            autoconv = ac_save
                            f_padded[i] = fi_save
                            f_padded[j] = fj_save
        pair_trials += len(delta_vals[::3]) * 4

    elapsed = time.time() - t0
    print(f"[Phase 2a done] neighbor_impr={neighbor_impr}, C={best_c:.16f}, "
          f"t={elapsed:.1f}s", flush=True)

    # Phase 2b: High-sensitivity random pairs
    print("[Phase 2b] High-sensitivity random pairs", flush=True)

    # Compute sensitivity: gradient at max position
    max_pos = int(np.argmax(autoconv))
    # gradient[m] = 2*dx*f_padded[(max_pos - m) % M]
    cross_m = (max_pos - np.arange(N, dtype=np.int64)) % M
    sensitivity = 2.0 * dx * f_padded[cross_m]
    top_sens_idx = np.argsort(np.abs(sensitivity))[::-1][:500]

    n_random = 15000
    random_impr = 0

    for trial in range(n_random):
        if time.time() > _DEADLINE:
            break
        # Pick pair: one high-sensitivity, one random
        i = int(top_sens_idx[rng.integers(len(top_sens_idx))])
        j = int(rng.integers(N))
        if i == j:
            j = (j + 1) % N

        delta_mag = delta_vals[rng.integers(len(delta_vals))]
        for si in (+1.0, -1.0):
            for sj in (+1.0, -1.0):
                di = si * delta_mag
                dj = sj * delta_mag
                if f_padded[i] + di < 0 or f_padded[j] + dj < 0:
                    continue
                new_int = integral + (di + dj) * dx
                if new_int <= 0:
                    continue
                pred_max = fast_check_pair(high_pos, i, j, di, dj)
                if pred_max / (new_int * new_int) < best_c:
                    ac_save = autoconv.copy()
                    fi_save = f_padded[i]
                    fj_save = f_padded[j]
                    apply_pair_inplace(i, j, di, dj)
                    true_c = np.max(autoconv) / (new_int * new_int)
                    if true_c < best_c:
                        best_c = true_c
                        integral = new_int
                        integral_sq = integral * integral
                        random_impr += 1
                        pair_impr += 1
                        high_pos = get_high_pos(1e-7)
                    else:
                        autoconv = ac_save
                        f_padded[i] = fi_save
                        f_padded[j] = fj_save

        pair_trials += 4
        if trial % 3000 == 2999:
            autoconv = _fft_resync(f_padded, dx)
            integral = np.sum(f_padded[:N]) * dx
            integral_sq = integral * integral
            best_c = np.max(autoconv) / integral_sq
            high_pos = get_high_pos(1e-7)
            # Refresh sensitivity
            max_pos = int(np.argmax(autoconv))
            cross_m = (max_pos - np.arange(N, dtype=np.int64)) % M
            sensitivity = 2.0 * dx * f_padded[cross_m]
            top_sens_idx = np.argsort(np.abs(sensitivity))[::-1][:500]
            print(f"[Phase 2b] trial={trial+1}, random_impr={random_impr}, "
                  f"C={best_c:.16f}, t={time.time()-t0:.1f}s", flush=True)

    # FFT resync
    autoconv = _fft_resync(f_padded, dx)
    integral = np.sum(f_padded[:N]) * dx
    integral_sq = integral * integral
    best_c = np.max(autoconv) / integral_sq
    elapsed = time.time() - t0
    print(f"[Phase 2 done] pair_impr={pair_impr}, pair_trials={pair_trials}, "
          f"C={best_c:.16f}, t={elapsed:.1f}s", flush=True)

    # ── Phase 3: Ultra-fine coordinate descent ────────────────────────────
    print("[Phase 3] Ultra-fine CD geomspace(1e-14, 1e-1, 100)", flush=True)
    t0 = time.time()
    uf_impr = 0
    total_rounds = 0
    resync_every = 3

    delta_grid = np.geomspace(1e-14, 1e-1, 100)
    high_pos = get_high_pos(1e-7)

    for round_num in range(200):
        if time.time() > _DEADLINE:
            break

        if round_num % resync_every == 0:
            autoconv = _fft_resync(f_padded, dx)
            integral = np.sum(f_padded[:N]) * dx
            integral_sq = integral * integral
            best_c = np.max(autoconv) / integral_sq
            high_pos = get_high_pos(1e-7)

        round_impr = 0
        for delta in delta_grid:
            if time.time() > _DEADLINE:
                break
            for sign in (+1.0, -1.0):
                d_val = sign * delta
                for i in range(N):
                    if f_padded[i] + d_val < 0:
                        continue
                    pred_max = fast_check_1(high_pos, i, d_val)
                    new_int = integral + d_val * dx
                    if new_int <= 0:
                        continue
                    if pred_max / (new_int * new_int) < best_c:
                        apply_single(i, d_val)
                        true_c = np.max(autoconv) / (new_int * new_int)
                        if true_c < best_c:
                            integral = new_int
                            integral_sq = integral * integral
                            best_c = true_c
                            uf_impr += 1
                            round_impr += 1
                            high_pos = get_high_pos(1e-7)
                        else:
                            apply_single(i, -d_val)  # revert

        total_rounds += 1
        if round_num % 5 == 4 or round_impr > 0:
            print(f"[Phase 3] round={round_num+1}, round_impr={round_impr}, "
                  f"total={uf_impr}, C={best_c:.16f}, t={time.time()-t0:.1f}s", flush=True)

        if round_impr == 0 and round_num >= 5:
            print(f"[Phase 3] converged after {round_num+1} rounds", flush=True)
            break

    # Final FFT resync
    autoconv = _fft_resync(f_padded, dx)
    integral = np.sum(f_padded[:N]) * dx
    integral_sq = integral * integral
    best_c = np.max(autoconv) / integral_sq
    elapsed = time.time() - t0
    print(f"[Phase 3 done] total_impr={uf_impr}, rounds={total_rounds}, "
          f"C={best_c:.16f}, t={elapsed:.1f}s", flush=True)
    print(f"[FINAL] C={best_c:.16f}", flush=True)

    return np.array(f_padded[:N], dtype=np.float64)
