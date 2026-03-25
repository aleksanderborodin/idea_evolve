# fitness: 3.0
# Raised cosine (Hann window) — purely analytical, no optimization
# f(x) = 0.5 * (1 + cos(4*pi*x)) on [-1/4, 1/4]
# This window function has compact support, is smooth, and has well-studied
# autocorrelation properties. Zero at boundaries, peak at center.

import numpy as np


def entrypoint() -> np.ndarray:
    N = 1000
    # Uniform grid on [-1/4, 1/4]
    x = np.linspace(-0.25, 0.25, N, endpoint=False)
    # Hann window: 0.5 * (1 + cos(4*pi*x)) = cos^2(2*pi*x)
    # At x = +-1/4: cos(+-pi) = -1, so 0.5*(1-1) = 0. Zero at boundaries.
    # At x = 0: cos(0) = 1, so 0.5*(1+1) = 1. Peak at center.
    f = 0.5 * (1.0 + np.cos(4.0 * np.pi * x))
    return f.astype(np.float64)
