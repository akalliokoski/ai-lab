---
title: Bruxism CAP pass37 tiny amplitude stabilization audit
date: 2026-05-05
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [dataset, evaluation, experiment, workflow, notes]
sources:
  - ../projects/bruxism-cap/reports/pass37-tiny-amplitude-stabilization-audit.md
  - ../projects/bruxism-cap/reports/pass37-tiny-amplitude-stabilization-audit.json
  - ../projects/bruxism-cap/reports/pass39-envelope-cv-mean-scale-floor-audit.md
  - ../projects/bruxism-cap/reports/pass39-envelope-cv-mean-scale-floor-audit.json
  - ../projects/bruxism-cap/reports/pass36-brux1-vs-n5-n11-fold-audit.md
  - ../projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit.md
---

# Bruxism CAP pass37 tiny amplitude stabilization audit

Question: on the exact repaired five-subject pass36 `EMG1-EMG2` `A1-only` composed scaffold, does one tiny amplitude-stabilization rule help the catastrophic early `brux1` three-window collapse without reopening the repaired control surface? [[bruxism-cap]] [[bruxism-cap-brux1-localization-after-pass36-2026-05-05]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]]

## Answer

Only modestly. A post-table upper clip on just three recurring record-relative amplitude / dispersion columns — `mean`, `rectified_std`, and `envelope_cv` capped at `2.5` — is directionally helpful but does not fix the benchmark bottleneck.

The tiny clip keeps the scaffold fully apples-to-apples with pass36: the same selected rows, the same five subjects, the same train-time exclusions, the same compact shape block, and the same `logreg` LOSO interpretation surface. Under that exact comparison, `brux1` improves from `0.112` to `0.118`, `n5` falls from `0.385` to `0.374`, and `n11` falls from `0.489` to `0.484`. `n3` rises from `0.068` to `0.090`, but it still stays below `brux1`, so the earlier `n3` reversal does not reopen. The overall honest verdict is unchanged: balanced accuracy stays `0.750`, sensitivity stays `0.500`, specificity stays `1.000`, and `brux2` remains strongly positive. [[bruxism-cap-emg-a1-record-relative-audit-2026-05-05]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]]

## What changed inside the early `brux1` trio

The clip clearly softens the exact failure surface that the pass36 fold audit localized, but only a little.

- Early `brux1` ranks `1-3` mean score rises from about `2.14e-82` to `2.23e-71`.
- Early `brux1` amplitude / dispersion mean contribution improves from `-205.274` to `-169.619`.
- Mid-window `brux1` mean score rises from `0.200` to `0.214`.
- Late-window `brux1` mean score rises from `0.105` to `0.107`.

So the tiny cap is working in the intended direction: it reduces the three-window penalty and nudges the later `brux1` windows upward too. But the decisive negative result is that the early trio still remains catastrophically close to zero and `brux1` still never approaches the `0.5` subject threshold. The bottleneck is therefore not just one or two post-table outliers; it still looks like a deeper issue in the record-relative amplitude construction itself. [[bruxism-cap-brux1-localization-after-pass36-2026-05-05]]

## Why this is still useful project state

This is a first-class negative-but-informative result rather than a dead end.

- It confirms that the live `brux1` bottleneck really is inside a tiny record-relative amplitude / dispersion subset, not in the compact shape block.
- It shows that a minimal post-table clip can preserve the repaired control verdict while slightly improving `brux1`, so the direction is not nonsense.
- It also shows that simple post-pass36 clipping is too weak to rescue the benchmark by itself, because the early trio stays essentially collapsed.

That combination narrows the next question again: the project should test whether the instability comes from how the pass34 record-relative transform is constructed, not from the later pass35 shape merge and not from a need to broaden the benchmark. [[bruxism-cap-emg-a1-record-relative-audit-2026-05-05]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]]

## Best next bounded step

Keep the same repaired five-subject scaffold and stay in the same narrow feature family, but move the stabilization test one stage earlier. The safest next audit is to keep the pass35 shape merge fixed and change only the pass34 record-relative construction for `mean`, `rectified_std`, and `envelope_cv` — for example by adding a bounded robust-scale floor before the pass36 composition rerun — so the repo can test whether the catastrophic early `brux1` trio is being created by the record-relative scaling step itself.

## Follow-through after the first earlier-stage floor audit

Pass38 answered that first follow-through question narrowly but clearly: moving the stabilization idea earlier for `envelope_cv` alone was weaker than this pass37 post-table clip. `brux1` reached only `0.115` on pass38 instead of `0.118` here, `n5` and `n11` drifted back upward, and the early three-window collapse stayed catastrophically close to zero. So this page should now be read as a bounded partial positive, not as evidence that the later clip is the main fix. The stronger lasting lesson is that the record-relative amplitude / dispersion block still dominates the remaining suppression and that single-feature `envelope_cv` scale is not enough by itself. [[bruxism-cap-pass38-envelope-cv-scale-floor-audit-2026-05-05]] [[bruxism-cap-brux1-localization-after-pass36-2026-05-05]]

The exact next benchmark task is therefore one equally bounded earlier-stage multi-feature audit on the same scaffold: keep the pass35 shape merge, selected rows, train-time exclusions, and evaluation contract fixed, and apply the same robust-scale-floor style to `envelope_cv` together with exactly one stronger recurring offender from the localized amplitude / dispersion block (`rectified_std` or `mean`).

## Follow-through after the bounded multi-feature floor audit

Pass39 closed that immediate follow-through question and sharpened how this page should be read. The paired earlier-stage floor on `envelope_cv + mean` softens the catastrophic early `brux1` trio more than pass38 did, but still not materially: the early amp/disp mean improves from `-194.660` on pass38 to `-162.058` on pass39 and the early three-window mean score rises from `4.61e-78` to `3.79e-65`, yet subject-level `brux1` still reaches only `0.114` and therefore stays below this simpler pass37 clip at `0.118`. [[bruxism-cap-pass39-envelope-cv-mean-scale-floor-audit-2026-05-05]]

That follow-through keeps the main lesson of pass37 intact. The early collapse can be softened without reopening the repaired `n3` surface, but the remaining threshold-relevant suppression still lives in the broader record-relative amplitude / dispersion block rather than in the later shape merge alone. `mean` is part of that collapse, but even the stronger two-feature earlier-stage floor leaves `n5` and `n11` essentially unchanged and does not rescue the benchmark. [[bruxism-cap-brux1-localization-after-pass36-2026-05-05]] [[bruxism-cap-pass39-envelope-cv-mean-scale-floor-audit-2026-05-05]]

The exact next benchmark task is now narrower again: keep the same repaired five-subject scaffold, selected rows, train-time exclusions, pass35 shape merge, and evaluation contract fixed, and run one last equally bounded earlier-stage audit that applies the same floor style to `envelope_cv + rectified_std`. Privacy implementation and LLM/RL or synthetic-data work remain gated until that final same-family benchmark follow-through reaches a handoff or temporary stabilization point. [[bruxism-cap-privacy-threat-model-activation-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]] [[bruxism-cap-campaign-handoff-2026-05-05]]

## Explicitly rejected broader move

Do not treat this modest improvement as a reason to pivot channels, add a larger feature family, or open the privacy / LLM branches. The pass37 clip preserved the exact pass36 verdict and only softened the localized `brux1` collapse. That means the correct next move is another equally narrow stabilization audit on the same scaffold, not a benchmark broadening step. [[bruxism-cap-campaign-handoff-2026-05-05]] [[bruxism-cap-privacy-threat-model-activation-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]]
