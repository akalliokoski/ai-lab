# artifact-card-failure-modes-rank-select-v2

Rank-calibration patch for the artifact-card failure-mode branch.

Goal
- keep the task focused on `primary_failure_modes`
- keep one-label-at-a-time supervision, but reduce schema leakage and sharpen rank calibration
- make `missing-required-detail` easier to select when field-omission evidence is explicit
- reduce false positives on `fluency-without-correctness` and `phrase-copy-or-template-collapse`

Why this branch exists
- `artifact-card-failure-modes-rank-select-v1` improved row metrics but still failed the real downstream objective
- the strongest repeated errors were calibration errors, not label-copying errors
- the first rank-select run underselected to zero positives on 5 of 8 held-out source examples and overselected noisy style labels on others
- one tuned row also leaked prompt schema by copying an `allowed_evidence_keys` tail into the JSON, so the next patch should shorten and harden the output contract directly

What changed from v1
- training now adds 8 train-only source cases targeted at:
  - stronger `missing-required-detail` primary or secondary evidence
  - harder negative control against spurious `fluency-without-correctness`
  - harder negative control against spurious `phrase-copy-or-template-collapse`
- the row prompt now uses a much smaller candidate card instead of a long `allowed_evidence_keys` list
- each row names exactly one `positive_evidence_key_if_selected` value and forces `not-supported` for `out`
- the prompt explicitly says there are exactly 2 positive labels overall and bans extra keys or copied policy text
- `max_new_tokens` is reduced to `40` to discourage policy echoing and extra JSON tails

Current shape
- train examples: 272
- eval examples: 64
- source examples before expansion: 26 train / 8 eval
- supplemental train-only source examples: 8
- source format: JSONL with `instruction`, `input`, `output`
- target output: JSON string only
- helper metadata: `train_metadata.json`, `eval_metadata.json`
- mean train input length: about 1525.8 chars

Success criterion
- row-level exact match should stay interpretable by field, but it is not the main success condition
- stage-2 reconstructed top-2 set match should beat the current best downstream baseline from `artifact-card-failure-modes-pairwise-v1` (`0.25`)
- stage-2 reconstructed ordered-pair match should beat the current `0.0` pairwise result
- if this branch still fails, the next redesign should likely separate stage-1 scoring from stage-2 selection more explicitly instead of relying on prompt-only calibration
