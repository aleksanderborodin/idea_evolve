## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/permcodes/attempt_001/population/gen000/baseline/sol01.py` → fitness 262 (greedy baseline)
No top/ directory yet — this is generation 1.

## Read First
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/constraints.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/agl18.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/compat.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/core.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/evaluate.py`

## Directive

Your mission: implement the AGL(1,8) algebraic construction and get the authoritative 616-codeword baseline on the board. This is the "establish our floor" task — we know this construction works, we just need it evaluated and scored.

**Background:** The problem is M(8,5) — find the largest set of permutations of {0,...,7} with pairwise Hamming distance ≥ 5. The best known lower bound is 616, achieved by Smith & Montemanni (2012) via AGL(1,8) orbit clique search. The helpers already implement this construction fully in `helpers/agl18.py`.

**Step 1 — AGL(1,8) baseline (target: 616):**
Use `agl18_max_clique_code(d=5)` from `helpers/agl18.py` directly. This finds the 11-orbit max clique in the AGL(1,8) compatibility graph and returns 616 codewords.

Write `output/sol01.py` implementing:
```python
from helpers.agl18 import agl18_max_clique_code
def entrypoint():
    return agl18_max_clique_code(d=5)
```

Evaluate immediately:
```bash
python3 /home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/evaluate.py output/sol01.py
```

Verify the `.score` file is created. Expected output: fitness=616, is_valid=1, min_distance=5.

**Step 2 — Greedy extension (target: 617+):**
Starting from the 616-codeword code, try to greedily add more codewords. Use `fast_compatible_mask` from `helpers/compat.py` for speed:

1. Get all 40320 permutations (build_all_perms)
2. Build bucket_ids once (build_bucket_ids)
3. Get indices of current 616 codewords within all_perms
4. Use fast_compatible_mask to find all permutations compatible with the entire code
5. If ANY compatible permutations exist, add them greedily

Write this as `output/sol02.py`. Evaluate immediately after writing. If it scores > 616, excellent. If not (and it returns 616 or less), that is also fine — it confirms the AGL(1,8) code may be maximal under this group structure.

**Step 3 — Stochastic greedy restart (target: 617+):**
Write `output/sol03.py` that:
1. Starts from the AGL(1,8) code
2. Randomly drops 10-30 codewords
3. Uses fast_compatible_mask to find all still-compatible permutations
4. Greedily refills, but in random order to potentially find different codewords
5. Repeats 5-10 times, keeps the best result

Evaluate immediately after writing.

**Mandatory workflow:** After EACH solution file is written, run evaluate.py and verify the `.score` file was created before writing the next solution.

**Working directory:** You are operating in the workspace. Write solution files to `output/` relative to your workspace. When you run evaluate.py, the `IDEA_EVOLVE_RUN_ROOT` environment variable is already set by the orchestrator.

**Important:** Import helpers as `from helpers.agl18 import ...` (not relative imports). The evaluate.py adds the problem directory to sys.path automatically.

After all solutions are written and evaluated, write `output/report.md` summarizing:
- Which solutions you produced and their scores
- Whether greedy extension found anything beyond 616
- Whether stochastic restart added codewords
- What the maximum compatible set size appears to be from the AGL(1,8) starting point
- Any observations about the code structure (are there compatible permutations outside the 11 orbits?)
