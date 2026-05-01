# First Unsloth Experiment

Date: 2026-04-29

## Goal

Turn the reading plan into the first concrete project artifact set.

Update on 2026-04-30:
- the original tutor-adapter track remains documented here as a useful negative result and debugging case study
- the new recommended first success-oriented project is now `artifact-card-sft`
- see `docs/first-artifact-card-experiment.md` for the active pivot scaffold

The original default project in this file was:
- `Hermes AI lab tutor adapter`

This project fine-tunes a small instruct model to explain ML and fine-tuning concepts in a concise, beginner-friendly way.

## Why this is the right next step

It matches the current repo state:
- the learning path is documented
- a Modal smoke-test file already exists
- the VPS is good for data prep and orchestration
- the first missing pieces were a small dataset, an experiment brief, and a GPU-run scaffold

It also matches the Unsloth beginner guidance already captured in this repo:
- start small
- prefer an instruct model for tiny datasets
- complete one end-to-end supervised fine-tuning cycle before doing anything ambitious

## Current chosen default model target

Recommended first remote target:
- `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`

Why this default:
- it is a small instruct model
- it matches the current small-dataset strategy
- it keeps the first GPU run focused on workflow validation rather than scale

## Artifacts created for this step

- `data/hermes-tutor-v1/train.jsonl`
- `data/hermes-tutor-v1/eval.jsonl`
- `data/hermes-tutor-v1/README.md`
- `scripts/preview_tutor_dataset.py`
- `modal/train_unsloth_tutor.py`
- `scripts/list_modal_runs.py`
- `scripts/show_modal_run_summary.py`
- `docs/first-artifact-card-experiment.md`
- `data/artifact-card-v1/train.jsonl`
- `data/artifact-card-v1/eval.jsonl`
- `data/artifact-card-v1/README.md`
- `scripts/preview_dataset.py`
- `scripts/evaluate_artifact_card_run.py`
- `modal/train_unsloth_artifact_card.py`

## Current dataset status

- train rows: 40
- eval rows: 10
- format: JSONL with `instruction`, `input`, `output`
- current stance: prefer a cleaner, tighter 40-row set over blindly expanding the dataset

## Modal artifacts are part of the debugging loop

The persistent Modal volume is not just storage. It is the main debugging surface for this project.

Primary artifact store:
- volume: `ai-lab-unsloth-artifacts`

Primary evidence to inspect after every run:
- `run_summary.json`
- `sample_eval` inside the run summary
- adapter files under `adapter/`
- metrics such as runtime, steps, and train loss

Working rule for this repo:
- every important dataset pass should be followed by a run review grounded in the saved artifacts
- every important run should be documented with what changed, what failed or improved, and what to try next

Useful commands:

```bash
source .venv/bin/activate && python scripts/list_modal_runs.py
source .venv/bin/activate && python scripts/show_modal_run_summary.py latest
mkdir -p tmp/modal-artifacts/<run_id>
set -a && source .env && set +a && source .venv/bin/activate && modal volume get ai-lab-unsloth-artifacts /hermes-tutor-v1/<run_id> tmp/modal-artifacts/<run_id>
```

## Current status

Completed by 2026-04-30:
- HF read-token auth is configured and working again from the repo `.env`.
- Modal smoke test passed.
- The training script now saves artifacts to a persistent Modal volume.
- The Modal image was pinned to a compatible Python/Torch/xFormers stack, so Unsloth used xFormers instead of falling back to plain PyTorch attention.
- The repository is connected to GitHub and the work has been pushed to `origin/main`.
- The v2 diagnostic run launched successfully after fixing the conversational dataset key needed by `assistant_only_loss=True`.

## Iteration log

### Iteration 1: initial successful durable run
- run_id: `20260429T093147Z`
- dataset: 36 train / 10 eval
- result: successful end-to-end run with durable saved artifacts
- takeaway: pipeline worked; this validated Modal, artifact saving, and the first real SFT loop

### Iteration 2: second dataset pass and stable 40-row runs
- run_ids:
  - `20260429T094629Z`
  - `20260429T101846Z`
  - `20260429T101953Z`
- dataset: 40 train / 10 eval
- result: reproducible runs with the same loss and very similar sample eval behavior
- takeaway: repeated identical runs showed the infrastructure was stable and the dataset had become the bottleneck

### Iteration 3: targeted 46-row patch that regressed quality
- run_id: `20260429T103541Z`
- dataset: 46 train / 10 eval
- result: successful infrastructure run, worse learning run
- train loss: `1.6949759691953659`
- how the failure showed up:
  - the instruct-model eval answer drifted away from instruction-following and talked about reusing the dataset
  - the “smallest useful outcome” eval answer became vague and incorrect
  - the eval-contamination answer became confused about evaluation flow instead of focusing on memorization and generalization
- likely cause:
  - the added rows overlapped with the weak eval themes, but their wording was not strict enough
  - several answers became too abstract and reflective instead of tutor-like and concrete
- fix applied:
  - downloaded the latest artifacts locally
  - inspected `run_summary.json`
  - removed the 6 regressive added rows
  - rewrote 9 existing rows to be shorter, stricter, and more directly aligned with the target tutor style
  - reset the dataset to a cleaner 40-row version

### Iteration 4: cleaned 40-row rerun after artifact-driven cleanup
- run_id: `20260429T105620Z`
- dataset: 40 train / 10 eval
- result: the cleanup improved loss versus the earlier 40-row runs and clearly recovered from the bad 46-row run, but the weak eval concepts are still not solved
- train loss: `1.637732070684433`
- artifact dir: `/artifacts/hermes-tutor-v1/20260429T105620Z`
- local artifact copy: `tmp/modal-artifacts/20260429T105620Z/`
- how it improved:
  - loss improved over the stable earlier 40-row runs (`1.6594930599133173`) and over the bad 46-row run (`1.6949759691953659`)
  - the run no longer produced the confused, highly regressed outputs seen in the 46-row run
  - this supports the decision to trust artifact review and prefer a tighter core dataset over loose targeted expansion
- what still looks weak in `sample_eval`:
  - the instruct-model answer still talks about fine-tuning convenience instead of already knowing instruction-following
  - the “smallest useful outcome” answer is still abstract and does not name the mini workflow directly
  - the eval-contamination answer is still muddled and does not clearly say memorization breaks valid generalization testing
- takeaway:
  - the cleanup helped recover direction, but the dataset still needs sharper anchor examples for the three weakest eval concepts

### Iteration 5: surgical 3-row anchor patch on the weak eval concepts
- run_id: `20260429T110801Z`
- dataset: 43 train / 10 eval
- result: mixed at best; one weak concept improved, but overall loss regressed and two outputs still showed distortion
- train loss: `1.6692575335502624`
- artifact dir: `/artifacts/hermes-tutor-v1/20260429T110801Z`
- local artifact copy: `tmp/modal-artifacts/20260429T110801Z/`
- what changed:
  - added 3 narrowly targeted rows aimed only at the weak eval concepts
  - tightened several overlapping training answers to use more exact anchor wording
- how it showed up in `sample_eval`:
  - the instruct-model answer improved and finally mentioned the key idea that the model already knows instruction-following
  - the “smallest useful outcome” answer partly copied the target structure but distorted it into `a saved adapter, and a saved adapter saved to a repo`
  - the eval-contamination answer stayed muddled and still failed to say clearly that memorization breaks valid generalization testing
- takeaway:
  - adding a few targeted rows was not enough by itself
  - near-duplicate anchor rows can increase phrase copying without fully fixing the concept
  - the next cleanup should rewrite overlapping rows more aggressively instead of just appending new ones

### Iteration 6: generalization cleanup after the overlap-heavy 43-row patch
- run_id: `20260429T112202Z`
- dataset: 40 train / 10 eval
- result: cleaner from an evaluation-leakage perspective, but still not a quality win overall
- train loss: `1.668097026149432`
- artifact dir: `/artifacts/hermes-tutor-v1/20260429T112202Z`
- local artifact copy: `tmp/modal-artifacts/20260429T112202Z/`
- what changed:
  - removed the 3 near-paraphrase train rows that were too close to the held-out eval prompts
  - rewrote the overlapping training rows to teach the same concepts through different task framing
  - re-checked train/eval overlap before rerunning to keep the eval focused on generalization instead of prompt reuse
- how it showed up in `sample_eval`:
  - the instruct-model answer still moved in the right direction and now does so without relying on a near-duplicate train prompt
  - the “smallest useful outcome” answer collapsed into an overly generic line about saving memory and keeping the workflow clean
  - the eval-contamination answer remained confused and still failed to state the key chain clearly: eval reuse -> memorization -> invalid generalization test
- takeaway:
  - this was the proper cleanup to make the evaluation more trustworthy
  - however, removing leakage-like overlap also exposed that the dataset still does not teach two of the weak concepts well enough
  - the next fix should improve canonical training examples, not reintroduce eval-like phrasing

### Iteration 7: scenario-style rewrite pass on the same 40-row dataset
- run_id: `20260429T172803Z`
- dataset: 40 train / 10 eval
- result: not a win; the scenario rewrite preserved separation but weakened answer sharpness further
- train loss: `1.6901863932609558`
- artifact dir: `/artifacts/hermes-tutor-v1/20260429T172803Z`
- local artifact copy: `tmp/modal-artifacts/20260429T172803Z/`
- what changed:
  - kept eval unchanged and kept train at 40 rows
  - rewrote 4 existing training rows into scenario-style prompts aimed at the smallest-useful-outcome and eval-contamination concepts
  - avoided definitional paraphrases so the concepts would be taught through task framing instead of prompt overlap
- how it showed up in `sample_eval`:
  - the instruct-model answer drifted backward and no longer mentioned the key idea that instruct models already know instruction-following
  - the “smallest useful outcome” answer became more natural than the previous collapsed baseline, but it still failed to mention the required workflow pieces: small dataset, short run, saved adapter, and side-by-side comparison
  - the eval-contamination answer kept the generalization idea but added new drift (`handles adapters`, `target language`) instead of stating the clean chain: prompt reuse -> memorization -> invalid eval
- takeaway:
  - scenario framing alone did not sharpen the concepts enough
  - this pass made the dataset less overlap-prone, but it also weakened the canonical wording the model had been using for the target ideas
  - the next fix should keep scenario-style diversity only where it helps and restore one crisp canonical row per weak concept

### Iteration 8: first narrow v2 run with assistant-only loss
- run_id: `20260430T061418Z`
- dataset: 20 train / 10 eval (`hermes-tutor-v2`)
- result: infrastructure and new objective path worked after one code fix, but output quality is still weak and often drifts into generic or distorted explanations
- train loss: `3.0707270860672`
- artifact dir: `/artifacts/hermes-tutor-v2/20260430T061418Z`
- what changed:
  - switched to the narrower repo-specific v2 dataset
  - ran the first short 20-step diagnostic pass with `assistant_only_loss=True`
  - fixed a launch blocker where the dataset used `conversations` instead of the conversational key name `messages`, which caused TRL/Unsloth to reject `assistant_only_loss=True`
- how it showed up in `sample_eval`:
  - the instruct-model answer became short and obviously synthetic, using a bad child/parent analogy instead of the target concept about instruction-following priors
  - the minimum-success answer collapsed to a vague single-task success criterion and lost the required workflow pieces
  - the eval-contamination answer kept a partial generalization idea but still failed to state the clean memorization -> invalid evaluation chain
- takeaway:
  - the trainer/objective reset now runs correctly, so the next bottleneck is no longer infrastructure
  - `assistant_only_loss=True` plus the narrow v2 data did not automatically yield sharper repo-specific tutoring answers on the first short pass
  - the next move should be artifact-driven review of the full v2 eval, then either sharpen the canonical v2 answers or test whether the 1B base is simply too weak for the precision target

### Iteration 9: sharpened v2 rerun after canonical row rewrite
- run_id: `20260430T062717Z`
- dataset: 20 train / 10 eval (`hermes-tutor-v2`)
- result: the rerun completed cleanly and slightly lowered train loss, but held-out answer quality did not materially improve
- train loss: `3.0663241863250734`
- artifact dir: `/artifacts/hermes-tutor-v2/20260430T062717Z`
- what changed:
  - kept the same narrow v2 split and same 20-step diagnostic shape
  - reran after rewriting the v2 training rows to sharpen four weak concepts: instruct-model priors, minimum-success workflow, eval-contamination causality, and Modal's role
- how it showed up in `sample_eval` and `full_eval`:
  - the instruct-model answer stayed distorted and actually regressed from the earlier child/parent analogy into an even shorter wrong explanation
  - the minimum-success answer remained unchanged and still collapsed to a vague single-task success criterion instead of naming the workflow pieces
  - the eval-contamination answer stayed partial and still failed to state the full memorization -> recall-not-generalization chain
  - the Modal answer changed wording but was still wrong, describing generic workflow mechanics instead of the remote GPU role
- takeaway:
  - this rerun is a useful negative result: the sharpened wording patch alone was not enough to move the 1B model toward the desired precise tutor behavior
  - the tiny loss improvement is not the signal to trust here; the held-out answers are still the deciding artifact
  - the next serious branch should be either a stronger instruct base model on the same narrow dataset or a more structural dataset rewrite rather than another small wording-only patch

### Iteration 10: stronger 3B base model test on the same v2 dataset
- run_id: `20260430T063654Z`
- dataset: 20 train / 10 eval (`hermes-tutor-v2`)
- model: `unsloth/Llama-3.2-3B-Instruct-bnb-4bit`
- result: the stronger base ran successfully on the same 20-step shape and lowered training loss more clearly, but the held-out answers were still mostly wrong in the same concept slots
- train loss: `2.9948059558868407`
- artifact dir: `/artifacts/hermes-tutor-v2/20260430T063654Z`
- what changed:
  - kept dataset, trainer settings, and run length fixed
  - changed only the base model from `unsloth/Llama-3.2-1B-Instruct-bnb-4bit` to `unsloth/Llama-3.2-3B-Instruct-bnb-4bit`
- how it showed up in `sample_eval` and `full_eval`:
  - the instruct-model answer became more fluent, but it still taught the wrong idea (`overfitting`, `simplicity`) instead of instruction-following priors
  - the minimum-success answer stayed wrong and now claimed a made-up validation-set improvement threshold
  - the eval-contamination answer was slightly cleaner, but it still failed to state the memorization -> recall-not-generalization chain
  - the Modal answer stayed plainly wrong and drifted to `code review tool`
  - some outputs became more concise or confident, but not more faithful to the repo-specific target concepts
- takeaway:
  - the stronger base model improved fluency more than correctness
  - this reduces the probability that the 1B base alone was the main bottleneck
  - the next best move is now a structural dataset redesign around tighter concept anchors and cleaner answer targets, not another base-model swap

## Current blockers

1. The run infrastructure now works well, but tuned output quality still depends on better objective targeting and better dataset sharpness.
2. Artifacts are persisted in a Modal volume, but not yet uploaded to Hugging Face Hub.
3. The VPS still has no NVIDIA GPU, so all real training remains Modal-first.

## Current reset for the next experiment

The project now has a cleaner next-step pair:
- implementation reset: the training script uses `assistant_only_loss=True`, saves `full_eval` artifacts, accepts `--dataset-name`, and defaults to a shorter `max_steps=20`
- dataset reset: `data/hermes-tutor-v2/` narrows the task to concise repo-specific beginner tutoring instead of broad ML concept coverage

Why this reset matters:
- the previous v1 loop mixed generic concept teaching with behavior steering
- the next run should test whether a narrower task plus assistant-only loss produces cleaner held-out answers
- this is a better root-cause test than doing another wording-only patch on the old broad dataset

## Documentation outcome for this project

A key deliverable of this project is not only the adapter itself, but also the experiment history:
- what changed between runs
- why a run failed or gave weak results
- how the failure showed up in the artifacts and eval outputs
- what was changed to improve or fix it

This is part of the ai-lab learning goal. The notes should make future iteration easier, not force the same mistakes to be rediscovered.

## Recommended next action order

### 1. Rerun the cleaned 40-row dataset

Target:
- verify whether the stricter 40-row cleanup recovers better alignment on the weak eval concepts

### 2. Keep iteration notes current immediately after the run

Capture:
- chosen model
- dataset version and row counts
- run_id and artifact dir
- 3-5 base vs tuned comparisons
- what improved, what regressed, and why

### 3. Only expand the dataset again if the artifact review justifies it

Rules:
- each answer should be short, specific, and beginner-friendly
- avoid abstract “project reflection” phrasing in target answers
- keep train and eval prompts meaningfully separate
- use run artifacts to justify the next patch

## Minimal command checklist

Preview the dataset:

```bash
python scripts/preview_tutor_dataset.py
```

Re-run environment check:

```bash
python3 scripts/check_env.py
```

Smoke-test Modal GPU connectivity:

```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/hello_gpu.py
```
