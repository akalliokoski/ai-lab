---
title: Bruxism CAP EMG time-only ablation (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass17-emg-a3-timeonly-ablation.md
  - concepts/bruxism-cap.md
---

# Question
Did removing the EEG-shaped spectral / band-ratio feature family improve the current matched `EMG1-EMG2` `A3-only` CAP baseline?

# Short answer
No.

On the fixed matched pass14 scaffold, removing `bp_*`, `rel_bp_*`, and `ratio_*` did **not** improve the honest subject-level verdict. Random-window CV stayed high, but LOSO subject sensitivity remained `0.000` and the best window-level LOSO score got slightly worse. [[bruxism-cap]] [[bruxism-cap-emg-feature-validity-audit-2026-05-04]]

# What changed
The run kept the same verified `5`-subject subset, the same `14`-windows-per-subject cap, the same `EMG1-EMG2` channel, and the same exclusive `SLEEP-S2 + MCAP-A3-only` extraction rule. It changed only the trainable feature family by dropping the spectral and ratio features, leaving `9` time-domain features. [[bruxism-cap-emg-a1-vs-a3-matched14-2026-05-04]] [[bruxism-cap-emg-a3-threshold-audit-2026-05-04]]

# Key evidence
- pass14 full-feature best LOSO window-level result (`logreg`): balanced accuracy `0.629`, sensitivity `0.057`, specificity `0.571`
- pass17 time-only best LOSO window-level result (`logreg`): balanced accuracy `0.614`, sensitivity `0.043`, specificity `0.571`
- pass14 full-feature subject-level result: balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`
- pass17 time-only subject-level result: balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`

The subject ordering also stayed hostile to honest EMG transfer:
- `n3` `0.328`
- `n5` `0.221`
- `brux1` `0.148`
- `n11` `0.144`
- `brux2` `0.055`

Compared with pass14, both bruxism subjects fell further while `n3` rose above them even more clearly.^[../projects/bruxism-cap/reports/pass17-emg-a3-timeonly-ablation.md]

# Interpretation
This preserves a useful negative result: the current EMG-first failure is not fixed by simply deleting the EEG-shaped spectral family. Some of those features were suspect, but removing them alone weakens `brux1` and `brux2` more than it improves the control ranking. The next bounded patch should therefore be **replacement-oriented**, not just subtraction-oriented: keep the matched scaffold fixed and add one compact EMG-specific burst / envelope / amplitude-variability family. [[bruxism-cap]] [[bruxism-better-project-and-data-options-2026-05-04]]
