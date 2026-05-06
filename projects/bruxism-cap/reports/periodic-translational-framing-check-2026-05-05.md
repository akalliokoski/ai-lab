# Periodic translational framing check

Date: 2026-05-05
Status: literature framing review completed; current CAP EMG-first benchmark framing still holds as a bounded open-data benchmark, with no immediate experiment pivot required

## Objective

Check whether the repo's current framing still makes scientific sense:
- CAP kept as the open benchmark scaffold
- `EMG1-EMG2` treated as the primary channel
- benchmark read as a leakage-aware reproducibility exercise, not a clinical detector

The question is not whether newer wearable science is more exciting in the abstract.
The question is whether that newer translational literature now makes the current repo framing misleading or obsolete.

## Sources inspected

Previously ingested repo sources:
- `wiki/raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md`
- `wiki/raw/articles/portable-emg-temporal-patterns-2026.md`
- `wiki/raw/articles/home-vs-lab-wearable-emg-2022.md`
- `wiki/raw/articles/sleep-bruxism-emg-only-setups-2020.md`
- `wiki/raw/articles/advanced-sensing-system-sleep-bruxism-emg-2024.md`
- `wiki/raw/articles/imu-sleep-bruxism-field-detection-2026.md`

Newly inspected this pass:
- `wiki/raw/articles/sleep-bruxism-analysis-window-portable-emg-2026.md`
- `wiki/raw/articles/sleep-bruxism-emg-frequency-spectrum-pilot-2026.md`
- `wiki/raw/articles/sleep-bruxism-contingent-electrical-stimulation-2024.md`
- `wiki/raw/articles/sleep-bruxism-vibratory-feedback-2024.md`

Repo framing inspected against:
- `projects/bruxism-cap/README.md`
- `projects/bruxism-cap/reports/first-baseline.md`
- `wiki/concepts/bruxism-cap.md`
- `wiki/queries/bruxism-better-project-and-data-options-2026-05-04.md`

## Short verdict

Yes: the current CAP EMG-first framing still makes sense.

More precisely:
1. `EMG1-EMG2` still looks like the right translationally aligned primary signal family.
2. CAP still looks acceptable as a small open benchmark, even though it is clearly not the ideal clinical or product-shaped dataset.
3. The stronger gap is still between open benchmark science and real wearable/intervention science, not between EMG and some obviously better open replacement inside the repo.
4. The literature supports better future project shape more strongly than it supports a better immediate public benchmark.

## What still looks justified

### 1. EMG-first is still the right translational framing
The 2024 meta-analysis still supports portable EMG as the practical sensing modality, even though evidence quality is limited by study heterogeneity and design weaknesses. The newer 2026 portable-EMG literature pushes even harder in the same direction rather than reversing it.

This means the repo would now look less aligned with the field if it moved back toward an EEG-first story.

### 2. CAP is still defensible as a benchmark scaffold
Nothing in the new sources produced a clearly better open benchmark that should replace CAP now.

The alternative directions are scientifically interesting but operationally weaker for this repo today:
- portable EMG validation studies are usually proprietary or cohort-limited
- home/wearable studies are often not openly downloadable as a reusable benchmark
- IMU/jaw-motion work is promising but still tiny and custom
- intervention papers depend on device-specific setups rather than shared public corpora

So CAP remains a reasonable compromise between openness, auditability, and bounded scope.

### 3. The repo's caution about labels and validity remains scientifically correct
The 2020 EMG-only scoring warning still matters: EMG is the practical sensor, not the gold-standard label source.

That matches the repo's current posture well. The benchmark is not claiming clinical event truth from raw EMG alone; it is using a public polysomnography-derived dataset to test whether a small reproducible EMG-first pipeline transfers honestly across subjects.

### 4. The repo is right to distinguish benchmark clarity from product realism
The newest translational papers are more wearable-minded, more longitudinal, and more intervention-aware. But that does not automatically create a better open benchmark.

So the repo's distinction still holds:
- better project shape in the long run: portable, home, multi-night, possibly intervention-linked EMG
- better open benchmark right now: not clearly available beyond CAP

## What the newer literature adds

### 1. Multi-night and home context matter more than one-night lab framing
The 2026 multi-day portable EMG paper and the earlier home-vs-lab wearable study both push toward ecological monitoring rather than single-night lab-only inference.

Implication: CAP should continue to be framed as a proxy benchmark, not as a miniature version of the final real-world task.

### 2. Window-definition choices matter in wearable-style scoring
The 2026 masseter-EMG analysis-window paper showed that event rates change depending on whether likely wakefulness near bedtime and final awakening is excluded.

Implication: the repo's obsession with explicit extraction windows, overlap rules, and matched scaffolds is scientifically well aligned. This is not over-engineering; translational papers are also sensitive to analysis-period definition.

### 3. EMG may matter for more than crude event counts
The 2026 frequency-spectrum pilot suggests that EMG spectral descriptors may separate clinically relevant phenotypes better than conventional event/time indices alone.

Implication: an EMG-first framing does not mean the repo should only favor simplistic count-like features. Some frequency-domain structure may still be translationally meaningful, even if the current tiny benchmark has not yet converted that into honest subject transfer.

### 4. The field is moving toward intervention-aware wearables
The 2024 contingent electrical stimulation and vibratory-feedback papers reinforce that wearable EMG is increasingly tied to closed-loop management, not only passive detection.

Implication: future science may care about longitudinal responsiveness and symptom coupling, not just binary event classification. But that is a future branch, not a reason to distort the current benchmark into an intervention claim.

## Remaining gaps between the repo and stronger wearable/intervention science

1. Single-night open CAP benchmarking is still far from the multi-night ecological monitoring setup that newer portable-EMG work prefers.
2. The repo still lacks symptom, pain, or intervention outcomes, so it cannot speak to management-oriented utility.
3. CAP-derived labels are still a compromise relative to carefully validated PSG plus audio/video or device-specific intervention studies.
4. The current task is still binary `bruxism` vs `control`, while newer translational work increasingly cares about phenotype, severity, timing context, and response to feedback.
5. Open benchmark availability still lags far behind the conceptual maturity of the wearable science.

These are real gaps, but they are exactly the kind that justify keeping the repo modest rather than forcing a premature pivot.

## One concrete repo-level implication

Keep the current benchmark loop fixed, but preserve translational claims more explicitly as a separate future branch:
- current branch: open, leakage-aware CAP benchmark for honest subject transfer
- future branch: portable/home/multi-night/intervention-aware EMG science once a suitable dataset or recording path exists

In practice, this means the repo should not treat every wearable/intervention paper as a reason to rewrite the immediate benchmark task.

## Immediate experiment decision

No immediate experiment should change.

Specifically:
- do not abandon CAP
- do not demote `EMG1-EMG2` back behind `C4-P4`
- do not force an intervention-oriented metric into the current benchmark loop
- do not pivot away from benchmark-validity work just because the translational literature is more product-shaped

## Bottom line

The translational literature has become more strongly wearable, longitudinal, and intervention-aware, but it has not invalidated the repo's current framing.

If anything, it sharpens it:
- keep `EMG1-EMG2` as the primary scientific direction
- keep CAP as the bounded open benchmark
- keep explicit validity caveats
- keep benchmark improvement separate from claims about real wearable usefulness

So the right read is not "pivot now."
It is "stay EMG-first, stay honest about CAP's limits, and postpone the wearable/intervention jump until data access catches up."
