---
title: Bruxism CAP pass40 envelope_cv + rectified_std scale-floor audit
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [dataset, evaluation, experiment, workflow, notes]
sources:
  - ../concepts/bruxism-cap.md
  - ../../projects/bruxism-cap/reports/pass40-envelope-cv-rectified-std-scale-floor-audit.md
---

# Bruxism CAP pass40 envelope_cv + rectified_std scale-floor audit

Pass40 was the final bounded same-family follow-through after pass39 on the repaired five-subject percentile-band `EMG1-EMG2` `A1-only` scaffold. It kept the pass35 shape merge, selected rows, train-time exclusions, and `logreg` LOSO contract fixed, and changed only one earlier-stage representation detail: apply the pass38/pass39 robust-scale floor to `envelope_cv + rectified_std` inside the pass34-style record-relative transform.

## Why this pass was still worth running

[[bruxism-cap-pass39-envelope-cv-mean-scale-floor-audit-2026-05-05]] already showed that `mean` was the stronger offender to test first, but it still did not beat [[bruxism-cap-pass37-tiny-amplitude-stabilization-audit-2026-05-05]]. The last unresolved same-family question was whether swapping only the companion feature to `rectified_std` could help `brux1` without reopening the repaired control surface from [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]].

## Result

- Subject-level verdict stayed unchanged at balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`.
- `brux1` was effectively flat versus pass36 (`0.112` -> `0.112`) and worse than pass37 (`0.118`), pass38 (`0.115`), and pass39 (`0.114`).
- `n3` did not formally reopen, but the margin shrank to `brux1 - n3 = +0.006`.
- `n5` and `n11` stayed above `brux1` by `+0.261` and `+0.361` respectively.
- The catastrophic early `brux1` trio softened relative to pass36 and pass38, but not as much as pass39: early amp/disp mean moved from `-205.274` (pass36) to `-194.660` (pass38) to `-162.058` (pass39) to `-182.086` (pass40).

## Interpretation

The important preserved lesson is not that `rectified_std` beat `mean`; it did not. The stronger pass39 conclusion still holds: `mean` was the right stronger offender to test first. Pass40 closes the bounded floor subloop by showing that swapping the companion feature does not materially improve `brux1`, so this exact earlier-stage floor family now looks exhausted as a benchmark-rescue idea on the repaired scaffold. [[bruxism-cap-pass39-envelope-cv-mean-scale-floor-audit-2026-05-05]] [[bruxism-cap-brux1-localization-after-pass36-2026-05-05]]

## Safest next bounded increment

Preserve [[bruxism-cap-pass37-tiny-amplitude-stabilization-audit-2026-05-05]] as the safest bounded stabilization surface inside the current scaffold, but stop extending this exact `envelope_cv` companion-floor family. The next bounded increment should be one new representation question outside this exact same-family floor subloop.

## Explicitly rejected broader move

Do not use pass40 as a reason to pivot channels, broaden features, or activate privacy / LLM / synthetic-data work. The pass is still a localized negative result on the current benchmark scaffold rather than a handoff signal. [[bruxism-cap-campaign-handoff-2026-05-05]] [[bruxism-cap-privacy-threat-model-activation-2026-05-05]]
