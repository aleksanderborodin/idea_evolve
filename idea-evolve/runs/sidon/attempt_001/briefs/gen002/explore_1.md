## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 99 (Singer q=97 + perturbation)
Target: 100. Theoretical upper bound: ~109.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_009.md` — Erdos-Turan construction (reference, different from Singer)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_001.md` — Algebraic constructions (to know what's been tried)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/history/coverage_matrix.md` — What combinations have been tested
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/reports/gen001/research_1.md` — Research findings on alternative constructions

## Directive

**This is a Track B radical exploration. You must NOT use Singer difference sets, Singer perturbation, or any code from `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` or `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/`. Start from scratch with a completely different mathematical framework.**

### What is OFF-LIMITS:
- Singer difference sets (GF(q³) construction) — this is the current dominant approach
- Perturbation of Singer sets
- Starting from any existing 98 or 99-element solution
- Greedy from {0, 1, 2, ...} (confirmed ceiling of 66-68)

### Directions to explore (pick one or combine):

**Option A: Ruzsa Construction.**
Ruzsa's construction: for prime p, define S = {a·p + (a² mod p) : a = 0, ..., p-1}. This gives p elements in {0, ..., p²+p-1} forming a Sidon set. For p=97: 97 elements in {0, ..., 9506}. Different structure from Singer — may have different extension properties. After constructing the Ruzsa base, try greedy extension into {0, ..., 10000}.

**Option B: Bose-Chowla Construction.**
For prime p, the Bose-Chowla construction uses: pick a primitive root g of p, then S = {i·p + (g^i mod p) : i = 0, ..., p-1}. Gives p elements. For p=97 or p=101, this could give 97-101 base elements. Verify the Sidon property carefully — not all formulations are equivalent.

**Option C: Modular Construction with Different Moduli.**
Try constructions in Z_m for composite m or prime-power m. For instance, Sidon sets in Z_{p²} for prime p ≈ 100 could be projected to {0, ..., 10000}. Explore whether non-prime-field constructions give different (potentially better) results.

**Option D: Probabilistic/Randomized Algebraic.**
Use the probabilistic method: randomly sample elements from a structured set (e.g., elements congruent to specific residues mod several primes) and check the Sidon property. This is not pure random search — it's search within algebraically constrained candidate sets.

### Rules:
- Build your solution from mathematical first principles. Do NOT read or copy existing solutions.
- Verify every solution with `is_sidon()` from `helpers/core.py` before submitting.
- Even a score of 90 from a genuinely new construction is valuable — it proves the construction works and can be refined.
- Run `python3 evaluate.py output/solNN.py` after EVERY solution.
- ALL solutions must have zero violations. `validate.py` returns fitness=0 for ANY violations.
