# Observations — gen007_explore_1

## What I Tried

### Construction 1: Ruzsa-Lindström (primitive root, 2p scaling)

**Formula**: S = {x*2p + g^x mod p : x=0,...,p-1} for prime p, g=primitive_root(p)

- The naive primitive root construction {xp + g^x mod p} is NOT a valid Sidon set (264 violations for p=97, g=5). The carry between the low part (g^x mod p) and high part (xp) creates sum collisions.
- Fix: scale high part by 2p instead of p. Since 2p > 2*(p-1) (max low-part variation), carries cannot bridge adjacent "rows". This gives a provably valid Sidon set.
- This is **structurally different** from the quadratic ET construction {2ip + i² mod p}: it uses the exponential map g^x instead of the polynomial i².
- For p=71, g=7: 71 elements in [1, 9941]. Valid Sidon set.
- For p=61, g=2: 61 elements in [1, 7321]. Valid Sidon set.

### Construction 2: Quadratic ET (sanity check)

- S = {2ip + (i² mod p) : i=0,...,p-1} — the Erdős-Turán/quadratic construction
- For p=71: 71 elements in [0, 9941]. Valid Sidon set.
- This appears to be the same as "ET(71)" in the state of affairs.

### Local Search: VLNS (Variable Large Neighborhood Search)

- All solutions used VLNS: remove k random elements, greedily repair with random candidate order.
- Two variants: slow VLNS (k=3-15, random shuffle repair) and fast VLNS (blocked-set precomputation for O(|S|*|diffs|) candidate identification).
- Fast VLNS gets ~100 iters/sec vs ~155 iters/sec for slow VLNS (fast is slower per iteration but finds addable candidates more reliably).

## Results

| Solution | Starting Construction | Base Size | After Greedy | After VLNS | Fitness |
|----------|----------------------|-----------|--------------|------------|---------|
| sol01    | Ruzsa prim-root p=71 | 71        | 73           | 74         | **74**  |
| sol02    | Random greedy (best of 20 seeds) | 62 | 62      | 65         | **65**  |
| sol03    | Ruzsa p=61 + Ruzsa p=71 multi-start | 68/73 | 68/73 | 75      | **75**  |

## What I Learned

### 1. The primitive root construction doesn't give more than ET(71)

The Ruzsa primitive root construction (2p-scaled) with p=71 gives 71 elements — same count as the quadratic construction. After greedy extension and VLNS, both converge to the same ceiling of **75 elements**. This confirms they are in the **same basin**.

### 2. The 75-element ceiling is robust across Ruzsa variants

- p=61 primitive root → 70 after VLNS (30s)
- p=71 primitive root → 75 after VLNS (60s)
- p=71 primitive root (more iterations) → 75, stuck

This matches the state of affairs: "ET(71)+1-opt hard ceiling 75 (30+ restarts)".

### 3. Random greedy starts are much worse

Random-order greedy (best of 20 seeds) gives only 62 elements. VLNS from 62 elements reaches only 65. The algebraic constructions are significantly better starting points, but none break through 75 from the 71-element regime.

### 4. The primitive root construction is NOT the breakthrough we need

The brief described the Ruzsa-Lindstrom construction as potentially being "in a different basin of attraction" than Bose-Chowla. Experimentally, the basin is similar to ET(71): ceiling ~75. The 30-element gap to Bose-Chowla (105) is NOT bridgeable by local search from a 71-element algebraic start.

### 5. The naive primitive root construction has violations

{xp + g^x mod p} for p=97, g=5 produces 97 elements with 264 violations. The idea in idea_025 (claiming this is a p-element Sidon set in {0,...,p²-1}) appears incorrect for integer arithmetic — it works modulo p² but not as integers.

## Why This Happened

The Sidon set problem has a fundamental gap: algebraic constructions with ~71 elements densely cover the difference space, leaving very few "clean" candidates for extension. With 71 elements using C(71,2)=2485 differences, about 25% of the [1, 9941] difference range is blocked. Each new element requires ALL its pairwise distances to be unblocked. With 75 elements using 2775 differences, the pool of addable candidates drops to essentially 0.

The 105-element Bose-Chowla construction lives in a completely different region: it has 105 elements in a set with the "self-healing" property. There is NO KNOWN local search path from 75 to 106.

## What Would Have Helped

1. A CP-SAT helper (helpers/cpsat.py) that the brief mentions has been requested for 3 consecutive generations. This would let me formulate "find 76-element Sidon set in [0,10000]" as an exact optimization problem and actually solve it.
2. Direct access to the OEIS A003022 database or confirmation of F₂(10000) — knowing the true maximum would inform whether 106 is achievable at all.
3. The VLNS formulation bug fix — the system mentions that VLNS with a fixed formulation is the highest-priority next step.

## Hypotheses for Future Agents

1. The 75 ceiling for 71-element starts appears robust. All algebraic constructions with p~71 converge here.
2. The only path to 106 is: (a) Fix VLNS formulation bug and run exact solver, (b) CP-SAT maximize formulation, (c) find a new algebraic construction with >105 elements.
3. The "Ruzsa-Lindstrom as different basin" hypothesis appears FALSE. Both exponential and polynomial constructions with p=71 land in the same basin.
4. The blocked-set fast VLNS (`fast_find_addable`) is a useful helper for future search agents — it speeds up candidate identification from O(N*|S|) to O(|S|*|diffs|).
