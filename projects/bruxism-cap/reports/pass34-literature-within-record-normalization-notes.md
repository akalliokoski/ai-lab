# Pass 34 — literature scan on within-record normalization and amplitude-invariance ideas for `EMG1-EMG2`

Status: literature-only synthesis completed; the repo evidence and external literature both point toward a bounded record-relative feature-space normalization audit, not another deletion-first pass and not a full feature-family rewrite.

## Repo context held fixed
- Current scaffold to protect: repaired matched `SLEEP-S2 + MCAP-A1-only` percentile-band `EMG1-EMG2` surface from pass28/pass29/pass30/pass31/pass32/pass33.
- Honest framing to preserve: same verified `5`-subject LOSO benchmark, same simple handcrafted baseline family, no claim that a new representation is already better.
- Current bottleneck from parent task: on the repaired scaffold, `brux1` still trails `n3`, and deletion-only ablations either fail to move `n3` or collapse `brux1`.

## Papers / sources inspected
1. Burden A. 2010. “How should we normalize electromyograms obtained from healthy participants? What we have learned from over 25 years of research.” PMID 20702112.
   - Key point: when the goal is reducing inter-individual variability, task-derived peak or mean EMG from the task under study is often a better reference than generic external normalization; MVC is not automatically superior.
2. Besomi M et al. 2020. “Consensus for experimental design in electromyography (CEDE) project: Amplitude normalization matrix.” PMID 32569878.
   - Key point: normalization choice should match the interpretation target; the point is comparable relative activation, not blindly maximizing amplitude invariance.
3. Yang JF, Winter DA. 1984. “Electromyographic amplitude normalization methods: improving their sensitivity as diagnostic tools in gait analysis.” PMID 6477083.
   - Key point: subject/task-relative normalization can reduce intersubject variability more effectively than raw amplitude comparison.
4. Liu L et al. 2013. “Electromyogram whitening for improved classification accuracy in upper limb prosthesis control.” PMID 23475374.
   - Key point: whitening reduced coefficient of variation of time-domain features and improved classification accuracy by about 5 points in their setup.
5. Hargrove LJ et al. 2010. “Study of stability of time-domain features for electromyographic pattern recognition.” PMID 20492713.
   - Key point: effort variation and electrode shift materially destabilize common time-domain features; autoregressive and cepstral coefficients were more stable than the weakest feature sets.
6. Jiang N et al. 2014. “Invariant Surface EMG Feature Against Varying Contraction Level for Myoelectric Control Based on Muscle Coordination.” PMID 25014975.
   - Key point: force variation can be reduced by using features built for contraction-level invariance rather than raw amplitude alone, but the proposed approach leans on multi-muscle coordination structure.
7. Ikeda T et al. 1996. “Criteria for the detection of sleep-associated bruxism in humans.” PMID 9161232.
   - Key point: even classical sleep-bruxism automation uses subject-specific thresholds (for example activity above a small percentage of each subject’s own MVC), which supports the general idea that record-relative scaling is physiologically natural in this domain.
8. Repo notes inspected: pass19, pass22, pass25, pass28, pass30, pass31, pass33 plus `wiki/concepts/bruxism-cap.md` and parent bottleneck handoff.

## What the literature suggests for this repo

### 1) Best fit: within-record robust feature-space normalization on the retained morphology-envelope family
Implementation shape:
- Keep extraction windows, selector, subjects, and model family fixed.
- Compute the existing features first on the repaired pass28 scaffold.
- For a narrow family only, convert raw values into record-relative values using per-record median and robust spread or quantiles across the kept windows from that record.
- Most relevant family on current evidence: `mean`, `max`, `ptp`, `line_length`, `zero_crossing_rate`, `rectified_std`, `envelope_std`, `envelope_cv`, and optionally `rectified_mean`, `envelope_mean`, `p95_abs`.

Why it fits:
- Burden 2010, CEDE 2020, and Yang/Winter 1984 all favor normalization that is anchored to the task/record when the problem is comparability across subjects.
- It directly addresses the current parent hypothesis: EMG morphology may need a record-relative representation rather than more feature deletion.
- It stays inside the current handcrafted baseline and LOSO framing.

Concrete transform candidates:
- robust z-score per record: `(x - median_record_feature) / MAD_record_feature`
- percentile-centered version: `(x - p50_record_feature) / (p90_record_feature - p10_record_feature)`
- ratio-to-record-peak or ratio-to-record-p95 for amplitude features only

### 2) Also plausible: keep raw features, add record-relative companion features instead of replacing them
Implementation shape:
- Add `*_rel_med`, `*_rel_p95`, or `*_robustz` columns for the retained EMG morphology-envelope family.
- Audit raw-only vs relative-only vs raw+relative on the same pass28 scaffold.

Why it fits:
- The pass22 negative result argues against normalizing every signal window before feature extraction.
- A companion-feature strategy preserves weak absolute information that pass22 may have erased while still giving the model a within-record comparison surface.

Most plausible fields for companion versions:
- amplitude/location: `mean`, `max`, `ptp`, `rectified_mean`, `rectified_std`, `envelope_mean`, `envelope_std`, `p95_abs`
- maybe not `sample_entropy` initially, because the pass31/pass33 evidence suggests the main control-favoring support is broader morphology and location, not only one complexity metric.

### 3) Bounded but second-tier: whitening before feature extraction
Implementation shape:
- Add one optional preprocessing mode before feature extraction that whitens the 30 s EMG window, then recompute the same handcrafted family.

Why it is interesting:
- Liu 2013 reported lower coefficient of variation for time-domain features and better classification.
- It is one of the few concrete preprocessing ideas that directly targets feature variability rather than only amplitude scaling.

Why it is not the first thing to test here:
- It is broader than the parent bottleneck and may change nearly every feature at once.
- It is less directly aligned with the repo’s current `brux1` vs `n3` representation question than a feature-space record-relative audit.

### 4) Heavier fallback: replace part of the current morphology family with more stable descriptors (AR / cepstral / TD-PSD-like)
Implementation shape:
- Add a compact stable descriptor family, retrain on the same scaffold, compare against current retained family.

Why it is supported:
- Hargrove 2010 found AR and cepstral coefficients more robust under effort variation/electrode shift.
- Phased myoelectric-control literature often treats force variation as a feature-design problem, not only a scaling problem.

Why it should not be the next pass:
- It is a broader feature-family change, not the smallest bounded adaptation.
- It risks becoming a new benchmark branch instead of a clean test of the current representation hypothesis.

## Which ideas likely overfit or are too heavy for this repo
- MVC-based normalization as the main next move: too heavy / not really available here. CAP does not include a clean calibration task, and inventing one from the record would blur the benchmark framing.
- Multi-muscle coordination invariant features from Jiang 2014: too far from the current setup. That work relies on multi-muscle coordination geometry and hand-motion control assumptions that do not map neatly onto one bipolar sleep EMG benchmark.
- Broad retraining on all force/posture disturbance strategies from prosthesis-control papers: over-scoped for this tiny LOSO CAP subset.
- Full signal-level normalization of every window before all feature extraction: already partly tested negatively in pass22 (`median_mad`), so repeating a broad signal-first rewrite is lower value than record-relative feature normalization.

## One smallest bounded adaptation to test next
Run exactly one matched audit on the repaired pass28 scaffold:

1. Keep the selected rows fixed.
2. Keep model family fixed.
3. Keep the current retained EMG morphology-envelope family fixed.
4. Create one alternate feature table where only that retained family is transformed into within-record robust relative form.
5. Compare raw vs transformed on:
   - LOSO subject means for `brux1`, `brux2`, `n3`, `n5`, `n11`
   - `best bruxism - highest control` margin
   - specifically the `n3 - brux1` gap

Recommended first transform:
- For each subject and each selected feature in the retained family, compute `(x - median) / max(MAD, eps)` across that subject’s kept windows.
- Leave non-morphology metadata and currently excluded families unchanged.

Why this is the best next step:
- It is smaller than whitening.
- It is more faithful to the literature than another blind deletion.
- It directly tests the parent hypothesis that the issue is record-relative representation, not feature presence alone.
- It avoids the main pass22 pitfall by normalizing feature distributions within record rather than normalizing each waveform before extraction.

## Exact repo files likely involved
Most likely:
- `projects/bruxism-cap/src/features.py`
  - only if the transform is implemented as a reusable helper in the feature pipeline.
- `projects/bruxism-cap/src/prepare_windows.py`
  - only if you decide to emit both raw and relative features directly during extraction.
- `projects/bruxism-cap/src/train_baseline.py`
  - likely unchanged for a pure transformed CSV, but relevant if new metadata columns are added and must stay excluded.
- `projects/bruxism-cap/src/run_pass33_raw_location_ablation.py`
  - current report already points to this exact next direction; useful as the template to clone.
- `projects/bruxism-cap/src/audit_percentile_band_channel_gap.py`
  - useful reference for the current repaired scaffold and the `brux1` vs `n3` / `brux2` vs `n3` audit surfaces.

Cleanest likely new file:
- `projects/bruxism-cap/src/run_pass34_record_relative_emg_audit.py`
  - read pass28 CSV
  - derive within-record transformed companion table
  - run LOSO raw vs relative comparison
  - emit summary focused on `brux1`, `n3`, and `best-bruxism-minus-highest-control`

## Bottom line
The literature does support normalization-aware ideas here, but it points more toward task/record-relative feature comparison than toward another per-window waveform normalization. The smallest honest next test is not “normalize everything again”; it is “keep the repaired pass28 scaffold and compare raw retained EMG morphology features against a within-record robust relative representation on the same LOSO surface.”
