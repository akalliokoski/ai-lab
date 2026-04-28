---
title: Unsloth
created: 2026-04-28
updated: 2026-04-28
type: entity
tags: [training, unsloth, research, workflow]
sources: [raw/articles/unsloth-docs-2026-04-28.md]
---

# Unsloth

Unsloth is the primary training framework currently chosen for the first `ai-lab` learning track. It is the fastest path to learning practical fine-tuning, adapter training, and later reinforcement-learning-style workflows in a way that can start small and scale up.^[raw/articles/unsloth-docs-2026-04-28.md]

Why it matters here
- It directly supports the learning-by-doing focus of `ai-lab`.
- Its docs are organized around beginner onboarding, requirements, notebooks, and model-specific guides.
- It fits a staged workflow: understand the concepts locally, prototype lightly on a MacBook, then move heavier runs to Modal when needed.

Operational stance
- The VPS should be the orchestration and documentation layer.
- The MacBook is the best first place for local interactive experiments.
- Modal is the preferred remote GPU escalation path when local resources stop being enough.

Related pages
- [[ai-lab-learning-path]]
