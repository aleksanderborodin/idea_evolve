"""Structure-preserving interpolation for sparse solution arrays.

Provides upsampling and downsampling that preserves near-zero regions
as exact zeros, avoiding the oscillation artifacts of cubic spline
interpolation on sparse arrays.
"""

import numpy as np


def interpolate_sparse(array, target_n, threshold=1e-4):
    """Upsample/downsample array preserving near-zero structure.

    Non-zero regions are interpolated with piecewise-linear interpolation.
    Regions where the original array is below threshold are set to exactly
    0.0 in the output (not interpolated through).

    Args:
        array: 1D array of non-negative values.
        target_n: Desired output length.
        threshold: Values below this are treated as structural zeros.
            Default 1e-4.

    Returns:
        result: 1D NumPy array of length target_n with non-negative values.

    Examples:
        >>> import numpy as np
        >>> arr = np.array([0.0, 0.0, 0.1, 0.2, 0.1, 0.0, 0.0])
        >>> upsampled = interpolate_sparse(arr, 14)
        >>> # Near-zero regions remain exactly 0.0
        >>> assert upsampled[0] == 0.0
        >>> assert upsampled[-1] == 0.0
    """
    arr = np.asarray(array, dtype=np.float64)
    n = len(arr)

    # Source and target normalized positions [0, 1]
    src_x = np.linspace(0.0, 1.0, n)
    dst_x = np.linspace(0.0, 1.0, target_n)

    # Piecewise-linear interpolation of values
    result = np.interp(dst_x, src_x, arr)

    # Build a zero mask: for each source element, mark if it's below threshold
    is_zero_src = (arr < threshold).astype(np.float64)

    # Interpolate the zero mask to target resolution
    # Use linear interp so transitions are smooth, then threshold at 0.5
    zero_mask_interp = np.interp(dst_x, src_x, is_zero_src)
    is_zero_dst = zero_mask_interp > 0.5

    # Zero out regions that were below threshold in the original
    result[is_zero_dst] = 0.0

    # Ensure non-negativity
    result = np.maximum(result, 0.0)

    return result
