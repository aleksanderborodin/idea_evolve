# Observations — Experimentator 1, Gen 5

## Key Discovery: 105-element Sidon set verified

The Rokicki-Dogon database at cube20.org/golomb/ provides the definitive constructive
lower bound for Sidon sets in {0, ..., 10000}:

- **105 elements** from an affine plane (ap) construction with q=107, multiplier=433
- Span = 9884 ≤ 10000 → valid Sidon set for our problem
- Previous pipeline best: 102 (Singer q=101 truncation)
- **Improvement: +3 elements**

## Algebraic ceiling established

Exhaustive search over all valid multipliers for q=103 (pp), q=107 (pp and ap), and q=109 (pp) confirms:

- **105 is the maximum from algebraic constructions for N=10000**
- The minimum span for 106 marks is 10135 (pp q=107, mul=255), exceeding the 10000 limit by 135
- No amount of multiplier search can reduce this — all 9072+ coprime multipliers were tested

## Structural observations

1. The 104-mark and 103-mark rulers are prefixes of each other (same construction, q=103).
   The 104-mark ruler is the 103-mark ruler with element 9581 appended.

2. The 105-mark ruler (ap q=107) is structurally different from the 104-mark ruler (pp q=103).
   Different prime power, different construction type, different element set.

3. The 105-mark ruler is maximal in [0, 10000] — zero additional elements can be added.
   This means 105 + greedy cannot reach 106.

## Implications for the pipeline

- **idea_020 (Rokicki-Dogon)** should be marked **CONFIRMED** with confidence 0.95.
  The database does contain 104-105 mark sets for span ≤ 10000, as hypothesized.
- **idea_008 (Singer q=101 truncation at 102)** is now superseded. The best algebraic
  construction is ap q=107 at 105, not pp q=101 at 102.
- **To reach 106+**, the pipeline must pursue non-algebraic approaches (CP-SAT/ILP,
  backtracking with intelligent pruning, or novel hybrid methods).
- **The gap to the theoretical upper bound (109) is now 4 elements**, not 7.
