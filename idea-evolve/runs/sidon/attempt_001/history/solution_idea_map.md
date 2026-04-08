# Solution-Idea Map — Generations 1-7

## Generation 7

### gen007_exploit_1_sol01 (score: 105)
- Central: idea_022 (Bose-Chowla AP q=107), idea_020 (Rokicki-Dogon Database), idea_024 (VLNS — corrected formulation)
- Peripheral: idea_023 (Multiplier Optimization — mul=433), idea_019 (CP-SAT — binary VLNS engine)
- Novel elements: Corrected VLNS formulation (integer vars, domain [0,N]) running 85+ trials. All 106-targets INFEASIBLE. Candidate counting proof: for k≤44, EXACTLY k candidates exist (mathematical impossibility). Binary VLNS proves INFEASIBLE in <0.01s (presolve-level). Remove-50 target-105 → OPTIMAL. **Confirms F₂(10000) = 105 with high confidence. Pattern_016 and pattern_017 created.**

### gen007_explore_1_sol01 (score: 74)
- Central: idea_025 (Ruzsa-Lindström — 2p-scaled primitive root, p=71)
- Peripheral: idea_011 (ET Extension + VLNS k=3-15)
- Novel elements: First implementation of Ruzsa-Lindström. Proved naive formula invalid (264 violations for p=71). 2p-scaled version valid. 71→73 (greedy)→74 (VLNS 90s). **Fact_005 created (naive Ruzsa not valid in integers).**

### gen007_explore_1_sol02 (score: 65)
- Central: idea_001 (Randomized Greedy — best of 20 seeds)
- Peripheral: idea_002 (Local Search — aggressive VLNS k=10-40)
- Novel elements: Multi-seed random greedy (best=62 from 20 trials) + aggressive VLNS for 110s. Result: 65. Confirms random greedy + large-neighborhood search is inferior to algebraic approaches.

### gen007_explore_1_sol03 (score: 75)
- Central: idea_025 (Ruzsa-Lindström — 2p-scaled, p=61 and p=71), idea_011 (ET Extension + fast VLNS)
- Peripheral: idea_002 (Local Search — fast blocked-set VLNS)
- Novel elements: Multi-start from two Ruzsa seeds (p=61→70, p=71→75). Fast blocked-set candidate identification (O(|S|*|diffs|)). Confirms 75-ceiling is same basin as ET(71). **Pattern_018 created (Ruzsa and ET converge to same basin).**

### gen007_full_1 (score: N/A — no solutions)
- Central: N/A
- Novel elements: Session interrupted during context reading. Planned binary variable CP-SAT maximize formulation (EXP-5) not implemented. Context gathering confirmed all prior findings.

### gen007_research_1 (score: N/A — no solutions)
- Central: N/A
- Novel elements: Live web searches for F₂(10000). Key findings: (1) No published F₂(10000) > 105 anywhere. (2) OEIS A003022 only covers n≤28 proven optimal. (3) cube20.org starts at 160 marks. (4) rokicki_data.py has no BEST_106 entry. (5) Gen6 VLNS code already had y[i]!=fv constraints — "formulation bug" diagnosis likely wrong. (6) Tabu search with swap-then-fill identified as best untried heuristic. (7) Eberhard 2023 confirms dense Sidon sets come from projective planes, but nondesarguesian planes don't exist for prime orders. **Pattern_016 evidence contributed.**

### gen007_experimentator_1 (score: N/A — helper delivery only)
- Central: idea_019 (CP-SAT), idea_024 (VLNS)
- Novel elements: Delivered `helpers/cpsat.py` with 3 functions: `solve_sidon_cpsat` (binary/element formulation), `vlns_sidon` (corrected VLNS with unified per-difference constraints), `vlns_batch`. All self-tested. Found and fixed free-to-free diff collision bug in initial implementation. 9 real VLNS trials: all OPTIMAL at 105 in <0.1s. **Resolves 3-generation-old request for cpsat.py helper.**

## Generation 6

### gen006_exploit_1_sol01 (score: 105)
- Central: idea_022 (Bose-Chowla AP q=107), idea_020 (Rokicki-Dogon Database)
- Peripheral: idea_023 (Multiplier Optimization — mul=433)
- Novel elements: Exhaustive remove-k perturbation (k=2-104, 27K+ trials). Discovered perfect self-healing property: removing k elements always opens exactly k addable slots = the removed elements. Singer pp q=107/109/113 exhaustive multiplier search. Swap walk exploration — all 105-sets are greedy-maximal. **Pattern_014 created from these findings.**

### gen006_explore_1_sol01 (score: 66)
- Central: idea_005 (Backtracking with Pruning — FIRST TEST)
- Peripheral: idea_001 (Randomized restarts — shuffled candidate order)
- Novel elements: DFS with position-count upper bound pruning on N=10000. Sequential DFS IS greedy (produces exact same 66-element set). Randomized restarts with shuffled candidate order also cap at 66. 27s total runtime. **Debunks idea_005.**

### gen006_explore_1_sol02 (score: 75)
- Central: idea_011 (ET Extension with Local Search), idea_009 (Erdos-Turan p=71)
- Peripheral: idea_002 (Local Search — 1-opt, 2-opt, LNS)
- Novel elements: Full pipeline ET(71)→greedy→1-opt→2-opt→LNS. 2-opt too slow (O(n²·N)). Confirms 75 ceiling.

### gen006_explore_1_sol03 (score: 75)
- Central: idea_011 (ET Extension with Local Search), idea_009 (Erdos-Turan p=71)
- Peripheral: idea_002 (Local Search — aggressive LNS k=2-15)
- Novel elements: ~20 LNS iterations with k=2-15 random element removal + greedy re-extend + 1-opt. Cannot escape 75 plateau.

### gen006_explore_1_sol04 (score: 75)
- Central: idea_011 (ET Extension with Local Search)
- Peripheral: idea_001 (Randomized restarts), idea_009 (ET base with perturbation)
- Novel elements: Multiple restart modes: fully random greedy, ET base + random extension, ET-perturbed base. ~6-8 complete restart cycles. All converge to 75 or lower.

### gen006_full_1_sol01 (score: 105)
- Central: idea_020 (Rokicki-Dogon Database), idea_022 (Bose-Chowla AP)
- Peripheral: none
- Novel elements: Hardcoded 105-mark baseline. No search, just the known best.

### gen006_full_1_sol02 (score: 105)
- Central: idea_019 (CP-SAT k=106), idea_020 (Rokicki-Dogon — warm-start hint)
- Peripheral: idea_022 (Bose-Chowla — fallback)
- Novel elements: CP-SAT with 105-mark hint, 1200s/16 workers → UNKNOWN. k=104 also UNKNOWN (30s). Linearization/symmetry parameters didn't help. Falls back to 105-mark set.

### gen006_full_1_sol03 (score: 105)
- Central: idea_024 (VLNS — NEW), idea_020 (Rokicki-Dogon — fixed elements)
- Peripheral: idea_019 (CP-SAT — solver engine), idea_022 (Bose-Chowla — fallback)
- Novel elements: VLNS: fix 85 of 105 elements, CP-SAT for 21 free. 9 trials all INFEASIBLE <1s. Likely formulation bug (abs-equality domain conflict). Falls back to 105-mark set.

### gen006_full_1_sol04 (score: 105)
- Central: idea_019 (CP-SAT — binary search on N)
- Peripheral: idea_022 (Bose-Chowla — fallback)
- Novel elements: Tested N=10000, 10200, 10500, 11000, 12000, 15000 with 120s CP-SAT each. All UNKNOWN. k=106 is hard regardless of N.

## Generation 5

### gen005_experimentator_1_sol01 (score: 105) — NEW PIPELINE BEST
- Central: idea_020 (Rokicki-Dogon Database), idea_022 (Bose-Chowla Affine Plane Construction)
- Peripheral: idea_023 (Multiplier Optimization — mul=433 for q=107)
- Novel elements: Downloaded and parsed Rokicki-Dogon database (cube20.org/golomb), extracted 105-mark ruler from rulers-all-00 file. Construction type: ap (affine plane), q=107, multiplier=433, span=9884. Hardcoded mark list. Set is maximal — zero elements can be added.

### gen005_experimentator_1_sol02 (score: 104)
- Central: idea_020 (Rokicki-Dogon Database), idea_006 (Singer Difference Set — pp type)
- Peripheral: idea_023 (Multiplier Optimization — mul=400 for q=103)
- Novel elements: Singer pp q=103 with multiplier=400 gives 104 marks in span=9581. This explains the 4-generation mystery: previous q=103 attempts used multiplier=1 and got only 102.

### gen005_experimentator_1_sol03 (score: 103)
- Central: idea_020 (Rokicki-Dogon Database), idea_006 (Singer Difference Set — pp type)
- Peripheral: idea_023 (Multiplier Optimization — mul=400 for q=103)
- Novel elements: Same as sol02 but 103-mark subset (span=9408). The 104-mark ruler is this set plus one additional element (9581).

### gen005_explore_1_sol01 (score: 69)
- Central: idea_021 (Beam Search Greedy — k=30, 3 candidates)
- Peripheral: idea_003 (Difference-Aware — sorted valid-candidate list)

### gen005_explore_1_sol02 (score: 67)
- Central: idea_021 (Beam Search Greedy — k=20, spread sampling)

### gen005_explore_1_sol03 (score: 67)
- Central: idea_021 (Beam Search Greedy — k=50, lookahead scoring)

### gen005_explore_1_sol04 (score: 67)
- Central: idea_021 (Beam Search Greedy — multi-seed, k=5 per seed)

### gen005_explore_1_sol05 (score: 70)
- Central: idea_021 (Beam Search Greedy — k=500, greedy candidates)

### gen005_explore_1_sol06 (score: 66)
- Central: idea_021 (Beam Search Greedy — k=500, percentile sampling)

### gen005_explore_1_sol07 (score: 70)
- Central: idea_021 (Beam Search Greedy — k=800, greedy candidates)

### gen005_explore_2_sol01 (score: 0, INVALID — 312 violations)
- Central: idea_004 (Modular Arithmetic — naive Bose-Chowla formula)
- Peripheral: idea_003 (Difference-Aware — greedy extension after construction)

### gen005_full_1_sol01 (score: 102)
- Central: idea_019 (CP-SAT Integer Formulation)
- Peripheral: idea_008 (Singer q=101 — fallback after UNKNOWN)

### gen005_research_1_sol01 (score: 105) — NEW PIPELINE BEST (independent confirmation)
- Central: idea_020 (Rokicki-Dogon Database), idea_022 (Bose-Chowla Affine Plane)
- Peripheral: idea_023 (Multiplier Optimization)

### gen005_research_1_sol02 (score: 104)
- Central: idea_020 (Rokicki-Dogon Database), idea_006 (Singer pp q=103)
- Peripheral: idea_023 (Multiplier Optimization — mul=400)

## Generation 4

### gen004_explore_1_sol01 (score: 68)
- Central: idea_016 (Min-Blocking Greedy)
- Peripheral: idea_003 (Difference-Aware — numpy-vectorized blocking computation)

### gen004_explore_2_sol01 (score: 69)
- Central: idea_016 (Min-Blocking Greedy — corrected implementation)
- Peripheral: idea_003 (Difference-Aware — midpoint blocking fix)

### gen004_full_1_sol01 (score: 102)
- Central: idea_019 (CP-SAT Integer Formulation)
- Peripheral: idea_008 (Singer q=101 — used as warm-start hint and fallback)

### gen004_research_1_sol01 (score: 102)
- Central: idea_006 (Singer Difference Set — q=103 via singer.py helper)
- Peripheral: idea_008 (Singer truncation — optimal cyclic shift search)

## Generation 3

### gen003_exploit_1_sol01 (score: 102)
- Central: idea_008 (Singer q=101 Truncation), idea_017 (Large-k Perturbation)

### gen003_explore_1_sol01 (score: 63)
- Central: idea_014 (Probabilistic Alteration)

### gen003_explore_1_sol02 (score: 0, INVALID — 280849 violations)
- Central: idea_016 (Min-Blocking Greedy)

### gen003_explore_2_sol01 (score: 63)
- Central: idea_001 (Randomized Greedy with Restarts)

### gen003_explore_2_sol02 (score: 0, INVALID — 7 violations)
- Central: idea_002 (Local Search — LNS)

### gen003_explore_2_sol03 (score: 67)
- Central: idea_002 (Local Search — LNS)

### gen003_explore_2_sol04 (score: 65)
- Central: idea_003 (Difference-Aware — spread-first heuristic)

### gen003_explore_2_sol05 (score: 69)
- Central: idea_015 (Fibonacci/Exponential Ordering Greedy)

### gen003_explore_2_sol06 (score: 68)
- Central: idea_018 (SA with Violation Relaxation)

## Generation 2

### gen002_exploit_1_sol01 (score: 102)
- Central: idea_008 (Singer q=101 Truncation), idea_004 (Modular Arithmetic Structure)

### gen002_exploit_1_sol02 (score: 102)
- Central: idea_008 (Singer q=101 Truncation)

### gen002_exploit_1_sol03 (score: 102)
- Central: idea_008 (Singer q=101 Truncation), idea_004 (Modular Arithmetic)

### gen002_exploit_2_sol01 (score: 99)
- Central: idea_007 (Singer q=97 Perturbation), idea_010 (SA from Algebraic Seed)

### gen002_exploit_2_sol02 (score: 102)
- Central: idea_008 (Singer q=101 Truncation)

### gen002_exploit_2_sol03 (score: 102)
- Central: idea_008 (Singer q=101 Truncation), idea_010 (SA from Algebraic Seed)

### gen002_exploit_2_sol04 (score: 102)
- Central: idea_008 (Singer q=101 Truncation), idea_012 (Singer q=101 Perturbation)

### gen002_explore_1_sol01 (score: 70)
- Central: idea_009 (Erdos-Turan Construction)

### gen002_explore_1_sol02 (score: 74)
- Central: idea_009 (Erdos-Turan), idea_011 (ET Extension with Local Search)

### gen002_explore_1_sol03 (score: 75)
- Central: idea_009 (Erdos-Turan), idea_011 (ET Extension with Local Search)

### gen002_explore_1_sol04 (score: 75)
- Central: idea_011 (ET Extension with Local Search)

## Generation 1

### gen001_explore_1_sol01 (score: 98)
- Central: idea_006 (Singer Difference Set Construction), idea_004 (Modular Arithmetic Structure)

### gen001_explore_1_sol02 (score: 99)
- Central: idea_006 (Singer Difference Set), idea_007 (Singer Set Perturbation)

### gen001_explore_1_sol03 (score: 99)
- Central: idea_006 (Singer Difference Set), idea_007 (Singer Set Perturbation)

### gen001_explore_1_sol04 (score: 99)
- Central: idea_006 (Singer Difference Set), idea_007 (Singer Set Perturbation)

### gen001_explore_2_sol01 (score: 68)
- Central: idea_002 (Local Search / Simulated Annealing)

### gen001_explore_2_sol02 (score: 0, INVALID — 1 violation)
- Central: idea_002 (Local Search — ILS with blocking score)

### gen001_explore_2_sol03 (score: 66)
- Central: idea_002 (Local Search — ILS)

### gen001_explore_2_sol04 (score: 67)
- Central: idea_002 (Local Search — targeted 2-opt)

### gen001_explore_2_sol05 (score: 66)
- Central: idea_002 (Local Search — exhaustive 2-opt)

### gen001_explore_2_sol06 (score: 0, INVALID — 1 violation)
- Central: idea_002 (Local Search — fixed 2-opt)

### gen001_full_1_sol01 (score: 66)
- Central: idea_001 (Randomized Greedy), idea_002 (Local Search — ILS)
