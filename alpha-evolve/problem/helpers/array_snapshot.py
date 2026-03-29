"""Load/save pre-optimized arrays for instant access.

Provides utilities to bake optimized arrays as .npy files and load them
instantly, avoiding expensive re-optimization on every entrypoint() call.
Eliminates non-reproducibility from deadline-based optimization pipelines.

Usage:
    from helpers.array_snapshot import load_best_array, save_array
    f = load_best_array()  # loads from population/top/best_array.npy
    f = load_best_array("/path/to/custom.npy")
"""

import numpy as np
from pathlib import Path


def load_best_array(path=None):
    """Load the best baked array from .npy file.

    Args:
        path: Path to .npy file. If None, loads from
              population/top/best_array.npy (relative to problem/helpers/).

    Returns:
        numpy.ndarray: Float64 array of function values on [-1/4, 1/4].

    Raises:
        FileNotFoundError: If the .npy file does not exist.

    Examples:
        >>> f = load_best_array()  # default location
        >>> f = load_best_array("/tmp/my_array.npy")  # custom path
    """
    if path is None:
        path = Path(__file__).parent.parent.parent / "population" / "top" / "best_array.npy"
    f = np.load(str(path))
    return np.asarray(f, dtype=np.float64)


def save_array(f_array, path, metadata=None):
    """Save an optimized array to .npy for instant loading.

    Args:
        f_array: 1D numpy array of function values.
        path: Destination path for the .npy file.
        metadata: Optional dict of metadata (not saved in .npy; caller
                  should write separately if needed).

    Examples:
        >>> import numpy as np
        >>> f = np.ones(100)
        >>> save_array(f, "/tmp/test_array.npy")
    """
    np.save(str(path), np.asarray(f_array, dtype=np.float64))
