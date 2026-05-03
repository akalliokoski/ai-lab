# First bruxism-cap baseline report

Date: 2026-05-03
Status: scaffold created, results pending

## Goal

Produce the first honest CAP-based bruxism baseline with both:
- random window cross-validation
- leave-one-subject-out cross-validation

## Pre-run checklist

- [ ] Raw EDF subset downloaded under `projects/bruxism-cap/data/raw/capslpdb/`
- [ ] Chosen channel exists for all included subjects
- [ ] `window_features.csv` regenerated from raw data
- [ ] Class balance checked
- [ ] Subject counts checked
- [ ] Random-window CV result saved
- [ ] LOSO CV result saved
- [ ] Gap between the two documented

## Dataset used

- Subjects:
- Labels:
- Channel:
- Window seconds:
- Total windows:

## Results

### Random window CV
- Balanced accuracy:
- Sensitivity:
- Specificity:
- AUROC:

### Leave-one-subject-out CV
- Balanced accuracy:
- Sensitivity:
- Specificity:
- AUROC:

## Interpretation

- Did random-window CV overstate performance?
- Which model was most stable?
- Did any class collapse happen?
- Is the result strong enough to justify an EMG-first follow-up?

## Failure notes

Record weak results honestly:
- what failed
- how it showed up in metrics or artifacts
- what to patch next
