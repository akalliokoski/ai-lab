---
title: Bruxism CAP EMG A1 raw-location ablation (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass33-raw-location-ablation.md
  - ../projects/bruxism-cap/reports/pass32-broad-morphology-ablation.md
  - concepts/bruxism-cap.md
---

# Question
On the repaired matched `SLEEP-S2 + MCAP-A1-only` percentile-band scaffold, does a smaller ablation that removes only the most extreme raw-location terms help `EMG1-EMG2` without breaking the comparison channel?

# Short answer
No. Removing only `mean`, `min`, and `max` does **not** improve the honest EMG-first result.

`EMG1-EMG2` stays at subject-level balanced accuracy `0.333` with subject sensitivity `0.000`, and the best-bruxism-versus-highest-control margin gets much worse (`-0.260` -> `-0.492`). The main damage is that `brux1` collapses from mean LOSO score `0.270` to `0.030`, while `n3` barely moves (`0.530` -> `0.527`). [[bruxism-cap]] [[bruxism-cap-emg-a1-broad-morphology-ablation-2026-05-05]]

# What changed relative to pass32
Pass32 showed that the broader morphology deletion was too destructive because it also erased the useful `C4-P4` `brux2 > n3` behavior. This smaller pass33 deletion keeps `zero_crossing_rate`, `ptp`, and the envelope family intact, so it is a tighter test of whether the remaining EMG failure is mostly caused by a few raw-location terms.^[../projects/bruxism-cap/reports/pass33-raw-location-ablation.md]

The answer is still negative, but in a different way than pass32:
- the comparison channel is basically unchanged (`C4-P4` subject-level balanced accuracy stays `0.750`, and `brux2 - n3` stays about `+0.54`)
- the EMG surface gets worse anyway because `brux1` loses support while `n3` keeps it
- so the bottleneck is not simply “delete a few raw-location terms and EMG becomes honest” [[bruxism-cap-a1-percentile-band-channel-gap-audit-2026-05-05]] [[bruxism-cap-c4-a1-percentile-band-vs-emg-2026-05-05]]

# Key evidence
## EMG-first result
- subject-level balanced accuracy: `0.333` -> `0.333`
- subject-level sensitivity: `0.000` -> `0.000`
- `brux1`: `0.270` -> `0.030`
- `brux2`: `0.036` -> `0.035`
- `n3`: `0.530` -> `0.527`
- `n3 - brux1` gap: `+0.260` -> `+0.497`

## Comparison-channel result
- `C4-P4` subject-level balanced accuracy: `0.750` -> `0.750`
- `C4-P4` subject-level sensitivity: `0.500` -> `0.500`
- `brux2 - n3` gap: `+0.542` -> `+0.544`

## Surviving EMG control-favoring terms
After removing `mean`, `min`, and `max`, the main `n3 > brux1` support on EMG is still carried by:
- `ptp`
- `zero_crossing_rate`
- `envelope_std`
- `line_length`
- `rectified_std`
- `envelope_cv`

That makes the next step a representation problem more than another deletion problem.^[../projects/bruxism-cap/reports/pass33-raw-location-ablation.md]

# Verdict
Preserve pass33 as a negative result. It is narrower and cleaner than pass32, but it still does not beat the current honest EMG baseline, and it strengthens the case for a representation-focused audit instead of another feature-removal pass.

# Best next bounded step
Keep the repaired matched `A1-only` scaffold fixed and stay EMG-first. The next best bounded move is to audit or test a record-relative / within-record standardized morphology representation on the retained EMG envelope family rather than stacking more deletions.
