---
title: Bruxism CAP pass38 envelope-CV scale-floor audit
date: 2026-05-05
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [dataset, evaluation, experiment, workflow, notes]
sources:
  - ../projects/bruxism-cap/reports/pass38-envelope-cv-scale-floor-audit.md
  - ../projects/bruxism-cap/reports/pass38-envelope-cv-scale-floor-audit.json
  - ../projects/bruxism-cap/reports/pass39-envelope-cv-mean-scale-floor-audit.md
  - ../projects/bruxism-cap/reports/pass39-envelope-cv-mean-scale-floor-audit.json
  - ../projects/bruxism-cap/reports/pass37-tiny-amplitude-stabilization-audit.md
  - ../projects/bruxism-cap/reports/pass36-brux1-vs-n5-n11-fold-audit.md
  - ../projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit.md
---

# Bruxism CAP pass38 envelope-CV scale-floor audit

Question: if the pass37 post-table clip was only a partial win, does moving one tiny stabilization idea earlier into the pass34-style record-relative transform help more? Specifically, can a bounded robust-scale floor on `envelope_cv` reduce the catastrophic early `brux1` collapse without reopening the repaired control surface? [[bruxism-cap]] [[bruxism-cap-pass37-tiny-amplitude-stabilization-audit-2026-05-05]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]]

## Answer

Only slightly, and less than pass37.

Pass38 keeps the same repaired five-subject `EMG1-EMG2` `A1-only` percentile-band scaffold, the same train-time exclusions, the same compact pass35 shape merge, and the same `logreg` LOSO interpretation surface. The only change is inside the earlier pass34-style record-relative transform: recompute `envelope_cv` with `z := (x - median) / max(MAD, 0.5 * q90(|x - median|), 1e-06)` instead of using the plain `MAD` scale alone. Under that exact apples-to-apples comparison, `brux1` rises only from `0.112` to `0.115`, while `n3` stays safely below it (`0.067`), `n5` remains at `0.386`, and `n11` remains at `0.490`. Balanced accuracy, sensitivity, and specificity all stay at `0.750`, `0.500`, and `1.000`. [[bruxism-cap-emg-a1-record-relative-audit-2026-05-05]] [[bruxism-cap-pass37-tiny-amplitude-stabilization-audit-2026-05-05]]

Compared with pass37, the earlier-stage floor is weaker on the target subject. Pass37 lifted `brux1` to `0.118` while also lowering `n5` and `n11`; pass38 falls back to `0.115` and lets both controls drift upward again. So this is a first-class negative-but-informative result: `envelope_cv` scale alone is not the main missing fix. [[bruxism-cap-pass37-tiny-amplitude-stabilization-audit-2026-05-05]]

## What changed inside the early `brux1` trio

The floor does reduce the `envelope_cv` over-amplification itself, but the overall early-window collapse barely moves.

- Early `brux1` ranks `1-3` mean score rise from about `2.14e-82` on pass36 to `4.61e-78` on pass38.
- Early `brux1` amplitude / dispersion mean contribution improves from `-205.274` to `-194.660`.
- That is still much weaker than pass37, which reached about `2.23e-71` and `-169.619` on the same early trio.
- The catastrophic windows therefore remain essentially near zero even after the tail-aware floor.

This matters because it narrows the diagnosis again: the live instability is not just that one `envelope_cv` denominator is too small. The broader record-relative amplitude / dispersion construction is still doing most of the damage. [[bruxism-cap-brux1-localization-after-pass36-2026-05-05]]

## Why this is useful project state

Pass38 closes a tempting single-feature explanation without broadening the benchmark.

- It shows that moving the stabilization idea earlier can help a little while preserving the repaired control surface.
- It also shows that a single-feature earlier-stage floor is not enough and does not beat the simpler pass37 clip.
- That means the next bounded question should remain inside the same feature family, but widen only one notch beyond this one-feature test rather than pivoting channels or adding a broad new feature block.

## Best next bounded step

Keep the same repaired five-subject scaffold and run one equally narrow multi-feature earlier-stage audit: apply the same style of robust-scale floor to `envelope_cv` plus exactly one stronger recurring offender from the localized audit, preferably `rectified_std` or `mean`, while keeping the pass35 shape merge and the full evaluation contract fixed.

## Follow-through after the bounded multi-feature floor audit

Pass39 answered the exact next-step proposal from this page and kept the verdict narrow but clearer. The bounded paired floor on `envelope_cv + mean` was the stronger immediate follow-through because the pass36 fold audit shows `mean` dominates the surviving `n5` / `n11` suppression versus `brux1` far more than `rectified_std` does. Even so, the result still did not materially soften the benchmark bottleneck: `brux1` reached only `0.114`, below both the pass37 clip (`0.118`) and essentially tied with this pass38 single-feature floor (`0.115`). [[bruxism-cap-pass39-envelope-cv-mean-scale-floor-audit-2026-05-05]]

The deeper diagnostic read therefore holds. Moving the stabilization earlier can help, and adding `mean` helps more than `envelope_cv` alone on the catastrophic early `brux1` trio, but the remaining threshold-relevant suppression still sits in the broader record-relative amplitude / dispersion block. `n5` and `n11` remain the active control-side bottleneck, and the repaired shape block still does not look like the dominant problem. [[bruxism-cap-brux1-localization-after-pass36-2026-05-05]] [[bruxism-cap-pass39-envelope-cv-mean-scale-floor-audit-2026-05-05]]

The exact next benchmark task is now the last equally bounded same-family follow-through: keep the repaired five-subject scaffold, selected rows, train-time exclusions, pass35 shape merge, and evaluation contract fixed again, and apply the same floor style to `envelope_cv + rectified_std`. The privacy branch and the LLM/RL future branch remain closed until that final bounded benchmark step reaches a real handoff or temporary stabilization point. [[bruxism-cap-privacy-threat-model-activation-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]] [[bruxism-cap-campaign-handoff-2026-05-05]]

## Explicitly rejected broader move

Do not treat this as a reason to pivot channels, expand the feature family broadly, or activate the privacy / LLM branches. Pass38 stays too small and too inconclusive for that; it sharpens the benchmark diagnosis instead of resolving it. [[bruxism-cap-campaign-handoff-2026-05-05]] [[bruxism-cap-privacy-threat-model-activation-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]]
