# Pass 36 follow-up — localizing the remaining `brux1` failure on the repaired `A1-only` EMG scaffold

Date: 2026-05-05
Status: bounded post-pass36 audit completed; no selector, channel, model-family, or feature-family expansion was introduced. This memo localizes why `brux1` still fails after the pass34 + pass35 composition while `brux2` now clears threshold.

## Scope
- Keep the repaired five-subject `SLEEP-S2 + MCAP-A1-only` percentile-band scaffold fixed.
- Keep the exact pass36 composed feature table and `logreg` LOSO interpretation surface fixed.
- Compare `brux1` directly against `n3`, `n5`, and `brux2` on the same repaired scaffold.
- Treat negative findings as first-class results rather than forcing a new broader patch.

## 1) Current `brux1`-specific bottleneck

The repaired scaffold is no longer failing generically. After pass36, `brux2` becomes a true positive (`0.808`) and `n3` is pushed far down (`0.068`), but `brux1` falls further to `0.112` with `0/10` positive windows.

So the remaining bottleneck is now narrower than "EMG cannot separate bruxism from controls":
- `brux1` is no longer mainly an `n3` inversion problem on this scaffold, because `brux1` now sits slightly above `n3` (`0.112` vs `0.068`, gap `-0.043` for `n3 - brux1`).
- `brux1` is now a low-score collapse problem relative to the whole repaired pass36 surface: it still trails `n5` (`0.385`) by `0.274`, trails `n11` (`0.489`) by `0.377`, trails `brux2` (`0.808`) by `0.696`, and remains `0.388` below the fixed `0.5` subject threshold.
- This means the pass36 gain is carried by a `brux2` rescue plus control suppression, not by a full two-subject bruxism recovery.

## 2) Evidence on the exact repaired scaffold

### Subject-score progression across the repaired scaffold family
- `brux1`: pass28 `0.270` -> pass34 `0.180` -> pass35 `0.216` -> pass36 `0.112`
- `brux2`: pass28 `0.036` -> pass34 `0.480` -> pass35 `0.399` -> pass36 `0.808`
- `n3`: pass28 `0.530` -> pass34 `0.439` -> pass35 `0.225` -> pass36 `0.068`
- `n5`: pass28 `0.291` -> pass34 `0.379` -> pass35 `0.387` -> pass36 `0.385`

### `brux1` versus `n3`
- pass30 framed `brux1 < n3` as the shared cross-channel hard case on the repaired scaffold.
- pass35 nearly erased that gap (`n3 - brux1 = +0.009`).
- pass36 flips it slightly in `brux1`'s favor (`n3 - brux1 = -0.043`).
- Therefore `n3` is no longer the main remaining blocker for `brux1` on the composed scaffold.

### `brux1` versus `n5`
- pass28: `n5 - brux1 = +0.021`
- pass34: `n5 - brux1 = +0.199`
- pass35: `n5 - brux1 = +0.171`
- pass36: `n5 - brux1 = +0.274`

Unlike the `n3` gap, the `n5` gap widens materially once the record-relative transform is introduced and stays wide after composition. That makes the remaining failure look more like a `brux1` under-scoring problem than a single surviving `n3` artifact.

### `brux1` versus `brux2`
- pass28: `brux2 - brux1 = -0.234`
- pass34: `brux2 - brux1 = +0.300`
- pass35: `brux2 - brux1 = +0.182`
- pass36: `brux2 - brux1 = +0.696`

The pass36 composition creates a strong within-bruxism split: the same scaffold that rescues `brux2` pushes `brux1` even lower. This is the cleanest evidence that the remaining error is now brux1-specific rather than a generic EMG collapse.

## 3) Which feature families now look `brux1`-specific rather than generic EMG problems

### Record-relative amplitude / dispersion family still drags `brux1`
On pass36, the strongest positive contribution deltas against `brux1` are still concentrated in the same broad record-relative amplitude / dispersion family:
- `mean` contribution delta toward `n3` over `brux1`: `+46.577`
- `rectified_std`: `+3.803`
- `envelope_cv`: `+1.422`
- `p95_abs`: `+0.854`
- `ptp`: `+0.831`
- `kurtosis`: `+0.674`

The same pattern also appears for `n5` over `brux1`:
- `mean`: `+46.576`
- `rectified_std`: `+3.797`
- `envelope_cv`: `+1.424`
- `p95_abs`: `+0.847`
- `ptp`: `+0.834`

So the remaining failure is not just one surviving `n3`-favoring control artifact. The broad record-relative amplitude / dispersion surface now suppresses `brux1` relative to multiple non-bruxism subjects.

### Shape features help `brux2` more than `brux1`
Against `brux1`, `brux2` gains extra support from the added shape block, especially:
- `hjorth_mobility`: `+2.306`
- `kurtosis`: `+0.254`

By contrast, the features that still push back toward `brux1` are smaller or mixed (`skewness`, `hjorth_complexity`, `rectified_mean`, `envelope_mean`). This suggests the compact shape family is not generically bad for EMG; it is asymmetric, helping `brux2` much more than `brux1`.

### What no longer looks like the main story
- A pure `n3` control inversion is no longer the main pass36 story, because `n3` is already below `brux1`.
- A narrow trio-only control family (`sample_entropy`, `burst_fraction`, `envelope_cv`) is not enough to explain the remaining miss; pass31 already showed the repaired scaffold was broader than that, and pass36 keeps the dominant weight on the wider amplitude / dispersion block.

## 4) Safest next bounded benchmark increment

Keep the exact repaired five-subject pass36 scaffold fixed and do one more localization-first increment, not a broad new rerun:
- audit `brux1` versus `n5` and `n11` fold-by-fold on the existing pass36 table,
- verify whether the miss is uniformly low across all `10` `brux1` windows or concentrated in a small subset,
- and quantify whether the dominant failure is specifically the record-relative amplitude / dispersion block (`mean`, `ptp`, `rectified_std`, `envelope_cv`, `p95_abs`) rather than the added Hjorth / shape block.

This is the safest next increment because pass36 already answered the larger composition question. The next uncertainty is not whether another broad family might help; it is whether the remaining miss is a stable `brux1` representation problem on the current fixed scaffold.

## 5) Explicitly rejected broader pivot

Rejected pivot: switch the active benchmark loop to `C4-P4` or another broader channel pivot now.

Why rejected:
- pass30 already showed the repaired scaffold's cross-channel difference is driven mainly by `brux2`, not by a clean `brux1` resolution;
- pass35's matched `C4-P4` record-relative comparator also behaved differently enough that a channel switch would blur the exact pass36 EMG-localization result;
- the current question is now narrow and answerable on the fixed EMG scaffold, so a channel pivot would reduce apples-to-apples interpretability precisely when the benchmark has become specific enough to localize.

## Bottom line

Pass36 converts the repaired scaffold from a generic EMG failure into a narrower subject-specific one. `brux2` is rescued and `n3` is no longer the dominant blocker, but `brux1` remains suppressed by the same broad record-relative amplitude / dispersion surface that helped clean up the controls. The next bounded step should therefore stay on the fixed pass36 scaffold and explain that `brux1` under-scoring directly, not pivot away from the benchmark.