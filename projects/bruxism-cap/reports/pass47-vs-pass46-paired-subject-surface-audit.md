# Subject-score comparison — pass47-repaired-a3-control-expanded vs pass46-repaired-a3-no-shape-plus-bursts-per-episode

## Compared reports
- Primary: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass47-emg-a3-control-expanded.json` (`logreg`)
- Anchor: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass46-emg-a3-pct10-90-record-relative-eventsubset-no-shape-plus-bursts-per-episode.json` (`logreg`)

## Shared subject score table
| Subject | Label | Primary mean score | Anchor mean score | Delta (primary-anchor) | Primary positive-window fraction | Anchor positive-window fraction | Primary label | Anchor label |
|---|---|---:|---:|---:|---:|---:|---|---|
| brux1 | bruxism | 0.669 | 0.639 | +0.030 | 0.700 | 0.700 | bruxism | bruxism |
| brux2 | bruxism | 0.212 | 0.196 | +0.016 | 0.000 | 0.000 | control | control |
| n11 | control | 0.283 | 0.345 | -0.062 | 0.200 | 0.300 | control | control |
| n3 | control | 0.081 | 0.131 | -0.050 | 0.000 | 0.100 | control | control |
| n5 | control | 0.334 | 0.347 | -0.013 | 0.300 | 0.200 | control | control |

## Score-surface summary
- Primary best bruxism subject: `brux1` at `0.669`.
- Primary highest control: `n5` at `0.334`.
- Primary best-bruxism-minus-highest-control margin: `+0.335`.
- Anchor best bruxism subject: `brux1` at `0.639`.
- Anchor highest control: `n5` at `0.347`.
- Anchor best-bruxism-minus-highest-control margin: `+0.292`.
- Margin delta (primary-anchor): `+0.043`.

## Subject prediction flips
- `[]`

## Copied-through subject-level summaries
- Primary balanced accuracy `0.750` | sensitivity `0.500` | specificity `1.000` | exact sensitivity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 1, 'trials': 2, 'low': 0.01257911709342505, 'high': 0.9874208829065749}` | exact specificity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 5, 'trials': 5, 'low': 0.4781762498950185, 'high': 1.0}` | Brier `0.1403160015336041`.
- Anchor balanced accuracy `0.750` | sensitivity `0.500` | specificity `1.000` | exact sensitivity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 1, 'trials': 2, 'low': 0.01257911709342505, 'high': 0.9874208829065749}` | exact specificity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 3, 'trials': 3, 'low': 0.2924017738212866, 'high': 1.0}` | Brier `0.20673123072228558`.

## Label-level mean deltas
- `{'bruxism': {'mean_primary_score': 0.44044163649111234, 'mean_anchor_score': 0.4173645899492424, 'mean_score_delta_primary_minus_anchor': 0.023077046541869914}, 'control': {'mean_primary_score': 0.23280946476481293, 'mean_anchor_score': 0.2743572502036525, 'mean_score_delta_primary_minus_anchor': -0.04154778543883958}}`
