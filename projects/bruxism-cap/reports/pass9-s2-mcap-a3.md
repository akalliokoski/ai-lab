# Pass 9 — narrower `SLEEP-S2 + MCAP-A3` rerun

Date: 2026-05-04
Status: bounded negative result; narrower overlap-family selection reduced random-split optimism a bit but did not improve honest held-out bruxism detection

## Why this pass exists

Pass8 showed that the pass7 mixed `S2+MCAP` subset was heterogeneous by subject and label. The next bounded experiment was therefore to keep the same verified 5-subject subset but narrow the overlap rule to a single CAP micro-event family.

This pass tests the smallest available version of that idea:
- keep only in-range `SLEEP-S2` windows
- require overlap with `MCAP-A3`
- keep `20` windows per subject
- reuse the current no-`n_samples` / no-`duration_s` training path in `src/train_baseline.py`

## Dataset used

- Feature CSV: `projects/bruxism-cap/data/window_features_pass9_s2_mcap_a3.csv`
- Subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- Labels: `2` bruxism subjects, `3` control subjects
- Channel: `C4-P4`
- Window seconds: `30`
- Windows per subject: `20`
- Total windows: `100`
- Extraction rule: in-range `SLEEP-S2` windows with `MCAP-A3` overlap

## Commands run

```bash
source .venv/bin/activate
python projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --annotation-txt projects/bruxism-cap/data/raw/capslpdb/brux1.txt \
  --annotation-events SLEEP-S2 \
  --require-overlap-events MCAP-A3 \
  --subject-id brux1 --label bruxism --channel C4-P4 \
  --window-seconds 30 --limit-windows 20 \
  --out projects/bruxism-cap/data/window_features_pass9_s2_mcap_a3.csv
# repeated with --append for brux2, n3, n5, n11

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass9_s2_mcap_a3.csv \
  --cv random \
  --out projects/bruxism-cap/reports/random-window-cv-pass9-s2-mcap-a3.json

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass9_s2_mcap_a3.csv \
  --cv loso \
  --out projects/bruxism-cap/reports/loso-cv-pass9-s2-mcap-a3.json
```

## Key results

### Random-window CV
- Best balanced accuracy: logistic regression `0.921`
- Best sensitivity: logistic regression / SVM `0.875`
- Best specificity: logistic regression / SVM `0.967`

### LOSO window-level CV
- Best balanced accuracy: random forest `0.550`
- Best sensitivity: logistic regression `0.020` and random forest `0.010`; SVM stayed `0.000`
- Best specificity: random forest `0.540`

### LOSO subject-level aggregation
- All three models stayed at subject balanced accuracy `0.500`
- All three models stayed at subject sensitivity `0.000`
- All three models stayed at subject specificity `1.000`

## Comparison to pass7 mixed `S2+MCAP`

Pass7 (`MCAP-A1|A2|A3` mixed overlap) versus pass9 (`MCAP-A3` overlap only):

- Random-window best balanced accuracy dropped from `1.000` to `0.921`
- LOSO best balanced accuracy dropped from `0.590` to `0.550`
- LOSO subject-level bruxism sensitivity stayed `0.000`

## Interpretation

This is a useful negative result, not an improvement:
1. Narrowing from the mixed CAP-overlap bucket to `MCAP-A3` overlap made random-window CV less unrealistically perfect, which is directionally good.
2. But the honest held-out result did **not** improve. LOSO stayed weak and subject-level bruxism detection remained completely absent.
3. So the pass7 failure was not merely caused by mixing `A1`, `A2`, and `A3` together. At least for this small 5-subject subset, an `A3`-focused rule still does not produce a transferable cross-subject boundary.
4. The project should still prioritize extraction/evaluation validity over bigger models.

## Best next bounded step

Do one more validity-focused extraction test rather than a model change. The strongest next candidate is to make the overlap rule **exclusive** rather than only requiring `A3` presence, so the next pass can answer a cleaner question:
- either strict `SLEEP-S2 + A3-only` windows with `A1/A2` overlap excluded
- or an opposite-family comparison such as `SLEEP-S2 + A1` on the largest feasible matched subset if subject counts stay interpretable

The main requirement is to keep the next extraction variant auditable and comparable to pass7/pass9.
