# Observations — gen007_full_1

## Summary

No solutions were produced this session. The agent was interrupted before any code was written.

## What Happened

The session began by reading context files (state_of_affairs.md, rokicki_data.py, gen006/full_1.md,
system_recommendations.md, experiment_suggestions/gen006.md, core.py) to understand the landscape
before implementing the binary variable CP-SAT formulation as directed. The session was interrupted
by the user before any sol*.py files were written.

## Key Context Gathered

- **Best score remains 105** (Bose-Chowla ap q=107, mul=433, Rokicki-Dogon)
- **AllDifferent formulation** (gens 4-6) returned UNKNOWN across 6000+ seconds — REC-5 forbids reuse
- **Directed approach**: Binary variable formulation (x_i ∈ {0,1}), maximize-k objective, warm-start from BEST_105
- **VLNS** had formulation bug (domain [1,N] should be [0,N]); 9 trials were INFEASIBLE artifacts

## No scores to report — zero solutions evaluated.
