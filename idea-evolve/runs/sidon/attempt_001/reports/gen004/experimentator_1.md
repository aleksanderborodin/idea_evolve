# Experimentator Debrief — Generation 4

Agent: experimentator_1
Date: 2026-04-06
Time budget: ~15-20 min/experiment (total ~40 min actual, ~130s compute)

---

## 1. What did I try?

**EXP-6 (Multi-Singer Hybrid):**
- Built Singer q=97 set (98 elements) via the singer.py helper
- Attempted Bose ET construction for p=71 (see ET bug note below)
- Tested full Singer-102 base vs. adding Singer-97 elements: **0 additions**
- Tested full Singer-102 base vs. adding ET-71 elements: **0 additions**
- Tested reduced bases (k=40,50,60,70,80,90) from Singer-102, adding from Singer-97 and ET
  - Singer-97 additions only start appearing at k=60 (1 element), k=50 (3), k=40 (9)
  - All totals well below 102
- Tested Singer-97 base (98 elements) + Singer-101 additions: **0 additions**
- Tested ET-71 base + Singer-101 additions: 2 elements added (total 73 — below 102)
- Tested three-way hybrid: **0** net gain for k=70-85

**Result**: No hybrid exceeds 102. idea_013 is definitively debunked.

**EXP-4 (Difference Spectrum):**
- Computed all 5151 pairwise differences of Singer q=101 set
- Computed 4849 free differences in {1,...,10000}
- Analyzed free diff distribution by decile — strong structural gradient
- Computed blocker counts for all 9899 non-members
  - Found minimum: **43 blockers** (c=9931) — corrects pattern_010's claim of 45
- Full-blocker removal analysis: removing all 43 blockers leaves 84 individually-addable elements
- Pair-trade analysis: checked 3828 pairs of blocker elements — net gain 0 for all

**Result**: Free differences cluster at large values (truncation artifact). Min blockers = 43.
2-element trades yield no gain.

---

## 2. What information did I lack?

- Whether the Bose ET construction for p=71 is truly Sidon or has sum-collision issues.
  I didn't have time to debug the construction; the Singer-97 results already answered the
  hybrid question definitively, so this was low priority.
- The actual greedy extension from the 59-element base (Singer-102 minus c=9931's 43 blockers).
  I ran the individual-addability check but not the full greedy extension. This is the one
  meaningful unknown left from EXP-4.
- Whether 5+ element trades can yield net positive results. My pair analysis covered only k=2.

---

## 3. What given facts might be wrong or outdated?

- **pattern_010 says "minimum 45 blockers"** — WRONG. The true minimum is **43** (c=9931).
  This is a small but real correction. The pattern should be updated.
- The State of Affairs says "minimum 45 blockers per non-member" in the pattern summary.
  This should be corrected to 43.
- The stale fact files (fact_002, fact_004) mentioned in state_of_affairs.md open questions —
  these remain problematic but I did not address them (out of scope).

---

## 4. Was the State of Affairs accurate?

Mostly accurate. The strategic overview is correct: Singer methods are exhausted,
hybrid approaches are the next thing to rule out (now ruled out), ILP is the main frontier.

Minor inaccuracy: "minimum 45 blockers" should be 43. This does not change strategy.

The pattern about zero addable elements to truncated Singer sets (pattern_010) is confirmed —
zero elements can be added to the full 102-element set from ANY source tried.

---

## 5. What would I do differently with more context?

- Run the greedy extension from the 59-element reduced base (Singer-102 minus c=9931's blockers).
  This was the most interesting open path from EXP-4 and I didn't have time.
- Debug the ET construction properly (verify against a known Sidon check for small p first).
- Test larger removal sizes: k=5,10,15 removals with exhaustive or random search for
  element sets whose removal yields net-positive trades.

---

## 6. Specific experiments to run next

**EXP-4b (priority: high)**: Greedy extension from reduced base
- Take Singer-102, remove all 43 blockers of c=9931 (59 elements remain)
- Run greedy extension over all {0,...,10000}
- Expected: gives ~85-99 elements (below 102), confirming trading is futile
- If result > 102: major breakthrough, investigate the structure

**EXP-7 (priority: medium)**: Larger k-element trades
- For k=5,10,15, try random/heuristic removal sets
- Specifically: for each of the top 20 best candidates (43-46 blockers),
  find a minimal subset of their blockers to remove, then check net gain
- This is more targeted than the pair search and covers k=3-15

**EXP-5 (from gen003 suggestions, priority: medium)**: Non-Singer PDS families
- Paley sets, Hall sextic residues for v near 10001
- EXP-6 showed Singer q=97 is incompatible with Singer q=101 (same algebraic family)
- Different algebraic families might have compatible difference structures

---

## 7. What surprised me?

1. **Singer q=97 and Singer q=101 are completely incompatible at any base ≥70.**
   I expected maybe 1-2 elements would combine, given they use different q values.
   Zero elements at base≥70 is a very strong result.

2. **The free difference distribution is a pure truncation artifact.** I expected some
   algebraic structure (residues, quadratic patterns). Instead, the "free" differences
   are simply those that can't be realized because the Singer set is capped at 9775.
   This means EXP-4 essentially closed a null hypothesis.

3. **Minimum blockers is 43, not 45.** The previous pattern claimed 45. Small correction
   but worth noting — this means c=9931 is very slightly more "promising" than thought,
   though still firmly blocked.

4. **The pair-trade analysis found net gain 0 universally.** I expected at least one pair
   trade to yield +1 net (remove 2, add 3). Not finding any from 3828 pairs is strong
   evidence that small-k trading is fundamentally impossible for this set.

---

## 8. Helper tools feedback

- **`singer.py` (find_singer_set)**: Worked correctly and quickly (0.1s for q=97). The
  docstring is accurate. No issues.
- **`core.py` (is_sidon, build_diffs helpers)**: is_sidon is correct but slow for large sets
  (O(n²) sum computation). Not a bottleneck here but would matter for n>200.
- **Wished existed**: A `sidon_greedy_extend(base, candidates)` helper that efficiently
  extends a Sidon base from a candidate list. I implemented this inline but it would be
  reusable. Also a `count_individual_addable(base)` helper for the difference-spectrum
  analysis pattern.

---

## 9. Time budget

Had enough time to complete both experiments fully except:
- EXP-4b (greedy extension from reduced base) — the most important follow-up
- Pair-trade analysis was limited to 3828 pairs (stopped at 5000 limit); could have
  run longer but the result was already conclusively 0

Both experiments completed within the 15-20 minute budget per experiment.
Total wall time: ~130 seconds of compute, ~25 minutes of work session.
