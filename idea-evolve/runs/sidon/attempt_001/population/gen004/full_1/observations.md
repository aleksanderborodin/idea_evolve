# Observations — gen004_full_1

## Summary

Implemented CP-SAT ILP for Sidon sets. One solution produced. **Best score: 102** (Singer baseline).

---

## Approach: CP-SAT Integer Element Formulation

### Key Insight

Instead of indicator variables (O(N²) auxiliary variables for N=10000), used integer element variables:
- k integer variables e_0 < e_1 < ... < e_{k-1} in {0,...,N}
- C(k,2) = 5253 difference variables d_{i,j} = e_j - e_i
- Single `AddAllDifferent` constraint on differences enforces Sidon condition
- Total model: 5356 variables (vs ~50M for indicator formulation)
- Model builds in **0.04 seconds**

### Experiments Run

#### 1. Formulation Validation (N=56, k=8–10)
- k=8, N=56: **OPTIMAL** (1.7s) — found valid 8-element Sidon set
- k=9, N=56: **OPTIMAL** (1.9s) — found valid 9-element set {0,4,14,19,21,44,45,53,56}
- k=10, N=56: **OPTIMAL** (7.9s) — found valid 10-element set
- k=11, N=56: **INFEASIBLE** (5.4s) — proved no 11-element set exists in {0,...,56}

This confirms Singer is NOT optimal for small N. Singer q=7 gives 8 elements; ILP finds 10.

#### 2. ILP vs Singer for Small Primes
- q=7, N=56: Singer=8, ILP optimal=**10** (beats Singer by 2)
- q=11, N=132: Singer=12, ILP finds **13** (beats Singer by 1, OPTIMAL)
- q=13, N=182: Singer=14, ILP UNKNOWN at k=15 after 40s
- q=17, N=306: Singer=18, ILP UNKNOWN at k=19 after 20s

**Key finding**: Singer is provably suboptimal for small N. ILP finds better Sidon sets.

The q=11 13-element solution was a "hybrid" — 8 elements shared with Singer, 8 added/removed.

#### 3. Main Attempt: k=103, N=10000 (300s)
- Status: **UNKNOWN** — solver neither found 103 elements nor proved none exist
- Hint: Singer 102 elements provided as warm start

#### 4. k=103, N=10000 Without Hints (300s)
- Status: **UNKNOWN** — same result without hints

#### 5. k=103, N=10302 (Singer q=101 full range, 120s)
- Status: **UNKNOWN** — slightly larger range doesn't help within 120s

#### 6. Indicator Formulation Maximization (N=56)
- Found **size=10** optimal Sidon set in {0,...,56} with 61s
- Set: {0, 1, 6, 10, 23, 26, 34, 41, 53, 55}
- Confirms theoretical upper bound is 10 for N=56 (vs Singer's 8)

---

## Key Findings

1. **Singer is not globally optimal.** For N=q²+q, ILP finds sets larger than q+1 (Singer size). This means 103+ elements might exist for N=10000.

2. **CP-SAT integer formulation is correct and fast to build** (5356 vars, 0.04s build). The bottleneck is search time, not model size.

3. **The problem is hard for CP-SAT.** At k=103, N=10000, 600 seconds was insufficient to find a solution or prove infeasibility. The search space is simply too large for current CP-SAT to explore exhaustively.

4. **Hint quality matters less than expected.** Both Singer-hinted and hint-free runs gave UNKNOWN in 300s. The Singer hint doesn't meaningfully constrain the search space.

---

## Scores

| Solution | Fitness | Status |
|----------|---------|--------|
| sol01.py | 102 | Valid (Singer baseline) |

---

## What Would Help

- Longer CP-SAT run (24h+) for k=103
- Commercial solver (Gurobi) — better LP relaxation and branching heuristics
- Explicit construction for "Singer+1" that works for large q
- Literature search: what is F(10000) published by O'Bryant/Helm?
