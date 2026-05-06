# Subject-score comparison — pass48-repaired-a1-control-expanded vs pass47-repaired-a3-control-expanded

## Compared reports
- Primary: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass48-emg-a1-control-expanded.json` (`logreg`)
- Anchor: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass47-emg-a3-control-expanded.json` (`logreg`)

## Shared subject score table
| Subject | Label | Primary mean score | Anchor mean score | Delta (primary-anchor) | Primary positive-window fraction | Anchor positive-window fraction | Primary label | Anchor label |
|---|---|---:|---:|---:|---:|---:|---|---|
| brux1 | bruxism | 0.108 | 0.669 | -0.561 | 0.000 | 0.700 | control | bruxism |
| brux2 | bruxism | 0.311 | 0.212 | +0.099 | 0.100 | 0.000 | control | control |
| n1 | control | 0.239 | 0.196 | +0.042 | 0.100 | 0.000 | control | control |
| n11 | control | 0.287 | 0.283 | +0.004 | 0.200 | 0.200 | control | control |
| n2 | control | 0.614 | 0.120 | +0.494 | 1.000 | 0.000 | bruxism | control |
| n3 | control | 0.427 | 0.081 | +0.347 | 0.400 | 0.000 | control | control |
| n5 | control | 0.211 | 0.334 | -0.123 | 0.100 | 0.300 | control | control |

## Score-surface summary
- Primary best bruxism subject: `brux2` at `0.311`.
- Primary highest control: `n2` at `0.614`.
- Primary best-bruxism-minus-highest-control margin: `-0.302`.
- Anchor best bruxism subject: `brux1` at `0.669`.
- Anchor highest control: `n5` at `0.334`.
- Anchor best-bruxism-minus-highest-control margin: `+0.335`.
- Margin delta (primary-anchor): `-0.637`.

## Subject prediction flips
- `[{'subject_id': 'brux1', 'true_label': 'bruxism', 'anchor_predicted_label': 'bruxism', 'primary_predicted_label': 'control'}, {'subject_id': 'n2', 'true_label': 'control', 'anchor_predicted_label': 'control', 'primary_predicted_label': 'bruxism'}]`

## Copied-through subject-level summaries
- Primary balanced accuracy `0.400` | sensitivity `0.000` | specificity `0.800` | exact sensitivity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 0, 'trials': 2, 'low': 0.0, 'high': 0.841886116991581}` | exact specificity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 4, 'trials': 5, 'low': 0.2835820638819105, 'high': 0.9949492366205319}` | Brier `0.2877418017644815`.
- Anchor balanced accuracy `0.750` | sensitivity `0.500` | specificity `1.000` | exact sensitivity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 1, 'trials': 2, 'low': 0.01257911709342505, 'high': 0.9874208829065749}` | exact specificity CI `{'method': 'clopper_pearson', 'confidence_level': 0.95, 'successes': 5, 'trials': 5, 'low': 0.4781762498950185, 'high': 1.0}` | Brier `0.1403160015336041`.

## Label-level mean deltas
- `{'bruxism': {'mean_primary_score': 0.20936034065555642, 'mean_anchor_score': 0.44044163649111234, 'mean_score_delta_primary_minus_anchor': -0.23108129583555592}, 'control': {'mean_primary_score': 0.355642159024451, 'mean_anchor_score': 0.20289750912935997, 'mean_score_delta_primary_minus_anchor': 0.152744649895091}}`
