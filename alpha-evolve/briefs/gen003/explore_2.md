## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helper.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/evaluate.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_004.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/established/idea_007.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/established/idea_012.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/population/gen002/explore_1/sol03.py`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/research/gen001/research_1/findings.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/feedback/experiment_suggestions/gen002.md`

## Directive

**Primary objective: Test structurally diverse coarse initializations with coarse-to-fine + warm smooth-max.** All top solutions use Gaussian bump initializations, which may funnel to the same basin. This experiment tests whether qualitatively different initializations find new basins.

**Hypothesis:** The Gaussian-bump init family all converge to the same ~1.509 basin. Structurally different inits (arcsine, comb, step, half-domain) may find basins that survive upsampling to N=600 and yield lower C values.

**Implementation plan — sol01 (fast baseline):**
1. At N=80, implement 5 initialization families (2 seeds each = 10 total):
   a. **Gaussian bumps** (current baseline — control group): random positions/widths
   b. **Comb function**: sum of 3-5 narrow peaks at evenly spaced positions
   c. **Arcsine-weighted**: f(x) proportional to 1/sqrt((x-a)(b-x)) for some subinterval [a,b] within [-0.25, 0.25]
   d. **Random step function**: piecewise constant with 8-12 random-height segments
   e. **Half-domain**: f=0 for x < 0, smooth random function for x > 0 (extreme asymmetry)
2. For each seed: warm smooth-max at N=80 (T=0.1→0.05→0.01→0.003, 8k steps each)
3. Upsample best from each family to N=600
4. Warm smooth-max fine-tuning (T=0.05→0.01→0.003→0.001→0.0003, 15k steps each)
5. **Report per-family best and variance** — this is the key deliverable

**Write sol01 with the simplest version first** (3 families, 2 seeds each). Evaluate immediately. Then expand.

**Follow-up (sol02+):** Focus compute on whichever init family produces the lowest score. Increase seeds for that family to 8-12.

**Critical rules:**
- Fine stage MUST start warm (T=0.05). Cold fine stage is a dead end.
- Use softplus reparameterization.
- Evaluate EACH solution immediately after writing. Do not batch.
- Asymmetry is required — symmetric inits give C >= 2 (mathematical fact, idea_012).

**Do NOT:**
- Use L-BFGS after smooth-max (confirmed dead end)
- Use SA at N=600 (confirmed dead end)
- Use symmetric initializations
- Spend all budget on one init family — the point is diversity comparison

**Current best: C = 1.5091.** Target: C <= 1.5053.
