# Pass 37 — tiny amplitude-stabilization audit on the fixed pass36 EMG table

Date: 2026-05-05
Status: bounded post-pass36 representation audit completed. One tiny post-table change was tested on the exact repaired five-subject composed scaffold: upper-clip only `mean, rectified_std, envelope_cv` at `2.5` while keeping selected rows, train-time exclusions, shape block, model family, and evaluation contract fixed.

## Hypothesis

The catastrophic early `brux1` trio is being over-penalized by a very small recurring subset of record-relative amplitude / dispersion columns that spike far above the same subject's later windows: `mean, rectified_std, envelope_cv`. If those three positive record-relative values are softly upper-clipped at `2.5`, the early `brux1` windows should become less catastrophically negative without reopening the repaired control surface or disturbing the pass36 shape contribution.

## Exact tiny change

- Start from the existing pass36 composed table, not a new selector or channel.
- Clip only these three columns after the pass36 composition step: `mean, rectified_std, envelope_cv`.
- Clip rule: `x := min(x, 2.5)`.
- Leave the rest of the pass36 feature table unchanged, including the compact shape block and all non-target amplitude / dispersion columns.

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass37_tiny_amplitude_stabilization_audit.py`
- Stabilized feature table: `projects/bruxism-cap/data/window_features_pass37_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_ampcap.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass37-emg-a1-pct10-90-record-relative-shape-ampcap.json`
- Summary JSON: `projects/bruxism-cap/reports/pass37-tiny-amplitude-stabilization-audit.json`
- Summary report: `projects/bruxism-cap/reports/pass37-tiny-amplitude-stabilization-audit.md`

## Apples-to-apples comparison against unchanged pass36

### Scaffold parity
- baseline pass36 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- clipped pass37 rows per subject: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
- train-time exclusions unchanged: `['bp_delta', 'rel_bp_delta', 'bp_theta', 'rel_bp_theta', 'bp_alpha', 'rel_bp_alpha', 'bp_beta', 'rel_bp_beta', 'ratio_theta_beta', 'ratio_alpha_beta', 'ratio_alpha_delta']`
- clipped features only: `['mean', 'rectified_std', 'envelope_cv']`

### Subject-level LOSO summary
- baseline balanced accuracy: `0.750`
- clipped balanced accuracy: `0.750`
- baseline sensitivity: `0.500`
- clipped sensitivity: `0.500`
- baseline specificity: `1.000`
- clipped specificity: `1.000`

Subject score deltas:
- `brux1`: baseline `0.112` -> clipped `0.118` (delta `+0.006`) | predicted `control` -> `control`
- `brux2`: baseline `0.808` -> clipped `0.823` (delta `+0.015`) | predicted `bruxism` -> `bruxism`
- `n3`: baseline `0.068` -> clipped `0.090` (delta `+0.021`) | predicted `control` -> `control`
- `n5`: baseline `0.385` -> clipped `0.374` (delta `-0.011`) | predicted `control` -> `control`
- `n11`: baseline `0.489` -> clipped `0.484` (delta `-0.005`) | predicted `control` -> `control`

## What happened to the early `brux1` trio

- early ranks `1-3` mean score: `2.14e-82` -> `2.23e-71`
- early ranks `1-3` amp/disp mean: `-205.274` -> `-169.619`
- mid ranks `4-7` mean score: `0.200` -> `0.214`
- late ranks `8-10` mean score: `0.105` -> `0.107`

Early-window detail:
- rank `1` | window `3` | start `3500s` | score `1.63e-97` -> `1.59e-74` | amp/disp `-227.752` -> `-174.211` | shape after clip `+1.002` | other after clip `+4.897`
- rank `2` | window `5` | start `3560s` | score `4.56e-84` -> `2.02e-72` | amp/disp `-196.537` -> `-169.091` | shape after clip `+0.692` | other after clip `+4.931`
- rank `3` | window `7` | start `4370s` | score `6.37e-82` -> `6.49e-71` | amp/disp `-191.532` -> `-165.555` | shape after clip `+0.537` | other after clip `+5.019`

## Did `brux1` improve without reopening `n3` / `n5` / `n11`?

Mostly yes, but only modestly.

- `brux1` improves from `0.112` to `0.118` (`+0.006`), so the tiny cap helps rather than hurts the target subject.
- `n5` falls from `0.385` to `0.374` and `n11` falls from `0.489` to `0.484`, so those two control gaps narrow modestly.
- `n3` rises from `0.068` to `0.090`, but it still stays below `brux1` (`brux1 - n3 = +0.028`), so the old `n3` reversal does not reopen.
- No control flips positive, `brux2` stays strongly positive, and subject-level specificity remains `1.000`.

Gap check after clipping:
- `brux1 - n3`: `+0.028`
- `n5 - brux1`: `+0.257`
- `n11 - brux1`: `+0.366`

## Verdict

This tiny stabilization rule is directionally helpful but not sufficient. It reduces the early `brux1` trio's average amplitude / dispersion penalty from `-205.274` to `-169.619` and lifts `brux1` modestly, while preserving the pass36 subject-level verdict (`0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity). But the trio remains catastrophically near zero and `brux1` still stays far below threshold, so the post-table clip softens the collapse without actually fixing it.

## Safest next bounded step

Keep the same repaired five-subject scaffold and test one equally narrow stabilization move one stage earlier in the same feature family: apply a bounded robust-scale-floor audit for `mean, rectified_std, envelope_cv` inside the pass34 record-relative transform before the pass35 shape merge, then rerun the exact same pass36 composition surface. This stays apples-to-apples while checking whether the remaining collapse comes from the record-relative scale construction itself rather than only from a few post-table outliers.

## Explicitly rejected broader move

Rejected move: another channel pivot or a broader feature-family expansion.

Why rejected:
- this audit already answered the current narrow question on the exact pass36 surface,
- the tiny clip preserved `brux2` and the control verdict, so the open issue is still a localized `brux1` stabilization problem rather than a reason to broaden the benchmark,
- a broader move now would blur whether the remaining failure comes from the record-relative construction itself or from unrelated new features.
