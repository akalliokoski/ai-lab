---
title: Bruxism CAP A1-only percentile-band channel gap audit (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass28-emg-a1-percentile-band-rerun.md
  - ../projects/bruxism-cap/reports/pass29-c4-a1-percentile-band-vs-emg.md
  - ../projects/bruxism-cap/reports/pass30-a1-percentile-band-channel-gap-audit.md
---

# Question
On the repaired percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold, why does `brux1` still trail `n3` under both channels while `brux2` recovers only on `C4-P4`?

# Short answer
Because the scaffold is no longer the ambiguous part.

The selected rows are timing-matched across `EMG1-EMG2` and `C4-P4`, so the remaining difference is now a real channel / feature-behavior difference on the same `10` windows per subject, not a hidden extraction mismatch. [[bruxism-cap]]

On that matched surface:
- `brux1` remains the shared unresolved subject under both channels
- `brux2` is the main channel separator: it stays far below `n3` on `EMG1-EMG2`, but flips far above `n3` on `C4-P4`
- the next bounded target should therefore be the recurring `n3`-favoring feature family, not another timing rewrite or a jump to larger models [[bruxism-cap-c4-a1-percentile-band-vs-emg-2026-05-05]] [[bruxism-cap-emg-a1-percentile-band-rerun-2026-05-05]]

# Evidence from the matched audit
The pass30 audit kept the repaired percentile-band `A1-only` scaffold fixed and rebuilt the same `logreg` LOSO folds with the same train-time exclusions on both channels.^[../projects/bruxism-cap/reports/pass30-a1-percentile-band-channel-gap-audit.md]

## Scaffold check
- selected rows are timing-matched across channels: `True`
- shared audited columns: `subject_id`, `window_index`, `start_s`, `end_s`, `relative_time_quantile`, `time_match_rank`
- each subject still contributes the same `10` selected windows on both channels

That means the pass28/pass29 difference is now interpretable as a channel / feature-behavior difference, not a row-selection difference.

## Subject-score gaps
- `EMG1-EMG2`: `n3 - brux1 = +0.260`, `brux2 - n3 = -0.494`
- `C4-P4`: `n3 - brux1 = +0.012`, `brux2 - n3 = +0.542`

So the repaired scaffold still leaves one shared hard case (`brux1 < n3`) under both channels, but the big matched channel gap is `brux2`: `C4-P4` recovers it decisively while `EMG1-EMG2` does not.^[../projects/bruxism-cap/reports/pass30-a1-percentile-band-channel-gap-audit.md]

# Practical interpretation
## What stayed bad under both channels
`brux1` is still the honest bottleneck. Even after the repaired timing control, it remains below `n3` under both channels, which means the next step should stay validity-focused rather than acting as if the benchmark is already stable. [[bruxism-cap]]

## What changed between channels
The repaired comparison is not saying “EEG wins everywhere.” It is saying something narrower and more actionable:
- `C4-P4` shrinks the `n3` versus `brux1` gap to almost zero
- `C4-P4` also flips `brux2` strongly above `n3`
- `EMG1-EMG2` still leaves both bruxism subjects in a control-dominant ordering on the same scaffold

That preserves the EMG-first framing while making the next diagnostic target smaller and more precise.

# Feature-level lesson worth keeping
The recurring `n3` support is now compact enough to audit directly. Across the repaired scaffold, the remaining overlap is consistent with a small control-favoring family rather than a broad project-wide collapse. The safest next move is therefore to audit whether `sample_entropy`, `burst_fraction`, and `envelope_cv` are the reusable cross-channel `n3`-favoring family before trying model complexity. [[bruxism-cap]]

# Bottom line
Pass30 is a benchmark-clarity win, not a new detector win:
- it confirms the repaired percentile-band scaffold is genuinely matched
- it shows the remaining shared honest failure is `brux1` versus `n3`
- it localizes the main cross-channel difference to `brux2` recovering only on `C4-P4`

So the next bounded experiment should stay on the same scaffold and target the narrow recurring `n3`-favoring feature family rather than changing the timing rule again or jumping to larger models.
