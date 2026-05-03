# artifact-card-failure-modes-forced-top2-v2p2

Forced-top-2 semantic patch branch for the artifact-card failure-mode project.

Goal
- keep `artifact-card-failure-modes-forced-top2-v2` as the semantic anchor
- add a small train-only semantic patch instead of more contract wording
- target the specific surviving confusion boundaries from the latest branch-aware evals

Why this branch exists
- `forced-top2-v2` is still the strongest current semantic baseline under branch-aware scoring
- `forced-top2-v2p1` and `forced-top2-v3` both regressed toward the same fallback pair `missing-required-detail + generic-explanation`
- the remaining failures are concentrated in four places: `fluency-without-correctness`, `hallucinated-detail`, `wrong-causal-point`, and overlap label-slot confusion

What changed from `forced-top2-v2`
- inherited every original `forced-top2-v2` train/eval row unchanged
- added 4 new train-only rows with the same four-field target and the same task config
- the new rows sharpen exactly these boundaries:
  - `fluency-without-correctness -> missing-required-detail`
  - `hallucinated-detail -> missing-required-detail`
  - `wrong-causal-point -> no-material-change`
  - `overlap-contaminated-eval -> phrase-copy-or-template-collapse`
- no anti-fence wording or generation-prefix changes were added here; this is a semantic patch only

Current shape
- train examples: 38
- eval examples: 8
- inherited train / eval examples from `forced-top2-v2`: 34 / 8
- new train-only supplemental examples: 4
- mean train input length: 4404.1 chars

Success criterion
- beat the current `forced-top2-v2` fallback concentration without losing its stronger top-2 recovery
- keep branch-aware evaluation as the decision surface, especially `top2_set_match_rate`, `top2_ordered_match_rate`, `invalid_row_rate`, and the new selector-collapse metrics
- if this branch does not beat `forced-top2-v2`, keep the anchor and preserve this patch as a negative result instead of stacking more prompt mass
