# artifact-card-failure-modes-joint-rank-v1 scaffold

Date: 2026-05-01
Status: first run completed and reviewed

Goal
- keep the task focused on `primary_failure_modes`
- score all 8 labels together in one output instead of asking the model to judge one label at a time
- force a globally normalized decision: exactly one `primary`, exactly one `secondary`, all other labels `out`
- test whether joint scoring fixes the underselection and dominant-label failures that survived the independent rank-select family

Why this branch exists
- `artifact-card-failure-modes-rank-select-v1` improved row metrics but reconstruction still stayed at `0.0`
- `artifact-card-failure-modes-rank-select-v2` fixed schema leakage, but reconstruction still stayed at `0.0` and underselection got worse
- the next clean test is not more per-label prompt tuning; it is to change the supervision shape so all labels compete in one shared decision object

What changed relative to rank-select-v2
- source rows still come from `artifact-card-failure-modes-v1`
- the 8 train-only supplemental source cases from `artifact-card-failure-modes-rank-select-v2` are reused
- each source example now becomes one row instead of 8 candidate-label rows
- output is one strict JSON object with the 8 label names as fixed keys
- each key value must be exactly one of `primary`, `secondary`, or `out`
- the prompt includes compact label cards plus explicit global constraints:
  - exactly one primary
  - exactly one secondary
  - all others out
  - `missing-required-detail` must stay out when all required fields stayed present
  - `phrase-copy-or-template-collapse` only becomes positive when copied or distorted wording is explicit
  - `overlap-contaminated-eval` only becomes positive when overlap is explicit

Current scaffold shape
- source examples before supplements: `26` train / `8` eval
- train-only supplemental source cases: `8`
- final rows: `34` train / `8` eval
- mean train input length: about `2655.2` chars
- generated files:
  - `data/artifact-card-failure-modes-joint-rank-v1/train.jsonl`
  - `data/artifact-card-failure-modes-joint-rank-v1/eval.jsonl`
  - `data/artifact-card-failure-modes-joint-rank-v1/train_metadata.json`
  - `data/artifact-card-failure-modes-joint-rank-v1/eval_metadata.json`
  - `data/artifact-card-failure-modes-joint-rank-v1/task_config.json`

Output contract
```json
{
  "no-material-change": "primary|secondary|out",
  "missing-required-detail": "primary|secondary|out",
  "generic-explanation": "primary|secondary|out",
  "overlap-contaminated-eval": "primary|secondary|out",
  "phrase-copy-or-template-collapse": "primary|secondary|out",
  "hallucinated-detail": "primary|secondary|out",
  "wrong-causal-point": "primary|secondary|out",
  "fluency-without-correctness": "primary|secondary|out"
}
```

Result from the first run (`20260501T064308Z`)
- the run completed successfully and saved artifacts under `/artifacts/artifact-card-failure-modes-joint-rank-v1/20260501T064308Z/`
- local copy pulled to `tmp/modal-artifacts/artifact-card-failure-modes-joint-rank-v1-20260501T064308Z/run_summary.json`
- raw `run_summary.json` auto-eval looked superficially better than earlier branches because it only checked JSON parseability plus per-field equality and reported tuned `valid_json_rate = 1.0`
- branch-specific evaluation showed the real outcome was still a clean failure once the global joint constraints were enforced
- tuned joint-rank evaluator metrics:
  - `valid_json_rate`: `0.0`
  - `exact_row_match_rate`: `0.0`
  - `exact_positive_set_match_rate`: `0.0`
  - `top2_set_match_rate`: `0.0`
  - `top2_ordered_match_rate`: `0.0`
  - `underselected_rate`: `1.0`
  - selected-positive histogram: `{0: 7, 1: 1}`
- the dominant failure pattern was even harsher underselection than `rank-select-v2`: 7/8 eval rows predicted all labels as `out`, and the remaining row emitted only `generic-explanation = secondary` with no `primary`
- all 8 tuned eval rows violated the branch contract `exactly one primary + exactly one secondary`, so the apparent raw-JSON success did not translate into a valid joint selector
- label behavior stayed narrow and brittle:
  - `generic-explanation` got the lone surviving positive and reached `positive_precision = 1.0`, `positive_recall = 1.0`
  - every other label had `positive_recall = 0.0`, including `missing-required-detail`

Decision after the first run
- keep `artifact-card-failure-modes-pairwise-v1` as the strongest downstream baseline
- record `joint-rank-v1` as another clean negative result, not progress toward the selector objective
- treat the key lesson as structural: making labels compete in one object was not enough when the model could still satisfy the loss by predicting near-all-`out`
- the next redesign should make the final two-slot choice explicit in the target itself, likely with either:
  - a direct `{primary_label, secondary_label}` output object with no per-label `out` state, or
  - a staged/tournament selector that only compares a small shortlist at once and cannot collapse to zero positives

Local verification completed
- `python3 -m py_compile scripts/build_failure_mode_joint_rank_v1_dataset.py scripts/evaluate_failure_mode_joint_rank_run.py scripts/preview_dataset.py modal/train_unsloth_artifact_card.py`
- `python3 scripts/build_failure_mode_joint_rank_v1_dataset.py`
- `python3 scripts/preview_dataset.py artifact-card-failure-modes-joint-rank-v1`
- synthetic perfect-payload smoke test written to `tmp/modal-artifacts/artifact-card-failure-modes-joint-rank-v1-smoke-run_summary.json`
- `python3 scripts/evaluate_failure_mode_joint_rank_run.py tmp/modal-artifacts/artifact-card-failure-modes-joint-rank-v1-smoke-run_summary.json data/artifact-card-failure-modes-joint-rank-v1/eval_metadata.json`
- smoke result: all row, rank, and reconstruction metrics returned `1.0`

Recommended first run
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-joint-rank-v1 --max-steps 20
```
