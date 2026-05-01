---
title: Artifact Card SFT
created: 2026-04-30
updated: 2026-05-01
type: concept
tags: [training, dataset, evaluation, unsloth, modal, experiment, workflow]
sources: [raw/articles/first-fine-tuning-use-case-research-2026-04-30.md]
---

# Artifact Card SFT

`artifact-card-sft` is the new recommended first success-oriented fine-tuning project for `ai-lab`. It replaces the broad repo-tutor task with a narrow structured-output task: read short experiment evidence and emit one strict JSON experiment card. [[first-fine-tuning-project-options]] [[artifact-driven-experiment-debugging]] [[ai-lab-learning-path]] [[unsloth]]

## Why this project is a better fit
- It matches what tiny LoRA/QLoRA SFT usually does well: format control, extraction, and narrow behavioral shaping.
- It reuses real repo artifacts instead of inventing a toy task.
- It gives a much cleaner success signal than the tutor adapter because the output can be scored automatically.
- It strengthens the repo rule that each experiment should record what changed, what failed, and what to try next.

## Current scaffold
- Dataset v1: `data/artifact-card-v1/`
- Dataset v2: `data/artifact-card-v2/`
- Dataset v3: `data/artifact-card-v3/`
- Decomposed branch: `data/artifact-card-failure-modes-v1/`
- Binary branch: `data/artifact-card-failure-modes-binary-v1/`
- Top-2 branch: `data/artifact-card-failure-modes-top2-v1/`
- Pairwise branch: `data/artifact-card-failure-modes-pairwise-v1/`
- Evidence-conditioned branch scaffold: `data/artifact-card-failure-modes-evidence-v1/`
- Contrast-group branch scaffold: `data/artifact-card-failure-modes-contrast-v1/`
- Targeted contrast patch scaffold: `data/artifact-card-failure-modes-contrast-v2/`
- Two-stage rank-then-select scaffold: `data/artifact-card-failure-modes-rank-select-v1/`
- Rank-calibration patch scaffold: `data/artifact-card-failure-modes-rank-select-v2/`
- Joint-rank scaffold: `data/artifact-card-failure-modes-joint-rank-v1/`
- Training entrypoint: `modal/train_unsloth_artifact_card.py`
- Dataset preview: `scripts/preview_dataset.py`
- Run scoring helpers: `scripts/evaluate_artifact_card_run.py`, `scripts/evaluate_failure_mode_evidence_run.py`, `scripts/evaluate_failure_mode_contrast_run.py`, `scripts/evaluate_failure_mode_rank_select_run.py`, `scripts/evaluate_failure_mode_joint_rank_run.py`
- Dataset builders: `scripts/build_failure_mode_evidence_dataset.py`, `scripts/build_failure_mode_contrast_dataset.py`, `scripts/build_failure_mode_contrast_v2_dataset.py`, `scripts/build_failure_mode_rank_select_dataset.py`, `scripts/build_failure_mode_rank_select_v2_dataset.py`, `scripts/build_failure_mode_joint_rank_v1_dataset.py`
- Experiment brief: `docs/first-artifact-card-experiment.md`
- Scaffold notes: `docs/artifact-card-failure-modes-evidence-v1-scaffold.md`, `docs/artifact-card-failure-modes-contrast-v1-scaffold.md`, `docs/artifact-card-failure-modes-rank-select-v1-scaffold.md`, `docs/artifact-card-failure-modes-rank-select-v2-scaffold.md`, `docs/artifact-card-failure-modes-joint-rank-v1-scaffold.md`
- Row counts: v1 = 20 train / 8 eval, v2 = 20 train / 8 eval, v3 = 26 train / 8 eval, failure-modes-v1 = 26 train / 8 eval, failure-modes-binary-v1 = 208 train / 64 eval, failure-modes-top2-v1 = 26 train / 8 eval, failure-modes-pairwise-v1 = 728 train / 224 eval, failure-modes-evidence-v1 = 208 train / 64 eval, failure-modes-contrast-v1 = 104 train / 32 eval, failure-modes-contrast-v2 = 128 train / 32 eval, failure-modes-rank-select-v1 = 208 train / 64 eval, failure-modes-rank-select-v2 = 272 train / 64 eval, failure-modes-joint-rank-v1 = 34 train / 8 eval

## Output schema
The model should return exactly one JSON object with these keys:
- `run_id`
- `dataset_name`
- `model_name`
- `verdict`
- `primary_failure_modes`
- `key_evidence`
- `next_action`

## Evaluation stance
Trust scored eval artifacts before train loss.

Important checks after each run:
- JSON validity rate
- exact-card match rate
- per-field accuracy
- which field fails most often
- whether remaining errors are formatting failures or labeling failures

## Why the tutor project is still useful
The earlier tutor adapter is still valuable as a negative result and debugging case study. It showed that repeated infra and wording fixes were not enough when the task itself was too broad for a tiny starter dataset. [[hermes-ai-lab-tutor-adapter]]

## First run status
- Diagnostic run `20260430T072526Z` completed successfully and saved artifacts under `/artifacts/artifact-card-v1/20260430T072526Z/`.
- Local copy of the summary was pulled to `tmp/modal-artifacts/artifact-card-v1-20260430T072526Z/run_summary.json`.
- The main gain was structural: `valid_json_rate` improved from `0.125` to `1.0`.
- The main remaining weakness was semantic normalization: `exact_card_match_rate` stayed at `0.0`, `verdict` reached only `0.375`, and `primary_failure_modes` / `key_evidence` / `next_action` stayed at `0.0` field accuracy.

## Second run status
- Dataset pass `artifact-card-v2` rewrote the task into constrained label-and-phrase selection while keeping the same JSON schema.
- Run `20260430T073913Z` completed successfully and saved artifacts under `/artifacts/artifact-card-v2/20260430T073913Z/`.
- Local copy of the summary was pulled to `tmp/modal-artifacts/artifact-card-v2-20260430T073913Z/run_summary.json`.
- The v2 run preserved the structure win and improved semantic fields substantially: `verdict` rose to `0.75`, `key_evidence` rose to `0.875`, `primary_failure_modes` reached `0.125`, and `next_action` reached `0.125`.
- `exact_card_match_rate` still stayed at `0.0`, so the remaining bottleneck is now concentrated in second-label selection and exact next-action selection.

## Third run status
- Dataset pass `artifact-card-v3` kept the v2 schema but added prompt-level selection hints plus 6 targeted contrast rows aimed at the exact v2 confusion patterns.
- Run `20260430T091500Z` completed successfully and saved artifacts under `/artifacts/artifact-card-v3/20260430T091500Z/`.
- Local copy of the summary was pulled to `tmp/modal-artifacts/artifact-card-v3-20260430T091500Z/run_summary.json`.
- The v3 run improved `next_action` from `0.125` to `0.5`, but `verdict` fell from `0.75` to `0.625`, `key_evidence` fell from `0.875` to `0.625`, and `primary_failure_modes` stayed at `0.125`.
- `exact_card_match_rate` still stayed at `0.0`, so the full-card task is now showing cross-field tradeoffs instead of clean monotonic improvement.

## First decomposed branch status
- Dataset pass `artifact-card-failure-modes-v1` kept the same underlying evidence as `artifact-card-v3` but narrowed the output to one strict JSON object containing only `primary_failure_modes`.
- The shared Modal entrypoint now supports dataset-level `task_config.json`, so narrower artifact-card subtasks can reuse the same training/eval pipeline.
- Run `20260430T094854Z` completed successfully and saved artifacts under `/artifacts/artifact-card-failure-modes-v1/20260430T094854Z/`.
- Local copy of the summary was pulled to `tmp/modal-artifacts/artifact-card-failure-modes-v1-20260430T094854Z/run_summary.json`.
- The decomposed branch kept `valid_json_rate` at `1.0` but still reached only `0.125` exact-match accuracy on `primary_failure_modes`, which means it did not beat either the base model or the best full-card field score.
- The tuned outputs collapsed repeatedly to `missing-required-detail` plus `phrase-copy-or-template-collapse`, so decomposition alone did not cleanly solve the label-selection problem.

## Second decomposed branch status
- Dataset pass `artifact-card-failure-modes-binary-v1` reframed the task into one-label-at-a-time binary judgments with output keys `candidate_label` and `belongs`.
- Run `20260430T104259Z` completed successfully and saved artifacts under `/artifacts/artifact-card-failure-modes-binary-v1/20260430T104259Z/`.
- Local copy of the summary was pulled to `tmp/modal-artifacts/artifact-card-failure-modes-binary-v1-20260430T104259Z/run_summary.json`.
- The binary framing produced a much stronger local training signal: tuned exact row match rose to `0.71875`, `candidate_label` accuracy reached `0.984375`, and `belongs` accuracy reached `0.734375`.
- But reconstructing the final top-2 failure-mode set from those 64 label judgments still gave `0.0` exact match across the original 8 eval cases.
- The tuned model over-selected `no-material-change` and completely missed positive `missing-required-detail` labels on the held-out split, so the remaining problem is now calibration and final selection structure.

## Third decomposed branch status
- Dataset pass `artifact-card-failure-modes-top2-v1` forced the final decision directly with output keys `first_label` and `second_label`.
- Run `20260430T122543Z` completed successfully and saved artifacts under `/artifacts/artifact-card-failure-modes-top2-v1/20260430T122543Z/`.
- Local copy of the summary was pulled to `tmp/modal-artifacts/artifact-card-failure-modes-top2-v1-20260430T122543Z/run_summary.json`.
- The branch kept valid JSON at `1.0`, but exact final-pair match still stayed at `0.0`.
- `first_label` accuracy stayed flat at `0.125` and `second_label` accuracy fell from `0.125` to `0.0`.
- The tuned model collapsed to `missing-required-detail` as the dominant first label on 7 of 8 eval rows, so a stronger final-decision prompt alone did not solve the calibration problem.

## Fourth decomposed branch status
- Dataset pass `artifact-card-failure-modes-pairwise-v1` expanded each original held-out case into pairwise comparisons across all 28 unordered label pairs.
- Run `20260430T125005Z` completed successfully and saved artifacts under `/artifacts/artifact-card-failure-modes-pairwise-v1/20260430T125005Z/`.
- Local copy of the summary was pulled to `tmp/modal-artifacts/artifact-card-failure-modes-pairwise-v1-20260430T125005Z/run_summary.json`.
- The tuned branch kept valid JSON at `1.0` and became the first comparison-style supervision format to recover any non-zero reconstructed held-out top-2 set match: `0.25`.
- But pairwise row accuracy itself was only `0.5580357142857143`, reconstructed ordered top-2 match stayed at `0.0`, and `missing-required-detail` still dominated pairwise win counts across most eval examples.

## Fifth decomposed branch scaffold
- Dataset scaffold `artifact-card-failure-modes-evidence-v1` now exists under `data/artifact-card-failure-modes-evidence-v1/`.
- It keeps the same 26 train / 8 eval source cases from `artifact-card-failure-modes-v1`, but expands them into 208 train / 64 eval one-label evidence judgments.
- Each row now predicts `candidate_label`, `supported`, and `evidence_key` instead of `preferred_label` or a bare binary `belongs` decision.
- The new prompts are much shorter than the pairwise branch: mean train input length is about `1085.0` chars here versus about `3086.8` in `artifact-card-failure-modes-pairwise-v1`.
- `scripts/build_failure_mode_evidence_dataset.py` regenerates the scaffold from the decomposed source dataset, and `scripts/evaluate_failure_mode_evidence_run.py` adds branch-specific reconstruction and per-label support metrics.
- The next run should test whether this shorter, evidence-anchored supervision beats the pairwise branch on reconstructed held-out positive-label set match.

## Fifth decomposed branch result
- Run `20260430T161302Z` completed successfully and saved artifacts under `/artifacts/artifact-card-failure-modes-evidence-v1/20260430T161302Z/`.
- Local copy of the summary was pulled to `tmp/modal-artifacts/artifact-card-failure-modes-evidence-v1-20260430T161302Z/run_summary.json`.
- The tuned branch improved row-level behavior: valid JSON reached `1.0`, exact row match reached `0.5`, `candidate_label` accuracy reached `0.984375`, `supported` accuracy reached `0.59375`, and `evidence_key` accuracy reached `0.671875`.
- But positive-only evidence-key accuracy stayed at `0.0625`, reconstructed exact positive-label set match stayed at `0.0`, and reconstructed top-2 set match also stayed at `0.0`.
- The new failure mode was broad over-acceptance: some held-out examples reconstructed 6 or 7 positive labels instead of the gold 2-label set.

## Sixth decomposed branch scaffold
- Dataset scaffold `artifact-card-failure-modes-contrast-v1` now exists under `data/artifact-card-failure-modes-contrast-v1/`.
- It keeps the same 26 train / 8 eval source cases from `artifact-card-failure-modes-v1`, but expands them into 104 train / 32 eval contrast-group judgments.
- Each row now predicts `contrast_group`, `decision`, and `evidence_key`, where `decision` is one of the local states `missing-required-detail`, the rival label, `both`, or `neither`.
- The branch only uses the four highest-value confusion groups: `missing-required-detail` vs `generic-explanation`, `no-material-change`, `hallucinated-detail`, and `overlap-contaminated-eval`.
- Mean train input length is about `1304.9` chars: longer than the broad evidence-v1 yes/no rows, but still far shorter than the full pairwise branch and much narrower in label-space pressure.
- `scripts/build_failure_mode_contrast_dataset.py` regenerates the scaffold from the decomposed source dataset, and `scripts/evaluate_failure_mode_contrast_run.py` scores both row-level behavior and reconstruction on the in-universe held-out subset.
- Reconstruction is intentionally scoped to the 4 held-out source cases whose gold label set stays inside the 5-label contrast universe.

## Current best interpretation
- `artifact-card-sft` remains the right first-project family because it yields sharp, scoreable failures.
- `artifact-card-v2` is still the strongest full-card baseline so far.
- `artifact-card-v3` is a useful negative result: extra full-card scaffolding improved one field while destabilizing others.
- `artifact-card-failure-modes-v1` is another useful negative result: removing the other card fields was not enough, by itself, to fix the weakest label-selection task.
- `artifact-card-failure-modes-binary-v1` is a useful mixed result: one-label binary supervision improved local judgment metrics strongly, but the final reconstructed label sets were still wrong.
- `artifact-card-failure-modes-top2-v1` is another useful negative result: directly forcing the final ranked pair still collapsed onto repeated default labels and did not improve held-out exact match.
- `artifact-card-failure-modes-pairwise-v1` is still the strongest downstream decomposition baseline because it reached reconstructed top-2 set match `0.25` on the full held-out split and `0.5` on the 4-case contrast-universe subset.
- `artifact-card-failure-modes-evidence-v1` is a useful negative result: shorter prompts and explicit evidence keys improved row behavior, but broad 8-label supervision still over-accepted too many labels and stayed at reconstructed top-2 set match `0.0`.
- `artifact-card-failure-modes-contrast-v1` is another useful negative result: it improved row structure again, but collapsed all 4 reconstructable held-out cases to singleton `missing-required-detail`, so reconstructed top-2 set match stayed at `0.0`.
- `artifact-card-failure-modes-contrast-v2` is now a second clean negative result for the narrow contrast path: the targeted 6-case patch preserved the same row metrics and the same `missing-required-detail` singleton collapse on all 4 reconstructable held-out cases.
- `artifact-card-failure-modes-rank-select-v1` is now another clean negative result: it improved row validity and rank-field accuracy, but downstream reconstruction still stayed at exact positive-set match `0.0`, top-2 set match `0.0`, and ordered top-2 match `0.0` on the full 8-example held-out split.
- `artifact-card-failure-modes-rank-select-v2` is now a second clean negative result for the rank-select family: schema leakage disappeared completely, but tuned row accuracy regressed and downstream reconstruction still stayed at exact positive-set match `0.0`, top-2 set match `0.0`, and ordered top-2 match `0.0`.

## Sixth decomposed branch result
- Run `20260430T164253Z` completed successfully and saved artifacts under `/artifacts/artifact-card-failure-modes-contrast-v1/20260430T164253Z/`.
- Local copy of the summary was pulled to `tmp/modal-artifacts/artifact-card-failure-modes-contrast-v1-20260430T164253Z/run_summary.json`.
- The tuned branch kept `valid_json_rate` at `1.0` and reached `0.5625` exact row match, with `contrast_group` accuracy `1.0`, `decision` accuracy `0.5625`, and `evidence_key` accuracy `0.5625`.
- But the downstream reconstruction still failed completely on the 4 in-universe held-out source cases: exact positive-set match `0.0`, top-2 set match `0.0`, and predicted positive-count histogram `{1: 4}`.
- The failure mode is now cleaner than in evidence-v1: instead of broad over-acceptance, the model underpredicted everything to a singleton `missing-required-detail` set on all reconstructable examples.
- The missed local states are now explicit and auditable: rival-only `generic-explanation`, rival-only `no-material-change`, rival-only `overlap-contaminated-eval`, plus several gold `both` states that all collapsed to the anchor label.

## Immediate next step
- Keep `artifact-card-v2` as the current baseline for the full-card task.
- Do not spend the next patch budget on more full-card prompt accretion.
- Do not assume simple output decomposition solves the remaining bottleneck.
- Do not assume row-level binary accuracy alone solves the final label-set task.
- Do not assume a stronger final-decision prompt alone solves the label-selection task either.
- Do not assume full 8-label pairwise expansion is enough by itself.
- Keep `artifact-card-failure-modes-pairwise-v1` as the strongest downstream decomposition baseline.
- Keep `artifact-card-failure-modes-evidence-v1`, `artifact-card-failure-modes-contrast-v1`, and `artifact-card-failure-modes-contrast-v2` as documented negative results, each revealing a different way that row-level gains can fail to transfer to reconstruction.
- The targeted-state patch did not improve downstream reconstruction at all: contrast-v2 stayed at exact positive-set match `0.0`, top-2 set match `0.0`, and singleton `missing-required-detail` predictions on all 4 reconstructable held-out source cases.
- The first rank-select run is now also documented as a negative result, not a success signal from row metrics.
- Its real failure pattern differs from contrast-v1/v2: instead of collapsing everything to one anchor label, it mostly underselected to zero positives, with one held-out example overselecting four positives.
- Keep `artifact-card-failure-modes-pairwise-v1` as the strongest downstream decomposition baseline until a later branch actually beats reconstructed top-2 set match `0.25`.
- The rank-select-v2 calibration patch fixed schema leakage completely, but it did not recover the core selector behavior: tuned reconstruction still stayed at exact positive-set match `0.0`, top-2 set match `0.0`, and ordered top-2 match `0.0`.
- The v2 failure mode became even more decisively underselective, with positive-count histogram `{0: 6, 1: 1, 2: 1}` and underselected rate `0.875`.
- `missing-required-detail` still failed to recover positive recall, while `phrase-copy-or-template-collapse` remained the main spurious surviving positive.
- Do not spend the next patch budget on more prompt-contract tuning inside the same independent per-label rank-select family.
- The next branch is now scaffolded as `artifact-card-failure-modes-joint-rank-v1`, which scores all candidate labels jointly inside one shared output object instead of one label at a time.
- Keep the first evaluation bar unchanged: a real success must beat `artifact-card-failure-modes-pairwise-v1` on reconstructed top-2 set match `0.25`.
- Continue judging every new branch by reconstruction before row metrics or loss.

## Related pages
- [[artifact-card-v1-vs-v2]]
- [[artifact-card-v2-vs-v3]]
- [[artifact-card-full-card-vs-failure-modes-branch]]
- [[artifact-card-failure-modes-v1-vs-binary-v1]]
- [[artifact-card-failure-modes-binary-v1-vs-top2-v1]]
- [[artifact-card-failure-modes-top2-v1-vs-pairwise-v1]]
- [[fine-tuning-lessons-from-first-project]]
- [[first-fine-tuning-project-options]]
