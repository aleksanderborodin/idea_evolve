# Alpha Evolve: Candidate Optimization Problems

A curated set of 13 problems ideally suited for multi-generation evolutionary code optimization. Each has a cheap deterministic fitness function, known benchmarks to compare against, and enough room for improvement that beating SOTA is plausible in 20–50 generations.

---

## 1. Low Autocorrelation Binary Sequences (LABS)

**Domain:** Signal processing / combinatorial optimization / statistical physics

**Solution format:** A binary sequence `s ∈ {-1, +1}^L`.

**Fitness function — Merit Factor (maximize):**
```python
def evaluate(s):
    L = len(s)
    E = sum(sum(s[i]*s[i+k] for i in range(L-k))**2 for k in range(1, L))
    return L**2 / (2 * E)  # merit factor
```

**Why it's a good fit:** The search space is 2^L with an extremely rugged landscape. No known polynomial-time algorithm produces optimal sequences. Multiple approaches exist: algebraic constructions (Legendre/Jacobi sequences), tabu search, memetic algorithms, self-avoiding walks, and hybrid methods. Knowledge about good starting constructions, symmetry exploitation (skew-symmetric), and local search operators compounds across generations.

**Known best results:** Optimal solutions proved by exhaustive search up to L=66. Best known skew-symmetric sequences have merit factor >9 for L up to ~255. The conjectured asymptotic optimal merit factor is 12.3248, but the best computationally achieved values are around 8.5–9.5 for L in the 150–300 range. The GitHub repo `borkob/git_labs` maintains a public table of best-known values.

**Practical value:** Used in radar/sonar pulse compression, spread spectrum communications, and cryptography. Equivalent to finding the ground state of the Bernasconi model in statistical physics.

**Estimated difficulty:** Very well suited. For L=60–100 (where you can compare to known optima), the system should make clear progress. For L=120–200, beating published skew-symmetric results is plausible.

---

## 2. Spherical Codes / Tammes Problem

**Domain:** Discrete geometry / packing theory

**Solution format:** An array of N points on the unit sphere, each represented as (θ, φ) or (x, y, z) with x²+y²+z²=1.

**Fitness function — minimum pairwise distance (maximize):**
```python
import numpy as np
def evaluate(points):
    # points: Nx3 array on unit sphere
    dots = points @ points.T
    np.fill_diagonal(dots, -2)  # exclude self
    return np.min(np.arccos(np.clip(dots, -1, 1)))
```

**Why it's a good fit:** Proven optimal only for N ≤ 14 and N = 24 on S². For N = 15–23 and N ≥ 25, only conjectured best configurations exist (maintained by Henry Cohn at MIT). Different approaches help: gradient descent on angular coordinates, algebraic constructions from group theory, simulated annealing, and icosahedral/polyhedral seeding. Higher-dimensional variants (S³, S⁴, etc.) are even more open.

**Known best results:** Henry Cohn's spherical code tables list the best known configurations for up to 130+ points in various dimensions. Neil Sloane's tables at OEIS provide reference values.

**Practical value:** Applications in antenna design, molecular chemistry, data quantization (vector quantization), coding theory, and virus capsid structure.

**Estimated difficulty:** Excellent. For N=20–60 in 3D, the system should find configurations matching or approaching best known. For less-explored dimensions (4D, 5D with moderate N), there's genuine room for new records.

---

## 3. Ramsey Number Lower Bounds

**Domain:** Extremal graph theory / combinatorics

**Solution format:** An adjacency matrix (or equivalently, a set of edges) for a 2-coloring of the complete graph K_n.

**Fitness function — minimize monochromatic cliques:**
```python
from itertools import combinations
def evaluate(adj, s, t):
    n = len(adj)
    violations = 0
    for clique in combinations(range(n), s):
        if all(adj[i][j] for i,j in combinations(clique, 2)):
            violations += 1
    for clique in combinations(range(n), t):
        if all(not adj[i][j] for i,j in combinations(clique, 2)):
            violations += 1
    return violations  # 0 means valid lower bound R(s,t) > n
```
(Use bit-parallel or numpy for speed. For R(5,5), checking n=43 takes seconds.)

**Why it's a good fit:** Finding R(s,t)-critical colorings is a classic search problem. Approaches include circulant/block-circulant constructions, Paley graphs, algebraic graph constructions, simulated annealing, and SAT-based search. The system can learn structural patterns (symmetry groups, regularity conditions). The current bounds are: R(5,5) is between 43 and 46. R(4,6) is between 36 and 41. Many multicolor bounds (R₃(4), R₃(5), etc.) have wide gaps.

**Known best results:** Radziszowski's dynamic survey "Small Ramsey Numbers" (frequently updated) is the definitive reference. Recent result: Angeltveit and McKay proved R(5,5) ≤ 46 in 2024.

**Practical value:** Primarily mathematical significance, but Ramsey theory connects to information theory and network design. Any improvement to a Ramsey lower bound is immediately publishable.

**Estimated difficulty:** Good for specific targets. For well-studied cases like R(5,5), matching n=42 is feasible but improving is very hard. For less-studied multicolor numbers (e.g., R(3,3,3,4) where bounds are 51–62, or various graph Ramsey numbers for non-complete graphs), improvements are more accessible.

---

## 4. Golomb Rulers

**Domain:** Combinatorics / coding theory / radio astronomy

**Solution format:** An array of n distinct non-negative integers (mark positions).

**Fitness function — ruler length (minimize), penalizing duplicate distances:**
```python
def evaluate(marks):
    marks = sorted(marks)
    diffs = [marks[j] - marks[i] for i in range(len(marks)) for j in range(i+1, len(marks))]
    penalty = (len(diffs) - len(set(diffs))) * 10000
    return marks[-1] + penalty  # minimize
```

**Why it's a good fit:** Optimal rulers proved only up to 28 marks (after decades of distributed computation by distributed.net). For 29+ marks, the best known constructions come from 75-year-old algebraic methods (Singer, Bose-Chowla). Remarkably, no one has beaten algebraic constructions for >16 marks despite massive computational effort. But there's a $250 bounty offered for any improvement over algebraically-constructed rulers for 36–40,000 marks.

**Known best results:** Optimal lengths for n=2..28 in OEIS A003022. Shearer's tables provide best known through 150+ marks. Rokicki and Dogon extended through 500,000 marks using modular constructions.

**Practical value:** Radio telescope array design, error-correcting codes, information theory, sensor placement for X-ray crystallography.

**Estimated difficulty:** Moderate-high. Matching algebraic constructions for n=20–30 is feasible. Actually beating them would be extraordinary and publishable, but the evidence suggests algebraic methods may be optimal for large n. Best used as a "prove you can match known results" benchmark.

---

## 5. Covering Arrays

**Domain:** Software testing / combinatorial design

**Solution format:** An N × k array over a v-symbol alphabet. For binary strength-2: an N × k matrix of 0s and 1s.

**Fitness function — number of uncovered t-tuples (minimize), or array size N (minimize for fixed coverage):**
```python
from itertools import combinations, product
def evaluate(array, t, v):
    N, k = array.shape
    uncovered = 0
    for cols in combinations(range(k), t):
        seen = set()
        for row in range(N):
            seen.add(tuple(array[row, c] for c in cols))
        uncovered += v**t - len(seen)
    return uncovered  # 0 = valid covering array; then minimize N
```

**Why it's a good fit:** The covering array number CAN(t,k,v) is unknown for most parameter combinations. Multiple construction methods exist: algebraic (perfect hash families), greedy algorithms, tabu search, recursive constructions, and probabilistic methods. The NIST and Colbourn tables maintain best known sizes. Recent papers (2024–2025) continue to improve bounds for strength 3–6. The search space is huge for practical parameters.

**Known best results:** Colbourn's tables (ASU) and NIST covering array tables are the standard references. Thousands of entries with gaps between known bounds.

**Practical value:** Directly used in software testing (combinatorial interaction testing), hardware testing, and drug screening. Companies like Microsoft, Google, and Siemens use covering arrays. Reducing array size = fewer tests needed = real cost savings.

**Estimated difficulty:** Excellent. Pick a specific (t, k, v) where there's a gap. For strength 3, binary, k=15–30, improvements over best known are achievable. This is one of the most practically impactful problems on this list.

---

## 6. Optimal Error-Correcting Codes (Binary Linear Codes)

**Domain:** Coding theory / information theory

**Solution format:** A k × n binary generator matrix G (or equivalently, an (n-k) × n parity-check matrix H).

**Fitness function — minimum distance (maximize for given n, k):**
```python
import numpy as np
from itertools import combinations
def evaluate(G):
    k, n = G.shape
    # Generate all non-zero codewords
    min_weight = n + 1
    for r in range(1, k+1):
        for rows in combinations(range(k), r):
            codeword = np.bitwise_xor.reduce(G[list(rows)], axis=0)
            w = np.sum(codeword)
            min_weight = min(min_weight, w)
    return min_weight  # maximize
```
(For larger k, use randomized or Zimmermann's algorithm instead of exhaustive.)

**Why it's a good fit:** Markus Grassl's code tables (codetables.de) list upper and lower bounds on d_max(n,k) for binary linear codes. Many entries have gaps. Constructing codes that achieve new lower bounds is an active research area. Approaches include algebraic constructions (BCH, Reed-Muller, quadratic residue codes), quasi-cyclic search, random constructions with local optimization, and concatenation techniques.

**Known best results:** codetables.de is the definitive online reference, maintained by Markus Grassl. Hundreds of open gaps exist.

**Practical value:** Error-correcting codes are foundational to all digital communication. Any improvement is publishable in IEEE Transactions on Information Theory.

**Estimated difficulty:** Good for targeted parameter ranges. Pick specific (n,k) with gaps in the Grassl tables (e.g., n=64–128, moderate k). The system can explore quasi-cyclic and other structured constructions.

---

## 7. Quadratic Assignment Problem (QAPLIB)

**Domain:** Operations research / facility layout

**Solution format:** A permutation of n elements (assignment of facilities to locations).

**Fitness function — total cost (minimize):**
```python
import numpy as np
def evaluate(perm, flow_matrix, distance_matrix):
    n = len(perm)
    cost = 0
    for i in range(n):
        for j in range(n):
            cost += flow_matrix[i][j] * distance_matrix[perm[i]][perm[j]]
    return cost
```

**Why it's a good fit:** QAP is NP-hard and one of the hardest combinatorial optimization problems. QAPLIB provides standardized benchmark instances with sizes from 12 to 256. Many large instances (Taillard's tai60a–tai256c) remain unsolved to optimality. The gap between best known solutions and lower bounds ranges from 1% to 5%+. Multiple approaches: simulated annealing, tabu search, genetic algorithms, ant colony optimization, and recently transformer-based methods.

**Known best results:** QAPLIB (coral.ise.lehigh.edu/data-sets/qaplib/) lists all instances with best known solutions and bounds. Tai256c has a 1.25% gap between best known upper and lower bounds. Many Sko100 instances have ~5.5% gaps.

**Practical value:** Direct applications in facility layout, keyboard design, circuit board placement, hospital layout, and logistics.

**Estimated difficulty:** Good for medium instances (n=30–60). For n=20–30, matching SOTA should be feasible. For Taillard instances n=40+, improving best known solutions is plausible since these are typically found by metaheuristics with no optimality guarantee.

---

## 8. Maximum-Size Cap Sets (or Sum-Free Sets in F₃ⁿ)

**Domain:** Additive combinatorics / extremal set theory

**Solution format:** A subset S of F₃ⁿ (the vector space over the field with 3 elements) such that no three elements sum to zero.

**Fitness function — set size (maximize) with constraint penalty:**
```python
import numpy as np
from itertools import combinations
def evaluate(S, n):
    # S: list of vectors in {0,1,2}^n
    violations = 0
    for triple in combinations(range(len(S)), 3):
        if all((S[triple[0]][i] + S[triple[1]][i] + S[triple[2]][i]) % 3 == 0 for i in range(n)):
            violations += 1
    return len(S) - violations * 100  # maximize size, penalize violations
```

**Why it's a good fit:** The cap set problem saw a breakthrough in 2016 (Croot-Lev-Pach / Ellenberg-Gijswijt) proving upper bounds, but the gap between the polynomial method upper bounds and the best explicit constructions remains enormous. For small n (6–12), finding the largest cap set is tractable and there are known values to compare against. The problem connects to matrix multiplication algorithms and Roth's theorem.

**Known best results:** Known exact values: n=1→2, n=2→4, n=3→9, n=4→20, n=5→45, n=6→112. For n=7 and beyond, only bounds are known.

**Practical value:** Connects to sunflower conjecture, matrix multiplication complexity, and communication complexity. Publishable in top combinatorics journals.

**Estimated difficulty:** Good for n=6–8 where the system can verify against known values and try to extend. For n=7, the exact value isn't fully established, creating genuine discovery potential.

---

## 9. Graph Coloring (DIMACS Benchmark Instances)

**Domain:** Graph theory / operations research

**Solution format:** An assignment of colors to vertices (array of integers).

**Fitness function — number of violated edges + color count penalty (minimize):**
```python
def evaluate(coloring, edges, target_colors):
    violations = sum(1 for u, v in edges if coloring[u] == coloring[v])
    num_colors = len(set(coloring))
    return violations * 10000 + max(0, num_colors - target_colors)
```

**Why it's a good fit:** Graph coloring is NP-hard and extremely well-benchmarked. The DIMACS graph coloring challenge provides standardized instances where the chromatic number is unknown for many graphs. Approaches include greedy heuristics, tabu search, evolutionary algorithms, column generation, and SAT-based methods. The landscape is rugged with many local optima.

**Known best results:** The DIMACS benchmark maintains best known colorings for each instance. Many instances with 100–1000 vertices have open chromatic numbers.

**Practical value:** Register allocation in compilers, scheduling, frequency assignment in telecommunications, map coloring. The 2025 PACE challenge features a graph coloring variant.

**Estimated difficulty:** Good. Select instances where the gap between best known coloring and lower bounds is 1–3 colors. The system can learn instance-specific patterns across generations.

---

## 10. Costas Arrays

**Domain:** Combinatorics / radar signal design

**Solution format:** A permutation of {1, 2, ..., n} — equivalently, positions of n non-attacking rooks on an n×n board such that all displacement vectors between pairs are distinct.

**Fitness function — number of repeated displacement vectors (minimize to 0):**
```python
def evaluate(perm):
    n = len(perm)
    displacements = set()
    violations = 0
    for i in range(n):
        for j in range(i+1, n):
            d = (j - i, perm[j] - perm[i])
            if d in displacements:
                violations += 1
            displacements.add(d)
    return violations  # 0 = valid Costas array; then maximize n
```

**Why it's a good fit:** Costas arrays are known to exist for all n ≤ 27 (and some larger n), but the question of whether they exist for all n remains open. Algebraic constructions (Welch, Golomb) generate Costas arrays for specific sizes (related to prime powers), but leave many orders uncovered. For "hard" sizes (not near primes), exhaustive search has verified existence up to n=29. Finding Costas arrays of larger orders, or proving density results, is publishable.

**Known best results:** All Costas arrays enumerated for n ≤ 29 by exhaustive search. Algebraic constructions work for n = p-1 or n = p-2 (p prime). The largest known Costas array found by search alone (non-algebraic) is around n=200 via algebraic constructions.

**Practical value:** Sonar and radar waveform design. A Costas array defines an ideal ambiguity function for time-frequency radar coding.

**Estimated difficulty:** Moderate. For "verification" sizes (n ≤ 25), the system can match known results. For challenging orders where algebraic methods don't apply (e.g., n where neither n+1 nor n+2 is prime), finding a Costas array by search is meaningful.

---

## 11. Sidon Sets (B₂ Sequences)

**Domain:** Additive number theory / combinatorics

**Solution format:** A subset S ⊂ {0, 1, ..., N} such that all pairwise sums are distinct.

**Fitness function — set size (maximize) with Sidon constraint:**
```python
def evaluate(S, N):
    S = sorted(s for s in S if 0 <= s <= N)
    sums = {}
    violations = 0
    for i in range(len(S)):
        for j in range(i, len(S)):
            s = S[i] + S[j]
            if s in sums:
                violations += 1
            sums[s] = True
    return len(S) - violations * 100  # maximize
```

**Why it's a good fit:** The maximum size of a Sidon set in {1,...,N} is √N + O(N^{1/4}). The best constructions come from Singer (1938) using projective planes, giving |S| ≈ √N. The upper bound was improved to √N + 0.998·N^{1/4} by Balogh, Füredi, and Roy (2021). For specific N values, beating Singer's construction is an open challenge. The search is interesting because you can try hybrid approaches combining algebraic structure with local optimization.

**Known best results:** For prime power q, Singer's construction gives a Sidon set of size q+1 in {0,...,q²+q}. For non-prime-power N, the best constructions are less clean. Tables of best known Sidon sets exist for N up to ~10,000.

**Practical value:** Applications in sparse signal recovery (compressed sensing), coding theory (superimposed codes), and frequency hopping.

**Estimated difficulty:** Good for moderate N (1,000–10,000). The system can learn which algebraic constructions to hybridize with local search. Beating Singer for specific N would be notable.

---

## 12. Hadamard Matrix Construction (Maximal Determinant Problem)

**Domain:** Linear algebra / combinatorial design

**Solution format:** An n × n matrix H with entries in {-1, +1}.

**Fitness function — absolute determinant (maximize):**
```python
import numpy as np
def evaluate(H):
    return abs(np.linalg.det(H))
    # Theoretical upper bound: n^(n/2) (Hadamard bound)
```

**Why it's a good fit:** A Hadamard matrix of order n achieves det = n^(n/2), but these are conjectured to exist only for n = 1, 2, or multiples of 4. The Hadamard conjecture (existence for all multiples of 4) is a major open problem. For n not a multiple of 4, the maximal determinant problem asks for the largest possible determinant. This is unsolved for most n. The search space is 2^(n²) but symmetry reduces it. Approaches: Williamson-type constructions, Paley constructions, local search on matrix entries.

**Known best results:** Will Orrick maintains the maximal determinant website with best known values for n up to ~120. Many entries are not known to be optimal. For n ≡ 1, 2, 3 (mod 4), the Barba/Ehlich/Wojtas bounds provide upper limits.

**Practical value:** Used in compressed sensing, experimental design (D-optimal designs), signal processing, and quantum computing (mutually unbiased bases).

**Estimated difficulty:** Good for n=15–40 (non-Hadamard orders). The system can learn construction techniques (circulant blocks, Williamson arrays) and optimize within structured search spaces.

---

## 13. Permutation Codes (Maximum Hamming Distance)

**Domain:** Coding theory / combinatorics

**Solution format:** A set of permutations of {1, 2, ..., n} with pairwise Hamming distance ≥ d.

**Fitness function — code size (maximize) with distance constraint:**
```python
def evaluate(perms, min_dist):
    violations = 0
    for i in range(len(perms)):
        for j in range(i+1, len(perms)):
            dist = sum(1 for k in range(len(perms[0])) if perms[i][k] != perms[j][k])
            if dist < min_dist:
                violations += 1
    return len(perms) - violations * 1000  # maximize
```

**Why it's a good fit:** The maximum size M(n,d) of a permutation code is known only for small parameters. Tables maintained by researchers (e.g., Montemanni and Smith) list best known bounds for n up to ~20 and various d. Multiple construction methods: group-theoretic (cosets of sharply transitive groups), clique search in distance graphs, partition-and-extend, and greedy/stochastic search. The gap between lower and upper bounds is significant for many parameter pairs.

**Known best results:** Tables of M(n,d) bounds for small n are published in multiple papers. For example, M(6,5) = 6, M(7,5) = 14. Many entries for n=8–15 have gaps.

**Practical value:** Powerline communication, flash memory coding (rank modulation), and data compression. Permutation codes are increasingly relevant for DNA storage.

**Estimated difficulty:** Good for n=7–14 with moderate d. The system can explore different group constructions and local optimization strategies.

---

## Summary Table

| # | Problem | Output Type | Fitness | Eval Time | Gap to Bound | Publishability |
|---|---------|------------|---------|-----------|--------------|----------------|
| 1 | LABS | Binary sequence | Merit factor ↑ | <1s (L≤200) | Large | High |
| 2 | Spherical Codes | Point coordinates | Min distance ↑ | <1s (N≤100) | Medium | High |
| 3 | Ramsey Lower Bounds | Adjacency matrix | Violations ↓ | 1–30s | Medium-Large | Very High |
| 4 | Golomb Rulers | Integer set | Length ↓ | <1s | Small | Very High |
| 5 | Covering Arrays | Integer matrix | Uncovered tuples ↓ | 1–10s | Medium | High |
| 6 | Error-Correcting Codes | Binary matrix | Min distance ↑ | 1–60s | Medium | High |
| 7 | QAP (QAPLIB) | Permutation | Cost ↓ | <1s | Small-Medium | Medium |
| 8 | Cap Sets in F₃ⁿ | Vector subset | Set size ↑ | 1–30s | Large | Very High |
| 9 | Graph Coloring | Integer array | Colors ↓ | <1s | Small | Medium |
| 10 | Costas Arrays | Permutation | Violations ↓ | <1s | Existential | High |
| 11 | Sidon Sets | Integer subset | Set size ↑ | <1s | Medium | High |
| 12 | Hadamard / Max Det | ±1 matrix | |det| ↑ | <1s | Medium | High |
| 13 | Permutation Codes | Permutation set | Code size ↑ | 1–10s | Medium | Medium-High |

## Recommended Starting Points

**For your first benchmarking run (prove the system works):**
- **LABS** (Problem 1) — excellent benchmark with public tables of best-known values, well-studied, and you can immediately see if you match or beat published results for L=60–120.
- **Covering Arrays** (Problem 5) — highly practical, thousands of open bounds, and improvements are directly useful.

**For maximum publishability:**
- **Ramsey Lower Bounds** (Problem 3) — any new lower bound on a Ramsey number, however small, is publishable.
- **Cap Sets** (Problem 8) — connections to cutting-edge additive combinatorics.

**For practical ROI with industry relevance:**
- **QAP** (Problem 7) — well-benchmarked, practically motivated, easy to explain.
- **Covering Arrays** (Problem 5) — direct impact on software testing costs.

**For "dark horse" problems where SOTA is soft:**
- **Permutation Codes** (Problem 13) — less studied, tables have many gaps, multiple approaches.
- **Hadamard/Max-Det** (Problem 12) — non-Hadamard orders are under-explored.
- **Costas Arrays** (Problem 10) — non-algebraic orders are barely explored computationally.

---

*All evaluation functions above are simplified sketches. Production versions should use numpy vectorization, bit-parallel operations, or C extensions for speed. Each can be implemented in <100 lines of Python for `evaluate.py`.*
