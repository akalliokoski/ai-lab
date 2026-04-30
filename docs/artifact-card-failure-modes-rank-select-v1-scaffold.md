# artifact-card-failure-modes-rank-select-v1 scaffold

Two-stage rank-then-select scaffold for the artifact-card `primary_failure_modes` branch.

Why this branch exists
- `artifact-card-failure-modes-pairwise-v1` is still the strongest downstream baseline, but it only reached reconstructed top-2 set match `0.25` and ordered recovery stayed `0.0`
- `artifact-card-failure-modes-evidence-v1` improved row metrics but reconstructed top-2 set match stayed `0.0`
- `artifact-card-failure-modes-contrast-v1` and `contrast-v2` both collapsed to singleton `missing-required-detail` on the reconstructable held-out subset
- the next clean hypothesis is that the model needs direct supervision over relative label rank before the final 2-label selection step

Generated dataset
- `data/artifact-card-failure-modes-rank-select-v1/`

Builder
- `scripts/build_failure_mode_rank_select_dataset.py`

Evaluator
- `scripts/evaluate_failure_mode_rank_select_run.py`

Training entrypoint
- `modal/train_unsloth_artifact_card.py`

Scaffold shape
- source dataset: `artifact-card-failure-modes-v1`
- source examples before expansion: `26` train / `8` eval
- expanded rows: `208` train / `64` eval
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
- positive labels keep the same tiny canonical evidence keys used in the evidence-conditioned branch
- non-selected labels must use `support_rank = out` with `evidence_key = not-supported`

What changed relative to earlier branches
- compared with `artifact-card-failure-modes-evidence-v1`, this scaffold keeps one-label-at-a-time prompts but adds explicit first-vs-second rank supervision instead of a flat supported/not-supported target
- compared with `artifact-card-failure-modes-pairwise-v1`, this scaffold avoids the 28-pair expansion and keeps prompt mass near the shorter evidence-conditioned format
- compared with `artifact-card-failure-modes-top2-v1`, the final pair is no longer emitted in one shot; it is reconstructed from a full score map built across the 8 candidate rows

Stage-2 selection rule used by the evaluator
- `primary -> 2`
- `secondary -> 1`
- `out -> 0`
- for each source example, the evaluator picks the top 2 labels by score to form the final selected pair
- it reports both:
  - exact positive-set match from labels with score `> 0`
  - exact selected top-2 set match and exact ordered top-2 match from the stage-2 selector

Local verification steps
1. Regenerate the dataset
- command: `python3 scripts/build_failure_mode_rank_select_dataset.py`

2. Preview the dataset
- command: `python3 scripts/preview_dataset.py artifact-card-failure-modes-rank-select-v1`

3. Run a perfect-payload smoke test through the evaluator
- smoke artifact path: `tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v1-smoke-run_summary.json`
- command pattern:
```bash
python3 scripts/evaluate_failure_mode_rank_select_run.py tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v1-smoke-run_summary.json data/artifact-card-failure-modes-rank-select-v1/eval_metadata.json
```

Recommended first training run
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-rank-select-v1 --max-steps 20
```

How to judge the first run
- row-level exact match and `support_rank` accuracy matter, but they are not the main success condition
- first check stage-2 reconstruction from `scripts/evaluate_failure_mode_rank_select_run.py`
- the minimum bar is to beat the current best downstream baseline:
  - pairwise-v1 top-2 set match `0.25`
  - pairwise-v1 ordered top-2 match `0.0`
- also inspect whether the rank outputs still collapse to `missing-required-detail` as `primary`

Interpretation rule
- if this branch improves reconstruction, keep iterating on score calibration and selector logic
- if it still collapses, stop treating prompt-only redesign as the main lever and consider a learned selector or explicit calibration against the pairwise mixed baseline
