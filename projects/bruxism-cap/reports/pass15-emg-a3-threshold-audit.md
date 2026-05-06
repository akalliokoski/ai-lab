# Pass 15 — subject-threshold audit on matched `EMG1-EMG2` `SLEEP-S2 + MCAP-A3-only`

Date: 2026-05-04
Status: bounded EMG-first threshold audit completed; no subject threshold rescues the current `EMG1-EMG2` `A3-only` run without losing the honest baseline criterion

## Why this pass exists

Pass14 left one narrow follow-up question before any bigger modeling or feature change:
- keep the strongest current EMG run fixed (`EMG1-EMG2`, exclusive `SLEEP-S2 + MCAP-A3-only`, matched `14` windows per subject)
- keep the same best LOSO model fixed (`logreg`)
- test whether the failure is mainly a subject-threshold choice or a deeper score-ordering problem

This pass therefore makes exactly one bounded increment: a subject-score / threshold audit on the saved LOSO artifacts, with pass12 `C4-P4 A1-only` kept as the honest anchor.

## Artifacts

- Audit script: `projects/bruxism-cap/src/audit_subject_thresholds.py`
- Audit JSON: `projects/bruxism-cap/reports/subject-threshold-audit-pass15-emg-a3-vs-c4-a1.json`
- Primary LOSO report audited: `projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json`
- Anchor LOSO report: `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json`

## Command path verified

```bash
python3 projects/bruxism-cap/src/audit_subject_thresholds.py \
  --report projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json \
  --model logreg \
  --anchor-report projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json \
  --anchor-model logreg \
  --out projects/bruxism-cap/reports/subject-threshold-audit-pass15-emg-a3-vs-c4-a1.json
```

## Key result

The current EMG-first failure is **not** mainly a bad default threshold.

On the matched `5`-subject subset, the best bruxism subject score in the pass15 primary audit is `brux1 = 0.176`, but two controls still score higher:
- `n3 = 0.267`
- `n5 = 0.266`

So any threshold low enough to recover `brux1` also flips at least `n3` and `n5` to false positives.

`brux2` is even lower at `0.074`, below every control except the already-low `n11 = 0.095`, so any threshold that recovers both bruxism subjects collapses control specificity entirely.

## Threshold sweep summary

### Primary audit: `EMG1-EMG2` `A3-only` pass14 `logreg`
- Default subject threshold `0.5`:
  - sensitivity `0.000`
  - specificity `1.000`
  - balanced accuracy `0.500`
- Best threshold with **zero false positives**:
  - threshold just above `0.266954`
  - sensitivity `0.000`
  - specificity `1.000`
  - balanced accuracy `0.500`
- Best threshold with **any positive subject sensitivity** while still using the saved ranking:
  - threshold at or below `0.176298`
  - sensitivity `0.500`
  - specificity `0.333`
  - balanced accuracy `0.417`
  - predicted positive subjects: `brux1`, `n3`, `n5`
- Thresholds low enough to recover **both** bruxism subjects (`<= 0.074342`) predict every subject positive:
  - sensitivity `1.000`
  - specificity `0.000`
  - balanced accuracy `0.500`

### Honest anchor: `C4-P4` `A1-only` pass12 `logreg`
- Default threshold `0.5` already lies in a stable good region:
  - sensitivity `0.500`
  - specificity `1.000`
  - balanced accuracy `0.750`
- The anchor keeps a positive bruxism-vs-control score margin:
  - best bruxism minus highest control = `+0.362`
- The EMG audit does not:
  - best bruxism minus highest control = `-0.091`

## Interpretation

1. The pass14 EMG run is failing because the **subject ranking is wrong**, not because the default subject threshold is too strict.
2. `A3-only` did lower one control (`n11`) meaningfully, but it still leaves `n3` and `n5` above the best bruxism subject score.
3. This makes threshold tuning a dead end for the current saved EMG score surface: no threshold improves the honest baseline over the default `0.5` setting.
4. The pass12 `C4-P4 A1-only` anchor remains stronger because it creates one clearly separated positive subject (`brux2`) without crossing any controls.
5. This is a useful negative result to preserve: the next EMG-first move should target score ordering / feature validity, not threshold tweaking.

## Best next bounded step

Stay EMG-first and keep model complexity fixed.

The next bounded experiment should be a **feature-validity audit** on the same matched pass14 scaffold:
- compare per-subject feature summaries for `brux1`, `brux2`, `n3`, and `n5`
- identify which current handcrafted features push `n3` / `n5` above `brux1`
- test one small EMG-aligned feature-family patch only after that audit, rather than trying more threshold schedules

## Baseline verdict

This pass does **not** beat the current best honest baseline.

The best honest baseline remains pass12 `C4-P4 A1-only` because it keeps subject-level specificity at `1.000` while still recognizing `brux2` at the subject level.