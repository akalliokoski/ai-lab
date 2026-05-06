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
---

# Dataset Scout: Post-CAP Bruxism Benchmark Candidates

## Objective
Identify 5-10 source-verified candidate datasets or benchmark directions to succeed the current `bruxism-cap` baseline, prioritizing scientific validity, label anchor reliability (PSG/AV), and practical accessibility.

## Ranked Candidate Benchmarks

### Tier 1: Truly Open / Downloadable (The "Reproducibility" Tier)

1. **Bruxism CAP (PhysioNet Baseline)**
   - **Modality:** EEG + EMG (`EMG1-EMG2`)
   - **Subject Count:** Small subset of CAP database.
   - **Positive-case Definition:** Micro-events (A1, A2, A3) from PSG/AV scoring.
   - **Label Anchor:** PSG + Audio-Video.
   - **Openness:** Fully downloadable/open.
   - **Why it's/isn't an upgrade:** It is the *only* truly open benchmark currently available. While it lacks modern "wearable" ecological validity, it is the indispensable baseline for all subsequent work.

2. **Large Pediatric Sleep Repositories (e.g., NSRR/PhysioNet generic)**
   - **Modality:** Primarily EEG/Respiratory/ECG.
   - **Subject Count:** Very high (hundreds/thousands).
   - **Positive-case Definition:** Likely lacks specific bruxism-event labels; requires manual/automated re-labeling.
   - **Label Anchor:** PSG.
   - **Openness:** High.
   - **Why it's/isn't an upgrade:** High subject count for robust statistical power, but requires massive manual effort to create bruxism-specific ground truth.

### Tier 2: Data-on-Request / Proprietary Cohorts (The "Clinical Validity" Tier)

3. **Shen 2025 (Wireless Signal recognition)**
   - **Modality:** Wireless/mmWave signals.
   - **Subject Count:** Not specified in snippet, likely small clinical cohort.
   - **Positive-case Definition:** Likely PSG-anchored.
   - **Label Anchor:** PSG/Wireless sensor.
   - **Openness:** Low (Data-on-request / Proprietary).
   - **Why it's an upgrade:** Represents the next frontier of non-contact/wireless sensing; high translational potential.

4. **Bondareva 2021 (Earables Feasibility)**
   - **Modality:** Earable (likely IMU/Acoustic).
   - **Subject Count:** Small study.
   - **Positive-case Definition:** Clinical bruxism detection.
   - **Label Anchor:** Likely PSG.
   - **Openness:** Low (Proprietary/Request).
   - **Why it's an upgrade:** Highly ecologically valid sensing modality for long-term home monitoring.

5. **Le 2025 (EMG Logger Utility)**
   - **Modality:** Portable EMG Logger.
   - **Subject Count:** Small study.
   - **Positive-case Definition:** Clinical bruxism diagnosis.
   - **Label Anchor:** PSG.
   - **Openness:** Low.
   - **Why it's an upgrade:** Direct validation of the "portable masseter EMG" sensing modality prioritized by recent literature.

6. **Gul et al. 2024 (Advanced Sensing System)**
   - **Modality:** Multi-posture EMG (Temporalis + Masseter).
   - **Subject Count:** 10 (Healthy subjects).
   - **Positive-case Definition:** Simulated/controlled bruxism-like behavior.
   - **Label Anchor:** Manual/Self-report.
   - **Openness:** Low.
   - **Why it's NOT an upgrade:** High feature-engineering value, but subjects are healthy and behaviors are simulated; poor clinical validity.

### Tier 3: Tiny Proof-of-Concepts (The "Novelty" Tier)

7. **IMU 2026 (Field Detection Proof-of-Concept)**
   - **Modality:** Tri-axial IMU (Mandibular motion).
   - **Subject Count:** 3 (Extremely small).
   - **Positive-case Definition:** Manually labeled motion classes.
   - **Label Anchor:** Manual.
   - **Openness:** Likely Low.
   - **Why it's NOT an upgrade:** Too small for a benchmark; useful only for initial modality validation.

## Summary Table

| Candidate | Category | Modality | Openness | Upgrade over CAP? |
|---|---|---|---|---|
| **CAP** | Open | EEG/EMG | High | N/A (Baseline) |
| **Shen 2025** | Request | Wireless/mmWave | Low | Yes (Sensing Novelty) |
| **Bondareva 2021** | Request | Earables | Low | Yes (Ecological Validity) |
| **Le 2025** | Request | Portable EMG | Low | Yes (Translational Alignment) |
| **Gul 2024** | Simulated | Multi-EMG | Low | No (Low Clinical Validity) |
| **IMU 2026** | Tiny PoC | IMU | Low | No (Insufficient Scale) |

## Final Recommendations

### 1. Best Realistic Next Dataset Recommendation
**The "EMG-First CAP" Pivot.** 
Since no other open, high-quality, PSG-anchored dataset exists, the project should continue with **CAP** but undergo a fundamental framing shift. Instead of EEG-centric detection, the project should pivot to **masseter-EMG-first benchmarking**. This uses the existing `EMG1-EMG2` channels in CAP to build the pipeline, ensuring reproducibility while aligning the scientific target with modern portable-EMG literature.

### 2. Best "Not Open Enough Yet" Scientific Direction
**Wireless/mmWave or Earable-based Monitoring.**
The research trends (Shen 2025, Bondareva 2021) point toward non-contact and earable modalities. These offer the highest ecological validity for long-term home monitoring, but the lack of open, large-scale, PSG-validated datasets for these modalities makes them currently unsuitable for a public, reproducible benchmark.

## Rejection Log
- **Gul 2024 (Simulated):** Rejected as a primary benchmark due to lack of clinical bruxism events and use of healthy subjects.
- **IMU 2026 (Tiny PoC):** Rejected due to extreme subject scarcity (N=3).
- **Generic Pediatric Repos:** Rejected for current benchmarking as they lack the necessary bruxism-specific event labels.

## Next Steps
- Update `wiki/concepts/bruxism-cap.md` to reflect the EMG-first pivot.
- Design the first "EMG-only" benchmark runner on the CAP subset.
