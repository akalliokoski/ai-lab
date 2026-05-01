# Proposed next branch: artifact-card-failure-modes-forced-top2-v2

Date: 2026-05-01
Status: implemented as a scaffold; see `docs/artifact-card-failure-modes-forced-top2-v2-scaffold.md`

## Why this branch should exist

`artifact-card-failure-modes-joint-rank-v1` made all 8 labels compete in one output object, but it still left an easy escape hatch: the model could mark nearly everything as `out` and avoid committing to the two required positive slots.

That is exactly what happened:
- 7/8 held-out eval rows predicted every label as `out`
- the remaining row emitted only `generic-explanation = secondary`
- branch-specific `valid_json_rate` fell to `0.0` once the exact-one-primary / exact-one-secondary contract was enforced

The next branch should not ask the model to emit a full 8-label state map at all.
It should force the model to pick the final ranked pair directly, while also binding each chosen slot to concrete evidence so the model cannot win by repeating a default label pair without support.

## Proposed branch name

`artifact-card-failure-modes-forced-top2-v2`

Why this name:
- it is a real successor to `artifact-card-failure-modes-top2-v1`
- but it is not a pure retry of the older direct-pair branch
- the key new ingredient is evidence binding, added after the later pairwise / evidence / rank-select / joint-rank lessons

## Core design

### Output format

One strict JSON object per source example:

```json
{
  "primary_label": "<allowed_label>",
  "primary_evidence_key": "<allowed_evidence_key>",
  "secondary_label": "<allowed_label>",
  "secondary_evidence_key": "<allowed_evidence_key>"
}
```

Hard constraints:
- `primary_label` and `secondary_label` must be distinct
- each label must come from the existing 8-label vocabulary
- each evidence key must come from a closed allowed list already used in the evidence/rank branches
- no `out`, `none`, `abstain`, or free-form justification field

This removes the all-`out` escape hatch completely.

### Training target philosophy

The model should not emit a full global label map.
It should emit only the final two slots that matter for downstream reconstruction.

This reuses a lesson from earlier branches:
- `pairwise-v1` helped because it turned the task into forced comparisons
- `joint-rank-v1` failed because the model could still refuse almost every label inside the shared object
- `top2-v1` failed because direct pair selection was too weakly grounded and too easy to collapse into repeated defaults

So the proposed new branch combines:
- direct final-pair prediction from `top2-v1`
- evidence grounding pressure from the later evidence/rank branches
- explicit removal of abstention states from `joint-rank-v1`

## Why this is different from top2-v1

`top2-v1` already forced exactly two labels, but it still failed badly.
This branch is not justified unless it changes the learning problem materially.

The intended differences are:

1. Evidence-bound slots
- `top2-v1` predicted labels only
- `forced-top2-v2` predicts label + evidence key for each slot
- that forces each chosen label to attach to some observed support, instead of only producing a memorized default pair

2. Better contrast notes from the later branches
- reuse the sharper confusion-boundary wording learned in `contrast-v1/v2`, `rank-select-v1/v2`, and `joint-rank-v1`
- especially for:
  - `missing-required-detail` vs `no-material-change`
  - `phrase-copy-or-template-collapse` vs `generic-explanation`
  - `overlap-contaminated-eval` vs generic badness labels

3. Shorter, cleaner supervision target than joint-rank-v1
- 4 required fields instead of 8 fixed label keys
- no opportunity to satisfy most of the object with repeated `out`
- easier evaluation: exactly the downstream object we care about

4. Supplemental train-only cases should now target slot allocation, not per-label calibration
- include examples where the tempting default label should not occupy either slot
- include examples where one correct label is obvious but the second label is easy to miss
- include examples where overlap contamination must outrank generic damage labels

## Expected dataset shape

Same source split policy as the recent branches:
- source examples before supplements: `26` train / `8` eval
- preserve the same held-out eval sources for continuity
- add a small train-only supplemental set, probably `8-12` source examples

Expected final row shape:
- one row per source example
- likely around `34-38` train rows and `8` eval rows

This keeps the run lightweight and comparable to `top2-v1` and `joint-rank-v1`, instead of returning to the large `pairwise-v1` expansion.

## Evaluation plan

Create a branch-specific evaluator with these main metrics:
- `valid_json_rate`
- `distinct_label_rate`
- `primary_label_accuracy`
- `secondary_label_accuracy`
- `top2_set_match_rate`
- `top2_ordered_match_rate`
- `primary_evidence_key_accuracy`
- `secondary_evidence_key_accuracy`

Primary pass/fail bar:
- must beat the current strongest downstream baseline, `artifact-card-failure-modes-pairwise-v1`, on reconstructed top-2 set match `0.25`

Secondary bar:
- should finally move ordered top-2 recovery above `0.0`

Important interpretation rule:
- label-set recovery matters more than evidence-key accuracy
- evidence keys are there to force grounding, not to become the main scoreboard

## Why this should be tried before a staged tournament

A staged shortlist/tournament selector is still a valid fallback.
But `forced-top2-v2` should come first because it is the smallest design change that directly tests the new hypothesis:

Hypothesis:
- the main remaining failure is not that the model cannot compare labels at all
- it is that the current target still makes near-abstention easier than forced selection

`forced-top2-v2` tests that hypothesis cleanly without introducing multi-step inference logic.

If `forced-top2-v2` still collapses, then the next stronger redesign should become a staged selector.

## If this branch fails, the next branch should be

`artifact-card-failure-modes-tournament-v1`

Likely shape:
- stage 1: pick the stronger label from a small candidate pair or mini-shortlist
- stage 2: pick the second label conditional on the first already being fixed
- possibly restrict candidate sets using evidence-group hints

That would borrow the relative-strength lesson from `pairwise-v1` while still removing all-`out` abstention.

## Recommended model plan for this branch

Keep model choice separate from target-design judgment.

Best experiment sequence:
1. implement `forced-top2-v2`
2. run it first on the current `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` for continuity
3. run the exact same branch on `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit`
4. optionally run `unsloth/gemma-3-1b-it-bnb-4bit` as a family-control comparison

This keeps the target-design readout clean while still testing the stronger replacement model path.

## Minimal implementation checklist

1. New dataset builder
- `scripts/build_failure_mode_forced_top2_v2_dataset.py`
- generate `train.jsonl`, `eval.jsonl`, metadata, and `task_config.json`

2. New evaluator
- `scripts/evaluate_failure_mode_forced_top2_run.py`
- score label-set and evidence-key recovery directly

3. New dataset folder
- `data/artifact-card-failure-modes-forced-top2-v2/`

4. Local verification
- build dataset
- preview dataset
- perfect-payload smoke eval

5. First Modal run
- keep `--max-steps 20` for comparability with recent short runs

## Recommended decision

The next branch to implement should be `artifact-card-failure-modes-forced-top2-v2`.

Reason:
- it removes the all-`out` escape hatch more cleanly than `joint-rank-v1`
- it stays closer to the actual downstream objective than the larger pairwise expansion
- it fixes the main weakness of `top2-v1` by requiring explicit evidence binding for each chosen slot
- it is the smallest high-value post-joint-rank test before escalating to a staged tournament design
