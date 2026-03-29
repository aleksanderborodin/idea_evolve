## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen008/explore_1/sol01.py` → C = 1.5028628684790137
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen008/exploit_1/sol01.py` → C = 1.5028628686351897

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_022.md` — Quadruplet perturbation (gen 8 technique)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/established/idea_021.md` — Triplet perturbation
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/patterns/active/pattern_014.md` — Interleaving unlocking effect
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen008/explore_1.md` — Quadruplet implementation details (use as reference)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen008/explore_1/sol01.py` — Starting solution
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/incremental_autoconv_update.py` — O(N) incremental update
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/cross_convolution_f64.py` — Float64 autoconvolution
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/compute_c_f64.py` — Float64 C computation

## Directive

**Implement quintuplet perturbation (d1+d2+d3+d4+d5=0) — 5-element integral-preserving moves.**

This is the next step in the perturbation hierarchy that has driven all recent improvements:
- Pairs: 1 improvement (gen 6)
- Triplets: 160 improvements (gen 7)
- Quadruplets: 8015 improvements (gen 8)
- **Quintuples: untested — you are the first to try this**

**Starting point:** `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen008/explore_1/sol01.py` (C = 1.5028628684790137)

**Implementation:**
1. Select 5 indices using strategies:
   - S0: 5 random from nonzero elements (~25k elements)
   - S1: 2 large (top-10%) + 2 small (bottom-10%) + 1 random
   - S3: 3 random nonzero + 2 fully random from [0..N)
   - (Skip consecutive-neighbor strategy — confirmed weakest for quadruplets)
2. Compute gradient g[m] = 2*dx*f_padded[(n*-idx_m)%M] for each of the 5 elements
3. Project onto sum-zero hyperplane: g_proj = g - mean(g) (4 free variables)
4. Descend: deltas = -alpha * g_proj for 9 step sizes (alpha from 1e-6 to 1e-1, log-spaced)
5. For each step size: check non-negativity (clamp to 0), verify sum(deltas) ≈ 0 after clamping
6. Use first-order approximation for fast screening, exact `incremental_update` only for acceptance

**Run 50k quintuplet trials.** Then:
- If quintuples found improvements: run a quadruplet follow-up pass (20k trials) to test the unlocking hypothesis
- Then run a triplet follow-up pass (20k trials)
- Log per-strategy improvement counts

**Key hypothesis:** If the perturbation landscape has 4D+ structure that quadruplets cannot access, quintuples should find improvements. The pattern so far is increasing move count but decreasing per-move delta. If this continues, quintuples should find O(10k+) improvements with total delta ~1e-11 to 1e-10.

**Performance budget:** At ~100 trials/s, 50k trials ≈ 8 min. Total with follow-ups: ~15 min compute. Well within session budget.

**DO NOT** attempt coord descent, triplets, or quadruplets first. Those are covered by exploit_1. Go directly to quintuples on the gen 8 best array. The whole point is to test the new order, not to redo what's already been tried.

**Log format:**
```
Quintuplet pass: N trials, N improvements (S0: N, S1: N, S3: N), delta_C = X.XXe-XX
Quadruplet follow-up: N trials, N improvements, delta_C = X.XXe-XX
Triplet follow-up: N trials, N improvements, delta_C = X.XXe-XX
Final C = X.XXXXXXXXXXXXXXXX
```
