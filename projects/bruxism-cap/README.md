# bruxism-cap

Minimal starter scaffold for **bruxism detection from EEG / EMG signals** using the public **PhysioNet CAP Sleep Database**.

This is intentionally a **small reproduction / benchmarking project**, not a clinical detector.

## Project goal

Build the smallest honest EMG-first baseline that can:
- load a tiny CAP subset with the positive class fixed at `brux1` and `brux2`
- add only bounded healthy controls that preserve the current dual-channel contract
- extract one jaw-muscle-aligned signal channel into fixed windows
- compute classical handcrafted features
- train simple models
- compare **leaky random window splits** vs **subject-aware splits**

## Why this project exists

The ai-lab research pass found that the easiest credible starting point is:
- one public dataset
- one channel family
- one binary task
- classical models
- subject-aware evaluation

CAP is not a purpose-built bruxism benchmark, but it is openly accessible and already used by recent bruxism papers. That makes it good enough for a first reproducible pilot.

A periodic translational literature check on `2026-05-05` did not overturn that framing. The newer science is more wearable-, multi-night-, and intervention-oriented, but it still does not expose a clearly better open benchmark than CAP. So the repo should stay EMG-first and validity-focused here, while treating portable/home/intervention EMG as a future branch rather than an immediate benchmark pivot.

## Scope for version 1

**Do now**
- reproduce a tiny EMG-first window-classification baseline
- keep the task binary: `bruxism` vs `control`
- keep the public positive class fixed at `brux1` and `brux2`
- treat `EMG1-EMG2` as the primary starting channel and `C4-P4` as the comparison channel
- expand controls only when they preserve the current dual-channel plus annotation-aware contract
- treat `LOSO` subject-level performance as the primary benchmark surface and keep random-window CV only as a leakage reference
- report balanced accuracy, sensitivity, specificity, and AUROC
- report raw subject counts plus exact `95%` binomial confidence intervals for subject-level sensitivity and specificity
- preserve lightweight subject-level calibration outputs in LOSO reports (`mean_positive_probability` per subject plus subject-level Brier score)
- keep one fixed primary subject threshold for the headline result and label any threshold sweep as exploratory only
- report the gap between random window CV and leave-one-subject-out CV

**Do not do yet**
- deep learning
- multimodal fusion
- clinical claims
- custom hardware collection

## Folder layout

- `data/README.md` — raw-data and manifest notes
- `data/subject_manifest.example.csv` — starter manifest format
- `notebooks/00_cap_subset_inspection.ipynb` — first inspection notebook stub
- `src/features.py` — handcrafted window features
- `src/prepare_windows.py` — EDF -> feature CSV pipeline
- `src/train_baseline.py` — baseline training with random vs LOSO CV
- `src/eval.py` — comparison helper for saved metric JSON files
- `reports/first-baseline.md` — experiment checklist / artifact template

## Environment

Bootstrap the repo if needed:

```bash
cd /home/hermes/work/ai-lab
./scripts/bootstrap-python.sh
source .venv/bin/activate
uv pip install -e '.[biosignals]'
```

The `biosignals` extra is intentionally optional so the main Unsloth/Modal workflow stays lightweight.

## Step 1: download a tiny CAP subset

```bash
cd /home/hermes/work/ai-lab
mkdir -p projects/bruxism-cap/data/raw/capslpdb
cd projects/bruxism-cap/data/raw/capslpdb

wget -nc https://physionet.org/files/capslpdb/1.0.0/brux1.edf
wget -nc https://physionet.org/files/capslpdb/1.0.0/brux2.edf
wget -nc https://physionet.org/files/capslpdb/1.0.0/n1.edf
wget -nc https://physionet.org/files/capslpdb/1.0.0/n2.edf
wget -nc https://physionet.org/files/capslpdb/1.0.0/n3.edf
wget -nc https://physionet.org/files/capslpdb/1.0.0/n5.edf
wget -nc https://physionet.org/files/capslpdb/1.0.0/n11.edf
```

These controls now follow the bounded control-side audit: keep `n3`, `n5`, and `n11` as the verified local core and treat `n1` plus `n2` as the next admissible dual-channel additions. Do not keep using the current local `n10` for stage-aware work unless you first refresh it from the canonical PhysioNet source and verify the full object size.

## Step 2: inspect channel names first

```bash
python3 projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --list-channels
```

The exact channel name may differ by record. For the current EMG-first pivot, start with `EMG1-EMG2` as the primary channel and use `C4-P4` as the main comparison channel when both are present.

## Step 3: build a feature CSV

Example for one record:

```bash
python3 projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --subject-id brux1 \
  --label bruxism \
  --channel EMG1-EMG2 \
  --window-seconds 30 \
  --limit-windows 120 \
  --out projects/bruxism-cap/data/window_features.csv
```

Append more records with `--append`:

```bash
python3 projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/n3.edf \
  --subject-id n3 \
  --label control \
  --channel EMG1-EMG2 \
  --window-seconds 30 \
  --limit-windows 120 \
  --append \
  --out projects/bruxism-cap/data/window_features.csv
```

## Step 4: train a baseline

Current tracked first-run artifacts in this repo:
- `projects/bruxism-cap/data/window_features_pass1.csv` — 3-subject pilot used to validate the pipeline
- `projects/bruxism-cap/data/window_features_pass2.csv` — first 6-subject feature table with `20` windows per subject from the first `600` seconds
- `projects/bruxism-cap/reports/random-window-cv-pass2.json` and `loso-cv-pass2.json` — first valid 6-subject baseline
- `projects/bruxism-cap/reports/random-window-cv-pass3-nosfreq.json` and `loso-cv-pass3-nosfreq.json` — same data after excluding obvious sampling-rate proxy features from training
- `projects/bruxism-cap/data/window_features_pass4_s2.csv` — first annotation-aware feature table using `SLEEP-S2` windows only on the stage-valid 5-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`)
- `projects/bruxism-cap/reports/random-window-cv-pass4-s2.json` and `loso-cv-pass4-s2.json` — pass4 rerun on the annotation-aware `S2` subset
- `projects/bruxism-cap/reports/annotation-alignment-audit-pass4-s2.md` — per-subject EDF versus sidecar audit explaining why `n10` was excluded and why `brux1` is only partially usable for `SLEEP-S2`
- `projects/bruxism-cap/reports/loso-cv-pass5-pass2-subjectagg.json` and `loso-cv-pass5-pass4-s2-subjectagg.json` — measurement-hardened LOSO reruns that preserve the original window metrics but also aggregate predictions to one verdict per held-out subject
- `projects/bruxism-cap/src/audit_subject_confound.py`, `projects/bruxism-cap/reports/subject-confound-audit-pass6.json`, and `subject-confound-audit-pass6.md` — a bounded pass6 audit checking whether the current feature tables separate windows more by subject or by label
- `projects/bruxism-cap/data/window_features_pass7_s2_mcap.csv`, `projects/bruxism-cap/reports/random-window-cv-pass7-s2-mcap.json`, `loso-cv-pass7-s2-mcap.json`, and `pass7-s2-mcap-overlap.md` — a pass7 rerun that keeps only `SLEEP-S2` windows overlapping CAP micro-events (`MCAP-A1`, `MCAP-A2`, `MCAP-A3`)
- `projects/bruxism-cap/src/audit_overlap_event_mix.py`, `projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.json`, and `overlap-event-mix-audit-pass8.md` — a bounded pass8 audit showing that the kept `S2+MCAP` subset mixes materially different CAP overlap-event families across subjects (for example `brux2` is mostly `A3` while `n5` is mostly `A1`)
- `projects/bruxism-cap/data/window_features_pass9_s2_mcap_a3.csv`, `projects/bruxism-cap/reports/random-window-cv-pass9-s2-mcap-a3.json`, `loso-cv-pass9-s2-mcap-a3.json`, and `pass9-s2-mcap-a3.md` — a pass9 rerun that narrows the overlap rule to `SLEEP-S2` windows with `MCAP-A3` overlap only
- `projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv`, `projects/bruxism-cap/reports/random-window-cv-pass10-s2-mcap-a3-only.json`, `loso-cv-pass10-s2-mcap-a3-only.json`, and `pass10-s2-mcap-a3-only.md` — a pass10 rerun that keeps only `SLEEP-S2` windows with `MCAP-A3` overlap and excludes simultaneous `MCAP-A1` / `MCAP-A2` overlap
- `projects/bruxism-cap/src/audit_rule_survival.py`, `projects/bruxism-cap/reports/rule-survival-audit-pass11.json`, and `projects/bruxism-cap/reports/pass11-rule-survival-audit.md` — a bounded pass11 validity audit showing how aggressively each overlap rule changes per-subject and per-label window availability before any model is rerun
- `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a1_only_matched14.csv`, `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a3_only_matched14.csv`, `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a1-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json`, `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a3-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a3-only-matched14.json`, and `projects/bruxism-cap/reports/pass12-exclusive-a1-vs-a3-matched14.md` — a pass12 matched-family comparison showing that exclusive `S2 + A1-only` transfers better than matched exclusive `S2 + A3-only`, but still misses one held-out bruxism subject
- `projects/bruxism-cap/data/window_features_pass13_emg_s2_mcap_a1_only_matched14.csv`, `projects/bruxism-cap/reports/random-window-cv-pass13-emg-s2-mcap-a1-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass13-emg-s2-mcap-a1-only-matched14.json`, and `projects/bruxism-cap/reports/pass13-emg-vs-c4-a1-only-matched14.md` — a pass13 matched channel comparison showing that the first `EMG1-EMG2` rerun on the strongest current `A1-only` scaffold regressed the honest baseline relative to `C4-P4`
- `projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv`, `projects/bruxism-cap/reports/random-window-cv-pass14-emg-s2-mcap-a3-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json`, and `projects/bruxism-cap/reports/pass14-emg-a1-vs-a3-matched14.md` — a pass14 matched EMG-family comparison showing that `A3-only` improves `EMG1-EMG2` relative to matched `A1-only` on window-level LOSO, but still leaves subject-level bruxism sensitivity at `0.000`
- `projects/bruxism-cap/src/audit_subject_thresholds.py`, `projects/bruxism-cap/reports/subject-threshold-audit-pass15-emg-a3-vs-c4-a1.json`, and `projects/bruxism-cap/reports/pass15-emg-a3-threshold-audit.md` — a pass15 threshold audit showing that the stronger `EMG1-EMG2 A3-only` run fails because two controls still outrank the best bruxism subject, so threshold tuning alone cannot rescue the honest baseline
- `projects/bruxism-cap/src/audit_emg_feature_validity.py`, `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.json`, and `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.md` — a pass16 EMG-first validity audit showing that the same `A3-only` ranking failure is being driven by a recurring high-score-control feature family (`ratio_alpha_delta`, `min`, `sample_entropy`) while `brux1` is dominated by extreme absolute-power / mean terms, narrowing the next patch to one small EMG feature ablation
- `projects/bruxism-cap/reports/random-window-cv-pass17-emg-a3-timeonly-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass17-emg-a3-timeonly-matched14.json`, and `projects/bruxism-cap/reports/pass17-emg-a3-timeonly-ablation.md` — a pass17 matched time-domain ablation showing that simply dropping the spectral / ratio family does not rescue the honest EMG-first baseline and slightly worsens the best LOSO window-level result
- `projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv`, `projects/bruxism-cap/reports/random-window-cv-pass18-emg-a3-envelope-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass18-emg-a3-envelope-matched14.json`, `projects/bruxism-cap/reports/pass18-emg-a3-envelope-replacement.md`, and `projects/bruxism-cap/reports/feature-validity-audit-pass18-emg-a3-envelope-logreg.md` — a pass18 replacement-oriented EMG rerun showing that adding one compact rectified-envelope / burst family slightly reshapes subject scores but still does not rescue the honest EMG-first baseline or beat the stronger pass14 window-level LOSO result
- `projects/bruxism-cap/reports/random-window-cv-pass19-emg-a3-envelope-selected-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json`, and `projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md` — a pass19 selection-aware EMG rerun showing that the pass18 envelope / burst family works better when spectral / ratio features are excluded at train time, but still does not rescue the honest subject-level baseline
- `projects/bruxism-cap/reports/random-window-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`, and `projects/bruxism-cap/reports/pass20-emg-a3-envelope-selected-nomean-matched14.md` — a pass20 mean-ablation rerun showing that once the spectral / ratio family is already excluded, naive raw-`mean` removal makes `brux1` much worse without lowering the two highest-score controls
- `projects/bruxism-cap/src/audit_emg_envelope_family.py`, `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.json`, and `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.md` — a pass21 retained-family audit showing that the pass19 envelope / burst working point is real but still not cleanly bruxism-aligned: `sample_entropy` and `burst_fraction` still lift controls while `rectified_mean`, `envelope_mean`, and `p95_abs` remain net-negative on `brux1`
- `projects/bruxism-cap/data/window_features_pass22_emg_s2_mcap_a3_only_matched14_medianmad.csv`, `projects/bruxism-cap/reports/random-window-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`, and `projects/bruxism-cap/reports/pass22-emg-a3-envelope-selected-medianmad-matched14.md` — a pass22 normalization-aware EMG rerun showing that robust per-window `median_mad` normalization makes the stronger pass19 EMG working point worse rather than better: the best LOSO window-level result regresses and both bruxism subjects rank even lower
- `projects/bruxism-cap/src/compare_subject_score_surfaces.py`, `projects/bruxism-cap/reports/subject-score-comparison-pass23-emg-pass19-vs-c4-pass12.json`, and `projects/bruxism-cap/reports/pass23-emg-pass19-vs-c4-pass12-subject-score-comparison.md` — a pass23 benchmark-clarity comparison showing that the stronger pass19 EMG working point improves `brux1` versus the honest pass12 `C4-P4 A1-only` anchor but still loses decisively overall because `brux2` collapses and `n3` becomes the highest-score control
- `projects/bruxism-cap/src/audit_emg_brux2_n3_gap.py`, `projects/bruxism-cap/reports/feature-validity-audit-pass24-emg-brux2-vs-n3.json`, and `feature-validity-audit-pass24-emg-brux2-vs-n3.md` — a pass24 focused EMG validity audit showing that the strongest remaining failure is the `brux2`-below-`n3` reversal, with `zero_crossing_rate` as the largest surviving control-favoring feature gap and unmatched time position as the next extraction-validity question
- `projects/bruxism-cap/src/select_time_position_matched_windows.py`, `projects/bruxism-cap/data/window_features_pass25_emg_s2_mcap_a3_only_full_envelope.csv`, `projects/bruxism-cap/data/window_features_pass25_emg_s2_mcap_a3_only_timepos10_envelope.csv`, `projects/bruxism-cap/reports/time-position-match-pass25-emg-a3.json`, `projects/bruxism-cap/reports/random-window-cv-pass25-emg-a3-timepos10-selected.json`, `projects/bruxism-cap/reports/loso-cv-pass25-emg-a3-timepos10-selected.json`, and `projects/bruxism-cap/reports/pass25-emg-a3-time-position-matched-selected.md` — a pass25 shared-time-position rerun showing that absolute time-position matching is only feasible at `10` windows per subject on the current verified subset, improves both bruxism subjects relative to pass19, but still leaves all controls above both bruxism subjects and does not beat the honest EMG baseline
- `projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_full_envelope.csv`, `projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_timepos10_envelope.csv`, `projects/bruxism-cap/reports/time-position-match-pass26-c4-a3.json`, `projects/bruxism-cap/reports/random-window-cv-pass26-c4-a3-timepos10-selected.json`, `projects/bruxism-cap/reports/loso-cv-pass26-c4-a3-timepos10-selected.json`, and `projects/bruxism-cap/reports/pass26-c4-a3-time-position-matched-vs-emg.md` — a pass26 matched strict-scaffold comparison showing that rebuilding the exact same shared-time-position `A3-only` subset on `C4-P4` does not rescue the benchmark and actually underperforms matched `EMG1-EMG2` on the honest LOSO surface
- `projects/bruxism-cap/data/window_features_pass27_emg_s2_mcap_a1_only_full_envelope.csv`, `projects/bruxism-cap/data/window_features_pass27_emg_s2_mcap_a1_only_timepos2_envelope.csv`, `projects/bruxism-cap/reports/time-position-match-pass27-emg-a1.json`, and `projects/bruxism-cap/reports/pass27-emg-a1-time-position-feasibility.md` — a pass27 extraction-validity audit showing that the same strict shared-time-position rule collapses `EMG1-EMG2 A1-only` to only `2` windows per subject, so the next timing-aware rerun needs a softer selector before another LOSO benchmark is trusted
- `projects/bruxism-cap/src/select_time_position_matched_windows.py`, `projects/bruxism-cap/src/train_baseline.py`, `projects/bruxism-cap/data/window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`, `projects/bruxism-cap/reports/time-position-match-pass28-emg-a1-pct10-90.json`, `projects/bruxism-cap/reports/random-window-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`, `projects/bruxism-cap/reports/loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`, and `projects/bruxism-cap/reports/pass28-emg-a1-percentile-band-rerun.md` — a pass28 softer-timing-control rerun showing that a percentile-band selector restores a usable `EMG1-EMG2 A1-only` scaffold (`10` windows per subject instead of `2`) but still leaves honest LOSO subject-level sensitivity at `0.000`
- `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_full_envelope.csv`, `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`, `projects/bruxism-cap/reports/time-position-match-pass29-c4-a1-pct10-90.json`, `projects/bruxism-cap/reports/random-window-cv-pass29-c4-a1-pct10-90-timepos10-selected.json`, `projects/bruxism-cap/reports/loso-cv-pass29-c4-a1-pct10-90-timepos10-selected.json`, and `projects/bruxism-cap/reports/pass29-c4-a1-percentile-band-vs-emg.md` — a pass29 matched-channel comparison showing that rebuilding the exact same repaired `A1-only` percentile-band scaffold on `C4-P4` clearly beats matched `EMG1-EMG2` on honest LOSO, but still only ties the older best subject-level baseline because `brux1` remains below `n3`
- `projects/bruxism-cap/src/audit_percentile_band_channel_gap.py`, `projects/bruxism-cap/reports/feature-validity-audit-pass30-a1-pct-channel-gap.json`, and `projects/bruxism-cap/reports/pass30-a1-percentile-band-channel-gap-audit.md` — a pass30 cross-channel validity audit showing that the repaired `A1-only` percentile-band scaffold is truly timing-matched across `EMG1-EMG2` and `C4-P4`, that `brux1` still trails `n3` under both channels, and that the main channel gap is now `brux2`: `C4-P4` flips `brux2` strongly above `n3` while EMG leaves it far below
- `projects/bruxism-cap/src/audit_percentile_band_n3_family_recurrence.py`, `projects/bruxism-cap/reports/feature-validity-audit-pass31-a1-pct-n3-family.json`, and `projects/bruxism-cap/reports/pass31-a1-percentile-band-n3-family-recurrence.md` — a pass31 recurrence audit showing that the suspected narrow `n3`-favoring trio (`sample_entropy`, `burst_fraction`, `envelope_cv`) is real but not sufficient: on the repaired scaffold, the harsher EMG `n3` advantage is still driven mainly by broader morphology terms such as `mean`, `max`, `ptp`, and `zero_crossing_rate`, so a trio-only ablation would be under-justified
- `projects/bruxism-cap/src/run_pass32_broad_morphology_ablation.py`, `projects/bruxism-cap/reports/loso-cv-pass32-emg-a1-pct10-90-broad-ablation.json`, `projects/bruxism-cap/reports/loso-cv-pass32-c4-a1-pct10-90-broad-ablation.json`, and `projects/bruxism-cap/reports/pass32-broad-morphology-ablation.md` — a pass32 matched broader-ablation rerun showing that removing the wider control-favoring morphology family is too destructive: `EMG1-EMG2` still misses both bruxism subjects while `C4-P4` loses its earlier `brux2` recovery, so the result should be preserved as a negative ablation rather than promoted as a new baseline
- `projects/bruxism-cap/src/run_pass33_raw_location_ablation.py`, `projects/bruxism-cap/reports/loso-cv-pass33-emg-a1-pct10-90-rawloc-ablation.json`, `projects/bruxism-cap/reports/loso-cv-pass33-c4-a1-pct10-90-rawloc-ablation.json`, and `projects/bruxism-cap/reports/pass33-raw-location-ablation.md` — a pass33 smaller raw-location ablation showing that removing only `mean`, `min`, and `max` is not the fix either: `C4-P4` stays essentially unchanged, but `EMG1-EMG2` gets markedly worse because `brux1` collapses while `n3` stays high
- `projects/bruxism-cap/src/run_pass34_record_relative_emg_audit.py`, `projects/bruxism-cap/data/window_features_pass34_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative.csv`, `projects/bruxism-cap/reports/loso-cv-pass34-emg-a1-pct10-90-record-relative.json`, and `projects/bruxism-cap/reports/pass34-record-relative-emg-audit.md` — a pass34 record-relative representation audit showing that within-record robust feature scaling removes the `n3` false positive and flips `brux2 - n3` positive, but still leaves `brux1` below threshold so subject-level sensitivity remains `0.000`
- `projects/bruxism-cap/src/features.py`, `projects/bruxism-cap/src/run_pass35_shape_feature_expansion.py`, `projects/bruxism-cap/data/window_features_pass35_emg_s2_mcap_a1_only_full_envelope_shape.csv`, `projects/bruxism-cap/data/window_features_pass35_emg_s2_mcap_a1_only_pct10_90_timepos10_shape.csv`, `projects/bruxism-cap/reports/time-position-match-pass35-emg-a1-pct10-90-shape.json`, `projects/bruxism-cap/reports/loso-cv-pass35-emg-a1-pct10-90-shape.json`, and `projects/bruxism-cap/reports/pass35-shape-feature-expansion.md` — a pass35 compact shape-feature expansion showing that the repaired scaffold can be rebuilt exactly with four new shape descriptors, sharply reducing both the `n3 - brux1` and `brux2 - n3` gaps, but still not enough to push either bruxism subject above threshold at the subject level
- `projects/bruxism-cap/src/run_pass36_record_relative_shape_composition_audit.py`, `projects/bruxism-cap/data/window_features_pass36_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape.csv`, `projects/bruxism-cap/reports/loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json`, and `projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit.md` — a pass36 composition audit showing that the pass34 record-relative and pass35 compact-shape gains do compose honestly on the repaired scaffold, lifting subject-level balanced accuracy to `0.750` and sensitivity to `0.500` via a strong `brux2` recovery, but still leaving `brux1` below threshold

Leakage-prone reference split:

```bash
python3 projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features.csv \
  --cv random \
  --out projects/bruxism-cap/reports/random-window-cv.json
```

Subject-aware split:

```bash
python3 projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features.csv \
  --cv loso \
  --out projects/bruxism-cap/reports/loso-cv.json
```

Compare the two:

```bash
python3 projects/bruxism-cap/src/eval.py \
  projects/bruxism-cap/reports/random-window-cv.json \
  projects/bruxism-cap/reports/loso-cv.json
```

For LOSO reports, the saved JSON keeps the original window-level summaries and also stores a `subject_aggregation` block per model. That block now includes per-subject mean positive probabilities (`mean_positive_probability`), exact and Wilson `95%` intervals for subject-level sensitivity / specificity, and a lightweight subject-level Brier score.

## Success criterion for the first pass

A successful first pass is **not** “95% accuracy.”

It is:
- a reproducible raw-data subset
- a feature CSV that can be regenerated
- one honest baseline report
- a clear comparison between leaky and subject-aware evaluation

## Current status after the first runs

The first real runs now exist and they should be read as a measurement lesson, not a success claim:
- random-window CV stayed extremely high even after removing an obvious sampling-rate proxy feature
- a first annotation-aware rerun on `SLEEP-S2` windows (`pass4`) still kept random CV unrealistically perfect while LOSO regressed further
- `n10` could not be kept in the stage-aware subset because its local EDF is only about `63` minutes long while the sidecar scoring file continues far beyond the available signal, leaving no in-range `SLEEP-S2` windows
- a follow-up alignment audit showed that `brux1` is only partially usable for `SLEEP-S2` locally because many later scored stage rows also exceed the EDF duration
- a follow-up subject-level LOSO aggregation pass (`pass5`) showed that the weak window-level bruxism sensitivity was still flattering the situation: at the subject verdict level, every tested model predicted **zero** held-out bruxism subjects correctly on both the pass3 and pass4 datasets
- a bounded subject-versus-label confound audit (`pass6`) showed that the current handcrafted feature tables are actually **more separable by label than by subject within random window splits**, so the next bottleneck is not just trivial subject-ID clustering; it is a label boundary that does not survive held-out-subject transfer
- a follow-up overlap-event mix audit (`pass8`) showed that the current `S2+MCAP` subset itself is heterogeneous: some subjects are dominated by `MCAP-A3` overlap while others are dominated by `MCAP-A1`, so the next extraction test should be a narrower single-family overlap rule rather than another mixed-event bucket
- a new single-family rerun (`pass9`) narrowed the overlap rule to `MCAP-A3`, which reduced random-window CV from perfect to about `0.921` balanced accuracy but still failed to improve honest transfer: the best LOSO balanced accuracy fell to `0.550` and subject-level bruxism sensitivity stayed `0.000`
- a stricter exclusive-`A3` rerun (`pass10`) then excluded simultaneous `MCAP-A1` / `MCAP-A2` overlap from the kept `SLEEP-S2` windows, making the extraction rule more auditable but not more transferable: random-window balanced accuracy fell slightly further to about `0.908`, the best LOSO balanced accuracy fell again to `0.500`, and subject-level bruxism sensitivity still stayed `0.000`
- a bounded rule-survival audit (`pass11`) then showed why these overlap-filter comparisons need explicit bookkeeping: the bruxism pool keeps `32.1%` of its pass4 `S2` windows under the exclusive-`A3` rule, while the control pool keeps only `15.2%`; `brux2` alone still has `111` eligible exclusive-`A3` windows, but `n5` falls to only `38`
- a matched-family comparison (`pass12`) then showed that the overlap-family choice itself matters under fairer conditions: when both exclusive families are capped to the same `14` windows per subject on the same 5-subject subset, `A1-only` reaches subject-level LOSO balanced accuracy `0.750` with sensitivity `0.500`, while matched `A3-only` still stays at `0.000` subject-level bruxism sensitivity across models
- a first matched EMG-versus-C4 comparison (`pass13`) then tested the new EMG-first framing on that same `A1-only` scaffold and preserved a negative result: `EMG1-EMG2` fell back to LOSO balanced accuracy `0.543` with subject-level sensitivity `0.000`, so it did not beat the current matched `C4-P4` anchor and missed both held-out bruxism subjects
- a matched EMG-family comparison (`pass14`) then tested whether EMG prefers a different overlap family on the same scaffold: exclusive `A3-only` improved EMG LOSO balanced accuracy to `0.629` and reduced several control mean scores, but subject-level sensitivity still stayed `0.000`, so the result is still a validity note rather than a new honest baseline
- a compact threshold audit (`pass15`) then showed that the stronger `EMG1-EMG2 A3-only` run cannot be rescued by lowering the subject threshold alone: two controls still outrank the best bruxism subject, so the next bottleneck is score ordering / feature validity rather than threshold choice
- a compact feature-validity audit (`pass16`) then localized that EMG score-ordering failure more tightly: `n3` and `n5` still outrank `brux1`, the same high-score controls repeatedly surface `ratio_alpha_delta`, `min`, and `sample_entropy` as positive contributors, and `brux1` is dominated by extreme absolute-power / mean terms

So the next correct step is still to improve extraction / evaluation validity before trying larger models or modality fusion, but the repo now has a sharper lesson than before: generic in-dataset label separation is easy, cross-subject transfer is the real failure surface, and overlap-family choice matters under matched conditions. Exclusive `A1-only` currently looks more transferable than exclusive `A3-only` for `C4-P4`, while `EMG1-EMG2` looks less bad under exclusive `A3-only` than under exclusive `A1-only`. The threshold audit then showed that no subject threshold rescues the stronger EMG run without collapsing specificity, because two controls still outrank the best bruxism subject. The new feature-validity audit narrowed the next move one step further: on the fixed pass14 scaffold, the high-score controls repeatedly benefit from `ratio_alpha_delta`, `min`, and `sample_entropy`, while `brux1` is dragged by extreme absolute-power / mean terms. The new pass17 time-domain ablation then preserved an equally important negative result: simply deleting the spectral / ratio family is not enough, because honest subject-level sensitivity still stays `0.000`, the best LOSO window-level result regresses slightly, and `n3` becomes even harder to separate. Pass18 then tested the complementary replacement idea and preserved the same overall verdict: adding one compact rectified-envelope / burst family slightly improves `brux1` and `brux2` versus pass17 and lowers `n3`, but it still leaves `n5` above `brux1`, keeps subject-level sensitivity at `0.000`, and still trails the stronger pass14 EMG LOSO result. Pass19 refined that one step further: the pass18 EMG family works better when the older spectral / ratio family is excluded at train time, recovering LOSO balanced accuracy `0.629`, but the honest subject-level verdict still stays flat at `0.000` sensitivity because `n3` and `n5` still outrank `brux1`. The next bounded move should therefore keep the selection-aware EMG recipe fixed and audit one remaining score-ordering driver such as `mean`, rather than broadening features or models again.

## Annotation-aware extraction example

To build stage-aware windows from RemLogic sidecar exports, point `prepare_windows.py` at the matching `.txt` file and select the sleep event to keep:

```bash
python3 projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --annotation-txt projects/bruxism-cap/data/raw/capslpdb/brux1.txt \
  --annotation-events SLEEP-S2 \
  --subject-id brux1 \
  --label bruxism \
  --channel EMG1-EMG2 \
  --window-seconds 30 \
  --limit-windows 20 \
  --out projects/bruxism-cap/data/window_features_pass4_s2.csv
```

## Where to extend next

After this scaffold works, the next sensible directions are:
1. keep future stage-aware reruns restricted to subjects whose chosen events are verified in-range by the audit
2. preserve the new rule-survival audit when reading pass7/pass9/pass10 so event-family comparisons are not mistaken for like-for-like sampling changes
3. audit why `brux1` still fails under the stronger matched `S2 + A1-only` rule and whether the apparent gain over `A3-only` is threshold-fragile or reflects a broader ranking improvement
4. preserve the matched-family comparison alongside the new threshold audit before testing any new overlap family
5. preserve the new pass19 selection-aware EMG rerun as the stronger current EMG-first working point
6. preserve the new pass20 mean-ablation rerun as evidence that naive raw-`mean` removal makes `brux1` much worse without lowering `n3` or `n5`
7. preserve the new pass21 retained-family audit as evidence that the next EMG-only move should be normalization-aware extraction rather than more blind feature deletion
8. preserve the new pass22 normalization-aware rerun as evidence that simple per-window `median_mad` normalization is **not** that fix: it makes the stronger pass19 EMG working point worse and pushes both bruxism subjects lower
9. preserve the new pass23 shared subject-score comparison as evidence that the current EMG gap is now concentrated in `brux2` collapse plus `n3` as the dominant control, not in a vague overall underperformance story
10. preserve the new pass24 focused gap audit as evidence that the current EMG failure is now localized to a `brux2`-below-`n3` reversal, with `zero_crossing_rate` as the largest surviving control-favoring gap on the fixed pass19 scaffold
11. preserve the new pass25 shared-time-position rerun as evidence that the timing concern was real but not sufficient: both bruxism subjects rise, yet all controls still outrank them on the honest LOSO subject surface
12. preserve the new pass26 matched strict-scaffold comparison as evidence that `C4-P4` does **not** rescue the stricter `A3-only` benchmark and that the timing-matched scaffold itself is now the bigger bottleneck than channel choice alone
13. preserve the new pass27 feasibility audit as evidence that the current hard shared-interval selector collapses `EMG1-EMG2 A1-only` to only `2` windows per subject, so extraction validity blocks a meaningful rerun before modeling begins
14. preserve the new pass28 percentile-band rerun as evidence that softer timing control fixes the extraction-collapse problem (`10` windows per subject again) but still does not rescue honest subject transfer on `EMG1-EMG2 A1-only`
15. preserve the new pass29 matched percentile-band comparison as evidence that channel choice still matters on the repaired `A1-only` scaffold: `C4-P4` recovers `brux2` cleanly, but `brux1` still trails `n3`
16. preserve the new pass30 cross-channel gap audit as evidence that the scaffold itself is now matched and the remaining honest failure is a narrower subject/control overlap problem rather than a timing-selection problem
17. preserve the new pass31 recurrence audit as evidence that the suspected narrow `n3`-favoring trio is not the whole story on the repaired scaffold: `burst_fraction` recurs, but the strongest EMG control-favoring gap is still broader (`mean`, `max`, `ptp`, `zero_crossing_rate`), so a trio-only ablation would have been under-justified
18. preserve the new pass32 broader morphology ablation as evidence that wholesale deletion is also not the fix: `EMG1-EMG2` still misses both bruxism subjects, `n3` stays above `brux1`, and `C4-P4` loses its earlier `brux2` recovery
19. preserve the new pass33 smaller raw-location ablation as evidence that a narrower deletion is not the fix either: removing only `mean`, `min`, and `max` leaves `C4-P4` essentially unchanged but makes `EMG1-EMG2` worse by collapsing `brux1` while `n3` stays high
20. preserve the new pass34 record-relative audit as evidence that one representation change can fix the worst `brux2` versus `n3` reversal without fixing the harder `brux1` bottleneck
21. preserve the new pass35 shape-feature expansion as evidence that compact waveform-shape descriptors also improve the repaired scaffold's control/bruxism margins, but still do not clear the honest subject-level sensitivity bar
22. preserve the new pass36 composition audit as evidence that the two best EMG representation clues do compose honestly on the repaired scaffold, recovering `brux2` and matching the stronger subject-level metric surface, but still leaving `brux1` as the remaining bottleneck
23. next, keep the repaired five-subject scaffold fixed and localize the remaining `brux1` failure before any channel pivot, broad feature stack, or neural-model branch
24. only after that consider REM-only filtering, channel fusion, or a small neural baseline
