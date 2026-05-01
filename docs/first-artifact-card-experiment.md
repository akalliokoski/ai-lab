# First Artifact-Card Experiment

Date: 2026-04-30

## Goal

Pivot the first serious Unsloth project away from broad tutoring and toward a narrow structured-output task that has a realistic chance to show a clean first win.

Chosen project:
- `artifact-card-sft`

Plain-language job:
- read short experiment evidence
- output one strict JSON experiment card
- keep the schema fixed and score the results automatically

## Why this project replaces the tutor adapter

The tutor adapter was useful as a debugging case study, but it was a poor first success target.

What it asked the model to do:
- explain ML concepts
- express repo-specific workflow heuristics
- stay concise and beginner-friendly
- keep the right causal idea on held-out prompts
- generalize across wording changes

That was too broad for a tiny starter dataset.

The new artifact-card task is a better first fit because it is:
- narrower
- structured
- directly useful inside this repo
- easy to evaluate automatically
- aligned with the real Modal artifact workflow already in place

## Dataset shape

Current starter dataset:
- `data/artifact-card-v1/train.jsonl`
- `data/artifact-card-v1/eval.jsonl`
- train rows: 20
- eval rows: 8

Each row uses the same outer format as the earlier tutor project:
- `instruction`
- `input`
- `output`

But the target output is now one strict JSON object with these keys:
- `run_id`
- `dataset_name`
- `model_name`
- `verdict`
- `primary_failure_modes`
- `key_evidence`
- `next_action`

## Success criteria

The smallest useful success is now:
- a short remote run on Modal
- a saved adapter and run summary
- automatic scoring over the full eval split
- tuned outputs that beat the base model on:
  - JSON validity
  - exact-card match rate
  - field accuracy

This is a much cleaner first success criterion than “the model became a better tutor.”

## New project artifacts

Created for this pivot:
- `data/artifact-card-v1/train.jsonl`
- `data/artifact-card-v1/eval.jsonl`
- `data/artifact-card-v1/README.md`
- `scripts/preview_dataset.py`
- `scripts/evaluate_artifact_card_run.py`
- `modal/train_unsloth_artifact_card.py`

## First real Modal run result

Run completed successfully:
- run_id: `20260430T072526Z`
- artifact path: `/artifacts/artifact-card-v1/20260430T072526Z/`
- local pulled summary: `tmp/modal-artifacts/artifact-card-v1-20260430T072526Z/run_summary.json`
- model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- steps: `20`
- train loss: `2.496953636407852`

What improved versus base:
- base JSON validity: `0.125`
- tuned JSON validity: `1.0`
- base exact-card match: `0.0`
- tuned exact-card match: `0.0`

Per-field accuracy:
- `run_id`: `0.125` -> `1.0`
- `dataset_name`: `0.125` -> `1.0`
- `model_name`: `0.125` -> `1.0`
- `verdict`: `0.0` -> `0.375`
- `primary_failure_modes`: `0.0` -> `0.0`
- `key_evidence`: `0.0` -> `0.0`
- `next_action`: `0.0` -> `0.0`

How the failure showed up in artifacts:
- The tuned model learned the outer JSON shape very strongly.
- It still failed to reproduce the canonical label vocabulary and evidence phrases.
- The remaining errors are mostly semantic normalization failures, not formatting failures.
- `verdict` improved on only 3 of 8 eval rows; the other 5 rows drifted into near-synonyms like `unreliable`, `no improvement`, `improvement`, or `mixed` instead of the target labels.
- `primary_failure_modes`, `key_evidence`, and `next_action` stayed at `0.0` field accuracy because the model paraphrased or invented plausible-looking alternatives instead of matching the target schema values.

Interpretation:
- This is a useful partial success: the project choice is better than the tutor task because the run produced a clear, scoreable improvement in structure.
- It is not yet a task success because semantic field accuracy is still weak.
- Trust this eval artifact over the falling train loss: the run mostly taught schema discipline, not canonical card content.

Next dataset fix:
- tighten label normalization for `verdict`
- reduce synonym freedom in `primary_failure_modes`
- shorten and canonicalize `key_evidence`
- constrain `next_action` to a smaller reusable action vocabulary
- add a few targeted rows that contrast allowed labels against tempting near-synonyms

## Second dataset pass: artifact-card-v2

What changed:
- created `data/artifact-card-v2/`
- kept the same output schema
- rewrote the task from loose summarization into constrained label-and-phrase selection
- added explicit allowed vocabularies for `verdict`, `primary_failure_modes`, `key_evidence`, and `next_action`
- asked the model to copy exact allowed phrases instead of inventing near-synonyms

Second run completed successfully:
- run_id: `20260430T073913Z`
- artifact path: `/artifacts/artifact-card-v2/20260430T073913Z/`
- local pulled summary: `tmp/modal-artifacts/artifact-card-v2-20260430T073913Z/run_summary.json`
- model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- steps: `20`
- train loss: `2.108652096986771`

v1 -> v2 tuned metric change:
- `valid_json_rate`: `1.0` -> `1.0`
- `exact_card_match_rate`: `0.0` -> `0.0`
- `verdict`: `0.375` -> `0.75`
- `primary_failure_modes`: `0.0` -> `0.125`
- `key_evidence`: `0.0` -> `0.875`
- `next_action`: `0.0` -> `0.125`

Interpretation:
- This is a real improvement in task fit.
- The sharper v2 dataset preserved the structure win and converted most of the remaining gain into semantic field accuracy, especially `verdict` and `key_evidence`.
- The project is now much closer to a genuine first-win task, even though exact-card match is still `0.0`.

What still fails:
- `primary_failure_modes` is still weak; the model often chooses a plausible but wrong second label.
- `next_action` is still weak; the model often picks a nearby action from the allowed list instead of the exact target action.
- A few outputs still normalize strings incorrectly, for example using hyphenated action text or swapping in a neighboring label.

Best next move from here:
- split the hardest semantic fields into even narrower subtasks for data generation discipline
- keep the card task, but patch `artifact-card-v2` with a few contrast rows focused only on:
  - second-label selection inside `primary_failure_modes`
  - choosing the exact `next_action` among nearby alternatives
- do not broaden the schema or add longer notes yet

## Third dataset pass: artifact-card-v3

What changed:
- created `data/artifact-card-v3/`
- kept the v2 schema and eval split unchanged
- added a short selection-hints block to every prompt
- added 6 targeted contrast rows focused on the exact v2 confusion patterns
- made the action mapping more explicit for:
  - structural gain with mixed semantics -> `add automatic field scoring before the next run`
  - longer inputs weakening schema discipline -> `shorten the inputs and keep the schema fixed before rerunning`
  - repeated unchanged failures -> `stop rerunning unchanged data and patch the weak concepts`
  - overlap contamination / copied phrasing -> `remove overlap-heavy rows and rerun`

Third run completed successfully:
- run_id: `20260430T091500Z`
- artifact path: `/artifacts/artifact-card-v3/20260430T091500Z/`
- local pulled summary: `tmp/modal-artifacts/artifact-card-v3-20260430T091500Z/run_summary.json`
- model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- steps: `20`
- train loss: `2.017786604166031`

v2 -> v3 tuned metric change:
- `valid_json_rate`: `1.0` -> `1.0`
- `exact_card_match_rate`: `0.0` -> `0.0`
- `verdict`: `0.75` -> `0.625`
- `primary_failure_modes`: `0.125` -> `0.125`
- `key_evidence`: `0.875` -> `0.625`
- `next_action`: `0.125` -> `0.5`

Interpretation:
- This was a mixed result, not a clean improvement.
- The v3 patch did improve exact `next_action` selection materially.
- But it also regressed `verdict` and `key_evidence`, while `primary_failure_modes` stayed flat.
- `exact_card_match_rate` still stayed at `0.0`, so the full-card task is now showing cross-field tradeoffs instead of steady improvement.

How the failure showed up in artifacts:
- The tuned model sometimes copied instruction scaffolding or prompt wording into the answer instead of staying tightly on the canonical evidence phrases.
- One held-out `regressed` case came back as the malformed label `regraded`, showing that lower loss did not translate into more reliable semantic normalization.
- Several rows improved action choice while simultaneously degrading evidence or failure-mode choice, which means the patch sharpened one decision boundary at the cost of others.

Updated conclusion after v3:
- The task choice is still better than the original tutor project.
- But the best next move is no longer “add more contrast rows to the full card task.”
- The cleaner next branch is to split supervision into smaller tasks such as `next_action`-only or `primary_failure_modes`-only prediction, then decide whether to recombine later.

## First decomposed branch: artifact-card-failure-modes-v1

What changed:
- created `data/artifact-card-failure-modes-v1/`
- kept the same underlying run evidence as `artifact-card-v3`
- narrowed the output to one strict JSON object with only `primary_failure_modes`
- removed full-card output pressure from `verdict`, `key_evidence`, and `next_action`
- added dataset-level `task_config.json` so the same Modal/Unsloth entrypoint can score narrower artifact-card subtasks

Decomposed run completed successfully:
- run_id: `20260430T094854Z`
- artifact path: `/artifacts/artifact-card-failure-modes-v1/20260430T094854Z/`
- local pulled summary: `tmp/modal-artifacts/artifact-card-failure-modes-v1-20260430T094854Z/run_summary.json`
- model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- steps: `20`
- train loss: `2.363450402021408`

Primary failure-mode metric change:
- full-card baseline field accuracy (`artifact-card-v2`): `0.125`
- full-card patched field accuracy (`artifact-card-v3`): `0.125`
- decomposed branch exact-match accuracy (`artifact-card-failure-modes-v1`): `0.125`
- valid JSON stayed `1.0`

How the failure showed up in artifacts:
- the tuned model did not beat the base model on the held-out split even after the task was narrowed
- it collapsed repeatedly to `missing-required-detail` plus `phrase-copy-or-template-collapse` on 5 of 8 eval rows
- the branch recovered the overlap-related eval row exactly, but it still missed rows that required distinguishing `no-material-change`, `generic-explanation`, `hallucinated-detail`, and `fluency-without-correctness`

Interpretation:
- decomposition alone was not enough to solve `primary_failure_modes`
- this is still a useful result because it rules out one simple hypothesis: the full-card fields were not the only reason this label set was failing
- the remaining bottleneck now looks more like label-semantic ambiguity or evidence framing than multi-field interference alone

Updated conclusion after the first decomposed branch:
- keep `artifact-card-v2` as the best full-card baseline
- keep `artifact-card-failure-modes-v1` as a documented negative result about simple output decomposition
- the next cleaner branch should probably redesign the supervision for this field more aggressively, for example with pairwise label-choice contrast prompts or one-label-at-a-time evidence judgments before recombining the final 2-label set

## Second decomposed branch: artifact-card-failure-modes-binary-v1

What changed:
- created `data/artifact-card-failure-modes-binary-v1/`
- expanded each original example into one-label-at-a-time binary judgments over the candidate failure-mode vocabulary
- changed the target output to one strict JSON object with exactly:
  - `candidate_label`
  - `belongs`
- kept dataset-level `task_config.json` so the shared training/eval pipeline could score the narrowed binary task without forking code
- preserved the same underlying held-out cases by converting the 8 eval examples into 64 label-judgment rows

Binary-judgment run completed successfully:
- run_id: `20260430T104259Z`
- artifact path: `/artifacts/artifact-card-failure-modes-binary-v1/20260430T104259Z/`
- local pulled summary: `tmp/modal-artifacts/artifact-card-failure-modes-binary-v1-20260430T104259Z/run_summary.json`
- model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- steps: `20`
- train loss: `2.651485913991928`

Binary-judgment metric change:
- base valid JSON: `0.984375`
- tuned valid JSON: `1.0`
- base exact binary row match: `0.359375`
- tuned exact binary row match: `0.71875`
- `candidate_label` accuracy: `0.546875` -> `0.984375`
- `belongs` accuracy: `0.546875` -> `0.734375`

How the failure still showed up in artifacts:
- The model learned the binary judgment format much better than the direct 2-label output format.
- But reconstructing the final top-2 failure-mode set from the 64 tuned binary judgments still gave `0.0` exact match across the original 8 eval cases.
- The tuned branch predicted `no-material-change` as positive on 7 of 8 cases.
- It predicted `missing-required-detail` as negative on all 8 eval cases even though that label was positive on 6 of the 8 held-out cases.

Interpretation:
- This is the first decomposed branch that produced a strong local supervision signal instead of a flat failure.
- But it is still not a usable final subtask result because the reconstructed failure-mode sets are wrong.
- So the next bottleneck is now calibration and final selection structure, not output formatting alone.

Updated conclusion after the binary branch:
- keep `artifact-card-v2` as the best full-card baseline
- keep `artifact-card-failure-modes-v1` as the negative result for simple direct decomposition
- keep `artifact-card-failure-modes-binary-v1` as the stronger supervision redesign that improved binary row-level judgment but still failed final label-set reconstruction
- the next branch should likely force a better final decision rule, such as exactly-two-positive selection, pairwise comparisons between labels, or evidence-conditioned scoring before final ranking

## Third decomposed branch: artifact-card-failure-modes-top2-v1

What changed:
- created `data/artifact-card-failure-modes-top2-v1/`
- kept the task focused on `primary_failure_modes`
- changed the target output to one strict JSON object with exactly:
  - `first_label`
  - `second_label`
- forced the model to make the final decision directly: exactly two distinct labels, ranked by strength of support
- added sharper contrast notes in the prompt, especially for the confusion boundary between `no-material-change` and `missing-required-detail`

Top-2 run completed successfully:
- run_id: `20260430T122543Z`
- artifact path: `/artifacts/artifact-card-failure-modes-top2-v1/20260430T122543Z/`
- local pulled summary: `tmp/modal-artifacts/artifact-card-failure-modes-top2-v1-20260430T122543Z/run_summary.json`
- model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- steps: `20`
- train loss: `1.9992237269878388`

Top-2 metric result:
- base valid JSON: `1.0`
- tuned valid JSON: `1.0`
- base exact final-pair match: `0.0`
- tuned exact final-pair match: `0.0`
- `first_label` accuracy: `0.125` -> `0.125`
- `second_label` accuracy: `0.125` -> `0.0`

How the failure showed up in artifacts:
- The tuned model collapsed to `missing-required-detail` as `first_label` on 7 of 8 held-out rows.
- It then rotated among weak second guesses such as `hallucinated-detail`, `phrase-copy-or-template-collapse`, and `wrong-causal-point`.
- It missed both `no-material-change` eval rows, both `fluency-without-correctness` rows, and the overlap-related eval row.
- This means the stronger final-decision prompt did not improve calibration; it just produced a new repeated default pair pattern.

Interpretation:
- This is a clean negative result despite the lower train loss.
- The branch did not beat either the direct decomposition branch or the binary supervision branch on the actual held-out top-2 objective.
- Forcing the final ranked pair directly is still too hard under the current supervision design.

Updated conclusion after the top-2 branch:
- keep `artifact-card-v2` as the best full-card baseline
- keep `artifact-card-failure-modes-binary-v1` as the strongest decomposition-style supervision result so far, but only for local binary judgment
- keep `artifact-card-failure-modes-top2-v1` as a negative result showing that a stronger final-decision prompt alone does not solve the label-selection problem
- the next branch should likely move to a true comparison structure such as pairwise label ranking or evidence-conditioned per-label scoring instead of asking the model to jump straight to the final ranked pair

## Fourth decomposed branch: artifact-card-failure-modes-pairwise-v1

What changed:
- created `data/artifact-card-failure-modes-pairwise-v1/`
- kept the task focused on `primary_failure_modes`
- expanded each original example into pairwise label comparisons across the full 8-label vocabulary
- changed the target output to one strict JSON object with exactly:
  - `preferred_label`
- induced a comparison target from the original ordered final pair: first gold label > second gold label > all non-gold labels
- added metadata files so pairwise eval rows could be reconstructed back into one top-2 prediction per original held-out example

Pairwise run completed successfully:
- run_id: `20260430T125005Z`
- artifact path: `/artifacts/artifact-card-failure-modes-pairwise-v1/20260430T125005Z/`
- local pulled summary: `tmp/modal-artifacts/artifact-card-failure-modes-pairwise-v1-20260430T125005Z/run_summary.json`
- model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- steps: `20`
- train loss: `2.256138324737549`

Pairwise metric result:
- base valid JSON: `0.9910714285714286`
- tuned valid JSON: `1.0`
- base exact pairwise row match: `0.6473214285714286`
- tuned exact pairwise row match: `0.5580357142857143`
- reconstructed base exact top-2 set match: `0.0`
- reconstructed tuned exact top-2 set match: `0.25`
- reconstructed tuned exact top-2 order match: `0.0`

How the mixed result showed up in artifacts:
- The pairwise branch is the first comparison-style supervision format that recovered any non-zero held-out top-2 set match beyond the earlier direct decomposition result.
- It correctly recovered 2 of the 8 original eval sets at the set level, but both were ranked backwards as `missing-required-detail` before `no-material-change`.
- On most other held-out rows, `missing-required-detail` still dominated the pairwise win counts and then pulled `no-material-change` or another fallback into second place.
- The overlap-related row still failed badly, reconstructing `missing-required-detail` + `no-material-change` instead of `overlap-contaminated-eval` + `phrase-copy-or-template-collapse`.

Interpretation:
- This is a mixed result, not a clean success and not a pure negative result either.
- Pairwise supervision did improve the real downstream objective relative to both the binary recomposition branch and the direct top-2 branch, because reconstructed exact set match rose from `0.0` to `0.25`.
- But it still failed the stricter ordered final-pair objective, and local pairwise row accuracy was only `0.5580357142857143`.
- So the comparison structure helped, but the full 8-label pairwise expansion still left `missing-required-detail` as an over-dominant default label.

Updated conclusion after the pairwise branch:
- keep `artifact-card-v2` as the best full-card baseline
- keep `artifact-card-failure-modes-binary-v1` as the strongest local supervision redesign so far
- keep `artifact-card-failure-modes-pairwise-v1` as the first branch that improved downstream held-out top-2 set recovery at all
- the next branch should likely narrow the comparison problem further, for example with evidence-conditioned per-label scoring or a smaller contrastive subset focused on the hardest confusion boundaries

## Fifth decomposed branch scaffold: artifact-card-failure-modes-evidence-v1

What changed:
- created `data/artifact-card-failure-modes-evidence-v1/`
- created `scripts/build_failure_mode_evidence_dataset.py`
- created `scripts/evaluate_failure_mode_evidence_run.py`
- created `docs/artifact-card-failure-modes-evidence-v1-scaffold.md`
- kept the task focused on `primary_failure_modes`
- expanded each original source row into one candidate-label evidence judgment for each of the 8 allowed labels
- changed the target output to one strict JSON object with exactly:
  - `candidate_label`
  - `supported`
  - `evidence_key`
- added `train_metadata.json` and `eval_metadata.json` so held-out rows can still be reconstructed back into one positive-label set per original example

Scaffold result:
- source dataset: `artifact-card-failure-modes-v1`
- train rows: `208`
- eval rows: `64`
- mean train input length: about `1085.0` chars
- pairwise comparison point for reference: about `3086.8` chars mean train input length in `artifact-card-failure-modes-pairwise-v1`

Why this scaffold is cleaner:
- each row now carries only one candidate label meaning and a short contrast note instead of the full repeated 8-label pairwise rubric
- positive labels are tied to tiny canonical evidence codes such as `broader-than-reference`, `missing-or-noncanonical-field`, `overlap-untrustworthy`, or `missed-core-cause`
- negative labels always map to `not-supported`, so the model must learn both support judgment and evidence binding
- the new branch-specific evaluator can report per-label support precision/recall, positive-only evidence-key accuracy, and reconstructed positive-label set match on the original held-out cases

Verification already completed:
- the dataset builder ran successfully and wrote the scaffold under `data/artifact-card-failure-modes-evidence-v1/`
- the branch-specific evaluator passed a smoke test on a mock perfect-summary payload and returned perfect row-level and reconstruction metrics

Next run to launch:
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-evidence-v1 --max-steps 20
```

How to judge the first evidence-conditioned run:
- first check row-level exact match and field accuracy for `candidate_label`, `supported`, and `evidence_key`
- then inspect per-label support precision/recall, especially whether `missing-required-detail` is still over-selected
- then check reconstructed positive-label set match against the current pairwise downstream baseline of `0.25`
- if `missing-required-detail` still dominates, the next patch should shrink to the four hardest contrast groups instead of broad full-label expansion again

## Evidence-conditioned run result: artifact-card-failure-modes-evidence-v1

Run completed successfully:
- run_id: `20260430T161302Z`
- artifact path: `/artifacts/artifact-card-failure-modes-evidence-v1/20260430T161302Z/`
- local pulled summary: `tmp/modal-artifacts/artifact-card-failure-modes-evidence-v1-20260430T161302Z/run_summary.json`
- model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- steps: `20`
- train loss: `2.563367021083832`

Row-level result:
- base valid JSON: `0.796875`
- tuned valid JSON: `1.0`
- base exact row match: `0.484375`
- tuned exact row match: `0.5`
- tuned `candidate_label` accuracy: `0.984375`
- tuned `supported` accuracy: `0.59375`
- tuned `evidence_key` accuracy: `0.671875`

Branch-specific reconstruction result:
- tuned positive-only evidence-key accuracy: `0.0625`
- tuned exact positive-label set match: `0.0`
- tuned exact positive-count match: `0.125`
- tuned reconstructed top-2 set match: `0.0`
- tuned overpredict rate: `0.375`
- tuned underpredict rate: `0.5`

How the failure showed up in artifacts:
- The model became very good at copying `candidate_label` and producing valid JSON.
- It improved local support judgment somewhat, especially for `missing-required-detail` and `fluency-without-correctness`.
- But it usually failed to bind the correct positive evidence key when `supported=yes`; positive-only evidence-key accuracy stayed at `0.0625`.
- On the original held-out cases, the reconstructed outputs often became too wide, with some examples predicting 6 or 7 positive labels instead of the gold 2-label set.
- Several important labels still had zero precision and zero recall, including `generic-explanation`, `hallucinated-detail`, `overlap-contaminated-eval`, `phrase-copy-or-template-collapse`, and `wrong-causal-point`.

Interpretation:
- This branch is a useful negative result.
- Shorter prompts and explicit evidence-conditioned supervision improved row-level formatting and field behavior, but they did not improve the real downstream label-set task.
- The failure mode shifted from pairwise dominant-label collapse to broad over-acceptance of many labels.
- So the next branch should not keep broad 8-label evidence expansion as-is.

Updated conclusion after the evidence-conditioned branch:
- keep `artifact-card-v2` as the best full-card baseline
- keep `artifact-card-failure-modes-pairwise-v1` as the strongest downstream decomposition result so far
- treat `artifact-card-failure-modes-evidence-v1` as a useful negative result that improved local row behavior but regressed the real reconstructed objective
- the next branch should narrow to a small set of confusion-targeted contrast groups instead of full 8-label expansion

## Sixth decomposed branch scaffold: artifact-card-failure-modes-contrast-v1

What changed:
- created `data/artifact-card-failure-modes-contrast-v1/`
- created `scripts/build_failure_mode_contrast_dataset.py`
- created `scripts/evaluate_failure_mode_contrast_run.py`
- created `docs/artifact-card-failure-modes-contrast-v1-scaffold.md`
- kept the task focused on `primary_failure_modes`
- shrank supervision to the four hardest `missing-required-detail` confusion groups instead of all 8 labels
- changed the target output to one strict JSON object with exactly:
  - `contrast_group`
  - `decision`
  - `evidence_key`
- made each source example produce exactly 4 local contrast-group rows
- allowed each local decision to be one of:
  - anchor label name
  - rival label name
  - `both`
  - `neither`
- scoped reconstruction to the held-out source examples whose gold 2-label set stays inside the 5-label contrast universe

Scaffold result:
- source dataset: `artifact-card-failure-modes-v1`
- train rows: `104`
- eval rows: `32`
- reconstructable source examples: `10` train / `4` eval
- mean train input length: about `1304.9` chars
- comparison points:
  - evidence-v1 mean train input length: about `1085.0` chars
  - pairwise-v1 mean train input length: about `3086.8` chars

Why this scaffold is cleaner:
- it keeps the evidence-key idea from evidence-v1, but removes the broad 8-label over-acceptance pressure
- it avoids arbitrary full-vocabulary pairwise ties on unrelated labels
- it still gives exactly one local decision per contrast group
- it keeps reconstruction explicit and auditable instead of trusting row metrics alone

Verification already completed:
- the dataset builder ran successfully and wrote the scaffold under `data/artifact-card-failure-modes-contrast-v1/`
- `python3 scripts/preview_dataset.py artifact-card-failure-modes-contrast-v1` passed
- the branch-specific evaluator passed a perfect-payload smoke test with:
  - exact row match `1.0`
  - exact reconstructed positive-set match `1.0` on the 4 reconstructable held-out cases
  - reconstructed top-2 set match `1.0` on the same subset

Next run to launch:
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-contrast-v1 --max-steps 20
```

How to judge the first contrast-v1 run:
- first check row-level exact match plus `decision` and `evidence_key` accuracy
- then inspect per-group decision confusion
- then compare reconstruction on the 4 in-universe held-out cases against:
  - evidence-v1 downstream top-2 set match `0.0`
  - pairwise-v1 downstream top-2 set match `0.25`

## Sixth decomposed branch result: artifact-card-failure-modes-contrast-v1

Run command used:
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-contrast-v1 --max-steps 20
```

Artifacts:
- run id: `20260430T164253Z`
- artifact path: `/artifacts/artifact-card-failure-modes-contrast-v1/20260430T164253Z/`
- local pulled summary: `tmp/modal-artifacts/artifact-card-failure-modes-contrast-v1-20260430T164253Z/run_summary.json`

Row-level result:
- valid JSON improved to `1.0`
- exact row match reached `0.5625`
- `contrast_group` accuracy reached `1.0`
- `decision` accuracy reached `0.5625`
- `evidence_key` accuracy reached `0.5625`

Per-group decision confusion:
- `missing-required-detail-vs-generic-explanation`: decision accuracy `0.625`; both `neither` rows and the one `both` row all collapsed to `missing-required-detail`
- `missing-required-detail-vs-hallucinated-detail`: decision accuracy `0.625`; both `neither` rows and the one `both` row again collapsed to `missing-required-detail`
- `missing-required-detail-vs-no-material-change`: decision accuracy `0.5`; both gold `both` rows plus the one rival-only `no-material-change` row collapsed to `missing-required-detail`
- `missing-required-detail-vs-overlap-contaminated-eval`: decision accuracy `0.5`; the gold rival-only overlap row collapsed to `missing-required-detail`, and 2 anchor-only rows were overpromoted to `both`

Reconstruction on the 4 in-universe held-out source examples:
- exact positive-set match: `0.0`
- reconstructed top-2 set match: `0.0`
- predicted positive-count histogram: `{1: 4}`
- every reconstructable eval case collapsed to the singleton prediction `missing-required-detail`

Comparison against the strongest earlier branches:
- against `artifact-card-failure-modes-evidence-v1`: downstream top-2 set match stayed tied at `0.0`, but the failure mode changed from broad over-acceptance (`0`, `6`, or `7` predicted positives depending on case) to universal underprediction (`1` predicted positive on all 4 reconstructable cases here)
- against `artifact-card-failure-modes-pairwise-v1`: contrast-v1 regressed on the main downstream metric (`0.0` here vs `0.25` across the full pairwise eval set)
- on the same 4 contrast-universe held-out cases, local reconstruction stayed at `0.0` for contrast-v1, while a direct recheck of pairwise-v1 on that exact subset gives `0.5` top-2 set match

Interpretation:
- the narrower 4-group supervision did improve local structure and JSON compliance
- but it overcorrected into anchor-label collapse rather than solving the actual contrast states
- the missing states are now explicit: rival-only `generic-explanation`, rival-only `no-material-change`, rival-only `overlap-contaminated-eval`, plus `both` states in the `generic-explanation`, `no-material-change`, and `hallucinated-detail` groups

Decision for the next branch:
- do not keep iterating this exact contrast-v1 dataset locally as the main line
- keep `artifact-card-failure-modes-pairwise-v1` as the strongest downstream baseline
- next branch should inspect the weak contrast states and either:
  - add a few source examples targeted only at the missing rival-only and `both` contrast states, or
  - move to a two-stage rank-then-select setup that first scores candidate labels and then selects the final top 2 from those scores
- given how complete the anchor-label collapse was on all 4 reconstructable cases, the cleaner next move is to try the targeted-source-case patch before broadening the decision pipeline again

## Targeted contrast-v2 patch scaffold

New scaffold now exists under `data/artifact-card-failure-modes-contrast-v2/` and is generated by `scripts/build_failure_mode_contrast_v2_dataset.py`.

What changed relative to contrast-v1:
- kept the exact same eval split, so downstream comparison stays clean
- kept the same 4 contrast groups and the same `contrast_group` / `decision` / `evidence_key` output contract
- added 6 supplemental train-only source cases aimed only at the missing states exposed by the contrast-v1 failure analysis:
  - rival-only `generic-explanation`
  - rival-only `no-material-change`
  - rival-only `overlap-contaminated-eval`
  - `both` in the `generic-explanation`, `no-material-change`, and `hallucinated-detail` groups

Current scaffold shape:
- source examples before contrast expansion: `32` train / `8` eval
- contrast rows: `128` train / `32` eval
- reconstructable source examples in the 5-label contrast universe: `13` train / `4` eval
- mean train input length stayed effectively flat: about `1306.2` chars here vs about `1304.9` in contrast-v1

Local verification completed:
- dataset preview passed with valid strict-JSON targets
- a perfect-payload smoke test through `scripts/evaluate_failure_mode_contrast_run.py` returned `1.0` row metrics and `1.0` reconstruction metrics on the unchanged eval split
- smoke summary written to `tmp/modal-artifacts/artifact-card-failure-modes-contrast-v2-smoke-run_summary.json`

Recommended next run command:
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-contrast-v2 --max-steps 20
```

Branch decision after scaffolding:
- this is the right immediate local iteration because it directly tests the narrowest falsifiable hypothesis left from contrast-v1: data sparsity on a few hard contrast states
- if contrast-v2 still collapses those held-out cases to the anchor label, stop patching locally and move to the two-stage rank-then-select branch

## Seventh decomposed branch result: artifact-card-failure-modes-contrast-v2

Run command used:
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-contrast-v2 --max-steps 20
```

Artifacts:
- run id: `20260430T170129Z`
- artifact path: `/artifacts/artifact-card-failure-modes-contrast-v2/20260430T170129Z/`
- local pulled summary: `tmp/modal-artifacts/artifact-card-failure-modes-contrast-v2-20260430T170129Z/run_summary.json`

Row-level result:
- valid JSON stayed at `1.0`
- exact row match stayed at `0.5625`
- `contrast_group` accuracy stayed at `1.0`
- `decision` accuracy stayed at `0.5625`
- `evidence_key` accuracy improved slightly from `0.5625` to `0.59375`

Per-group decision confusion:
- `missing-required-detail-vs-generic-explanation`: unchanged collapse; 2 gold `neither` rows and 1 gold `both` row still mapped to `missing-required-detail`
- `missing-required-detail-vs-hallucinated-detail`: unchanged collapse; 2 gold `neither` rows and 1 gold `both` row still mapped to `missing-required-detail`
- `missing-required-detail-vs-no-material-change`: unchanged collapse; both gold `both` rows, the gold rival-only `no-material-change` row, and the gold `neither` row all mapped to `missing-required-detail`
- `missing-required-detail-vs-overlap-contaminated-eval`: still failed the rival-only overlap state, and 2 anchor-only rows were still overpromoted to `both`

Reconstruction on the 4 in-universe held-out source examples:
- exact positive-set match: `0.0`
- reconstructed top-2 set match: `0.0`
- predicted positive-count histogram: `{1: 4}`
- every reconstructable eval case still collapsed to the singleton prediction `missing-required-detail`

Comparison against earlier branches:
- against `artifact-card-failure-modes-contrast-v1`: no downstream improvement at all; reconstruction stayed at `0.0` / `0.0` and the same singleton-collapse pattern remained, despite the targeted 6-case patch
- against `artifact-card-failure-modes-pairwise-v1`: contrast-v2 still trails the strongest downstream branch (`0.0` here vs `0.25` top-2 set match on the full pairwise eval and `0.5` on this exact 4-case subset)
- against `artifact-card-failure-modes-evidence-v1`: contrast-v2 still avoids broad over-acceptance, but that just means it fails by consistent underprediction instead of evidence-v1’s mixed `0`, `6`, and `7` predicted-positive counts

Interpretation:
- the minimal targeted-state patch did not fix the actual bottleneck
- this is strong evidence that the problem is no longer just missing state coverage inside the narrow contrast dataset
- the branch is now saturated on local structural gains while still failing the ranked label-recovery objective

Decision for the next branch:
- treat `artifact-card-failure-modes-contrast-v2` as a clean negative result
- stop patching this narrow contrast branch locally
- keep `artifact-card-failure-modes-pairwise-v1` as the strongest downstream baseline
- next branch should move to a two-stage rank-then-select design that first scores candidate labels and then selects the final top 2 from those scores
- the two-stage design should preserve artifact-first evaluation and must be judged by reconstruction first, not row metrics or loss

## Eighth decomposed branch scaffold: artifact-card-failure-modes-rank-select-v1

New scaffold now exists under `data/artifact-card-failure-modes-rank-select-v1/` and is generated by `scripts/build_failure_mode_rank_select_dataset.py`.

What changed relative to earlier branches:
- keeps the same 26 train / 8 eval source cases from `artifact-card-failure-modes-v1`
- returns to one-label-at-a-time supervision like `artifact-card-failure-modes-evidence-v1`, but replaces flat support with explicit rank supervision
- each candidate row now predicts `candidate_label`, `support_rank`, and `evidence_key`
- `support_rank` is a 3-level target: `primary`, `secondary`, or `out`
- stage 2 is deterministic inside `scripts/evaluate_failure_mode_rank_select_run.py`: `primary -> 2`, `secondary -> 1`, `out -> 0`, then select the final ordered top 2 from the resulting score map

Current scaffold shape:
- expanded rows: `208` train / `64` eval
- helper metadata: `data/artifact-card-failure-modes-rank-select-v1/train_metadata.json` and `eval_metadata.json`
- mean train input length is about `1289.0` chars, which stays close to the shorter evidence-conditioned branch and far below the pairwise prompt mass

Why this is the right next branch:
- `pairwise-v1` is still the strongest downstream baseline, but it only reached top-2 set match `0.25` and ordered recovery `0.0`
- `evidence-v1` showed that one-label prompts can improve row metrics without solving final selection
- `contrast-v1` and `contrast-v2` showed that even cleaner local boundary supervision can still collapse the final prediction to singleton `missing-required-detail`
- this scaffold directly tests whether the missing ingredient is explicit first-vs-second rank supervision before the final selection step

Local verification completed:
- `python3 -m py_compile scripts/build_failure_mode_rank_select_dataset.py scripts/evaluate_failure_mode_rank_select_run.py scripts/preview_dataset.py modal/train_unsloth_artifact_card.py` passed
- `python3 scripts/build_failure_mode_rank_select_dataset.py` generated the dataset successfully
- `python3 scripts/preview_dataset.py artifact-card-failure-modes-rank-select-v1` passed with valid strict-JSON targets
- a perfect-payload smoke test through `scripts/evaluate_failure_mode_rank_select_run.py` returned `1.0` row metrics plus `1.0` reconstruction metrics and wrote `tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v1-smoke-run_summary.json`

Recommended next run command:
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-rank-select-v1 --max-steps 20
```

How to judge the first rank-select run:
- first check `scripts/evaluate_failure_mode_rank_select_run.py`, not just `run_summary.json` field metrics
- row-level exact match and `support_rank` accuracy matter, but the main pass/fail condition is reconstruction
- minimum downstream bar to beat:
  - `artifact-card-failure-modes-pairwise-v1` top-2 set match `0.25`
  - `artifact-card-failure-modes-pairwise-v1` ordered top-2 match `0.0`
- also inspect whether the model still collapses to `missing-required-detail` as `primary` across most eval cases

## Eighth decomposed branch result: artifact-card-failure-modes-rank-select-v1

Run command used:
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-rank-select-v1 --max-steps 20
```

Artifacts:
- Modal artifact dir: `/artifacts/artifact-card-failure-modes-rank-select-v1/20260430T182335Z/`
- Local summary copy: `tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v1-20260430T182335Z/run_summary.json`

What improved locally:
- train loss finished at `2.4495701491832733`
- tuned row validity rose to `0.984375`
- tuned exact row match reached `0.65625`
- tuned field accuracy reached:
  - `candidate_label = 0.984375`
  - `support_rank = 0.703125`
  - `evidence_key = 0.6875`

But the branch still failed the real downstream test:
- exact positive-set match stayed `0.0`
- top-2 set match stayed `0.0`
- ordered top-2 match stayed `0.0`
- first-label accuracy fell to `0.0`
- second-label accuracy reached only `0.125`
- selected positive-count histogram was `{0: 5, 2: 2, 4: 1}` across the 8 held-out source examples

Why this is still a negative result:
- the scaffold improved row behavior again, but that gain did not transfer to final rank reconstruction
- unlike the narrow contrast branch, this failure is not a pure singleton anchor collapse
- the tuned scorer mostly underselected to zero positives on 5 of 8 held-out source examples, while one example overselected 4 positives
- the surviving false positives were still concentrated in the same confusing label family: `generic-explanation`, `phrase-copy-or-template-collapse`, `fluency-without-correctness`, and sometimes `no-material-change`
- the only invalid tuned row also revealed a schema leak: the model copied an `allowed_evidence_keys` tail into the JSON instead of returning only the required fields

Decision after the first rank-select run:
- keep `artifact-card-failure-modes-pairwise-v1` as the strongest downstream baseline
- record `artifact-card-failure-modes-rank-select-v1` as another clean negative result
- do not treat improved row metrics or lower loss as evidence that the selector worked
- next patch budget should target rank calibration and schema leakage directly, not just rerun the same scaffold unchanged

## Ninth decomposed branch scaffold: artifact-card-failure-modes-rank-select-v2

New scaffold now exists under `data/artifact-card-failure-modes-rank-select-v2/` and is generated by `scripts/build_failure_mode_rank_select_v2_dataset.py`.

What changed relative to rank-select-v1:
- adds 8 train-only supplemental source cases targeted at the exact rank-select-v1 failure pattern
- strengthens positive `missing-required-detail` cases in both primary and secondary rank positions
- adds harder negative control against spurious `fluency-without-correctness` and `phrase-copy-or-template-collapse` positives when all required fields stayed present
- replaces the long `allowed_evidence_keys` list with one explicit `positive_evidence_key_if_selected` value per row
- tells the model there are exactly 2 positive labels overall and explicitly bans extra keys, copied policy text, and prompt echoes
- reduces `max_new_tokens` from `48` to `40` to discourage schema spillover

Current scaffold shape:
- source examples before expansion: `26` train / `8` eval
- supplemental train-only source cases: `8`
- expanded rows: `272` train / `64` eval
- helper metadata: `data/artifact-card-failure-modes-rank-select-v2/train_metadata.json` and `eval_metadata.json`
- mean train input length is about `1525.8` chars

Why this is the right next branch:
- rank-select-v1 already showed that row metrics can improve while reconstruction still fails completely
- the clearest repeated misses were calibration misses, especially `missing-required-detail -> out`
- the clearest repeated false positives were `generic-explanation`, `phrase-copy-or-template-collapse`, and `fluency-without-correctness`
- the only invalid tuned row copied an `allowed_evidence_keys` tail into the JSON, so the prompt contract itself needed to be simplified and hardened before spending more GPU time

Local verification completed:
- `python3 -m py_compile scripts/build_failure_mode_rank_select_v2_dataset.py scripts/evaluate_failure_mode_rank_select_run.py scripts/preview_dataset.py modal/train_unsloth_artifact_card.py` passed
- `python3 scripts/build_failure_mode_rank_select_v2_dataset.py` generated the dataset successfully
- `python3 scripts/preview_dataset.py artifact-card-failure-modes-rank-select-v2` passed with valid strict-JSON targets
- a perfect-payload smoke test through `scripts/evaluate_failure_mode_rank_select_run.py` returned `1.0` row metrics plus `1.0` reconstruction metrics and wrote `tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v2-smoke-run_summary.json`

Recommended next run command:
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-rank-select-v2 --max-steps 20
```

How to judge the first rank-select-v2 run:
- first check `scripts/evaluate_failure_mode_rank_select_run.py`, not just `run_summary.json` field metrics
- main pass/fail condition remains reconstruction, not loss or row-level structure alone
- minimum downstream bar to beat is still `artifact-card-failure-modes-pairwise-v1` top-2 set match `0.25`
- specifically inspect whether `missing-required-detail` finally recovers positive recall and whether the schema leak disappears entirely

Result from the first rank-select-v2 run (`20260501T052544Z`):
- the run completed successfully and saved artifacts under `/artifacts/artifact-card-failure-modes-rank-select-v2/20260501T052544Z/`
- local copy pulled to `tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v2-20260501T052544Z/run_summary.json`
- schema leakage was fixed cleanly: tuned `valid_json_rate` rose to `1.0` and there were no invalid rows or copied prompt tails
- but the main task regressed relative to rank-select-v1: tuned exact row match fell to `0.359375`, `support_rank` accuracy to `0.359375`, and `evidence_key` accuracy to `0.46875`
- downstream reconstruction still failed completely: exact positive-set match `0.0`, top-2 set match `0.0`, ordered top-2 match `0.0`
- the failure mode also became more decisively underselective: positive-count histogram `{0: 6, 1: 1, 2: 1}` with underselected rate `0.875`
- the intended calibration fix did not land: `missing-required-detail` positive precision and recall both stayed `0.0`
- the one label that still fired as a positive was mostly the wrong one: `phrase-copy-or-template-collapse` kept positive recall `1.0` but only `0.5` precision, while the other labels mostly collapsed to zero positive recall

Decision after the first rank-select-v2 run:
- keep the schema-hardening change as a useful diagnostic success, not a task success
- do not spend more patch budget on the same independent per-label rank-select prompt family
- keep `artifact-card-failure-modes-pairwise-v1` as the strongest downstream baseline
- next branch should test a selector that scores labels jointly instead of independently, because prompt cleanup removed schema spillover but made the underselection problem even worse

## Tenth decomposed branch scaffold: artifact-card-failure-modes-joint-rank-v1

New scaffold now exists under `data/artifact-card-failure-modes-joint-rank-v1/` and is generated by `scripts/build_failure_mode_joint_rank_v1_dataset.py`.

What changed relative to rank-select-v2:
- keeps the same source task and label vocabulary, including the 8 supplemental train-only calibration cases
- changes the supervision shape from 8 independent candidate-label rows per source example to 1 joint ranking row per source example
- outputs one strict JSON object whose fixed keys are the 8 allowed labels and whose values must be `primary`, `secondary`, or `out`
- forces global normalization directly in the prompt: exactly one primary label, exactly one secondary label, and all remaining labels out
- adds explicit guardrails for the failure boundaries that kept causing trouble: `missing-required-detail` must stay out when required fields stayed present, `phrase-copy-or-template-collapse` only becomes positive on explicit copy/distortion evidence, and `overlap-contaminated-eval` only becomes positive when overlap is explicit

Current scaffold shape:
- source examples before supplements: `26` train / `8` eval
- train-only supplemental source cases: `8`
- final rows: `34` train / `8` eval
- helper metadata: `data/artifact-card-failure-modes-joint-rank-v1/train_metadata.json` and `eval_metadata.json`
- mean train input length is about `2655.2` chars

Why this is the right next branch:
- the v2 schema patch already proved the prompt contract could be cleaned up without fixing the real selector problem
- the remaining issue is no longer prompt spillover first; it is bad allocation of the two positive slots
- independent per-label scoring kept collapsing either to zero positives or to a recurring false-positive label, so the next clean test is to make the labels compete inside one shared output object

Local verification completed:
- `python3 -m py_compile scripts/build_failure_mode_joint_rank_v1_dataset.py scripts/evaluate_failure_mode_joint_rank_run.py scripts/preview_dataset.py modal/train_unsloth_artifact_card.py` passed
- `python3 scripts/build_failure_mode_joint_rank_v1_dataset.py` generated the dataset successfully
- `python3 scripts/preview_dataset.py artifact-card-failure-modes-joint-rank-v1` passed with valid strict-JSON targets
- a perfect-payload smoke test through `scripts/evaluate_failure_mode_joint_rank_run.py` returned `1.0` row metrics, `1.0` per-label rank metrics, and `1.0` reconstruction metrics and wrote `tmp/modal-artifacts/artifact-card-failure-modes-joint-rank-v1-smoke-run_summary.json`

Recommended next run command:
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-joint-rank-v1 --max-steps 20
```

Result from the first joint-rank-v1 run (`20260501T064308Z`):
- the run completed successfully and saved artifacts under `/artifacts/artifact-card-failure-modes-joint-rank-v1/20260501T064308Z/`
- local copy pulled to `tmp/modal-artifacts/artifact-card-failure-modes-joint-rank-v1-20260501T064308Z/run_summary.json`
- the raw training summary was misleading on first glance: built-in auto-eval reported tuned `valid_json_rate = 1.0` because the model emitted parseable JSON objects with the expected keys
- branch-specific evaluation exposed the real failure: every tuned eval row violated the required global constraint `exactly one primary + exactly one secondary`
- tuned joint-rank evaluator metrics:
  - `valid_json_rate`: `0.0`
  - `exact_row_match_rate`: `0.0`
  - `exact_positive_set_match_rate`: `0.0`
  - `top2_set_match_rate`: `0.0`
  - `top2_ordered_match_rate`: `0.0`
  - `first_label_accuracy`: `0.25`
  - `second_label_accuracy`: `0.0`
  - `underselected_rate`: `1.0`
  - selected-positive histogram: `{0: 7, 1: 1}`
- the failure pattern was even more extreme than rank-select-v2:
  - 7/8 eval rows predicted every label as `out`
  - the remaining row emitted only `generic-explanation = secondary` and still no `primary`
  - `generic-explanation` became the lone surviving positive (`positive_precision = 1.0`, `positive_recall = 1.0`)
  - every other label, including `missing-required-detail`, collapsed to `positive_recall = 0.0`

Decision after the first joint-rank-v1 run:
- keep `artifact-card-failure-modes-pairwise-v1` as the strongest downstream baseline because joint-rank-v1 still did not recover a single exact top-2 set
- record `joint-rank-v1` as another clean negative result rather than as a schema or selector improvement
- the main lesson is that joint scoring alone was insufficient: the model learned the fixed key set, but not the compulsory two-slot allocation
- the next redesign should likely remove the easy all-`out` escape hatch entirely, either by:
  - predicting a direct `{primary_label, secondary_label}` object, or
  - using a staged selector / shortlist tournament where every inference step must choose among a smaller set instead of independently refusing all labels

## Latest reproduced full-card run

```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-v3 --max-steps 20
```

## Verification checklist before spending GPU time

1. Preview the dataset:
```bash
python3 scripts/preview_dataset.py artifact-card-v1
```

2. Check environment:
```bash
python3 scripts/check_env.py
```

3. Verify the Modal entrypoint CLI:
```bash
source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --help
```

4. If needed, smoke-test Modal again:
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/hello_gpu.py
```

## How to read the first run

Trust the scored eval artifacts before train loss.

Main things to check in `run_summary.json`:
- `auto_eval.base_metrics`
- `auto_eval.tuned_metrics`
- `full_eval`
- `sample_eval`

Questions to ask:
- Did tuned JSON validity beat the base model?
- Did exact field accuracy improve?
- Which field still fails most often: `verdict`, `primary_failure_modes`, `key_evidence`, or `next_action`?
- Are errors mostly formatting failures or labeling failures?

## Expected likely failure modes

Most likely early issues:
- extra prose outside the JSON
- missing required fields
- evidence copied into label fields
- overly long `key_evidence`
- correct schema but wrong `verdict` on mixed cases

Those are good early failures because they are sharp, visible, and patchable.

## Why this fits ai-lab better

This project keeps the repo's learning-by-doing goals intact while making the task much easier to diagnose.

It also reuses what already exists:
- Modal training flow
- durable artifact volume
- run-history notes
- failure analysis habits

The goal is not just another fine-tuning run.
The goal is a first fine-tuning project whose outcomes are easy to interpret and improve.
