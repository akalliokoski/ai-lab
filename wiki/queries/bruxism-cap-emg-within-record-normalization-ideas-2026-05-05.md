---
title: Bruxism CAP EMG within-record normalization ideas (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass34-literature-within-record-normalization-notes.md
  - concepts/bruxism-cap.md
---

# Question
What does the broader EMG literature suggest about normalization or amplitude-invariance ideas that could help the current repaired `EMG1-EMG2 A1-only` scaffold without changing the repo's handcrafted LOSO framing?

# Short answer
The best-supported next move is a within-record feature-space normalization audit, not another deletion-first pass and not another per-window waveform normalization rewrite.

The strongest literature fit is to keep the repaired pass28 scaffold fixed and compare the retained EMG morphology-envelope family in raw form versus a record-relative form such as robust z-scores or percentile-centered scaling computed within each subject record. That matches the repo bottleneck after pass33: the problem now looks more like fold-by-fold representation of morphology than simple feature presence or absence. [[bruxism-cap]] [[bruxism-cap-emg-a1-raw-location-ablation-2026-05-05]]

# Sources inspected
- Burden 2010 (PMID 20702112) — review arguing that task-derived references can reduce inter-individual EMG variability more appropriately than generic normalization choices.
- CEDE amplitude normalization matrix 2020 (PMID 32569878) — normalization method should match the interpretation target.
- Yang and Winter 1984 (PMID 6477083) — subject/task-relative amplitude normalization can improve comparability.
- Liu et al. 2013 whitening paper (PMID 23475374) — whitening reduced feature CV and improved classification in a myoelectric-control setting.
- Hargrove et al. 2010 stability study (PMID 20492713) — effort variation and electrode shift destabilize many common time-domain features.
- Jiang et al. 2014 invariant-feature paper (PMID 25014975) — contraction-level invariance can be designed into features, but their solution is heavier than this repo needs.
- Ikeda et al. 1996 sleep-bruxism criteria paper (PMID 9161232) — classical automated bruxism detection already uses subject-specific EMG thresholds, so record-relative scaling is physiologically natural in-domain.

# Best next bounded step
Run one matched audit on the repaired pass28 scaffold only:
1. keep rows, model family, and LOSO evaluation fixed
2. keep the retained EMG morphology-envelope family fixed
3. build one alternate table where only that family is transformed into within-record robust relative form
4. compare raw vs transformed on `brux1`, `brux2`, `n3`, and best-bruxism-minus-highest-control margin

Recommended first transform:
- per subject, for each retained morphology/envelope feature, compute `(x - median) / max(MAD, eps)` across that subject's kept windows
- use this first on `mean`, `max`, `ptp`, `line_length`, `zero_crossing_rate`, `rectified_std`, `envelope_std`, and `envelope_cv`

# What not to do first
- do not jump to MVC-based normalization; the CAP benchmark has no clean calibration task
- do not treat multi-muscle invariant feature designs as the next repo step; they are too heavy for this small benchmark
- do not rerun another broad signal-level normalization like pass22 before testing feature-space record-relative scaling

# Exact files likely involved
- `projects/bruxism-cap/src/features.py`
- `projects/bruxism-cap/src/prepare_windows.py`
- `projects/bruxism-cap/src/train_baseline.py`
- new likely runner: `projects/bruxism-cap/src/run_pass34_record_relative_emg_audit.py`

# Verdict
The literature supports normalization-aware experimentation here, but the most faithful and smallest next test is feature-space within-record normalization on the repaired scaffold, not another deletion and not another normalize-every-waveform rewrite.
