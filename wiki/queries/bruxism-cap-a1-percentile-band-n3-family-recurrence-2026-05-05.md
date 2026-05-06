---
title: Bruxism CAP A1-only percentile-band n3-family recurrence audit (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass30-a1-percentile-band-channel-gap-audit.md
  - ../projects/bruxism-cap/reports/pass31-a1-percentile-band-n3-family-recurrence.md
---

# Question
On the repaired percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold, is the remaining `n3` support really concentrated in the small suspected feature trio `sample_entropy`, `burst_fraction`, and `envelope_cv`?

# Short answer
Not enough to justify a trio-only ablation.

The suspected trio is real, but it is not the whole story on the matched pass28/pass29 scaffold. `burst_fraction` recurs, `envelope_cv` recurs in several contrasts, and `sample_entropy` is mixed. But the harsher `EMG1-EMG2` control advantage is still driven mainly by broader morphology terms such as `mean`, `max`, `ptp`, and `zero_crossing_rate`, especially on the shared honest failure `n3 > brux1`. [[bruxism-cap]] [[bruxism-cap-a1-percentile-band-channel-gap-audit-2026-05-05]]

# What changed relative to the pass30 hypothesis
Pass30 ended with the safest next question: maybe the remaining `n3` support was narrow enough to isolate to `sample_entropy`, `burst_fraction`, and `envelope_cv`. Pass31 checked that directly on the same repaired scaffold and found a more cautious answer: the trio recurs, but it explains only a minority of the positive `n3` support in the main matched gaps.^[../projects/bruxism-cap/reports/pass31-a1-percentile-band-n3-family-recurrence.md]

That means the repo should preserve the suspected trio as part of the explanation, but not mistake it for the full explanation. [[bruxism-cap-emg-a1-percentile-band-rerun-2026-05-05]] [[bruxism-cap-c4-a1-percentile-band-vs-emg-2026-05-05]]

# Evidence worth keeping
## The scaffold stayed matched
Pass31 reused the same repaired pass28/pass29 rows and re-verified that the selected rows remained timing-matched across channels (`True`). So the new conclusion is about feature behavior, not about hidden extraction drift.^[../projects/bruxism-cap/reports/pass31-a1-percentile-band-n3-family-recurrence.md]

## The main `EMG1-EMG2` failure is broader than the trio
For the shared hard case `n3 - brux1` on `EMG1-EMG2`:
- total positive contribution toward `n3`: `164.690`
- suspected-trio contribution: `0.443`
- trio share: only `0.269%`

The largest positive `n3` support instead comes from broader morphology / crossing terms:
- `mean` `+156.609`
- `max` `+1.825`
- `ptp` `+1.414`
- `zero_crossing_rate` `+1.348`
- `line_length` `+1.138`

So on the hardest honest EMG gap, the trio is not dominant.^[../projects/bruxism-cap/reports/pass31-a1-percentile-band-n3-family-recurrence.md]

## The trio is more real than random, but still not sufficient
Across the four audited contrasts (`EMG n3-brux1`, `EMG n3-brux2`, `C4 n3-brux1`, `C4 n3-brux2`):
- `burst_fraction` is positive in `4/4`
- `envelope_cv` is positive in `3/4`
- `sample_entropy` is positive in only `1/4`

So the trio does recur, but unevenly. It is not one clean universally positive family across both channels.^[../projects/bruxism-cap/reports/pass31-a1-percentile-band-n3-family-recurrence.md]

## `C4-P4` is also not a pure trio story
Even where the trio contributes on `C4-P4`, the shared `n3 > brux1` gap is still led by larger non-trio terms (`max`, `mean`, `zero_crossing_rate`, `burst_rate_hz`). The trio share there is only about `10.386%` of the positive `n3` support.^[../projects/bruxism-cap/reports/pass31-a1-percentile-band-n3-family-recurrence.md]

# Practical interpretation
This is a useful negative audit, not a dead end:
- it preserves the EMG-first framing
- it keeps the repaired percentile-band scaffold as the valid surface
- it prevents the next ablation from being too narrow for the actual failure

The safest next move is therefore a **compact but wider** control-favoring exclusion set on the same scaffold, not a trio-only patch. [[bruxism-cap]]

# Bottom line
Pass31 refines the pass30 hypothesis in a valuable way:
- yes, `burst_fraction` and `envelope_cv` really do recur
- no, the remaining `n3` support is not concentrated tightly enough to justify a trio-only ablation
- the stronger next bounded experiment should therefore widen slightly to a compact morphology-focused exclusion set (`mean`, `max`, `ptp`, `zero_crossing_rate`, plus the recurring trio) on the same repaired scaffold
