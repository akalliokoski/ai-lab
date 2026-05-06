---
title: Bruxism CAP pass39 envelope-CV plus mean scale-floor audit
date: 2026-05-05
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [dataset, evaluation, experiment, workflow, notes]
sources:
  - ../projects/bruxism-cap/reports/pass39-envelope-cv-mean-scale-floor-audit.md
  - ../projects/bruxism-cap/reports/pass39-envelope-cv-mean-scale-floor-audit.json
  - ../projects/bruxism-cap/reports/pass38-envelope-cv-scale-floor-audit.md
  - ../projects/bruxism-cap/reports/pass37-tiny-amplitude-stabilization-audit.md
  - ../projects/bruxism-cap/reports/pass36-brux1-vs-n5-n11-fold-audit.md
  - ../projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit.md
---

# Bruxism CAP pass39 envelope-CV plus mean scale-floor audit

Question: after pass38 showed that `envelope_cv` scale alone was too weak, does applying the same earlier-stage robust-scale floor to `envelope_cv` plus the strongest remaining recurring offender, `mean`, improve `brux1` without reopening the repaired control surface? [[bruxism-cap]] [[bruxism-cap-pass38-envelope-cv-scale-floor-audit-2026-05-05]] [[bruxism-cap-pass37-tiny-amplitude-stabilization-audit-2026-05-05]]

## Answer

Not materially. `mean` was the right bounded companion feature to test, but the paired earlier-stage floor still does not beat the simpler pass37 post-table clip and does not change the honest benchmark verdict.

The choice of `mean` over `rectified_std` is strongly justified by the pass36 fold audit itself. Against `n5`, `mean` contributes `+46.576` to the `n5 - brux1` gap while `rectified_std` contributes only `+3.797`; against `n11`, `mean` contributes `+46.632` while `rectified_std` contributes only `+3.840`. The corresponding record-relative z-mean deltas are also far larger for `mean` (`-655.648` vs about `-13.878` / `-13.876`). So pass39 tests the most dominant remaining offender without broadening beyond one added feature inside the same record-relative amplitude block. [[bruxism-cap-brux1-localization-after-pass36-2026-05-05]]

Pass39 keeps the scaffold fully apples-to-apples with pass36, pass37, and pass38: the same repaired five-subject `EMG1-EMG2` `A1-only` percentile-band rows, the same train-time exclusions, the same compact pass35 shape merge, and the same `logreg` LOSO interpretation surface. The only change is earlier-stage: recompute `envelope_cv` and `mean` with `z := (x - median) / max(MAD, 0.5 * q90(|x - median|), 1e-06)` inside the pass34-style record-relative transform. Under that exact comparison, `brux1` reaches only `0.114`, versus `0.112` on pass36, `0.118` on pass37, and `0.115` on pass38. `n3` stays safely below it at `0.067`, while `n5` and `n11` stay high at `0.386` and `0.490`. Balanced accuracy, sensitivity, and specificity remain fixed at `0.750`, `0.500`, and `1.000`. [[bruxism-cap-emg-a1-record-relative-audit-2026-05-05]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]]

## What changed inside the early `brux1` trio

The paired floor softens the catastrophic early three-window collapse more than pass38 did, but the gain still fails to matter at the subject level.

- Early `brux1` ranks `1-3` mean score rises from about `2.14e-82` on pass36 to `3.79e-65` on pass39.
- Early `brux1` amplitude / dispersion mean contribution improves from `-205.274` on pass36 to `-162.058` on pass39.
- That early-window recovery is better than pass38 and roughly competitive with the direction seen in pass37, but the later `brux1` windows remain in the same weak band and the final subject mean still reaches only `0.114`.
- The old `n3` reversal does not reopen, but the `n5` / `n11` bottleneck remains essentially unchanged.

So pass39 narrows the diagnosis again: the dominant early collapse really does involve the `mean` scale surface, but fixing `mean` together with `envelope_cv` still is not enough to move the benchmark in a threshold-relevant way.

## Why this is useful project state

Pass39 closes the strongest remaining two-feature explanation that was still compatible with the earlier audits.

- It confirms that the repo tested the most dominant residual offender next, not just another arbitrary amplitude feature.
- It shows that even a correctly targeted paired floor leaves the subject-level verdict unchanged and still does not beat the simpler pass37 clip.
- It therefore preserves a sharper negative result: the remaining `brux1` miss is not solved by `envelope_cv` plus `mean` scale alone, even though those features do account for much of the catastrophic early suppression.

## Best next bounded step

Keep the same repaired five-subject scaffold and stay inside the same earlier-stage record-relative family, but swap the companion floor feature once: preserve this `mean` result as evidence, then test the same bounded floor on `envelope_cv` plus `rectified_std` while keeping the pass35 shape merge, selected rows, and evaluation contract fixed.

## Explicitly rejected broader move

Do not treat pass39 as a reason to pivot channels, broaden the feature family, or activate the privacy / LLM branches. The pass39 result is still a localized stabilization read on the same scaffold, not a benchmark-resolution or branch-handoff moment. [[bruxism-cap-campaign-handoff-2026-05-05]] [[bruxism-cap-privacy-threat-model-activation-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]]
