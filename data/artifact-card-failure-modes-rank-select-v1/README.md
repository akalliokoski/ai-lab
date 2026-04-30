# artifact-card-failure-modes-rank-select-v1

Two-stage rank-then-select scaffold for the artifact-card failure-mode branch.

Goal
- keep the task focused on `primary_failure_modes`
- score one candidate label at a time with an explicit rank target
- preserve a deterministic stage-2 selector that picks the final top 2 labels from the stage-1 scores
- test whether explicit `primary` vs `secondary` supervision beats the current pairwise downstream baseline

Why this branch exists
- `artifact-card-failure-modes-pairwise-v1` is still the strongest downstream branch, but it only reached reconstructed top-2 set match `0.25` and ordered recovery stayed `0.0`
- `artifact-card-failure-modes-evidence-v1` improved local row metrics but reconstructed top-2 match stayed `0.0`
- `artifact-card-failure-modes-contrast-v1` and `contrast-v2` both collapsed to singleton `missing-required-detail` on the reconstructable held-out subset
- the next disciplined branch is to supervise the ranking stage directly, then judge the experiment by the final selected top 2 rather than row metrics alone

What changed from earlier branches
- source rows come from `artifact-card-failure-modes-v1` so the evidence and label vocabulary stay aligned with the decomposed task
- each original row is expanded into 8 candidate-label scoring rows, one per allowed failure mode
- output is now one strict JSON object with exactly three keys: `candidate_label`, `support_rank`, `evidence_key`
- `support_rank` uses an explicit 3-level target: `primary`, `secondary`, or `out`
- `scripts/evaluate_failure_mode_rank_select_run.py` performs stage-2 deterministic selection from the predicted stage-1 scores and reports both ordered and unordered reconstruction metrics

Current shape
- train examples: 208
- eval examples: 64
- source examples: 26 train / 8 eval before expansion
- source format: JSONL with `instruction`, `input`, `output`
- target output: JSON string only
- helper metadata: `train_metadata.json`, `eval_metadata.json`
- mean train input length: about 1289.0 chars

Success criterion
- row-level exact match should stay interpretable by field, but it is not the main success condition
- stage-2 reconstructed top-2 set match should beat the current best downstream baseline from `artifact-card-failure-modes-pairwise-v1` (`0.25`)
- stage-2 reconstructed ordered-pair match should beat the current `0.0` pairwise result
- if this branch still collapses to `missing-required-detail`, the next redesign should likely combine score supervision with targeted calibration or a separate learned selector instead of more prompt-only rewrites
