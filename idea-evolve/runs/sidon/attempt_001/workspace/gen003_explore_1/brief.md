## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` -> fitness = 102 (Singer q=101 truncation)
All top-10 solutions score 102. Target: 109.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/history/coverage_matrix.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/description.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py`

## Directive

**This is a Track B radical exploration. You must NOT start from the current 102-element Singer set. You must NOT use Singer difference sets, cyclic shifts, or GF(q^3) constructions. Start from scratch with a completely different approach.**

Your goal: construct a Sidon set in {0,...,10000} using a method that has NEVER been tried in this system. All current top solutions use Singer q=101. You must find a different basin of attraction.

**Suggested directions (pick ONE and go deep):**

1. **Correct Bose-Chowla construction.** The versions tried before used carry-violating formulas. The REAL Bose-Chowla theorem says: if g is a primitive root mod p^2, then {i : 0 <= i < p, g^i mod p^2 has a specific property} forms a Sidon set. Research the correct formulation, implement it, and test for primes near 100. This is NOT the same as {i*p + g^i%p} which was already tried and failed.

2. **Modular Sidon sets via quadratic residues in Z_p.** For a prime p, the set {x^2 mod p : x in Z_p} has the Sidon-like property in Z_p. Lift this to a Sidon set in the integers via careful embedding. Different from Erdos-Turan.

3. **Probabilistic construction with derandomization.** Use the Lovasz Local Lemma or the alteration method: start with a random subset of {0,...,10000} where each element is included with probability ~N^{-1/3}, then iteratively remove elements involved in collisions. Repeat with many random seeds.

4. **Perfect difference set constructions beyond Singer.** Gordon-Mills-Welch (GMW) difference sets, or Hall's sextic residue construction. These produce difference sets with different structure than Singer.

**Rules:**
- Do NOT read or use `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` or any file in `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/`.
- Do NOT implement Singer q=101 or any Singer construction.
- Do NOT use greedy-from-scratch (known ceiling: 66-75).
- You ARE allowed to use helpers from `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py` (is_sidon, can_add, etc.)
- Write multiple solutions exploring different parameters of your chosen approach.
- Evaluate EVERY solution immediately: `python3 evaluate.py output/solNN.py`

A score of 85 from a genuinely new approach is more valuable than yet another 102 from Singer.

## Dead Ends -- Do NOT Investigate
- Singer q=97..109 (exhausted, ceiling 102)
- SA/local search from any existing solution
- Ruzsa {a*p + a^2%p} (carry violations for p>=11)
- Bose-Chowla {i*p + g^i%p} (carry violations for p>=11)
- Plain randomized greedy (ceiling 66)
- Erdos-Turan {2pk + k^2%p} (ceiling 75, already thoroughly tested)
