# Wiki Index

> AI lab knowledge base for this profile.
> Last updated: 2026-04-30 | Total pages: 15

## Entities
- [[unsloth]] — Main fine-tuning framework currently chosen for the first learning track.

## Concepts
- [[ai-lab-learning-path]] — The current staged plan for learning by doing across VPS, MacBook, and Modal.
- [[artifact-card-sft]] — The active structured-output first project: turn short experiment evidence into a strict JSON experiment card.
- [[artifact-driven-experiment-debugging]] — Use saved Modal artifacts and run summaries as the main debugging surface for experiment iteration.
- [[hermes-ai-lab-tutor-adapter]] — The original tutor-style first experiment, now mainly useful as a negative result and debugging case study.

## Comparisons
- [[artifact-card-failure-modes-binary-v1-vs-top2-v1]] — Comparison showing that forcing the final ranked pair directly regressed against the stronger binary supervision branch and still failed held-out top-2 selection.
- [[artifact-card-failure-modes-top2-v1-vs-pairwise-v1]] — Comparison showing that pairwise comparison structure improved reconstructed held-out top-2 set recovery but still failed ordered ranking and kept `missing-required-detail` over-dominant.
- [[artifact-card-failure-modes-v1-vs-binary-v1]] — Comparison showing that one-label-at-a-time binary supervision improved local judgment metrics sharply but still failed final top-2 label-set reconstruction.
- [[artifact-card-full-card-vs-failure-modes-branch]] — Comparison showing that a simple `primary_failure_modes`-only branch did not beat the full-card field score, pointing to label/evidence design rather than only field interference.
- [[artifact-card-v1-vs-v2]] — Run-by-run comparison showing how constraining labels and phrases improved semantic field accuracy without changing the schema.
- [[artifact-card-v2-vs-v3]] — Comparison showing that extra full-card scaffolding improved `next_action` but regressed other fields, motivating task decomposition.
- [[first-fine-tuning-project-options]] — Ranked comparison of better-scoped first fine-tuning projects after the repo-tutor adapter failed to improve reliably.

## Queries
- [[fine-tuning-improvement-strategies-2026-04-30]] — Fresh strategy memo on how to improve the current fine-tuning work, emphasizing supervision redesign, confusion-targeted contrasts, and shorter prompts.
- [[fine-tuning-lessons-from-first-project]] — Practical lessons learned from the tutor failure, artifact-card-v1 structure win, artifact-card-v2 semantic improvements, and the later decomposition tests.
- [[fine-tuning-no-improvement-root-cause-review]] — Fresh diagnosis of why the tutor-adapter fine-tuning runs are not showing stable improvements.
