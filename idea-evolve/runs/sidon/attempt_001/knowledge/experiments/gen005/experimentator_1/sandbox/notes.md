# Experiment Notes

## Data Downloaded
- `golomb-all-00`: Metadata for Golomb rulers with 5-999 marks
- `rulers-all-00`: Actual ruler positions for 5-999 marks (direct from database)
- `modrules-pp-00`: Projective plane modular rulers for q < 1000
- `modrules-ap-00`: Affine plane modular rulers for q < 1000

## Key Findings

### 105-mark ruler (BEST for N=10000)
- Source: ap (affine plane), q=107, multiplier=433
- Span: 9884 (fits in [0, 10000])
- Verified as valid Sidon set: fitness=105, violations=0
- **MAXIMAL**: No elements can be added in [0, 10000] while maintaining Sidon property
- **ROBUST**: Remove-1 and remove-2 + greedy re-extend (4000 trials) never exceeds 105

### 104-mark ruler
- Source: pp (projective plane), q=103, multiplier=400
- Span: 9581
- Verified: fitness=104, violations=0
- Note: 103-mark and 104-mark share same prefix (104 adds element 9581)

### 106+ marks DO NOT FIT in [0, 10000]
Exhaustive search over all multipliers confirms:
- pp q=107: best 106-mark span = 10135 > 10000
- ap q=107: best 106-mark span = 10163 > 10000
- pp q=109: best 106-mark span = 10169 > 10000
- No algebraic construction (Singer/Bose-Chowla/Ruzsa) produces 106+ marks in [0, 10000]

### Implication
**105 is the algebraic ceiling for N=10000.** To reach 106+, one would need:
1. A non-algebraic construction (backtracking search, CP-SAT/ILP solver)
2. Or a fundamentally new mathematical approach
