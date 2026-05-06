# Pass 10 — exclusive `SLEEP-S2 + MCAP-A3-only` rerun

Date: 2026-05-04
Status: bounded negative result; excluding simultaneous `MCAP-A1`/`MCAP-A2` overlap made the extraction rule cleaner but did not improve honest held-out bruxism detection

## Why this pass exists

Pass9 showed that requiring `MCAP-A3` overlap alone was still too loose to answer the next extraction question cleanly, because a kept `SLEEP-S2` window could still overlap `A1` or `A2` at the same time.

This pass tests the smallest stricter version of that idea:
- keep only in-range `SLEEP-S2` windows
- require overlap with `MCAP-A3`
- exclude any simultaneous overlap with `MCAP-A1` or `MCAP-A2`
- keep `20` windows per subject on the same verified 5-subject subset
- reuse the current no-`n_samples` / no-`duration_s` training path in `src/train_baseline.py`

## Code change

`src/prepare_windows.py` now accepts `--exclude-overlap-events` so annotation-selected windows can be filtered by both required and forbidden overlap families in one bounded extraction pass.

## Dataset used

- Feature CSV: `projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv`
- Subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- Labels: `2` bruxism subjects, `3` control subjects
- Channel: `C4-P4`
- Window seconds: `30`
- Windows per subject: `20`
- Total windows: `100`
- Extraction rule: in-range `SLEEP-S2` windows with `MCAP-A3` overlap and no simultaneous `MCAP-A1` or `MCAP-A2` overlap

## Feasibility check

All five already-verified subjects still had at least `20` eligible exclusive-`A3` windows locally:
- `brux1`: `31`
- `brux2`: `111`
- `n3`: `76`
- `n5`: `38`
- `n11`: `42`

So the stricter rerun preserved the same `5`-subject / `20`-windows-per-subject shape as pass9.

## Commands run

```bash
source .venv/bin/activate
python -m py_compile projects/bruxism-cap/src/prepare_windows.py

python projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --annotation-txt projects/bruxism-cap/data/raw/capslpdb/brux1.txt \
  --annotation-events SLEEP-S2 \
  --require-overlap-events MCAP-A3 \
  --exclude-overlap-events MCAP-A1,MCAP-A2 \
  --subject-id brux1 --label bruxism --channel C4-P4 \
  --window-seconds 30 --limit-windows 20 \
  --out projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv
# repeated with --append for brux2, n3, n5, n11

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv \
  --cv random \
  --out projects/bruxism-cap/reports/random-window-cv-pass10-s2-mcap-a3-only.json

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv \
  --cv loso \
  --out projects/bruxism-cap/reports/loso-cv-pass10-s2-mcap-a3-only.json
```

## Key results

### Random-window CV
- Best balanced accuracy: random forest `0.908`
- Logistic regression balanced accuracy: `0.900`
- SVM balanced accuracy: `0.900`

### LOSO window-level CV
- Best balanced accuracy: SVM `0.500`
- Logistic regression balanced accuracy: `0.420`
- Random forest balanced accuracy: `0.470`
- Best held-out bruxism sensitivity: logistic regression / random forest `0.010`; SVM stayed `0.000`

### LOSO subject-level aggregation
- All three models stayed at subject balanced accuracy `0.500`
- All three models stayed at subject sensitivity `0.000`
- All three models stayed at subject specificity `1.000`

## Comparison to pass9 non-exclusive `S2 + A3`

Pass9 (`A3` required) versus pass10 (`A3` required, `A1/A2` excluded):

- Random-window best balanced accuracy fell slightly from `0.921` to `0.908`
- LOSO best balanced accuracy fell from `0.550` to `0.500`
- LOSO subject-level bruxism sensitivity stayed `0.000`

## Interpretation

This is a cleaner but still negative result:
1. The extraction rule is now more auditable because kept windows cannot mix `A3` with simultaneous `A1/A2` overlap.
2. That stricter rule did **not** improve honest transfer. The best LOSO result fell to chance-level balanced accuracy and subject-level bruxism detection remained absent.
3. The pass9 failure therefore was not just caused by mixed overlap within the kept `A3` windows; even exclusive `A3` windows do not produce a transferable cross-subject boundary in this tiny subset.
4. The project should still prefer extraction/evaluation validity work over bigger models, but the next bounded step should probably change the measurement surface or event family comparison rather than making `A3` even narrower.

## Best next bounded step

Do one measurement or extraction-comparison increment, not a model jump. The most useful next candidates are:
- compare exclusive `S2 + A3-only` against an exclusive `S2 + A1-only` subset on the largest matched subject set that still remains interpretable, or
- add a small audit artifact that summarizes how many kept windows per subject survive each overlap rule (`pass7` mixed, `pass9` A3-required, `pass10` A3-only) so future reruns can distinguish label signal from changing event availability.
