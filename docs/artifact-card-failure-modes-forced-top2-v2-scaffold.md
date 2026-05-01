# artifact-card-failure-modes-forced-top2-v2

Status
- scaffolded and locally verified on 2026-05-01
- first real Modal run not launched yet

Goal
- keep the task focused on `primary_failure_modes`
- remove the all-`out` escape hatch that broke `joint-rank-v1`
- force a direct ranked top-2 decision with explicit evidence binding for each slot
- test whether no-abstention direct choice beats the current downstream baseline from `pairwise-v1`

Why this branch exists
- `artifact-card-failure-modes-top2-v1` forced the final pair directly, but it did not require evidence-bound slots and still collapsed onto repeated defaults
- `artifact-card-failure-modes-pairwise-v1` remains the strongest downstream baseline at top-2 set match `0.25`, but ordered recovery stayed `0.0`
- `artifact-card-failure-modes-joint-rank-v1` failed because the model could still satisfy most of the output object with `out` values and avoid real slot allocation
- the clean next test is to predict only the final ranked pair and require each chosen slot to bind to a closed evidence key

What changed relative to joint-rank-v1
- keeps the same 8-label vocabulary and the same held-out source examples
- keeps the same 8 train-only supplemental source cases introduced for rank-select-v2
- changes supervision from an 8-label state map to one strict four-field object per source example
- removes abstention states entirely: there is no `out`, `none`, or `abstain`
- requires explicit evidence grounding for both ranked slots

Strict JSON target
```json
{
  "primary_label": "<allowed_label>",
  "primary_evidence_key": "<allowed_evidence_key>",
  "secondary_label": "<allowed_label>",
  "secondary_evidence_key": "<allowed_evidence_key>"
}
```

Hard constraints
- `primary_label` and `secondary_label` must be distinct
- both labels must come from the fixed 8-label vocabulary
- each evidence key must be valid for the chosen label
- output must contain exactly the 4 required keys and no prose

Current scaffold shape
- source examples before supplements: `26` train / `8` eval
- train-only supplemental source examples: `8`
- final rows: `34` train / `8` eval
- helper metadata:
  - `data/artifact-card-failure-modes-forced-top2-v2/train_metadata.json`
  - `data/artifact-card-failure-modes-forced-top2-v2/eval_metadata.json`
- mean train input length: about `4366.2` chars

Why this is better motivated than top2-v1
- `top2-v1` forced two labels but did not force the model to justify each slot through explicit evidence
- `joint-rank-v1` forced one shared object but still left a cheap near-abstention path
- `forced-top2-v2` keeps the target close to the downstream object while removing abstention entirely and preserving the evidence-binding lessons from the later branches

Files added for the scaffold
- dataset builder: `scripts/build_failure_mode_forced_top2_v2_dataset.py`
- evaluator: `scripts/evaluate_failure_mode_forced_top2_run.py`
- dataset folder: `data/artifact-card-failure-modes-forced-top2-v2/`
- smoke artifact: `tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v2-smoke-run_summary.json`

Local verification completed
- `python3 -m py_compile scripts/build_failure_mode_forced_top2_v2_dataset.py scripts/evaluate_failure_mode_forced_top2_run.py scripts/preview_dataset.py modal/train_unsloth_artifact_card.py` passed
- `python3 scripts/build_failure_mode_forced_top2_v2_dataset.py` generated the dataset successfully
- `python3 scripts/preview_dataset.py artifact-card-failure-modes-forced-top2-v2` showed valid strict-JSON rows for train and eval
- a perfect-payload smoke test through `scripts/evaluate_failure_mode_forced_top2_run.py` returned `1.0` for row validity, exact row match, top-2 set match, top-2 ordered match, and both evidence-key accuracies

Recommended first run command
```bash
set -a && source .env && set +a && source .venv/bin/activate && \
modal run modal/train_unsloth_artifact_card.py \
  --dataset-name artifact-card-failure-modes-forced-top2-v2 \
  --max-steps 20
```

Recommended comparison order
1. run `artifact-card-failure-modes-forced-top2-v2` on the current `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
2. rerun the exact same branch on `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit`
3. optionally run `unsloth/gemma-3-1b-it-bnb-4bit` as a family-control comparison

Success criterion
- beat the current strongest downstream baseline, `artifact-card-failure-modes-pairwise-v1`, on top-2 set match `0.25`
- also treat any ordered top-2 recovery above `0.0` as an important sign that the no-abstention target is learning something real
- evidence-key accuracy matters as a grounding check, but label-pair recovery is the main pass/fail condition

If this branch still fails
- do not spend the next patch budget on another flat one-shot target
- move to a staged shortlist / tournament selector that forces choice in smaller comparison steps
