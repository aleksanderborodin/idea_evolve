# Backward compatibility shim — new code should use: from helpers.core import <function>
from helpers.core import hamming_distance, check_code, min_distance, pairwise_distances  # noqa: F401
