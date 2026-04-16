## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen000/baseline/sol02.py` -> fitness = 50572
Second best: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen000/baseline/sol01.py` -> fitness = 101000000

## Read first
- `problems/megaminx/description.md`
- `problems/megaminx/initial_ideas.md`
- `problems/megaminx/initial_facts.md`
- `problems/megaminx/helpers/README.md`
- `problems/megaminx/examples/baseline_cayleypy.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen000/baseline/sol02.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/history/score_progression.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/summary.md`

## Directive
This is a Track B research mission. Find approaches the system has never tried. Read the seeded ideas and dead ends implied by the current baseline to understand what has and has not been tried, then search adjacent sources for stronger Megaminx-specific solver patterns.

Research scope:
- Identify the most actionable patterns from the listed Kaggle Megaminx notebooks and general CayleyPy references.
- Focus on concrete implementation details that a generation-2 explore/full agent could code immediately: predictor architecture, data generation strategy, beam-search objective shaping, MITM state encoding, macro-move construction, or depth-bucket scheduling.
- Compare at least three candidate families and rank them by expected upside, implementation risk, and fit with this environment.

Expected deliverables:
- A findings report that names the highest-leverage next coding directions.
- Concrete implementation notes, not vague summaries.
- At least one recommendation for a generation-2 Track B explore agent and one recommendation for a directed exploit/full agent.

Do not spend time writing solver code unless it is necessary to validate a specific claim. The primary output is actionable research.
