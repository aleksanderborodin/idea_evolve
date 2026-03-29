"""Coordinate descent with top-K screening and periodic FFT resync.

Combines three algorithmic discoveries from gen 10:
1. Top-K screening (pattern_022): ~50x speedup by only checking K highest
   autoconv positions as pre-filter. No false negatives.
2. FFT resync (pattern_021): Recompute autoconv from scratch periodically
   to eliminate incremental drift (~1.4e-12/round).
3. Geometric delta grid: np.geomspace(1e-14, 1e-1, 100) covering all
   productive scales.

Import: from helpers.topk_screened_cd import topk_screened_cd
"""

import time
import numpy as np


def topk_screened_cd(f, K=30, deltas=None, resync_interval=1,
                     max_rounds=200, deadline=None, verbose=False):
    """
    Coordinate descent with top-K screening and periodic FFT resync.

    Implements the best-known CD algorithm combining:
    1. Top-K screening (pattern_022): Only check K highest autoconv positions
       per trial as pre-filter. No false negatives. ~50x speedup.
    2. FFT resync (pattern_021): Recompute autoconv from scratch every
       `resync_interval` rounds to eliminate incremental drift (~1.4e-12/round).
    3. Geometric delta grid: Default np.geomspace(1e-14, 1e-1, 100) covering
       all productive scales.

    Args:
        f: 1D numpy array, non-negative function values on [-1/4, 1/4].
        K: Number of top autoconv positions for screening (default 30).
        deltas: Array of positive delta values to try. Default: geomspace(1e-14, 1e-1, 100).
        resync_interval: FFT resync every N rounds (default 1 = every round).
        max_rounds: Maximum number of full sweeps over all elements.
        deadline: Unix timestamp to stop by (time.time() + budget). None = no limit.
        verbose: If True, print per-round stats.

    Returns:
        dict with keys:
            'f': optimized array (numpy float64)
            'C': final verified C value (float64, from FFT — not incremental)
            'n_improvements': total accepted moves (int)
            'n_rounds': rounds completed (int)
            'round_log': list of dicts with per-round stats:
                {'round': int, 'improvements': int, 'C_verified': float, 'elapsed_s': float}
    """
    f = np.asarray(f, dtype=np.float64).copy()
    N = len(f)

    if N == 0:
        return {
            'f': f,
            'C': float('nan'),
            'n_improvements': 0,
            'n_rounds': 0,
            'round_log': [],
        }

    if N == 1:
        # Single element: autoconv is f[0]^2 * dx, integral is f[0]*dx
        # C = f[0]^2 * dx / (f[0]*dx)^2 = 1/dx = 2*N = 2
        dx = 0.5 / N
        integral = float(f[0]) * dx
        if integral ** 2 < 1e-30:
            return {
                'f': f,
                'C': float('nan'),
                'n_improvements': 0,
                'n_rounds': 0,
                'round_log': [],
            }
        c_val = _compute_c_from_fft(f, N, dx)
        return {
            'f': f,
            'C': c_val,
            'n_improvements': 0,
            'n_rounds': 0,
            'round_log': [],
        }

    # Ensure non-negativity
    np.maximum(f, 0.0, out=f)

    dx = 0.5 / N
    M = 2 * N

    if deltas is None:
        deltas = np.geomspace(1e-14, 1e-1, 100)
    deltas = np.asarray(deltas, dtype=np.float64)

    # Clamp K to valid range
    K = max(1, min(K, M))

    # Initialize autoconv via FFT
    f_padded = np.zeros(M, dtype=np.float64)
    f_padded[:N] = f
    autoconv, integral_f = _fft_recompute(f_padded, dx, M)

    # Pre-compute n_arr for incremental updates
    n_arr = np.arange(M, dtype=np.int64)

    # Get initial top-K indices
    topk_indices = _get_topk_indices(autoconv, K)

    best_C = _c_from_autoconv(autoconv, integral_f)
    total_improvements = 0
    round_log = []
    t_start = time.time()

    for rnd in range(max_rounds):
        # Deadline check at start of round
        if deadline is not None and time.time() > deadline:
            break

        round_improvements = 0

        # FFT resync at start of round if needed
        if resync_interval > 0 and rnd % resync_interval == 0:
            autoconv, integral_f = _fft_recompute(f_padded, dx, M)
            topk_indices = _get_topk_indices(autoconv, K)
            best_C = _c_from_autoconv(autoconv, integral_f)

        # Sweep all elements
        for idx in range(N):
            # Deadline check periodically (every 1000 elements)
            if deadline is not None and idx % 1000 == 0 and time.time() > deadline:
                break

            for delta in deltas:
                # Try both +delta and -delta
                for sign in (1.0, -1.0):
                    d = sign * delta

                    # Non-negativity check
                    if f_padded[idx] + d < 0.0:
                        continue

                    # Top-K screening: check only topk positions
                    # Compute predicted new autoconv at topk positions
                    # new_autoconv[n] = autoconv[n] + 2*d*f_padded[(n-idx)%M]*dx + d^2*dx*(n==2*idx)
                    screening_indices = topk_indices
                    cross_at_topk = f_padded[(screening_indices - idx) % M]
                    new_ac_at_topk = (autoconv[screening_indices]
                                      + 2.0 * d * cross_at_topk * dx)
                    # Add self-term if 2*idx is in topk
                    self_idx = (2 * idx) % M
                    self_mask = (screening_indices == self_idx)
                    if np.any(self_mask):
                        new_ac_at_topk[self_mask] += d * d * dx

                    new_integral = integral_f + d * dx
                    if new_integral ** 2 < 1e-30:
                        continue

                    screen_max = float(np.max(new_ac_at_topk))
                    screen_C = screen_max / (new_integral ** 2)

                    # If screening C already >= best_C, this can't help
                    # (screen_max underestimates true max, so true C >= screen_C)
                    # Wait — screening UNDERESTIMATES max, so screen_C <= true_C.
                    # We want true_C < best_C. If screen_C >= best_C, then true_C >= screen_C >= best_C → reject.
                    # If screen_C < best_C, we need full verification.
                    if screen_C >= best_C:
                        continue

                    # Full incremental update to verify
                    cross_indices = (n_arr - idx) % M
                    new_autoconv = (autoconv
                                    + 2.0 * d * f_padded[cross_indices] * dx)
                    new_autoconv[self_idx] += d * d * dx

                    true_max = float(np.max(new_autoconv))
                    true_C = true_max / (new_integral ** 2)

                    if true_C < best_C:
                        # Accept
                        autoconv = new_autoconv
                        f_padded[idx] += d
                        f[idx] += d
                        integral_f = new_integral
                        best_C = true_C
                        round_improvements += 1
                        total_improvements += 1

                        # Update topk indices
                        topk_indices = _get_topk_indices(autoconv, K)
                        break  # Move to next delta magnitude (already found improvement)
                else:
                    continue
                break  # Found improvement at this delta, move to next element

        # End-of-round resync for verified C
        autoconv_verified, integral_verified = _fft_recompute(f_padded, dx, M)
        C_verified = _c_from_autoconv(autoconv_verified, integral_verified)

        elapsed = time.time() - t_start
        round_log.append({
            'round': rnd,
            'improvements': round_improvements,
            'C_verified': C_verified,
            'elapsed_s': elapsed,
        })

        if verbose:
            print(f"  Round {rnd}: {round_improvements} improvements, "
                  f"C_verified={C_verified:.16f}, elapsed={elapsed:.1f}s")

        # If no improvements this round, we're converged at this delta grid
        if round_improvements == 0:
            break

    # Final FFT verification
    autoconv_final, integral_final = _fft_recompute(f_padded, dx, M)
    C_final = _c_from_autoconv(autoconv_final, integral_final)

    # Ensure output is non-negative
    f_out = np.maximum(f, 0.0)

    return {
        'f': f_out,
        'C': C_final,
        'n_improvements': total_improvements,
        'n_rounds': len(round_log),
        'round_log': round_log,
    }


def _fft_recompute(f_padded, dx, M):
    """Full FFT recomputation of autoconv and integral."""
    N = M // 2
    fft_f = np.fft.fft(f_padded)
    autoconv = np.fft.ifft(fft_f * fft_f).real * dx
    integral_f = float(np.sum(f_padded[:N])) * dx
    return autoconv, integral_f


def _c_from_autoconv(autoconv, integral_f):
    """Compute C from autoconv array and integral."""
    if integral_f ** 2 < 1e-30:
        return float('inf')
    return float(np.max(autoconv)) / (integral_f ** 2)


def _compute_c_from_fft(f, N, dx):
    """Compute C from scratch via FFT for a raw f array."""
    M = 2 * N
    f_padded = np.zeros(M, dtype=np.float64)
    f_padded[:N] = np.maximum(f, 0.0)
    fft_f = np.fft.fft(f_padded)
    autoconv = np.fft.ifft(fft_f * fft_f).real * dx
    integral = float(np.sum(f_padded[:N])) * dx
    if integral ** 2 < 1e-30:
        return float('nan')
    return float(np.max(autoconv)) / (integral ** 2)


def _get_topk_indices(autoconv, K):
    """Get indices of top K values in autoconv."""
    if K >= len(autoconv):
        return np.arange(len(autoconv), dtype=np.int64)
    # Use argpartition for O(M) instead of O(M log M) sort
    indices = np.argpartition(autoconv, -K)[-K:]
    return indices.astype(np.int64)
