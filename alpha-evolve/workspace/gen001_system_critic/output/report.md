# System Critic Debrief — Generation 1

## 1. What did I try?

Read all 4 agent debrief reports (explore_1, explore_2, full_1, research_1), the research
findings in population/gen001/research_1/findings.md, the knowledge base state (ideas/,
patterns/), timing.json, eval_cache.json, and .score sidecar files.

From these I reconstructed: what each agent did, how many solutions were evaluated in-session
vs post-hoc, which approaches beat the baseline, and what the timing data reveals about where
compute was spent.

## 2. What information did I lack?

- **evaluator_report.md** does not exist in reports/gen001/. I do not know the Evaluator's
  own synthesis and strategic recommendations. The ideas/patterns it created are visible, but
  its reasoning about what to prioritize in gen 2 is absent.

- **State of Affairs not updated**. The current state_of_affairs.md is still "Pre-Generation."
  I cannot verify what Layer 0 content the gen-2 Architect will receive.

- **Scores for most gen-1 solutions are in the eval_cache but not in .score sidecars**.
  I can see 37 scored entries in eval_cache.json but only 5 have .score files. I cannot
  definitively map cache entries to specific solutions (hashes to filenames). I know the
  best cache score is 1.5167 but cannot confirm which solution file it belongs to.

- **Brief content for each agent**. I don't know exactly what the Architect told each agent
  (couldn't read briefs/gen001/). This would clarify whether the evaluate-immediately
  instruction was prominent in the actual prompts delivered.

- **Parallel group structure**. I don't know which agents ran in parallel vs sequential in
  gen 1. This affects how to interpret the total wall-clock time.

## 3. What given facts might be wrong or outdated?

- **idea_005 (regularization) may be too harshly marked "disputed"**. The two negative data
  points (TV regularization, L1 normalization) were both confounded with other design choices.
  Simple Adam weight decay was never isolated. I'd treat idea_005 as "requires more testing"
  rather than disputed.

- **The best score being ~1.5167** — I'm reading this from the eval_cache, which doesn't
  identify which solution file it corresponds to. If the evaluator post-processed only
  some solutions, or if there was an eval error, this number might not be confirmed.

- **Pattern_001's assertion that symmetric unimodal = C≥2 always** — technically valid
  per the math, but the claim that "symmetry enforcement" itself is the problem is misleading.
  Symmetric *bimodal* functions are theoretically optimal. The knowledge base needs to be
  clearer that the failure mode is unimodal init WITH symmetry, not symmetry enforcement itself.

## 4. Was the State of Affairs accurate?

The current State of Affairs (generation: 0, Pre-Generation) is severely outdated — it has
not been updated after gen 1. This is a significant gap. The gen-2 Architect will read this
and get no useful guidance about what was learned in gen 1. The knowledge base (ideas/,
patterns/) is more informative than the State of Affairs, but agents are told to read the
State of Affairs as the primary orientation document.

## 5. What would I do differently with more context?

If I had the evaluator_report.md and the briefs/gen001/ content, I could determine:
- Whether the evaluate-immediately instruction was actually prominent in the delivered prompts
  (to assess whether this is a prompt wording issue or a systemic agent compliance issue)
- What the Evaluator's strategic recommendations were for gen 2
- Whether the Architect explicitly or implicitly encouraged writing many solutions

With the score-to-filename mapping from the eval_cache, I could identify exactly which
approaches achieved the best scores and make more specific recommendations.

## 6. Specific experiments to run

See experiment_suggestions.md for detailed experimental designs. In brief:

1. Symmetry + bimodal init (highest priority — tests main theoretical prediction)
2. softplus reparameterization in multi-scale pipeline (direct test of baseline deficiency)
3. Sidon-inspired 4-bump initialization (strong theoretical prior, never tested)
4. Adam → L-BFGS-B with softplus (tests whether refinement step adds value)
5. Higher resolution final phase (N=4000+) — tests if resolution is the bottleneck
6. Smooth max (log-sum-exp) annealing — tests gradient landscape quality

## 7. What surprised me?

- **All 3 solution agents violated evaluate-immediately**. I expected one or two to slip, but
  100% noncompliance is a signal that the workflow instruction is either not being followed or
  not being enforced by the prompt structure. Given that the CLAUDE.md notes this as a "fixed"
  issue (DESIGN-10 MITIGATED), the reality is that it remains unmitigated in practice.

- **The timeout cascade**: both explore agents triggered 3 sessions each (work + wrap-up + debrief).
  The wrap-up session (intended to "catch up" on evaluations) also timed out because the
  agents had so many unevaluated solutions queued up. The three-phase timeout mechanism works,
  but the underlying cause (too many unevaluated solutions) defeats it.

- **Research agent was exceptional** despite timing out. The research_1 findings are
  theoretically grounded, actionable, and directly predict what the next-generation agents
  should try. The agent even correctly noted debugging checks (argmax position for symmetric f)
  and identified specific initialization coordinates (Sidon bumps at {-0.25, -0.167, 0, 0.25}).
  This level of quality from a research-only agent is a strong asset.

- **The pipeline still made progress despite the chaos**: gen-1 best ~1.5167 vs baseline 1.5185
  (~0.001 improvement). Not dramatic, but real. The multi-scale Adam approach is working.
  The concern is that all gen-1 results cluster around 1.517x — if gen 2 doesn't try
  qualitatively different approaches, it will stay in this local minimum.
