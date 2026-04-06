## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` → fitness = 99 (Singer q=97 + perturbation)
Target: 100. Helpers currently available: `is_sidon`, `count_violations`, `differences`, `can_add`, `is_prime`, `prime_factors` in `helpers/core.py`.

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/feedback/system_recommendations.md` — REC-1 details exactly what helpers to build
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/feedback/experiment_suggestions/gen001.md` — EXP-7 specifies the helper requirements
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` — Reference implementation of Singer construction for testing

## Directive

**Build three shared helper functions and deploy them for all future agents.** Four agents in gen 1 independently reimplemented these, wasting ~30 turns and introducing bugs. This is critical infrastructure.

### Helper 1: `find_singer_set(q)`
- Input: prime q
- Output: sorted list of q+1 indices forming a Singer difference set in {0, ..., q²+q}
- Algorithm: GF(q³) construction via irreducible cubic and primitive element
- Reference implementation: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` has working GF(97³) code — generalize it
- **Verification tests:**
  - `find_singer_set(97)` returns 98 elements, all in {0..9506}, `is_sidon()` returns True
  - `find_singer_set(101)` returns 102 elements, all in {0..10302}, `is_sidon()` returns True
  - `find_singer_set(7)` returns 8 elements, `is_sidon()` returns True (small sanity check)

### Helper 2: `greedy_sidon(candidates, N=10000)`
- Input: ordered list of candidate integers, maximum value N
- Output: sorted list forming a valid Sidon set (greedy selection in order)
- Must maintain `used_diffs` incrementally for speed
- **Verification tests:**
  - `greedy_sidon(range(10001))` returns exactly 66 elements (matching baseline)
  - `greedy_sidon(find_singer_set(97))` returns 98 elements (Singer set is already Sidon)

### Helper 3: `build_diff_counts(S)`
- Input: sorted list S (a Sidon set)
- Output: dict mapping each positive difference to count (should be 1 for valid Sidon sets)
- Used by local search to track which differences are free after element removal
- **Verification tests:**
  - For Singer q=97 set: all values should be 1, and the number of differences should be C(98,2) = 4753

### Deployment
Write helpers to `output/helpers/singer.py` (for `find_singer_set`) and `output/helpers/search.py` (for `greedy_sidon` and `build_diff_counts`). The orchestrator will validate and deploy to `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/`.

Each helper must:
- Be a pure function (no side effects, no file I/O at module level)
- Have a docstring explaining usage
- Pass all verification tests above
- Handle edge cases (empty input, q=2)

Run your verification tests as part of the experiment and report results.
