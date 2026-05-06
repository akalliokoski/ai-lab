---
title: Bruxism CAP EMG A3 time-position-matched rerun
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [project, biosignal, benchmark, evaluation]
sources:
  - ../projects/bruxism-cap/reports/pass25-emg-a3-time-position-matched-selected.md
  - ../projects/bruxism-cap/reports/time-position-match-pass25-emg-a3.json
  - ../projects/bruxism-cap/reports/loso-cv-pass25-emg-a3-timepos10-selected.json
---

# Bruxism CAP EMG A3 time-position-matched rerun

## Question
Does a stricter shared absolute time-position-matched `EMG1-EMG2` rerun fix the current pass19 EMG failure on the verified 5-subject exclusive `SLEEP-S2 + MCAP-A3-only` scaffold?

## Answer
No. A simple shared absolute time-position match is feasible, but only by shrinking the scaffold from `14` to `10` windows per subject. That stricter rerun improves both bruxism subjects relative to pass19, especially `brux2`, yet it still leaves **all three controls above both bruxism subjects** on the honest LOSO subject surface. So time-position mismatch was a real contributor, but it was not the sole cause of EMG-first failure. [[bruxism-cap]] [[bruxism-cap-emg-brux2-vs-n3-gap-2026-05-05]]

## What changed
- Regenerated the uncapped exclusive `SLEEP-S2 + MCAP-A3-only` `EMG1-EMG2` feature pool for `brux1`, `brux2`, `n3`, `n5`, and `n11`.
- Added `projects/bruxism-cap/src/select_time_position_matched_windows.py` to select a shared absolute-interval subset reproducibly.
- Hardened `train_baseline.py` so `time_match_rank` is treated as metadata instead of a train feature.
- Reran random-window and LOSO baselines on the new `10`-windows-per-subject shared-interval scaffold.

## Evidence
- Shared interval across all five subjects: `start_s 3210.0 -> 12230.0`.
- Candidate windows inside that shared interval: `brux1 25`, `brux2 29`, `n3 10`, `n5 10`, `n11 12`.
- This means absolute time-position matching cannot preserve the old matched-14 cap on the current verified subset.
- Pass19 `logreg` subject means: `n3 0.280`, `n5 0.222`, `brux1 0.151`, `n11 0.147`, `brux2 0.088`.
- Pass25 shared-time-position `logreg` subject means: `n11 0.417`, `n5 0.416`, `n3 0.400`, `brux1 0.282`, `brux2 0.215`.
- Best LOSO window-level metric regresses from pass19 `0.629` to pass25 `0.600` (best model shifts from `logreg` to `svm`).
- Honest LOSO subject-level sensitivity stays `0.000`.

## Interpretation
- Pass24 was directionally right that time position mattered, because both bruxism subjects rise under the stricter shared-interval rerun.
- But the stricter scaffold also lifts the controls, so the main honest decision boundary is still not fixed.
- Pass19 remains the best current honest EMG working point even though pass25 is a useful validity result.

## Best next step
Rebuild the **same shared-interval / 10-windows-per-subject scaffold on `C4-P4`** and compare it directly against this pass25 EMG rerun. That will isolate whether the failure is mainly channel-specific or mainly a property of the stricter time-position-matched scaffold itself. [[bruxism-cap-emg-pass19-vs-c4-pass12-subject-scores-2026-05-05]] [[bruxism-cap-emg-envelope-selection-2026-05-04]]
