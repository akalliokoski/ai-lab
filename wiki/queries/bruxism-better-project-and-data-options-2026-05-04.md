---
title: Better bruxism project and data options (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md
  - raw/articles/sleep-bruxism-emg-only-setups-2020.md
  - raw/articles/advanced-sensing-system-sleep-bruxism-emg-2024.md
  - raw/articles/portable-masseter-emg-validity-2019.md
  - raw/articles/home-vs-lab-wearable-emg-2022.md
  - raw/articles/portable-emg-temporal-patterns-2026.md
  - raw/articles/imu-sleep-bruxism-field-detection-2026.md
  - concepts/bruxism-cap.md
---

# Question
Is there now a more suitable bruxism project and dataset than the current `bruxism-cap` track, especially if better aligned with recent EMG-focused research?

# Short answer
There is a more suitable project shape, but I did not find a clearly better open dataset.

Update after closure: this page should now be read as an early strategic precursor to the post-CAP successor direction. Its core literature conclusion still holds — portable jaw-muscle EMG is the stronger translational direction — but the benchmark-comparison framing has changed because the CAP branch is now complete rather than still active. [[bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06]] [[bruxism-cap]]

The stronger 2024-2026 research direction is:
- portable jaw-muscle EMG for ecological monitoring
- multi-night recording instead of single-night snapshots
- cautious validation against PSG rather than EMG-only overclaiming
- growing interest in wearable alternatives such as IMU jaw-motion sensing

But the open-data situation still looks weak. I did not find a public jaw-EMG sleep-bruxism benchmark that is clearly better than CAP for a reproducible first project. Most recent EMG studies appear to rely on proprietary cohorts, wearable device studies, or simulated behaviors rather than openly downloadable benchmark corpora.

# What changed relative to the earlier recommendation
The earlier CAP recommendation was still reasonable as the easiest reproducible entry point. The new evidence does not really overturn that on openness. What it does change is the preferred scientific target: if the goal is stronger alignment with the translational literature, the project should now be framed as EMG-first rather than EEG-first.^[raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md]^[raw/articles/portable-emg-temporal-patterns-2026.md]

# Current literature signal

## 1. Portable EMG is the most relevant practical sensing modality
The 2024 meta-analysis found portable EMG devices can show good diagnostic capacity relative to PSG, but the certainty of evidence remains very low because studies are small and heterogeneous.^[raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md]

A 2019/2020 wearable-validation study reported strong agreement between single-channel masseter EMG and PSG-audio-video scoring in a 20-subject cohort, with an apparent operating point near 5.5 episodes/hour.^[raw/articles/portable-masseter-emg-validity-2019.md]

A 2026 multi-day portable EMG paper pushed the field even further toward longitudinal monitoring, arguing that three days may be the minimum viable monitoring period because sleep and awake bruxism vary across nights and hours.^[raw/articles/portable-emg-temporal-patterns-2026.md]

## 2. EMG-only is useful for sensing, but risky as a gold-standard label source
The 2020 scoring-comparison study is still the key warning sign: EMG-only setups were unreliable compared with PSG plus audio-video review.^[raw/articles/sleep-bruxism-emg-only-setups-2020.md]

So the field is not saying “just use EMG and call it solved.” It is saying:
- EMG is the practical sensor family
- PSG remains the validity anchor
- thresholds, labeling rules, and study design still matter a lot

## 3. Home / wearable monitoring matters more than lab-only snapshots
A 2022 home-vs-lab wearable EMG study found fewer bruxism bursts and episodes in the laboratory than at home, suggesting that home monitoring may be more ecologically representative.^[raw/articles/home-vs-lab-wearable-emg-2022.md]

This matters because it weakens the idea that a one-night lab-style dataset should be the end goal. It is still useful as a benchmark, but not the whole scientific target.

## 4. Alternative wearable sensing is emerging, but not benchmark-ready
A 2026 IMU proof-of-concept reported high classification accuracy for labeled jaw motions, but it used only 3 individuals and manually labeled motion classes.^[raw/articles/imu-sleep-bruxism-field-detection-2026.md]

A 2024 Sensors paper using temporalis and masseter EMG plus classical ML is useful for feature ideas, but it was based on healthy subjects simulating bruxism-like behaviors and the data are only available on request, not as an open benchmark.^[raw/articles/advanced-sensing-system-sleep-bruxism-emg-2024.md]

# Data availability verdict

## What I could verify
- The current CAP subset remains the only clearly open, already-downloaded dataset in the repo.
- All 6 locally inspected CAP EDFs in the current project subset (`brux1`, `brux2`, `n3`, `n5`, `n10`, `n11`) contain the `EMG1-EMG2` channel in addition to EEG channels, so an EMG-first pivot can be done without changing datasets.
- I did not verify any newer public benchmark with open downloadable jaw-muscle bruxism recordings that clearly beats CAP on openness plus labels.

## What I did not find
- No clearly open masseter-EMG bruxism benchmark analogous to PhysioNet sleep datasets.
- No obvious public multi-night wearable bruxism dataset from the recent portable-EMG literature.
- No strong open event-labeled benchmark from the newer IMU / wearable studies.

# Recommended project decision

## Best next project now: keep the dataset, change the project framing
Do not abandon `bruxism-cap` yet. Instead, shift it to:

**EMG-first, subject-aware, validity-limited benchmarking on CAP**

Concretely:
1. Make `EMG1-EMG2` the primary channel, not `C4-P4`.
2. Re-run the same leakage-aware pipeline on EMG features first.
3. Keep the current evaluation discipline: random-window vs LOSO plus subject-level summaries.
4. Compare `EMG1-EMG2` directly against `C4-P4` on the same verified subject/event subsets.
5. Preserve the core caveat: CAP still lacks ideal jaw-muscle event labels, so this is a sensing-alignment benchmark, not a clinical detector.

## Stronger-science-but-harder option
If you want the project to align more tightly with the newest literature than with open-data convenience, the better project is:

**portable masseter-EMG bruxism monitoring and threshold validation**

But this is blocked by data access. Without an open dataset or your own recordings, it becomes mainly a literature-reproduction and methods-design exercise rather than a reproducible public benchmark.

## Not recommended as the next primary project
- replacing CAP with the 2024 simulated EMG paper setup
- replacing CAP with the tiny 2026 IMU proof of concept
- jumping straight to custom wearable collection before the offline EMG analysis pipeline is stronger

# Bottom line
Yes, there is a more suitable scientific project shape than the current EEG-leaning CAP baseline: it is an EMG-first, wearable-minded, multi-night-aware bruxism monitoring project.

But no, I did not find a clearly better open dataset ready to replace CAP right now.

So the best move is not “switch datasets.” The best move is:
- keep CAP for reproducibility
- pivot the current project to `EMG1-EMG2` as the primary channel
- treat the result as a bounded benchmark on the path toward a future portable-EMG project

# Suggested next bounded experiment
Run a matched comparison on the current verified subset:
- `EMG1-EMG2` vs `C4-P4`
- same subject set
- same annotation rule
- same per-subject cap
- same LOSO + subject-level evaluation

That would answer the most important scientific question now: whether the existing open dataset already supports a more JawSense-aligned EMG-first baseline without sacrificing the current reproducibility and audit trail.
