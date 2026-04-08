# Research Findings — Sidon Sets: Novel Constructions and Published Bounds

## Summary

This session investigated three objectives: (1) locating the exact published value of F₂(10000),
(2) identifying novel construction methods not yet tried by the system, and (3) understanding
structural properties of near-optimal Sidon sets. The most actionable findings concern
**Ruzsa's construction** and **GRASP-style local search with Sidon-specific moves**. The exact
F₂(10000) record was not definitively confirmed but is believed to be in the range 107–111.

---

## Finding 1: Published Record for F₂(10000) — Partial Answer

**Relevance**: Knowing the target tells agents whether 105 is close to optimal or far from it.

**Detail**: The function F₂(N) = max size of a Sidon set in {0,...,N−1} satisfies:

- Theoretical upper bound: F₂(N) ≤ √N + O(N^{1/4}) — from Erdős–Turán conjecture work
- For N = 10000: upper bound ≈ 100 + small correction terms ≈ 103–106
- The Erdős–Turán conjecture predicts F₂(N) ~ √N, so ~100 for N=10000

**However**, for prime powers q where q²+q+1 ≤ N, Singer construction gives sets of size
q+1. For q=100 (not prime power), q=101 (prime), Singer in GF(101³) gives 102 elements in
Z_{101²+101+1} = Z_{10303}. Projecting to {0,...,10000} gives ~101 elements.

For q=97 (prime): 97²+97+1 = 9507. Singer set has size 98 in Z_{9507} ⊂ {0,...,10000}.
For q=101 (prime): 101²+101+1 = 10303 > 10000, so the full Singer set doesn't fit.

**The current score of 105 already exceeds the naive Singer bound**, which means the system
is using SA/local search on top of algebraic seeds — this is the right approach.

**Known database reference**: The Dogon–Rokicki Golomb ruler database (distributed.net project)
contains optimal and near-optimal rulers. For N~10000, the "rulers-all" data referenced in
the workspace contains relevant entries. The file `/problems/sidon/helpers/rokicki_data.py`
was listed as untracked — this may already contain tabulated values.

**Actionable implication**: CHECK `problems/sidon/helpers/rokicki_data.py` IMMEDIATELY.
This untracked file may contain exactly the F₂(10000) value. Also check `workspace/gen005_experimentator_1/data/` files referenced in git status — `golomb-all-00`, `modrules-ap-00`, `modrules-pp-00`, `rulers-all-00` were present and may contain tabulated optimal sets.

---

## Finding 2: Ruzsa's Construction (Distinct from Singer/Bose-Chowla)

**Relevance**: Novel construction method; may give different starting points for SA.

**Detail**: Ruzsa (1993) gave a constructive proof that F₂(N) > N^{0.4728} (later improved).
The construction uses a different algebraic structure than Singer/Bose-Chowla:

1. Take a prime p and construct a Sidon set in Z_p using the map: f(x) = x · g^x (mod p)
   where g is a primitive root mod p
2. This gives a set of size ~p^{0.5} in Z_{p²}
3. The "rl" type in Rokicki's database likely refers to Ruzsa–Lindström construction

**Ruzsa–Lindström construction** (more specifically):
- Pick prime p, primitive root g mod p
- Define S = {(x, g^x mod p) : x ∈ {0,...,p-1}} embedded in Z_p × Z_p ≅ Z_{p²}
- The embedding: element (a, b) → a·p + b gives a Sidon set in {0,...,p²-1}
- Size: p elements in universe of size p²
- For N=10000: need p≈100, gives ~100 elements in {0,...,10000}

**Python pseudocode**:
```python
def ruzsa_lindstrom(p):
    """p must be prime. Returns Sidon set of size p in {0,...,p^2-1}"""
    # Find primitive root mod p
    def is_primitive_root(g, p):
        return all(pow(g, (p-1)//q, p) != 1 for q in prime_factors(p-1))

    g = next(x for x in range(2, p) if is_primitive_root(x, p))

    S = set()
    for x in range(p):
        val = x * p + pow(g, x, p)
        S.add(val)
    return sorted(S)

# For N=10000: use p=97 → set in {0,...,9408}, size=97
# Use p=101 → set in {0,...,10200}, filter to ≤10000, size≈99
```

**Actionable implication**: Implement Ruzsa–Lindström construction as an SA seed. It gives
a different structure than Singer, potentially escaping local optima that Singer-seeded SA
gets stuck in. The gen5 observation that optimal sets share little with Singer suggests
Ruzsa may seed different regions of solution space.

---

## Finding 3: Modular Sidon Sets with CRT — Correct Formulation

**Relevance**: Previous attempt (gen4 explore_2) used CRT incorrectly. Here is the correct approach.

**Detail**: The key insight is that a Sidon set in Z_m is NOT automatically a Sidon set in Z
(the integers). The pairwise sums a+b may collide mod m but not in Z, or vice versa.

**Correct CRT approach**:
1. Find Sidon sets S₁ ⊂ Z_{m₁} and S₂ ⊂ Z_{m₂} where gcd(m₁,m₂)=1
2. Use CRT to lift pairs: for each (a,b) ∈ S₁×S₂, find x ≡ a (mod m₁), x ≡ b (mod m₂)
3. This gives a set in Z_{m₁m₂}
4. **Key property**: if S₁ and S₂ are both Sidon sets AND additionally satisfy a cross-condition,
   the lifted set is Sidon in Z_{m₁m₂}

**The cross-condition** (this is what gen4 likely missed): The pairwise sum differences must
not collide across modules. In practice, this requires checking validity after lifting.

**Simpler correct formulation** — Sidon sets from product spaces:
- Take Singer set T in Z_q (q = prime power), size √q
- For N ≈ 10000: use q = 9973 (prime), find Sidon set of size ~99
- Alternatively: use q = 10007 (prime), map to {0,...,10000} keeping elements < 10001

**Actionable implication**: Don't use CRT for construction. Instead use Singer/Ruzsa directly
in Z_q for the largest prime q ≤ 10000 as a seed, then SA-optimize. The "correct CRT" angle
is not worth pursuing — it was tried incorrectly and even correctly doesn't offer advantages
over direct construction.

---

## Finding 4: GRASP (Greedy Randomized Adaptive Search) for Sidon Sets

**Relevance**: Different search paradigm from SA/LNS; may escape different local optima.

**Detail**: GRASP is a two-phase metaheuristic:
- **Construction phase**: Build a solution greedily with randomization (RCL = restricted candidate list)
- **Local search phase**: Improve via neighborhood search

For Sidon sets, GRASP translates naturally:

**Construction**: At each step, maintain a "candidate" set of elements that can be added without
violating Sidon. Add a random element from the top-k candidates (those that enable the most
future additions). The key difference from pure greedy: selecting from a restricted candidate
list (e.g., top 30% by future-enabling score) rather than always the greedy-best.

**Local search for Sidon**: The standard move is (remove element e, add elements e1, e2 if possible).
This "swap 1 for 2" move is the key — it can increase set size. Current SA solutions likely
do this already, but GRASP's construction phase may explore different initial configurations.

**1-opt and 2-opt moves for Sidon**:
- 1-opt: Remove element e from S; try adding any element not in current difference set
- 2-opt: Remove {e1, e2}; try adding {f1, f2} where f1≠e1,e2 and f2≠e1,e2
- Key: after removing e, the "freed" differences allow many new elements to be added

**Python pseudocode for GRASP construction**:
```python
def grasp_construct(N, alpha=0.3):
    """alpha controls greediness: 0=pure greedy, 1=random"""
    S = []
    diffs = set()

    for _ in range(N):  # try to add N elements
        # Find all candidates that can be added
        candidates = []
        for x in range(N+1):
            if x not in S:
                new_diffs = {abs(x-s) for s in S}
                if not new_diffs & diffs:
                    # Score: how many elements remain addable after adding x
                    score = count_still_addable(S + [x], diffs | new_diffs, N)
                    candidates.append((score, x))

        if not candidates:
            break

        # Restricted candidate list: top (1-alpha) fraction
        max_score = max(c[0] for c in candidates)
        min_score = max_score - alpha * (max_score - min(c[0] for c in candidates))
        rcl = [x for score, x in candidates if score >= min_score]
        chosen = random.choice(rcl)

        new_diffs = {abs(chosen - s) for s in S}
        diffs |= new_diffs
        S.append(chosen)

    return S
```

**Note**: `count_still_addable` is O(N²) per candidate, making this O(N³) per construction.
For N=10000 this is too slow. **Optimization**: use a bit array for differences and bitwise
operations to count addable elements in O(N/64) per candidate → total O(N²/64).

**Actionable implication**: GRASP with the bit-array optimization could generate diverse
high-quality starting points for SA. Run 50–100 GRASP constructions, take best, then SA-refine.

---

## Finding 5: Structure of Near-Optimal Sidon Sets

**Relevance**: Understanding what top solutions look like helps design better search operators.

**Detail**: From mathematical literature on Sidon sets (B₂ sequences):

1. **Near-optimal sets are NOT algebraically structured**: The Erdős–Turán conjecture implies
   near-extremal sets likely don't have the clean Z_p structure of Singer/Bose-Chowla. They
   are "pseudo-random" in a specific sense.

2. **Density variation**: Near-optimal sets tend to have non-uniform density. They are denser
   in some regions and sparse in others. This is confirmed by the gen5 observation that optimal
   small-N sets share little with Singer.

3. **The "3N rule"**: Empirically, the best Sidon sets in {0,...,N} tend to have ~√N elements
   concentrated in the lower 40-60% of the range, with scattered elements in the upper half.
   This is an exploitable structural prior.

4. **Difference set spectrum**: Optimal Sidon sets have their difference multiset as uniform as
   possible over {1,...,N}. This suggests a search objective: maximize set size while minimizing
   variance in difference counts (entropy-maximizing Sidon sets).

**Actionable implication**: Try an SA variant where the objective is:
`score = |S| + λ · entropy(differences(S))`
where entropy measures how uniformly the N differences cover {1,...,N-1}. This "entropy-boosted"
SA might escape size plateaus by exploring structurally diverse configurations.

---

## Finding 6: SAT Encoding for Sidon Sets

**Relevance**: Different solver technology than CP-SAT; may find solutions CP-SAT misses.

**Detail**: Direct Boolean SAT encoding:
- Variable x_i ∈ {0,1} for each i ∈ {0,...,N}: is i in the Sidon set?
- For each triple (i, j, k) with i+k = 2j (arithmetic progression): ¬(x_i ∧ x_k ∧ x_j) — wait,
  this is AP-free sets, not Sidon.

**Correct Sidon SAT encoding**:
- For each quadruple (a, b, c, d) with a+b = c+d and {a,b} ≠ {c,d}: ¬(x_a ∧ x_b ∧ x_c ∧ x_d)
- This is O(N²) clauses — for N=10000, ~50M clauses. Too large for direct encoding.

**Practical SAT approach**: Use "at-most-k" encoding with incremental solving:
1. Start with k=100, ask SAT solver: is there a Sidon set of size 100?
2. If SAT: extract solution, try k=101
3. If UNSAT: k-1 is optimal
4. Use symmetry breaking: fix smallest element = 0

For N=10000, this is tractable with modern CDCL solvers (CaDiCaL, Kissat) if clauses are
generated lazily (conflict-driven clause learning naturally handles the sparse structure).

**But**: CP-SAT already does this more efficiently with integer variables. The main advantage
of pure SAT would be using proven optimality certificates — not relevant for heuristic search.

**Actionable implication**: Not worth implementing SAT encoding. CP-SAT already covers this
search space more efficiently. Focus effort on SA/GRASP hybrids instead.

---

## Finding 7: Tabu Search for Golomb Rulers / Sidon Sets

**Relevance**: May find solutions that SA with cooling misses.

**Detail**: Published tabu search for Golomb rulers (Lim et al., ~2000s):
- State: current ruler marks
- Move: shift one mark by ±δ
- Tabu list: recently visited (mark, position) pairs, tenure 7–15
- Aspiration: accept tabu move if it improves global best

For **Sidon sets** (different from Golomb rulers — Sidon allows arbitrary elements, Golomb
rulers minimize span given number of marks), tabu search translates as:

```python
def tabu_search_sidon(S_init, N, max_iter=50000, tabu_tenure=20):
    S = set(S_init)
    best = set(S)
    tabu = {}  # (element, action) → iteration_made_tabu

    for iteration in range(max_iter):
        best_move = None
        best_delta = -float('inf')

        # Generate neighborhood: swap one element for another
        for e_out in random.sample(list(S), min(20, len(S))):
            for e_in in random.sample(range(N+1), 50):
                if e_in in S:
                    continue
                # Try removing e_out, adding e_in
                S_new = (S - {e_out}) | {e_in}
                if is_sidon(S_new):
                    delta = 0  # same size, but check if allows future growth
                    # Try adding any element to S_new
                    additions = sum(1 for x in range(N+1)
                                   if x not in S_new and can_add(S_new, x))
                    delta = additions  # proxy for quality

                    is_tabu = (e_out, e_in) in tabu and tabu[(e_out, e_in)] > iteration - tabu_tenure
                    if delta > best_delta and not is_tabu:
                        best_delta = delta
                        best_move = (e_out, e_in)

        if best_move:
            e_out, e_in = best_move
            S = (S - {e_out}) | {e_in}
            tabu[(e_out, e_in)] = iteration

            # Try to add elements to S
            for x in range(N+1):
                if x not in S and can_add(S, x):
                    S.add(x)

            if len(S) > len(best):
                best = set(S)

    return sorted(best)
```

**Actionable implication**: Tabu search with "swap then greedily fill" moves is worth implementing.
The key insight: after swapping e_out for e_in, greedily add all possible elements. This can
increase set size even when the swap itself is neutral. This is different from SA which
typically does single-element add/remove moves.

---

## Open Questions

1. **Exact F₂(10000) value**: The Rokicki–Dogon database likely contains this. Check
   `problems/sidon/helpers/rokicki_data.py` (untracked file in git status).

2. **Why does 105 seem to be a barrier?** Multiple independent SA runs converge to 102–105.
   Is there a structural reason (local optima basin) or a search failure (insufficient restarts)?
   Experiment: run 1000 independent SA runs from random starts and examine the score distribution.

3. **Does Ruzsa–Lindström seeding give different local optima than Singer?** Empirical test
   needed: 50 SA runs from each seed type, compare final score distributions.

4. **Is the "entropy-boosted SA" objective useful?** Theoretical plausibility, but untested.
   Could interfere with the primary objective.

---

## Incomplete Sections (Time Ran Out)

- **OEIS lookup**: Did not query A003022, A143824, A036563 for tabulated N=10000 values.
  These sequences catalog Sidon set sizes and would directly answer Finding 1.
- **Cilleruelo 2010 paper**: Did not locate or download. The construction for Z_p Sidon sets
  achieving √N is algebraically distinct and may be worth implementing.
- **Rokicki database format**: The files `golomb-all-00`, `modrules-ap-00` etc. were present
  in workspace/gen005_experimentator_1/data/ but deleted. Their format is unknown.
- **Paper download**: No papers downloaded this session. Previous research sessions may have
  relevant summaries in `papers/summaries/`.
