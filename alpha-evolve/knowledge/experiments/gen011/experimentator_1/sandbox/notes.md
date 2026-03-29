# Development Notes — topk_screened_cd

## Key design decisions

1. **Inline incremental update instead of importing helper.** The screening loop needs to compute partial updates (only at K positions) before deciding whether to do the full update. Importing `incremental_update` would require computing the full O(M) update for every trial, defeating the screening's purpose. Verified the inline formula is bit-identical to the helper.

2. **Both +delta and -delta per magnitude.** Simpler than gradient-directed approach. At 100 deltas × 2 signs = 200 trials per element. For N=30000, that's 6M trials per round — but with K=30 screening, most reject in O(K) time.

3. **argpartition instead of argsort for top-K.** O(M) vs O(M log M). At M=60000, this saves ~10ms per top-K recomputation.

4. **End-of-round FFT resync for round_log.** Even when resync_interval > 1, we do an FFT at end of each round to provide verified C in the round_log. This is the only way to report accurate per-round C values. Overhead: ~0.2s/round for N=30k.

## Bug fixed during development

- All-zero array: initially expected 0 improvements, but CD correctly adds small positive deltas to build up from zero. Updated test expectation.

## Performance estimates at N=30k

Based on gen 10 reports:
- Full O(M) incremental update: ~15μs per trial
- Top-K screening (K=30): ~0.5μs per trial
- FFT resync: ~0.2s
- Per-round estimate: 30000 elements × 200 trials × 0.5μs screening + ~1% pass rate × 15μs verify ≈ 3s + 0.2s FFT = ~3.2s/round
- Gen 10 measured 6-12s/round (with 200 deltas), so our 100-delta default should be ~3-6s/round
