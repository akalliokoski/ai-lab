---
title: Bruxism-cap rule survival audit (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [experiment, evaluation, dataset, workflow, notes]
sources:
  - raw/articles/cap-sleep-database-physionet-2012.md
  - raw/articles/bruxism-single-channel-eeg-2024.md
---

# Question
What changed in the usable CAP window pools as `bruxism-cap` moved from plain `SLEEP-S2` windows to stricter CAP-overlap filters?

# Short answer
The overlap rules are not availability-neutral. As the repo moved from pass4 `S2` windows to pass7 mixed `S2+MCAP`, then pass9 `S2+A3`, then pass10 exclusive `S2+A3-only`, the bruxism pool stayed relatively richer than the control pool. That means later reruns changed both event semantics and sampling balance, so they should not be interpreted as like-for-like subsets. [[bruxism-cap]] [[bruxism-cap-first-baseline-lessons-2026-05-03]] [[ai-lab-learning-path]]

# Audited artifacts
- Script: `projects/bruxism-cap/src/audit_rule_survival.py`
- JSON report: `projects/bruxism-cap/reports/rule-survival-audit-pass11.json`
- Markdown report: `projects/bruxism-cap/reports/pass11-rule-survival-audit.md`

# Rules compared
- `pass4_s2` — in-range `SLEEP-S2` windows only
- `pass7_s2_mcap_any` — `SLEEP-S2` windows overlapping any of `MCAP-A1`, `MCAP-A2`, or `MCAP-A3`
- `pass9_s2_mcap_a3` — `SLEEP-S2` windows overlapping `MCAP-A3`
- `pass10_s2_mcap_a3_only` — `SLEEP-S2` windows overlapping `MCAP-A3` while excluding simultaneous `MCAP-A1` or `MCAP-A2`

# Key evidence

## Label-level survival
- Bruxism subjects:
  - pass4 `S2`: `442` eligible windows
  - pass7 mixed `S2+MCAP`: `258` (`58.4%` of pass4)
  - pass9 `S2+A3`: `161` (`36.4%` of pass4)
  - pass10 exclusive `S2+A3-only`: `142` (`32.1%` of pass4)
- Control subjects:
  - pass4 `S2`: `1026` eligible windows
  - pass7 mixed `S2+MCAP`: `456` (`44.4%` of pass4)
  - pass9 `S2+A3`: `177` (`17.3%` of pass4)
  - pass10 exclusive `S2+A3-only`: `156` (`15.2%` of pass4)

## Subject-level imbalance
- `brux2` remains unusually rich under the strictest rule with `111` eligible exclusive-`A3` windows.
- `n5` drops much more sharply, falling from `413` eligible pass4 `S2` windows to only `38` eligible exclusive-`A3` windows.
- `brux1` also narrows substantially, from `144` eligible pass4 `S2` windows to `31` exclusive-`A3` windows.

# Why this matters
1. Pass7, pass9, and pass10 were useful negative results, but they also changed the candidate window pool in a label-skewed way.
2. The later `A3`-focused reruns preserved relatively more bruxism windows than control windows.
3. Lower random-window optimism in pass9/pass10 therefore cannot be read only as a cleaner physiological boundary; it also reflects a changed sampling surface.
4. Future family-to-family comparisons need this survival context preserved alongside the model metrics.

# Practical conclusion
The cleanest next bounded experiment is no longer “make `A3` stricter again.” It is to compare one alternate exclusive family such as `S2 + A1-only` against the current `S2 + A3-only` subset on the same verified subject set, while keeping this rule-survival audit beside the evals so the comparison stays interpretable. [[bruxism-cap]] [[bruxism-eeg-emg-starter-project-2026-05-03]]
