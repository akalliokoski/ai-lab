---
source_url: https://pubmed.ncbi.nlm.nih.gov/41491795/
ingested: 2026-05-04
sha256: manual-note-2026-imu-field-detection
---

# A new approach for the field detection of sleep bruxism based on inertial sensor data and machine learning classification

Source: PubMed / Scientific Reports (2026)
PMID: 41491795
DOI: 10.1038/s41598-025-29679-8

## Abstract-style summary
- Built a small proof-of-concept setup using a tri-axial IMU to capture mandibular motion.
- Used 21 in-vivo recordings from 3 individuals with manually labeled grinding and opening/closing motions.
- Reported up to about 96% test accuracy with classical ML models when using all sensors together.

## Important caveat
This is an interesting translational direction, but it is a tiny proof of concept with only 3 individuals and manually labeled motion classes, not a strong clinical benchmark.

## Takeaway for ai-lab
If the goal is alignment with where product sensing may go, IMU-based jaw-motion sensing is worth tracking. If the goal is a trustworthy public benchmark today, this is too small and too custom to replace CAP.
