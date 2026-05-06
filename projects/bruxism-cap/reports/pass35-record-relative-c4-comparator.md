# Pass 35 — matched `C4-P4` comparator for the record-relative scaffold rebuild

Date: 2026-05-05
Status: matched comparison-channel rerun completed; rebuilt `C4-P4` on the same repaired percentile-band `A1-only` scaffold and applied the same within-record robust feature-space transform used in pass34 so the repo can separate representation effects from channel effects.

## Why this pass exists

Pass34 changed representation only on the repaired `EMG1-EMG2` scaffold. This comparator rebuild answers the follow-up question the same day:
- keep the same repaired `SLEEP-S2 + MCAP-A1-only` percentile-band subset
- keep the same train-time exclusions fixed: `^bp_, ^rel_bp_, ^ratio_`
- keep the same retained feature family and the same relative-feature transform list
- keep the same `logreg` LOSO evaluation contract
- change only the channel source (`C4-P4` baseline table instead of `EMG1-EMG2` baseline table)

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass35_record_relative_c4_comparator.py`
- Transformed feature table: `projects/bruxism-cap/data/window_features_pass35_c4_s2_mcap_a1_only_pct10_90_timepos10_record_relative.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass35-c4-a1-pct10-90-record-relative.json`
- Summary JSON: `projects/bruxism-cap/reports/pass35-record-relative-c4-comparator-summary.json`
- Summary report: `projects/bruxism-cap/reports/pass35-record-relative-c4-comparator.md`

## Scaffold matching confirmation
- Cross-channel selected rows still timing-match after the transform: `True`.
- Shared selector columns checked: `subject_id, window_index, start_s, end_s, relative_time_quantile, time_match_rank`.
- Selected trainable feature columns match pass34 EMG exactly: `True`.
- Relative feature list matches pass34 EMG exactly: `True`.
- Evaluation contract matches pass34 EMG (`logreg` LOSO with the same exclusion regex set): `True`.

## Honest LOSO subject-level comparison inside `C4-P4`
- baseline subject-level balanced accuracy: `0.750`
- relative subject-level balanced accuracy: `0.583`
- baseline subject-level sensitivity: `0.500`
- relative subject-level sensitivity: `0.500`
- baseline best-bruxism-minus-highest-control margin: `+0.542`
- relative best-bruxism-minus-highest-control margin: `+0.069`

Subject score deltas:
- `brux1`: baseline `0.405` -> relative `0.669` (delta `+0.263`) | predicted `control` -> `bruxism`
- `brux2`: baseline `0.959` -> relative `0.262` (delta `-0.697`) | predicted `bruxism` -> `control`
- `n3`: baseline `0.417` -> relative `0.600` (delta `+0.183`) | predicted `control` -> `bruxism`
- `n5`: baseline `0.212` -> relative `0.325` (delta `+0.113`) | predicted `control` -> `control`
- `n11`: baseline `0.188` -> relative `0.295` (delta `+0.107`) | predicted `control` -> `control`

## Comparator-focused score checks
- baseline `n3 - brux1` gap: `+0.012`
- relative `n3 - brux1` gap: `-0.069`
- baseline `brux2 - n3` gap: `+0.542`
- relative `brux2 - n3` gap: `-0.338`

## EMG-vs-C4 comparison on the same transformed scaffold
- pass34 EMG relative balanced accuracy: `0.500`
- pass35 C4 relative balanced accuracy: `0.583`
- pass34 EMG relative best-bruxism-minus-highest-control margin: `+0.041`
- pass35 C4 relative best-bruxism-minus-highest-control margin: `+0.069`
- pass34 EMG relative `brux2 - n3` gap: `+0.041`
- pass35 C4 relative `brux2 - n3` gap: `-0.338`

## Unavoidable divergences and warnings
- Baseline source tables and anchor reports are intentionally channel-specific (`pass28` EMG vs `pass29` C4), even though the repaired percentile-band subset and evaluation contract are matched.

## Interpretation
1. This comparator pass preserves the same scaffold logic as pass34, so any difference against the EMG rebuild is still interpretable as a channel/representation interaction rather than a selector drift.
2. If `C4-P4` stays stronger after the same transform, then the pass34 gain was not just “representation fixed everything”; it helped EMG, but the comparison channel still carries a stronger signal on this repaired benchmark.
3. If `C4-P4` weakens materially under the same transform, then the new representation may be specifically aligned with the EMG morphology failure rather than a universal scaffold improvement.
