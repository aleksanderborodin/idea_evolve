# Generation 1 — Strategic Reasoning

## Situation Assessment
- **Generation:** 1 (cold start). No population, no clusters, no coverage data.
- **Baseline:** C = 1.5185 from the initial program (JAX/Adam, N=600, 40k steps).
- **Target:** C <= 1.5053. Gap: ~0.013 (0.9% relative improvement needed).
- **Known bounds:** 1.28 <= C <= 1.5098. The target is very close to the best known upper bound (1.5098), suggesting even modest improvements are meaningful.
- **No timing data** — using default timeouts.

## Agent Mix Rationale

**4 agents total** (2 explore + 1 full + 1 research), per cold-start rules.

### explore_1 — Numerical optimization improvements (sonnet, 1200s)
**Why:** The baseline uses a basic Adam setup. There are many low-hanging fruit improvements: better initialization (Gaussians, cosines), multi-scale optimization (coarse→fine), stronger optimizers (L-BFGS), higher resolution, longer runs. This agent casts a wide net over numerical approaches.

### explore_2 — Analytical/structural constructions (sonnet, 1200s)
**Why:** Maximally orthogonal to explore_1. Instead of black-box optimization, this agent exploits mathematical structure — indicator functions, symmetric constructions, Fourier basis, B-splines. The optimal function likely has a specific shape that can be approximated analytically. These constructions also serve as better initializations for future exploit agents.

### full_1 — Improved baseline (sonnet, 900s)
**Why:** Provides a reliable improved baseline by making systematic, conservative enhancements to the initial program (longer training, higher resolution, better initialization, enforced non-negativity). Even if the explores don't find breakthroughs, this should produce a solid C~1.50-1.51.

### research_1 — Mathematical survey (sonnet, 600s)
**Why:** The problem has deep mathematical roots (additive combinatorics, Sidon sets). Understanding what's known — especially the constructions behind the 1.5098 upper bound and any properties of the extremal function — will inform all future generations. This is a one-time investment.

## Parallel Groups
All 4 agents in one group (no dependencies). Maximum parallelism for gen 1.

## Timeout Choices
- **Explores (1200s):** Extra time for iterating through multiple approaches. These agents need to write, evaluate, and iterate many variants.
- **Full (900s):** Standard. Single focused improvement path, less iteration needed.
- **Research (600s):** Lower. Research produces text, not code; fewer turns needed.

## What I Deliberately Did NOT Do
- **No exploit/genetic agents:** Nothing to refine or cross yet. Cold-start rule.
- **No experimentator:** No hypotheses to test yet; need data first.
- **No opus models:** Gen 1 is exploratory. Sonnet is cost-efficient for broad search. Opus reserved for later exploit/genetic work where precision matters.

## Risks
1. **Explore agents may overlap** despite different directives — e.g., both try Gaussian initialization. Mitigated by explicit "do NOT" constraints in each brief.
2. **Research agent may not find actionable results** — the problem is niche. But even partial findings help.
3. **1200s timeout may be tight** for explores trying many variants. If agents time out, gen 2 will increase timeouts.

## Next Generation Expectations
- Population of 10-20 solutions spanning C~1.49-1.52.
- Research findings identifying optimal function properties and relevant constructions.
- Clear signal on which approach family (numerical vs analytical) is more promising.
- Gen 2 can then launch exploit agents on the best solutions and explore agents on the most promising untried directions.
