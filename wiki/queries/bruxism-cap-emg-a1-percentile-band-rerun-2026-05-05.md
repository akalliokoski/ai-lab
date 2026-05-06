---
title: Bruxism CAP EMG A1-only percentile-band timing rerun
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, ml, sleep, biosignal]
sources:
  - ../projects/bruxism-cap/reports/pass28-emg-a1-percentile-band-rerun.md
  - ../projects/bruxism-cap/reports/time-position-match-pass28-emg-a1-pct10-90.json
  - ../projects/bruxism-cap/reports/loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json
  - ../projects/bruxism-cap/reports/pass27-emg-a1-time-position-feasibility.md
---

# Query
Did a softer timing-control scaffold make the EMG-first `A1-only` CAP benchmark usable, and did it beat the current honest baseline?

# Answer
Partly on extraction, no on transfer.

The new pass28 rerun kept the EMG-first frame, patched `select_time_position_matched_windows.py` with a `percentile-band` mode, and rebuilt the verified `5`-subject exclusive `SLEEP-S2 + MCAP-A1-only` scaffold on `EMG1-EMG2` using relative-time quantiles `0.10` to `0.90` instead of one hard shared absolute interval. That change solved the immediate pass27 validity problem: the scaffold expands from only `2` windows per subject (`10` rows total) under the strict shared interval to `10` windows per subject (`50` rows total) under the percentile-band selector [[bruxism-cap]].

But the honest benchmark verdict did not improve. On LOSO, the best model (`svm`) reaches window-level balanced accuracy `0.600` with sensitivity `0.000` and specificity `0.600`, and the corresponding subject-level summary stays at balanced accuracy `0.500` with subject-level sensitivity still `0.000`. Both held-out bruxism subjects remain below all three controls in mean score order: `n3` `0.422`, `n11` `0.319`, `n5` `0.264`, `brux1` `0.222`, `brux2` `0.209` [[bruxism-cap]].

# Why it matters
- This is still useful progress because it separates a selector-collapse problem from a transfer problem.
- The repo now has a reproducible softer timing-control scaffold for `EMG1-EMG2 A1-only` instead of only a `10`-row failure artifact.
- But the stronger extraction scaffold does not yet beat the current honest EMG baseline or rescue subject transfer, so it should be preserved as a negative result rather than read as a benchmark win.

# Best next step
Keep the new percentile-band selector fixed and run the matched comparison channel on the same scaffold next: rebuild `C4-P4` on the same verified `5`-subject `A1-only` percentile-band `10`-windows-per-subject subset, then compare it directly against pass28 `EMG1-EMG2` before trying another timing rule or a larger model family.
