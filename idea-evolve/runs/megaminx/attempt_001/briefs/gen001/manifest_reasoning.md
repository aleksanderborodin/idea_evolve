# Manifest Reasoning — Generation 1

## Situation Assessment

This is a genuine cold start. The run has only two baseline solutions in the population:

- `population/gen000/baseline/sol02.py` at fitness `50572`, which is the sample-submission floor.
- `population/gen000/baseline/sol01.py` at fitness `101000000`, which is effectively the invalid/random sentinel baseline.

There are no generated clusters, no prior-generation reports, no coverage matrix, no solution-idea map, no system recommendations, and no consistency reviews yet. The only strategic knowledge comes from `problems/megaminx/description.md`, the seeded `initial_ideas.md`, and `initial_facts.md`.

The core fact shaping this generation is that the current best solution is not a real solver. It simply echoes Kaggle's sample submission, which is guaranteed valid but leaves enormous headroom. Generation 1 should therefore prioritize breadth of first-principles exploration while still establishing one credible practical baseline that future generations can refine.

## Why This Agent Mix

Per the cold-start rule, I launched exactly:

- 2 `explore`
- 1 `full`
- 1 `research`

I did not launch exploit, genetic, or experimentator instances because there is nothing meaningful to refine or recombine yet, and no concrete open experimental question has emerged from prior generations.

The split is intentional:

- `full_1` is the practical baseline-builder. It should produce the first sample-backed search solver that is both valid and plausibly stronger than the 50572 floor.
- `explore_1` probes a fundamentally different search paradigm: meet-in-the-middle / bidirectional search.
- `explore_2` probes a non-search-heavy angle: path compression and local improvement of known-valid solution strings.
- `research_1` gathers Megaminx-specific external tactics so generation 2 is not constrained to what was pre-seeded in `initial_ideas.md`.

This creates one likely-to-work baseline track and two orthogonal discovery tracks.

## Why These Directions

### `full_1`

The most defensible generation-1 coding task is to turn the existing cayleypy example into a robust solution with a sample fallback and depth-aware budget allocation. That direction is grounded in the seeded ideas, is likely to beat the current floor on short/medium buckets, and creates an obvious exploitation target if it works.

### `explore_1`

Bidirectional / MITM search is strategically important because it attacks the combinatorial barrier differently from beam search. If it shows promise even on a narrow depth band, that is valuable diversity and a possible route away from the unguided-beam ceiling.

### `explore_2`

Path compression is a cheap, structurally different bet. Because every sample path is valid, a method that safely shortens even a subset of them can create wins without solving the entire search problem. This is useful especially if full search remains too expensive.

### `research_1`

The problem description explicitly says the top Kaggle entrants used custom predictors and hand-tuned search. The seeded materials list specific notebooks and references. Research should extract concrete next-step implementations so generation 2 can decide whether predictor training, MITM, or more specialized heuristics deserve priority.

## Parallel Scheduling Choice

`metrics.yaml` says `concurrency: parallel`, so all agents are placed in one parallel group:

`[["explore_1", "explore_2", "full_1", "research_1"]]`

This is the correct wall-clock choice for this problem. There is no benefit to splitting generation 1 into sequential groups because there is no existing intra-generation knowledge to compound yet, and parallel evaluation is explicitly supported.

## Timeout Choices

`history/timing.json` is empty, so I used the problem's documented eval scale instead of historical measurements.

- `research_1: 1800s`
  Research should be the fastest lane. It needs enough time to inspect the provided references and produce a useful report, but it does not need the full default budget.
- `explore_1`, `explore_2: 2400s`
  Both are exploratory coding tasks on a problem where single proxy evaluations can already be substantial. They need room for several write-evaluate cycles.
- `full_1: 2700s`
  This agent has the most likely path to a strong generation-1 result and the broadest end-to-end scope, so it gets the largest budget.

I did not go below 1800s because even CPU-parallel Megaminx evaluations can be non-trivial once cayleypy search is involved.

## What I Deliberately Chose Not To Do

- No `exploit`: there is no meaningful non-baseline solution to defend yet.
- No `genetic`: recombining the sample-submission baseline with the invalid random baseline would be wasted compute.
- No `experimentator`: no recurring helper need or sharply defined pipeline question exists yet.
- No predictor-training implementation in generation 1: it likely has the highest upside, but it is too open-ended for the first coding pass without first harvesting details from research.
- No sequential grouping: the problem is configured for parallel execution, and generation 1 benefits more from breadth than from inter-group feedback.

## Risks And Contingencies

- The `full_1` beam-search baseline may still fail to beat the 50572 floor if unguided search is too weak on the proxy. If that happens, generation 2 should lean harder on either path-compression or learned-predictor directions.
- `explore_1` MITM work may be too expensive or too complex to produce a meaningful result in one session. Even a partial result is still useful if it clarifies feasibility boundaries.
- `explore_2` path-compression may produce only marginal gains. That is acceptable; the point is to test whether structural rewrites of valid paths are a live direction.
- The provided context referenced several files that do not exist yet in this attempt. Agents must rely on the real on-disk files listed in their briefs, not on the stale context paths.

If `research_1` finds a concrete predictor-training recipe with manageable implementation cost, the next generation should likely allocate one Track B explore or full agent to implement it directly.
