# Wiki Log

> Chronological record of wiki actions.

## [2026-04-28] create | ai-lab wiki initialized
- Domain: home AI lab learning and experiments
- Files created:
  - SCHEMA.md
  - index.md
  - log.md
  - entities/unsloth.md
  - concepts/ai-lab-learning-path.md
  - raw/articles/unsloth-docs-2026-04-28.md

## [2026-04-29] update | first unsloth experiment scaffold
- Files created:
  - concepts/hermes-ai-lab-tutor-adapter.md
- Files updated:
  - index.md
  - log.md

## [2026-04-29] update | first modal unsloth training run saved durable artifacts
- Files updated:
  - concepts/hermes-ai-lab-tutor-adapter.md
  - log.md
- Notes:
  - Fixed the Modal training entrypoint to match current TRL APIs.
  - Pinned the Modal image to Python 3.10, Torch 2.10.0, and xFormers 0.0.35 so Unsloth used xFormers correctly.
  - Successful run saved adapter artifacts into Modal volume `ai-lab-unsloth-artifacts` under `/artifacts/hermes-tutor-v1/20260429T093147Z/`.

## [2026-04-29] update | cleaned 40-row rerun documented from artifacts
- Files updated:
  - concepts/artifact-driven-experiment-debugging.md
  - concepts/hermes-ai-lab-tutor-adapter.md
  - log.md
- Notes:
  - Verified rerun `20260429T105620Z` from the saved Modal artifacts and pulled a local copy under `tmp/modal-artifacts/20260429T105620Z/`.
  - The cleaned 40-row dataset improved loss to `1.637732070684433` and recovered from the 46-row regression.
  - Artifact review still showed weak alignment on the same three eval concepts, so the next dataset pass should add stricter anchor wording rather than broad new rows.

## [2026-04-29] update | artifact-driven debugging notes and iteration history
- Files created:
  - concepts/artifact-driven-experiment-debugging.md
- Files updated:
  - concepts/hermes-ai-lab-tutor-adapter.md
  - index.md
  - log.md
- Notes:
  - Declared the Modal artifact volume and `run_summary.json` workflow as the default debugging surface for training runs.
  - Documented the key run sequence from the stable 40-row runs through the regressive 46-row run and the subsequent dataset cleanup.
  - Recorded the learning rule that experiment outcomes must include failure analysis, how regressions showed up, and how the next fix was chosen.

## [2026-04-29] update | second dataset pass and artifact inspection helpers
- Files updated:
  - concepts/hermes-ai-lab-tutor-adapter.md
  - log.md
- Files created:
  - scripts/list_modal_runs.py
  - scripts/show_modal_run_summary.py
- Notes:
  - Expanded the tutor dataset to 40 train rows after a second quality pass based on real base-vs-tuned outputs.
  - Added local helper scripts to inspect Modal run summaries stored in the artifact volume.
  - Latest successful run saved artifacts under `/artifacts/hermes-tutor-v1/20260429T094629Z/`.

## [2026-04-29] update | surgical 43-row patch documented from artifacts
- Files updated:
  - concepts/artifact-driven-experiment-debugging.md
  - concepts/hermes-ai-lab-tutor-adapter.md
  - log.md
- Notes:
  - Verified run `20260429T110801Z` from the saved Modal artifacts and pulled a local copy under `tmp/modal-artifacts/20260429T110801Z/`.
  - The 43-row surgical patch improved the instruct-model answer, but overall loss regressed to `1.6692575335502624` versus the cleaner 40-row recovery run.
  - Artifact review showed phrase-copy distortion on the smallest-useful-outcome answer and continued confusion on eval contamination, so the next fix should prefer rewriting overlapping rows over appending more near-duplicates.

## [2026-04-29] update | generalization cleanup rerun documented from artifacts
- Files updated:
  - concepts/artifact-driven-experiment-debugging.md
  - concepts/hermes-ai-lab-tutor-adapter.md
  - log.md
- Notes:
  - Verified run `20260429T112202Z` from the saved Modal artifacts and pulled a local copy under `tmp/modal-artifacts/20260429T112202Z/`.
  - Removed the 3 near-paraphrase training rows so the eval no longer depended on overlap-heavy prompt wording.
  - The rerun made the evaluation cleaner, but it also showed that the smallest-useful-outcome and eval-contamination concepts still need better canonical training examples.

## [2026-04-29] update | scenario-style rewrite rerun documented from artifacts
- Files updated:
  - concepts/hermes-ai-lab-tutor-adapter.md
  - log.md
- Notes:
  - Verified run `20260429T172803Z` from the saved Modal artifacts and pulled a local copy under `tmp/modal-artifacts/20260429T172803Z/`.
  - Rewrote 4 existing train rows into scenario-style prompts while keeping the dataset at 40 train / 10 eval.
  - The rerun increased loss to `1.6901863932609558` and showed that the scenario-style rewrite weakened canonical answers on all 3 tracked eval concepts.

## [2026-04-29] query | fresh root-cause review of no-improvement fine-tuning runs
- Files created:
  - queries/fine-tuning-no-improvement-root-cause-review.md
- Files updated:
  - index.md
  - log.md
- Notes:
  - Fresh review concluded that the main bottleneck is now objective-plus-dataset mismatch rather than infrastructure.
  - The current training script likely supervises the full rendered conversation instead of only assistant answers because `assistant_only_loss=True` is not set.
  - The 40-row dataset is over-scoped for its size, the 1B instruct base may be too weak for the desired precision, and the current `max_steps=60` implies about 12 epochs.
  - Detailed project note written to `docs/fine-tuning-no-improvement-root-cause-review-2026-04-29.md`.

## [2026-04-30] update | artifact-card first-project scaffold created
- Files created:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - ../data/artifact-card-v1/train.jsonl
  - ../data/artifact-card-v1/eval.jsonl
  - ../data/artifact-card-v1/README.md
  - ../scripts/preview_dataset.py
  - ../scripts/evaluate_artifact_card_run.py
  - ../modal/train_unsloth_artifact_card.py
- Files updated:
  - concepts/ai-lab-learning-path.md
  - concepts/hermes-ai-lab-tutor-adapter.md
  - index.md
  - log.md
- Notes:
  - Added the new active first-project concept page for `artifact-card-sft`.
  - Recorded the pivot from the broad tutor adapter to a stricter structured-output task.
  - Kept the tutor project as a documented negative result and debugging case study.

## [2026-04-30] update | comparison and lessons-learned pages added for the first fine-tuning project
- Files created:
  - comparisons/artifact-card-v1-vs-v2.md
  - queries/fine-tuning-lessons-from-first-project.md
- Files updated:
  - concepts/artifact-card-sft.md
  - index.md
  - log.md
- Notes:
  - Added a dedicated v1 vs v2 comparison page so the wiki preserves the actual run-to-run learning path rather than only the latest state.
  - Added a practical lessons-learned page that summarizes what the repo should retain from the tutor failure, the artifact-card-v1 structure win, and the artifact-card-v2 semantic improvements.
  - Recorded the central learning pattern: for tiny starter SFT, narrowing the task and canonicalizing labels helped much more than rerunning the same broad task or chasing train loss alone.
  - Kept the current open problem explicit: `exact_card_match_rate` is still `0.0`, with the remaining bottleneck concentrated in second-label selection and exact next-action selection.

## [2026-04-30] update | artifact-card-v2 tightened semantics and improved field accuracy
- Files created:
  - ../data/artifact-card-v2/train.jsonl
  - ../data/artifact-card-v2/eval.jsonl
  - ../data/artifact-card-v2/README.md
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Built `artifact-card-v2` by rewriting the task into constrained label-and-phrase selection with explicit allowed vocabularies while keeping the JSON schema fixed.
  - Run `20260430T073913Z` completed successfully on `artifact-card-v2` with `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/artifact-card-v2/20260430T073913Z/`.
  - Pulled a local copy of `run_summary.json` to `../tmp/modal-artifacts/artifact-card-v2-20260430T073913Z/run_summary.json` for artifact-first review.
  - Compared with the first `artifact-card-v1` run, tuned field accuracy improved from `0.375` to `0.75` on `verdict`, from `0.0` to `0.875` on `key_evidence`, and from `0.0` to `0.125` on both `primary_failure_modes` and `next_action`.
  - `exact_card_match_rate` still stayed at `0.0`, so the next patch should focus narrowly on second-label selection and exact next-action selection rather than broadening the task again.

## [2026-04-30] update | first artifact-card diagnostic run completed and reviewed
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Run `20260430T072526Z` completed successfully on `artifact-card-v1` with `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/artifact-card-v1/20260430T072526Z/`.
  - Pulled a local copy of `run_summary.json` to `../tmp/modal-artifacts/artifact-card-v1-20260430T072526Z/run_summary.json` for artifact-first review.
  - The run clearly improved structure (`valid_json_rate` `0.125` -> `1.0`) but not task semantics (`exact_card_match_rate` stayed `0.0`; only `verdict` reached `0.375`; the other semantic fields stayed `0.0`).
  - This confirms the new project is a better first fine-tuning target than the tutor task, but the next iteration should tighten canonical label vocabulary instead of chasing lower loss.

## [2026-04-30] update | artifact-card-v3 mixed run documented and decomposition branch identified
- Files created:
  - comparisons/artifact-card-v2-vs-v3.md
  - ../data/artifact-card-v3/train.jsonl
  - ../data/artifact-card-v3/eval.jsonl
  - ../data/artifact-card-v3/README.md
- Files updated:
  - concepts/artifact-card-sft.md
  - queries/fine-tuning-lessons-from-first-project.md
  - index.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Built `artifact-card-v3` by adding prompt-level selection hints and 6 targeted contrast rows aimed at the exact v2 confusion patterns.
  - Run `20260430T091500Z` completed successfully on `artifact-card-v3` with `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/artifact-card-v3/20260430T091500Z/`.
  - Pulled a local copy of `run_summary.json` to `../tmp/modal-artifacts/artifact-card-v3-20260430T091500Z/run_summary.json` for artifact-first review.
  - The patch improved `next_action` field accuracy from `0.125` to `0.5`, but regressed `verdict` from `0.75` to `0.625`, regressed `key_evidence` from `0.875` to `0.625`, left `primary_failure_modes` at `0.125`, and kept `exact_card_match_rate` at `0.0`.
  - Recorded the main learning rule: once the full-card task shows cross-field tradeoffs, the next disciplined branch should narrow by task decomposition rather than by stacking more full-card prompt scaffolding.

## [2026-04-30] update | primary-failure-modes decomposition branch documented
- Files created:
  - comparisons/artifact-card-full-card-vs-failure-modes-branch.md
  - ../data/artifact-card-failure-modes-v1/train.jsonl
  - ../data/artifact-card-failure-modes-v1/eval.jsonl
  - ../data/artifact-card-failure-modes-v1/README.md
  - ../data/artifact-card-failure-modes-v1/task_config.json
- Files updated:
  - ../modal/train_unsloth_artifact_card.py
  - ../scripts/evaluate_artifact_card_run.py
  - concepts/artifact-card-sft.md
  - queries/fine-tuning-lessons-from-first-project.md
  - index.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Extended the shared artifact-card Modal entrypoint and scoring helper so dataset-level `task_config.json` can define narrower subtasks while reusing the same training and artifact pipeline.
  - Built `artifact-card-failure-modes-v1` by reusing the v3 run evidence but narrowing the output to one strict JSON key: `primary_failure_modes`.
  - Run `20260430T094854Z` completed successfully on `artifact-card-failure-modes-v1` with `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/artifact-card-failure-modes-v1/20260430T094854Z/`.
  - Pulled a local copy of `run_summary.json` to `../tmp/modal-artifacts/artifact-card-failure-modes-v1-20260430T094854Z/run_summary.json` for artifact-first review.
  - The decomposed branch kept JSON validity at `1.0` but stayed at `0.125` exact-match accuracy on `primary_failure_modes`, matching the weak full-card field score instead of improving it.
  - The main new learning rule is that simple output decomposition is a good diagnostic move, but not a guaranteed fix; the next branch must likely redesign label supervision or evidence framing for this field itself.

## [2026-04-30] update | binary failure-mode branch documented after stronger local metrics
- Files created:
  - comparisons/artifact-card-failure-modes-v1-vs-binary-v1.md
  - ../data/artifact-card-failure-modes-binary-v1/train.jsonl
  - ../data/artifact-card-failure-modes-binary-v1/eval.jsonl
  - ../data/artifact-card-failure-modes-binary-v1/README.md
  - ../data/artifact-card-failure-modes-binary-v1/task_config.json
- Files updated:
  - ../scripts/evaluate_artifact_card_run.py
  - concepts/artifact-card-sft.md
  - queries/fine-tuning-lessons-from-first-project.md
  - index.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Built `artifact-card-failure-modes-binary-v1` by expanding each original example into one-label-at-a-time candidate-label judgments with output keys `candidate_label` and `belongs`.
  - Run `20260430T104259Z` completed successfully on `artifact-card-failure-modes-binary-v1` with `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/artifact-card-failure-modes-binary-v1/20260430T104259Z/`.
  - Pulled a local copy of `run_summary.json` to `../tmp/modal-artifacts/artifact-card-failure-modes-binary-v1-20260430T104259Z/run_summary.json` for artifact-first review.
  - The binary framing improved local metrics strongly: tuned exact row match reached `0.71875`, `candidate_label` accuracy reached `0.984375`, and `belongs` accuracy reached `0.734375`.
  - Reconstructing the original 2-label failure-mode sets from the binary judgments still failed on all 8 held-out cases (`0.0` exact set match), with over-selection of `no-material-change` and systematic misses on positive `missing-required-detail`.
  - Patched `scripts/evaluate_artifact_card_run.py` so dataset-level `task_config.list_fields=[]` is preserved correctly instead of silently falling back to the default full-card list fields.

## [2026-04-30] update | top-2 failure-mode branch documented as another negative result
- Files created:
  - comparisons/artifact-card-failure-modes-binary-v1-vs-top2-v1.md
  - ../data/artifact-card-failure-modes-top2-v1/train.jsonl
  - ../data/artifact-card-failure-modes-top2-v1/eval.jsonl
  - ../data/artifact-card-failure-modes-top2-v1/README.md
  - ../data/artifact-card-failure-modes-top2-v1/task_config.json
- Files updated:
  - concepts/artifact-card-sft.md
  - queries/fine-tuning-lessons-from-first-project.md
  - index.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Built `artifact-card-failure-modes-top2-v1` to force the final ranked decision directly with output keys `first_label` and `second_label`.
  - Run `20260430T122543Z` completed successfully on `artifact-card-failure-modes-top2-v1` with `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/artifact-card-failure-modes-top2-v1/20260430T122543Z/`.
  - Pulled a local copy of `run_summary.json` to `../tmp/modal-artifacts/artifact-card-failure-modes-top2-v1-20260430T122543Z/run_summary.json` for artifact-first review.
  - The branch kept valid JSON at `1.0` but exact final-pair match still stayed at `0.0`; `first_label` stayed at `0.125` accuracy and `second_label` fell to `0.0`.
  - The tuned model collapsed to `missing-required-detail` as `first_label` on 7 of 8 held-out rows, so a stronger final-decision prompt alone did not solve the label-selection problem.
  - The next recommended branch is now a true comparison structure such as pairwise label ranking or evidence-conditioned per-label scoring.

## [2026-04-30] update | pairwise failure-mode branch documented as a mixed result
- Files created:
  - comparisons/artifact-card-failure-modes-top2-v1-vs-pairwise-v1.md
  - ../data/artifact-card-failure-modes-pairwise-v1/train.jsonl
  - ../data/artifact-card-failure-modes-pairwise-v1/eval.jsonl
  - ../data/artifact-card-failure-modes-pairwise-v1/README.md
  - ../data/artifact-card-failure-modes-pairwise-v1/task_config.json
  - ../data/artifact-card-failure-modes-pairwise-v1/train_metadata.json
  - ../data/artifact-card-failure-modes-pairwise-v1/eval_metadata.json
- Files updated:
  - concepts/artifact-card-sft.md
  - queries/fine-tuning-lessons-from-first-project.md
  - index.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Built `artifact-card-failure-modes-pairwise-v1` by expanding each held-out case into all 28 unordered pairwise label comparisons and training the model to emit `preferred_label`.
  - Run `20260430T125005Z` completed successfully on `artifact-card-failure-modes-pairwise-v1` with `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/artifact-card-failure-modes-pairwise-v1/20260430T125005Z/`.
  - Pulled a local copy of `run_summary.json` to `../tmp/modal-artifacts/artifact-card-failure-modes-pairwise-v1-20260430T125005Z/run_summary.json` for artifact-first review.
  - The tuned branch kept valid JSON at `1.0`, reached `0.5580357142857143` exact pairwise row match, and improved reconstructed exact top-2 set match across the original 8 held-out cases from `0.0` to `0.25`.
  - Ordered reconstructed top-2 accuracy still stayed at `0.0`, and `missing-required-detail` remained the dominant default winner across most pairwise tournaments.

## [2026-04-30] update | first-project use-case comparison and recommendation
- Files created:
  - raw/articles/first-fine-tuning-use-case-research-2026-04-30.md
  - comparisons/first-fine-tuning-project-options.md
- Files updated:
  - concepts/hermes-ai-lab-tutor-adapter.md
  - index.md
  - log.md
- Notes:
  - Compared several better-scoped first fine-tuning project types after repeated tutor-adapter runs failed to produce stable qualitative gains.
  - Recommended `artifact-card-sft`, which converts run artifacts and operator notes into a strict experiment-card schema.
  - Chose it because it better matches small SFT strengths: format control, extraction, and easy automatic evaluation.

## [2026-04-29] update | assistant-only-loss trainer reset and narrower v2 dataset
- Files created:
  - data/hermes-tutor-v2/train.jsonl
  - data/hermes-tutor-v2/eval.jsonl
  - data/hermes-tutor-v2/README.md
- Files updated:
  - modal/train_unsloth_tutor.py
  - scripts/preview_tutor_dataset.py
  - docs/first-unsloth-experiment.md
  - concepts/hermes-ai-lab-tutor-adapter.md
  - queries/fine-tuning-no-improvement-root-cause-review.md
  - log.md
- Notes:
  - The training entrypoint now uses `assistant_only_loss=True`, saves `full_eval` artifacts, supports dataset selection, and defaults to a shorter 20-step diagnostic run.
  - A new `hermes-tutor-v2` dataset narrows the task to concise repo-specific beginner tutoring instead of broad ML term coverage.
  - Local verification passed: the patched Python files compiled and the preview script showed the new 20-train / 10-eval v2 dataset correctly.

## [2026-04-30] update | first v2 assistant-only-loss run launched and documented
- Files updated:
  - modal/train_unsloth_tutor.py
  - docs/first-unsloth-experiment.md
  - concepts/hermes-ai-lab-tutor-adapter.md
  - index.md
  - log.md
- Notes:
  - The first launch failed because TRL only recognizes conversational datasets when the message list lives under `messages`; using `conversations` caused `assistant_only_loss=True` to fail before training.
  - After fixing the key name, rerun `20260430T061418Z` completed successfully and saved durable artifacts under `/artifacts/hermes-tutor-v2/20260430T061418Z`.
  - The first narrow v2 run is now the new baseline for artifact review, but the tuned answers still drifted into generic or distorted explanations on the held-out prompts.

## [2026-04-30] update | sharpened canonical v2 training rows after first baseline review
- Files updated:
  - data/hermes-tutor-v2/train.jsonl
  - data/hermes-tutor-v2/README.md
  - concepts/hermes-ai-lab-tutor-adapter.md
  - log.md
- Notes:
  - Reviewed the full eval from run `20260430T061418Z` and found the biggest misses were still instruct-model priors, minimum-success workflow pieces, eval-contamination causality, and Modal's concrete role.
  - Rewrote existing v2 rows to restore sharper canonical wording on those concepts without broadening the dataset.
  - Re-verified the dataset preview and checked train/eval instruction similarity so the next rerun starts from a cleaner narrow-data baseline.

## [2026-04-30] update | sharpened v2 rerun confirmed wording-only patch was not enough
- Files updated:
  - docs/first-unsloth-experiment.md
  - concepts/hermes-ai-lab-tutor-adapter.md
  - log.md
- Notes:
  - Rerun `20260430T062717Z` completed successfully on the sharpened `hermes-tutor-v2` dataset and saved artifacts under `/artifacts/hermes-tutor-v2/20260430T062717Z`.
  - Train loss moved only slightly in the better direction (`3.0707270860672` -> `3.0663241863250734`), but the held-out answers did not materially improve on the tracked weak concepts.
  - The minimum-success answer stayed effectively unchanged, the eval-contamination answer stayed partial, and the instruct-model plus Modal-role answers remained distorted.
  - This is a useful negative result: the current bottleneck is now more plausibly 1B base-model capability or dataset structure, not launch infrastructure or one more wording-only rewrite.

## [2026-04-30] update | stronger 3B base improved fluency more than correctness
- Files updated:
  - docs/first-unsloth-experiment.md
  - concepts/hermes-ai-lab-tutor-adapter.md
  - log.md
- Notes:
  - Run `20260430T063654Z` completed successfully on `hermes-tutor-v2` with `unsloth/Llama-3.2-3B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/hermes-tutor-v2/20260430T063654Z`.
  - This kept dataset, trainer settings, and `max_steps=20` fixed, so the main comparison axis was base-model strength.
  - Train loss improved more clearly (`3.0663241863250734` -> `2.9948059558868407`), but the held-out answers still missed the same repo-specific target concepts.
  - The 3B run produced more fluent outputs, but not meaningfully more correct ones; that points more strongly to dataset structure and target-answer design as the next bottleneck.

## [2026-04-30] query | fresh fine-tuning improvement strategy pass
- Files created:
  - queries/fine-tuning-improvement-strategies-2026-04-30.md
  - ../docs/fine-tuning-improvement-strategies-2026-04-30.md
- Files updated:
  - index.md
  - log.md
- Notes:
  - Reviewed the current tutor and artifact-card history, the strongest full-card baseline, and the latest pairwise branch to decide what should improve next.
  - Fresh local analysis showed the largest current confusions collapse into `missing-required-detail`, especially against `generic-explanation`, `no-material-change`, `hallucinated-detail`, and `overlap-contaminated-eval`.
  - Measured prompt length across branches and found the later decomposition tasks had grown very verbose, which likely dilutes the evidence signal.
  - Recommended the next branch as evidence-conditioned per-label scoring with confusion-targeted contrast data, shorter prompts, and delayed recombination into the full-card task.

## [2026-04-30] update | evidence-conditioned failure-mode branch scaffolded
- Files created:
  - ../data/artifact-card-failure-modes-evidence-v1/train.jsonl
  - ../data/artifact-card-failure-modes-evidence-v1/eval.jsonl
  - ../data/artifact-card-failure-modes-evidence-v1/README.md
  - ../data/artifact-card-failure-modes-evidence-v1/task_config.json
  - ../data/artifact-card-failure-modes-evidence-v1/train_metadata.json
  - ../data/artifact-card-failure-modes-evidence-v1/eval_metadata.json
  - ../scripts/build_failure_mode_evidence_dataset.py
  - ../scripts/evaluate_failure_mode_evidence_run.py
  - ../docs/artifact-card-failure-modes-evidence-v1-scaffold.md
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Turned the strategy memo into a runnable next branch centered on one-label evidence-conditioned support judgments with output keys `candidate_label`, `supported`, and `evidence_key`.
  - Regenerated the dataset from `artifact-card-failure-modes-v1`, keeping the same 26 train / 8 eval source cases but expanding them into 208 train / 64 eval candidate-label rows.
  - Shortened the supervision prompts substantially: mean train input length is about `1085.0` chars here versus about `3086.8` in the pairwise branch.
  - Added a branch-specific evaluation helper that reports per-label support precision/recall, positive-only evidence-key accuracy, and reconstructed positive-label set match on the original held-out cases.
  - Smoke-tested the new evaluator on a mock perfect-summary payload before handing the branch off for the first real training run.

## [2026-04-30] update | contrast-group failure-mode branch scaffolded
- Files created:
  - ../data/artifact-card-failure-modes-contrast-v1/train.jsonl
  - ../data/artifact-card-failure-modes-contrast-v1/eval.jsonl
  - ../data/artifact-card-failure-modes-contrast-v1/README.md
  - ../data/artifact-card-failure-modes-contrast-v1/task_config.json
  - ../data/artifact-card-failure-modes-contrast-v1/train_metadata.json
  - ../data/artifact-card-failure-modes-contrast-v1/eval_metadata.json
  - ../scripts/build_failure_mode_contrast_dataset.py
  - ../scripts/evaluate_failure_mode_contrast_run.py
  - ../docs/artifact-card-failure-modes-contrast-v1-scaffold.md
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Turned the post-evidence recommendation into a runnable narrow branch centered on exactly four `missing-required-detail` confusion groups.
  - Regenerated the dataset from `artifact-card-failure-modes-v1`, keeping the same 26 train / 8 eval source cases but expanding them into 104 train / 32 eval contrast-group rows.
  - Each row now returns `contrast_group`, `decision`, and `evidence_key`, where `decision` is one of the local states anchor label, rival label, `both`, or `neither`.
  - Reconstruction is intentionally limited to the 10 train / 4 eval source cases whose gold label set stays inside the 5-label contrast universe.
  - Prompt mass stayed far below the pairwise branch while remaining more structured than evidence-v1: mean train input length is about `1304.9` chars here versus about `3086.8` in pairwise-v1 and about `1085.0` in evidence-v1.
  - Verified the scaffold with dataset preview plus a perfect-payload smoke test for `scripts/evaluate_failure_mode_contrast_run.py`, which returned perfect row-level and reconstruction metrics on the generated eval rows.

## [2026-04-30] update | evidence-conditioned failure-mode run completed and reviewed
- Files created:
  - ../docs/artifact-card-failure-modes-evidence-v1-run-2026-04-30.md
  - ../tmp/modal-artifacts/artifact-card-failure-modes-evidence-v1-20260430T161302Z/run_summary.json
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Run `20260430T161302Z` completed successfully on `artifact-card-failure-modes-evidence-v1` with `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/artifact-card-failure-modes-evidence-v1/20260430T161302Z/`.
  - Pulled a local copy of `run_summary.json` to `../tmp/modal-artifacts/artifact-card-failure-modes-evidence-v1-20260430T161302Z/run_summary.json` for artifact-first review.
  - The tuned branch improved local row behavior (`valid_json_rate=1.0`, exact row match `0.5`, `candidate_label` accuracy `0.984375`) but did not improve the real downstream task.
  - Branch-specific evaluation showed `positive_evidence_key_accuracy=0.0625`, reconstructed exact positive-label set match `0.0`, and reconstructed top-2 set match `0.0`.
  - The main new learning rule is that broad 8-label evidence-conditioned expansion still over-asks the model; the next branch should narrow to the hardest confusion-targeted contrast groups instead of keeping full-label expansion.

## [2026-04-30] update | contrast-group failure-mode run completed and reviewed
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Files created:
  - ../tmp/modal-artifacts/artifact-card-failure-modes-contrast-v1-20260430T164253Z/run_summary.json
- Notes:
  - Run `20260430T164253Z` completed successfully on `artifact-card-failure-modes-contrast-v1` with `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/artifact-card-failure-modes-contrast-v1/20260430T164253Z/`.
  - Pulled a local copy of `run_summary.json` to `../tmp/modal-artifacts/artifact-card-failure-modes-contrast-v1-20260430T164253Z/run_summary.json` for artifact-first review.
  - The tuned branch improved row structure again (`valid_json_rate=1.0`, exact row match `0.5625`, `contrast_group` accuracy `1.0`) but still failed the real downstream reconstruction objective.
  - Branch-specific evaluation showed exact positive-set match `0.0`, reconstructed top-2 set match `0.0`, and predicted positive-count histogram `{1: 4}` on the 4 reconstructable held-out source cases.
  - The key new learning rule is that the narrow contrast branch overcorrected into anchor-label collapse: every reconstructable eval case reduced to singleton `missing-required-detail`, so the next move should target the missing rival-only and `both` states before trying a more complex selector.

## [2026-04-30] update | contrast-group failure-mode v2 scaffold patched with targeted states
- Files created:
  - ../data/artifact-card-failure-modes-contrast-v2/README.md
  - ../data/artifact-card-failure-modes-contrast-v2/supplemental_train_cases.json
  - ../data/artifact-card-failure-modes-contrast-v2/task_config.json
  - ../data/artifact-card-failure-modes-contrast-v2/train.jsonl
  - ../data/artifact-card-failure-modes-contrast-v2/eval.jsonl
  - ../data/artifact-card-failure-modes-contrast-v2/train_metadata.json
  - ../data/artifact-card-failure-modes-contrast-v2/eval_metadata.json
  - ../scripts/build_failure_mode_contrast_v2_dataset.py
  - ../tmp/modal-artifacts/artifact-card-failure-modes-contrast-v2-smoke-run_summary.json
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Built `artifact-card-failure-modes-contrast-v2` as a minimal patch over contrast-v1 instead of broadening the architecture immediately.
  - Added exactly 6 train-only source cases covering the missing rival-only and `both` states exposed by contrast-v1: rival-only `generic-explanation`, rival-only `no-material-change`, rival-only `overlap-contaminated-eval`, plus `both` in the `generic-explanation`, `no-material-change`, and `hallucinated-detail` groups.
  - The eval split stayed unchanged, so the next run can be compared directly against contrast-v1 on the same 4 reconstructable held-out source cases.
  - Dataset shape is now 32 train / 8 eval source examples, expanded to 128 train / 32 eval contrast rows; reconstructable source examples are 13 train / 4 eval.
  - Mean train prompt length stayed effectively flat at about `1306.2` chars versus about `1304.9` in contrast-v1, so the patch adds state coverage without materially increasing prompt mass.
  - Verified the scaffold with `scripts/preview_dataset.py artifact-card-failure-modes-contrast-v2` plus a perfect-payload smoke test through `scripts/evaluate_failure_mode_contrast_run.py`, which returned perfect row-level and reconstruction metrics on the unchanged eval split.
  - Recommended next run command: `set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-contrast-v2 --max-steps 20`

## [2026-04-30] update | contrast-group failure-mode v2 run completed and reviewed
- Files created:
  - ../tmp/modal-artifacts/artifact-card-failure-modes-contrast-v2-20260430T170129Z/run_summary.json
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Run `20260430T170129Z` completed successfully on `artifact-card-failure-modes-contrast-v2` with `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/artifact-card-failure-modes-contrast-v2/20260430T170129Z/`.
  - Pulled a local copy of `run_summary.json` to `../tmp/modal-artifacts/artifact-card-failure-modes-contrast-v2-20260430T170129Z/run_summary.json` for artifact-first review.
  - The targeted 6-case patch did not improve the main downstream objective: tuned reconstruction stayed at exact positive-set match `0.0`, reconstructed top-2 set match `0.0`, and predicted positive-count histogram `{1: 4}` on the 4 reconstructable held-out source cases.
  - Row structure also effectively plateaued: `valid_json_rate=1.0`, exact row match `0.5625`, `contrast_group` accuracy `1.0`, `decision` accuracy `0.5625`, and only a slight `evidence_key` bump to `0.59375`.
  - The failure pattern remained the same as contrast-v1: all reconstructable eval cases still collapsed to singleton `missing-required-detail`, including the targeted rival-only and `both` states.
  - This rules out the narrow missing-state patch as a sufficient fix and makes the next branch decision cleaner: stop patching the contrast branch and move to a two-stage rank-then-select design while keeping `artifact-card-failure-modes-pairwise-v1` as the strongest downstream baseline.

## [2026-04-30] update | two-stage rank-then-select scaffold created for failure-mode selection
- Files created:
  - ../data/artifact-card-failure-modes-rank-select-v1/README.md
  - ../data/artifact-card-failure-modes-rank-select-v1/task_config.json
  - ../data/artifact-card-failure-modes-rank-select-v1/train.jsonl
  - ../data/artifact-card-failure-modes-rank-select-v1/eval.jsonl
  - ../data/artifact-card-failure-modes-rank-select-v1/train_metadata.json
  - ../data/artifact-card-failure-modes-rank-select-v1/eval_metadata.json
  - ../scripts/build_failure_mode_rank_select_dataset.py
  - ../scripts/evaluate_failure_mode_rank_select_run.py
  - ../docs/artifact-card-failure-modes-rank-select-v1-scaffold.md
  - ../tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v1-smoke-run_summary.json
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Built `artifact-card-failure-modes-rank-select-v1` as the next branch after the clean contrast-v2 negative result.
  - The new scaffold keeps one-label-at-a-time prompts but replaces flat support judgments with explicit `primary` / `secondary` / `out` rank supervision.
  - The branch-specific evaluator reconstructs the final ordered top 2 by mapping `primary -> 2`, `secondary -> 1`, and `out -> 0`, then selecting the highest-scoring labels.
  - Dataset shape is 26 train / 8 eval source examples expanded to 208 train / 64 eval rank rows, with mean train input length about `1289.0` chars.
  - Verified the scaffold with Python syntax checks, dataset generation, dataset preview, and a perfect-payload smoke test through `scripts/evaluate_failure_mode_rank_select_run.py`, which returned `1.0` row metrics and `1.0` reconstruction metrics on the eval split.
  - Recommended next run command: `set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-rank-select-v1 --max-steps 20`

## [2026-04-30] update | first rank-select run completed and reviewed
- Files created:
  - ../tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v1-20260430T182335Z/run_summary.json
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Run `20260430T182335Z` completed successfully on `artifact-card-failure-modes-rank-select-v1` with `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/artifact-card-failure-modes-rank-select-v1/20260430T182335Z/`.
  - Pulled a local copy of `run_summary.json` to `../tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v1-20260430T182335Z/run_summary.json` for artifact-first review.
  - Tuned row behavior improved sharply over the base model: `valid_json_rate=0.984375`, exact row match `0.65625`, `candidate_label` accuracy `0.984375`, `support_rank` accuracy `0.703125`, and `evidence_key` accuracy `0.6875`.
  - But the downstream objective still failed completely: branch-specific evaluation kept exact positive-set match `0.0`, top-2 set match `0.0`, and ordered top-2 match `0.0` on the full 8-example held-out split.
  - The failure pattern shifted away from contrast-style anchor collapse into mixed calibration failure: 5 held-out source examples underselected to zero positives, 2 selected exactly 2 positives but still chose the wrong pair, and 1 example overselected 4 positives.
  - `artifact-card-failure-modes-pairwise-v1` therefore remains the strongest downstream decomposition baseline, and the next patch should target rank calibration plus schema leakage rather than rerunning the same scaffold unchanged.

## [2026-05-01] update | rank-select-v2 calibration patch run completed and reviewed
- Files created:
  - ../tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v2-20260501T052544Z/run_summary.json
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Run `20260501T052544Z` completed successfully on `artifact-card-failure-modes-rank-select-v2` with `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` and saved artifacts under `/artifacts/artifact-card-failure-modes-rank-select-v2/20260501T052544Z/`.
  - Pulled a local copy of `run_summary.json` to `../tmp/modal-artifacts/artifact-card-failure-modes-rank-select-v2-20260501T052544Z/run_summary.json` for artifact-first review.
  - The schema-hardening patch succeeded on its narrow target: tuned `valid_json_rate` reached `1.0` with no invalid rows and no copied prompt-tail leakage.
  - But the core task regressed relative to rank-select-v1: exact row match fell to `0.359375`, `support_rank` accuracy to `0.359375`, and `evidence_key` accuracy to `0.46875`.
  - Downstream reconstruction still failed completely on the full 8-example held-out split: exact positive-set match `0.0`, top-2 set match `0.0`, and ordered top-2 match `0.0`.
  - The failure mode became even more decisively underselective than rank-select-v1, with tuned positive-count histogram `{0: 6, 1: 1, 2: 1}` and underselected rate `0.875`.
  - The intended calibration fix did not land: `missing-required-detail` positive recall stayed at `0.0`, while `phrase-copy-or-template-collapse` remained the main surviving false-positive label.
  - Decision: keep the schema-cleanup change as a useful diagnostic lesson, but stop spending patch budget on the same independent per-label rank-select family and test a joint selector next while keeping `artifact-card-failure-modes-pairwise-v1` as the strongest downstream baseline.

## [2026-05-01] update | joint-rank-v1 selector branch scaffolded
- Files created:
  - ../data/artifact-card-failure-modes-joint-rank-v1/train.jsonl
  - ../data/artifact-card-failure-modes-joint-rank-v1/eval.jsonl
  - ../data/artifact-card-failure-modes-joint-rank-v1/train_metadata.json
  - ../data/artifact-card-failure-modes-joint-rank-v1/eval_metadata.json
  - ../data/artifact-card-failure-modes-joint-rank-v1/task_config.json
  - ../data/artifact-card-failure-modes-joint-rank-v1/README.md
  - ../scripts/build_failure_mode_joint_rank_v1_dataset.py
  - ../scripts/evaluate_failure_mode_joint_rank_run.py
  - ../docs/artifact-card-failure-modes-joint-rank-v1-scaffold.md
  - ../tmp/modal-artifacts/artifact-card-failure-modes-joint-rank-v1-smoke-run_summary.json
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - New branch: `artifact-card-failure-modes-joint-rank-v1` scores all 8 labels jointly in one strict JSON object instead of one candidate label per row.
  - The scaffold reuses the 8 train-only supplemental source cases from `rank-select-v2`, but compresses each source example back to one row with fixed label keys and `primary|secondary|out` values.
  - Local verification passed: dataset build, preview, and a synthetic perfect-payload smoke test through `scripts/evaluate_failure_mode_joint_rank_run.py` all succeeded.
  - The first real success criterion is unchanged: the branch only counts as progress if reconstructed top-2 set match beats the current `pairwise-v1` baseline of `0.25`.

## [2026-05-01] update | joint-rank-v1 first run completed and reviewed
- Files created:
  - ../tmp/modal-artifacts/artifact-card-failure-modes-joint-rank-v1-20260501T064308Z/run_summary.json
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - ../docs/artifact-card-failure-modes-joint-rank-v1-scaffold.md
  - log.md
- Notes:
  - Run `20260501T064308Z` completed successfully on Modal and saved artifacts under `/artifacts/artifact-card-failure-modes-joint-rank-v1/20260501T064308Z/`.
  - Raw `run_summary.json` auto-eval was misleading: it reported tuned `valid_json_rate = 1.0` because the outputs were parseable JSON with the expected keys.
  - Branch-specific evaluation showed the real selector failure: all 8 tuned eval rows violated the required `exactly one primary + exactly one secondary` contract.
  - Tuned downstream reconstruction stayed at exact positive-set match `0.0`, top-2 set match `0.0`, and ordered top-2 match `0.0`, so `artifact-card-failure-modes-pairwise-v1` remains the strongest downstream baseline.
  - Failure pattern: 7/8 eval rows predicted all labels as `out`, and the remaining row emitted only `generic-explanation = secondary`, so the joint branch still collapsed to near-zero positive allocation.
  - Decision: treat `joint-rank-v1` as another clean negative result and move the next redesign toward a target that removes the all-`out` escape hatch, likely a direct `{primary_label, secondary_label}` object or a staged shortlist selector.

## [2026-05-01] query | qwen3 vs gemma3 model swap and post-joint-rank branch design
- Files created:
  - queries/model-swap-qwen3-vs-gemma3-for-artifact-card-sft.md
  - ../docs/model-swap-qwen3-vs-gemma3-2026-05-01.md
  - ../docs/artifact-card-failure-modes-forced-top2-v2-proposal.md
- Files updated:
  - index.md
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - log.md
- Notes:
  - Researched the latest practical Qwen and Gemma replacement paths for the artifact-card SFT loop and filed the result into the wiki and repo docs.
  - Best immediate replacement candidate is `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit` with chat template `qwen3` because it is a recent text-generation CausalLM and a clean fit for the current Unsloth text-only training path.
  - Best low-risk Gemma comparison is `unsloth/gemma-3-1b-it-bnb-4bit` with chat template `gemma-3`; `gemma-3-4b-it` is a weaker first fit because HF metadata marks it as multimodal `Gemma3ForConditionalGeneration`.
  - Designed the next post-joint-rank branch as `artifact-card-failure-modes-forced-top2-v2`: a no-abstention direct top-2 target with evidence-bound slots `{primary_label, primary_evidence_key, secondary_label, secondary_evidence_key}`.
  - Rationale: keep the target close to the downstream object, remove the all-`out` escape hatch completely, and improve over `top2-v1` by forcing each chosen slot to bind to explicit evidence.
  - If `forced-top2-v2` still fails, the next redesign should become a staged shortlist / tournament selector.

## [2026-05-01] update | forced-top2-v2 scaffold implemented and locally verified
- Files created:
  - ../docs/artifact-card-failure-modes-forced-top2-v2-scaffold.md
  - ../scripts/build_failure_mode_forced_top2_v2_dataset.py
  - ../scripts/evaluate_failure_mode_forced_top2_run.py
  - ../data/artifact-card-failure-modes-forced-top2-v2/README.md
  - ../data/artifact-card-failure-modes-forced-top2-v2/train.jsonl
  - ../data/artifact-card-failure-modes-forced-top2-v2/eval.jsonl
  - ../data/artifact-card-failure-modes-forced-top2-v2/train_metadata.json
  - ../data/artifact-card-failure-modes-forced-top2-v2/eval_metadata.json
  - ../data/artifact-card-failure-modes-forced-top2-v2/task_config.json
  - ../tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v2-smoke-run_summary.json
- Files updated:
  - concepts/artifact-card-sft.md
  - ../docs/first-artifact-card-experiment.md
  - ../docs/artifact-card-failure-modes-forced-top2-v2-proposal.md
  - log.md
- Notes:
  - Implemented the no-abstention forced-top-2 branch as `artifact-card-failure-modes-forced-top2-v2`.
  - The builder converts each source example into one strict four-field target: `primary_label`, `primary_evidence_key`, `secondary_label`, `secondary_evidence_key`.
  - The evaluator enforces distinct ranked labels plus label-compatible evidence keys and reports downstream set/order recovery along with evidence-key accuracy.
  - Local verification passed end to end: compile, dataset build, preview, and perfect-payload smoke evaluation.
  - The branch is ready for the first real Modal run on the current 1B Llama baseline.

## [2026-05-01] update | forced-top2-v2 first run beat the pairwise baseline
- Files created:
  - ../tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v2-20260501T074237Z/run_summary.json
- Files updated:
  - ../docs/artifact-card-failure-modes-forced-top2-v2-scaffold.md
  - ../docs/first-artifact-card-experiment.md
  - concepts/artifact-card-sft.md
  - log.md
- Notes:
  - Reviewed the first real `artifact-card-failure-modes-forced-top2-v2` run from Modal artifacts with the branch-specific evaluator.
  - Run `20260501T074237Z` on `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` reached tuned branch-specific `top2_set_match_rate = 0.375` and `top2_ordered_match_rate = 0.375`.
  - That beats the old downstream best from `artifact-card-failure-modes-pairwise-v1` (`0.25` set match, `0.0` ordered match), making `forced-top2-v2` the strongest decomposition branch so far.
  - The main remaining issue is a repeated fallback pair of `missing-required-detail + generic-explanation`, plus one structural confusion where evidence-key names were emitted in label slots.
  - Next clean comparison: rerun the exact same branch on `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit` before spending more patch budget on data changes.

## [2026-05-01] update | forced-top2-v2 Qwen3 comparison regressed on strict JSON compliance
- Files created:
  - ../tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v2-20260501T075313Z/run_summary.json
- Files updated:
  - ../docs/artifact-card-failure-modes-forced-top2-v2-scaffold.md
  - ../docs/first-artifact-card-experiment.md
  - concepts/artifact-card-sft.md
  - log.md
- Notes:
  - Reviewed the direct Qwen3 rerun of `artifact-card-failure-modes-forced-top2-v2` with the branch-specific evaluator.
  - Run `20260501T075313Z` on `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit` looked cheaper by train loss (`1.7252290666103363` vs `1.8952500939369201`) but was materially worse on the task.
  - Tuned branch-specific metrics fell to `valid_json_rate = 0.375`, `top2_set_match_rate = 0.125`, `top2_ordered_match_rate = 0.125`, and `invalid_row_rate = 0.625`.
  - The main regression was output-contract failure rather than a repeated fallback label pair: 5/8 tuned rows wrapped the answer in Markdown code fences instead of returning raw JSON only.
  - Decision: keep the 1B Llama `forced-top2-v2` run as the best current result, and spend the next patch budget on anti-fence / raw-JSON-only hardening before running more model-family comparisons.

## [2026-05-01] update | forced-top2-v3 anti-fence patch scaffolded and locally verified
- Files created:
  - ../docs/artifact-card-failure-modes-forced-top2-v3-scaffold.md
  - ../data/artifact-card-failure-modes-forced-top2-v3/README.md
  - ../data/artifact-card-failure-modes-forced-top2-v3/train.jsonl
  - ../data/artifact-card-failure-modes-forced-top2-v3/eval.jsonl
  - ../data/artifact-card-failure-modes-forced-top2-v3/train_metadata.json
  - ../data/artifact-card-failure-modes-forced-top2-v3/eval_metadata.json
  - ../data/artifact-card-failure-modes-forced-top2-v3/task_config.json
  - ../tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v3-smoke-run_summary.json
  - ../scripts/build_failure_mode_forced_top2_v3_dataset.py
- Files updated:
  - ../modal/train_unsloth_artifact_card.py
  - ../docs/first-artifact-card-experiment.md
  - concepts/artifact-card-sft.md
  - log.md
- Notes:
  - Scaffolded `artifact-card-failure-modes-forced-top2-v3` as a narrow contract-hardening patch on top of the strongest current branch design.
  - Kept the same no-abstention four-field target and the same source/eval semantics so comparisons remain apples-to-apples with `forced-top2-v2`.
  - Hardened the prompt contract against Markdown fences by explicitly requiring raw JSON only, explicitly banning ```json wrappers, and adding a rule that the first answer character must be `{`.
  - Added generic pipeline support for `generation_prefix` in `modal/train_unsloth_artifact_card.py`; `forced-top2-v3` sets it to `{` so generation starts inside the JSON object.
  - Tightened the response budget with `max_new_tokens = 48` and completed local verification: compile, dataset build, preview, smoke evaluation, env check, and CLI verification.

## [2026-05-01] update | forced-top2-v3 anti-fence run removed fences but regressed downstream
- Files created:
  - ../tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v3-20260501T085312Z/run_summary.json
- Files updated:
  - ../docs/artifact-card-failure-modes-forced-top2-v3-scaffold.md
  - ../docs/first-artifact-card-experiment.md
  - concepts/artifact-card-sft.md
  - log.md
- Notes:
  - Reviewed the first real `artifact-card-failure-modes-forced-top2-v3` run from Modal artifacts with the branch-specific evaluator.
  - Run `20260501T085312Z` on `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` did remove the specific fenced-JSON failure mode seen in the Qwen3 rerun, but it still regressed on the real task.
  - Tuned branch-specific metrics reached only `valid_json_rate = 0.625`, `top2_set_match_rate = 0.125`, `top2_ordered_match_rate = 0.125`, and `invalid_row_rate = 0.375`.
  - That is better than the `forced-top2-v2` Qwen3 rerun on raw validity (`0.375`) but worse than the stronger `forced-top2-v2` 1B baseline (`0.875`, `0.375`, `0.375`, `0.125`).
  - The new main failure mode was evidence-key/label incompatibility rather than Markdown wrapping: 3/8 tuned rows paired `generic-explanation` with `missing-or-noncanonical-field`, which the evaluator marked as `bad-secondary-evidence-key`.
  - Decision: keep `forced-top2-v2` as the strongest current branch, and if this family continues, patch more narrowly from the `v2` prompt shape instead of continuing the heavier `v3` contract rewrite.

## [2026-05-01] update | forced-top2-v2p1 narrow continuation scaffolded and locally verified
- Files created:
  - ../docs/artifact-card-failure-modes-forced-top2-v2p1-scaffold.md
  - ../data/artifact-card-failure-modes-forced-top2-v2p1/README.md
  - ../data/artifact-card-failure-modes-forced-top2-v2p1/train.jsonl
  - ../data/artifact-card-failure-modes-forced-top2-v2p1/eval.jsonl
  - ../data/artifact-card-failure-modes-forced-top2-v2p1/train_metadata.json
  - ../data/artifact-card-failure-modes-forced-top2-v2p1/eval_metadata.json
  - ../data/artifact-card-failure-modes-forced-top2-v2p1/task_config.json
  - ../data/artifact-card-failure-modes-forced-top2-v2p1/supplemental_train_cases.json
  - ../tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v2p1-smoke-run_summary.json
  - ../scripts/build_failure_mode_forced_top2_v2p1_dataset.py
- Files updated:
  - ../docs/first-artifact-card-experiment.md
  - concepts/artifact-card-sft.md
  - log.md
- Notes:
  - Scaffolded `artifact-card-failure-modes-forced-top2-v2p1` as the narrower continuation after `forced-top2-v3` regressed.
  - Preserved the stronger `forced-top2-v2` branch shape: same four-field target and `max_new_tokens = 64`.
  - Added only light anti-fence pressure: one no-fences reminder in the system prompt and instruction plus `generation_prefix = "{"` in task config.
  - Added 6 targeted train-only compatibility cases focused on the real remaining confusion patterns instead of reusing the heavier `v3` contract rewrite.
  - Local verification passed: compile, dataset build, preview, smoke evaluation, env check, and CLI verification.


## [2026-05-01] query | Karpathy LLM Wiki pattern and autoresearch improvements
- Sources captured:
  - raw/articles/karpathy-llm-wiki-2026-05-01.md
- Files created:
  - ../docs/autoresearch-karpathy-and-training-patch-2026-05-01.md
  - queries/karpathy-llm-wiki-and-autoresearch-improvements-2026-05-01.md
- Files updated:
  - concepts/artifact-card-sft.md
  - index.md
  - log.md
- Notes:
  - Re-read Andrej Karpathy's original `LLM Wiki` pattern and extracted the parts most relevant to ai-lab's local `autoresearch` workflow.
  - Patched `modal/train_unsloth_artifact_card.py` so `generation_prefix` prefill is train/infer consistent and forced-top-2 runs now emit built-in `task_aware_eval`.
  - Updated the local `autoresearch` skill so future passes preserve persistent compiled notes instead of leaving expensive conclusions only in chat.

## [2026-05-01] update | verified built-in forced-top-2 task-aware evaluation on a live Modal run
- Files updated:
  - concepts/artifact-card-sft.md
  - log.md
- Notes:
  - Ran `artifact-card-failure-modes-forced-top2-v2p1` again after patching the shared training entrypoint.
  - Verification run `20260501T111907Z` emitted `task_aware_eval` directly in the training result, confirming the new evaluator path works end-to-end.
  - The run also showed that better measurement did not automatically improve behavior: tuned branch-aware `valid_json_rate = 0.75`, `top2_set_match_rate = 0.125`, `top2_ordered_match_rate = 0.125`, `invalid_row_rate = 0.25`, with two rows still failing on illegal `generic-explanation` secondary evidence keys.

## [2026-05-01] update | kickoff autoresearch reran forced-top2-v2 as the semantic anchor
- Files updated:
  - concepts/artifact-card-sft.md
  - log.md
- Notes:
  - Preflight passed: `python3 scripts/check_env.py` confirmed required env vars, and `modal run modal/train_unsloth_artifact_card.py --help` verified the Modal entrypoint.
  - Ran exactly one capped Modal experiment: `artifact-card-failure-modes-forced-top2-v2` with `max_steps = 20`, producing run `20260501T145949Z` under `/artifacts/artifact-card-failure-modes-forced-top2-v2/20260501T145949Z/`.
  - The rerun reconfirmed `forced-top2-v2` as the strongest current semantic baseline under built-in branch-aware scoring: tuned `valid_json_rate = 0.875`, `top2_set_match_rate = 0.375`, `top2_ordered_match_rate = 0.375`, and `invalid_row_rate = 0.125`.
  - The remaining errors stayed concentrated in the same fallback pair `missing-required-detail + generic-explanation`, with one additional invalid overlap example that copied evidence keys into label slots.

## [2026-05-01] update | autoresearch cron repair and wiki documentation contract
- Files updated:
  - concepts/artifact-card-sft.md
  - queries/karpathy-llm-wiki-and-autoresearch-improvements-2026-05-01.md
  - log.md
- Notes:
  - Recorded that the practical scheduler repair for this profile is `scripts/cron_tick_loop.sh`, which drives `hermes cron tick --accept-hooks` every 30 seconds from the repo workdir.
  - Recorded that real Modal launches from cron need `.env` exported in the launch shell, not only a passing env-check script.
  - Tightened the expected autoresearch documentation contract: every pass should append to `wiki/log.md`, and any pass that changes understanding or code should also update at least one durable wiki page.

## [2026-05-01] update | forced-top2 branch-aware comparison preserved the semantic anchor
- Files created:
  - comparisons/artifact-card-forced-top2-v2-vs-v2p1-vs-v3.md
- Files updated:
  - concepts/artifact-card-sft.md
  - index.md
  - log.md
- Notes:
  - Inspected the required autoresearch surface in order: `wiki/SCHEMA.md`, `wiki/index.md`, recent `wiki/log.md`, `docs/autoresearch-artifact-card-playbook.md`, `docs/autoresearch-karpathy-and-training-patch-2026-05-01.md`, `wiki/concepts/artifact-card-sft.md`, `modal/train_unsloth_artifact_card.py`, both forced-top-2 `task_config.json` files, the latest local forced-top-2 run summaries, and `git status`.
  - Also pulled the latest real Modal summaries for `artifact-card-failure-modes-forced-top2-v2` run `20260501T145949Z` and `artifact-card-failure-modes-forced-top2-v2p1` run `20260501T111907Z` from the artifact volume, then re-ran the local forced-top-2 evaluator on `forced-top2-v3` so the three branches could be compared on the same branch-aware scoreboard.
  - Decision: no code patch and no new Modal launch this pass. The highest-value bounded increment was a durable comparison note because the evidence already shows the selector bottleneck clearly and there is uncommitted local training/wiki work that should not be overwritten blindly.
  - Preserved the main result explicitly: `forced-top2-v2` remains the strongest semantic anchor (`valid_json_rate = 0.875`, `top2_set_match_rate = 0.375`, `top2_ordered_match_rate = 0.375`), while `v2p1` (`0.75`, `0.125`, `0.125`) and `v3` (`0.625`, `0.125`, `0.125`) are useful negative results about contract pressure that did not fix fallback collapse.
  - Exact next step: start from `artifact-card-failure-modes-forced-top2-v2` and add one small train-only semantic patch for `fluency-without-correctness`, `hallucinated-detail`, `wrong-causal-point`, and the overlap label-slot confusion instead of spending the next pass on more anti-fence wording.

## [2026-05-01] update | measurement hardening patch for forced-top-2 selector collapse
- Files updated:
  - ../modal/train_unsloth_artifact_card.py
  - concepts/artifact-card-sft.md
  - log.md
- Notes:
  - Inspected the required autoresearch surface in order: `wiki/SCHEMA.md`, `wiki/index.md`, recent `wiki/log.md`, `docs/autoresearch-artifact-card-playbook.md`, `docs/autoresearch-karpathy-and-training-patch-2026-05-01.md`, `wiki/concepts/artifact-card-sft.md`, `modal/train_unsloth_artifact_card.py`, both forced-top-2 `task_config.json` files, the latest present local forced-top-2 run summaries, and `git status`.
  - Reviewed the strongest available local summaries again: `forced-top2-v2` remains the semantic anchor, while `v2p1` and `v3` both regress toward the same fallback family rather than revealing a new formatting bottleneck worth another immediate GPU run.
  - Decision: no Modal launch this pass. The highest-value bounded increment was a small measurement patch because the repo already has enough evidence that selector collapse, not raw JSON formatting alone, is the live bottleneck.
  - Patched `modal/train_unsloth_artifact_card.py` so future forced-top-2 `task_aware_eval` blocks also emit mismatch-only ordered-pair histograms, `most_common_mismatch_ordered_pair`, `most_common_mismatch_ordered_pair_rate`, `mismatch_rows`, and a boolean `selector_collapse_alert` when one wrong pair dominates at least half of 3+ mismatches.
  - Local verification passed: `python3 -m py_compile modal/train_unsloth_artifact_card.py`.
  - Exact next step: create one small train-only semantic patch on top of `artifact-card-failure-modes-forced-top2-v2`, then use the new collapse metrics on the next capped rerun to verify whether fallback-pair concentration actually falls.

## [2026-05-01] update | forced-top2-v2p2 semantic patch scaffold
- Files created:
  - ../data/artifact-card-failure-modes-forced-top2-v2p2/README.md
  - ../data/artifact-card-failure-modes-forced-top2-v2p2/task_config.json
  - ../data/artifact-card-failure-modes-forced-top2-v2p2/train.jsonl
  - ../data/artifact-card-failure-modes-forced-top2-v2p2/eval.jsonl
  - ../data/artifact-card-failure-modes-forced-top2-v2p2/train_metadata.json
  - ../data/artifact-card-failure-modes-forced-top2-v2p2/eval_metadata.json
  - ../data/artifact-card-failure-modes-forced-top2-v2p2/supplemental_train_cases.json
  - ../scripts/build_failure_mode_forced_top2_v2p2_dataset.py
- Files updated:
  - concepts/artifact-card-sft.md
  - log.md
- Notes:
  - Inspected the required autoresearch surface in order: `wiki/SCHEMA.md`, `wiki/index.md`, recent `wiki/log.md`, `docs/autoresearch-artifact-card-playbook.md`, `docs/autoresearch-karpathy-and-training-patch-2026-05-01.md`, `wiki/concepts/artifact-card-sft.md`, `modal/train_unsloth_artifact_card.py`, `data/artifact-card-failure-modes-forced-top2-v2/task_config.json`, `data/artifact-card-failure-modes-forced-top2-v2p1/task_config.json`, the latest relevant forced-top-2 run summaries (including the current volume-backed `forced-top2-v2`, `v2p1`, and `v3` results), and `git status`.
  - Evidence used for the decision: `forced-top2-v2` remains the semantic anchor at tuned branch-aware `valid_json_rate = 0.875`, `top2_set_match_rate = 0.375`, `top2_ordered_match_rate = 0.375`, with the remaining misses concentrated in the same fallback pair; `v2p1` and `v3` both regress to `0.125` / `0.125` on top-2 recovery while adding more contract pressure.
  - Decision: no Modal launch this pass. The highest-value bounded increment was the planned train-only semantic patch because the bottleneck is still selector collapse, not missing measurement or a lack of anti-fence wording.
  - Built `artifact-card-failure-modes-forced-top2-v2p2` as a narrow continuation of `forced-top2-v2`: it inherits the anchor dataset unchanged and adds only 4 train-only cases for `fluency-without-correctness -> missing-required-detail`, `hallucinated-detail -> missing-required-detail`, `wrong-causal-point -> no-material-change`, and `overlap-contaminated-eval -> phrase-copy-or-template-collapse`.
  - Local verification passed: `python3 scripts/build_failure_mode_forced_top2_v2p2_dataset.py` and `python3 scripts/preview_dataset.py artifact-card-failure-modes-forced-top2-v2p2` produced a clean 38-train / 8-eval scaffold with valid JSON targets.
  - Exact next step: if preflight passes, run one capped Modal experiment on `artifact-card-failure-modes-forced-top2-v2p2` with `--max-steps 20` and judge it first by branch-aware `top2_set_match_rate`, `top2_ordered_match_rate`, `selector_collapse_alert`, and the mismatch ordered-pair histogram versus the `forced-top2-v2` anchor.

## [2026-05-01] update | forced-top2-v2p2 capped rerun preserved the same collapse pattern
- Files created:
  - ../tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v2p2-20260501T184312Z/run_summary.json
- Files updated:
  - concepts/artifact-card-sft.md
  - log.md
- Notes:
  - Inspected the required autoresearch surface in order: `wiki/SCHEMA.md`, `wiki/index.md`, recent `wiki/log.md`, `docs/autoresearch-artifact-card-playbook.md`, `docs/autoresearch-karpathy-and-training-patch-2026-05-01.md`, `wiki/concepts/artifact-card-sft.md`, `modal/train_unsloth_artifact_card.py`, `data/artifact-card-failure-modes-forced-top2-v2/task_config.json`, `data/artifact-card-failure-modes-forced-top2-v2p1/task_config.json`, the latest relevant forced-top-2 run summaries for `v2`, `v2p1`, and `v3`, and `git status`.
  - Modal preflight passed exactly as required: `source .venv/bin/activate && python3 scripts/check_env.py` and `source .venv/bin/activate && set -a && source .env && set +a && modal run modal/train_unsloth_artifact_card.py --help` both succeeded.
  - Ran one capped Modal experiment: `source .venv/bin/activate && set -a && source .env && set +a && modal run modal/train_unsloth_artifact_card.py --dataset-name artifact-card-failure-modes-forced-top2-v2p2 --max-steps 20`, producing run `20260501T184312Z` under `/artifacts/artifact-card-failure-modes-forced-top2-v2p2/20260501T184312Z/`.
  - Result: `v2p2` did not beat the `forced-top2-v2` anchor. Tuned branch-aware metrics stayed exactly flat at `valid_json_rate = 0.875`, `exact_row_match_rate = 0.375`, `top2_set_match_rate = 0.375`, `top2_ordered_match_rate = 0.375`, and `invalid_row_rate = 0.125`.
  - The new measurement fields confirm the same selector-collapse bottleneck: `selector_collapse_alert = true`, `mismatch_rows = 5`, and `most_common_mismatch_ordered_pair = missing-required-detail -> generic-explanation` with rate `0.8` across mismatches.
  - The train-only patch also failed to fix the overlap label-slot confusion: one held-out row still copied evidence-key names into label slots (`bad-primary-label`) instead of emitting `overlap-contaminated-eval` plus `phrase-copy-or-template-collapse`.
  - Decision: preserve `forced-top2-v2` as the semantic anchor and keep `v2p2` as a useful negative result showing that a 4-row semantic supplement inside the same direct forced-top-2 framing was too weak to move held-out behavior.
  - Exact next step: stop stacking tiny direct-prompt patches on top of `forced-top2-v2`; the next bounded branch should redesign supervision for the surviving confused labels so they compete differently, especially the repeated `missing-required-detail` vs `generic-explanation` fallback and the overlap label-slot namespace confusion.

## [2026-05-03] query | bruxism EEG/EMG starter project research
- Files created:
  - queries/bruxism-eeg-emg-starter-project-2026-05-03.md
  - raw/articles/cap-sleep-database-physionet-2012.md
  - raw/articles/bruxism-single-channel-eeg-2024.md
  - raw/articles/bruxism-multimodal-ensemble-2024.md
  - raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md
  - raw/articles/sleep-bruxism-emg-only-setups-2020.md
  - raw/articles/advanced-sensing-system-sleep-bruxism-emg-2024.md
- Files updated:
  - index.md
  - log.md
- Notes:
  - Compared open-data starter options for bruxism detection from EEG/EMG signals.
  - Chose a CAP Sleep Database pilot as the simplest reproducible first project because it is public and already used by recent bruxism classification papers.
  - Explicitly recorded that high published accuracies come from tiny cohorts and should be treated as reproduction baselines rather than clinical evidence.

## [2026-05-03] update | bruxism-cap starter scaffold created
- Files created:
  - ../projects/bruxism-cap/README.md
  - ../projects/bruxism-cap/data/README.md
  - ../projects/bruxism-cap/data/subject_manifest.example.csv
  - ../projects/bruxism-cap/notebooks/00_cap_subset_inspection.ipynb
  - ../projects/bruxism-cap/reports/first-baseline.md
  - ../projects/bruxism-cap/src/features.py
  - ../projects/bruxism-cap/src/prepare_windows.py
  - ../projects/bruxism-cap/src/train_baseline.py
  - ../projects/bruxism-cap/src/eval.py
  - ../docs/plans/2026-05-03-bruxism-cap-scaffold.md
- Files updated:
  - ../README.md
  - ../pyproject.toml
  - queries/bruxism-eeg-emg-starter-project-2026-05-03.md
  - log.md
- Notes:
  - Added a minimal public-data starter project under `projects/bruxism-cap/` for CAP-based EEG/EMG bruxism experiments.
  - Kept the first baseline explicitly classical and leakage-aware, with random-window versus leave-one-subject-out evaluation.
  - Added an optional `biosignals` dependency group so EDF loading stays isolated from the core Unsloth/Modal workflow.
