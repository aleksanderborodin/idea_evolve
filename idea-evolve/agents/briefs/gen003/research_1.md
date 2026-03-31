## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problem/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/knowledge/research/gen001/research_1/findings.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/feedback/experiment_suggestions/gen002.md`

## Directive

**Primary objective: Find and retrieve the AlphaEvolve solution array for the First Autocorrelation Inequality problem.**

IdeaEvolve reportedly achieved C = 1.5032 on this problem using a 600-interval discretization. If we can obtain the actual solution array, it provides:
1. An immediate warm-start below our current best (1.5091)
2. A visualization of what a near-optimal function looks like
3. A benchmark to validate our optimization pipeline (can we at least maintain C=1.503 from their starting point?)

**Research plan:**
1. Search for the IdeaEvolve paper/publication on the autocorrelation inequality. Check arXiv, Google Scholar.
2. Search for any published code repositories (GitHub, etc.) associated with IdeaEvolve or the autocorrelation constant problem.
3. Look for the specific 600-point array in supplementary materials, code repos, or data files.
4. If the exact array is found, save it as a Python file implementing `entrypoint()` that returns the array.
5. If the array is not directly available but the paper describes the approach in detail, document:
   - Exact SA parameters used (temperature schedule, perturbation scale, N for coarse stage)
   - Number of SA iterations
   - Any other algorithmic details not in our current knowledge base

**Secondary objective: Find ThetaEvolve's approach (C = 1.503133) if any details are published.**

**Deliverables:**
1. `findings.md` — What was found, where, and how it relates to our optimization.
2. If array retrieved: a working solution file that returns the array via `entrypoint()`.
3. Any new algorithmic insights not already in our knowledge base.

**What we already know (from gen1 research):**
- Boyer et al. (2023) studied this inequality
- The problem arises in additive combinatorics / Sidon sets
- Known bounds: 1.28 <= C <= ~1.5098 (analytical)
- IdeaEvolve used SA at N=23 coarse grid — this is our #1 experiment priority
- ThetaEvolve achieved slightly better than IdeaEvolve

**Do NOT spend time on:**
- Re-deriving mathematical theory we already have
- General optimization literature surveys
- Anything about fine-grid SA (confirmed dead end)
