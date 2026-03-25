# System Critic Debrief — Generation 2

## 1. What did I try?

Read all available gen2 reports:
- `reports/gen002/explore_1.md` — coarse-to-fine agent, new best C=1.5091
- `reports/gen002/explore_2.md` — SA wrapper agent, best 1.5108 (no improvement)
- `reports/gen002/exploit_1.md` — deeper smooth-max agent, best 1.5107 (marginal)
- `reports/gen002/full_1.md` — combined pipeline agent, 0 scored solutions
- `reports/gen002/evaluator.md` — evaluator report with strategic shift flag
- `reports/gen002/evaluator_debrief.md` — critical: states individual knowledge files NOT written

Read supporting context:
- `population/gen002/{explore_1,explore_2,exploit_1,full_1}/observations.md` — all 4 agents
- `feedback/agent_gaps/gen001.md` and `gen002.md`
- `knowledge/state_of_affairs.md` — gen1 state, not updated for gen2
- `history/generations/gen001.md` and `gen002.md`

No prior `feedback/system_recommendations.md` existed (no gen1 system critic ran, or the file was not preserved).

All reads succeeded. No consistency review files existed.

## 2. What information did I lack?

- **The actual knowledge file contents** (idea_004.md, idea_007.md, idea_010.md etc.) — I read the State of Affairs but not individual idea files. This meant I was assessing knowledge base staleness from the evaluator's debrief description rather than by direct inspection. I should have read `knowledge/ideas/` to verify what state the files are currently in (e.g., whether the orchestrator already applied the evaluator's inline recommendations).

- **user/config.yaml** — I didn't read the pipeline config (max_turns, timeouts, agent enables). This would have told me the actual timeout budgets agents are given, relevant to diagnosing the full_1 failure.

- **The full.md agent template** — I diagnosed that it doesn't enforce "cheapest first" based on agent behavior, but didn't confirm by reading the prompt. My recommendation could be already present in the template.

- **Whether the orchestrator applies inline evaluator recommendations** — My most critical finding (evaluator didn't write individual knowledge files) hinges on whether the orchestrator has a fallback that reads evaluator_report.md inline. I don't know if this is handled in orchestrator.py.

- **Previous system critic output** — feedback/system_recommendations.md doesn't exist, so I can't compare my findings against gen1 recommendations. I don't know if the "cheapest first" rule was already recommended and ignored, or if this is being caught for the first time.

## 3. What given facts might be wrong or outdated?

- The State of Affairs says best score = 1.5108. The actual current best is 1.5091. If any gen3 agent reads only the State of Affairs, they have a wrong picture.

- The State of Affairs says "Biggest gap: smooth-max + L-BFGS, coarse-to-fine, SA" — all three of these have now been tested. L-BFGS + smooth-max is a dead end. Coarse-to-fine is the breakthrough. SA at fine scale is dead; SA at coarse scale is the new priority.

- idea_010 (L-BFGS fine-tuning) likely still has confidence 0.4 in its file, which overstates its usefulness after gen2's results.

- The evaluator's `strategic_shift: true` flag in its YAML frontmatter (evaluator.md line 3) suggests the orchestrator might trigger a consistency review. If so, that reviewer would also be reading a stale State of Affairs.

## 4. Was the State of Affairs accurate?

No — it's accurate for gen1 but stale for gen2. It correctly identified the highest-priority gap (coarse-to-fine + smooth-max), which was explored and confirmed. But it has not been updated with:
- New best score (1.5091)
- Confirmed dead ends (fine-grid SA, L-BFGS after smooth-max)
- New priority experiment (coarse-scale SA)
- Resolution of the 4 open questions (L-BFGS: no; coarse-to-fine: yes; visualization: still missing; SA at coarse: untested)

This is a direct consequence of the evaluator running out of time. The evaluator correctly triaged (scoring > knowledge updates), but the downstream consequence is a stale knowledge base entering gen3.

## 5. What would I do differently with more or different context?

1. Read the actual idea files to verify current lifecycle/confidence state rather than inferring from debrief text.
2. Read user/config.yaml to understand actual timeout budgets and turn limits.
3. Read agents/full.md to confirm whether "cheapest first" rule is or isn't there already.
4. Read orchestrator.py (or ask) whether the evaluator's inline-only output is handled downstream.
5. Look at the briefs for gen002 (briefs/gen002/) to understand what the Architect actually told agents — this would let me identify whether the SA scale error (explore_2 doing fine-grid SA) was a prompt failure or agent failure.

## 6. Specific experiments to run

See experiment_suggestions.md for the full list. Top priority:
1. Coarse-scale SA at N=30-50 before upsampling (Boyer et al. approach, never tried)
2. Warm-start polish from 1.5091 solution (cheap, fast, high ROI)
3. AlphaEvolve array retrieval (instant path to target if array is accessible)

## 7. What surprised me?

- **The evaluator's incomplete output is the most critical finding** and was not anticipated. The evaluator correctly prioritized (scoring is more important than knowledge file structure), but the consequence is that the entire knowledge base may be stale entering gen3. The system has no mechanism to detect that knowledge files haven't been updated — the orchestrator just proceeds.

- **The cold vs warm fine-stage gap (0.0095 score difference) is larger than the entire gen1 improvement (0.0077).** A single hyperparameter choice (fine stage starting temperature) swings results more than the entire previous generation of work. This underscores how sensitive this problem is to "obvious-seeming" design choices that aren't actually obvious.

- **Three agents independently recommended the same experiment (coarse-scale SA) for gen3.** This is a strong convergent signal from the pipeline. The Architect should treat this near-unanimity as a strong prior.

- **full_1 wasted its entire slot for the second consecutive generation.** What's surprising is that the agent correctly diagnosed the fix ("profile first, then scale; cheapest variant first") in its own debrief. The prompt is producing agents that know the right strategy but don't apply it until after they've failed. This suggests the prompt needs to make the constraint explicit and mandatory, not just leave it to agent judgment.
