# Solution-Idea Map — Generations 1-4

## Generation 4

### gen004_explore_1_sol01 (score: 68)
- Central: idea_016 (Min-Blocking Greedy)
- Peripheral: idea_003 (Difference-Aware — numpy-vectorized blocking computation)
- Novel elements: Numpy-vectorized min-blocking greedy. Had duplicate bug (valid_arr[chosen] not cleared after selection). Reported 69 from internal test but evaluate.py scores 68 due to the bug. Confirms non-algebraic greedy ceiling.

### gen004_explore_2_sol01 (score: 69)
- Central: idea_016 (Min-Blocking Greedy — corrected implementation)
- Peripheral: idea_003 (Difference-Aware — midpoint blocking fix)
- Novel elements: Correct min-blocking greedy with proper midpoint invalidation. Fixed the gen 3 bug. Also tested Ruzsa quadratic (violations in integers, score 0) and CRT product (violations, score 0) before settling on min-blocking. 19.6s runtime.

### gen004_full_1_sol01 (score: 102)
- Central: idea_019 (CP-SAT Integer Formulation)
- Peripheral: idea_008 (Singer q=101 — used as warm-start hint and fallback)
- Novel elements: First working ILP formulation for Sidon sets. k integer variables + AllDifferent on differences. Proved Singer suboptimal for small N (q=7: 8→10, q=11: 12→13). CP-SAT UNKNOWN for k=103 at N=10000 after 600s. Falls back to Singer 102 baseline.

### gen004_research_1_sol01 (score: 102)
- Central: idea_006 (Singer Difference Set — q=103 via singer.py helper)
- Peripheral: idea_008 (Singer truncation — optimal cyclic shift search)
- Novel elements: Singer q=103 with optimal shift search. Min span = 10290 > 10000, so only 102 elements fit. No improvement over q=101. Key contribution: discovered Rokicki-Dogon database showing 105-mark constructions exist.

## Generation 3

### gen003_exploit_1_sol01 (score: 102)
- Central: idea_008 (Singer q=101 Truncation), idea_017 (Large-k Perturbation)
- Peripheral: idea_007 (Perturbation methodology)
- Novel elements: Tested k=5-25 with strategic (top/bottom blocker) and random removal. 4000+ trials. No improvement over 102. Confirms perturbation futility.

### gen003_explore_1_sol01 (score: 63)
- Central: idea_014 (Probabilistic Alteration)
- Peripheral: idea_001 (Randomized restarts — shuffled greedy extension)
- Novel elements: Random sampling with p=0.010-0.015, repair by removing highest-violation elements, greedy extend. 160 configs tested. Significantly below greedy baseline.

### gen003_explore_1_sol02 (score: 0, INVALID — 280849 violations)
- Central: idea_016 (Min-Blocking Greedy)
- Peripheral: idea_003 (Difference-Aware Construction)
- Novel elements: Min-blocking candidate selection via conflict array. CRITICAL BUG: does not verify Sidon property when adding elements. Produced 775 elements with 280849 violations in 1728s. Concept needs correct implementation with proper used_diffs enforcement.

### gen003_explore_2_sol01 (score: 63)
- Central: idea_001 (Randomized Greedy with Restarts)
- Peripheral: none
- Novel elements: 25s of random-shuffle greedy restarts. Confirms 58-63 range for random ordering.

### gen003_explore_2_sol02 (score: 0, INVALID — 7 violations)
- Central: idea_002 (Local Search — LNS)
- Peripheral: idea_003 (Difference-Aware — incremental diff tracking)
- Novel elements: Bug in diff computation: _build_used_diffs didn't use abs() for unsorted input. 68 raw elements but 7 violations → fitness 0.

### gen003_explore_2_sol03 (score: 67)
- Central: idea_002 (Local Search — LNS)
- Peripheral: none
- Novel elements: Fixed abs() bug from sol02. Adaptive k (3-35). Reached 67 from greedy-66 seed.

### gen003_explore_2_sol04 (score: 65)
- Central: idea_003 (Difference-Aware — spread-first heuristic)
- Peripheral: idea_002 (Local Search — LNS improvement phase)
- Novel elements: "Spread-first" greedy: pick valid candidate maximizing min-distance to existing elements. Sampled 150 candidates per step. Underperformed standard greedy (65 < 66).

### gen003_explore_2_sol05 (score: 69)
- Central: idea_015 (Fibonacci/Exponential Ordering Greedy)
- Peripheral: idea_002 (LNS post-processing — no improvement)
- Novel elements: Wide Fibonacci parameter search (2400+ configs). Best: 69 elements. New non-algebraic record. Geometric and Wythoff orderings ineffective.

### gen003_explore_2_sol06 (score: 68)
- Central: idea_018 (SA with Violation Relaxation)
- Peripheral: idea_015 (Fibonacci ordering — seed construction)
- Novel elements: Objective = size - 8*violations. 58 seconds SA from 68-element Fibonacci set. No improvement. Confirms SA futility for non-algebraic seeds too.

## Generation 2

### gen002_exploit_1_sol01 (score: 102)
- Central: idea_008 (Singer q=101 Truncation), idea_004 (Modular Arithmetic Structure)
- Peripheral: idea_007 (Perturbation — attempted but no improvement)
- Novel elements: Dynamic polynomial search over all 1054 irreducible cubics; exhaustive cyclic shift search; greedy extension (adds 0)

### gen002_exploit_1_sol02 (score: 102)
- Central: idea_008 (Singer q=101 Truncation)
- Peripheral: none
- Novel elements: Hardcoded 102-element set with optimal shift d=2337. Instant evaluation (0.003s). Canonical reference solution.

### gen002_exploit_1_sol03 (score: 102)
- Central: idea_008 (Singer q=101 Truncation), idea_004 (Modular Arithmetic)
- Peripheral: idea_007 (Perturbation — attempted greedy extension, adds 0)
- Novel elements: Hardcoded polynomial parameters (x³-3x-1, primitive (0,0,2)); confirmed all polynomials give equivalent results

### gen002_exploit_2_sol01 (score: 99)
- Central: idea_007 (Singer q=97 Perturbation), idea_010 (SA from Algebraic Seed)
- Peripheral: idea_002 (Local Search — SA framework)
- Novel elements: True Boltzmann SA with incremental diff tracking; 3 move types (swap, multi-remove, targeted); 114s runtime. No improvement over seed.

### gen002_exploit_2_sol02 (score: 102)
- Central: idea_008 (Singer q=101 Truncation)
- Peripheral: none
- Novel elements: Independent implementation of Singer q=101; confirms exploit_1's result

### gen002_exploit_2_sol03 (score: 102)
- Central: idea_008 (Singer q=101 Truncation), idea_010 (SA from Algebraic Seed)
- Peripheral: idea_002 (Local Search — SA framework)
- Novel elements: SA from 102-element base; blocker analysis revealing 40+ minimum blockers per candidate

### gen002_exploit_2_sol04 (score: 102)
- Central: idea_008 (Singer q=101 Truncation), idea_012 (Singer q=101 Perturbation)
- Peripheral: idea_003 (Difference-Aware — partial shifts to free differences)
- Novel elements: Tested partial shifts (98-101 Singer elements) + greedy extension; none exceeded 102

### gen002_explore_1_sol01 (score: 70)
- Central: idea_009 (Erdos-Turan Construction)
- Peripheral: none
- Novel elements: ET(71) pure construction. Proved Ruzsa/Bose-Chowla formulas wrong for large primes.

### gen002_explore_1_sol02 (score: 74)
- Central: idea_009 (Erdos-Turan), idea_011 (ET Extension with Local Search)
- Peripheral: idea_003 (Difference-Aware — greedy candidate selection)
- Novel elements: ET(71) + greedy extension adds 4 elements (0, 71, 235, 4219)

### gen002_explore_1_sol03 (score: 75)
- Central: idea_009 (Erdos-Turan), idea_011 (ET Extension with Local Search)
- Peripheral: idea_002 (Local Search — 1-opt swap)
- Novel elements: 1-opt improves ET+greedy from 74→75; removing element 9010 enables +1

### gen002_explore_1_sol04 (score: 75)
- Central: idea_011 (ET Extension with Local Search)
- Peripheral: idea_001 (Randomized restarts)
- Novel elements: 25 random restarts all converge to 75, confirming robust local optimum

## Generation 1

### gen001_explore_1_sol01 (score: 98)
- Central: idea_006 (Singer Difference Set Construction), idea_004 (Modular Arithmetic Structure)
- Peripheral: none
- Novel elements: GF(97³) implementation via irreducible cubic; primitive element search

### gen001_explore_1_sol02 (score: 99)
- Central: idea_006 (Singer Difference Set), idea_007 (Singer Set Perturbation)
- Peripheral: idea_002 (Local Search — greedy extension after removal)
- Novel elements: Remove 1-3 Singer elements, extend with candidates from full range {0..10000}

### gen001_explore_1_sol03 (score: 99)
- Central: idea_006 (Singer Difference Set), idea_007 (Singer Set Perturbation)
- Peripheral: idea_001 (Randomized restarts — multiple random seeds for perturbation)
- Novel elements: Larger perturbation window (k≤15 removals); multiple random seeds

### gen001_explore_1_sol04 (score: 99)
- Central: idea_006 (Singer Difference Set), idea_007 (Singer Set Perturbation)
- Peripheral: idea_003 (Difference-Aware — targeted blocker analysis)
- Novel elements: Two-phase approach: quick 99 from sol02, then targeted 99→100 push via blocker removal

### gen001_explore_2_sol01 (score: 68)
- Central: idea_002 (Local Search / Simulated Annealing)
- Peripheral: idea_003 (Difference-Aware — incremental diff tracking)
- Novel elements: Three move types (add, swap, remove-k-refill); linear cooling schedule

### gen001_explore_2_sol02 (score: 0, INVALID — 1 violation)
- Central: idea_002 (Local Search — ILS with blocking score)
- Peripheral: idea_003 (Difference-Aware — blocking score heuristic)
- Novel elements: Blocking score metric for removal prioritization; implementation bug caused violation

### gen001_explore_2_sol03 (score: 66)
- Central: idea_002 (Local Search — ILS)
- Peripheral: none
- Novel elements: Numpy-vectorized candidate finding; no improvement over baseline

### gen001_explore_2_sol04 (score: 67)
- Central: idea_002 (Local Search — targeted 2-opt)
- Peripheral: none
- Novel elements: Single-removal gain analysis; random double-removal sampling

### gen001_explore_2_sol05 (score: 66)
- Central: idea_002 (Local Search — exhaustive 2-opt)
- Peripheral: none
- Novel elements: Bug: greedy re-added removed elements, producing net-0 gain

### gen001_explore_2_sol06 (score: 0, INVALID — 1 violation)
- Central: idea_002 (Local Search — fixed 2-opt)
- Peripheral: none
- Novel elements: Attempted fix of sol05 bug; introduced new validity violation

### gen001_full_1_sol01 (score: 66)
- Central: idea_001 (Randomized Greedy), idea_002 (Local Search — ILS)
- Peripheral: idea_004 (Modular Arithmetic — parabola attempt, FAILED)
- Novel elements: Parabola construction {i*p + i²%p} tried but failed for p=101 (312 violations);
  vectorized numpy ILS; confirmed greedy-66 tightness
