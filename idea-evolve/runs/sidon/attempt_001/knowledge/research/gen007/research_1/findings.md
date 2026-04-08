# Research Findings — F₂(10000) Record, Algorithm Survey, and VLNS Diagnosis

## Summary

This session performed live web searches (not training-data-only) to answer the six-generation open question about F₂(10000). Key findings: **no published record of a Sidon set larger than 105 in {0,...,10000} was found** — the pipeline is likely at or near the known optimum. The VLNS infeasibility may be genuine (not just a bug). Tabu search with swap-then-fill is the best untried heuristic. Two recent papers (arXiv:1902.08660, arXiv:2107.05744) provide actionable algorithm guidance.

---

## Finding 1: F₂(10000) — Best Published Record Appears to Be 105

**Source labels:** `[web: cube20.org]`, `[web: oeis.org]`, `[web: arxiv.org]`

**What was searched:**
- OEIS A003022 (Optimal Golomb ruler lengths)
- cube20.org/golomb/ (Rokicki-Dogon database)
- Distributed searches for "106 marks Golomb ruler span", "B2 sequence N=10000 maximum", "Sidon set record 10000"
- arXiv papers 2020-2024 on Sidon sets

**What was found:**

1. **`rokicki_data.py` (already on disk) contains only BEST_105, BEST_104, BEST_102.** There is no BEST_106 entry. The file's docstring says it contains "best known constructions for the range {0..10000}". The absence of BEST_106 is itself evidence that 106 is not known.

2. **cube20.org/golomb/ covers 160 to 40,000 marks** — their database starts above 159, so it contains no specific data for 106-mark rulers. There is no publicly accessible table entry showing a 106-mark ruler with span ≤ 10000. `[web: cube20.org]`

3. **Proven optimal Golomb rulers (OEIS A003022) go only up to n=28 marks.** For n=106, no proven optimum is known — only "best known" (near-optimal) constructions exist. `[web: oeis.org/A003022]`

4. **No search result from 2020-2024 literature** mentioned a 106-element Sidon set in {0,...,10000}. Recent Sidon set papers focus on: (a) theoretical upper bounds, (b) Sidon sets in 𝔽₂ᵗ (finite fields, different problem), (c) extending the database to 40,000+ marks.

5. **Algebraic analysis (training data, corroborated by pipeline's exhaustive search):** The Bose-Chowla ap construction with q=107 gives 108 marks in modulus Z_{11556} (span ≥ 11555 > 10000). A 105-element subset fits in {0,...,9884}. The three missing elements cannot be recovered without exceeding span 10000. Singer pp with q=107 gives Z_{11557} (span ≥ 11556). Singer pp with q=109 gives 110 marks in Z_{11991}. **No algebraic construction naturally produces exactly 106 marks with span ≤ 10000.** `[training data: corroborated by pipeline's exhaustive multiplier search]`

**Conclusion:**
- F₂(10000) **appears to be 105** based on all available evidence.
- No published construction for F₂(10000) ≥ 106 was found anywhere.
- The pipeline is at or near the known optimum for N=10000.

**Actionable implication:** The primary goal should shift from "find 106" to either:
(a) Confirm optimality: run CP-SAT to prove k=106 INFEASIBLE (not just UNKNOWN), OR
(b) Accept 105 as optimal and document this conclusion.

---

## Finding 2: The VLNS INFEASIBLE Results May Be Genuine, Not a Bug

**Source labels:** `[pipeline: gen006/full_1/sol03.py]`, `[pipeline: gen006 reports]`

**Background:** Gen6 full_1 ran 9 VLNS trials (fix 85 elements, solve for 21 free) and got INFEASIBLE in <1s each. This was diagnosed as a "formulation bug" (abs-equality domain conflict). I examined the actual code.

**Code analysis of sol03.py:**

The code DOES add `model.add(yi != fv)` for all fixed values `fv` before the abs_equality constraints. So the `y[i] = fv` case is explicitly forbidden. The domain conflict bug diagnosis may be incorrect.

The more likely explanation for fast INFEASIBLE results:

1. **The 105-mark set uses 5460 differences** (105×104/2). With N=10000, there are only 9999 possible differences. The fixed 85 elements use 3570 differences already.

2. **For any new element y[i] in {0,...,10000}**, it must have 85 cross-differences to fixed elements, ALL distinct AND not among the 3570 fixed diffs. That leaves ≤ 6429 available differences for 85 cross-diffs per free variable — but they must also not conflict with each other.

3. **The presolve is detecting genuine combinatorial infeasibility**, not a domain bug. The constraint is genuinely unsatisfiable for the chosen removal patterns.

**However**, this does NOT mean k=106 is impossible. It means: with THIS fixed set of 85 elements from BEST_105, there is no 106th element consistent with them. A different starting set (not a subset of BEST_105) might permit 106 elements.

**Actionable implication:**
- Fix VLNS to try starting from algebraically different seeds (e.g., Ruzsa-Lindström construction), not subsets of BEST_105.
- Or: run CP-SAT with NO hint (no fixed elements) and maximize k. This explores outside the BEST_105 basin entirely.
- The formulation itself (as written in sol03.py) appears correct. The `y[i] != fv` constraints are already there.

**One genuine bug to check:** The `diff_domain` for cross-diffs uses `make_domain_excluding(N, fixed_diffs)` which creates [1,N] \ fixed_diffs. If this domain excludes ALL values that |y[i] - fv| could take for some (i, fv) pair, it triggers presolve INFEASIBLE. This IS a potential issue if the domain becomes empty for some variable — worth verifying by checking which specific variable triggers the infeasibility in verbose mode.

---

## Finding 3: Best Algorithm from Literature — Hybrid Tabu + Constraint Programming

**Source labels:** `[web: arxiv.org/abs/1902.08660]`, `[web: link.springer.com]`

**Paper: arXiv:1902.08660** — "A Computational Comparison of Optimization Methods for the Golomb Ruler Problem"

Key results from this paper:
- **Constraint Programming with parallelization** is best for large instances (>20 marks)
- **Hybrid metaheuristics (Tabu + GRASP)** achieve near-optimal solutions for moderate sizes
- **ILP/Benders decomposition** is outperformed by CP for large problems
- **Branch & bound** is only practical up to ~20 marks

**Paper: Springer (2007)** — "Local Search-based Hybrid Algorithms for Finding Golomb Rulers"
- Tabu search with swap moves achieves ~60% success on 16-mark rulers
- GRASP + tabu refinement is recommended for near-optimal large rulers

**Actionable implication for our problem (105-mark, seeking 106):**

Tabu search with "swap-then-fill" moves — the approach mentioned in gen6 research but never implemented:

```
Algorithm: Swap-Fill Tabu Search
1. Start with S = BEST_105
2. For each iteration:
   a. Try swapping element e ∈ S for candidate c ∉ S (not tabu)
   b. After swap, greedily fill with random candidate order
   c. If resulting |S'| > |S|, accept and record
   d. Otherwise, pick best-scoring swap (most addable candidates after swap)
   e. Add (e, c) to tabu list for T iterations
3. Return best seen

Key insight: The swap move is lateral (size stays 105), but changes which
differences are used. Random-order greedy fill after swap explores different
basins than the canonical BEST_105 basin.
```

**Why this differs from what's been tried:** All SA and perturbation variants tested so far used BEST_105 as a fixed starting point with small perturbations. The self-healing property means perturbations return to BEST_105. Tabu search PREVENTS returning by forbidding recently-tried swaps, forcing exploration of genuinely new 105-element configurations.

---

## Finding 4: Ruzsa-Lindström Construction — Algebraically Different Basin

**Source labels:** `[training data: unverified]`, `[pipeline: idea_025]`

The Ruzsa-Lindström construction: for prime p, define  
`S = {x·p + g^x mod p : x ∈ {0,...,p-1}}`  
where g is a primitive root mod p. This produces a p-element Sidon set in {0,...,p²-1}.

For N=10000:
- p=97: 97 elements in {0,...,9408} (fits, but small)
- p=101: ~99 elements in {0,...,10200} (filter to ≤10000, ~97-99 elements)

This gives a WORSE raw score than BEST_105 but is **algebraically distinct** from Singer and Bose-Chowla. The key value is not the raw score but the different basin of attraction under SA/VLNS.

**Actionable implication:** Use Ruzsa-Lindström as the STARTING POINT for VLNS rather than BEST_105. If VLNS from BEST_105 is genuinely infeasible (all removals create unsatisfiable sub-problems), starting from a different algebraic structure may open feasible neighborhoods.

**Note:** idea_025 has confidence 0.2. This construction is untested in the pipeline. It should be implemented and tested as an SA seed.

---

## Finding 5: Recent Structural Insight — Dense Sidon Sets Come from Projective Planes

**Source labels:** `[web: arxiv.org/abs/2107.05744]`

**Paper: arXiv:2107.05744** — Eberhard 2023, "The Apparent Structure of Dense Sidon Sets"
- Published in *Electronic Journal of Combinatorics* v30(1) 2023
- **Key conjecture:** ALL dense Sidon sets arise from finite projective planes through specific constructions
- **Finding:** Nondesarguesian (non-classical) projective planes contain "many further examples" beyond Singer/Bose-Chowla
- **Implication:** There may be 105-element (or larger) Sidon sets NOT derivable from Singer/Bose-Chowla but from nondesarguesian planes

**What this means for our pipeline:**
- The Singer and Bose-Chowla constructions use the **classical** Desarguesian projective plane PG(2,q)
- **Nondesarguesian planes** of the same order (if they exist for our parameters) might give different — potentially better — constructions
- However: nondesarguesian planes of prime order q don't exist (they only exist for prime powers q = p^k with k ≥ 2 that are not prime)
- For N=10000, the relevant primes are q≈100, which are actual primes → no nondesarguesian planes available
- **Conclusion:** This structural insight is theoretically interesting but not immediately actionable for N=10000

---

## Finding 6: Upper Bound Confirmation — Theoretical Ceiling ~109

**Source labels:** `[web: arxiv.org/abs/2103.15850]`, `[web: arxiv.org/abs/2207.07800]`

- **Balogh, Füredi, Roy (2021):** F₂(N) ≤ √N + 0.998·N^(1/4). For N=10000: ≤ 100 + 9.98 ≈ **110**
- **O'Bryant (2022):** F₂(N) ≤ √N + 0.99703·N^(1/4). For N=10000: ≤ **109.97** → effectively ≤ **109**
- **State of Affairs claims "~109"** — this matches the O'Bryant 2022 paper exactly. `[confirmed]`

The gap is: current best 105, theoretical upper bound 109. So there are 4 elements of theoretical room. However, the absence of published constructions for 106+ suggests the true optimum may be 105.

---

## Finding 7: CP-SAT Formulation Improvement — Maximize Objective

**Source labels:** `[pipeline: gen006/full_1 report]`, `[training data: unverified]`

Current CP-SAT formulation: decision problem "find k=106 elements" → returns UNKNOWN.

Better formulation for finding the true maximum:
```python
# Instead of: find exactly k=106 elements
# Use: maximize number of elements

k = model.new_int_var(0, N, 'k')
# Binary variables: x[i] = 1 if element i is in the set
x = [model.new_bool_var(f'x_{i}') for i in range(N+1)]
model.add(k == sum(x))
model.maximize(k)

# Sidon constraint: for all (i,j,k,l) with i+j=k+l and {i,j}≠{k,l}: not (x[i] & x[j] & x[k] & x[l])
# This is still exponential in constraints...
```

The maximize formulation is more "solver-friendly" because:
1. CP-SAT can find k=105 immediately (use BEST_105 as hint)
2. Then incrementally try to improve: can it find k=106?
3. If INFEASIBLE at k=106, immediately proves F₂(10000) = 105

**Actionable implication:** This formulation was identified in gen6 but never tried. An exploit or full agent should implement and run it for 4h+ with 16 workers.

---

## Open Questions

1. **Is F₂(10000) = 105 provably?** CP-SAT has returned UNKNOWN, not INFEASIBLE. A long proof-search run (overnight, 4h+) with the maximize formulation might settle this.

2. **Why is VLNS infeasible in <1s?** Is it genuine combinatorial infeasibility (the fixed 85 elements block all possible 21 replacements) or a domain-emptying bug? Run with `verbose=True` and inspect which variable's domain becomes empty.

3. **Does the Ruzsa-Lindström seed escape the BEST_105 basin?** Untested after 6 generations.

4. **Does tabu search find any 105-element set other than BEST_105?** If the self-healing property is universal (ALL greedy fills from perturbed BEST_105 return to BEST_105), then tabu search cannot escape — and this itself would be a strong optimality signal.

5. **What does the cube20.org database say for rulers near 106 marks?** Their database starts at 160 marks. For 106-mark rulers, there is no publicly accessible tabulated minimum span. Directly contacting Rokicki/Dogon (cube20.org) would be the most reliable way to answer whether a 106-mark ruler with span ≤ 10000 exists.

---

## Summary for Downstream Agents

**If you are an Exploit/Full agent planning next steps:**

1. **Priority 1 (high value, fast):** Run CP-SAT with MAXIMIZE formulation (not k=106 decision). Start from BEST_105 hint. Run 4h+ with 16 workers. This either finds 106 or produces an INFEASIBLE proof.

2. **Priority 2 (medium value, fast to implement):** Tabu search with swap-then-fill. The swap prevents the self-healing return-to-BEST_105 phenomenon. Key: must use tabu list to prevent cycling. Run 10,000+ swap iterations.

3. **Priority 3 (medium value):** Implement Ruzsa-Lindström construction (p=97 or p=101) as VLNS starting point. If VLNS from BEST_105 is genuinely infeasible, a different starting set may not be.

4. **DO NOT** spend more time on: Singer/Bose-Chowla multiplier search (exhausted), SA from BEST_105 (exhausted, self-healing prevents improvement), greedy variants (ceiling confirmed at 70).
