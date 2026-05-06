---
title: Dataset Scout: Post-CAP Bruxism Benchmark Candidates (2026-05-06)
created: 2026-05-06
updated: 2026-05-06
type: query
tags: [research, dataset, benchmark, bruxism, emg]
sources:
  - raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md
  - raw/articles/sleep-bruxism-emg-only-setups-2020.md
  - raw/articles/advanced-sensing-system-sleep-bruxism-emg-2024.md
  - raw/articles/portable-masseter-emg-validity-2019.md
  - raw/articles/home-vs-lab-wearable-emg-2022.md
  - raw/articles/portable-emg-temporal-patterns-2026.md
  - raw/articles/imu-sleep-bruxism-field-detection-2026.md
  - queries/bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06.md
---

# Dataset Scout: Post-CAP Bruxism Benchmark Candidates

## Objective
Identify source-verified candidate datasets or benchmark directions to succeed the `bruxism-cap` baseline, prioritizing scientific validity, label-anchor reliability, and practical accessibility.

## Important update
This scout originally fed a pre-closure CAP strategy decision. Since then, the final matched repaired control-expanded replication (`pass48`) has closed the public CAP benchmark branch. So this page should now be read as successor-direction scouting, not as a reason to continue CAP tuning. [[bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06]]

## Ranked candidate directions

### Tier 1: Truly open / downloadable
1. **Bruxism CAP (PhysioNet baseline)**
   - Modality: EEG + EMG (`EMG1-EMG2`)
   - Subject count: small and positive-limited
   - Label anchor: PSG + audio-video
   - Openness: high
   - Current role after closure: completed baseline, not the next active tuning branch

2. **Large generic sleep repositories**
   - Modality: broader sleep signals
   - Subject count: high
   - Main problem: poor bruxism-label validity without major relabeling effort

### Tier 2: Data-on-request / proprietary cohorts
3. **Wireless or mmWave monitoring cohorts**
   - Strong translational value
   - Low current reproducibility/access

4. **Earable cohorts**
   - Strong ecological validity
   - Low openness/access

5. **Portable jaw-EMG cohorts**
   - Strongest scientific alignment with the intended future direction
   - Still not open enough to replace CAP as a public benchmark in the old loop, but now the best successor direction to pursue

### Tier 3: Tiny proof-of-concepts
6. **Simulated or healthy-subject sensing studies**
   - Useful for feature ideas
   - Poor as primary benchmark replacements

7. **Very small IMU proof-of-concepts**
   - Interesting modality signal
   - Too small to anchor the next benchmark

## Updated recommendation after closure
### 1. Best realistic successor direction
**Portable or wearable jaw-EMG, with privacy-aware design.**

Before `pass48`, this scout supported an EMG-first framing inside CAP. After `pass48`, the stronger read is different: CAP should remain the preserved public baseline, while the next active design effort should target better future jaw-EMG data surfaces and privacy-preserving wearable measurement design.

### 2. Best “not open enough yet” scientific direction
Wireless/mmWave and earable monitoring remain interesting, but they are still weaker than portable jaw-EMG as the next serious successor branch because they are both less directly jaw-muscle aligned and not clearly open enough.

## Rejection log
- Generic open sleep repositories: rejected as immediate successors because they lack trustworthy bruxism labels.
- Simulated healthy-subject EMG studies: rejected as primary benchmark replacements because label validity is too weak.
- Tiny PoC datasets: rejected because subject count is too small.

## Bottom line
This scout no longer says “continue CAP.” It says:
- preserve CAP as the completed public baseline
- use the scout to prioritize the next non-CAP branch
- treat privacy-preserving wearable jaw-EMG as the most meaningful successor direction
