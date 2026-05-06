---
title: Bruxism CAP translational framing check (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md
  - raw/articles/portable-emg-temporal-patterns-2026.md
  - raw/articles/home-vs-lab-wearable-emg-2022.md
  - raw/articles/sleep-bruxism-emg-only-setups-2020.md
  - raw/articles/advanced-sensing-system-sleep-bruxism-emg-2024.md
  - raw/articles/imu-sleep-bruxism-field-detection-2026.md
  - raw/articles/sleep-bruxism-analysis-window-portable-emg-2026.md
  - raw/articles/sleep-bruxism-emg-frequency-spectrum-pilot-2026.md
  - raw/articles/sleep-bruxism-contingent-electrical-stimulation-2024.md
  - raw/articles/sleep-bruxism-vibratory-feedback-2024.md
  - concepts/bruxism-cap.md
---

# Question
Does the current CAP EMG-first benchmark framing still match the newer translational bruxism sensing literature, or should the repo pivot again?

# Short answer
Yes, the current framing still matches well enough for the repo's actual purpose.

The translational literature is more strongly wearable, multi-night, and intervention-aware than the repo's benchmark loop. But that creates a stronger distinction between project shape and open benchmark availability, not a strong reason to abandon the current CAP EMG-first framing.

# What still looks justified

## 1. EMG-first remains the right signal-family framing
Portable EMG is still the most relevant practical sensing modality in the recent literature, even though the evidence base remains methodologically uneven.^[raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md]

The newer multi-day portable EMG work pushes that same direction harder rather than reversing it.^[raw/articles/portable-emg-temporal-patterns-2026.md]

## 2. CAP still works as the bounded open benchmark
I still do not see a clearly better open dataset ready to replace CAP. The stronger wearable and intervention papers are usually proprietary, device-specific, very small, or not released as benchmark corpora.^[raw/articles/advanced-sensing-system-sleep-bruxism-emg-2024.md]^[raw/articles/imu-sleep-bruxism-field-detection-2026.md]^[raw/articles/sleep-bruxism-contingent-electrical-stimulation-2024.md]^[raw/articles/sleep-bruxism-vibratory-feedback-2024.md]

So CAP remains a reasonable reproducibility scaffold even if it is not the final scientific destination.

## 3. The repo's validity caution is still correct
The older warning about EMG-only scoring unreliability still matters: EMG is the practical sensing family, but not a substitute for gold-standard labeling.^[raw/articles/sleep-bruxism-emg-only-setups-2020.md]

That means the repo is still right to treat CAP as a benchmark proxy and not a clinical detector.

# What the newer literature adds

## 1. Real wearable science is increasingly multi-night and ecological
The strongest newer signal is not "replace EMG" or "replace CAP with another open dataset." It is that clinically interesting bruxism sensing is moving toward home, multi-day monitoring rather than single-night lab-style classification.^[raw/articles/portable-emg-temporal-patterns-2026.md]^[raw/articles/home-vs-lab-wearable-emg-2022.md]

## 2. Analysis-window definitions matter
A 2026 portable masseter-EMG paper showed that event counts shift depending on whether likely wakeful time around bedtime and final awakening is included.^[raw/articles/sleep-bruxism-analysis-window-portable-emg-2026.md]

That actually strengthens the repo's current validity discipline: explicit subset rules and matched scaffolds are scientifically appropriate, not incidental bookkeeping.

## 3. Translational EMG may care about richer descriptors than event counts alone
A 2026 home-PSG pilot found EMG frequency-spectrum features separated TMD-pain status better than conventional bruxism time or activation indices.^[raw/articles/sleep-bruxism-emg-frequency-spectrum-pilot-2026.md]

That does not force a new benchmark pivot, but it is a useful caution against treating frequency-style EMG information as clinically irrelevant.

## 4. The field is becoming intervention-aware
The 2024 CES and vibratory-feedback papers show wearable EMG increasingly coupled to closed-loop management, not only passive detection.^[raw/articles/sleep-bruxism-contingent-electrical-stimulation-2024.md]^[raw/articles/sleep-bruxism-vibratory-feedback-2024.md]

This supports a future intervention-minded branch, but not an immediate rewrite of the current benchmark loop.

# Gaps that remain relative to stronger wearable science
- CAP is still a one-night public benchmark, not a multi-night ecological monitoring dataset.
- The repo still has no symptom, pain, or intervention outcomes.
- The current binary task is narrower than newer phenotype- or management-oriented studies.
- Open benchmark availability still trails the scientific ambitions of the wearable literature.

# Concrete repo implication
Keep the current benchmark branch fixed and describe the stronger translational destination separately:
- benchmark branch now: EMG-first, leakage-aware CAP subject-transfer audit
- future branch later: portable/home/multi-night/intervention-aware EMG once data access exists

# Immediate experiment decision
No immediate experiment should change.

Do not:
- abandon CAP
- demote `EMG1-EMG2`
- force intervention metrics into the current benchmark
- treat newer wearable papers as proof that the current benchmark loop is obsolete

# Bottom line
The translational literature now supports the repo's EMG-first framing even more strongly than before, but it still does not supply a clearly better open benchmark than CAP.

So the right update is restraint, not a pivot: keep the current CAP EMG-first framing, keep the validity caveats explicit, and reserve the wearable/intervention jump for a later branch when data access catches up.
