# Data notes for bruxism-cap

## Raw data layout

Expected raw EDF files live under:

- `projects/bruxism-cap/data/raw/capslpdb/`

Suggested starter subset:
- bruxism: `brux1.edf`, `brux2.edf`
- controls: `n3.edf`, `n5.edf`, `n10.edf`, `n11.edf`

Keep this first pass tiny. The goal is to exercise the pipeline, not to maximize sample count.

## Manifest file

Copy `subject_manifest.example.csv` to `subject_manifest.csv` and edit it for the exact files / channels you decide to use.

Suggested columns:
- `subject_id`
- `label`
- `edf_path`
- `channel`
- `notes`

## Derived data files

Typical derived outputs:
- `window_features.csv` — one row per signal window
- `random-window-cv.json` — leakage-prone reference result
- `loso-cv.json` — subject-aware result

## Label discipline

Keep labels binary for version 1:
- `bruxism`
- `control`

Do not mix in other CAP pathology groups for the first baseline.

## Important caveat

CAP is primarily a sleep-instability database, not a bruxism benchmark. The public bruxism subset is tiny.

That means:
- treat this as a reproducible pilot
- prefer transparent feature engineering over aggressive modeling
- document every evaluation shortcut explicitly
