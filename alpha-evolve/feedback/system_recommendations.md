# System Recommendations — Generation 2

Prioritized by impact. Each item states what to change, why, and expected effect.

---

## Priority 1 — Fix knowledge base staleness before gen3 launches

**What to change:** The orchestrator or a human operator must manually apply the evaluator's inline recommendations from `reports/gen002/evaluator.md` to the knowledge files, since the evaluator ran out of time to write individual files.

Specifically:
- Update `knowledge/ideas/active/idea_004.md`: lifecycle = disputed→active, confidence = 0.25→0.65. Add evidence from gen002_explore_1_sol02 (1.5093) and sol03 (1.5091).
- Update `knowledge/ideas/established/idea_007.md` (or wherever it lives): confidence = 0.85→0.9. Add gen2 coarse-to-fine confirmation.
- Update `knowledge/ideas/active/idea_010.md`: confidence = 0.4→0.25. Add note: "L-BFGS has zero effect after smooth-max convergence; confirmed by exploit_1/sol01, exploit_1/sol02, explore_2/sol03 in gen002."
- Create `knowledge/ideas/active/idea_013.md`: Coarse-scale SA (N=30-80) before upsampling. lifecycle=active, confidence=0.0 (untested), rationale: Boyer et al., recommended by 3 gen2 agents.
- Create `knowledge/ideas/active/idea_014.md`: Warm-start from existing best solution. lifecycle=active, confidence=0.0.
- Rewrite `knowledge/state_of_affairs.md`: best score 1.5091, update dead ends (fine-grid SA, L-BFGS after smooth-max), update open questions, update coverage.

**Why:** The Architect for gen3 reads the knowledge base. Stale knowledge = bad briefs. The "biggest gap: smooth-max + L-BFGS untested" is now wrong, and the new best is not reflected.

**Expected impact:** Prevents gen3 agents from wasting compute on confirmed dead ends. Ensures coarse-scale SA is correctly elevated as the primary explore target.

---

## Priority 2 — Fix full.md to enforce "cheapest first" rule

**What to change:** Add to `agents/full.md` an explicit first-solution constraint:

> "Your FIRST solution (sol01.py) must be a FAST BASELINE — a stripped-down version that completes evaluation in under 60 seconds. Use the simplest approach (e.g., warm-start from the current best solution + 10 fine-tuning steps) to establish that your pipeline runs. Only in sol02 and sol03 should you add the full complexity of your planned approach."

**Why:** Two consecutive full_1 agents produced over-engineered first solutions that timed out and yielded zero scores. Both agents self-reported the exact same fix. This is a prompt problem, not an agent capability problem — the agent knows the right approach but the prompt doesn't constrain it.

**Expected impact:** full_1 will produce at least one scored solution per generation, recovering 25% of agent compute currently being wasted.

---

## Priority 3 — Add runtime estimation to agent briefs

**What to change:** When the orchestrator writes agent briefs, include a "runtime context" section with observed step rates from the most recent evaluation runs. Format:

```
## Runtime Context
Observed step rate (gen002): ~3000-3700 steps/second (JAX on CPU)
Time budget: ~600 seconds
Safe step budget: ~1.5M total steps (conservative)
```

This can be extracted from the timing.json or inferred from previous agents' step counts and evaluation times.

**Why:** Without knowing steps/sec, agents cannot estimate whether a 3-stage × 12-restart × 20k-step pipeline will complete in 600 seconds or take 20 minutes. This caused the full_1 failure and explore_1/sol03 timeout.

**Expected impact:** Agents can self-regulate compute commitment. Eliminates the primary cause of evaluation timeouts.

---

## Priority 4 — Add `problem/visualize.py` helper

**What to change:** Create `problem/visualize.py` with a function that takes a solution array and plots it via matplotlib (or prints ASCII art if display is unavailable). One suggested interface:

```python
# python3 problem/visualize.py population/gen002/explore_1/sol03.py
# Loads the solution, calls entrypoint(), plots the function f(x) for x in [0,1]
# Saves plot to /tmp/solution_plot.png
```

**Why:** Three gen2 agents and two gen1 agents noted inability to reason about what optimized functions look like. Understanding the shape of the 1.5091 solution would directly inform initialization design (e.g., if the solution is comb-like, design coarse inits with comb-like structure).

**Expected impact:** Agents gain interpretability tools. Moderate improvement in initialization diversity quality.

---

## Priority 5 — Add SA acceptance rate logging to the problem context or agent templates

**What to change:** Either (a) add an SA logging snippet to `agents/explore.md` that shows how to track and print acceptance rate every N SA iterations, or (b) add it to `problem/helper.py`.

```python
# Example snippet for agents:
n_accepted = sum(1 for acc in accepted_log[-10:] if acc)
acceptance_rate = n_accepted / len(accepted_log[-10:])
# Target: 20-50% acceptance. If < 10%, sigma too small. If > 70%, sigma too large.
```

**Why:** explore_2 spent 3 solutions tuning SA hyperparameters blind. Without acceptance rate diagnostics, SA experiments are uninterpretable.

**Expected impact:** SA experiments in gen3 will be diagnosable and improvable within a session.

---

## Priority 6 — Update briefs to specify coarse-scale SA as the primary explore target for gen3

**What to change:** The Architect for gen3 should receive explicit guidance (via the State of Affairs or a dedicated "gen3 priorities" section in the brief) that:
- Coarse-scale SA at N=30-50 is the #1 unexplored priority
- SA must be applied at the COARSE grid (before upsampling), NOT at N=600
- Boyer et al. used N=23 for SA phase; N=30-50 is the recommended starting point

**Why:** explore_2 in gen2 applied SA at the wrong scale (N=600) despite the literature specifically recommending coarse-scale SA. A more explicit brief constraint would have prevented this.

**Expected impact:** Prevents another generation of exploring fine-grid SA, which is confirmed ineffective.

---

## Priority 7 — Attempt to retrieve AlphaEvolve warm-start array

**What to change:** Assign one agent (research or full) to specifically retrieve the AlphaEvolve 600-interval array from the published source. This was identified in gen1 research findings and listed in gen1 agent_gaps but never actioned.

**Why:** AlphaEvolve achieved C=1.5032, which is below the target. Their published array is a known-good starting point that could immediately establish a new baseline and confirm the target is reachable with the current optimization setup.

**Expected impact:** If successful, provides a warm-start at C=1.5032, immediately meeting the target.
