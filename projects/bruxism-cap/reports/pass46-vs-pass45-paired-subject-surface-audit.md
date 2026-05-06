# Subject-score comparison — pass46-repaired-a3-no-shape-plus-evt-bursts-per-episode-mean vs pass45-repaired-a3-no-shape

## Compared reports
- Primary: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass46-emg-a3-pct10-90-record-relative-eventsubset-no-shape-plus-bursts-per-episode.json` (`logreg`)
- Anchor: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass45-emg-a3-pct10-90-record-relative-eventsubset-no-shape.json` (`logreg`)

## Shared subject score table
| Subject | Label | Primary mean score | Anchor mean score | Delta (primary-anchor) | Primary positive-window fraction | Anchor positive-window fraction | Primary label | Anchor label |
|---|---|---:|---:|---:|---:|---:|---|---|
| brux1 | bruxism | 0.639 | 0.641 | -0.002 | 0.700 | 0.700 | bruxism | bruxism |
| brux2 | bruxism | 0.196 | 0.178 | +0.018 | 0.000 | 0.000 | control | control |
| n11 | control | 0.345 | 0.345 | -0.000 | 0.300 | 0.300 | control | control |
| n3 | control | 0.131 | 0.134 | -0.003 | 0.100 | 0.100 | control | control |
| n5 | control | 0.347 | 0.337 | +0.010 | 0.200 | 0.200 | control | control |

## Score-surface summary
- Primary best bruxism subject: `brux1` at `0.639`.
- Primary highest control: `n5` at `0.347`.
- Primary best-bruxism-minus-highest-control margin: `+0.292`.
- Anchor best bruxism subject: `brux1` at `0.641`.
- Anchor highest control: `n11` at `0.345`.
- Anchor best-bruxism-minus-highest-control margin: `+0.295`.
- Margin delta (primary-anchor): `-0.004`.

## Subject prediction flips
- `[]`

## Copied-through subject-level summaries
- Primary balanced accuracy `0.750` | sensitivity `0.500` | specificity `1.000` | exact sensitivity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 1, 'trials': 2, 'low': 0.01257911709342505, 'high': 0.9874208829065749}` | exact specificity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 3, 'trials': 3, 'low': 0.2924017738212866, 'high': 1.0}` | Brier `0.20673123072228558`.
- Anchor balanced accuracy `0.750` | sensitivity `0.500` | specificity `1.000` | exact sensitivity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 1, 'trials': 2, 'low': 0.01257911709342505, 'high': 0.9874208829065749}` | exact specificity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 3, 'trials': 3, 'low': 0.2924017738212866, 'high': 1.0}` | Brier `0.21110745154712704`.

## Label-level mean deltas
- `{'bruxism': {'mean_primary_score': 0.4173645899492424, 'mean_anchor_score': 0.40944111481933193, 'mean_score_delta_primary_minus_anchor': 0.007923475129910498}, 'control': {'mean_primary_score': 0.2743572502036525, 'mean_anchor_score': 0.2721714344746094, 'mean_score_delta_primary_minus_anchor': 0.0021858157290430926}}`
