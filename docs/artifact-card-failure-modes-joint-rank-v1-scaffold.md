# artifact-card-failure-modes-joint-rank-v1 scaffold

Date: 2026-05-01
Status: scaffolded and locally verified

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

How to judge the first run
- do not trust train loss by itself
- first run `scripts/evaluate_failure_mode_joint_rank_run.py` on the produced `run_summary.json`
- main success criterion is downstream reconstruction, not exact row match alone
- the branch should beat the current best downstream baseline from `artifact-card-failure-modes-pairwise-v1`:
  - reconstructed top-2 set match must exceed `0.25`
- a strong secondary win would be finally improving ordered recovery above the current `0.0` pairwise/rank-select ceiling
- if this branch still fails, the next redesign should likely move to an explicitly learned two-pass selector or a smaller learned tournament among shortlisted labels

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
