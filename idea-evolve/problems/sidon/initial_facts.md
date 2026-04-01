# Initial Facts for Sidon Sets

## fact_001: Greedy Baseline Score
The simple greedy algorithm (add smallest valid element) produces a Sidon set
of size 66 for N=10000. This is the starting baseline.

## fact_002: Theoretical Upper Bound
For a Sidon set in {0, ..., N}, the maximum size is at most sqrt(N) + O(N^{1/4}).
For N=10000, this gives an upper bound of approximately 100-102.

## fact_003: Evaluation Speed
evaluate.py runs in under 1 second for sets of ~100 elements. The bottleneck is
the O(n^2) pairwise sum check in validate.py. Agents can iterate quickly.

## fact_004: Violation Tolerance
If a solution has violations (repeated pairwise sums), the validator extracts
the largest valid Sidon subset using a greedy algorithm. So submitting a
slightly-too-large set with a few violations can still score well — the
extracted subset may be larger than a perfectly valid smaller set.

## fact_005: Difference Set Equivalence
A set S is Sidon if and only if all positive differences (b-a for a<b in S)
are distinct. This dual view (sums vs differences) can suggest different
construction strategies. The helpers provide both `count_violations` (sums)
and `differences` (differences) for analysis.
