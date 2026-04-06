# Observations — gen002_explore_1

## Directive
Explore non-Singer constructions for Sidon sets. Ruzsa and Bose-Chowla as described in the brief.

## What I Tried

### 1. Ruzsa construction {a·p + (a² mod p)} — FAILED, not Sidon
- Formula from brief: S = {a·p + (a² mod p) : a=0..p-1}
- Tested for primes 5, 7, 11, 13, 17, 23, 97, 101
- Works for p=5 and p=7 (0 violations), but FAILS for p≥11
- p=97: 312 violations; p=101: 304 violations
- Root cause: the "big part" a·p has spacing p, but the "small part" a²%p ∈ [0,p-1] can create carries. When a+b-c-d = ±1, we get (a+b-c-d)·p = r_c+r_d-r_a-r_b which can equal ±p since |RHS| < 2p. This allows sum collisions.
- The dead-end note in state_of_affairs ("Parabola/quadratic-residue constructions: Mathematically incorrect for large primes") is correct and applies here.

### 2. Bose-Chowla construction {i·p + g^i mod p} — ALSO FAILED
- Formula: S = {i·p + g^i%p : i=0..p-2}, g = primitive root mod p
- Same carry issue as Ruzsa — violations for p≥11
- p=97: 248 violations; p=101: 263 violations

### 3. Erdős-Turán construction {2pk + k² mod p} — CORRECT, gives 70 elements (sol01)
- Formula: S = {2·p·k + (k²%p) : k=1..p-1}, p=71
- Spacing 2p prevents carries: (a+b-c-d)·2p = r_c+r_d-r_a-r_b, |RHS| < 2p, so only carry=0 is possible
- p=71 gives 70 elements in {143..9941}, 0 violations — PROVEN SIDON
- p=71 is optimal: p=73 gives 68, p=67 gives 66
- Result: fitness=70

### 4. ET p=71 + Greedy Extension (sol02)
- After building ET(71), greedily scan {0..10000} for additional elements
- Added 4 elements: {0, 71, 235, 4219}
- Result: fitness=74

### 5. ET p=71 + Greedy + 1-opt swap search (sol03)
- For each element in the 74-element set: remove it, re-run greedy extension
- Accept if new size > old size (found one improvement: removing element 9010 → size 75)
- Converges at 75 elements — no single removal leads to ≥2 new elements being added
- Result: fitness=75

### 6. Randomized greedy + 1-opt, multiple restarts (sol04)
- Random shuffles of {0..10000} as greedy ordering, apply 1-opt after each
- 25-second time limit, ran multiple restarts
- All restarts converge to the same 75-element local optimum
- No restart found >75 elements
- Result: fitness=75

## Key Findings

1. **The brief's Ruzsa and Bose-Chowla formulas are wrong** — they do not produce Sidon sets for large primes. The state_of_affairs dead-end note about "parabola/quadratic-residue constructions being incorrect for large primes" applies to BOTH.

2. **Erdős-Turán IS a valid alternative to Singer**, giving 75 elements after local search. This is a genuinely different mathematical construction (uses Z field arithmetic, not GF(q³)), but is limited to ~75 elements for N=10000.

3. **The 99→100 barrier is inaccessible from ET-based constructions** without a fundamentally different approach. The ET set saturates at 75; 2-opt analysis showed negligible probability of improvement.

4. **ET uses only 24% of available differences** (vs Singer's ~50%), suggesting more room in theory, but the algebraic structure prevents exploitation via simple search.

5. **Greedy from random orderings caps at ~68** (consistent with state_of_affairs ceiling of 68 for search methods). Starting from ET(70) is necessary to reach 74-75.

## What Didn't Work / Dead Ends
- Ruzsa {a·p + a²%p}: not Sidon for p≥11
- Bose-Chowla {i·p + g^i%p}: not Sidon for p≥11
- Alternative embedding {a + p·(a²%p)}: also not Sidon for p≥7
- 2-opt analysis: probability ~10^{-11} that removing 2 elements allows 3 new ones
- Random restarts: all converge to 75, confirming strong local optimum

## Hypotheses for Future Work
- The 75-element ceiling may be the actual maximum for purely search-based methods
- Singer q=101 truncation (idea_008) remains the top priority for reaching 100
- Could combine ET(71) structure with Singer as a crossover target for genetic agents
- SA with temperature >0 accepting SIZE DECREASES might escape the 75 local optimum, but would need hours of runtime
