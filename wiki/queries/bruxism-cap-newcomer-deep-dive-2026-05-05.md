---
title: Bruxism CAP newcomer deep dive (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/notebooklm-bruxism-cap-deep-dive-2026-05-05.md
  - concepts/bruxism-cap.md
  - queries/bruxism-cap-campaign-handoff-2026-05-05.md
  - comparisons/bruxism-cap-patched-emg-vs-matched-c4-anchor-comparison-2026-05-05.md
  - queries/bruxism-cap-record-relative-shape-composition-audit-2026-05-05.md
---

# Question
What should a newcomer understand first about the `bruxism-cap` project: its goals, dataset, evolution, lessons, limitations, critique, and the best next steps?

# Short answer
Start with the benchmark philosophy, not the headline metric. `bruxism-cap` is a deliberately tiny, leakage-aware CAP benchmark whose value comes from honest iteration, not from a big final score. The project has already learned that random-window CV is highly misleading, annotation validity matters, many plausible EMG tweaks fail, and the latest `record-relative + shape` EMG composition helps materially without yet solving the benchmark because `brux1` remains the bottleneck. [[bruxism-cap]] [[bruxism-cap-campaign-handoff-2026-05-05]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]]

# Best file to read
The full newcomer briefing lives here:
- `projects/bruxism-cap/reports/notebooklm-bruxism-cap-deep-dive-2026-05-05.md`

It covers:
- project purpose and scope
- dataset description and caveats
- pass-by-pass project evolution
- lessons learned and preserved negative results
- current benchmark state
- limitations and critique
- best next-step ideas

# Why this matters
This briefing was prepared as the main source pack for a NotebookLM deep-dive notebook so a new contributor can learn the project from the current repo evidence rather than from stale memory or one-off chat summaries. [[bruxism-cap]] [[bruxism-cap-campaign-handoff-2026-05-05]]
