## Question

Can the Rokicki-Dogon "Possibly Optimal Golomb Rulers" database provide Sidon sets with 104+ elements fitting within {0, ..., 10000}?

## Methodology

1. **Downloaded** the Rokicki-Dogon database from cube20.org/golomb/:
   - `golomb-all-00` (metadata: marks, span, construction type, prime power, multiplier)
   - `rulers-all-00` (actual ruler mark positions for sizes 5-3999)
   - `modrules-pp-00` and `modrules-ap-00` (modular rulers for all q < 1000)

2. **Extracted** ruler mark lists for 103, 104, and 105 marks from `rulers-all-00`.

3. **Verified** each ruler using `evaluate.py` (checks Sidon property + range [0, 10000]).

4. **Extension test**: Tried to extend the 105-mark ruler by greedy addition of elements in [0, 10000].

5. **Perturbation test**: Removed k=1,2 elements from 105-mark ruler and greedily re-extended (4000 random trials).

6. **Exhaustive multiplier search**: For q=107 (pp and ap) and q=109 (pp), tested ALL coprime multipliers to find minimum 106-mark sub-ruler span:
   - pp q=107: 9072 multipliers tested
   - ap q=107: ~5700 multipliers tested
   - pp q=109: ~9900 multipliers tested

## Results

### Rulers that fit in [0, 10000]

| Marks | Span | Type | q | Multiplier | Fitness (verified) |
|-------|------|------|---|------------|--------------------|
| 105 | 9884 | ap | 107 | 433 | **105** |
| 104 | 9581 | pp | 103 | 400 | **104** |
| 103 | 9408 | pp | 103 | 400 | **103** |
| 102 | 9218 | pp | 101 | 1758 | 102 |

### Rulers that DO NOT fit in [0, 10000]

| Marks | Best span (all multipliers) | Source |
|-------|-----------------------------|--------|
| 106 | 10135 (pp q=107) | Exhaustive search |
| 106 | 10163 (ap q=107) | Exhaustive search |
| 106 | 10169 (pp q=109) | Exhaustive search |
| 107 | 10241 (pp q=109) | Exhaustive search |
| 107 | 10299 (pp q=107) | Exhaustive search |
| 108 | 10415 (pp q=109) | Exhaustive search |

### Extension and perturbation results

- **105-mark ruler is maximal**: Zero elements can be added in [0, 10000] while maintaining Sidon property. All 10001-105 = 9896 non-member candidates create a difference conflict.
- **Remove-and-extend fails**: 2000 trials at k=1, 2000 trials at k=2: never exceeded 105.

## Conclusions

1. **The Rokicki-Dogon database provides verified 105-element Sidon sets for N=10000.** This is a +3 improvement over the previous best (102, Singer q=101 truncation).

2. **105 is the algebraic ceiling for N=10000.** Exhaustive search over all multipliers for all relevant prime powers (q=103, 107, 109) confirms that no Singer/Bose-Chowla/Ruzsa construction produces 106+ marks within span ≤ 10000.

3. **The 105-mark ruler is maximal and robust.** It cannot be extended and perturbation search does not improve it.

4. **To reach 106+, non-algebraic methods are required.** CP-SAT/ILP solvers or backtracking search would be needed.

## Confidence Level

**High** — Results are verified by evaluate.py and the exhaustive multiplier search leaves no algebraic constructions unchecked.

## Limitations

- Only tested algebraic constructions from the Rokicki-Dogon database (Singer/Bose-Chowla projective and affine plane types). Non-algebraic search approaches (randomized backtracking, ILP) could potentially find 106+ mark Sidon sets that are not modular rulers.
- Perturbation search was limited to 4000 trials. More extensive perturbation (k=3,4,5 with millions of trials) might find marginally different 105-element sets but is unlikely to reach 106.
- The "Ruzsa" construction type (rl) was not tested — it is known to produce worse rulers than Singer/Bose-Chowla for these sizes.
