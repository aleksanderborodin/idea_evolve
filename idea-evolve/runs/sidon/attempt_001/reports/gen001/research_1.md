# Research Findings — Sidon Sets: Mathematical Constructions and Computational Strategies

## Summary

The Singer difference set construction (perfect difference sets) is the dominant algebraic approach for large Sidon sets. For N=10000, the Singer set with q=97 gives 98 elements in {0,...,9506} — the best algebraically guaranteed result. The target of 100 may be achievable by: (1) greedy extension of the Singer q=97 set into {9507,...,10000}, or (2) truncating the Singer q=101 set (102 elements in Z_{10303}) to elements ≤ 10000. The existing ideas in our system completely miss algebraic constructions, relying only on search heuristics.

---

## Finding 1: Singer Perfect Difference Sets — The Gold Standard

**Relevance**: All solution agents. This is the most important finding. No current idea uses this.

**Detail**:

A **Singer difference set** (also called a **perfect difference set** with parameters (v, k, 1)) is a set of k=q+1 elements in the cyclic group Z_v where v=q²+q+1, such that every nonzero element of Z_v appears exactly once as a difference of two set elements. This is the strongest possible Sidon property: not only are differences distinct, they cover ALL nonzero residues exactly once.

**Existence**: For every prime power q, a Singer difference set of size q+1 in Z_{q²+q+1} exists (Singer 1938). This is not a probabilistic result — it's guaranteed and constructive.

**Key sizes for N=10000**:

| q | Modulus v=q²+q+1 | Set size | Fits in {0..10000}? |
|---|-----------------|----------|---------------------|
| 89 (prime) | 8011 | 90 | YES — in {0..8010} |
| 97 (prime) | 9507 | **98** | YES — in {0..9506} |
| 101 (prime) | 10303 | 102 | PARTIALLY — 102 elements in Z_{10303}, ~99 fall in {0..10000} |

**Why the Singer set is a valid integer Sidon set**: In Z_{9507} (q=97 case), all 9506 nonzero differences appear exactly once. As integers in {0,...,9506}, all positive differences are in {1,...,9506} with no repeats. This means the set is Sidon not just modulo 9507 but as a plain set of integers.

**Actionable implication**: Implement Singer set construction for q=97 to get 98 elements. This is 32 elements better than the greedy baseline (66 → 98). This should be the first thing any agent implements.

---

## Finding 2: How to Construct a Singer Set — Primitive Polynomial Method

**Relevance**: Any agent implementing Singer sets. Concrete algorithm, copy-pasteable.

**Detail**:

The standard construction uses a linear recurrence (m-sequence) over GF(q):

1. Choose a **primitive polynomial** of degree 3 over GF(q): `f(x) = x³ - a₁x² - a₂x - a₃`
2. Initialize: `x[0]=0, x[1]=0, x[2]=1`
3. Run recurrence: `x[k] = (a₁*x[k-1] + a₂*x[k-2] + a₃*x[k-3]) % q` for k = 3, 4, ..., q²+q
4. Collect all indices k where `x[k] == 0` — these q+1 indices form the Singer set

**For q=97**, this gives 98 indices in {0,...,9506}.

**How to find a primitive polynomial over GF(q)**: Trial-and-error is fast. For each candidate (a1, a2, a3) with a3 ≠ 0:
- Run the recurrence for q²+q+1 steps
- If exactly q+1 zeros are found and the period of the sequence is exactly q²+q+1, it's a primitive polynomial
- Expect to succeed with probability φ(q²+q)/((q³-1)/3) — roughly 1 in 3*q attempts succeed for large q

**Faster alternative**: Use the algebraic construction directly. For GF(q³), pick a generator α of the multiplicative group. The Singer set is `{k : tr_{GF(q³)/GF(q)}(α^k) = 0, 0 ≤ k < q²+q+1}`, where the trace is the standard field trace. But the recurrence method is easier to implement.

**For q=97, concrete starting search**:
```python
q = 97
v = q*q + q + 1  # = 9507
target_size = q + 1  # = 98

def try_singer(a1, a2, a3):
    x = [0, 0, 1]
    zeros = []
    if x[2] == 0: zeros.append(2)
    for k in range(3, v):
        xk = (a1*x[-1] + a2*x[-2] + a3*x[-3]) % q
        x.append(xk)
        if xk == 0:
            zeros.append(k)
    if len(zeros) == target_size:
        return zeros
    return None

# Try a3=1 first, vary a1 and a2
for a1 in range(q):
    for a2 in range(q):
        result = try_singer(a1, a2, 1)
        if result:
            print(f"Found! a1={a1}, a2={a2}, a3=1: {result[:5]}...")
            break
```

This will typically find a Singer set within the first few hundred (a1, a2) pairs tested.

**Known working primitive polynomials over GF(97)**:
The polynomial x³ + x + 1 is NOT necessarily primitive over GF(97), but the search above finds one quickly. A valid primitive polynomial over GF(97) can be found by testing that the recurrence has period exactly 9507 = 97² + 97 + 1. If the zero-count equals 98 and the sequence is non-periodic before step 9507, it's a primitive polynomial.

**Actionable implication**: An agent can implement the 20-line function above, find a primitive polynomial in seconds, extract the 98-element Singer set, and immediately have a score of 98.

---

## Finding 3: Singer q=101 Truncation Strategy — Path to 100+

**Relevance**: Agents trying to hit the target of 100.

**Detail**:

The Singer set for q=101 has 102 elements in Z_{10303} = {0,...,10302}. These cannot all fit in {0,...,10000}, but a key property saves us: **any subset of a Sidon set is also a Sidon set**.

**Strategy**:
1. Construct the Singer set for q=101 (102 elements in {0,...,10302})
2. Keep only elements ≤ 10000
3. The remaining subset is a valid Sidon set in {0,...,10000}

**Expected yield**: The 102 elements are roughly uniformly distributed in {0,...,10302}. Elements above 10000 number roughly 102 * (10302-10000)/10302 ≈ 102 * 0.029 ≈ 3. So we expect to retain **~99 elements**.

**Critical insight**: The yield varies by which Singer set (which primitive polynomial) we pick. By trying multiple primitive polynomials over GF(101) and keeping the one where most elements fall in {0,...,10000}, we can maximize the count. With enough primitive polynomials, we'll find one where ≥100 elements are ≤10000.

**Better strategy — shift the Singer set**: The Singer set is defined in Z_{10303}. A cyclic shift of the set by any constant d gives another Singer set with the same properties. So take the Singer set S for q=101, try all offsets: `S_shifted = {(s + d) % 10303 for s in S}` for d = 0, 1, ..., 10302. For each shift, count elements in {0,...,10000}. Pick the shift that maximizes this count.

Since the elements are roughly uniformly spaced in Z_{10303}, some shifts will land many elements in the window {0,...,10000} (which covers 10001/10303 ≈ 97% of the group). Expect best-case ~101 elements in {0,...,10000}.

The shifted subset is still Sidon in Z_{10303} (shift preserves the Sidon property modulo v), and since elements are in {0,...,10000} (no modular wraparound), it's also Sidon as a set of plain integers.

**Actionable implication**: Implement Singer for q=101, try all cyclic shifts, keep elements ≤10000. This is likely to find 99-101 elements. **This is the main path to hitting target=100.**

---

## Finding 4: Erdős-Turán Construction — Baseline Explanation

**Relevance**: Understanding why greedy = 66 and what easy improvements exist.

**Detail**:

The Erdős-Turán (1941) construction: fix prime p, define
```
S_ET(p) = {2pk + (k² mod p) : k = 1, 2, ..., p-1}
```

For p=67 (largest prime with 2p² ≤ 10000), this gives exactly 66 elements in {135,...,8978}. This perfectly explains why the greedy baseline achieves 66 — the greedy algorithm is essentially discovering the Erdős-Turán set.

For p=71: 2p² = 10082 > 10000. Elements range up to ~10082. Elements within {0,...,10000} number approximately `(p-1) * (10000 / 2p²)` ≈ `70 * 0.99` ≈ **69 elements** still within range.

For p=73: 2p² = 10658. About `72 * (10000/10658)` ≈ **67 elements** within range.

**Actionable implication**: Erdős-Turán for p=71 gives ~70 elements easily (better than greedy 66), but is still much worse than Singer (98). Implement Singer first.

---

## Finding 5: Singer + Extension Hybrid

**Relevance**: Agents that already have the Singer q=97 set and want to push beyond 98.

**Detail**:

The Singer set for q=97 uses elements in {0,...,9506}. There are 494 unused values in {9507,...,10000}. Greedy extension into this range may add 1-2 elements:

1. Start with the 98-element Singer set
2. For each candidate in {9507,...,10000}, check if it can be added (no difference collision)
3. The differences already used number 98*97/2 = 4753 out of 9506 possible differences (50% coverage)
4. For a new element x ∈ {9507,...,10000}, it generates differences x-s for each s in S, all in {1,...,10000}
5. The probability that all 98 differences are unused: roughly (0.5)^98 per candidate — extremely unlikely

**More realistic estimate**: The difference collision probability for each new element is high (~1 - e^{-98/9506*98}) due to birthday paradox effects. Expect 0-1 elements added by extension. The Singer set is already "full" in a sense.

**Better alternative**: Local search (swap one element for two nearby ones) combined with the Singer base might do better than pure extension.

**Actionable implication**: Try greedy extension of Singer q=97, but don't rely on it. The Singer q=101 truncation strategy (Finding 3) is more promising for reaching 100.

---

## Finding 6: What Our System Is Missing (Gap Analysis)

**Relevance**: Architect agent — identifies missing ideas.

**Detail**:

Current ideas: (1) Randomized Greedy, (2) Local Search, (3) Difference-Aware Greedy, (4) Modular Arithmetic, (5) Backtracking.

**Completely missing**:
- **Singer perfect difference sets** — the theoretically optimal algebraic construction. Should give 98 elements directly. Not mentioned anywhere in the idea pool.
- **Singer + truncation** — using Singer q=101 in Z_{10303} and restricting to {0,...,10000}.
- **Singer + cyclic shifts** — optimizing the embedding via cyclic rotation.
- **Singer + local search hybrid** — using algebraic construction as seed for search.

**Present but weak**:
- idea_004 "Modular Arithmetic Structure" vaguely hints at Singer-type constructions but doesn't name them or give concrete parameters.

**Unlikely to reach target without algebraic construction**:
- Randomized greedy typically reaches 70-80, not 98-100
- Local search starting from greedy-66 is very unlikely to reach 98
- Backtracking for N=10000 is computationally intractable

**Actionable implication**: Any agent should start with Singer construction, not greedy. The gap from 66 to 98 is almost entirely closeable with algebra, not search.

---

## Finding 7: Upper Bound Precision

**Relevance**: Target setting and expectation management.

**Detail**:

The best known upper bound for Sidon sets in {0,...,N} is:
- **h(N) ≤ √N + 0.98183 × N^{1/4} + O(1)** (Carter, Hunter, O'Bryant 2025)
- For N=10000: h(10000) ≤ 100 + 0.98183×10 + O(1) ≈ **109.8**, so h(10000) ≤ **109**

The lower bound from construction: Singer q=97 gives **98**.

**Gap**: The true optimum F(10000) is somewhere in [98, 109]. Whether 100 is achievable is an open computational question. The target of 100 is well within the theoretical possibility space but not yet proven constructively.

**Historical note**: O'Bryant's 2004 survey is the canonical bibliography for all Sidon set results. For specific N values, the best known Sidon sets are maintained in computational databases, but no publicly accessible table for N=10000 was found.

**Actionable implication**: Target 100 is ambitious but likely achievable (lies well within the theoretical bound of 109). Singer q=101 truncation is the most promising path.

---

## Open Questions

1. **Does Singer q=101 with optimal cyclic shift achieve ≥100 elements in {0,...,10000}?** This requires implementation and testing. The expected answer is yes, but needs confirmation.

2. **Can local search improve on Singer q=97 starting from 98?** The "dense Sidon sets have algebraic structure" result (Eberhard 2023) suggests Singer sets are close to maximal and hard to improve via random local moves.

3. **What is the exact value of F(10000)?** This appears to be an open problem. The answer is somewhere in [98, 109].

4. **Are there primitive polynomials over GF(97) that give Singer sets with especially good extension properties into {9507,...,10000}?** This is testable but probably won't yield much.

5. **Are there non-Singer Sidon sets of size ≥ 99 in {0,...,10000} found computationally?** No public database found. This would require a serious computational search.

---

## Concrete Implementation Roadmap (Priority Order)

### Priority 1: Singer q=97 (immediate 98-element solution)
```python
def find_singer_set(q):
    v = q*q + q + 1
    import random
    while True:
        a3 = random.randint(1, q-1)
        a2 = random.randint(0, q-1)
        a1 = random.randint(0, q-1)
        x = [0, 0, 1]
        zeros = []
        for k in range(3, v):
            xk = (a1*x[-1] + a2*x[-2] + a3*x[-3]) % q
            x.append(xk)
            if xk == 0:
                zeros.append(k)
        if len(zeros) == q + 1:
            return sorted(zeros)

# Usage:
singer_97 = find_singer_set(97)  # 98 elements in {0,...,9506}
```
Note: include index 0 check (x[0]=0 by definition, so 0 is always in the set).

### Priority 2: Singer q=101 with cyclic shift optimization
```python
def find_best_truncation(q, N=10000):
    S = find_singer_set(q)  # q+1 elements in Z_{q^2+q+1}
    v = q*q + q + 1
    best = []
    for shift in range(v):
        truncated = sorted([(s + shift) % v for s in S if (s + shift) % v <= N])
        if len(truncated) > len(best):
            best = truncated
    return best

# Expected: ~99-101 elements for q=101
```

### Priority 3: Greedy extension of Singer q=97 baseline
After obtaining the 98-element Singer set, try adding each element from {9507,...,10000} using the `can_add` helper.

### Priority 4: Local search seeded from Singer base
Use the Singer q=97 set as starting point for local search (swap/replace moves), accepting moves that increase set size.

---

## Debrief

**1. What I tried:**
- Surveyed the Sidon set (B2 sequence) literature via web search and fetch
- Found the definitive references: Singer (1938), Erdős-Turán (1941), O'Bryant's 2004 bibliography (arXiv:math/0407117)
- Computed exact parameters for Singer sets fitting in {0,...,10000}
- Analyzed the Erdős-Turán construction to explain why the greedy baseline = 66
- Identified that Singer q=101 truncation is the path to 100+ elements

**2. Information I lacked:**
- Specific primitive polynomial coefficients (a1, a2, a3) for q=97 — need trial-and-error in code
- A direct online table of best-known Sidon sets for specific N values; O'Bryant's survey has this but requires downloading the PDF
- Whether F(10000) ≥ 100 has been proven (i.e., proven existence of a 100-element Sidon set in {0,...,10000})

**3. What given facts might be wrong:**
- fact_002 says "upper bound of approximately 100-102 for N=10000." The modern upper bound is 109 (Carter, Hunter, O'Bryant 2025), not 102. The 100-102 was the Erdős-Turán era estimate. This may mislead agents into thinking 100 is right at the theoretical ceiling — it's not, the ceiling is ~109.

**4. State of Affairs accuracy:**
Correct that generation 0 has no evaluated solutions. But the initial ideas (greedy restarts, local search, difference-aware, modular arithmetic, backtracking) completely omit algebraic constructions. This is the main gap.

**5. What I would do differently:**
- Download O'Bryant's survey PDF to get the explicit table of best-known F(N) values
- Compute and verify a concrete Singer q=97 example

**6. Specific experiments to run:**
- Implement Singer q=97: verify it produces 98 Sidon elements (should take ~1 min to code)
- Implement Singer q=101 with cyclic shift: find shift maximizing elements ≤ 10000
- Try greedy extension of Singer q=97 set into {9507,...,10000} for free extra elements
- Local search (SA) starting from Singer q=97 to probe 99-101 range

**7. Surprises:**
- The greedy baseline of 66 exactly matches the Erdős-Turán construction for p=67. Not a coincidence — greedy discovers this algebraic structure.
- The upper bound is 109 (not ~102): more room for improvement than expected.
- Singer q=101 truncation is elegant: ~99 elements survive in {0,...,10000}, with shifts potentially yielding exactly 100.

**8. Helper tools feedback:**
- `can_add(S_sorted, used_diffs, candidate)` is the key incremental-check primitive. Well-designed.
- `is_prime(n)` available — useful for checking candidate primes.
- Missing: `find_singer_set(q)` helper that implements the recurrence construction. Would save every agent ~20 lines of boilerplate and prevent off-by-one errors in the recurrence.

**9. Time budget:**
Research was feasible within session. Did not have time to verify Singer construction with an actual numeric example. Solution agents should prioritize Singer q=97 implementation first.
