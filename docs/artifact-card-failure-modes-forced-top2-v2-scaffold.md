# artifact-card-failure-modes-forced-top2-v2

Status
- scaffolded and locally verified on 2026-05-01
- first real Modal run completed and reviewed on 2026-05-01
- Qwen3 comparison run completed and reviewed on 2026-05-01

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
3. only if the stronger-model rerun helps, decide whether the next budget should go to a targeted confusion-set patch or to a Gemma-family control
4. optionally run `unsloth/gemma-3-1b-it-bnb-4bit` as a family-control comparison after the stronger-model result is understood

First real run result
- Run ID: `20260501T074237Z`
- Model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- Train loss: `1.8952500939369201`
- Built-in auto-eval looked encouraging:
  - `valid_json_rate`: `1.0`
  - `exact_card_match_rate`: `0.375`
  - field accuracy: `primary_label = 0.375`, `primary_evidence_key = 0.5`, `secondary_label = 0.375`, `secondary_evidence_key = 0.5`
- Branch-specific evaluator is the real read:
  - `valid_json_rate`: `0.875`
  - `top2_set_match_rate`: `0.375`
  - `top2_ordered_match_rate`: `0.375`
  - `primary_label_accuracy`: `0.375`
  - `secondary_label_accuracy`: `0.375`
  - `primary_evidence_key_accuracy`: `0.375`
  - `secondary_evidence_key_accuracy`: `0.375`
  - `invalid_row_rate`: `0.125`
- This is the first decomposed branch to beat the old `pairwise-v1` downstream baseline:
  - previous best `pairwise-v1` top-2 set match: `0.25`
  - `forced-top2-v2` top-2 set match: `0.375`
  - previous best ordered top-2 recovery: `0.0`
  - `forced-top2-v2` ordered top-2 recovery: `0.375`
- Main remaining failure pattern:
  - the branch still overuses `missing-required-detail` as the primary label and `generic-explanation` as the fallback secondary label
  - both `fluency-without-correctness` eval rows were pulled into the repeated `missing-required-detail + generic-explanation` pair
  - the `hallucinated-detail` row and the `wrong-causal-point + no-material-change` row also collapsed into that same repeated pair
  - the overlap / phrase-copy eval row failed structurally because the model emitted evidence-key names (`overlap-untrustworthy`, `phrase-copy-distortion`) in label slots instead of the corresponding labels
- Practical interpretation:
  - removing the abstention path worked: the branch no longer collapses to all-`out`, and it finally recovered real downstream top-2 behavior
  - the new bottleneck is not escape-hatch abstention but label/evidence namespace confusion plus a repeated fallback pair under ambiguity
  - this branch is a real improvement, not just a clean negative result

Success criterion
- beat the current strongest downstream baseline, `artifact-card-failure-modes-pairwise-v1`, on top-2 set match `0.25`
- also treat any ordered top-2 recovery above `0.0` as an important sign that the no-abstention target is learning something real
- evidence-key accuracy matters as a grounding check, but label-pair recovery is the main pass/fail condition

Current verdict
- `forced-top2-v2` cleared the success bar on the 1B Llama baseline.
- The Qwen3 comparison run did not improve the branch and regressed it materially.
- Run ID: `20260501T075313Z`
- Model: `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit`
- Train loss looked lower at `1.7252290666103363`, but the branch-specific evaluator showed that this was not a real task win.
- Built-in auto-eval already looked worse than the 1B Llama run:
  - `valid_json_rate = 0.375`
  - `exact_card_match_rate = 0.125`
  - field accuracy: `primary_label = 0.375`, `primary_evidence_key = 0.375`, `secondary_label = 0.125`, `secondary_evidence_key = 0.125`
- Branch-specific evaluator confirmed the regression:
  - `valid_json_rate = 0.375`
  - `top2_set_match_rate = 0.125`
  - `top2_ordered_match_rate = 0.125`
  - `primary_label_accuracy = 0.375`
  - `secondary_label_accuracy = 0.125`
  - `primary_evidence_key_accuracy = 0.375`
  - `secondary_evidence_key_accuracy = 0.125`
  - `invalid_row_rate = 0.625`
- Main failure pattern in the Qwen3 run:
  - 5/8 tuned rows were invalid because the model wrapped otherwise plausible JSON in Markdown code fences instead of returning raw JSON only
  - the model did not recover the repeated `missing-required-detail + generic-explanation` fallback from the 1B Llama run, but it replaced that with a worse formatting failure that destroyed downstream recovery
  - distinct predicted label coverage also collapsed from `0.875` on the baseline run to `0.375` on Qwen3 once invalid rows were excluded by the evaluator
- Comparison decision:
  - keep the 1B Llama `forced-top2-v2` run as the current best decomposition result
  - do not treat the lower Qwen3 train loss as evidence of progress
  - the next patch budget should go to output-contract hardening for this branch, especially anti-fence / raw-JSON-only behavior, before spending more time on model-family swaps

If a later stronger-model rerun still fails to improve
- do not immediately return to another flat target redesign
- instead patch the branch around the now-visible confusion set, because this scaffold already proved the no-abstention target can beat the old downstream baseline
