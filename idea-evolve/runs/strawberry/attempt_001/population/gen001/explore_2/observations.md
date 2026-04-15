# Observations — explore_2

## Approach
Attempted to explore `copy_paste=0.65` (higher than exp5's 0.5) to further oversample rare classes.

## Results

| Solution | copy_paste | Score | Valid | Notes |
|----------|------------|-------|-------|-------|
| sol01.py | 0.65 | 0 (invalid) | No | Broken pipe error during evaluation |

## What Happened
- sol01.py was written and submitted for evaluation
- Evaluation failed with `[Errno 32] Broken pipe` — is_valid=0
- The broken pipe suggests the training process crashed or was killed before completing
- Likely cause: the higher copy_paste value may have caused memory issues or the training process terminated unexpectedly

## Lessons
- copy_paste=0.65 (or higher) needs validation — the crash could be due to the parameter itself or a random failure
- Future exploration should test copy_paste=0.6 first (incremental step from 0.5) rather than jumping to 0.65

## Suggested Next Steps
1. Retry with `copy_paste=0.6` instead of 0.65
2. Try `copy_paste_mode="mixup"` as an alternative direction
3. Consider staged training: 10 epochs first to validate before committing to 20