# fitness: 1.5028628712540075
# Extended coordinate descent on TTT-Discover 30k array
# Continues from gen006_exploit_1 which left off at ~1800 improvements/pass
# Uses O(N) incremental autoconv update (28x faster than full FFT)
import numpy as np
import importlib.util
import sys
import time


def _load_best_solution():
    sol_path = "/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen006/exploit_1/sol01.py"
    spec = importlib.util.spec_from_file_location("best_sol", sol_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return np.array(mod.entrypoint(), dtype=np.float64)


def _setup_helpers():
    proj_problem = "/home/sasha/Desktop/project_alpha/alpha-evolve/problem"
    if proj_problem not in sys.path:
        sys.path.insert(0, proj_problem)


def entrypoint():
    t_start = time.time()
    _setup_helpers()
    from helpers.compute_c_f64 import compute_c_f64

    print("Loading best 30k solution...")
    f = _load_best_solution()
    N = len(f)
    dx = 0.5 / N
    M = 2 * N
    C0 = compute_c_f64(f)
    print(f"  N={N}, C={C0:.12f}")

    # ── Initialize autoconv and working arrays ─────────────────────────────
    f_pad = np.zeros(M, dtype=np.float64)
    f_pad[:N] = f
    fft_fp = np.fft.fft(f_pad)
    autoconv = np.fft.ifft(fft_fp * fft_fp).real * dx
    integral = np.sum(f) * dx
    current_C = autoconv.max() / integral**2
    print(f"  Recomputed C = {current_C:.12f}")

    # Nonzero elements
    nonzero_mask = f > 1e-12
    nonzero_idx = np.where(nonzero_mask)[0]
    print(f"  Nonzero elements: {len(nonzero_idx)}")

    # Delta candidates: absolute offsets at multiple scales
    deltas = np.array([
        1e-9, 2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7,
        1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4
    ])

    total_improvements = 0
    round_num = 0
    TIME_LIMIT = 260  # leave buffer for evaluate.py

    while time.time() - t_start < TIME_LIMIT:
        round_num += 1
        t_round = time.time()
        improvements_this_round = 0

        # Shuffle order to avoid direction bias
        perm = np.random.permutation(len(nonzero_idx))

        for p_i in perm:
            idx = nonzero_idx[p_i]
            fi = f_pad[idx]

            if fi <= 0:
                continue

            best_delta = 0.0
            best_C_local = current_C

            # Precompute the convolution shift for this index
            # autoconv_new[n] = autoconv[n] + dx * 2 * delta * f_pad[(n-idx)%M]
            # i.e., the shift vector at idx: f_pad[(n-idx) for n in 0..M-1]
            # = np.roll(f_pad, idx) (right-roll)
            roll_f = np.roll(f_pad, idx)  # shape (M,)

            # Try positive and negative deltas
            for sign in [1.0, -1.0]:
                for d_abs in deltas:
                    delta = sign * d_abs
                    new_fi = fi + delta
                    if new_fi < 0:
                        continue
                    new_integral = integral + delta * dx
                    if new_integral < 1e-12:
                        continue
                    # Proposed autoconv change
                    new_autoconv_max = np.max(autoconv + 2.0 * dx * delta * roll_f)
                    new_C = new_autoconv_max / new_integral**2
                    if new_C < best_C_local:
                        best_C_local = new_C
                        best_delta = delta

            if best_delta != 0.0:
                # Accept the improvement
                roll_f_best = np.roll(f_pad, idx)
                autoconv += 2.0 * dx * best_delta * roll_f_best
                f_pad[idx] += best_delta
                if idx < N:
                    f[idx] = f_pad[idx]
                integral += best_delta * dx
                current_C = best_C_local
                improvements_this_round += 1

        total_improvements += improvements_this_round
        elapsed = time.time() - t_start
        print(f"  Round {round_num}: {improvements_this_round} improvements, "
              f"C={current_C:.12f}, elapsed={elapsed:.1f}s")

        if improvements_this_round == 0:
            print("  No improvements in this round, stopping")
            break

    # Final verification
    f_final = f_pad[:N].copy()
    f_final = np.maximum(f_final, 0.0)
    C_final = compute_c_f64(f_final)
    print(f"\nFinal C={C_final:.12f}, total improvements={total_improvements}")
    print(f"Improvement over baseline: {C0 - C_final:.6e}")
    return f_final
