# artifact-card-v1

First scaffold for the new success-oriented fine-tuning pivot.

Goal
- replace the broad repo-tutor task with a narrow structured-output task
- teach the model to read short experiment evidence and emit one strict JSON experiment card
- judge progress by JSON validity and field accuracy, not train loss alone

Task shape
- input: run metadata, short run summary, 2-3 evidence bullets, and one operator note
- output: one JSON object with exactly these keys:
  - `run_id`
  - `dataset_name`
  - `model_name`
  - `verdict`
  - `primary_failure_modes`
  - `key_evidence`
  - `next_action`

Why this is a better first project
- much narrower than repo tutoring
- output is short and machine-checkable
- examples can be authored from real Modal artifacts and iteration notes
- fits the repo's artifact-driven debugging workflow

Current shape
- train examples: 20
- eval examples: 8
- source format: JSONL with `instruction`, `input`, `output`
- target output: JSON string only

Label and phrase discipline
- keep `verdict` inside: `improved`, `same`, `regressed`, `inconclusive`
- keep `primary_failure_modes` inside a small canonical label set
- keep `key_evidence` short and canonical rather than free-form
- keep `next_action` chosen from a small practical action vocabulary

Suggested first run
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-v1 --max-steps 20
```

Preview locally
```bash
python3 scripts/preview_dataset.py artifact-card-v1
```

Score a saved run locally
```bash
python3 scripts/evaluate_artifact_card_run.py tmp/modal-artifacts/<run_id>/<run_id>/run_summary.json
```

Immediate next moves after the first run
1. inspect `auto_eval.base_metrics` vs `auto_eval.tuned_metrics` in the saved `run_summary.json`
2. look at rows where tuned JSON is invalid or the wrong field is missing
3. patch the dataset by field failure, not by train loss alone
