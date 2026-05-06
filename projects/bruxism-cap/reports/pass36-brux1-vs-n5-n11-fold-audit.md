# Pass 36 follow-up — fold-by-fold `brux1` vs `n5` / `n11` audit on the exact composed EMG table

Date: 2026-05-05
Status: bounded extraction-only audit completed on the fixed pass36 `EMG1-EMG2` `A1-only` composed table. No selector, channel, feature-family, or benchmark rerun was introduced; the audit only rebuilds the existing held-out `logreg` folds to expose per-window scores and grouped contribution blocks.

## Artifacts
- Audit script: `projects/bruxism-cap/src/audit_pass36_brux1_vs_n5_n11.py`
- Audit JSON: `projects/bruxism-cap/reports/pass36-brux1-vs-n5-n11-fold-audit.json`
- Audit memo: `projects/bruxism-cap/reports/pass36-brux1-vs-n5-n11-fold-audit.md`
- Fixed feature table inspected: `projects/bruxism-cap/data/window_features_pass36_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape.csv`
- Existing benchmark report inspected: `projects/bruxism-cap/reports/loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json`

## 1) Fold-by-fold / window-group evidence on the exact current pass36 table

### Held-out subject score surface
- `brux1`: mean score `0.112` | range `1.63e-97` to `0.291` | positive windows `0/10`
- `n5`: mean score `0.385` | range `0.106` to `0.599` | positive windows `3/10`
- `n11`: mean score `0.489` | range `0.372` to `0.621` | positive windows `5/10`
- `n5 - brux1` subject gap: `+0.274`
- `n11 - brux1` subject gap: `+0.377`

### `brux1` window distribution
- score bins: `<0.1` = `4`, `0.1-0.2` = `5`, `0.2-0.3` = `1`, `0.3-0.5` = `0`, `>=0.5` = `0`
- early ranks `1-3`: mean score `2.14e-82` | amp/disp mean `-205.274` | shape mean `+0.795`
- mid ranks `4-7`: mean score `0.200` | amp/disp mean `+0.791` | shape mean `-0.095`
- late ranks `8-10`: mean score `0.105` | amp/disp mean `+0.526` | shape mean `-0.414`

The three earliest `brux1` windows are the decisive collapse point:
- rank `1` | window `3` | start `3500s` | score `1.63e-97` | amp/disp `-227.752` | shape `+1.040` | other `+5.493`
- rank `2` | window `5` | start `3560s` | score `4.56e-84` | amp/disp `-196.537` | shape `+0.758` | other `+5.518`
- rank `3` | window `7` | start `4370s` | score `6.37e-82` | amp/disp `-191.532` | shape `+0.587` | other `+5.624`

The best `brux1` windows are still sub-threshold:
- rank `7` | window `16` | start `9770s` | score `0.291` | amp/disp `+0.810` | shape `+1.042` | other `-1.105`
- rank `4` | window `10` | start `6050s` | score `0.199` | amp/disp `+0.478` | shape `+0.664` | other `-0.895`
- rank `6` | window `14` | start `8870s` | score `0.196` | amp/disp `+0.915` | shape `-1.108` | other `+0.418`

### Comparator window-group surfaces
- `n5` grouped means: early `0.370` | mid `0.442` | late `0.324`
- `n11` grouped means: early `0.415` | mid `0.539` | late `0.494`
- `n5` score bins: `<0.1` = `0`, `0.1-0.2` = `2`, `0.2-0.3` = `0`, `0.3-0.5` = `5`, `>=0.5` = `3`
- `n11` score bins: `<0.1` = `0`, `0.1-0.2` = `0`, `0.2-0.3` = `0`, `0.3-0.5` = `5`, `>=0.5` = `5`

## 2) Is the miss uniformly low or sparse-window low?

Not uniformly low, but also not a one-window fluke. The cleanest read is: `brux1` has a sparse catastrophic subset plus a weak residual floor.

- Sparse catastrophic subset: the earliest three held-out `brux1` windows score essentially zero (`~1.6e-97`, `~4.6e-84`, `~6.4e-82`) and alone pull the subject mean down hard.
- Residual weak floor: the remaining seven windows recover only to a `0.088` to `0.291` band, with no window even reaching `0.3` and no positive windows at all.
- Comparator contrast: `n5` already has `3/10` windows above `0.5`, while `n11` splits cleanly into `5/10` above and `5/10` below `0.5`.

So the remaining pass36 miss is best described as sparse-window low in its most extreme form, but still globally sub-threshold across all `10` `brux1` windows.

## 3) Does the remaining suppression live mainly in the record-relative amplitude / dispersion block or the added shape block?

It lives overwhelmingly in the record-relative amplitude / dispersion block, not in the added shape block.

### Block-level deltas versus `brux1`
- `n5 - brux1`: amp/disp `+60.638` | shape `-0.124` | other `-1.488`
- `n11 - brux1`: amp/disp `+61.265` | shape `+0.015` | other `-1.752`

### Top positive feature deltas keeping `n5` above `brux1`
- `mean` (amp_disp) contribution delta `+46.576` | z-mean delta `-655.648` | raw-mean delta `-0.783542`
- `rectified_std` (amp_disp) contribution delta `+3.797` | z-mean delta `-13.878` | raw-mean delta `-10.526547`
- `rms` (amp_disp) contribution delta `+2.428` | z-mean delta `-8.341` | raw-mean delta `-0.000011`
- `std` (amp_disp) contribution delta `+2.422` | z-mean delta `-8.320` | raw-mean delta `-0.000011`
- `min` (amp_disp) contribution delta `+2.117` | z-mean delta `+5.548` | raw-mean delta `+0.000093`
- `envelope_cv` (amp_disp) contribution delta `+1.424` | z-mean delta `-11.702` | raw-mean delta `-32.940846`
- `p95_abs` (amp_disp) contribution delta `+0.847` | z-mean delta `-4.242` | raw-mean delta `-6.554752`
- `ptp` (amp_disp) contribution delta `+0.834` | z-mean delta `-20.335` | raw-mean delta `-84.118473`

### Top positive feature deltas keeping `n11` above `brux1`
- `mean` (amp_disp) contribution delta `+46.632` | z-mean delta `-655.648` | raw-mean delta `-0.783413`
- `rectified_std` (amp_disp) contribution delta `+3.840` | z-mean delta `-13.876` | raw-mean delta `-10.511814`
- `rms` (amp_disp) contribution delta `+2.368` | z-mean delta `-8.168` | raw-mean delta `-0.000009`
- `std` (amp_disp) contribution delta `+2.362` | z-mean delta `-8.147` | raw-mean delta `-0.000009`
- `min` (amp_disp) contribution delta `+2.068` | z-mean delta `+5.409` | raw-mean delta `+0.000083`
- `envelope_cv` (amp_disp) contribution delta `+1.466` | z-mean delta `-11.668` | raw-mean delta `-32.144824`
- `ptp` (amp_disp) contribution delta `+0.898` | z-mean delta `-20.370` | raw-mean delta `-86.263671`
- `p95_abs` (amp_disp) contribution delta `+0.895` | z-mean delta `-4.320` | raw-mean delta `-6.959636`

### Important negative evidence against blaming the shape block
- For `n5 - brux1`, the net shape delta is slightly negative (`-0.124`), meaning the added shape block is mildly helping `brux1`, not suppressing it.
- For `n11 - brux1`, the net shape delta is almost zero (`+0.015`).
- Inside the catastrophic early `brux1` trio, amp/disp is massively negative (`-205.274`) while shape is actually positive (`+0.795`).

So the audit-local answer is unambiguous: the remaining suppression is still the record-relative amplitude / dispersion surface, led by `mean`, `rectified_std`, `rms`, `std`, `min`, `envelope_cv`, `ptp`, and `p95_abs`.

## 4) Safest next bounded benchmark increment

Keep the exact repaired five-subject pass36 scaffold fixed again and do one narrower representation audit before any new rerun:
- isolate the catastrophic early `brux1` trio (ranks `1-3`) against the same subject's mid / late windows,
- test whether one bounded cap or robust clipping rule on the record-relative amplitude / dispersion family can prevent those three windows from dominating the held-out fold,
- keep the same selected rows, same model family, same train-time exclusions, and same shape block fixed so the result stays apples-to-apples with pass36.

This is the safest next increment because this audit shows the remaining uncertainty is not about the Hjorth add-on at all; it is about whether a very small amplitude/dispersion stabilization patch can remove the catastrophic `brux1` under-scoring without disturbing the real `brux2` rescue.

## 5) Explicitly rejected broader move

Rejected move: launch another channel pivot or broader feature-family expansion now.

Why rejected:
- the exact current pass36 table already answers the composition question and this follow-up audit now localizes the remaining miss to one dominant block,
- a channel pivot would blur the new finding that the catastrophic `brux1` collapse is already visible inside the fixed EMG scaffold,
- a broader feature expansion would hide whether the unresolved issue was actually the existing amplitude/dispersion surface all along.

## Bottom line

The pass36 miss is no longer best read as a uniform low-score brux1 subject or as a Hjorth-shape failure. It is a fixed-table, fold-localized problem: three early `brux1` windows catastrophically collapse under the record-relative amplitude / dispersion surface, and the remaining seven windows never recover enough to reach threshold. That makes one more amplitude-stabilization audit the safest next benchmark increment, while channel pivots and broader feature growth should stay out of scope for the next step.
