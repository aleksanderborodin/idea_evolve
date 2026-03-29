import numpy as np


# Problem parameters
N = 8   # permutation length
D = 5   # minimum Hamming distance


def validate(perms):
    perms = np.asarray(perms, dtype=int)

    if perms.ndim != 2:
        raise ValueError(f"Expected 2D array, got shape {perms.shape}")

    K, n = perms.shape

    if K == 0:
        raise ValueError("Code cannot be empty")

    if n != N:
        raise ValueError(f"Permutation length must be {N}, got {n}")

    # Check each row is a valid permutation of {0, ..., N-1}
    expected = np.arange(N)
    for i in range(K):
        if not np.array_equal(np.sort(perms[i]), expected):
            raise ValueError(
                f"Row {i} is not a valid permutation of {{0,...,{N-1}}}: {perms[i]}"
            )

    # Check for duplicate rows
    unique_rows = set(map(tuple, perms))
    if len(unique_rows) < K:
        raise ValueError(
            f"Duplicate permutations found: {K} rows but only {len(unique_rows)} unique"
        )

    # Check all pairwise Hamming distances >= D
    # Vectorized: compare all pairs
    min_dist = N  # max possible distance
    for i in range(K):
        # Compare row i with all rows j > i
        if i + 1 < K:
            dists = np.sum(perms[i] != perms[i + 1:], axis=1)
            pair_min = np.min(dists)
            if pair_min < D:
                j = i + 1 + np.argmin(dists)
                raise ValueError(
                    f"Hamming distance between rows {i} and {j} is {pair_min} < {D}"
                )
            min_dist = min(min_dist, pair_min)

    return {"fitness": int(K), "is_valid": 1, "min_distance": int(min_dist)}
