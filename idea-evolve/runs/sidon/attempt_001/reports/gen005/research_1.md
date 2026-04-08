# Research Agent Debrief — Gen 5, research_1

## 1. What Did I Try?

**Primary objective: Retrieve Rokicki-Dogon mark lists for 104/105-mark rulers.**

Used a subagent to access cube20.org/golomb and retrieve the rulers-all-00 database. **This succeeded.** The database is live and returns actual mark positions for all sizes 5–999. Both the 104-mark and 105-mark integer sequences were retrieved and verified.

**Solutions produced**:
- `sol01.py` — 105-mark Bose-Chowla (ap, q=107, multiplier=433): **fitness=105** ✓
- `sol02.py` — 104-mark Singer (pp, q=103, multiplier=400): **fitness=104** ✓

**Literature check**:
- arXiv:2310.20032 (Carter-Hunter-O'Bryant 2023): upper bound ≈ 109-114 for N=10000
- OEIS A003022, A143824: only cover small n, no F(10000) table available online

## 2. What Information Did I Lack?

- The exact O(1) constant in Carter-Hunter-O'Bryant for small n — the true upper bound for N=10000 is somewhere in 109-114, but we can't pin it down more precisely without reading the full paper.
- Whether OEIS or any other source has F(10000) as a computed value — this seems to not exist publicly.

## 3. What Given Facts Might Be Wrong or Outdated?

- **`problem/description.md`** still says "theoretical maximum ~100 elements" and "target: >= 109". The constructive lower bound is now **105** (confirmed). The theoretical upper bound is **~109-114**, not exactly 109.
- **CLAUDE.md brief** said "Published constructive lower bound: possibly 105 (Rokicki-Dogon, UNVERIFIED)" — this is now VERIFIED. The 105-mark set scores 105 with is_valid=1, violations=0.
- **State of Affairs open question 2** ("Does the Rokicki-Dogon database actually contain 104-105 mark sets?") — NOW RESOLVED. Yes, both exist and both fit in {0..10000}.

## 4. Was the State of Affairs Accurate?

Mostly accurate. The key missing update was that the constructive lower bound is 105 (not 102). The State of Affairs correctly identified Rokicki-Dogon as the top priority and correctly noted the ~109 upper bound. The new information to add:

1. **F(10000) constructive lower bound = 105** (Bose-Chowla ap, q=107, multiplier=433)
2. **106-mark ruler has span 10135 > 10000** — 105 is the algebraic ceiling for N=10000
3. **Singer multiplier=400 (not 1) explains why q=103 previously scored 102** — the helper doesn't search multiplier space
4. The remaining gap (105 to ~109-114) requires computational search, not algebraic construction

## 5. What Would I Do Differently?

With more time, I would implement a greedy extension check on the 105-mark set:
- Check if any element in {0..10000} \ S can be added to the 105-mark set without creating a repeated difference
- If any exists, that immediately gives fitness=106
- If none, the 105-set is locally maximal and further search must explore different 105-element configurations

## 6. Specific Experiments to Run

| Priority | Experiment | Expected Gain |
|----------|------------|---------------|
| **CRITICAL** | Greedy extend the 105-mark set: `greedy_extend(sol01_set, 10000)` | Possible 106 if any gap exists |
| **HIGH** | CP-SAT k=106 with 105-mark hint | Could prove/disprove feasibility |
| **HIGH** | Remove-k/extend from 105-mark seed (k=1..5, many trials) | Possible 106-107 |
| **MEDIUM** | Download and check 106-mark ruler (span=10135): try cyclic shift to get span<10000 | Small chance of 106 |
| **LOW** | Try Ruzsa construction (third type in Rokicki-Dogon database) for any new configurations | Unknown |

## 7. What Surprised Me?

- **The 104-mark Singer set does NOT use the raw Singer q=103 set.** It uses multiplier=400 applied to the Singer set. Previous pipeline attempts used multiplier=1 (or tried only a few multipliers) and got span ~10290 → only 102 elements fit. The correct multiplier=400 compresses the span to 9581, allowing all 104 elements to fit. This explains a 4-generation mystery.
- **Both 104 and 105 mark sets are immediately accessible** as hardcoded integer lists — no computation needed. The pipeline spent 4 generations on algorithmic approaches when the answer was in a downloadable database.
- **105 is the constructive ceiling** — the 106-mark ruler exceeds N=10000. This means the gap to theory (109-114) must be closed by search, not construction.

## 8. Helper Tools Feedback

- `helpers/singer.py`: The issue is that `find_singer_set()` doesn't search multiplier space adequately. Adding multiplier search (trying all multipliers 1..q²+q to minimize span) would allow it to reproduce the Rokicki-Dogon 104-mark result algebraically. This would be a valuable helper improvement.
- **Missing helper**: A `helpers/rokicki_dogon.py` that hardcodes (or fetches/parses) the mark lists for common sizes would make these constructions instantly available to all agents.
- **Missing helper**: A simple `greedy_extend(S, N)` function in `helpers/core.py` — many agents implement their own version; centralizing would reduce redundancy.

## 9. Time Budget

Sufficient for the primary objective. The session retrieved both mark lists, implemented and evaluated both solutions (105 and 104), and wrote complete findings.

**Highest-value next step**: Implement greedy extension of the 105-mark set to check for 106. This takes ~5 minutes of implementation and would immediately tell us whether 106 is accessible via simple local search.

---

## Solution Table

| File | Fitness | is_valid | Strategy |
|------|---------|----------|----------|
| sol01.py | **105** | 1 | Rokicki-Dogon 105-mark Bose-Chowla (ap, q=107, multiplier=433) — NEW BEST |
| sol02.py | 104 | 1 | Rokicki-Dogon 104-mark Singer (pp, q=103, multiplier=400) — explains q=103 mystery |
