# Manifest Reasoning — Generation 4

## Situation Assessment

**Score**: 102 (Singer q=101 truncation). Plateaued for 2 generations.
**Target**: 109. Gap: 7 elements (6.9% improvement needed).
**Trajectory**: Flat. Singer approaches are mathematically proven exhausted. The 102-element set has 45+ minimum blockers per non-member and zero addable elements. No perturbation, SA, or local search has ever improved on 102.

**Non-algebraic ceiling**: 69 (Fibonacci ordering greedy, 2400+ parameter search). This is 33 elements below Singer and unlikely to be a path to 103+.

**Key unknowns**:
1. Is 102 the published best for N=10000? Three research agents have failed to answer this.
2. Is ILP feasible with the correct formulation? One attempt used the wrong formulation and crashed.
3. Can elements from different algebraic families be combined? Never tested.
4. Can min-blocking greedy (correctly implemented) beat 69? Never tested.

## Agent Mix Rationale

### Track A — Directed work (3 agents)

**full_1 (ILP/CP-SAT)**: Highest priority. The system critic, evaluator, architect, and multiple agents across 3 generations have all identified ILP as the most promising path forward. The one attempt (gen 3 explore_2) used the wrong formulation (quadruple constraints, 661K for M=200). The correct difference-indicator formulation has O(N²) constraints but much sparser, and CP-SAT should handle it. I'm giving this a `full` type because it's an end-to-end approach that needs careful formulation, validation at small N, and scaling. Timeout 1800s because solver execution takes time.

**explore_1 (min-blocking greedy, correct impl)**: The concept from idea_016 was broken in gen 3 — the implementation didn't enforce Sidon validity. A correct min-blocking greedy that picks the least-blocking valid candidate at each step could plausibly reach 72-80 elements (above the 69 non-algebraic ceiling). Combined with backtracking variants (idea_005), this could establish a new non-algebraic baseline. Even if it doesn't beat 102, it provides diversity and structural insight.

**experimentator_1 (hybrid + spectrum analysis)**: Two quick experiments. EXP-6 (multi-Singer hybrid) resolves idea_013 — either we find a combination >102 or debunk it. EXP-4 (difference spectrum) provides structural understanding of why 102 is rigid and whether element trading is possible. Both are computationally cheap (<20 min each) and close open questions.

### Track B — Radical exploration (2 agents)

**explore_2 (non-Singer algebraic constructions)**: Must NOT use Singer, SA, greedy, or any existing approach. Directed to try Ruzsa's construction (S = {(x, x² mod p)}), Bose-Chowla, CRT-based combinations, or graph-theoretic encodings. These are genuinely different algebraic families that could produce competitive Sidon sets through completely different mathematics. Even a score of 80+ from a non-Singer algebraic approach would open a new optimization basin.

**research_1 (literature search + new constructions)**: Must finally complete the F(10000) literature search. Brief enforces incremental output (write after every query) so that even a timeout produces partial findings. Also searches for Cilleruelo, Paley, and other algebraic constructions. This is the 4th attempt at the literature search — the brief is structured to force early output.

## Timeout Rationale

- **full_1: 1800s** — ILP solvers need wall-clock time. Scaling from N=100 to N=10000 with multiple solver runs requires extended time.
- **explore_1: 1200s** — Algorithmic implementation + testing at N=1000 + scaling to N=10000. Standard explore budget.
- **explore_2: 1200s** — Multiple algebraic constructions to try. Standard explore budget.
- **research_1: 1200s** — Literature search with web access. Previous research agent (gen 1) completed in 698s but gen 3 failed (timeout unclear). 1200s should suffice with the incremental output requirement.
- **experimentator_1: 900s** — Two focused computational experiments. Each is <20 min. 900s gives buffer.

## What I Deliberately Did NOT Do

1. **No exploit agent.** There is nothing to exploit. The best solution (102) has been proven rigid — 4000+ perturbation trials, SA, greedy extension all fail. An exploit agent would waste compute confirming what pattern_009 and pattern_010 already establish.

2. **No genetic crossover.** All top solutions are identical (Singer q=101). Crossing two copies of the same solution is pointless. Crossing Singer with a 69-element non-algebraic set is unlikely to produce anything useful — the difference structures are incompatible. The experimentator_1 hybrid test addresses this question more efficiently.

3. **Deferred Fibonacci exhaustive search.** explore_2 (gen 3) searched 2400 Fibonacci parameters and found 69. More parameter search could find 70 but is extremely unlikely to reach 80+. Not worth an agent slot.

4. **No additional experimentator for helpers.** The gen 3 experimentator deployed singer.py, optimal_shift.py, search.py. These helpers are confirmed present in `problem/helpers/`. No new helper needs identified.

## Risks

1. **ILP may be infeasible at N=10000.** CP-SAT for N=10000 creates ~10000 x variables and ~50M auxiliary variables (10000 differences × 5000 pairs each). This may exceed memory. Mitigation: the brief instructs starting small and scaling.

2. **Research agent fails again.** 4th attempt. Mitigation: incremental output requirement. Even partial findings (one arXiv paper) are valuable.

3. **All Track B scores are <80.** If neither Ruzsa, Bose-Chowla, nor min-blocking greedy produces competitive results, we learn that Singer really is the only path to 100+. That's useful knowledge but doesn't advance the score.

4. **explore_2 reinvents Singer.** Some of the suggested constructions (Bose-Chowla) are mathematically related to Singer. The agent might discover this and pivot to Singer variants, violating Track B intent. The brief explicitly forbids Singer.
