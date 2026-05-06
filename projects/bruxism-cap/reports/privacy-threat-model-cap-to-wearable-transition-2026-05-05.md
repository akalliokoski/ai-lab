# Privacy threat model and CAP-to-wearable transition memo for `bruxism-cap`

Date: 2026-05-05
Status: bounded repo-specific memo completed; this is a future-branch constraint note, not a claim that the repo already operates a wearable fleet or handles private jaw-EMG user data.

## Why this memo exists

The current repo is still a bounded public-data benchmark:
- CAP remains the active open benchmark because the latest translational check did not surface a clearly better open replacement.
- `EMG1-EMG2` remains the primary benchmark channel and `C4-P4` remains the honest comparison anchor.
- The campaign handoff explicitly said privacy/PET work should wait until one more bounded benchmark question was answered.
- That question has now been answered narrowly by pass36: the pass34 record-relative and pass35 compact-shape clues do compose honestly on the repaired five-subject scaffold, but only partially, because `brux1` still fails while `brux2` recovers.

So this memo activates the first bounded privacy branch without pretending the benchmark is finished or that the repo has already become a product. The right read is: the CAP benchmark is now stable enough to support one repo-specific privacy memo, while the main modeling loop still remains a benchmark and not a wearable deployment.

## Current benchmark state that should constrain privacy design

Any future privacy design for this repo should stay tied to what the benchmark actually is today:
- data scale is tiny and subject count is very low
- subject-aware evaluation is the core honesty discipline
- pass29 `C4-P4` is still the comparison anchor on the repaired `A1-only` percentile-band scaffold
- pass36 improves EMG subject-level sensitivity to `0.500`, but only by recovering `brux2`; `brux1` remains the unresolved bottleneck
- the repo still relies on handcrafted windows, derived features, and simple models rather than end-to-end deep wearable inference

That matters because the first privacy transition should protect future wearable data without breaking the current benchmark discipline. Privacy work here should be additive system design around the benchmark, not a premature rewrite of the benchmark itself.

## Main threat-model shift: from public CAP benchmark to private jaw-EMG collection

Today the repo mostly handles public CAP signals. The privacy posture changes sharply if the project ever ingests user or wearable jaw EMG, even before any cloud training or product features exist.

The first sensitive surfaces would be:
1. Raw jaw-EMG waveforms from nights at home
2. Per-window timestamps and recording schedules
3. Device, firmware, phone, and app metadata
4. Derived feature tables computed from those waveforms
5. Subject-level scores, alerts, trend summaries, and clinician/research exports
6. Trained model parameters or embeddings if they are updated from private user data

The practical rule for this repo is simple: once signals stop being public CAP records and start being user-specific jaw EMG, almost every layer becomes health data, not just the raw waveform.

## Concrete sensitive surfaces for this repo

### 1. Raw waveform leakage
The repo currently extracts fixed windows and computes morphology, envelope, and record-relative features. In a wearable future, the underlying jaw-EMG waveform itself becomes the highest-risk artifact.

Why it is sensitive here:
- it may encode highly individual muscle activation patterns and electrode-placement quirks
- it can reveal sleep timing, event density, arousal structure, and night-to-night behavior
- it is rich enough that future models could infer more than the current repo intends
- if raw windows are exported, the repo loses the cleanest privacy boundary it could preserve early

Repo-specific implication:
- do not let future wearable ingestion normalize raw waveform export just because the current benchmark uses offline CSV/report artifacts
- treat raw wearable waveform retention as an exceptional debugging mode, not the default data path

### 2. Metadata leakage
Even if waveforms never leave device, metadata can still leak a lot:
- nightly recording start/end times
- timezone and locale
- device model, firmware version, electrode impedance or battery status
- frequency of missed nights or partial recordings
- app version and experiment cohort tags

Repo-specific implication:
- the current benchmark culture values detailed audit artifacts, but that same habit becomes dangerous on private users
- future wearable logs must avoid copying exact timestamps, device identifiers, or per-user run handles into normal research exports

### 3. Health-state inference leakage
The repo currently asks a narrow benchmark question: can a small feature pipeline separate bruxism from control honestly under LOSO? A wearable system would create broader health inferences automatically, even if the product claim stays narrow.

Possible unintended inferences from jaw-EMG or its summaries:
- sleep fragmentation or arousal burden
- medication, stress, alcohol, or pain-related state changes
- temporomandibular or clenching intensity proxies
- adherence, insomnia-like patterns, or other behavioral rhythms

Repo-specific implication:
- future exports should not assume that "derived feature" means "safe"
- several current feature families (`mean`, `ptp`, `zero_crossing_rate`, envelope statistics, shape terms, and record-relative summaries) are useful exactly because they preserve physiological structure; that same usefulness can support unwanted health-state inference

### 4. Re-identification / biometric leakage from waveform or feature signatures
Even if the project never stores names, repeated nights from the same person may still be linkable through stable signal characteristics.

High-risk linkable surfaces for this repo would include:
- raw windows or long clips
- high-resolution per-window feature rows
- persistent subject embeddings or latent vectors
- stable subject-level score fingerprints across nights
- feature-distribution summaries tied to exact devices or nights

Repo-specific implication:
- current benchmark artifacts often preserve per-subject score tables because the subject set is public and tiny
- in a wearable branch, per-subject score dumps and row-level feature exports should be treated as sensitive by default because they can become pseudonymous biometric traces

### 5. Model inversion / membership / gradient leakage
The current repo uses small classical models, but a future personalized or federated branch could still leak information through model artifacts.

Risk surfaces include:
- model parameters trained on tiny user cohorts
- per-round gradient or update sharing
- feature importance tables computed on small populations
- debugging exports that compare one subject against cohort means

Repo-specific implication:
- the repo's tiny-N discipline is scientifically honest for benchmarking, but tiny-N makes privacy worse if the same artifact shapes are exported from real users
- any future cross-device learning path should assume that naive parameter sharing is not privacy-preserving just because raw waveforms stay local

## What should stay on device or phone side

For this repo's first wearable transition, the safest default boundary is:
- sensor -> phone/device local preprocessing -> local feature extraction -> local scoring -> export only minimal bounded summaries when needed

The following should stay on device or phone side by default:
1. Raw jaw-EMG waveforms
2. Long contiguous waveform segments
3. Exact per-window timestamps
4. Exact event-aligned window selections
5. Per-night full feature tables at window granularity
6. Debug plots that reconstruct waveform morphology closely
7. Personalized calibration state tied to one user
8. Any local labels or notes linked to a specific night's symptoms

Repo-specific reason:
- the benchmark currently derives its insight from per-window analyses and subject-score tables, but exporting that same structure from private wearables would recreate the most sensitive layer outside the phone

## What may leave device first, if the project ever transitions carefully

If anything leaves device early, it should be the least reconstructive, least linkable, most purpose-bounded layer.

Safer first candidates are:
1. Cohort-level aggregate metrics with minimum cohort sizes
   - example: mean nightly positive-window fraction over many users
   - only if exact dates and user IDs are removed and cohort sizes are large enough

2. Per-night coarse summaries with heavy minimization
   - example: one nightly bruxism-risk bin, one confidence bin, one wear-time bin
   - better than exporting window-level rows

3. Range-limited derived counters
   - example: count of candidate jaw-activity bursts per night, clipped/bucketed rather than exact

4. Trend summaries over longer windows
   - example: 2-week rolling change categories rather than raw nightly trajectories

5. Privacy-reviewed benchmark-surrogate tables
   - if research absolutely needs off-device analysis, export only a reduced feature set that has been explicitly screened for reconstructive and linkage risk

Important caveat:
- even these are not automatically safe; they are only safer than raw waveform or dense per-window feature export
- the right first export surface for this repo is likely coarse nightly summaries, not the current pass-style window tables

## Derived features that are especially risky to export unchanged

Because this repo already knows which features drive separation, it should assume those same features can leak physiology.

Higher-risk export candidates include:
- raw-location/amplitude families such as `mean`, `min`, `max`, `ptp`
- envelope and burst morphology summaries such as `rectified_*`, `envelope_*`, `p95_abs`, `burst_fraction`
- shape descriptors such as `skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`
- any record-relative normalization outputs when paired with enough raw context to reconstruct intra-night distribution shifts
- dense per-window entropy or transition descriptors such as `sample_entropy` and `zero_crossing_rate`

Why risky here:
- they are useful precisely because they preserve individual morphology and night structure
- pass34/pass35/pass36 show that representation changes can strongly alter subject ordering, which means these features retain person- and night-specific information rather than acting like harmless generic counts

## Leakage surfaces to name explicitly

### Waveform re-identification
Risk: raw or near-raw jaw-EMG segments may support linking repeated nights from the same person, and could become more identifying as better models appear.

Repo constraint:
- do not build the future pipeline around server-side waveform archives for convenience

### Metadata leakage
Risk: timestamps, timezone, device IDs, app/build IDs, and recording gaps can reveal routines, geography, adherence, or cohort membership.

Repo constraint:
- keep experiment-traceability discipline, but redesign it around coarse audit IDs and local-only logs rather than user-identifying research exports

### Health-state inference
Risk: off-device artifacts may let later analysts infer more than bruxism, including stress, sleep quality, or other health signals.

Repo constraint:
- future reports should state the allowed inference target explicitly and minimize all other retained dimensions

### Model inversion / membership inference
Risk: a server or collaborator may infer whether a person's nights were in training, or approximate unique signal traits from shared updates or small-cohort models.

Repo constraint:
- if collaborative learning is explored later, secure aggregation and cohort thresholds should be treated as entry requirements, not optional upgrades

## CAP-to-wearable transition constraints for this repo

This repo should not jump directly from CAP benchmarking to cloud-centered wearable learning. The transition should preserve the benchmark's honesty rules while adding privacy boundaries.

Concrete constraints:
1. Keep CAP and wearable branches conceptually separate
   - CAP remains the public reproducible benchmark.
   - wearable data, if it appears later, should live behind a separate data boundary and should not silently mix into CAP artifacts.

2. Do not export raw waveform just because CAP artifacts are file-based
   - the current repo culture saves CSVs, JSON metrics, and markdown reports.
   - that pattern should not be copied naively to wearable waveforms or dense per-window tables.

3. Keep phone-side feature extraction ahead of cloud-side modeling
   - the first wearable stack should compute candidate features on device/phone first.
   - off-device training or analysis, if any, should start from minimized summaries.

4. Preserve subject-aware evaluation logic locally
   - LOSO and subject-level aggregation are central lessons from the repo.
   - a wearable branch should preserve user-level holdout thinking in simulation/prototyping rather than regress to pooled random splits.

5. Separate research observability from user-data observability
   - benchmark reports can stay detailed on CAP.
   - private-wearable observability needs different defaults: fewer raw artifacts, more local inspection, stricter export gates.

6. Avoid pretending federated learning solves the whole problem
   - federated or collaborative learning may help later, but it does not remove leakage from gradients, updates, or tiny cohorts.
   - privacy design should begin with minimization and boundary placement, not with a crypto buzzword.

7. Keep the future branch bounded and simulation-first
   - until there is actual hardware or private data collection, use CAP-derived simulations or architecture memos rather than product-like claims

## Recommended architecture posture if the repo ever evolves

A clean first posture would be:
- CAP branch: public benchmark, reproducible reports, current pass discipline
- wearable local branch: phone-side signal cleaning, feature extraction, scoring, and storage
- optional research export branch: only coarse derived summaries, cohort-gated and privacy-reviewed
- optional collaborative learning branch later: only after threat-model review, cohort thresholds, and secure aggregation design exist

This keeps the benchmark useful while preventing the repo from inheriting a server-first data habit that would be hard to unwind later.

## What not to do first

Do not start with:
- server-side raw waveform collection
- uploading full per-window feature CSVs modeled after current CAP artifacts
- central dashboards with exact nightly timestamps per user
- tiny-cohort parameter sharing marketed as privacy-preserving by default
- broad claims that federated learning or differential privacy are already justified here

Those moves would import the benchmark's most detailed artifact style into the most sensitive future setting.

## One clean next bounded privacy task

Recommended next task:
- `privacy: design a minimized off-device export schema for future wearable bruxism-cap experiments`

Why this next:
- it follows directly from this memo
- it stays non-clinical and non-productized
- it is still repo-specific
- it does not require a wearable fleet
- it creates a concrete bridge between current CAP artifact habits and a safer wearable architecture

Expected output shape:
- one schema memo listing exactly which fields would be allowed off device at nightly, weekly, and cohort level
- one denylist of fields that must remain local (raw waveform, exact timestamps, dense per-window rows, stable identifiers)
- one rationale mapping each allow/deny decision back to the leakage surfaces named here

## Bottom line

The current repo should remain honest about what it is: a small CAP benchmark with partial EMG progress, not a wearable detector. But if the project grows toward private jaw-EMG learning, privacy constraints appear immediately and should be designed around this repo's real artifact flow.

The core transition rule is:
- keep raw waveform, dense timing structure, and personalized calibration local
- let only minimized derived summaries leave device first
- treat pass29/pass36-style benchmark discipline as a guide for honest evaluation, not as permission to export equally detailed private artifacts

That is the cleanest way to open the wearable future branch without breaking either the repo's scientific discipline or its future privacy posture.
