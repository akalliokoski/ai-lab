# artifact-card-failure-modes-evidence-v1

Evidence-conditioned per-label scaffold for the artifact-card project.

Goal
- keep the task focused on `primary_failure_modes`
- replace broad pairwise comparisons with one candidate label at a time
- bind each positive label to a tiny canonical evidence key instead of a bare belongs/not-belongs target
- keep prompts shorter than the pairwise branch so more tokens are actual evidence

Why this branch exists
- `artifact-card-failure-modes-pairwise-v1` improved reconstructed held-out top-2 set match to `0.25`, but still failed ordered recovery and over-promoted `missing-required-detail`
- the next strategy memo recommended evidence-conditioned per-label scoring with shorter prompts, confusion-targeted contrast data, and explicit evidence anchoring
- this scaffold turns that recommendation into runnable repo artifacts without changing the shared Unsloth training entrypoint

What changed from earlier branches
- source rows come from `artifact-card-failure-modes-v1` so the base evidence and gold top-2 labels stay aligned with the current failure-mode task
- each original row is expanded into 8 candidate-label judgments, one per allowed failure mode
- output is now one strict JSON object with exactly three keys: `candidate_label`, `supported`, `evidence_key`
- positive rows carry a tiny canonical evidence key; negative rows use `not-supported`
- prompts keep only the local candidate meaning, a short contrast note, and the observed evidence bullets

Current shape
- train examples: 208
- eval examples: 64
- source examples: 26 train / 8 eval before expansion
- source format: JSONL with `instruction`, `input`, `output`
- target output: JSON string only
- helper metadata: `train_metadata.json`, `eval_metadata.json`

Success criterion
- row-level exact match should beat the earlier binary branch while staying interpretable by field
- per-label support precision/recall should make `missing-required-detail` over-selection easier to detect
- reconstructed positive-label set match across the original held-out cases should beat the current pairwise downstream result (`0.25`)
- if the scaffold still over-predicts `missing-required-detail`, the next patch should narrow to the four hardest contrast groups instead of expanding the full label space again
