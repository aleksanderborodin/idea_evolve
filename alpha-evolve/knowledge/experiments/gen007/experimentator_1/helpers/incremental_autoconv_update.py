"""O(N) incremental autoconvolution update for coordinate descent optimization.

When a single element f[idx] changes by delta, this module updates the full
autoconvolution array in O(N) time instead of recomputing via FFT in O(N log N).

The speedup is ~28x for N=30000 (measured in gen006 exploit_1 debrief).

Background
----------
Autoconvolution is computed as: conv[n] = IFFT(FFT(f_padded)^2).real * dx
where f_padded = [f[0], ..., f[N-1], 0, ..., 0] has length M_fft = 2N.

When f[idx] += delta, the update rule is:
    conv_new[n] = conv_old[n] + dx * (2 * delta * f_padded[(n - idx) % M_fft]
                                      + delta^2 * (n == 2*idx))

The cross term (2 * delta * ...) is a shifted copy of f_padded scaled by 2*delta*dx.
The self term (delta^2) is a point update at index 2*idx.

This is exact to floating-point precision — no approximation is made.
"""

import numpy as np


def incremental_update(autoconv, f_padded, idx, delta, dx, M_fft):
    """Update autoconvolution array when f[idx] changes by delta.

    O(N) instead of O(N log N) FFT recomputation. Produces bit-identical
    results to full FFT recomputation (within float64 rounding, < 1e-14 error).

    IMPORTANT: This function does NOT modify f_padded in-place. The caller
    must update f_padded[idx] += delta after calling this function.

    Args:
        autoconv: 1D numpy float64 array of length M_fft. The current
            autoconvolution array: IFFT(FFT(f_padded)^2).real * dx.
            This is the SCALED autoconvolution (already multiplied by dx).
        f_padded: 1D numpy float64 array of length M_fft. The zero-padded
            function: f_padded[:N] = f, f_padded[N:] = 0.
            Must reflect the state BEFORE the delta is applied.
        idx: int in [0, N-1]. The index of the element being changed.
        delta: float. The change amount: f_new[idx] = f_old[idx] + delta.
        dx: float. Grid spacing = 0.5 / N.
        M_fft: int. FFT array length = 2*N.

    Returns:
        new_autoconv: 1D numpy float64 array of length M_fft. The updated
            autoconvolution array after f[idx] += delta.

    Examples:
        >>> import numpy as np
        >>> rng = np.random.default_rng(42)
        >>> N = 500
        >>> f = np.abs(rng.standard_normal(N))
        >>> dx = 0.5 / N
        >>> M = 2 * N
        >>> f_padded = np.pad(f, (0, N)).astype(np.float64)
        >>> # Compute baseline autoconv
        >>> fft_f = np.fft.fft(f_padded)
        >>> autoconv = np.fft.ifft(fft_f * fft_f).real * dx
        >>> # Apply incremental update
        >>> idx, delta = 100, 0.01
        >>> new_ac = incremental_update(autoconv, f_padded, idx, delta, dx, M)
        >>> # Apply the actual change and recompute reference
        >>> f_padded[idx] += delta
        >>> fft_new = np.fft.fft(f_padded)
        >>> ref_ac = np.fft.ifft(fft_new * fft_new).real * dx
        >>> # Max absolute difference should be < 1e-14
        >>> assert np.max(np.abs(new_ac - ref_ac)) < 1e-14
    """
    autoconv = np.asarray(autoconv, dtype=np.float64)
    f_padded = np.asarray(f_padded, dtype=np.float64)

    if len(autoconv) != M_fft:
        raise ValueError(
            f"autoconv length {len(autoconv)} != M_fft {M_fft}"
        )
    if len(f_padded) != M_fft:
        raise ValueError(
            f"f_padded length {len(f_padded)} != M_fft {M_fft}"
        )
    if not (0 <= idx < M_fft // 2):
        raise ValueError(
            f"idx {idx} out of range [0, N-1] = [0, {M_fft // 2 - 1}]"
        )

    n_arr = np.arange(M_fft, dtype=np.int64)
    cross_indices = (n_arr - idx) % M_fft

    # Cross term: 2 * delta * f_padded[(n - idx) % M] * dx  for all n
    new_autoconv = autoconv + 2.0 * delta * f_padded[cross_indices] * dx

    # Self-convolution term: delta^2 * dx at index 2*idx
    self_idx = (2 * idx) % M_fft
    new_autoconv[self_idx] += delta * delta * dx

    return new_autoconv


def batch_incremental_updates(autoconv, f_padded, indices, deltas, dx, M_fft):
    """Apply multiple incremental updates sequentially.

    Equivalent to calling incremental_update in a loop, but slightly more
    efficient as it avoids repeated numpy overhead. Updates are applied
    one at a time in order — this is exact when changes are independent
    (different indices) but also correct for repeated indices.

    IMPORTANT: Updates f_padded in-place as each update is applied.
    Pass a copy of f_padded if you need the original preserved.

    Args:
        autoconv: Current autoconvolution array (modified in-place).
        f_padded: Zero-padded f array (modified in-place: f_padded[idx] += delta).
        indices: Array of indices to update.
        deltas: Array of delta values, same length as indices.
        dx: Grid spacing = 0.5 / N.
        M_fft: FFT array length = 2*N.

    Returns:
        autoconv: Updated autoconvolution array (same object, modified in-place).
        f_padded: Updated f_padded array (same object, modified in-place).
    """
    autoconv = np.asarray(autoconv, dtype=np.float64)
    f_padded = np.asarray(f_padded, dtype=np.float64)
    indices = np.asarray(indices, dtype=np.int64)
    deltas = np.asarray(deltas, dtype=np.float64)

    n_arr = np.arange(M_fft, dtype=np.int64)

    for idx, delta in zip(indices, deltas):
        cross_indices = (n_arr - int(idx)) % M_fft
        autoconv += 2.0 * delta * f_padded[cross_indices] * dx
        self_idx = (2 * int(idx)) % M_fft
        autoconv[self_idx] += delta * delta * dx
        f_padded[int(idx)] += delta

    return autoconv, f_padded
