---
title: Bruxism-cap first baseline lessons (2026-05-03)
created: 2026-05-03
updated: 2026-05-04
type: query
tags: [experiment, evaluation, dataset, workflow, notes]
sources:
  - raw/articles/cap-sleep-database-physionet-2012.md
  - raw/articles/bruxism-single-channel-eeg-2024.md
---

# Question
What did the first real `bruxism-cap` baseline runs actually show?

# Short answer
They showed that the project pipeline is now real and reproducible, but the current result is mainly a leakage/measurement warning rather than a believable bruxism detector. [[bruxism-cap]] [[bruxism-eeg-emg-starter-project-2026-05-03]] [[ai-lab-learning-path]]

# Runs completed

## Pass 1 — 3-subject pilot
- Subjects: `brux1`, `brux2`, `n10`
- Purpose: validate extraction and baseline code end to end
- Result: random-window CV looked unrealistically strong, while LOSO was not valid yet because one fold lost class diversity in training

## Pass 2 — first valid 6-subject baseline
- Subjects: `brux1`, `brux2`, `n3`, `n5`, `n10`, `n11`
- Channel: `C4-P4`
- Windows: `20` windows per subject, `30 s` each
- Feature CSV: `projects/bruxism-cap/data/window_features_pass2.csv`
- Best random-window result: logistic regression balanced accuracy `1.000`
- Best LOSO result: SVM balanced accuracy `0.783`, sensitivity `0.167`, specificity `0.617`

## Pass 3 — first autoresearch-motivated fix
- Change: excluded `n_samples` and `duration_s` from train features because `n_samples` was directly encoding subject acquisition differences, especially `brux2` at `256 Hz` versus the `512 Hz` records
- Best random-window result after the fix: logistic regression balanced accuracy `0.963`
- Best LOSO result after the fix: SVM balanced accuracy `0.733`, sensitivity `0.117`, specificity `0.617`

## Pass 4 — first annotation-aware rerun
- Change: patched `prepare_windows.py` to read local RemLogic `.txt` sidecars and select stage-scored windows such as `SLEEP-S2`
- Local data issue exposed: `n10.edf` is only about `3783` seconds long while `n10.txt` continues far beyond the available signal, so `n10` had to be excluded from the stage-aware subset
- Stage-aware CSV: `projects/bruxism-cap/data/window_features_pass4_s2.csv`
- Subjects used: `brux1`, `brux2`, `n3`, `n5`, `n11`
- Best random-window result: logistic regression balanced accuracy `1.000`
- Best LOSO result: SVM balanced accuracy `0.600`, sensitivity `0.030`, specificity `0.570`

## Pass 5 — subject-level LOSO hardening
- Change: patched `train_baseline.py` so LOSO reports also include a `subject_aggregation` block that converts each held-out subject's windows into one verdict using the mean positive score
- New reports:
  - `projects/bruxism-cap/reports/loso-cv-pass5-pass2-subjectagg.json`
  - `projects/bruxism-cap/reports/loso-cv-pass5-pass4-s2-subjectagg.json`
- Best subject-level result on pass3: SVM subject balanced accuracy `0.375`, subject sensitivity `0.000`, subject specificity `0.750`
- Best subject-level result on pass4: all models stayed at subject sensitivity `0.000`; the best balanced accuracy was `0.500`

## Pass 7 — event-aware stage rerun with CAP micro-event overlap
- Change: patched `prepare_windows.py` again so extracted annotation windows can be required to overlap a second event family via `--require-overlap-events`
- New extraction rule: keep only in-range `SLEEP-S2` windows that overlap `MCAP-A1`, `MCAP-A2`, or `MCAP-A3`
- New overlap-aware CSV: `projects/bruxism-cap/data/window_features_pass7_s2_mcap.csv`
- Subjects used: `brux1`, `brux2`, `n3`, `n5`, `n11`
- Important scope note: `n10` is still excluded because it has `0` in-range `SLEEP-S2` windows locally, so it also has `0` usable `S2+MCAP` windows
- Best random-window result: logistic regression balanced accuracy `1.000`
- Best LOSO result: logistic regression balanced accuracy `0.590`, sensitivity `0.000`, specificity `0.590`
- Best subject-level LOSO result: all models tied at subject balanced accuracy `0.500`, subject sensitivity `0.000`, subject specificity `1.000`

## Pass 8 — overlap event mix audit
- Change: added `src/audit_overlap_event_mix.py` to audit which overlap families dominate the pass7 subset by subject and label
- New audit artifacts:
  - `projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.json`
  - `projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.md`
- Key result: the mixed `S2+MCAP` bucket is heterogeneous rather than uniform
  - `brux2` kept windows are heavily `MCAP-A3`-dominated (`19/20` with `A3`)
  - `n5` kept windows are heavily `MCAP-A1`-dominated (`16/20` with `A1`)
  - that mismatch already exists in the full eligible pools, not only in the first-20 cap

## Pass 9 — narrower single-family `S2 + MCAP-A3` rerun
- Change: rebuilt the stage-aware subset so every kept window had to overlap `MCAP-A3`
- New artifacts:
  - `projects/bruxism-cap/data/window_features_pass9_s2_mcap_a3.csv`
  - `projects/bruxism-cap/reports/random-window-cv-pass9-s2-mcap-a3.json`
  - `projects/bruxism-cap/reports/loso-cv-pass9-s2-mcap-a3.json`
  - `projects/bruxism-cap/reports/pass9-s2-mcap-a3.md`
- Best random-window result: logistic regression balanced accuracy `0.921`
- Best LOSO result: random forest balanced accuracy `0.550`, sensitivity `0.010`, specificity `0.540`
- Best subject-level LOSO result: all models again stayed at subject sensitivity `0.000` and subject balanced accuracy `0.500`

## Pass 10 — exclusive `S2 + MCAP-A3-only` rerun
- Change: patched `prepare_windows.py` again so extracted annotation windows can both require and forbid overlap families via `--require-overlap-events` plus the new `--exclude-overlap-events`
- New artifacts:
  - `projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv`
  - `projects/bruxism-cap/reports/random-window-cv-pass10-s2-mcap-a3-only.json`
  - `projects/bruxism-cap/reports/loso-cv-pass10-s2-mcap-a3-only.json`
  - `projects/bruxism-cap/reports/pass10-s2-mcap-a3-only.md`
- New extraction rule: keep only in-range `SLEEP-S2` windows that overlap `MCAP-A3` and do **not** overlap `MCAP-A1` or `MCAP-A2`
- Feasibility check: all five already-verified subjects still had at least `20` eligible exclusive-`A3` windows, so the rerun preserved the same `5`-subject / `20`-windows-per-subject shape as pass9
- Best random-window result: random forest balanced accuracy `0.908`
- Best LOSO result: SVM balanced accuracy `0.500`, sensitivity `0.000`, specificity `0.500`
- Best subject-level LOSO result: all models again stayed at subject sensitivity `0.000` and subject balanced accuracy `0.500`

# What improved
- LOSO is now runnable on a non-degenerate subset because the extra controls finished downloading.
- The first obvious feature leak was identified and removed from the training feature set.
- The repo now has a reproducible annotation-aware extraction path using local RemLogic sidecars.
- The repo now also has a reproducible event-overlap extraction path for tighter CAP-aware window selection.
- The project now has saved artifacts for pilot, first valid baseline, first measurement-fix rerun, first stage-aware negative rerun, and first CAP-micro-event-overlap negative rerun.

# What failed or stayed weak

## 1. Random-window CV is still too optimistic
Perfect or near-perfect random-window results persisted even after removing the explicit sampling-rate proxy feature. That strongly suggests residual subject/background leakage or a too-easy window definition.^[raw/articles/cap-sleep-database-physionet-2012.md]

## 2. Held-out bruxism sensitivity stayed poor
The honest subject-aware metric that matters most here — recognizing held-out bruxism subjects — remained weak. The best pass3 LOSO sensitivity was only `0.117`.

## 3. Simple stage matching was not enough
The pass4 `SLEEP-S2` rerun was more physiologically targeted than the first-`600`-seconds baseline, but it still kept random-window CV perfect while LOSO regressed to `0.600` balanced accuracy and only `0.030` held-out bruxism sensitivity. That means stage restriction alone did not remove the core subject/background separability.

## 4. Subject-level aggregation showed the current LOSO result was still flattering the model
Once LOSO predictions were aggregated to one verdict per held-out subject, every tested model still missed every held-out bruxism subject on both pass3 and pass4. So the small nonzero window-level sensitivity in the earlier reports was not a sign of actual subject recognition.

## 5. Annotation auditing is still part of the bottleneck
The new extraction path exposed that at least one local control record, `n10`, appears truncated relative to its sidecar scoring file, and `brux1` has some late scored events beyond the available EDF duration as well. So the next best bounded step is now narrower than before: audit EDF/scoring alignment before trusting broader stage-aware comparisons.

## 6. The mixed `S2+MCAP` bucket is itself heterogeneous
The new pass8 overlap-event audit showed that the pass7 subset does not represent one consistent CAP-overlap regime. `brux2` is mostly `MCAP-A3` while `n5` is mostly `MCAP-A1`, and that mismatch already exists before the first-20 cap. So the next extraction variant should be a narrower single-family overlap rule rather than another broad mixed-event bucket.

## 7. Narrowing to `S2 + A3` still did not fix held-out transfer
The new pass9 rerun showed that moving from the mixed `S2+MCAP` bucket to an `S2 + A3` overlap rule made random-window CV less perfect, but it still did not help the honest target. The best LOSO balanced accuracy fell to `0.550`, and subject-level bruxism sensitivity still stayed `0.000`. So the pass7 failure is not explained just by mixed CAP-event families; the next extraction step should become more auditable still, likely by making the overlap rule exclusive rather than only requiring `A3` presence.

## 8. Exclusive `A3` windows still did not transfer
The new pass10 rerun made that next extraction step explicit by excluding simultaneous `A1/A2` overlap from the kept `SLEEP-S2 + A3` windows. That made the extraction rule cleaner, but the honest result still did not improve: the best LOSO balanced accuracy fell again to `0.500`, and subject-level bruxism sensitivity still stayed `0.000`. So even exclusive `A3` windows do not isolate a transferable cross-subject boundary in the current tiny subset.

# Main lesson
The first serious baseline did its job: it turned the project from an idea into a measurable system and showed where the current design is invalid or weak. The correct next move is to improve extraction validity before trying bigger models, more channels, or deep learning.

# Best next bounded experiment
1. keep `n10` excluded from local `SLEEP-S2` reruns and keep `brux1` explicitly in-range filtered
2. preserve the new overlap-event audit as evidence that the pass7 mixed bucket is heterogeneous
3. build one narrower single-family extraction variant such as `SLEEP-S2 + MCAP-A3`
4. if that still fails, tighten the overlap rule so the family is exclusive rather than merely required
5. if exclusive `A3` also fails, compare one alternate exclusive family such as `S2 + A1-only` or add a compact rule-survival audit before changing model families
6. only then decide whether another annotation-aware extraction variant is worth the next patch

# Why this matters for ai-lab
This is exactly the kind of early project result that should be preserved: not because the numbers are good, but because the failure mode is informative and directly shapes the next better experiment. [[artifact-driven-experiment-debugging]] [[artifact-card-sft]]
