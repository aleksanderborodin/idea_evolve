# Manifest Reasoning — Generation 2

## Situation assessment

Generation 1 established a real but narrow floor: `46312`, entirely from cancellation-based compression of the guaranteed-valid sample submission. Every valid competitive solution converged to that same number. The score progression improved strongly from the zero-search baseline `50572`, but the run is now sitting on a clear local floor rather than a promising frontier.

The central strategic fact is unchanged across the state of affairs, clusters, consistency review, and system recommendations: no solution actually ran predictor-guided beam search despite that being the highest-upside path. Unguided beam search is already saturated. The most important unanswered yes/no question is whether any predictor, even the cheap hamming one, beats compression on the proxy.

## Why this agent mix

I chose five agents:

- `exploit_1` to push the strongest existing scaffold (`gen001/full_1/sol01.py`) into actual predictor-guided search without losing the guaranteed-valid fallback behavior.
- `experimentator_1` because the system critic made the hamming predictor baseline a critical recommendation, and generation 2 is exactly when that tight measurement should happen.
- `explore_1` as a Track B radical search-family bet outside beam search entirely.
- `explore_2` as a second Track B branch on algebraic / long-range rewrite rules, explicitly separated from both predictor work and the debunked `idea_002` shortcut.
- `research_1` because the mandatory Track B research lane should keep feeding genuinely new implementation ideas instead of letting the knowledge base collapse into exploit-only local search.

This satisfies the mandatory two-track rule: one directed exploitation lane plus a research lane and two radical exploration lanes that are forbidden from simply refining the current best.

## Why these directions

### exploit_1

This is the highest expected-value agent. The best gen001 solution already has a valid bucket-aware fallback structure. The missing piece is predictor injection and guided search. The brief points it straight at that gap and explicitly forbids more unguided parameter sweeps.

### experimentator_1

This answers the narrowest critical question first: does `Predictor(graph, 'hamming')` help at all? If the answer is no, future generations should treat trained predictors as mandatory rather than optional. If yes, the exploit lane has a cheap baseline to build from. I also allowed a minimal shared helper only if it directly removes predictor-interface friction.

### explore_1

The system is at real risk of beam-search monoculture. This brief forces a new search family, ideally IDA* or a restricted pattern-database style approach. Even a partial-bucket success would be strategically useful because it opens a basin of attraction that is not beam-based.

### explore_2

Compression may still have limited headroom, but gen001 only tested adjacent cancellation plus one invalid heuristic. This brief tests whether automatically verified rewrite rules or valid identities exist beyond that. It is intentionally orthogonal to predictor work and to search-family work.

### research_1

Research in gen001 was useful but too broad. This brief narrows it to implementation-grade extraction: notebook details, local cayleypy API behavior, and actionable recipes for predictor training or tuned guided search. The goal is to produce instructions a gen003 solution agent can apply immediately.

## Scheduling decision

`metrics.yaml` says `concurrency: parallel`, and the problem docs say evaluations are CPU-only and cache-friendly. Following the architect rules, all agents are placed in one parallel group. Splitting into sequential groups would only add light-evaluator overhead without resource benefits.

## Timeout choices

Generation-1 timings were informative:

- `explore_2` finished in ~354s, so simple compression-style exploration is cheap.
- `research_1` took ~713s and still left important work unfinished.
- `explore_1` took ~1184s.
- `full_1` hit the 2700s limit and needed wrap-up + debrief, showing that end-to-end search experimentation can easily consume a long budget.

Based on that:

- `exploit_1`: `2400s` because it is the most complex implementation task but should still be narrower than gen001 full-agent breadth.
- `experimentator_1`: `1800s` because the experiment is narrow but may need direct API work and a helper shim.
- `explore_1`: `2100s` because a fresh search-family prototype is likely to involve more iteration than compression work.
- `explore_2`: `1800s` because algebraic rewrite discovery is exploratory but should not need the longest budget.
- `research_1`: `1800s` to address the system critic's concern that gen001 research scope was too broad for its budget.

## What I chose not to do

- No `full` agent in gen002. Generation 1 already used a full end-to-end baseline; gen002 should spend compute on targeted questions rather than another broad baseline rewrite.
- No `genetic` agent. There is not enough meaningful solution diversity yet; most valid gen001 solutions are the same compression floor in different wrappers.
- No second exploit. Until at least one predictor-guided or genuinely orthogonal solution shows evidence of traction, a second exploit would likely duplicate work.
- No dedicated experimentator for MITM coverage yet. That question matters, but the hamming predictor baseline is the more important gating measurement.

## Risks and contingencies

- The helper interface friction may still slow down predictor experiments if agents spend too much time working around it.
- The radical explore lanes may fail to beat 46312. That is acceptable if they produce real evidence about ceilings or promising new mechanisms.
- Research may again encounter inaccessible Kaggle artifacts. The brief explicitly allows a quick pivot to local API/source inspection to avoid wasting the session.
- If the hamming predictor is useless and trained predictors are too slow or weak, generation 3 may need to pivot harder toward bucket-specialized search or richer helper infrastructure.
