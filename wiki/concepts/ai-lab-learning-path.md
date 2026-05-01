---
title: AI Lab Learning Path
created: 2026-04-28
updated: 2026-04-30
type: concept
tags: [workflow, notes, experiment, vps, macbook, modal]
sources: [raw/articles/unsloth-docs-2026-04-28.md]
---

# AI Lab Learning Path

The current `ai-lab` learning path is intentionally staged:
1. read the docs and understand constraints
2. run the smallest end-to-end example
3. build a tiny dataset worth caring about
4. run one controlled LoRA or QLoRA experiment
5. compare outputs before scaling up
6. move the same workflow to Modal when real GPU time is justified

Current first-project pivot:
- the original tutor adapter is now treated as a useful negative result and debugging case study
- the active first success-oriented project is [[artifact-card-sft]], which keeps the task narrow, structured, and automatically scoreable

The main design principle is to avoid ambitious but blurry projects too early. Small, documented experiments beat vague grand plans because they compound into reusable knowledge.

Execution split
- VPS: Hermes orchestration, repo updates, Telegram access, wiki maintenance
- MacBook: local Python, notebooks, small experiments
- Modal: reproducible GPU-backed training and batch jobs

Related pages
- [[unsloth]]
