# Agent Gaps — Generation 1

## Workflow Gaps

### 1. Evaluate-immediately workflow violated by all agents
- **explore_1**: Evaluated sol01-04 properly, then wrote sol05-sol13 without evaluation (timeout)
- **explore_2**: Evaluated only sol01, wrote sol02-sol12 without evaluation
- **full_1**: Wrote all 5 solutions without evaluation (timeout, though sol03 was informally tested)
- **Impact**: 25 of 30 solutions lacked .score files. The evaluator had to verify all 30.
- **Recommendation**: Agents must be more disciplined about evaluating after EACH solution.
  Consider reducing solution count targets in briefs and emphasizing quality over quantity.

### 2. No observations.md written by any agent
- None of the three solution agents wrote observations.md
- This means intermediate findings (which init worked, what the function shape looks like,
  what error messages appeared) are lost
- **Impact**: Medium — debrief reports captured most key observations, but structured
  observations would help the evaluator

### 3. explore_2 did not read the baseline before starting
- Started with a symmetric Gaussian (C=2.0) when the baseline flat-block init achieves 1.5185
- Wasted the first 1-2 solutions on approaches strictly worse than baseline
- **Recommendation**: Brief should require reading initial_programs/optimize.py first

## Knowledge Gaps

### 4. Function shape of best solutions unknown
- No agent reported what the optimized function LOOKS LIKE (plot, qualitative description)
- Is it unimodal? Multi-bump? Where are the peaks? What does the autoconvolution look like?
- This information is critical for validating research_1's prediction that multi-bump is better
- **Recommendation**: Next generation agents should print/describe the shape of their best solution

### 5. Softplus reparameterization untested in isolation
- Research_1 called this "the single most important change" but no solution tested
  softplus + Adam (only softplus + L-BFGS, which is confounded)
- **Recommendation**: Explicit experiment: Adam + softplus vs Adam + relu, same init, same budget

### 6. Sidon-set initializations untested
- Research_1 provided specific multi-bump positions but no solution agent tried them
- This is the highest-priority unexplored direction
- **Recommendation**: Priority brief for explore agent in gen 2

## Pipeline Gaps

### 7. Agent timeout causing incomplete evaluation
- 3 of 3 solution agents hit timeout before completing all evaluations
- The computation-heavy solutions (N=2000+, 80k+ steps) each take significant wall-clock time
- **Recommendation**: Architect should set more generous timeouts for heavy-optimization agents,
  or brief agents to attempt fewer but more thoroughly evaluated solutions

### 8. Research findings not consumed by solution agents
- research_1 produced findings in the same generation, but solution agents (running in parallel)
  could not access them
- **Impact**: Solution agents independently discovered things (e.g., symmetry dead end) that
  research already identified
- **Recommendation**: Consider running research agents in an earlier parallel group so their
  findings are available to solution agents
