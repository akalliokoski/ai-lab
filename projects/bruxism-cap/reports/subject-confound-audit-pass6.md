# Subject-versus-label confound audit

This audit checks whether standardized handcrafted feature windows cluster more strongly by `subject_id` than by the target `label`.
Higher subject clustering than label clustering is evidence that random window splits can reward subject memorization rather than transferable bruxism detection.

## Metrics

- `silhouette.subject_id` vs `silhouette.label`: larger values mean stronger cluster separation in feature space.
- `nearest_neighbor.same_subject_rate` vs `same_label_rate`: for each window, compare its closest other window after standardization.
- `memorization_probe.subject_1nn_random_cv_accuracy` vs `label_1nn_random_cv_accuracy`: a 5-fold random-window 1-NN probe showing whether subject identity is easier to recover than label under the same leakage-prone split style.

## window_features_pass2.csv

- rows: `120`
- subjects: `6`
- label counts: `{'bruxism': 40, 'control': 80}`
- silhouette(subject): `0.19501968177528328`
- silhouette(label): `0.36431549674169567`
- silhouette gap subject-label: `-0.16929581496641238`
- nearest-neighbor same-subject rate: `0.8166666666666667`
- nearest-neighbor same-label rate: `0.9666666666666667`
- nearest-neighbor subject-label gap: `-0.15000000000000002`
- 1-NN subject random-CV accuracy: `0.7999999999999999`
- 1-NN label random-CV accuracy: `0.9583333333333333`
- 1-NN random-CV gap subject-label: `-0.15833333333333333`

## window_features_pass4_s2.csv

- rows: `100`
- subjects: `5`
- label counts: `{'bruxism': 40, 'control': 60}`
- silhouette(subject): `0.14673355697294943`
- silhouette(label): `0.32713360928419294`
- silhouette gap subject-label: `-0.1804000523112435`
- nearest-neighbor same-subject rate: `0.83`
- nearest-neighbor same-label rate: `1.0`
- nearest-neighbor subject-label gap: `-0.17000000000000004`
- 1-NN subject random-CV accuracy: `0.8099999999999999`
- 1-NN label random-CV accuracy: `1.0`
- 1-NN random-CV gap subject-label: `-0.19000000000000006`

## Comparison summary

- Subject silhouette changed from `0.19501968177528328` to `0.14673355697294943`.
- Label silhouette changed from `0.36431549674169567` to `0.32713360928419294`.
- Nearest-neighbor subject-label gap changed from `-0.15000000000000002` to `-0.17000000000000004`.

## Verdict

Across the audited tables, label-separation signals were stronger than subject-separation signals on all three quick probes.
That means the current leakage story is not best summarized as pure subject-ID memorization. The sharper bottleneck is that the label boundary visible inside random window splits does not transfer to held-out subjects.
