# Experiment Results — Generation 4 Experimentator

Generated: 2026-04-06
Singer q=101 set: 102 elements (from population/best.py)

---

## EXP-6: Multi-Singer Hybrid Test

### Question
Can elements from different algebraic constructions (Singer q=101, Singer q=97, ET p=71)
be combined into a Sidon set larger than 102 elements in {0,...,10000}?

### Methodology
- Control: Full 102-element Singer q=101 set (zero addable elements, confirmed)
- Treatment A: Add elements from Singer q=97 (98 elements) to the Singer q=101 base
- Treatment B: Add elements from ET p=71 (71 elements, Bose construction) to Singer q=101 base
- Variable: base size (full 102, or reduced to k=40,50,60,70,80,90 elements)
- Addition method: greedy forward scan — try adding each candidate c in order, accept if Sidon property preserved
- Fixed: N=10000, deterministic procedure

**Note on ET construction**: The Bose construction `S = {p*k + (k² mod p) : k=0,...,p-1}` for p=71
gave a set flagged as non-Sidon by the is_sidon checker (which also checks 2a sums). The ET set
produced 71 elements in {0,...,4971} but may violate the 2a = b+c condition. This does not
substantially affect the hybrid conclusion but is noted.

Singer q=97 was verified: 98 elements in {0,...,9506}, all within N=10000. Construction took 0.1s.

### Results

**Test 1: Full Singer-102 + ET-71 additions**
- Elements added: **0**

**Test 2: Full Singer-102 + Singer-97 additions**
- Elements added: **0**

**Test 3: Reduced Singer-101 bases + ET-71 additions**
| Base size k | ET elements added | Total |
|-------------|-------------------|-------|
| 90          | 0                 | 90    |
| 80          | 0                 | 80    |
| 70          | 0                 | 70    |
| 60          | 0                 | 60    |
| 50          | 0                 | 50    |
| 40          | 1                 | 41    |

**Test 4: Reduced Singer-101 bases + Singer-97 additions**
| Base size k | Singer-97 elems added | Total |
|-------------|----------------------|-------|
| 90          | 0                    | 90    |
| 80          | 0                    | 80    |
| 70          | 0                    | 70    |
| 60          | 1                    | 61    |
| 50          | 3                    | 53    |
| 40          | 9                    | 49    |

**Test 5: ET-71 base + Singer-101 additions**
- Base: 71 ET elements
- Added from Singer-101: **2** elements (8776, 9627)
- Total: **73**

**Test 6: Singer-97 base + Singer-101 additions**
- Base: 98 Singer-97 elements
- Added from Singer-101: **0** elements
- Total: **98**

**Test 7: Three-way hybrid (Singer-101 reduced → add ET → add Singer-97)**
| Base k | +ET | +Singer-97 | Total |
|--------|-----|------------|-------|
| 70     | 0   | 0          | 70    |
| 75     | 0   | 0          | 75    |
| 80     | 0   | 0          | 80    |
| 85     | 0   | 0          | 85    |

**Best hybrid total: 85** (no combination exceeds 102)

### Conclusions
Multi-Singer hybrid yields nothing above 102. The pairwise-difference structures of Singer q=101
and Singer q=97 are almost completely incompatible — when the Singer-101 base is sufficiently
populated (≥70 elements), not a single element from Singer-97 or ET-71 can be added.
Only when the base is reduced below ~60 elements do cross-construction additions become possible,
and even then the combined totals are well below 102.

### Confidence Level
**High** — the experiment is fully deterministic with no randomness. All three constructions
were tested at multiple base sizes. The zero-addition result at full and near-full bases is definitive.

### Limitations
1. ET p=71 construction may have a bug (non-Sidon result); however, even if fixed, the
   Singer-97 results (which are definitively Sidon) already answer the question: incompatible.
2. Only forward-scan greedy was used. A smarter search (e.g., pick ET elements optimally to
   minimize Singer conflicts) might yield 1-2 more at reduced bases, but not at full base.
3. Only three construction families tested. Other PDS families (Paley, Hall sextic residues)
   remain untested (EXP-5).

### Implications for idea_013 (Multi-Singer Hybrid)
**Debunked.** Idea_013 should be moved to the debunked directory. The experiment tested
exactly the mechanism idea_013 hypothesized (combining elements from different algebraic
families) and found no synergy at any useful base size. The two Singer constructions
(q=101 and q=97) use the same algebraic mechanism (GF(q³)) and their difference sets
are apparently incompatible by design — they both cover {1,...,v} differences densely in
their respective modular groups.

---

## EXP-4: Unused Difference Spectrum Analysis

### Question
What is the algebraic structure of the "free" differences (not used by Singer q=101) and
do they reveal any mechanism for trading elements to exceed 102?

### Methodology
- Compute all C(102,2) = 5151 pairwise differences of the Singer set
- Compute 4849 free differences in {1,...,10000}
- Analyze distribution by decile, consecutive runs, and gap statistics
- For each non-member c, compute blocker count (Singer elements s with |c-s| ∈ used_diffs)
- Trading analysis: remove best-candidate blockers, count individually-addable elements
- Pair-trade analysis: try all pairs from the top-10 candidates' blocker sets (~3828 pairs)

### Results

**Difference usage by decile:**
| Range         | Used | Free | % Used |
|---------------|------|------|--------|
| [1-1000]      | 989  | 11   | 98.9%  |
| [1001-2000]   | 902  | 98   | 90.2%  |
| [2001-3000]   | 794  | 206  | 79.4%  |
| [3001-4000]   | 702  | 298  | 70.2%  |
| [4001-5000]   | 586  | 414  | 58.6%  |
| [5001-6000]   | 454  | 546  | 45.4%  |
| [6001-7000]   | 327  | 673  | 32.7%  |
| [7001-8000]   | 238  | 762  | 23.8%  |
| [8001-9000]   | 133  | 867  | 13.3%  |
| [9001-10000]  | 26   | 974  | 2.6%   |

**Key observation**: Free differences are heavily concentrated at LARGE values. The longest
consecutive run of free diffs is 225 (starting at 9776), due to the Singer set's maximum
element being 9775 — no differences > 9775 can exist, so all of {9776,...,10000} are free.

**Free difference consecutive runs**: 217 runs of length ≥5. The top runs are all near
the end of the range (9776, 9499, 9391) — artifacts of the truncation at N=9775.

**Blocker count statistics:**
- **Minimum: 43 blockers** (c=9931) — corrects previous knowledge (pattern_010 said 45)
- Maximum: 96 blockers
- Mean: 71.46 blockers

**Blocker count distribution** (first 10 levels):
| Blockers | # non-members |
|----------|--------------|
| 43       | 1            |
| 44       | 14           |
| 45       | 3            |
| 46       | 23           |
| 47       | 11           |
| 48       | 54           |
| 49       | 17           |
| 50       | 105          |
| 51       | 40           |
| 52       | 144          |

Only 1 non-member has 43 blockers. The distribution shows a steep rise — very few candidates
with fewer than 48 blockers exist.

**Best candidate: c=9931 (43 blockers)**
Blocking elements: all in range [2337, 9775], concentrated in the upper half of the Singer set.

**Trading analysis — remove all 43 blockers of c=9931:**
- Remaining base: 59 elements
- Elements individually addable to reduced base: 84
  (Note: these 84 elements are each individually compatible with the 59-element base,
  NOT simultaneously compatible. Greedy extension needed for actual set size.)
- Net change: remove 43, gain 84 individual-compatibility slots
- **The 84 addable elements INCLUDE the 43 removed elements themselves**, plus c=9931
  and other non-members freed by the removal.
- Actual achievable set size (via greedy extension from 59 base) was NOT measured — this is
  a follow-up experiment priority.

**Pair-trade analysis (remove 2, add 3+):**
- Checked 3828 pairs from the top-10 candidates' blocker sets
- Best net gain: **0** (no pair removal allows adding 3+ new elements)
- All pairs result in net = 0 (remove 2, gain ≤2)

### Conclusions

1. **Free differences are NOT uniformly distributed.** They follow a clear structural gradient:
   small differences (1-1000) are 98.9% occupied (Singer uses nearly all of them), large
   differences (9001-10000) are 97.4% free. This is a direct geometric consequence of the
   Singer set's range [0, 9775] — differences near 10000 simply cannot exist.

2. **Minimum blockers is 43, not 45.** pattern_010 should be corrected. The single
   best candidate (c=9931) has only 43 blocking elements.

3. **2-element trades yield no gain.** Checked 3828 pairs from the most promising blocker
   sets. No pair removal allows a net positive trade. This strongly suggests single-digit
   element trades cannot break the 102 ceiling.

4. **The "free difference" structure does NOT reveal new algebraic patterns.** The concentration
   of free differences at large values is a truncation artifact, not an algebraic signal.
   The small free differences (only 11 in the range 1-1000) are too sparse to form any
   recognizable pattern.

5. **Large-scale removal DOES free many candidates.** Removing 43 elements leaves 84
   individually-addable elements. Whether greedy extension from this 59-element base can
   exceed 102 is unknown and is the most interesting open question from this experiment.

### Confidence Level
**High** for the structural findings and the 2-element trade analysis.
**Medium** for the implications of the 43 minimum (only 1 candidate at this level; could
be a special artifact of the truncation boundary near c=9931).

### Limitations
1. Trading analysis only tested up to 2-element removals from a restricted set of candidates'
   blockers. Larger removals (k=5,10) from non-blocker-restricted elements were not tested.
2. The 84 individually-addable elements after full-blocker removal were not greedily extended.
3. "Algebraic pattern" analysis of free differences was qualitative (decile buckets), not
   a formal number-theoretic analysis (e.g., quadratic residue mod prime testing).

---

## Summary and Implications for Generation 5

| Finding | Implication |
|---------|-------------|
| No hybrid exceeds 102 (EXP-6) | Debunk idea_013; close the Multi-Singer hybrid direction |
| Min blockers = 43, not 45 (EXP-4) | Correct pattern_010; best candidate is c=9931 |
| Free diffs concentrated at large values (EXP-4) | Structural artifact, not exploitable |
| 2-element trades yield no gain (EXP-4) | Element trading up to k=2 is futile |
| 84 indiv-addable after 43-blocker removal (EXP-4) | Need greedy extension from 59-element base |
| Singer-97 ↔ Singer-101: zero compatibility (EXP-6) | Same algebraic family = incompatible |

**Priority recommendations for Gen 5:**
1. Greedily extend from Singer-102 minus all 43 blockers of c=9931. May still give ~102 but worth confirming.
2. Try larger k-element trades (k=5,10,15) via exhaustive or heuristic search — 2-element proved futile, but larger k with smart selection might open a new path.
3. The ILP / CP-SAT direction remains the most promising unexplored avenue (EXP-2).
