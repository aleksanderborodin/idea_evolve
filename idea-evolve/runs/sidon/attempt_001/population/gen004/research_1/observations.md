# Research Agent Observations — Gen 4

## Solutions Produced

### sol01.py — Singer q=103 truncation
- **Score**: 102 (fitness=102, is_valid=1, violations=0)
- **Strategy**: Build Singer difference set for q=103 (104 elements in Z_{10713}), find cyclic shift with all elements ≤ 10000
- **Result**: The minimum span of Singer q=103 is 10290 (not 9581 as believed from Rokicki-Dogon). No rotation fits all 104 elements within {0,...,10000}. Best truncation = 102 elements (same as current best Singer q=101).

## Key Research Findings

### CRITICAL DISCOVERY: 103–105 elements are achievable in {0,...,10000}
The Rokicki-Dogon "Possibly Optimal Golomb Rulers" database (cube20.org/golomb) contains near-optimal ruler data showing:
- 103 marks: span 9408 ≤ 10000 ✓
- 104 marks: span 9581 ≤ 10000 ✓
- 105 marks: span 9884 ≤ 10000 ✓
- 106 marks: span 10135 > 10000 ✗

**The published best for N=10000 is 105 elements.**

### Critical Misunderstanding
The Rokicki-Dogon entries are from near-optimal SEARCH results, not pure Singer constructions. The "type=pp, q=103" metadata indicates the seed used (Singer for q=103), but the final 104-mark ruler with span 9581 was found through additional search. The actual mark lists are needed to reproduce these results.

The Singer q=103 construction alone gives span 10290 > 10000, so it cannot trivially be used.

### What Is Needed to Achieve 104+ Elements
1. **Get the actual mark list** from the Rokicki-Dogon database (zip file at cube20.org/golomb-all-00.zip). The file contains the actual rulers, not just parameters.
2. **Alternatively**: Run exhaustive/stochastic search on the Singer q=103 set to find modifications (remove 1-3 elements, add others) that reduce the span below 10000 while keeping 104 elements.
3. **For 105 elements**: Reconstruct the affine plane (Bose-Chowla) construction for q=107 and find the right rotation/truncation.

## What Worked / Didn't Work
- Singer q=103 direct application: ❌ span too large (10290 > 10000)
- Literature search: ✅ Found that 105 elements IS achievable (Rokicki-Dogon database)
- Upper bound clarification: ✅ Confirmed 109 is hard upper bound (Carter-Hunter-O'Bryant 2023)

## Score Summary
| File | Fitness | Notes |
|------|---------|-------|
| sol01.py | 102 | Singer q=103 truncated — no improvement over best |
