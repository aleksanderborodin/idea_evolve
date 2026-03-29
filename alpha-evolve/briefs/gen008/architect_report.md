# Architect Report — Generation 8

## Data Anomalies

1. **helpers/README.md still says "none yet."** Seven experimentator-created helpers are deployed in `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helpers/` but README was never updated. This has persisted since gen 6. experimentator_1 in gen 8 is tasked with fixing it. Until then, agents reading only the README will think no helpers exist beyond core.py — though in practice, briefs list specific helpers to use.

2. **Score progression display still at 4 decimals.** Priority 3 in system recommendations (gen 7). Gens 4-7 all show "1.502863" — now 4 consecutive generations of hidden progress. This is an orchestrator change, not something agents can fix. The Architect reads the SoA (which has full precision) so this is not blocking, but it misrepresents pipeline health to human observers.

3. **fact_002 outdated for 5 consecutive generations.** Flagged by evaluator gen 5, 6, 7; system critic gen 6, 7; consistency review gen 7. Still not fixed. States "target C ≤ 1.5053" when we've beaten that since gen 3. Very low impact — agents read SoA, not individual facts.

4. **pattern_007 duplicate file** still exists in `patterns/active/`. Flagged for 3 generations. The confirmed version in `patterns/confirmed/pattern_007_update.md` is authoritative.

5. **population/top/ appears empty.** The git status shows deleted rank files but untracked new ones (rank01_1.502863.py through rank10). This may be a display artifact from uncommitted changes.

## Confidence: Medium

**Why Medium (not Medium-High):**
- The interleaving hypothesis (exploit_1) is the highest-value bet but completely untested. If both coord descent and triplets have truly converged, interleaving won't help either.
- Triplets found 0 improvements in a second 20k pass (gen 7). The 160 improvements may have been a one-time gain. All three triplet-based agents could return unchanged solutions.
- The improvement signal is now at the 9th-10th decimal place. FFT artifact risk has not been validated (explore_2 will address this).

**Why not Low:**
- The interleaving protocol is well-motivated by the mathematical structure (different methods perturb different subspaces)
- The experimentator delivers concrete infrastructure value regardless of solution progress
- explore_2's diagnostics will answer 2 persistent open questions even if no score improves
- Every brief is concrete with pseudocode; no vague directives

## What Didn't Fit

1. **Fresh array generation at N=50000.** Gradient descent from random init caps at C~1.509, so a fresh N=50000 array would start 6e-3 above frontier. Would need many gen of coord descent to close the gap. Deferred until explore_2 diagnostics inform whether higher-N arrays are worth the investment.

2. **Column generation LP.** More sophisticated LP approach that starts with 10 variables and iteratively adds profitable columns. Could handle full N=30000. Deferred to gen 9 if explore_2 shows LP is viable at any resolution.

3. **CMA-ES in coordinate subspace.** Listed in cluster_001 remaining opportunities. Speculative — no evidence it would outperform gradient-guided triplets. Would need a full agent.

4. **Simulated annealing at N=30000.** SA at coarse scale is a confirmed dead end (pattern_009), but SA on the 30k array with very low temperature (accepting only improvements) is essentially coord descent. No added value.

## Strategic Risks

1. **Total triplet failure.** If all three triplet/quadruplet agents return 0 improvements, we are at the end of the line for this array. Gen 9 would need a fundamentally different approach (N=50000+, completely different starting point, or declaring the problem solved at C=1.50286).

2. **FFT artifacts invalidate progress.** If explore_2 finds that C varies by >1e-9 across FFT padding sizes, all coord descent and triplet improvements since gen 5 are unreliable. This would be a serious confidence hit.

3. **Helper timing.** The coordinate_descent.py helper won't be available to gen 8 solution agents. The 40x discrepancy in improvement counts will persist for one more generation. exploit_1's brief includes the full standardized delta grid to compensate.

## Open Questions for System Critic

1. **Should we set a "diminishing returns" threshold?** If gen 8 improvement is <1e-9, is it worth continuing? The pipeline is spending $5-10 per generation for 9th-decimal improvements.

2. **Is there a principled way to estimate how far we are from the true optimum?** The lower bound is C≥1.28, the current best is 1.50286. That's a huge gap. Are there tighter lower bounds in the literature?

3. **Should gen 9 attempt N=50000+ from scratch?** If all gen 8 agents return minimal improvements, the TTT-Discover 30k basin may be exhausted. A higher-resolution fresh start is the only remaining structural change, but it requires many generations of coord descent.
