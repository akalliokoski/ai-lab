---
title: Bruxism CAP newcomer deep dive (2026-05-05)
created: 2026-05-05
updated: 2026-05-06
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/notebooklm-bruxism-cap-deep-dive-2026-05-05.md
  - concepts/bruxism-cap.md
  - queries/bruxism-cap-campaign-handoff-2026-05-05.md
  - comparisons/bruxism-cap-patched-emg-vs-matched-c4-anchor-comparison-2026-05-05.md
  - queries/bruxism-cap-record-relative-shape-composition-audit-2026-05-05.md
  - queries/bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06.md
---

# Question
What should a newcomer understand first about the `bruxism-cap` project: its goals, dataset, evolution, lessons, limitations, and final outcome?

# Short answer
Start with the benchmark philosophy, not the headline metric. `bruxism-cap` is a deliberately tiny, leakage-aware CAP benchmark whose value comes from honest iteration and preserved negative results. It is now complete: the final matched control-expanded replication (`pass48`) closed the branch, so the project should be read as a finished benchmark history and methodology scaffold rather than as an active optimization loop. [[bruxism-cap]] [[bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06]]

# Best file to read
The full long-form newcomer briefing still lives here:
- `projects/bruxism-cap/reports/notebooklm-bruxism-cap-deep-dive-2026-05-05.md`

Read it as historical project context, then pair it with:
- `projects/bruxism-cap/reports/bruxism-cap-final-closure-report-2026-05-06.md`

## What a newcomer should retain
- The project was benchmark-first, not deployment-first.
- The honest positive set was always only `brux1` and `brux2`.
- Random-window CV was much more flattering than subject-level LOSO.
- Many plausible EMG tweaks were directionally useful but not enough to create a stable stronger detector claim.
- The repaired scaffold produced real intermediate anchors, but the final matched repaired control-expanded replication closed the benchmark in the negative direction.

## Bottom line
This is a good project to study if you want to learn how a small public biosignal benchmark becomes honest, auditable, and scientifically bounded. It is not a project that ended in a strong detector win.
