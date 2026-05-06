# Subject-score comparison — pass45-repaired-a3-no-shape vs pass44-repaired-a3-event-subset

## Compared reports
- Primary: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass45-emg-a3-pct10-90-record-relative-eventsubset-no-shape.json` (`logreg`)
- Anchor: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass44-emg-a3-pct10-90-record-relative-shape-eventsubset.json` (`logreg`)

## Shared subject score table
| Subject | Label | Primary mean score | Anchor mean score | Delta (primary-anchor) | Primary positive-window fraction | Anchor positive-window fraction | Primary label | Anchor label |
|---|---|---:|---:|---:|---:|---:|---|---|
| brux1 | bruxism | 0.641 | 0.532 | +0.109 | 0.700 | 0.400 | bruxism | bruxism |
| brux2 | bruxism | 0.178 | 0.123 | +0.055 | 0.000 | 0.000 | control | control |
| n11 | control | 0.345 | 0.395 | -0.049 | 0.300 | 0.400 | control | control |
| n3 | control | 0.134 | 0.034 | +0.100 | 0.100 | 0.000 | control | control |
| n5 | control | 0.337 | 0.365 | -0.028 | 0.200 | 0.200 | control | control |

## Score-surface summary
- Primary best bruxism subject: `brux1` at `0.641`.
- Primary highest control: `n11` at `0.345`.
- Primary best-bruxism-minus-highest-control margin: `+0.295`.
- Anchor best bruxism subject: `brux1` at `0.532`.
- Anchor highest control: `n11` at `0.395`.
- Anchor best-bruxism-minus-highest-control margin: `+0.138`.
- Margin delta (primary-anchor): `+0.158`.

## Subject prediction flips
- `[]`

## Copied-through subject-level summaries
- Primary balanced accuracy `0.750` | sensitivity `0.500` | specificity `1.000` | exact sensitivity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 1, 'trials': 2, 'low': 0.01257911709342505, 'high': 0.9874208829065749}` | exact specificity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 3, 'trials': 3, 'low': 0.2924017738212866, 'high': 1.0}` | Brier `0.21110745154712704`.
- Anchor balanced accuracy `0.750` | sensitivity `0.500` | specificity `1.000` | exact sensitivity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 1, 'trials': 2, 'low': 0.01257911709342505, 'high': 0.9874208829065749}` | exact specificity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 3, 'trials': 3, 'low': 0.2924017738212866, 'high': 1.0}` | Brier `0.2557186480925962`.

## Label-level mean deltas
- `{'bruxism': {'mean_primary_score': 0.40944111481933193, 'mean_anchor_score': 0.32746319545834374, 'mean_score_delta_primary_minus_anchor': 0.08197791936098822}, 'control': {'mean_primary_score': 0.2721714344746094, 'mean_anchor_score': 0.26443530616720784, 'mean_score_delta_primary_minus_anchor': 0.007736128307401581}}`
