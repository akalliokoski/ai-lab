---
title: Bruxism CAP EMG A1 broad morphology ablation (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [experiment, evaluation, notes, research]
sources:
  - concepts/bruxism-cap.md
  - projects/bruxism-cap/reports/pass32-broad-morphology-ablation.md
---

# Question
Does the wider control-favoring morphology exclusion set fix the repaired `EMG1-EMG2 A1-only` percentile-band benchmark, and does it preserve the useful `C4-P4` comparison-channel behavior?

# Short answer
No. The wider deletion is too destructive to promote as the next baseline move.

On the matched repaired scaffold, excluding `mean`, `max`, `ptp`, `zero_crossing_rate`, `sample_entropy`, `burst_fraction`, and `envelope_cv` does **not** rescue the EMG-first result. `EMG1-EMG2` still misses both bruxism subjects and the main hard control (`n3`) stays above `brux1`. The same ablation also removes the earlier `C4-P4` advantage where `brux2` clearly outranked `n3`. [[bruxism-cap]] [[bruxism-cap-a1-percentile-band-n3-family-recurrence-2026-05-05]] [[bruxism-cap-c4-a1-percentile-band-vs-emg-2026-05-05]]

# What changed in pass32
- Kept the repaired percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold from pass28/pass29 fixed.
- Kept the same verified `5`-subject subset and the same matched selected rows across `EMG1-EMG2` and `C4-P4`.
- Kept the same honest interpretation surface: LOSO `logreg` subject-level summaries.
- Removed one compact broader morphology family at train time instead of only the narrower pass31 trio.

# Key evidence

## 1. `EMG1-EMG2` still does not clear the honest bar
- Subject-level balanced accuracy stays `0.333` before and after the ablation.
- Subject-level sensitivity stays `0.000` before and after the ablation.
- The best-bruxism-minus-highest-control margin improves only slightly from `-0.260` to `-0.224`, which is still the wrong sign.
- `n3` actually separates from `brux1` even more strongly in mean score (`+0.260` -> `+0.425`).

## 2. The ablation changes *which* EMG subject looks less bad, but not the verdict
- `brux2` rises sharply on EMG (`0.036` -> `0.406`), which is interesting.
- But `brux1` falls (`0.270` -> `0.205`) and `n3` rises too (`0.530` -> `0.630`).
- So the overall honest EMG verdict does not improve; the failure surface just rotates.

## 3. The same deletion breaks the strongest useful comparison-channel behavior
- On `C4-P4`, subject-level balanced accuracy stays `0.750`, but only because `brux1` flips positive while `brux2` collapses.
- The main channel-comparison gain from pass29 disappears: `brux2 - n3` mean-score gap flips from `+0.542` to `-0.126`.
- That means this deletion erases the cleanest previously useful `C4-P4` signal while still not producing an honest EMG win.

# Interpretation
This is a first-class negative result, not a near-miss success.

Pass31 was right that the trio-only story was too narrow, but pass32 shows the obvious wider deletion is also the wrong move. The recurring morphology family is part of the problem surface, yet removing it wholesale destroys signal faster than it removes the transfer failure. [[bruxism-cap]] [[bruxism-cap-a1-percentile-band-channel-gap-audit-2026-05-05]]

# Best next bounded step
Stay EMG-first and keep the repaired percentile-band `A1-only` scaffold fixed.

The safer next move is now one of:
1. a validity-focused morphology representation audit for `EMG1-EMG2` (for example record-relative or subject-relative amplitude framing), or
2. a smaller raw-location ablation that does **not** also remove `zero_crossing_rate` and the broader envelope structure.

Do not promote pass32 as the new baseline. Preserve it as the repo's proof that wholesale morphology deletion is too blunt for this benchmark.
