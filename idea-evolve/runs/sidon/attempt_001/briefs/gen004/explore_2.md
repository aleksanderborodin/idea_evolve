## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 102 (Singer q=101 truncation)
Second best: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/rank02_69.py` → fitness = 69 (Fibonacci ordering greedy)

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/history/coverage_matrix.md` (know what has been tried — avoid ALL of it)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_001.md` (Singer-family approaches — avoid these)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_002.md` (search-based approaches — avoid standard greedy/SA)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/description.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py`

## Dead Ends — DO NOT pursue these
- ANY Singer-based approach (q=97, q=101, q=103, perturbation, hybrid)
- SA / simulated annealing from any seed
- Randomized greedy restarts
- Fibonacci ordering greedy (ceiling 69, saturated after 2400 trials)
- Erdos-Turan construction (ceiling 75)
- Probabilistic alteration (ceiling 63)

## CRITICAL: Stale fact files warning
`/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/facts/fact_002.md` says upper bound is "~100-102" — WRONG. Correct: ~109.
`/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/facts/fact_004.md` says validator extracts valid subsets — WRONG. Sentinel scoring, 0 for invalid.

## Directive

**This is a Track B radical exploration. You must NOT use Singer constructions, NOT start from any existing solution in population/, NOT use SA/greedy/local-search as your primary method. Start from scratch with a fundamentally different approach.**

The system has been stuck at 102 for 2 generations. Every existing approach (Singer, ET, greedy, SA, perturbation) has hit proven ceilings. You must find something genuinely new.

### Direction: Constructions from finite geometry / number theory NOT based on Singer

Try ONE OR MORE of these approaches (pick whichever you find most promising):

**Option A — Ruzsa's construction using dense Sidon sets in Z_p:**
For a prime p, consider S = {(x, x²) mod p : x in Z_p} viewed as integers in {0,...,p²-1}. The set {x*p + (x² mod p) : x in {0,...,p-1}} is a Sidon set in {0,...,p²-1}. For p=101, this gives a Sidon set in {0,...,10200}. Truncate to {0,...,10000}. This is a DIFFERENT algebraic family from Singer — it uses quadratic residues, not cyclic difference sets. It should give ~100 elements for p=101.

**Option B — Bose-Chowla construction:**
For prime p and primitive root g of p, the set {i*p + (g^i mod p) : i = 0, 1, ..., p-1} is a Sidon set. This is related to but distinct from Singer. Try different primes near √10000 ≈ 100.

**Option C — Modular Sidon sets with Chinese Remainder Theorem:**
Build Sidon sets modulo small primes (p₁, p₂, ...), then combine using CRT to construct a Sidon set in a larger range. For example:
- Build a Sidon set S₁ in Z_{p₁}
- Build a Sidon set S₂ in Z_{p₂}
- Use CRT: for each (a,b) in S₁ × S₂, compute x such that x ≡ a (mod p₁) and x ≡ b (mod p₂)
- The resulting set is Sidon in Z_{p₁*p₂}

**Option D — Greedy construction with algebraic ordering:**
Instead of ascending or Fibonacci ordering, try orderings based on:
- Quadratic residues: iterate candidates in order of their quadratic residue mod some prime
- Primitive root powers: for prime p near √N, iterate g^0, g^1, g^2, ... mod p, scaled to [0,N]
- Multiplicative characters: order candidates by their discrete log mod p

**Option E — Graph-theoretic / SAT encoding:**
Encode the Sidon constraint as a graph coloring or SAT problem:
- Create a graph where vertices are integers {0,...,10000}
- Add edges between pairs (a,b) and (c,d) if a+b = c+d (same sum constraint)
- Find a maximum independent set

This is NP-hard but modern SAT solvers (minisat, glucose) can sometimes find good solutions with random restarts.

### Rules
1. Test every approach at N=100 or N=1000 FIRST before scaling to N=10000.
2. Run `python3 evaluate.py output/solNN.py` after EACH solution.
3. A score of 80+ from a non-Singer approach would be a significant finding even if it doesn't beat 102. A score of 95+ would be a breakthrough.
4. If you discover an approach that scores 90+ at N=1000 (relative to √1000 ≈ 32), scale it to N=10000.
