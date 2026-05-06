# Data notes for bruxism-cap

## Raw data layout

Expected raw EDF files live under:

- `projects/bruxism-cap/data/raw/capslpdb/`

Suggested bounded control-side subset:
- bruxism: `brux1.edf`, `brux2.edf`
- already verified controls: `n3.edf`, `n5.edf`, `n11.edf`
- next admissible control additions: `n1.edf`, `n2.edf`

Keep this branch tiny. The goal is to stress specificity under a fixed two-positive public benchmark, not to maximize sample count.

Do not include `n10.edf` in stage-aware rebuilds until the local file is refreshed and re-verified against the canonical PhysioNet object. The current local copy is truncated relative to the remote source.

## Manifest file

Copy `subject_manifest.example.csv` to `subject_manifest.csv` and edit it for the exact files / channels you decide to use.

Suggested columns:
- `subject_id`
- `label`
- `edf_path`
- `annotation_txt_path`
- `primary_channel`
- `comparison_channel`
- `include_in_control_expansion`
- `control_audit_status`
- `s2_in_range`
- `a1_only_in_range`
- `a3_only_in_range`
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
