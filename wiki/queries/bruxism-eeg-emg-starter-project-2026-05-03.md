---
title: Bruxism EEG/EMG starter project (2026-05-03)
created: 2026-05-03
updated: 2026-05-03
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - raw/articles/cap-sleep-database-physionet-2012.md
  - raw/articles/bruxism-single-channel-eeg-2024.md
  - raw/articles/bruxism-multimodal-ensemble-2024.md
  - raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md
  - raw/articles/sleep-bruxism-emg-only-setups-2020.md
  - raw/articles/advanced-sensing-system-sleep-bruxism-emg-2024.md
---

# Question
What is the simplest bruxism-from-EEG/EMG project to start in ai-lab?

# Short answer
The simplest credible starter project is **an open-data pilot on the PhysioNet CAP Sleep Database**, framed as **binary bruxism-vs-control classification using very simple EEG/EMG features and subject-aware evaluation**. In practice, start with **one open dataset, one channel family, one binary task, and classical models**.

My recommended first version is:

1. **Dataset:** CAP Sleep Database (`brux1.edf`, `brux2.edf` plus a small matched control subset)
2. **Task:** binary classification of bruxism subject / bruxism epochs vs controls
3. **Signals:** start with **one EEG channel** used in the literature (C4-P4 when available) **or one available EMG channel**, but do **not** start with multimodal fusion
4. **Models:** logistic regression, random forest, and SVM on handcrafted spectral + amplitude features
5. **Evaluation:** leave-one-subject-out or subject-level holdout; explicitly avoid random epoch splits

# Why this is the simplest good start

## 1. The public-data path is CAP, not a purpose-built bruxism benchmark
The cleanest open starting point found here is the **PhysioNet CAP Sleep Database**, because it is openly downloadable and explicitly contains `brux1.edf` and `brux2.edf`. That makes it straightforward to build a reproducible first project with no data-access negotiation.^[raw/articles/cap-sleep-database-physionet-2012.md]

## 2. EEG-only reproduction is simpler than EMG hardware collection
The 2024 single-channel EEG paper already shows a concrete, reproducible path on CAP: use REM-sleep epochs, extract time/frequency/nonlinear features, and benchmark a simple classifier. The paper's headline numbers are very high, but the sample is only **2 bruxism patients and 4 controls**, so the real value is the pipeline shape, not the reported accuracy.^[raw/articles/bruxism-single-channel-eeg-2024.md]

## 3. Multimodal fusion is a second project, not the first one
The multimodal ensemble paper reports even stronger numbers from EEG+ECG+EMG, but this almost certainly adds complexity faster than it adds trustworthy evidence because the public bruxism subset is tiny and likely vulnerable to leakage from epoch-level splitting.^[raw/articles/bruxism-multimodal-ensemble-2024.md]

## 4. EMG is the more practical future modality, but not the easiest public benchmark
The broader diagnostic literature says **portable EMG matters**, and a 2024 meta-analysis supports it as a practical approach relative to PSG. But EMG-only setups are also known to be unreliable as a clinical gold standard, which means an EMG-first *device* project is attractive long term while an EMG-only *validation* claim is risky.^[raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md]^[raw/articles/sleep-bruxism-emg-only-setups-2020.md]

## 5. Simulated EMG studies are useful references, not the best first benchmark
The 2024 Sensors study with 10 healthy subjects simulating bruxism-like behavior is useful for feature engineering and wearable design ideas, but it is not the cleanest first ML benchmark because the labels come from instructed behavior rather than natural overnight events.^[raw/articles/advanced-sensing-system-sleep-bruxism-emg-2024.md]

# Recommended first project shape

## Option A — easiest reproducible benchmark (recommended)
**Reproduce a tiny CAP-based classifier with subject-aware evaluation.**

### Setup
- Download CAP Sleep Database metadata and a minimal subset of EDF files.
- Start with the exact bruxism records (`brux1`, `brux2`) and the controls used by the 2024 EEG paper when channel compatibility allows.
- Segment into 30 s windows or use annotated REM windows.
- Extract a compact feature set:
  - band powers (delta/theta/alpha/beta)
  - band ratios
  - RMS / standard deviation
  - sample entropy
- Train logistic regression, random forest, and SVM.
- Report:
  - subject-level split scheme
  - number of windows per subject
  - class balance
  - AUROC / balanced accuracy / sensitivity / specificity

### Why I recommend this
- fully public starting point
- low engineering overhead
- easy to run on the VPS or MacBook
- good project for learning EDF loading, feature extraction, leakage checks, and small-sample evaluation

## Option B — more biologically direct, but harder to source cleanly
**EMG-first jaw-muscle event detection.**

This is closer to the real sensing problem, but it becomes harder immediately because the best signals are usually masseter / temporalis channels from portable or PSG studies that are not as easy to obtain openly in a standardized dataset. Use this as the second project after the CAP reproduction baseline.

# What not to do first
- Do not start with deep learning.
- Do not start with multimodal fusion.
- Do not trust epoch-level cross-validation on a tiny dataset.
- Do not present a first result as clinically meaningful detection.
- Do not start by collecting your own wearable data before you have a working offline pipeline.

# Minimal ai-lab plan

## Week 1 target
Build a tiny but honest baseline repo that can:
1. load CAP EDF files
2. extract one EEG or EMG channel
3. window the signal
4. compute ~10-20 handcrafted features
5. train 2-3 classical models
6. evaluate with subject-level splits
7. write a short artifact report showing leakage-sensitive vs leakage-safe results

## Suggested folder scaffold
- `projects/bruxism-cap/README.md`
- `projects/bruxism-cap/data/README.md`
- `projects/bruxism-cap/notebooks/00_cap_subset_inspection.ipynb`
- `projects/bruxism-cap/src/features.py`
- `projects/bruxism-cap/src/train_baseline.py`
- `projects/bruxism-cap/src/eval.py`
- `projects/bruxism-cap/reports/first-baseline.md`

## Success criterion for project 1
A successful first project is **not** "high accuracy". It is:
- fully reproducible
- based on open data
- leakage-checked
- easy to extend to EMG-first or multimodal follow-ups

# Best next project after that
After the CAP pilot works, the next step should be **EMG-first event detection** on a dataset with jaw-muscle channels and stronger labels, or a small curated wearable pilot if you can access such data. That is the path that better matches real bruxism sensing.

# Current operating status
As of 2026-05-03, `projects/bruxism-cap/` is the main active `ai-lab` project and the artifact-card fine-tuning track is paused. The current goal is to get the first leakage-aware CAP baseline running before adding model complexity or returning to a different primary track.

# Scaffold created in repo
A starter implementation scaffold now exists under `projects/bruxism-cap/` with:
- `README.md` describing the tiny pilot workflow
- `data/README.md` and `data/subject_manifest.example.csv` for the raw CAP subset
- `src/features.py` for handcrafted signal features
- `src/prepare_windows.py` for EDF-to-window-feature extraction
- `src/train_baseline.py` for random-window vs LOSO baselines
- `src/eval.py` for metric comparison
- `reports/first-baseline.md` and `notebooks/00_cap_subset_inspection.ipynb` for experiment execution and inspection

This keeps the first project grounded in open data and makes the next step concrete: download a tiny CAP subset, inspect channels, generate `window_features.csv`, then compare random-window CV against subject-aware CV.

# Bottom line
If the goal is to get moving **this week**, start with a **public CAP-based, classical-feature, subject-aware baseline** and treat it as a **reproduction / benchmarking project**. If the goal is the **best eventual sensing modality**, EMG is probably the better long-term focus, but it is not the cleanest zero-friction public starting point I found today.
