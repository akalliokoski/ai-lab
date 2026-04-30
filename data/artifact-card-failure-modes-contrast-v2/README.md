# artifact-card-failure-modes-contrast-v2

Targeted patch to the contrast-group artifact-card failure-mode branch.

Goal
- keep the contrast-group supervision from `contrast-v1`
- preserve the narrow 4-group decomposition around `missing-required-detail`
- patch the exact weak states that contrast-v1 failed to reconstruct
- stay local and cheap before escalating to a two-stage selector

Why this branch exists
- `artifact-card-failure-modes-contrast-v1` improved row structure but collapsed every reconstructable held-out source case to singleton `missing-required-detail`
- the missed states were concentrated, not random: rival-only `generic-explanation`, rival-only `no-material-change`, rival-only `overlap-contaminated-eval`, plus `both` states in the `generic-explanation`, `no-material-change`, and `hallucinated-detail` groups
- this branch adds only those targeted source cases first, so we can test whether the failure was data sparsity at the hardest boundaries instead of an architectural limit

What changed from contrast-v1
- eval split is unchanged, so downstream comparison remains clean
- the original 26 source train cases from `artifact-card-failure-modes-v1` stay intact
- added 6 supplemental train-only source cases targeted at the exact missing rival-only and `both` states
- the contrast prompt/output format stays the same: `contrast_group`, `decision`, `evidence_key`
- reconstruction is still scored only on source examples whose gold pair stays inside the 5-label contrast universe

Targeted additions
- rival-only `generic-explanation`
- rival-only `no-material-change`
- rival-only `overlap-contaminated-eval`
- `both` for `missing-required-detail` vs `generic-explanation`
- `both` for `missing-required-detail` vs `no-material-change`
- `both` for `missing-required-detail` vs `hallucinated-detail`

Current shape
- train examples: 128
- eval examples: 32
- source examples before contrast expansion: 32 train / 8 eval
- supplemental train-only source cases: 6
- contrast rows per source example: 4
- reconstructable source examples inside the contrast universe: 13 train / 4 eval
- source format: JSONL with `instruction`, `input`, and `output`
- target output: JSON string only
- helper metadata: `train_metadata.json`, `eval_metadata.json`

Success criterion
- beat `contrast-v1` on reconstructed exact positive-set and top-2 set match without losing JSON stability
- specifically recover some of the missing rival-only and `both` states instead of collapsing every held-out in-universe case to the anchor label
- if this still fails, the next move should be a two-stage rank-then-select design rather than another small prompt/data patch
