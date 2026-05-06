---
title: Bruxism CAP brux1 localization after pass36
date: 2026-05-05
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [dataset, evaluation, experiment, workflow, notes]
sources:
  - ../projects/bruxism-cap/reports/pass36-brux1-localization-audit.md
  - ../projects/bruxism-cap/reports/pass36-brux1-vs-n5-n11-fold-audit.md
  - ../projects/bruxism-cap/reports/pass36-brux1-vs-n5-n11-fold-audit.json
  - ../projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit.md
  - ../projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit-summary.json
  - ../projects/bruxism-cap/reports/pass34-record-relative-emg-audit.md
  - ../projects/bruxism-cap/reports/pass35-shape-feature-expansion.md
---

# Bruxism CAP brux1 localization after pass36

Question: after the repaired five-subject `A1-only` EMG scaffold finally composes pass34 record-relative normalization with the compact pass35 shape family, why does `brux1` still fail even though `brux2` now clears threshold? [[bruxism-cap]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]] [[bruxism-cap-emg-a1-record-relative-audit-2026-05-05]] [[bruxism-cap-emg-a1-shape-feature-expansion-2026-05-05]]

## Answer

The remaining failure is now `brux1`-specific, not a generic repaired-scaffold EMG collapse.

On pass36, `brux2` rises to `0.808` and becomes a clean true positive while `n3` falls to `0.068`. `brux1`, however, drops further to `0.112` with `0/10` positive windows. That means the old `n3 > brux1` story is largely resolved on the composed scaffold; the unresolved problem is instead that `brux1` stays broadly under-scored relative to both `n5` (`0.385`) and the highest control `n11` (`0.489`) while `brux2` is strongly rescued. [[bruxism-cap-a1-percentile-band-channel-gap-audit-2026-05-05]] [[bruxism-cap-a1-percentile-band-n3-family-recurrence-2026-05-05]]

This changes the project understanding in one narrow but important way: the live benchmark question is no longer whether pass34 record-relative normalization and the pass35 compact shape family compose honestly on the repaired scaffold. Pass36 already answered that composition question. The active benchmark bottleneck is now specifically why `brux1` stays low against `n5` and `n11` on the exact composed table, even after `brux2` is rescued and `n3` is suppressed. That keeps the campaign handoff logic intact but updates the exact next task from a composition rerun to a localization-first audit on the already-composed scaffold. [[bruxism-cap-campaign-handoff-2026-05-05]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]]

## Evidence that the bottleneck narrowed
- `brux1` score path: pass28 `0.270` -> pass34 `0.180` -> pass35 `0.216` -> pass36 `0.112`
- `brux2` score path: pass28 `0.036` -> pass34 `0.480` -> pass35 `0.399` -> pass36 `0.808`
- `n3` score path: pass28 `0.530` -> pass34 `0.439` -> pass35 `0.225` -> pass36 `0.068`
- `n5` score path: pass28 `0.291` -> pass34 `0.379` -> pass35 `0.387` -> pass36 `0.385`

The key gap changes are:
- `n3 - brux1`: `+0.260` -> `+0.259` -> `+0.009` -> `-0.043`
- `n5 - brux1`: `+0.021` -> `+0.199` -> `+0.171` -> `+0.274`
- `brux2 - brux1`: `-0.234` -> `+0.300` -> `+0.182` -> `+0.696`

So pass36 solves the earlier `brux2` and `n3` problems much more than it solves `brux1` itself.

## What still appears to suppress `brux1`

The dominant pass36 contribution deltas against `brux1` still come from the broad record-relative amplitude / dispersion family, not from a generic all-feature failure:
- `mean`
- `rectified_std`
- `envelope_cv`
- `p95_abs`
- `ptp`
- with `kurtosis` as a smaller extra shape-term contributor

This pattern shows up for both `n3 > brux1` and `n5 > brux1`, which means the remaining miss is not only one surviving `n3` artifact. At the same time, the compact shape block helps `brux2` more than `brux1`, especially through `hjorth_mobility`, creating a strong within-bruxism split rather than a clean two-subject recovery.

## Deeper fold-by-fold answer

The follow-up fold-level audit on the exact pass36 table tightened the localization again instead of changing the benchmark frame. `brux1` is not uniformly low across all `10` windows, but it is also not one noisy outlier. The strongest read is: a sparse catastrophic subset plus a weak residual floor.

- The earliest three held-out `brux1` windows collapse almost to zero (`~1.6e-97`, `~4.6e-84`, `~6.4e-82`) and are the decisive drop in the subject mean.
- The remaining seven `brux1` windows recover only into a `0.088` to `0.291` band, so none reach threshold and none even clear `0.3`.
- `n5` already has `3/10` windows above `0.5`, and `n11` has `5/10` above `0.5`, so the control-side surface is not just marginally higher on average; it contains real threshold-crossing windows that `brux1` never reaches.

The same deeper audit also makes the block attribution clearer than before. Against `brux1`, the net contribution deltas are overwhelmingly in the record-relative amplitude / dispersion family, not in the added shape block:
- `n5 - brux1`: amp/disp `+60.638`, shape `-0.124`, other `-1.488`
- `n11 - brux1`: amp/disp `+61.265`, shape `+0.015`, other `-1.752`

So the added Hjorth/shape block is not the main suppressor here. In fact, on the catastrophic early `brux1` trio the shape block is mildly positive while the amplitude / dispersion block is massively negative, and the leading repeat offenders are still `mean`, `rectified_std`, `rms`, `std`, `min`, `envelope_cv`, `ptp`, and `p95_abs`.

## Best next bounded step

Keep the exact pass36 scaffold fixed and move one step narrower from localization to stabilization: isolate the catastrophic early `brux1` trio against the same subject's mid/late windows, then run one amplitude-stabilization audit on the record-relative amplitude / dispersion family while keeping the selected rows, model family, train-time exclusions, and shape block fixed.

The exact next benchmark task is: on the fixed pass36 table, compare the early `brux1` trio against the same subject's later windows and test one very small cap or robust clipping rule on the record-relative amplitude / dispersion block, without adding a new rerun, channel comparison, or broader feature-family growth.

## Follow-through after pass37 and pass38

The two bounded follow-ups sharpen this localization rather than weakening it. Pass37 softened the catastrophic early `brux1` trio only modestly, and pass38's earlier-stage single-feature floor on `envelope_cv` was weaker still. Across both follow-ups, the early collapse never softened materially, `n5` and `n11` stayed the active control-side bottleneck, and the net suppression signal remained centered in the record-relative amplitude / dispersion block rather than in the added shape family. [[bruxism-cap-pass37-tiny-amplitude-stabilization-audit-2026-05-05]] [[bruxism-cap-pass38-envelope-cv-scale-floor-audit-2026-05-05]]

That means this page's core diagnosis still stands, but its next-step wording should now be read more specifically: keep the same repaired scaffold and move to one equally bounded earlier-stage multi-feature floor audit that pairs `envelope_cv` with exactly one stronger recurring offender such as `rectified_std` or `mean`, instead of repeating a post-table clip or broadening the benchmark frame.

## Future-branch gate status after this audit

Neither future branch moved here; both remain preserved in the wiki but closed as board work.

The privacy branch did not move from gated memo state to active implementation state. The next privacy task is still exactly `privacy: design a minimized off-device export schema for future wearable bruxism-cap experiments`, but that gate remains closed until the current benchmark reaches a handoff or temporary stabilization point after this bounded amplitude-stabilization follow-up. [[bruxism-cap-privacy-threat-model-activation-2026-05-05]] [[bruxism-cap-campaign-handoff-2026-05-05]]

The LLM/RL branch also did not move. The roadmap still stays wiki-first, and the first bounded promotion remains either `rl: write a repo-specific adaptive-biofeedback problem formulation and safety-shield memo for a future JawSense-style branch` or the synthetic-EMG comparison memo only after benchmark handoff or temporary stabilization. This fold audit does not justify activating either task yet. [[bruxism-cap-llm-rl-roadmap-2026-05-05]] [[bruxism-cap-campaign-handoff-2026-05-05]]

## Explicitly rejected broader pivot

Do not switch the active loop to `C4-P4` or another broader channel pivot yet. The repaired scaffold is finally specific enough that the repo can localize the remaining EMG error directly; a channel pivot now would blur the exact `brux1` failure surface instead of explaining it. [[bruxism-cap-c4-record-relative-comparator-2026-05-05]] [[bruxism-cap-translational-framing-check-2026-05-05]]
