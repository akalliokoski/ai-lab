# Literature scan — compact EMG morphology ideas for the repaired `A1-only` scaffold

Date: 2026-05-05
Status: literature scan completed; current repo bottleneck still looks representation-driven, and the strongest next ideas are compact morphology changes rather than a dataset switch or a model-family rewrite

## Objective

Scan recent literature for compact EMG feature or morphology ideas that match the repo's current failure pattern on the repaired percentile-band `A1-only` scaffold:
- `EMG1-EMG2` still misses both bruxism subjects
- `brux1` remains below `n3` on the same matched scaffold where `C4-P4` is stronger
- deletion-only passes are now preserved negative results

This memo stays bounded to ideas that fit the current handcrafted baseline and current CAP benchmark posture.

## Repo bottleneck used as the filter

Grounding from the current repo state:
- Parent task `t_ffddab6c` localized the next bottleneck to EMG representation, not extraction validity alone and not another deletion-first pass.
- `pass30` showed the repaired percentile-band `A1-only` scaffold is timing-matched across channels, so the remaining gap is not just a row-selection artifact.
- `pass31` showed the suspected narrow trio (`sample_entropy`, `burst_fraction`, `envelope_cv`) recurs but does not explain the whole `n3 > brux1` problem.
- `pass33` showed removing only `mean`, `min`, and `max` makes `EMG1-EMG2` worse by collapsing `brux1` (`0.270 -> 0.030`) while `n3` stays high (`0.530 -> 0.527`).

Working read: the current handcrafted EMG family is still mixing subject-specific amplitude/location effects with genuine morphology, and the next increment should change representation more carefully than it changes feature count.

## Sources inspected

Repo-local literature notes:
- `wiki/raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md`
- `wiki/raw/articles/advanced-sensing-system-sleep-bruxism-emg-2024.md`
- `wiki/raw/articles/sleep-bruxism-emg-frequency-spectrum-pilot-2026.md`
- `wiki/raw/articles/portable-emg-temporal-patterns-2026.md`
- `wiki/raw/articles/sleep-bruxism-analysis-window-portable-emg-2026.md`
- `wiki/raw/articles/portable-masseter-emg-validity-2019.md`

Additional PubMed / PMC inspection during this pass:
- PMID `33772835` — ambulatory EMG scoping review for sleep bruxism; highlighted wide variability in rectification, filtering, thresholding, and event definitions, and argued outcomes often reduce to frequency, duration, and intensity of masticatory muscle activity.
- PMID `39205120` — Sensors 2024 feasibility study; used 10 compact time-domain statistics including mean, standard deviation, variance, co-variance, kurtosis, skewness, root mean square, square integral, average energy, and temporal moment.
- PMID `31754982` — surface-EMG recognition evaluation; reported a compact feature set of waveform length + correlation coefficient + Hjorth parameters, and noted logarithmic RMS plus normalized logarithmic energy among the best-performing single features.
- PMID `41354960` — stage-specific EMG feature optimization; from 38 time/frequency features, compact subsets repeatedly kept time-domain features, especially Difference Absolute Standard Deviation Value and Sample Entropy, while performance improved when selection was matched to the population rather than forced as one universal set.
- PMID `17473984` and PMID `20526612` — TKEO-conditioned surface EMG onset papers; both reported that Teager-Kaiser energy conditioning improved burst/onset boundary detection by emphasizing amplitude plus instantaneous-frequency changes.
- PMID `41581017` — 2026 sleep-bruxism spectral pilot; reported that EMG frequency-spectrum descriptors separated TMD-pain-related sleep bruxism severity better than conventional activity/time indices alone.

## Ideas that fit this repo

### 1. Record-relative and log-compressed amplitude-envelope features

What to add:
- `log_rms`
- `log_p95_abs`
- `log_envelope_mean`
- record-relative z-score or quantile versions of `rectified_mean`, `rectified_std`, `envelope_mean`, `envelope_std`, `p95_abs`, `ptp`, `rms`
- optionally a simple within-record percentile rank for each selected window against that subject's eligible pool

Why this fits the exact bottleneck:
- `pass33` strongly suggests the raw location family is not simply "bad"; deleting it collapses `brux1`, which means some amplitude information is useful but currently represented in a fragile cross-subject way.
- The best external support here is not that bruxism-specific papers prove log transforms, but that general sEMG work repeatedly rewards log-energy / log-RMS style compaction (PMID `31754982`) and that the current parent task already pointed toward record-relative representation instead of more deletion.
- This is the most direct way to test whether `brux1` is being punished for absolute scale while preserving the directionally useful information inside the amplitude-envelope family.

Why it is small enough:
- no selector change
- no model-family change
- no dataset change
- compatible with the existing `extract_window_features(...)` path plus a small post-extraction within-record transform

### 2. Shape-only morphology statistics that reduce dependence on raw level

What to add:
- `skewness`
- `kurtosis`
- one compact temporal-moment feature
- `hjorth_mobility`
- `hjorth_complexity`

Why this fits the exact bottleneck:
- The current failure family is broad and still led by location / spread / roughness terms (`mean`, `max`, `ptp`, `zero_crossing_rate`) rather than one obviously wrong feature.
- The Sensors 2024 study (PMID `39205120`) explicitly used compact higher-order statistics such as kurtosis, skewness, square integral, average energy, and temporal moment.
- The recognition-evaluation paper (PMID `31754982`) found Hjorth parameters useful inside a compact sEMG set.
- These features are attractive here because they may preserve morphology/shape differences without leaning as hard on absolute level as `mean`/`max` do.

Why it may help this exact gap:
- `n3 > brux1` survived both the broad and narrow deletion passes, which suggests the remaining separation problem is not only amplitude magnitude but also waveform organization or roughness shape.
- Hjorth-style mobility/complexity and moment/skewness/kurtosis descriptors are cheap ways to test whether `brux1` and `brux2` differ from controls in waveform shape even when absolute level is unstable.

### 3. Better burst morphology via TKEO-conditioned or adaptive-threshold burst features

What to add:
- compute a Teager-Kaiser-energy-conditioned signal before burst detection
- from that conditioned trace, derive compact burst descriptors such as:
  - burst count
  - mean burst duration
  - median burst duration
  - burst duty cycle
  - burst inter-burst interval summary
- keep the feature count small; do not build a large event engine

Why this fits the exact bottleneck:
- The repo already has `burst_fraction` and `burst_rate_hz`, but they are built from a simple `rectified_mean + rectified_std` threshold on the raw rectified trace.
- The sleep-bruxism scoping review (PMID `33772835`) stressed that thresholding and signal-processing choices vary widely and affect what gets counted as masticatory muscle activity.
- The TKEO papers (PMID `17473984`, `20526612`) are not bruxism-specific, but they directly support a cheap preprocessing step that sharpens muscle-activity boundaries by using amplitude plus instantaneous-frequency changes.

Why it may help this exact gap:
- If `n3` is benefiting from diffuse high-roughness windows while brux windows are more burst-like, the current threshold may be too crude to represent that difference.
- A better-conditioned burst representation is one of the few compact changes that can alter morphology meaningfully without leaving the handcrafted baseline.

### 4. EMG-specific spectral descriptors, but only in a compact and event-aware form

What to add:
- `median_frequency`
- `mean_frequency`
- one low/high EMG-band ratio chosen for the CAP sampling limits
- preferably compute them on active / burst-dominant portions or on the rectified-conditioned signal rather than on the entire window with EEG-style band logic

Why this still fits despite the repo's earlier spectral negatives:
- `pass17` showed that removing the current `bp_*`, `rel_bp_*`, and `ratio_*` family did not rescue the benchmark, but that was mostly a negative result for the current broad EEG-style spectral package, not for all possible EMG spectral morphology.
- The 2026 bruxism spectral pilot (PMID `41581017`) specifically argues that frequency-spectrum descriptors can capture clinically meaningful variation that simple activity/time counts miss.
- The same paper is a caution against over-learning from the current negative spectral result: it may be the wrong spectral representation, not proof that EMG spectrum is irrelevant.

Why this is only the fourth idea, not the first:
- it is more fragile than the record-relative amplitude and shape ideas
- the current dataset is tiny
- it is easier to overfit if the spectrum is computed too broadly or with EEG-centric bins

## Ideas that do not fit well right now

### A. Full dataset switch away from CAP
Not justified by the inspected literature. The 2024 meta-analysis and newer wearable papers strengthen the translational case for EMG, but they do not reveal a clearly better open dataset that should replace the current benchmark immediately.

### B. A broad deep-learning rewrite
Not the smallest next step. The current bottleneck is already localized enough that one representation-aware handcrafted rerun is the sharper experiment. A model-family rewrite would hide whether the gain came from representation or just extra capacity.

### C. Cross-channel correlation / multi-muscle relational features
PMID `31754982` reported correlation-coefficient utility in general sEMG recognition, and the Sensors 2024 feasibility paper also discussed co-variance/correlation-style statistics across muscles. That does not transfer cleanly to the current repo because the main benchmark surface is intentionally single derived channel (`EMG1-EMG2`) on a tiny subject set. It would also blur the current matched EMG-vs-C4 interpretation.

### D. Posture- or simulation-specific classifiers from the Sensors 2024 paper
Useful as feature inspiration, not as a benchmark template. That study used healthy subjects performing bruxism-like behaviors across postures, so its reported classifier success should not drive immediate benchmark decisions here.

## Smallest next experiment to run here

Run exactly one representation-focused matched rerun on the repaired percentile-band `A1-only` `EMG1-EMG2` scaffold:

1. Keep the current selector, subjects, labels, window cap, and `logreg` LOSO surface fixed.
2. Keep the current retained EMG family from `pass33` as the base.
3. Add only a compact record-relative representation layer for the amplitude-envelope family:
   - raw features preserved for comparison
   - within-record robust z-score or percentile-rank versions added for `rms`, `ptp`, `rectified_mean`, `rectified_std`, `envelope_mean`, `envelope_std`, `p95_abs`
   - log-compressed versions added for `rms`, `envelope_mean`, `p95_abs`
4. Rerun only `EMG1-EMG2` first.
5. Compare against `pass28` / `pass33` on:
   - subject-level sensitivity
   - `brux1 - n3` margin
   - best-bruxism minus highest-control margin

Why this is the smallest good test:
- it is the most directly supported by both the repo evidence and the external sEMG literature
- it answers the parent question of representation before feature-family expansion
- it avoids turning one literature pass into a large uncontrolled rewrite

## If that smallest experiment fails

The next compact fallback should be shape-focused, not a dataset pivot:
1. add `skewness`, `kurtosis`, `hjorth_mobility`, and `hjorth_complexity`
2. keep the selector and model fixed again
3. postpone TKEO-conditioned burst features until after the record-relative audit, because burst-threshold changes are slightly harder to interpret

## Exact repo files likely involved

Most likely direct edits:
- `projects/bruxism-cap/src/features.py`
- `projects/bruxism-cap/src/prepare_windows.py`
- `projects/bruxism-cap/src/train_baseline.py`
- `projects/bruxism-cap/src/audit_percentile_band_channel_gap.py`

Likely new or copied runner / report scripts:
- `projects/bruxism-cap/src/run_pass34_emg_record_relative_representation.py` (new bounded rerun script)
- `projects/bruxism-cap/reports/` (new pass34 JSON/markdown outputs)

Possibly useful audit surfaces if shape/burst features are added later:
- `projects/bruxism-cap/src/run_pass33_raw_location_ablation.py` (template for a tightly bounded follow-up)
- `projects/bruxism-cap/src/audit_emg_feature_validity.py`

## Bottom line

The literature does not point to a better immediate dataset or a need for a deeper model. It points to a narrower fix: keep the repaired scaffold fixed and make the EMG morphology representation less raw-level-dependent before trying another deletion pass.

The best next single experiment is therefore not "remove more features" and not "switch datasets." It is "re-express the retained amplitude-envelope family in a record-relative, log-compressed form and see whether `brux1` and `brux2` recover against `n3` without changing the benchmark surface."