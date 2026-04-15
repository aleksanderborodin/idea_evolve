## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/permcodes/attempt_001/population/gen000/baseline/sol01.py` → fitness 262 (greedy baseline)
No top/ directory yet — this is generation 1.

## Read First
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/agl18.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/compat.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/core.py`

## Directive

**This is a Track B radical exploration using alternative algebraic group structures.** Do NOT use the AGL(1,8) construction — that is covered by another agent. Your specific contribution is to find a different algebraic framework that might yield a larger code.

**Background:** AGL(1,8) = {x → ax+b : a ∈ GF(8)*, b ∈ GF(8)} has 7×8=56 elements, partitioning S₈ into 720 orbits of size 56. The max clique in the orbit compatibility graph is 11 (→ 616 codewords). We need to try different groups.

**Approach A — AΓL(1,8): the semilinear affine group**

AΓL(1,8) extends AGL(1,8) by adding the Frobenius automorphism φ: x → x². This gives:
- AΓL(1,8) = {x → a·φᵏ(x) + b : a ∈ GF(8)*, b ∈ GF(8), k ∈ {0,1,2}}
- Group size: 56 × 3 = 168 elements
- Orbits: 40320 / 168 = 240 orbits, each of size 168

Larger orbits → fewer orbits → smaller compatibility graph → potentially different/larger clique.

Implement this:
1. Generate all 168 elements of AΓL(1,8): for each (a, k, b), map x → GF8_mul(a, x^(2^k)) ⊕ b, where x^(2^k) is the Frobenius: x^1=x, x^2=x², x^4=x⁴ in GF(8)
   - k=0: x → ax+b (the AGL(1,8) maps, 56 elements)
   - k=1: x → a·x²+b (56 elements, where x² means GF(8) squaring, i.e., square in GF(8))
   - k=2: x → a·x⁴+b (56 elements, where x⁴ is the Frobenius squared)
   - Note: GF(8) squaring: if x=α^i then x²=α^(2i mod 7) (for nonzero x; 0²=0)
   - GF(8) with primitive poly x³+x+1: 0→0, 1→1, 2→4, 3→5, 4→2, 5→3, 6→7, 7→6 (squaring map)
2. Partition S₈ into 240 orbits under left-action of AΓL(1,8)
3. Build the orbit compatibility graph (240×240)
4. Find the max clique (greedy from highest-degree vertex)
5. Expand clique orbits into full codeword sets

Write as `output/sol01.py`. Evaluate immediately.

**Approach B — Direct clique search on a random subset**

Instead of group orbits, try a direct probabilistic max-clique approach:
1. Build all 40320 permutations as vertices
2. Use the precomputed bucket_ids (from helpers/compat.py) for fast adjacency checking
3. Run multiple iterations of a greedy constructive heuristic:
   - Pick a random starting vertex
   - Repeatedly add the compatible vertex with the most connections to remaining compatible vertices (greedy densest-first)
4. Use beam search: maintain top-B partial cliques at each step

Write as `output/sol02.py`. This is parameter-heavy — try beam width B=10, 100 iterations. Evaluate immediately.

**Approach C — Coset construction**

Sharply transitive subgroups of S₈ each give a natural code. Try:
1. Take the cyclic group C₈ = {0→1→2→...→7→0, 0→2→4→6→1→3→5→7→0, ...}: the 8 cyclic shifts
2. Enumerate all cosets of a small subgroup H in S₈
3. For each such coset decomposition, pick one representative per coset such that pairwise distances are ≥ 5
4. Specifically: try using the dihedral group D₈ (8 rotations + 8 reflections of octagon) as the seed group

Write as `output/sol03.py`. Evaluate immediately.

**Mandatory workflow:** Write one solution → run evaluate.py → verify .score file created → next solution.

The evaluate.py path is:
```bash
python3 /home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/evaluate.py output/sol01.py
```

Write `output/report.md` after all solutions are evaluated:
- Scores for each approach
- For AΓL(1,8): how many orbits, what clique size, final codeword count
- For direct clique search: best clique found, computational cost
- For coset construction: code size achieved
- Recommendations: which algebraic group structure seems most promising to pursue further
- Any theoretical observations about why certain groups might yield larger codes
