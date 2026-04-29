---
title: Hermes AI Lab Tutor Adapter
created: 2026-04-29
updated: 2026-04-29
type: concept
tags: [training, unsloth, dataset, evaluation, modal, experiment, workflow]
sources: [raw/articles/unsloth-docs-2026-04-28.md]
---

# Hermes AI Lab Tutor Adapter

The current default first experiment for `ai-lab` is a tiny tutoring adapter project: fine-tune a small instruct model so it explains ML and fine-tuning concepts clearly, briefly, and step-by-step. It is intentionally narrow and small so the full workflow can be completed once before the project expands. [[unsloth]] [[ai-lab-learning-path]]

Why this project is a good fit
- It matches the repo's learning-by-doing focus.
- It is easy to author and inspect by hand.
- It encourages disciplined comparison between base and tuned outputs.
- It cleanly fits the VPS/MacBook/Modal split already defined in the workspace.

Current implementation status
- A seed dataset exists in `data/hermes-tutor-v1/` with 40 train rows and 10 eval rows.
- A dataset preview script exists in `scripts/preview_tutor_dataset.py`.
- Local helper scripts now exist to inspect Modal artifacts: `scripts/list_modal_runs.py` and `scripts/show_modal_run_summary.py`.
- A Modal training entrypoint exists in `modal/train_unsloth_tutor.py` using a small Llama 3.2 instruct default.
- The latest short Modal SFT run succeeded on 2026-04-29 and saves a LoRA adapter plus tokenizer into the Modal volume `ai-lab-unsloth-artifacts` at `/artifacts/hermes-tutor-v1/20260429T094629Z/adapter`.
- The Modal image is pinned to a compatible Python 3.10 / Torch 2.10.0 / xFormers 0.0.35 stack so Unsloth uses xFormers correctly on the T4 run.
- A small base-vs-tuned eval snapshot is returned in the run summary for quick inspection.

Next milestone
- Review the dataset for style consistency.
- Configure `HF_TOKEN` and smoke-test Modal GPU access.
- Run one short supervised fine-tuning pass and record the comparison results. [[ai-lab-learning-path]] [[unsloth]]
