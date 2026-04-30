# artifact-card-failure-modes-evidence-v1 scaffold

Date: 2026-04-30

Purpose
- turn the fresh strategy memo into a runnable next branch for `primary_failure_modes`
- keep the shared Unsloth training path unchanged
- shorten prompts and bind each positive label to a tiny evidence code

Created files
- `data/artifact-card-failure-modes-evidence-v1/README.md`
- `data/artifact-card-failure-modes-evidence-v1/task_config.json`
- `data/artifact-card-failure-modes-evidence-v1/train.jsonl`
- `data/artifact-card-failure-modes-evidence-v1/eval.jsonl`
- `data/artifact-card-failure-modes-evidence-v1/train_metadata.json`
- `data/artifact-card-failure-modes-evidence-v1/eval_metadata.json`
- `scripts/build_failure_mode_evidence_dataset.py`
- `scripts/evaluate_failure_mode_evidence_run.py`

Design
- source dataset: `data/artifact-card-failure-modes-v1/`
- expansion: one source row becomes 8 candidate-label judgments
- output schema:
  - `candidate_label`
  - `supported`
  - `evidence_key`
- negative rows always use `supported = "no"` and `evidence_key = "not-supported"`
- positive rows use short canonical evidence keys such as:
  - `missing-or-noncanonical-field`
  - `broader-than-reference`
  - `overlap-untrustworthy`
  - `phrase-copy-distortion`
  - `invented-detail`
  - `missed-core-cause`
  - `fluency-gain-without-correctness`
  - `repeated-no-change`
  - `mixed-fields-no-clear-task-win`

Why this branch is cleaner than pairwise-v1
- mean train prompt length dropped from about `3086.8` chars in `artifact-card-failure-modes-pairwise-v1` to about `1085.0` chars here
- the full repeated 8-label rubric is removed from each row
- each row contains only one candidate label, one short contrast note, and the observed evidence bullets
- the target is more diagnostic than bare binary `belongs`, because wrong evidence binding is visible separately from wrong support judgment

Evaluation logic
- row-level exact JSON/field scoring still works through the shared training entrypoint
- `scripts/evaluate_failure_mode_evidence_run.py` adds branch-specific checks:
  - row exact match
  - per-label support precision/recall/F1
  - positive-only evidence-key accuracy
  - reconstructed positive-label set match on the original held-out examples
  - overprediction / underprediction rate for the number of positive labels

Quick validation already done
- dataset builder ran successfully and produced `208` train rows and `64` eval rows
- branch-specific evaluator was smoke-tested on a mock perfect-summary payload and returned perfect row + reconstruction metrics

Recommended next command
- `modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-evidence-v1 --max-steps 20`

Interpretation target for the first run
- if reconstructed positive-label set match beats the current pairwise downstream result (`0.25`), keep iterating this branch
- if `missing-required-detail` still over-dominates, shrink next to the four hardest contrast packs instead of broad full-label expansion again
