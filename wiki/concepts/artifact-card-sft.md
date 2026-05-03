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
- Forced-top-2 scaffold: `data/artifact-card-failure-modes-forced-top2-v2/`
- Forced-top-2 narrow semantic patch scaffold: `data/artifact-card-failure-modes-forced-top2-v2p2/`
- Forced-top-2 anti-fence scaffold: `data/artifact-card-failure-modes-forced-top2-v3/`
- Training entrypoint: `modal/train_unsloth_artifact_card.py`
- Dataset preview: `scripts/preview_dataset.py`
- Run scoring helpers: `scripts/evaluate_artifact_card_run.py`, `scripts/evaluate_failure_mode_evidence_run.py`, `scripts/evaluate_failure_mode_contrast_run.py`, `scripts/evaluate_failure_mode_rank_select_run.py`, `scripts/evaluate_failure_mode_joint_rank_run.py`, `scripts/evaluate_failure_mode_forced_top2_run.py`
- Dataset builders: `scripts/build_failure_mode_evidence_dataset.py`, `scripts/build_failure_mode_contrast_dataset.py`, `scripts/build_failure_mode_contrast_v2_dataset.py`, `scripts/build_failure_mode_rank_select_dataset.py`, `scripts/build_failure_mode_rank_select_v2_dataset.py`, `scripts/build_failure_mode_joint_rank_v1_dataset.py`, `scripts/build_failure_mode_forced_top2_v2_dataset.py`, `scripts/build_failure_mode_forced_top2_v2p2_dataset.py`, `scripts/build_failure_mode_forced_top2_v3_dataset.py`
- Experiment brief: `docs/first-artifact-card-experiment.md`
- Scaffold notes: `docs/artifact-card-failure-modes-evidence-v1-scaffold.md`, `docs/artifact-card-failure-modes-contrast-v1-scaffold.md`, `docs/artifact-card-failure-modes-rank-select-v1-scaffold.md`, `docs/artifact-card-failure-modes-rank-select-v2-scaffold.md`, `docs/artifact-card-failure-modes-joint-rank-v1-scaffold.md`, `docs/artifact-card-failure-modes-forced-top2-v2-scaffold.md`, `docs/artifact-card-failure-modes-forced-top2-v3-scaffold.md`
- Row counts: v1 = 20 train / 8 eval, v2 = 20 train / 8 eval, v3 = 26 train / 8 eval, failure-modes-v1 = 26 train / 8 eval, failure-modes-binary-v1 = 208 train / 64 eval, failure-modes-top2-v1 = 26 train / 8 eval, failure-modes-pairwise-v1 = 728 train / 224 eval, failure-modes-evidence-v1 = 208 train / 64 eval, failure-modes-contrast-v1 = 104 train / 32 eval, failure-modes-contrast-v2 = 128 train / 32 eval, failure-modes-rank-select-v1 = 208 train / 64 eval, failure-modes-rank-select-v2 = 272 train / 64 eval, failure-modes-joint-rank-v1 = 34 train / 8 eval, failure-modes-forced-top2-v2 = 34 train / 8 eval, failure-modes-forced-top2-v2p2 = 38 train / 8 eval, failure-modes-forced-top2-v3 = 34 train / 8 eval

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
- `artifact-card-failure-modes-joint-rank-v1` is now another clean negative result for the joint-selector idea: built-in auto-eval showed parseable JSON, but branch-specific evaluation found that all 8 tuned eval rows violated the exact-one-primary / exact-one-secondary contract and downstream reconstruction still stayed at `0.0` across every top-2 metric.

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
- `artifact-card-failure-modes-joint-rank-v1` also failed cleanly on the real run: tuned branch-specific `valid_json_rate` fell to `0.0` once the global two-slot constraint was enforced, and the model collapsed to all-`out` predictions on 7/8 eval rows plus one singleton `generic-explanation = secondary` row.
- Keep `artifact-card-failure-modes-pairwise-v1` as the strongest downstream baseline until a later branch actually beats reconstructed top-2 set match `0.25`.
- The main new lesson is that joint scoring by itself was not enough if the target still allowed an easy near-all-`out` escape hatch during generation.
- The next branch is now scaffolded as `artifact-card-failure-modes-forced-top2-v2`, documented in `../docs/artifact-card-failure-modes-forced-top2-v2-scaffold.md`.
- Its core change is to remove abstention states completely and predict only `{primary_label, primary_evidence_key, secondary_label, secondary_evidence_key}`.
- This is intentionally different from `top2-v1`: each chosen slot must now bind to a closed evidence key, so the model cannot satisfy the task with an unsupported default pair as easily.
- Local verification already passed: dataset build, preview, and a perfect-payload smoke evaluation all succeeded.
- The first real `forced-top2-v2` run then became the first decomposition branch to beat `pairwise-v1` downstream: tuned branch-specific `top2_set_match_rate` reached `0.375` and `top2_ordered_match_rate` reached `0.375` versus the old `0.25` / `0.0` pairwise baseline.
- Built-in auto-eval slightly overstated the row quality because it accepted one structurally wrong row where evidence-key names were copied into label slots; the branch-specific evaluator still showed a strong real gain with `valid_json_rate = 0.875`.
- The remaining bottleneck from the 1B run was a narrower repeated fallback pair: `missing-required-detail + generic-explanation`, especially on `fluency-without-correctness`, `hallucinated-detail`, and `wrong-causal-point` examples.
- The direct Qwen3 rerun on the same branch did not help: run `20260501T075313Z` dropped to tuned branch-specific `valid_json_rate = 0.375`, `top2_set_match_rate = 0.125`, and `top2_ordered_match_rate = 0.125`.
- The main Qwen3 failure mode was output-contract breakage rather than label collapse: 5/8 tuned rows wrapped the answer in Markdown code fences, which made them invalid for the strict raw-JSON task.
- Keep `artifact-card-failure-modes-forced-top2-v2` as the current strongest decomposition branch, but keep the 1B Llama run as the best actual result so far.
- The next patch should harden raw-JSON-only behavior on this branch before spending more budget on further model-family comparisons.
- That anti-fence patch is now scaffolded as `artifact-card-failure-modes-forced-top2-v3`, documented in `../docs/artifact-card-failure-modes-forced-top2-v3-scaffold.md`.
- `forced-top2-v3` keeps the same four-field no-abstention target, the same labels/evidence keys, and the same eval reconstruction metrics so the comparison stays apples-to-apples.
- Its main changes are contract hardening rather than semantic redesign: stronger raw-JSON-only instructions, an explicit "first character must be `{`" rule, a shorter `max_new_tokens = 48`, and a new `generation_prefix = "{"` hook in the training/inference pipeline.
- Local verification already passed for `forced-top2-v3`: compile, dataset build, preview, smoke evaluation, env check, and CLI verification all succeeded.
- The first real `forced-top2-v3` run removed the specific Qwen3 fence-wrapping failure mode, but it still regressed against the stronger `forced-top2-v2` 1B baseline: tuned branch-specific `valid_json_rate = 0.625`, `top2_set_match_rate = 0.125`, `top2_ordered_match_rate = 0.125`, `invalid_row_rate = 0.375`.
- The new failure mode was contract-compatible evidence mismatch rather than Markdown wrapping: 3/8 tuned rows paired `generic-explanation` with the wrong secondary evidence key (`missing-or-noncanonical-field`), so the branch-specific evaluator marked them `bad-secondary-evidence-key`.
- Decision: keep `artifact-card-failure-modes-forced-top2-v2` as the current strongest decomposition branch and treat `forced-top2-v3` as a useful negative result showing that heavy contract hardening can remove fence wrappers while still hurting the real downstream objective.
- If this family continues, the next patch should be narrower: start from the stronger `forced-top2-v2` prompt shape and add only minimal anti-fence pressure or targeted evidence-key compatibility cases instead of the larger `v3` rewrite.
- That narrower continuation is now scaffolded as `artifact-card-failure-modes-forced-top2-v2p1`, documented in `../docs/artifact-card-failure-modes-forced-top2-v2p1-scaffold.md`.
- `forced-top2-v2p1` preserves the original `forced-top2-v2` four-field target and the stronger `max_new_tokens = 64` setting, instead of reusing the heavier `v3` contract block.
- Its anti-fence additions are intentionally small: one no-fences reminder in the system prompt and instruction plus `generation_prefix = "{"` in task config.
- Its train-only patch is also narrower: 6 targeted compatibility cases aimed at the remaining `fluency-without-correctness`, `generic-explanation`, `wrong-causal-point`, `hallucinated-detail`, and `phrase-copy-or-template-collapse` confusions without rewriting the whole prompt contract.
- Local verification already passed for `forced-top2-v2p1`: compile, dataset build, preview, smoke evaluation, env check, and CLI verification all succeeded.
- Continue judging every new branch by reconstruction before row metrics or loss.
- As of 2026-05-01, the shared Modal training entrypoint now includes built-in task-aware forced-top-2 evaluation and strips `generation_prefix` from assistant targets during training so prefilled JSON prefixes stay train/infer consistent.
- The repo also now treats Karpathy-style persistent compiled notes as part of the optimization surface: important training conclusions should land in `docs/` and `wiki/`, not only in chat or raw artifacts.
- Verification run `20260501T111907Z` confirmed the new `task_aware_eval` path is wired into the shared training entrypoint: tuned branch-specific `valid_json_rate = 0.75`, `top2_set_match_rate = 0.125`, `top2_ordered_match_rate = 0.125`, and `invalid_row_rate = 0.25`.
- The new summary also made the remaining failure more explicit: the tuned model still overused `missing-required-detail + generic-explanation`, and two rows failed specifically because `generic-explanation` was paired with the illegal secondary evidence key `missing-or-noncanonical-field`.
- Kickoff autoresearch run `20260501T145949Z` rechecked the semantic anchor branch itself (`artifact-card-failure-modes-forced-top2-v2`) with the patched shared entrypoint rather than the narrower `v2p1` continuation.
- The rerun reconfirmed `forced-top2-v2` as the strongest current semantic baseline under built-in branch-aware scoring: tuned `valid_json_rate = 0.875`, `exact_row_match_rate = 0.375`, `top2_set_match_rate = 0.375`, `top2_ordered_match_rate = 0.375`, and `invalid_row_rate = 0.125`.
- The remaining errors stayed tightly concentrated instead of broad: 4 eval rows still collapsed to the fallback pair `missing-required-detail + generic-explanation`, and the only invalid tuned row copied evidence keys into label slots on the `overlap-contaminated-eval` example (`bad-primary-label`).
- That makes the next patch direction narrower than another prompt rewrite: prefer a small data-side compatibility fix aimed at the `fluency-without-correctness`, `hallucinated-detail`, and `wrong-causal-point` boundaries plus the overlap label-slot confusion.
- A later apples-to-apples forced-top-2 comparison also confirmed that neither follow-up contract branch beat the anchor: `forced-top2-v2p1` reached tuned branch-aware `valid_json_rate = 0.75`, `top2_set_match_rate = 0.125`, `top2_ordered_match_rate = 0.125`, and `invalid_row_rate = 0.25`, while `forced-top2-v3` reached `0.625`, `0.125`, `0.125`, and `0.375` respectively. [[artifact-card-forced-top2-v2-vs-v2p1-vs-v3]]
- The important learning rule from that comparison is that `generation_prefix = "{"` plus extra anti-fence language did not solve the real bottleneck; both branches still regressed toward the same `missing-required-detail + generic-explanation` fallback family.
- So the next bounded move should stay anchored on `forced-top2-v2` and patch the surviving semantic boundaries directly, not spend another pass on broader raw-JSON contract wording.
- A follow-up autoresearch measurement patch on 2026-05-01 hardened the shared trainer to summarize collapse concentration directly inside future forced-top-2 `task_aware_eval` blocks: it now records mismatch-only ordered-pair histograms, the most common wrong pair, its rate across mismatches, and a `selector_collapse_alert` flag when one repeated wrong pair dominates at least half of 3+ mismatches.
- That patch is intentionally measurement-first rather than another GPU rerun: the current repo already has enough evidence that `forced-top2-v2` is the semantic anchor and that `v2p1` / `v3` regress toward the same fallback family, so the next expensive run should only happen after a small data-side boundary patch is ready.
- The next bounded autoresearch pass created that data-side continuation as `artifact-card-failure-modes-forced-top2-v2p2` instead of spending Modal budget immediately.
- `v2p2` is intentionally narrow: it inherits every `forced-top2-v2` row unchanged and adds only 4 train-only semantic patch cases for the four surviving confusion boundaries from the anchor run: `fluency-without-correctness -> missing-required-detail`, `hallucinated-detail -> missing-required-detail`, `wrong-causal-point -> no-material-change`, and `overlap-contaminated-eval -> phrase-copy-or-template-collapse`.
- This keeps the stronger `v2` contract shape, avoids the broader anti-fence prompt mass from `v2p1` / `v3`, and gives the next capped rerun a cleaner test of whether selector-collapse concentration actually falls.
- The first real `v2p2` run (`20260501T184312Z`) is now another useful negative result rather than a new baseline.
- The branch-specific headline metrics were unchanged from the `forced-top2-v2` anchor despite the 4 train-only semantic patch rows: tuned `valid_json_rate = 0.875`, `exact_row_match_rate = 0.375`, `top2_set_match_rate = 0.375`, `top2_ordered_match_rate = 0.375`, and `invalid_row_rate = 0.125`.
- The new collapse metrics show the same selector bottleneck even more explicitly: `selector_collapse_alert = true`, `mismatch_rows = 5`, and 4 of those 5 mismatches (`0.8`) were still the fallback pair `missing-required-detail -> generic-explanation`.
- The surviving misses stayed on the same four semantic boundaries as the anchor (`fluency-without-correctness`, `hallucinated-detail`, `wrong-causal-point`, and the overlap label-slot confusion), which means the extra rows did not actually change the model's held-out decision behavior.
- Practical lesson: another tiny train-only patch inside the same direct forced-top-2 framing is now lower-value than a supervision redesign that makes the confused labels compete differently or binds the overlap case to label names more directly.

## Autoresearch loop operating status
- The repo now has a recurring local-delivery cron loop for bounded artifact-card autoresearch.
- The original gateway scheduler path was not reliably advancing due jobs in this profile, even when `hermes cron status` reported the gateway as running.
- The current repair is a local ticker loop at `scripts/cron_tick_loop.sh` that runs `hermes cron tick --accept-hooks` every 30 seconds. [[karpathy-llm-wiki-and-autoresearch-improvements-2026-05-01]]
- Real Modal launches from cron also required exporting the repo `.env` in the same shell as the command (`set -a && source .env && set +a`); a passing env-check alone was not enough.
- After that repair, the kickoff autoresearch run and the first recurring loop pass both executed successfully.

## Autoresearch documentation contract
- Every autoresearch pass must inspect `wiki/SCHEMA.md`, `wiki/index.md`, and the recent tail of `wiki/log.md` before changing anything.
- Every pass must append a chronological entry to `wiki/log.md`, even if it decides not to patch code or launch Modal.
- If a pass changes understanding, confirms a new result, or patches code, it must also update at least one durable wiki page such as this concept page or a dedicated comparison/query note.
- Documentation updates are required bookkeeping and do not replace the single primary experiment/patch budget for the pass.
- The current recurring loop should therefore leave evidence in three places whenever it makes progress: cron session logs, repo artifacts/docs, and the wiki.

## Related pages
- [[artifact-card-v1-vs-v2]]
- [[artifact-card-v2-vs-v3]]
- [[artifact-card-full-card-vs-failure-modes-branch]]
- [[artifact-card-failure-modes-v1-vs-binary-v1]]
- [[artifact-card-failure-modes-binary-v1-vs-top2-v1]]
- [[artifact-card-failure-modes-top2-v1-vs-pairwise-v1]]
- [[fine-tuning-lessons-from-first-project]]
- [[first-fine-tuning-project-options]]
- [[model-swap-qwen3-vs-gemma3-for-artifact-card-sft]]
