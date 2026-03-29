"""Autoconvolution plateau structure analyzer.

Identifies near-maximum positions in the autoconvolution array and computes
per-element gradients at each plateau position. Designed for minimax
perturbation strategies (idea_023) where the optimizer needs to reduce
the maximum across ALL near-tied positions simultaneously.

Performance: < 10ms at N=30000 with K=13 plateau positions.
"""

import numpy as np


def plateau_analysis(f, autoconv=None, threshold_rel=1e-12):
    """
    Analyze the autoconvolution plateau structure.

    Finds all positions where the autoconvolution is within a relative
    threshold of its maximum, and computes the exact gradient of the
    autoconvolution at each such position with respect to every element
    of f. This enables minimax optimization: finding perturbation
    directions that reduce the maximum across all near-tied positions.

    Args:
        f: (N,) array of non-negative function values on [-1/4, 1/4].
            Negative values are clamped to 0.
        autoconv: (optional) (2N,) float64 array — pre-computed SCALED
            autoconvolution (IFFT(FFT(f_padded)^2).real * dx). If None,
            computed from f via FFT. Must have length exactly 2*N.
        threshold_rel: float — relative threshold for near-max positions.
            Position n is "plateau" if autoconv[n] >= max * (1 - threshold_rel).
            Default 1e-12. Use 1e-6 for broader plateau detection.

    Returns:
        dict with keys:
            positions: (K,) int64 array — indices where autoconv >= threshold
            values: (K,) float64 array — autoconv values at those positions
            gradients: (K, N) float64 array — gradient of autoconv at each
                plateau position w.r.t. each element of f.
                gradients[p, m] = d(autoconv[positions[p]]) / d(f[m])
                             = 2 * dx * f_padded[(positions[p] - m) % (2N)]
            max_val: float — max(autoconv)
            max_idx: int — argmax(autoconv)

    Raises:
        ValueError: If f is empty, wrong shape, or autoconv has wrong length.

    Mathematical basis:
        autoconv[n] = dx * sum_j f_padded[j] * f_padded[(n-j) % M]
        d(autoconv[n])/d(f[m]) = 2 * dx * f_padded[(n - m) % M]
        where M = 2*N, f_padded = [f[0],...,f[N-1], 0,...,0], dx = 0.5/N.

    Performance:
        Autoconv computation (if needed): O(N log N) via FFT
        Plateau detection: O(N) scan
        Gradient matrix: O(K * N) vectorized numpy indexing
        Total at N=30000, K=13: ~7ms

    Examples:
        >>> import numpy as np
        >>> f = np.abs(np.random.default_rng(42).standard_normal(1000)) * 0.1
        >>> result = plateau_analysis(f, threshold_rel=1e-6)
        >>> result['positions']  # indices of near-max autoconv values
        array(...)
        >>> result['gradients'].shape  # (K, N) gradient matrix
        (...)
        >>> # Use with minimax LP: find direction reducing max across all K positions
        >>> # For each candidate perturbation delta (N,):
        >>> #   predicted_change[p] = gradients[p, :] @ delta
        >>> # Minimize max_p(values[p] + predicted_change[p])

        >>> # Verify consistency with compute_c_f64:
        >>> from helpers.compute_c_f64 import compute_c_f64
        >>> dx = 0.5 / len(f)
        >>> integral = np.sum(np.maximum(f, 0.0)) * dx
        >>> c_from_plateau = result['max_val'] / integral**2
        >>> c_from_helper = compute_c_f64(f)
        >>> abs(c_from_plateau - c_from_helper) < 1e-12
        True
    """
    f = np.asarray(f, dtype=np.float64)
    if f.ndim != 1:
        raise ValueError(f"Expected 1D array, got shape {f.shape}")
    N = len(f)
    if N == 0:
        raise ValueError("Array cannot be empty")

    M = 2 * N
    dx = 0.5 / N

    # Compute autoconvolution if not provided
    if autoconv is None:
        f_padded = np.zeros(M, dtype=np.float64)
        f_padded[:N] = np.maximum(f, 0.0)
        fft_f = np.fft.fft(f_padded)
        autoconv = np.fft.ifft(fft_f * fft_f).real * dx
    else:
        autoconv = np.asarray(autoconv, dtype=np.float64)
        if len(autoconv) != M:
            raise ValueError(
                f"autoconv length {len(autoconv)} != expected 2*N = {M}"
            )
        f_padded = np.zeros(M, dtype=np.float64)
        f_padded[:N] = np.maximum(f, 0.0)

    # Find plateau positions
    max_val = float(np.max(autoconv))
    max_idx = int(np.argmax(autoconv))
    threshold = max_val * (1.0 - threshold_rel)
    positions = np.where(autoconv >= threshold)[0].astype(np.int64)
    values = autoconv[positions].copy()

    # Compute gradients vectorized: gradients[p, m] = 2 * dx * f_padded[(n_p - m) % M]
    m_arr = np.arange(N, dtype=np.int64)
    lookup = (positions[:, np.newaxis] - m_arr[np.newaxis, :]) % M  # (K, N)
    gradients = 2.0 * dx * f_padded[lookup]  # (K, N)

    return {
        "positions": positions,
        "values": values,
        "gradients": gradients,
        "max_val": max_val,
        "max_idx": max_idx,
    }
