# artifact-card-failure-modes-rank-select-v2 scaffold

Rank-calibration and schema-hardening patch for the artifact-card `primary_failure_modes` branch.

Why this branch exists
- `artifact-card-failure-modes-rank-select-v1` improved row validity and field accuracy, but downstream reconstruction still stayed at exact positive-set match `0.0`, top-2 set match `0.0`, and ordered top-2 match `0.0`
- the clearest repeated failure was calibration, especially `missing-required-detail` being pushed to `out` even when it should be primary or secondary
- the clearest repeated false positives were `generic-explanation`, `phrase-copy-or-template-collapse`, and `fluency-without-correctness`
- one invalid tuned row also copied an `allowed_evidence_keys` tail into the JSON, so the prompt contract itself needed to be simplified before another GPU run

Generated dataset
- `data/artifact-card-failure-modes-rank-select-v2/`

Builder
- `scripts/build_failure_mode_rank_select_v2_dataset.py`

Evaluator
- `scripts/evaluate_failure_mode_rank_select_run.py`

Training entrypoint
- `modal/train_unsloth_artifact_card.py`

What changed relative to rank-select-v1
- train-only supplemental source cases were added to sharpen:
  - `missing-required-detail` as primary with explicit missing or non-canonical field cues
  - `missing-required-detail` as secondary under `no-material-change` and `fluency-without-correctness`
  - true negatives for `missing-required-detail` on style-noise cases where all required fields stayed present
  - true positives for `phrase-copy-or-template-collapse` without accidentally introducing missing-field evidence
- the prompt now gives one compact candidate card instead of a long `allowed_evidence_keys` section
- each row names one exact `positive_evidence_key_if_selected` value, so the model only has to choose between that key and `not-supported`
- the prompt explicitly says there are exactly 2 positive labels overall and forbids extra keys or copied policy text
- `max_new_tokens` dropped from `48` to `40` to reduce schema spillover

Scaffold shape
- source dataset: `artifact-card-failure-modes-v1`
- source examples before expansion: `26` train / `8` eval
- supplemental train-only source cases: `8`
- expanded rows: `272` train / `64` eval
- one row per source example per candidate label across the full 8-label vocabulary

Output contract
- each row returns one strict JSON object with exactly these keys:
  - `candidate_label`
  - `support_rank`
  - `evidence_key`
- allowed `support_rank` values:
  - `primary`
  - `secondary`
  - `out`
- if `support_rank` is `primary` or `secondary`, `evidence_key` must be the named `positive_evidence_key_if_selected`
- if `support_rank` is `out`, `evidence_key` must be `not-supported`

Stage-2 selection rule used by the evaluator
- `primary -> 2`
- `secondary -> 1`
- `out -> 0`
- the evaluator reconstructs the final ordered top 2 by score, then reports:
  - exact positive-set match
  - exact selected top-2 set match
  - exact ordered top-2 match
  - first-label and second-label accuracy

Local verification steps completed
1. Syntax check
- command:
```bash
python3 -m py_compile scripts/build_failure_mode_rank_select_v2_dataset.py scripts/evaluate_failure_mode_rank_select_run.py scripts/preview_dataset.py modal/train_unsloth_artifact_card.py
```

2. Dataset generation
- command:
```bash
python3 scripts/build_failure_mode_rank_select_v2_dataset.py
```
- result: wrote dataset files under `data/artifact-card-failure-modes-rank-select-v2/`

3. Dataset preview
- command:
```bash
python3 scripts/preview_dataset.py artifact-card-failure-modes-rank-select-v2
```
- result: train/eval examples render correctly and outputs are valid strict JSON

4. Evaluator smoke test
- smoke artifact path: `tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v2-smoke-run_summary.json`
- command pattern:
```bash
python3 scripts/evaluate_failure_mode_rank_select_run.py tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v2-smoke-run_summary.json data/artifact-card-failure-modes-rank-select-v2/eval_metadata.json
```
- result:
  - tuned row exact match: `1.0`
  - tuned exact positive-set match: `1.0`
  - tuned top-2 set match: `1.0`
  - tuned ordered top-2 match: `1.0`

Recommended first training run
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-rank-select-v2 --max-steps 20
```

How to judge the first run
- row-level exact match and `support_rank` accuracy still matter, but they are not the main success condition
- first check stage-2 reconstruction from `scripts/evaluate_failure_mode_rank_select_run.py`
- the minimum bar is still to beat the current best downstream baseline:
  - pairwise-v1 top-2 set match `0.25`
  - pairwise-v1 ordered top-2 match `0.0`
- specifically inspect whether:
  - `missing-required-detail` recovers positive recall
  - `phrase-copy-or-template-collapse` and `fluency-without-correctness` stop overfiring on the wrong held-out rows
  - the invalid JSON rate falls to `0.0` with no copied schema tails

First run result (`20260501T052544Z`)
- artifact path: `/artifacts/artifact-card-failure-modes-rank-select-v2/20260501T052544Z/`
- local summary copy: `tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v2-20260501T052544Z/run_summary.json`
- tuned row metrics:
  - `valid_json_rate = 1.0`
  - `exact_row_match_rate = 0.359375`
  - `candidate_label` accuracy = `1.0`
  - `support_rank` accuracy = `0.359375`
  - `evidence_key` accuracy = `0.46875`
- tuned reconstruction metrics:
  - exact positive-set match = `0.0`
  - top-2 set match = `0.0`
  - ordered top-2 match = `0.0`
  - first-label accuracy = `0.25`
  - second-label accuracy = `0.125`
  - underselected rate = `0.875`
  - positive-count histogram = `{0: 6, 1: 1, 2: 1}`
- main interpretation:
  - the schema-hardening patch solved the copied-tail / invalid-JSON problem
  - but the selector regressed overall and became more underselective than rank-select-v1
  - `missing-required-detail` still failed to recover positive recall, so the intended calibration fix did not land
  - `phrase-copy-or-template-collapse` remained the main surviving false-positive label

Interpretation rule
- if this branch improves reconstruction, keep iterating on calibration and selector logic
- if it still fails completely, stop assuming prompt-only calibration is the main lever and consider a selector that scores all stage-1 outputs jointly instead of independently
