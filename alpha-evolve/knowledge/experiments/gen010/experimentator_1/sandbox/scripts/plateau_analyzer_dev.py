"""Development version of plateau_analyzer — iterate here before shipping."""

import numpy as np


def plateau_analysis(f, autoconv=None, threshold_rel=1e-12):
    """
    Analyze the autoconvolution plateau structure.

    Args:
        f: (N,) array of non-negative function values
        autoconv: (optional) pre-computed autoconvolution array (SCALED by dx).
                  If None, computed from f via FFT.
        threshold_rel: relative threshold for near-max positions.
                       A position n is "plateau" if autoconv[n] >= max * (1 - threshold_rel).

    Returns dict with:
        positions: (K,) int array — indices where autoconv >= max * (1 - threshold_rel)
        values: (K,) float array — autoconv values at those positions
        gradients: (K, N) float array — per-element gradient of autoconv at each plateau position.
                   gradients[p, m] = d(autoconv[positions[p]]) / d(f[m])
        max_val: float — current max(autoconv)
        max_idx: int — argmax of autoconv
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

    # Compute gradients: gradients[p, m] = 2 * dx * f_padded[(positions[p] - m) % M]
    # Vectorized: for each plateau position p and each element m in [0, N),
    # index into f_padded at (positions[p] - m) % M
    K = len(positions)
    m_arr = np.arange(N, dtype=np.int64)  # (N,)
    # (K, N): indices into f_padded
    lookup = (positions[:, np.newaxis] - m_arr[np.newaxis, :]) % M  # (K, N)
    gradients = 2.0 * dx * f_padded[lookup]  # (K, N)

    return {
        "positions": positions,
        "values": values,
        "gradients": gradients,
        "max_val": max_val,
        "max_idx": max_idx,
    }


if __name__ == "__main__":
    # Quick smoke test
    rng = np.random.default_rng(42)
    N = 100
    f = np.abs(rng.standard_normal(N)) * 0.1
    result = plateau_analysis(f, threshold_rel=1e-6)
    print(f"N={N}, K={len(result['positions'])}, max_val={result['max_val']:.10f}")
    print(f"positions: {result['positions']}")
    print(f"gradients shape: {result['gradients'].shape}")
    print("Smoke test passed.")
