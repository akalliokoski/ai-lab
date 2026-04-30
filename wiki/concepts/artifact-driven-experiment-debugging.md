---
title: Artifact-Driven Experiment Debugging
created: 2026-04-29
updated: 2026-04-29
type: concept
tags: [training, evaluation, workflow, modal, experiment, notes]
sources: [raw/articles/unsloth-docs-2026-04-28.md]
---

# Artifact-Driven Experiment Debugging

For ai-lab training projects, saved run artifacts are not just outputs. They are the main debugging surface for understanding what the model actually learned and where the dataset or setup failed. [[hermes-ai-lab-tutor-adapter]] [[unsloth]]

Core rule
- Every training run should leave behind enough evidence to explain the result later: run summary, metrics, adapter files, and a small base-vs-tuned eval snapshot.

Current Modal artifact workflow
- The Modal volume `ai-lab-unsloth-artifacts` is the durable store for adapters and run summaries.
- `scripts/list_modal_runs.py` lists saved runs and headline metrics.
- `scripts/show_modal_run_summary.py` shows one run in detail, including `sample_eval` outputs.
- Local copies can be pulled into `tmp/modal-artifacts/<run_id>/` when deeper inspection is needed.

Why this matters
- A successful infrastructure run can still be a failed learning run.
- Loss alone is not enough for tiny tutor datasets.
- The `sample_eval` block is the fastest way to see drift, vagueness, memorization, or concept confusion.
- Comparing multiple `run_summary.json` files makes iteration decisions more concrete and less guessy.

Debugging questions to ask after every run
- Did the tuned output move closer to the reference, or just move somewhere else?
- Did the model become shorter and clearer, or only more generic?
- Are repeated runs with the same dataset stable?
- If a run got worse, which dataset edits likely caused the drift?
- Does the failure show up as abstraction, concept confusion, memorization, or style inconsistency?

Documentation rule for ai-lab experiments
- Record each important run and each important dataset pass.
- Note what changed, what failed, how the failure showed up in the artifacts, and what was changed next.
- Treat this writeup as part of the learning outcome, not as optional cleanup.

Tutor adapter example from this repo
- The stable 40-row runs produced reproducible loss and similar eval behavior, which showed the infrastructure was sound and the dataset was the bottleneck.
- A later 46-row targeted patch looked reasonable on paper but produced worse `sample_eval` answers, showing that concept overlap and vague phrasing can make the model drift instead of improve.
- Pulling the latest `run_summary.json` locally made it easy to compare failure modes and justify a stricter dataset cleanup.
- The cleaned 40-row rerun then improved loss and recovered from the worst regression, but the artifacts still showed weak concept alignment on the same three eval prompts.
- A later 43-row surgical patch improved one weak concept, but the artifacts also showed phrase-copy distortion (`saved adapter ... saved to a repo`) and continued confusion on eval contamination. That was useful evidence that tiny additive patches can still be too overlap-heavy.
- The follow-up 40-row cleanup rerun removed those near-paraphrase rows and made the eval cleaner again. That exposed the more important truth: two weak concepts were still under-taught, so overlap removal improved trustworthiness more than it improved quality.
