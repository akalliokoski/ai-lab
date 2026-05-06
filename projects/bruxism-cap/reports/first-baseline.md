# First bruxism-cap baseline report

Date: 2026-05-03
Status: first real baseline runs completed; current result is a strong leakage warning, not a credible detector

## Goal

Produce the first honest CAP-based bruxism baseline with both:
- random window cross-validation
- leave-one-subject-out cross-validation

Then document what failed, what was fixed, and what the next bounded step should be.

## Pre-run checklist

- [x] Raw EDF subset downloaded under `projects/bruxism-cap/data/raw/capslpdb/`
- [x] Chosen channel exists for all included subjects
- [x] Feature CSV regenerated from raw data
- [x] Class balance checked
- [x] Subject counts checked
- [x] Random-window CV result saved
- [x] LOSO CV result saved
- [x] Gap between the two documented
- [x] First measurement fix from the autoresearch pass tested
- [x] First annotation-aware rerun tested and documented

## Dataset used for the first real runs

- Subjects: `brux1`, `brux2`, `n3`, `n5`, `n10`, `n11`
- Labels: `2` bruxism subjects, `4` control subjects
- Channel: `C4-P4` for the original baseline history; `EMG1-EMG2` is now the primary next-pass channel
- Window seconds: `30`
- Window count per subject: `20`
- Total windows: `120`
- Time slice: first `600` seconds of each record (current known weakness)
- Feature CSV: `projects/bruxism-cap/data/window_features_pass2.csv`

## Run history

### Pass 1 — tiny pilot / pipeline shakeout
- Subjects: `brux1`, `brux2`, `n10`
- Feature CSV: `projects/bruxism-cap/data/window_features_pass1.csv`
- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass1.json`
- Outcome:
  - random-window CV looked unrealistically perfect or near-perfect
  - LOSO was not valid yet because the lone control fold left the training split with only bruxism examples
- Value of this pass:
  - proved the extraction + baseline path worked end to end
  - exposed the need for more controls before claiming any subject-aware result

### Pass 2 — first valid 6-subject baseline
- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass2.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass2.json`
- Best random-window result:
  - logistic regression balanced accuracy / sensitivity / specificity / AUROC:
    `1.000 / 1.000 / 1.000 / 1.000`
- Best LOSO result:
  - SVM balanced accuracy / sensitivity / specificity / AUROC:
    `0.783 / 0.167 / 0.617 / n/a`
- Interpretation:
  - adding controls made LOSO runnable, but the leakage gap remained huge
  - held-out bruxism sensitivity was still very poor

### Pass 3 — first autoresearch-motivated measurement fix
- Change tested:
  - excluded `n_samples` and `duration_s` from model features in `src/train_baseline.py`
  - reason: `n_samples` was directly encoding sampling-rate differences across subjects, especially `brux2` (`256 Hz`) versus the `512 Hz` records
- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass3-nosfreq.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass3-nosfreq.json`
- Best random-window result:
  - logistic regression balanced accuracy / sensitivity / specificity / AUROC:
    `0.963 / 0.950 / 0.975 / 0.996875`
- Best LOSO result:
  - SVM balanced accuracy / sensitivity / specificity / AUROC:
    `0.733 / 0.117 / 0.617 / n/a`
- Interpretation:
  - removing the obvious sampling-rate proxy reduced the random-window score slightly
  - it did not solve the real problem: LOSO still generalizes poorly to held-out bruxism subjects

### Pass 4 — first annotation-aware rerun on sleep-stage windows
- Change tested:
  - patched `src/prepare_windows.py` to accept RemLogic `.txt` sidecars and select windows by scored events such as `SLEEP-S2`
  - downloaded local annotation sidecars `brux1.txt`, `brux2.txt`, `n3.txt`, `n5.txt`, `n10.txt`, `n11.txt`
  - built a stage-aware CSV using the first `20` in-range `SLEEP-S2` windows for each usable subject
- Important scope note:
  - `n10` could not be included because its local EDF is only about `3783` seconds long while its scoring file continues far beyond the available signal, leaving `0` in-range `SLEEP-S2` windows
  - `brux1` also has many late scoring entries beyond the available EDF duration, but it still has enough in-range `SLEEP-S2` windows for this bounded test
- Feature CSV: `projects/bruxism-cap/data/window_features_pass4_s2.csv`
- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass4-s2.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass4-s2.json`
- Dataset used:
  - subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
  - labels: `2` bruxism subjects, `3` control subjects
  - channel: `C4-P4` in the original stage-aware history; `EMG1-EMG2` is now the primary next-pass channel
  - windows: `20` per subject, all tagged `SLEEP-S2`
- Best random-window result:
  - logistic regression balanced accuracy / sensitivity / specificity / AUROC:
    `1.000 / 1.000 / 1.000 / 1.000`
- Best LOSO result:
  - SVM balanced accuracy / sensitivity / specificity / AUROC:
    `0.600 / 0.030 / 0.570 / n/a`
- Interpretation:
  - annotation-aware extraction is now reproducible in the repo, which is a real infrastructure improvement
  - the result is still a negative one scientifically: stage-matching alone did not reduce the leakage gap and in this small subset it made honest held-out performance even worse
  - this strongly suggests the remaining problem is not just “first 10 minutes” slicing; it is deeper subject/background separability plus tiny-subject instability and possibly record/annotation mismatches

### Pass 5 — subject-level LOSO aggregation hardening
- Change tested:
  - patched `src/train_baseline.py` so evaluation reports now preserve the original window-level metrics and also add a `subject_aggregation` block that collapses each held-out subject to one verdict using the mean positive score across that subject's windows
  - reran LOSO on the pass3 and pass4 feature tables into `loso-cv-pass5-pass2-subjectagg.json` and `loso-cv-pass5-pass4-s2-subjectagg.json`
- Why this matters:
  - the earlier LOSO summaries could look slightly less bad because a held-out bruxism subject might get a few positive windows without ever crossing a subject-level positive verdict
  - for this project, subject-level detection is the more honest reading of whether a held-out person is actually being recognized
- Key subject-level results:
  - pass3 best window-level LOSO model remained SVM at `0.733` balanced accuracy and `0.117` window sensitivity, but its subject-level summary fell to `0.375` balanced accuracy with `0.000` subject sensitivity and `0.750` subject specificity
  - pass4 best window-level LOSO model remained SVM at `0.600` balanced accuracy and `0.030` window sensitivity, while subject-level aggregation was `0.500` balanced accuracy with `0.000` subject sensitivity and `1.000` subject specificity
- Interpretation:
  - none of the current models actually identifies a held-out bruxism subject at the subject verdict level on either pass3 or pass4
  - the earlier small window-level true-positive counts were therefore not a meaningful sign of subject recognition

### Pass 6 — subject-versus-label confound audit
- Change tested:
  - added `src/audit_subject_confound.py` to compare the current pass3/pass4 feature tables on a bounded unsupervised/semi-supervised audit surface
  - saved artifacts to `projects/bruxism-cap/reports/subject-confound-audit-pass6.json` and `projects/bruxism-cap/reports/subject-confound-audit-pass6.md`
- Why this matters:
  - the repo had already shown a large random-vs-LOSO gap, but the next bottleneck was still ambiguous: are the handcrafted features mostly clustering by person, or do they separate the current labels inside the seen-subject pool while failing to transfer?
  - this audit checks that directly with subject-vs-label silhouette scores, nearest-neighbor agreement, and a random-window 1-NN probe
- Key results:
  - pass3 (`window_features_pass2.csv`) showed stronger label than subject separation: silhouette `0.364` for label vs `0.195` for subject, nearest-neighbor same-label rate `0.967` vs same-subject rate `0.817`, and random-window 1-NN label accuracy `0.958` vs subject-ID accuracy `0.800`
  - pass4 (`window_features_pass4_s2.csv`) showed the same pattern after annotation-aware `SLEEP-S2` extraction: silhouette `0.327` for label vs `0.147` for subject, nearest-neighbor same-label rate `1.000` vs same-subject rate `0.830`, and random-window 1-NN label accuracy `1.000` vs subject-ID accuracy `0.810`
- Interpretation:
  - this does **not** support the narrow story that random-window optimism is mainly coming from trivial subject-ID recovery inside the current feature space
  - instead, the data now point to a different bottleneck: the current windows contain an easy label-separation pattern inside the seen-subject pool, but that pattern is not stable enough to survive held-out-subject transfer
  - annotation-aware `SLEEP-S2` filtering alone did not make the class boundary more transferable

### Pass 7 — SLEEP-S2 plus CAP micro-event overlap
- Change tested:
  - patched `src/prepare_windows.py` with `--require-overlap-events` and `--min-overlap-seconds`
  - rebuilt the annotation-aware feature table so every kept `SLEEP-S2` window also overlaps at least one `MCAP-A1`, `MCAP-A2`, or `MCAP-A3` row
  - saved the new artifacts to `projects/bruxism-cap/data/window_features_pass7_s2_mcap.csv`, `projects/bruxism-cap/reports/random-window-cv-pass7-s2-mcap.json`, `projects/bruxism-cap/reports/loso-cv-pass7-s2-mcap.json`, and `projects/bruxism-cap/reports/pass7-s2-mcap-overlap.md`
- Important scope note:
  - `n10` is still excluded because the local EDF still has `0` in-range `SLEEP-S2` windows, so it also has `0` usable `S2+MCAP` windows
  - the other five subjects all had more than `20` eligible overlap windows, so the bounded rerun kept the same `5`-subject / `20`-windows-per-subject shape as pass4
- Best random-window result:
  - logistic regression balanced accuracy / sensitivity / specificity / AUROC:
    `1.000 / 1.000 / 1.000 / 1.000`
- Best LOSO result:
  - logistic regression balanced accuracy / sensitivity / specificity / AUROC:
    `0.590 / 0.000 / 0.590 / n/a`
- Subject-level result:
  - all three models stayed at subject balanced accuracy `0.500` with subject sensitivity `0.000` and subject specificity `1.000`
- Interpretation:
  - this tighter event-aware extraction rule is a useful infrastructure addition and a useful negative result, but not a performance improvement
  - random-window CV remained effectively perfect while held-out bruxism detection regressed to zero sensitivity even at the window level
  - the failure surface is therefore now tighter again: simple stage restriction plus CAP micro-event overlap is still not enough to produce a transferable cross-subject boundary

### Pass 8 — overlap event mix audit for the kept S2+MCAP subset
- Change tested:
  - added `src/audit_overlap_event_mix.py` to audit which CAP micro-event overlap families (`MCAP-A1`, `MCAP-A2`, `MCAP-A3`) dominate the pass7 subset, both before the `20`-window cap and inside the final kept windows
  - saved artifacts to `projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.json` and `projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.md`
- Why this matters:
  - pass7 proved that the mixed `S2+MCAP` bucket did not transfer better, but it still left an ambiguity: are all subjects contributing roughly the same CAP overlap-event regime, or is the kept subset itself heterogeneous in a way that makes the next extraction variant hard to interpret?
- Key results:
  - `brux2` kept windows were overwhelmingly `MCAP-A3`-overlap (`19/20` with `A3`), while `n5` kept windows were mostly `MCAP-A1`-overlap (`16/20` with `A1`)
  - that imbalance already existed in the full eligible pools, not only in the first-`20` cap: `brux2` had `111/181` eligible windows with `MCAP-A3` only, while `n5` had `134/194` eligible windows with `MCAP-A1` only
  - at the label level, the eligible bruxism pool was `A3`-dominated (`142/258` `A3`-only windows), while the eligible control pool was `A1`-dominated (`177/456` `A1`-only windows)
- Interpretation:
  - the pass7 negative result is now easier to read: the current mixed-event `S2+MCAP` subset is not one homogeneous physiological bucket
  - a narrower single-family overlap extraction rule is a better next step than another broad mixed-event rerun

### Pass 9 — narrower single-family `S2 + MCAP-A3` rerun
- Change tested:
  - rebuilt the stage-aware subset so every kept window had to be in-range `SLEEP-S2` and overlap `MCAP-A3`
  - saved artifacts to `projects/bruxism-cap/data/window_features_pass9_s2_mcap_a3.csv`, `projects/bruxism-cap/reports/random-window-cv-pass9-s2-mcap-a3.json`, `projects/bruxism-cap/reports/loso-cv-pass9-s2-mcap-a3.json`, and `projects/bruxism-cap/reports/pass9-s2-mcap-a3.md`
- Dataset used:
  - subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
  - labels: `2` bruxism subjects, `3` control subjects
  - windows: `20` per subject, all tagged `SLEEP-S2` with `MCAP-A3` overlap
- Best random-window result:
  - logistic regression balanced accuracy / sensitivity / specificity / AUROC:
    `0.921 / 0.875 / 0.967 / 0.950`
- Best LOSO result:
  - random forest balanced accuracy / sensitivity / specificity / AUROC:
    `0.550 / 0.010 / 0.540 / n/a`
- Subject-level result:
  - all three models again stayed at subject balanced accuracy `0.500` with subject sensitivity `0.000` and subject specificity `1.000`
- Interpretation:
  - narrowing from the mixed `S2+MCAP` bucket to `S2+A3` reduced random-split optimism, which is directionally useful
  - but honest held-out transfer still did not improve, so the pass7 failure was not simply caused by mixing `A1`, `A2`, and `A3` together
  - the next extraction test should become more auditable still, for example by making the overlap rule exclusive (`A3` without simultaneous `A1/A2`) rather than only requiring `A3` presence

### Pass 10 — exclusive `S2 + MCAP-A3-only` rerun
- Change tested:
  - patched `src/prepare_windows.py` to accept `--exclude-overlap-events` so annotation-selected windows can require one overlap family while forbidding others
  - rebuilt the stage-aware subset so every kept window had to be in-range `SLEEP-S2`, overlap `MCAP-A3`, and avoid simultaneous `MCAP-A1` / `MCAP-A2` overlap
  - saved artifacts to `projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv`, `projects/bruxism-cap/reports/random-window-cv-pass10-s2-mcap-a3-only.json`, `projects/bruxism-cap/reports/loso-cv-pass10-s2-mcap-a3-only.json`, and `projects/bruxism-cap/reports/pass10-s2-mcap-a3-only.md`
- Feasibility check:
  - all five already-verified subjects still had at least `20` eligible exclusive-`A3` windows locally (`brux1` `31`, `brux2` `111`, `n3` `76`, `n5` `38`, `n11` `42`), so the bounded rerun preserved the same `5`-subject / `20`-windows-per-subject shape as pass9
- Best random-window result:
  - random forest balanced accuracy / sensitivity / specificity / AUROC:
    `0.908 / 0.850 / 0.967 / 0.9791666666666666`
- Best LOSO result:
  - SVM balanced accuracy / sensitivity / specificity / AUROC:
    `0.500 / 0.000 / 0.500 / n/a`
- Subject-level result:
  - all three models again stayed at subject balanced accuracy `0.500` with subject sensitivity `0.000` and subject specificity `1.000`
- Interpretation:
  - the extraction rule is now more auditable because the kept `A3` windows can no longer mix with simultaneous `A1/A2` overlap
  - but honest held-out transfer still did not improve; it regressed again to chance-level balanced accuracy
  - this is therefore another useful negative result: even exclusive `A3` windows do not produce a transferable cross-subject boundary in the current tiny subset

### Pass 11 — rule-survival audit across overlap filters
- Change tested:
  - added `src/audit_rule_survival.py` to summarize how many eligible windows each verified subject and label keeps under the current stage-aware overlap rules before any new model rerun
  - saved artifacts to `projects/bruxism-cap/reports/rule-survival-audit-pass11.json` and `projects/bruxism-cap/reports/pass11-rule-survival-audit.md`
- Why this matters:
  - pass7, pass9, and pass10 changed event semantics, but they also changed per-subject and per-label window availability
  - without an explicit availability audit, later run-to-run comparisons can look like physiology changes when they are partly sampling-surface changes
- Key results:
  - the bruxism pool keeps `258/442` eligible pass4 `S2` windows (`58.4%`) under the mixed `S2+MCAP` rule, `161/442` (`36.4%`) under `S2+A3`, and `142/442` (`32.1%`) under exclusive `S2+A3-only`
  - the control pool thins much faster: `456/1026` (`44.4%`) under mixed `S2+MCAP`, `177/1026` (`17.3%`) under `S2+A3`, and `156/1026` (`15.2%`) under exclusive `S2+A3-only`
  - the imbalance is also sharp at the subject level: `brux2` still has `111` eligible exclusive-`A3` windows, while `n5` falls to `38`
- Interpretation:
  - the later overlap-filter reruns are still useful negative results, but they are not availability-neutral comparisons
  - the stricter `A3` rules preserve relatively more bruxism windows than control windows, so future family-to-family comparisons need explicit survival bookkeeping

### Pass 12 — matched exclusive `S2 + A1-only` versus `S2 + A3-only`
- Change tested:
  - built one matched exclusive-family comparison on the same verified 5-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`)
  - generated `A1-only` and `A3-only` feature tables capped to the same `14` windows per subject because `n11` has only `14` eligible `A1-only` windows locally
  - saved artifacts to `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a1_only_matched14.csv`, `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a3_only_matched14.csv`, `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a1-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json`, `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a3-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a3-only-matched14.json`, and `projects/bruxism-cap/reports/pass12-exclusive-a1-vs-a3-matched14.md`
- Why this matters:
  - pass10 showed that exclusive `A3` windows were still not transferable, while pass11 showed that overlap-rule comparisons were also availability comparisons
  - this pass answers the next validity question directly by holding the subject set and per-subject cap constant while changing only the exclusive overlap family
- Key results:
  - matched `A1-only` achieved the best LOSO window-level balanced accuracy at `0.686` (`logreg`) with held-out bruxism sensitivity `0.186`
  - matched `A1-only` also achieved the best subject-level LOSO summary at balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
  - matched `A3-only` remained weak even under the same `14`-window cap: best LOSO balanced accuracy was only `0.514`, and subject-level bruxism sensitivity stayed `0.000` for every model
  - the `A1-only` gain is still incomplete and fragile because only `brux2` crossed the subject threshold; `brux1` remained missed
- Interpretation:
  - the earlier focus on exclusive `A3` windows was too narrow; under matched conditions, exclusive `A1-only` is the stronger transfer candidate in the current tiny subset
  - this is still not a trustworthy detector, because subject-level sensitivity only improved from `0.000` to `0.500` and still depends on one of two bruxism subjects being recognized
  - the next bounded question should therefore stay on score/threshold auditing for pass12 rather than on model-family expansion

### Pass 13 — first matched `EMG1-EMG2` versus `C4-P4` channel comparison on the strongest current `A1-only` scaffold
- Change tested:
  - kept the same verified 5-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`), the same exclusive `SLEEP-S2 + MCAP-A1-only` rule, and the same `14`-windows-per-subject cap as pass12
  - regenerated the matched feature table using `EMG1-EMG2` instead of `C4-P4`
  - saved artifacts to `projects/bruxism-cap/data/window_features_pass13_emg_s2_mcap_a1_only_matched14.csv`, `projects/bruxism-cap/reports/random-window-cv-pass13-emg-s2-mcap-a1-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass13-emg-s2-mcap-a1-only-matched14.json`, and `projects/bruxism-cap/reports/pass13-emg-vs-c4-a1-only-matched14.md`
- Why this matters:
  - the repo had just been reframed as EMG-first, but that framing still needed one real matched channel comparison inside the current verified CAP scaffold
  - this pass changes only the signal channel, so it is the cleanest first test of whether the current honest `A1-only` result transfers to `EMG1-EMG2`
- Key results:
  - best random-window EMG balanced accuracy stayed superficially strong at `0.882` (`svm`), which means random splits remain a misleading comparison surface
  - best EMG LOSO balanced accuracy fell to only `0.543` (`logreg`), with held-out bruxism sensitivity `0.043`
  - subject-level EMG sensitivity fell back to `0.000` for every model; unlike pass12 `C4-P4`, the EMG rerun missed both `brux1` and `brux2`
- Interpretation:
  - this is a first-class negative result, not an EMG win: the first matched `EMG1-EMG2` rerun did **not** beat the current `C4-P4` anchor under the same rule and subset
  - the main failure is honest transfer, not in-dataset separability: random CV stayed high while LOSO subject detection regressed
  - the next bounded EMG-first question should be whether `EMG1-EMG2` prefers a different overlap family (for example exclusive `A3-only`) rather than assuming the current strongest `C4-P4` family transfers unchanged

### Pass 14 — matched `EMG1-EMG2` exclusive `A1-only` versus exclusive `A3-only`
- Change tested:
  - kept the same verified 5-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`), the same `14`-windows-per-subject cap, and the same EMG channel (`EMG1-EMG2`)
  - changed only the exclusive overlap family from `MCAP-A1-only` to `MCAP-A3-only`
  - saved artifacts to `projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv`, `projects/bruxism-cap/reports/random-window-cv-pass14-emg-s2-mcap-a3-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json`, and `projects/bruxism-cap/reports/pass14-emg-a1-vs-a3-matched14.md`
- Why this matters:
  - pass13 showed that the strongest current `C4-P4` family did not transfer cleanly to EMG
  - this pass answers the narrower EMG-first validity question directly: does `EMG1-EMG2` prefer a different exclusive overlap family on the same matched scaffold?
- Key results:
  - best random-window EMG balanced accuracy improved from `0.882` on `A1-only` to `0.954` on `A3-only` (`svm`), which is still not the trustworthy surface
  - best EMG LOSO balanced accuracy improved from `0.543` to `0.629` (`logreg`), with sensitivity rising only from `0.043` to `0.057`
  - subject-level EMG sensitivity still stayed `0.000` for every model, so both `brux1` and `brux2` remained missed at the default subject threshold
- Interpretation:
  - overlap-family choice matters inside EMG too: `A3-only` is less bad than `A1-only` on the current matched scaffold
  - but this is still not a baseline win, because the honest subject-level criterion did not improve at all
  - the next bounded EMG-first question should now be score / threshold auditing on the stronger `A3-only` EMG run rather than another model-family change

### Pass 15 — subject-threshold audit on the stronger EMG `A3-only` run
- Change tested:
  - added `src/audit_subject_thresholds.py` to sweep subject-score thresholds over a saved LOSO report and compare the resulting subject-level metrics against an anchor report
  - saved artifacts to `projects/bruxism-cap/reports/subject-threshold-audit-pass15-emg-a3-vs-c4-a1.json` and `projects/bruxism-cap/reports/pass15-emg-a3-threshold-audit.md`
- Why this matters:
  - pass14 still left one ambiguity: does the current EMG-first failure come from a bad default subject threshold, or from a deeper score-ordering problem that threshold tuning cannot fix?
- Key results:
  - in the stronger EMG run (`EMG1-EMG2` `A3-only` `logreg`), the best bruxism subject score is only `0.176` (`brux1`), while two controls still score higher: `n3` `0.267` and `n5` `0.266`
  - any threshold low enough to recover `brux1` also flips both `n3` and `n5` positive, dropping subject specificity to `0.333` and balanced accuracy to `0.417`
  - any threshold low enough to recover both bruxism subjects predicts every subject positive, collapsing specificity to `0.000`
  - the current honest anchor (`C4-P4` `A1-only` `logreg`) still has a positive best-bruxism minus highest-control margin of `+0.362`, while the EMG run has a negative margin of `-0.091`
- Interpretation:
  - this preserves a sharper negative result than pass14 alone: the current EMG-first failure is **not** mainly a threshold-choice problem
  - the bottleneck is now better localized to score ordering / feature validity on the fixed matched EMG scaffold
  - the next bounded step should therefore move to one compact EMG feature-validity audit rather than more threshold tweaking

### Pass 16 — EMG feature-validity audit on the stronger matched `A3-only` run
- Change tested:
  - added `src/audit_emg_feature_validity.py` to rebuild the saved pass14 `EMG1-EMG2 A3-only` `logreg` LOSO folds and summarize per-subject feature contributions
  - saved artifacts to `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.json` and `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.md`
- Why this matters:
  - pass15 showed that threshold tuning was a dead end, so the next bounded question became which handcrafted features were actually lifting `n3` and `n5` above `brux1`
- Key results:
  - the problematic subject ranking reproduced exactly under the audit rebuild: `n3` `0.267`, `n5` `0.266`, `brux1` `0.176`, `n11` `0.095`, `brux2` `0.074`
  - the same recurring high-score-control feature family kept appearing: `ratio_alpha_delta`, `min`, and `sample_entropy`
  - `brux1` looked like a different instability surface because its fold was dominated by extreme absolute-power / mean terms rather than the same control-favoring pattern
- Interpretation:
  - this preserved a useful EMG-first validity result: the failure survives a fold-by-fold rebuild and is not a reporting artifact
  - the next bounded step should be one small feature-family ablation on the fixed pass14 scaffold rather than more threshold schedules or larger models

### Pass 17 — matched `EMG1-EMG2` `A3-only` time-domain ablation
- Change tested:
  - patched `src/train_baseline.py` so the baseline runner can optionally include or exclude feature families by regex without changing the saved feature table
  - reran the same matched pass14 `EMG1-EMG2 A3-only` scaffold after dropping only the spectral / ratio family (`bp_*`, `rel_bp_*`, `ratio_*`), leaving `9` time-domain features
  - saved artifacts to `projects/bruxism-cap/reports/random-window-cv-pass17-emg-a3-timeonly-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass17-emg-a3-timeonly-matched14.json`, and `projects/bruxism-cap/reports/pass17-emg-a3-timeonly-ablation.md`
- Why this matters:
  - pass16 suggested the safest next patch was a single deletion-style ablation before trying new EMG-specific features
- Key results:
  - random-window CV stayed superficially high: best balanced accuracy improved slightly from `0.954` to `0.967`, so random splits remain a misleading surface
  - best LOSO window-level balanced accuracy regressed slightly from `0.629` to `0.614` (`logreg`), while sensitivity fell from `0.057` to `0.043`
  - subject-level sensitivity still stayed `0.000` for every model, so the honest subject-level verdict did not improve at all
  - the score ordering stayed hostile and in one respect worsened: `n3` rose from `0.267` to `0.328`, while `brux1` fell from `0.176` to `0.148` and `brux2` fell from `0.074` to `0.055`
- Interpretation:
  - this preserves another important negative result: the current EMG-first failure is **not** fixed by simply deleting the EEG-shaped spectral family
  - deletion-only ablation removes some suspect features, but it also weakens both bruxism subjects and leaves `n3` even harder to separate
  - the next bounded EMG-first step should therefore move from subtraction-only patches to one compact EMG-specific replacement family such as burst / envelope / amplitude-variability features

### Pass 18 — matched `EMG1-EMG2` `A3-only` envelope / burst replacement family
- Change tested:
  - patched `src/features.py` to add `8` compact EMG-oriented summaries: `rectified_mean`, `rectified_std`, `envelope_mean`, `envelope_std`, `envelope_cv`, `burst_fraction`, `burst_rate_hz`, and `p95_abs`
  - regenerated the same matched `EMG1-EMG2 A3-only` feature table on the verified `5`-subject / `14`-windows-per-subject scaffold
  - saved artifacts to `projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv`, `projects/bruxism-cap/reports/random-window-cv-pass18-emg-a3-envelope-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass18-emg-a3-envelope-matched14.json`, `projects/bruxism-cap/reports/pass18-emg-a3-envelope-replacement.md`, and `projects/bruxism-cap/reports/feature-validity-audit-pass18-emg-a3-envelope-logreg.md`
- Why this matters:
  - pass17 showed that subtraction-only cleanup was not enough, so the next bounded EMG-first question became whether one compact replacement-oriented EMG family could help on the same matched scaffold
- Key results:
  - random-window CV stayed unrealistically high: best balanced accuracy was still `0.933` (`logreg`)
  - best LOSO window-level balanced accuracy regressed again from `0.629` on pass14 and `0.614` on pass17 to `0.600` on pass18 (`logreg`)
  - subject-level sensitivity still stayed `0.000` for every model, so the honest verdict remained unchanged
  - the score ordering shifted but did not improve enough: `brux1` recovered slightly from `0.148` to `0.158`, `brux2` from `0.055` to `0.092`, and `n3` dropped from `0.328` to `0.245`, but `n5` stayed above `brux1` at `0.267`
- Interpretation:
  - this is another useful EMG-first negative result: adding one compact rectified-envelope / burst family is not enough by itself to rescue honest transfer
  - the new features do enter the model, but the same older feature family still dominates the wrong subject ordering, especially the large negative `mean` / bandpower burden on `brux1`
  - the next bounded step should therefore keep the new EMG family but test it under stricter feature selection rather than simple add-only expansion

### Pass 19 — matched `EMG1-EMG2` `A3-only` envelope family under stricter train-time feature selection
- Change tested:
  - kept the same pass18 feature table and reran the same matched `EMG1-EMG2 A3-only` scaffold while excluding only `bp_*`, `rel_bp_*`, and `ratio_*` at train time
  - saved artifacts to `projects/bruxism-cap/reports/random-window-cv-pass19-emg-a3-envelope-selected-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json`, and `projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md`
- Why this matters:
  - pass18 suggested that the new EMG-oriented family might be useful only if the older EEG-shaped spectral family stopped dominating the same matched scaffold
- Key results:
  - random-window CV stayed unrealistically high again: best balanced accuracy stayed `0.933` (`logreg`)
  - best LOSO window-level balanced accuracy recovered from `0.600` on pass18 to `0.629` on pass19 (`logreg`), matching pass14 while slightly improving specificity from `0.571` to `0.586`
  - subject-level sensitivity still stayed `0.000` for every model, so the honest verdict remained unchanged
  - the score ordering became slightly less hostile than pass18 on one edge (`n5` fell from `0.267` to `0.222` and `n11` stayed below `brux1`), but `n3` (`0.280`) and `n5` (`0.222`) still outranked `brux1` (`0.151`)
- Interpretation:
  - this is a useful partial-validity result, not a baseline win: the pass18 envelope / burst family behaves better under stricter feature selection than under add-only expansion
  - but the honest bottleneck still survives because the subject ordering remains wrong and subject-level bruxism sensitivity stays `0.000`
  - the next bounded step should now focus on one remaining score-ordering driver such as `mean`, rather than broader feature growth or model complexity

### Pass 20 — matched `EMG1-EMG2` `A3-only` envelope family with stricter selection plus `mean` ablation
- Change tested:
  - kept the same pass18 feature table and reran the same matched `EMG1-EMG2 A3-only` scaffold with the same pass19 exclusions for `bp_*`, `rel_bp_*`, and `ratio_*`
  - also excluded only one additional feature at train time: raw `mean`
  - saved artifacts to `projects/bruxism-cap/reports/random-window-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`, and `projects/bruxism-cap/reports/pass20-emg-a3-envelope-selected-nomean-matched14.md`
- Why this matters:
  - pass19 narrowed the remaining EMG-first suspicion to whether raw `mean` was still the one removable scalar dragging `brux1` down after the older spectral / ratio family had already been excluded
- Key results:
  - random-window CV stayed unrealistically high again: best balanced accuracy stayed `0.933` (`logreg`)
  - best LOSO window-level balanced accuracy regressed from `0.629` on pass19 to `0.600` overall (`svm`), while pass20 `logreg` fell further to `0.571` with sensitivity collapsing from `0.043` to `0.000`
  - subject-level sensitivity still stayed `0.000` for every model, so the honest verdict remained unchanged
  - the score ordering got materially worse for the key bruxism subject: `brux1` fell from `0.151` to `0.018`, while `n3` (`0.280`) and `n5` (`0.223`) barely moved
- Interpretation:
  - this is another useful EMG-first negative result: direct `mean` removal does **not** rescue the pass19 scaffold and instead makes `brux1` much less separable
  - the next bounded step should therefore stop doing blind deletion-only tweaks and instead audit the retained amplitude / envelope family directly

### Pass 21 — retained amplitude / envelope family audit on the pass19 working point
- Change tested:
  - kept the stronger pass19 matched `EMG1-EMG2 A3-only` scaffold fixed
  - kept the same pass19 train-time exclusions for `bp_*`, `rel_bp_*`, and `ratio_*`
  - added `projects/bruxism-cap/src/audit_emg_envelope_family.py` and audited the retained focused family (`sample_entropy`, `rectified_*`, `envelope_*`, `burst_*`, `p95_abs`) without changing the model recipe itself
  - saved artifacts to `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.json` and `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.md`
- Why this matters:
  - pass20 showed that naive raw-`mean` removal was the wrong next move, but the repo still needed one compact explanation of what the retained pass19 EMG family is actually doing subject by subject
- Key results:
  - the audit reproduced the pass19 ordering exactly: `n3` `0.280`, `n5` `0.222`, `brux1` `0.151`, `n11` `0.147`, `brux2` `0.088`
  - among the retained focused features, `sample_entropy` and `burst_fraction` still push `n3` and `n5` upward relative to `brux1`
  - `brux1` does look distinct on raw amplitude scale (`rectified_mean`, `envelope_mean`, `p95_abs` all much larger), but those same features remain net-negative contributors under the pass19 learned coefficients, so larger raw amplitude alone does not rescue the ranking
  - `burst_rate_hz` is the main retained feature that still pushes back toward `brux1`, but not strongly enough to overcome the control-favoring pieces
- Interpretation:
  - this is a useful EMG-first validity increment, not a baseline win: the retained family is active, but it is not cleanly bruxism-aligned on the current tiny matched subset
  - the next bounded EMG-only move should therefore be normalization-aware extraction or scaling work that preserves the retained family, not more blind single-feature deletion

### Pass 22 — selection-aware `EMG1-EMG2 A3-only` rerun with robust per-window `median_mad` normalization
- Change tested:
  - kept the stronger pass19 matched `EMG1-EMG2 A3-only` scaffold fixed
  - kept the same pass19 train-time exclusions for `bp_*`, `rel_bp_*`, and `ratio_*`
  - patched the extraction path so each kept window can be robust-centered and scaled before feature computation using `median` plus `MAD`, then regenerated the matched 5-subject / 14-windows-per-subject EMG table with `signal_transform=median_mad`
  - saved artifacts to `projects/bruxism-cap/data/window_features_pass22_emg_s2_mcap_a3_only_matched14_medianmad.csv`, `projects/bruxism-cap/reports/random-window-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`, and `projects/bruxism-cap/reports/pass22-emg-a3-envelope-selected-medianmad-matched14.md`
- Why this matters:
  - pass21 said the safest EMG-only next move was one normalization-aware extraction test rather than more blind feature deletion
- Key results:
  - random-window CV stayed unrealistically high again: best balanced accuracy stayed `0.933` (`logreg`)
  - best LOSO window-level balanced accuracy regressed from `0.629` on pass19 to only `0.571` on pass22 (`svm`), with sensitivity collapsing to `0.000`
  - subject-level sensitivity still stayed `0.000` for every model, so the honest verdict remained unchanged
  - the subject ranking became harsher than pass19: pass22 `logreg` scored `n11` `0.270`, `n5` `0.251`, `n3` `0.195`, `brux2` `0.033`, `brux1` `0.009`
- Interpretation:
  - this preserves another useful EMG-first negative result: simple per-window robust normalization is **not** the fix for the current matched EMG scaffold
  - the stronger EMG-first working point remains pass19, and the next bounded step should shift back toward benchmark clarity rather than another extraction rewrite

A new project-framing decision now sits on top of that history: keep CAP as the reproducible benchmark dataset, but pivot the next active extraction path to `EMG1-EMG2` as the primary channel and treat `C4-P4` as the comparison channel. That keeps the anti-leakage lessons from the first 14 passes while aligning the next experiments more closely with the newer portable-EMG literature.

## Key evidence from the first runs

### 0. Current project framing changed after the first 12 passes
As of `2026-05-04`, the repo still preserves the original `C4-P4`-based baseline history exactly as run, but the project itself is now documented as an **EMG-first** benchmark. `EMG1-EMG2` is the primary next-pass channel, and `C4-P4` is now the comparison channel for matched reruns rather than the default extraction target.

### 1. Random-window CV is still overly optimistic
Even after dropping the explicit sampling-rate proxy feature, random-window CV remained extremely high (`0.963` balanced accuracy). That is too strong to trust on `120` windows from `6` people when LOSO remains weak.

### 2. The strongest current result is a leakage warning, not a bruxism detector
The best honest subject-aware result after the first measurement fix was only:
- balanced accuracy: `0.733`
- sensitivity on held-out bruxism subjects: `0.117`
- specificity on held-out control subjects: `0.617`

That means the model mostly fails to recognize held-out bruxism subjects.

### 3. Annotation-aware stage matching alone did not fix generalization
The first stage-aware rerun used only `SLEEP-S2` windows from a 5-subject subset and still produced perfect random-window CV while LOSO fell to only `0.600` balanced accuracy and `0.030` held-out bruxism sensitivity. That is a stronger negative result than pass3, not an improvement.

### 4. Subject-level aggregation makes the honest result even harsher
After pass5, every tested LOSO model still produced `0.000` held-out bruxism sensitivity once predictions were collapsed to one verdict per held-out subject. In other words, the models sometimes emitted a few positive windows, but never enough to call a bruxism subject positive overall at the default threshold.

### 5. The local record/annotation pairing itself now needs scrutiny
The annotation-aware pass exposed a concrete data-validity issue: `n10.edf` is only about `3783` seconds long, but `n10.txt` contains later scored sleep events that fall outside the available signal. `brux1` shows a milder version of the same mismatch. So the next bottleneck is now narrower and better defined: validate record completeness / scoring alignment before trusting more stage-aware comparisons.

### 6. An obvious acquisition confound was real
A quick coefficient check on the pass2 logistic-regression fit showed that `n_samples` had the largest absolute coefficient. That was a useful first autoresearch catch, but removing it only slightly reduced the random-split optimism. So the confound was real, just not the only one.

### 7. The pass4 alignment audit narrowed the data-validity problem further
A follow-up EDF-versus-sidecar audit is now saved in `projects/bruxism-cap/reports/annotation-alignment-audit-pass4-s2.md`. The key finding is that `n10` has `0` in-range `SLEEP-S2` windows for the local files, while `brux1` has enough usable early `S2` windows but hundreds of later scored `S2` rows beyond the available EDF duration. So pass4 was still useful, but the next bottleneck is now more precise than before: preserve the annotation-aware path, keep explicit subject exclusions, and audit local record completeness before trying to interpret more stage-aware results.

### 8. The new confound audit narrowed the failure story again
The new pass6 artifact (`projects/bruxism-cap/reports/subject-confound-audit-pass6.md`) did **not** find stronger subject clustering than label clustering in the current handcrafted feature tables. On both the pass3 and pass4 datasets, label silhouette and nearest-neighbor agreement were higher than the subject versions. That means the leakage story is now more specific: random window splits still flatter the project, but the current feature tables are not winning only by memorizing subject identity. They appear to capture a label-separation pattern that holds within the seen-subject pool and breaks under held-out-subject transfer.

### 9. The pass7 mixed-event bucket is heterogeneous by subject and label
The new pass8 artifact (`projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.md`) showed that the current `SLEEP-S2 + (MCAP-A1|A2|A3)` subset mixes materially different overlap-event families across subjects. `brux2` is heavily `A3`-dominated while `n5` is heavily `A1`-dominated, and that mismatch already exists in the full eligible pools before the first-`20` cap. So the next extraction test should be a narrower single-family overlap rule rather than another broad mixed-event bucket.

### 10. Narrowing to `S2 + A3` reduced random optimism but still did not transfer
The new pass9 artifact (`projects/bruxism-cap/reports/pass9-s2-mcap-a3.md`) showed that moving from the mixed `S2+MCAP` bucket to an `S2 + A3` overlap rule reduced random-window balanced accuracy from `1.000` to `0.921`, which is directionally healthier. But the honest result did not improve: the best LOSO balanced accuracy fell from `0.590` to `0.550`, and subject-level bruxism sensitivity still stayed `0.000` for every model. So the failure is not explained just by mixing `A1`, `A2`, and `A3` together; the next extraction step needs to be even more auditable.

### 11. Exclusive `A3` windows were cleaner but still not transferable
The new pass10 artifact (`projects/bruxism-cap/reports/pass10-s2-mcap-a3-only.md`) made the overlap rule more auditable by excluding simultaneous `MCAP-A1` and `MCAP-A2` overlap from the kept `SLEEP-S2 + A3` windows. But the honest result still did not improve: the best LOSO balanced accuracy fell again to `0.500`, and subject-level bruxism sensitivity still stayed `0.000` for every model. So even exclusive `A3` windows do not isolate a transferable cross-subject boundary in the current tiny subset.

### 12. The overlap rules also change availability, not just event meaning
The new pass11 artifact (`projects/bruxism-cap/reports/pass11-rule-survival-audit.md`) showed that the later overlap filters are not availability-neutral. Relative to pass4 `S2`, the bruxism pool keeps `32.1%` of its eligible windows under exclusive `A3`, while the control pool keeps only `15.2%`. `brux2` still has `111` eligible exclusive-`A3` windows, but `n5` falls to `38`. So future overlap-family comparisons need to preserve the rule-survival context rather than reading each rerun as a like-for-like subset.

### 13. Under matched conditions, exclusive `A1-only` transfers better than exclusive `A3-only`
The new pass12 comparison (`projects/bruxism-cap/reports/pass12-exclusive-a1-vs-a3-matched14.md`) controlled the subject set and per-subject cap by matching both exclusive families to `14` windows per subject. Under that fairer comparison, `A1-only` improved the honest measurement surface: best LOSO balanced accuracy rose to `0.686`, and subject-level bruxism sensitivity rose to `0.500`, while matched `A3-only` still stayed at `0.000` subject-level sensitivity. That is an important validity clue, but not yet a stable baseline win, because `brux1` still failed and the gain is carried by only one of the two bruxism subjects.

### 14. EMG prefers `A3-only` over `A1-only`, but still fails the honest subject test
The new pass14 comparison (`projects/bruxism-cap/reports/pass14-emg-a1-vs-a3-matched14.md`) held the same verified subject set, cap, channel, and model family constant while changing only the exclusive overlap family inside `EMG1-EMG2`. That improved the best EMG LOSO balanced accuracy from `0.543` on `A1-only` to `0.629` on `A3-only`, and it reduced several control-subject mean scores. But subject-level bruxism sensitivity still stayed `0.000` for every model, so the best honest baseline in the repo remains the pass12 `C4-P4 A1-only` run rather than any EMG family.

### 15. The stronger EMG run fails because subject ordering is wrong, not because `0.5` is too strict
The new pass15 threshold audit (`projects/bruxism-cap/reports/pass15-emg-a3-threshold-audit.md`) showed that the stronger `EMG1-EMG2 A3-only` run cannot be rescued by retuning the subject threshold alone. The best bruxism subject score (`brux1` `0.176`) still sits below two controls (`n3` `0.267`, `n5` `0.266`), so any threshold that recovers `brux1` also creates at least two control false positives. Thresholds that recover both bruxism subjects collapse specificity entirely. That makes the next bottleneck sharper: feature validity / score ordering, not subject-threshold choice.

### 16. The EMG score-ordering failure is now localized to one small feature family plus one brux1-specific instability
The new pass16 audit (`projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.md`) rebuilt the saved pass14 `logreg` LOSO folds and explained which standardized features are pushing each held-out subject up or down. It reproduced the same subject ordering as pass15 (`n3` `0.267`, `n5` `0.266`, `brux1` `0.176`, `n11` `0.095`, `brux2` `0.074`), so the negative result is stable. The useful new narrowing is that the high-score controls repeatedly surface `ratio_alpha_delta`, `min`, and `sample_entropy` as positive contributors, while `brux1` is dominated by extreme absolute-power / mean terms. So the next EMG-first move should be one small feature-family ablation, not more threshold schedules.

### 17. The new EMG family works better under stricter feature selection, but the honest subject verdict still does not move
The new pass19 rerun (`projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md`) kept the pass18 envelope / burst family and excluded the older `bp_*`, `rel_bp_*`, and `ratio_*` family at train time on the same matched `EMG1-EMG2 A3-only` scaffold. That recovered the best pass14 LOSO balanced accuracy (`0.629`) and slightly improved specificity (`0.586`), which is useful evidence that the EMG-oriented family should not just be stacked on top of the older spectral features. But the honest baseline verdict still did not improve: subject-level sensitivity remained `0.000`, and both `n3` and `n5` still outranked `brux1`. So the next bottleneck is now narrower again: one remaining score-ordering driver, not a broad feature-family choice.

### 18. Naive `mean` removal makes the strongest current EMG recipe worse
The new pass20 rerun (`projects/bruxism-cap/reports/pass20-emg-a3-envelope-selected-nomean-matched14.md`) tested that narrowed suspicion directly by taking the pass19 selection-aware recipe and excluding only raw `mean` in addition to the existing spectral / ratio removals. The result is a preserved negative one: best LOSO window-level balanced accuracy regressed to `0.600` overall, pass20 `logreg` fell to `0.571`, subject-level sensitivity stayed `0.000`, and `brux1` collapsed from `0.151` to `0.018` while `n3` and `n5` barely moved. So `mean` is not safe to delete naively on the current EMG-first scaffold; if it is revisited at all, it should be through normalization-aware extraction rather than another simple ablation.

### 19. The retained pass19 envelope family is active, but still not cleanly bruxism-aligned
The new pass21 audit (`projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.md`) then checked the retained pass19 family directly instead of launching another rerun. That audit preserved the same honest ranking and made the remaining failure shape more specific: `sample_entropy` and `burst_fraction` still help the highest-score controls, while `brux1`'s much larger raw `rectified_mean`, `envelope_mean`, and `p95_abs` remain net-negative under the current learned coefficients. So the next EMG-only step should be normalization-aware extraction or scaling that preserves the retained family, not more blind deletion-only feature tweaks.

### 20. Direct `median_mad` normalization also fails on the same matched EMG scaffold
The new pass22 rerun (`projects/bruxism-cap/reports/pass22-emg-a3-envelope-selected-medianmad-matched14.md`) tested that exact normalization-aware hypothesis by robust-centering and scaling each kept EMG window before feature extraction while leaving the pass19 subject subset, overlap rule, and train-time feature exclusions fixed. That did **not** improve the honest result. Best LOSO balanced accuracy regressed from `0.629` to `0.571`, subject-level sensitivity stayed `0.000`, and both bruxism subjects fell even lower in the ranking under `logreg` (`brux1` `0.151 -> 0.009`, `brux2` `0.088 -> 0.033`). So the stronger EMG-first working point still remains pass19, and the next bounded step should return to benchmark-clarity comparison rather than another extraction rewrite.

### 21. Shared subject-score comparison makes the remaining EMG gap explicit
The new pass23 comparison (`projects/bruxism-cap/reports/pass23-emg-pass19-vs-c4-pass12-subject-score-comparison.md`) finally put the stronger pass19 `EMG1-EMG2 A3-only` working point and the honest pass12 `C4-P4 A1-only` anchor into one shared subject-score table on the same verified `5`-subject / `14`-windows-per-subject scaffold. That clarified the benchmark gap more sharply than aggregate metrics alone. The EMG working point does improve one hard case—`brux1` rises from `0.018` on the anchor to `0.151` on EMG—but the overall honest baseline still belongs to the anchor because `brux2` collapses from `0.795` to `0.088` and the highest-score control shifts from `n5` (`0.433`) to `n3` (`0.280`). The net best-bruxism-minus-highest-control margin therefore swings from `+0.362` on the anchor to `-0.129` on EMG. So the next bounded EMG-first step should focus specifically on why `brux2` collapses under `EMG1-EMG2` and why `n3` becomes the dominant control, not on another broad extraction rewrite.

### 22. Shared-time-position matching improves bruxism scores but still does not rescue EMG transfer
The new pass25 rerun (`projects/bruxism-cap/reports/pass25-emg-a3-time-position-matched-selected.md`) tested the pass24 timing concern directly by regenerating the uncapped exclusive `SLEEP-S2 + MCAP-A3-only` `EMG1-EMG2` pool for the same verified `5`-subject subset, then forcing every subject onto the same shared absolute `start_s` interval before rerunning the pass19-style feature exclusions. That stricter scaffold turned out to be feasible only at `10` windows per subject because `n3` and `n5` each have just `10` valid candidate windows inside the common interval. The result is another useful negative-but-informative EMG note: both bruxism subjects do rise (`brux1` `0.151` -> `0.282`, `brux2` `0.088` -> `0.215`), so time-position mismatch was contributing something real, but all three controls rise too (`n11` `0.417`, `n5` `0.416`, `n3` `0.400`) and honest subject-level sensitivity still stays `0.000`. Best LOSO window-level balanced accuracy also fails to beat pass19 (`0.600` best on pass25 versus `0.629` on pass19). So the stricter time-position match changes the failure surface but does not overturn the current best honest EMG working point.

### 23. Rebuilding the same strict scaffold on `C4-P4` does not rescue the benchmark either
The new pass26 comparison (`projects/bruxism-cap/reports/pass26-c4-a3-time-position-matched-vs-emg.md`) reused the exact same shared-time-position `SLEEP-S2 + MCAP-A3-only` scaffold from pass25—same `5` subjects, same `3210.0` to `12230.0` interval, same `10` windows per subject, and same train-time feature exclusions—but swapped only the extracted channel from `EMG1-EMG2` to `C4-P4`. This clarified the channel-vs-scaffold question directly. Random-window CV favored `C4-P4` again (`0.883` vs `0.808` balanced accuracy), but the honest LOSO surface did **not**: strict-scaffold `C4-P4` reached only `0.520` best LOSO balanced accuracy and `0.333` subject-level balanced accuracy, versus `0.600` and `0.500` for strict-scaffold `EMG1-EMG2`. Both channels still failed with `0.000` subject-level sensitivity, but `C4-P4` was worse because it also turned `n3` into a subject-level false positive. That preserves the EMG-first framing: the stricter `A3-only` / time-position-matched scaffold itself now looks like the larger bottleneck than channel choice alone.

### 24. The same strict time-position rule is too brittle for `EMG1-EMG2 A1-only`
The new pass27 feasibility audit (`projects/bruxism-cap/reports/pass27-emg-a1-time-position-feasibility.md`) followed the exact next question from pass26 without reverting away from the EMG-first frame: keep the same verified `5`-subject subset, keep `EMG1-EMG2`, switch to exclusive `SLEEP-S2 + MCAP-A1-only`, and reuse the same simple shared-absolute-interval selector before any new model rerun. The uncapped `A1-only` pool is large enough overall (`233` rows total: `27` for `brux1`, `29` for `brux2`, `29` for `n3`, `134` for `n5`, `14` for `n11`), so the overlap family itself is not missing locally. But once the strict common interval is enforced, the scaffold collapses to `7650.0`–`12650.0` seconds and only `2` windows per subject remain feasible because `n3` and `n11` each contribute just `2` candidate rows there while `brux2` contributes only `3`. I therefore preserved this as an extraction-validity result and intentionally did **not** trust a new LOSO rerun on the resulting `10`-row subset. The lesson is useful and specific: the current hard shared-interval matching rule is itself too brittle for `A1-only`, so the next timing-aware EMG pass should soften the selector rather than pretending a `2`-windows-per-subject scaffold is a meaningful benchmark.

### 25. A softer percentile-band timing scaffold fixes the extraction collapse but not the honest EMG transfer failure
The new pass28 rerun (`projects/bruxism-cap/reports/pass28-emg-a1-percentile-band-rerun.md`) made the next bounded move from pass27 rather than abandoning the EMG-first frame: patch the selector itself, keep the same verified `5` subjects and exclusive `SLEEP-S2 + MCAP-A1-only`, and test one softer timing-control scaffold before any bigger modeling change. The new `percentile-band` mode in `select_time_position_matched_windows.py` keeps windows by relative within-subject time position (`0.10` to `0.90`) instead of forcing one hard shared absolute interval, and `train_baseline.py` now treats the new `relative_time_quantile` field as metadata so the selector does not leak its own coordinate into training. That patch solves the immediate pass27 validity problem: the scaffold expands from only `2` windows per subject (`10` rows total) to a reproducible `10` windows per subject (`50` rows total). But the honest result stays negative. Best LOSO window-level balanced accuracy reaches `0.600` (`svm`), which only ties the stricter pass25 EMG result, and subject-level sensitivity still stays `0.000` with both bruxism subjects below all three controls in mean score order (`n3` `0.422`, `n11` `0.319`, `n5` `0.264`, `brux1` `0.222`, `brux2` `0.209`). So the softer timing-control patch is real progress in extraction validity and reproducibility, but it still does not produce a better honest EMG benchmark.

### 26. A matched cross-channel audit shows the repaired scaffold is real and localizes the remaining gap to `brux1` versus `n3`
The new pass30 audit (`projects/bruxism-cap/reports/pass30-a1-percentile-band-channel-gap-audit.md`) followed directly from pass29 without reverting the EMG-first frame or launching another rerun. It kept the same repaired percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold fixed, verified that the selected rows are timing-matched across `EMG1-EMG2` and `C4-P4`, and rebuilt the same `logreg` LOSO folds with the same train-time feature exclusions to inspect the remaining subject-score gaps. This preserved two sharper conclusions. First, the pass28/pass29 comparison is a real channel / feature-behavior difference rather than a hidden row-selection change: the same `10` windows per subject are being compared. Second, `brux1` remains the shared hard case under both channels, but the gap is much smaller on `C4-P4` (`n3 - brux1 = +0.012`) than on `EMG1-EMG2` (`+0.260`), while the main channel-level separation is now concentrated in `brux2`: EMG leaves `brux2` far below `n3` (`brux2 - n3 = -0.494`), whereas `C4-P4` flips that decisively positive (`+0.542`). The feature summaries also preserve a useful negative result for EMG-first work: on the repaired scaffold, the stubborn overlap is now narrow enough to audit directly, with recurring support for `n3` from irregularity / burst-style features and hostile amplitude / crossing behavior on the bruxism folds. So the next bounded move should stay validity-first and target the shared `brux1`-versus-`n3` overlap before changing model family.

## Failure notes

Record weak results honestly:
- What failed first:
  - the original extraction path was too expensive for large CAP EDFs until loading and entropy computation were made lighter
- What failed next:
  - the initial `3`-subject pilot could not support a valid LOSO baseline
- What still fails now:
  - the `6`-subject baseline still shows a large random-vs-LOSO gap and near-collapse on held-out bruxism sensitivity
- How it showed up in artifacts:
  - pass2 random CV was effectively perfect while LOSO was poor
  - pass3 removed an obvious feature leak, but LOSO stayed weak
- Why that matters:
  - the current task setup is still too vulnerable to subject-specific or acquisition-specific cues

## Current best explanation

The current project bottleneck is still not model capacity. It is now the combination of:
- tiny subject count
- a label-separation pattern that looks strong under random window mixing but does not survive held-out-subject transfer
- a harsher subject-level failure mode where partial positive windows do not translate into correct held-out subject calls
- possible EDF / scoring-file mismatches for at least `n10` and partly `brux1`
- annotation-aware `SLEEP-S2` filtering that is reproducible but still too coarse to isolate a more transferable physiological signature
- a mixed `S2+MCAP` bucket whose overlap-event composition differs materially across subjects
- window-level evaluation on single-subject folds

## Best next bounded step

Do not add model complexity yet.

Next experiment:
1. preserve `n10` as excluded from local `SLEEP-S2` reruns unless a fuller matching EDF is found
2. keep `brux1` in the stage-aware subset only with explicitly in-range windows
3. preserve the new overlap-event audit as evidence that the current mixed `S2+MCAP` bucket is heterogeneous by subject
4. preserve the new matched EMG-family comparison as evidence that `A3-only` is currently the less-bad EMG overlap family on the verified subset
5. preserve the new subject-threshold audit as evidence that the stronger EMG run fails because two controls still outrank the best bruxism subject
6. preserve the new pass19 selection-aware rerun as the stronger current EMG-first working point
7. preserve the new pass22 normalization-aware rerun as evidence that simple per-window `median_mad` extraction is **not** the fix for that working point
8. preserve the new shared subject-score comparison as evidence that the current EMG gap is dominated by `brux2` collapse plus `n3` as the highest-score control
9. preserve the new shared-time-position rerun as evidence that the timing concern was real but not sufficient: both bruxism subjects rise, yet all controls still outrank them and honest subject-level sensitivity stays `0.000`
10. preserve the new matched strict-scaffold comparison as evidence that `C4-P4` does **not** rescue the stricter `A3-only` benchmark and that the timing-matched scaffold itself is now the bigger bottleneck than channel choice alone
11. preserve the new strict-`A1-only` feasibility audit as evidence that the current hard shared-interval selector collapses `EMG1-EMG2 A1-only` to only `2` windows per subject and should not be treated as a trustworthy new benchmark surface
12. preserve the new pass28 percentile-band rerun as evidence that softer timing control fixes the extraction-collapse problem but still leaves both bruxism subjects below all three controls on the honest LOSO subject surface
13. preserve the new pass29 matched percentile-band comparison as evidence that `C4-P4` does beat matched `EMG1-EMG2` on the repaired `A1-only` scaffold, but only partially: `brux2` is recovered cleanly while `brux1` still trails `n3`, so the result ties rather than beats the older best honest subject-level baseline
14. preserve the new pass30 cross-channel gap audit as evidence that the repaired percentile-band scaffold itself is now genuinely matched across channels and that the remaining honest bottleneck is narrower than “EMG is worse”: `brux1` still trails `n3` under both channels, while the main channel gap is `brux2` flipping only on `C4-P4`
15. preserve the new pass31 recurrence audit as evidence that the suspected narrow `n3`-favoring trio is not the whole story on the repaired scaffold: `burst_fraction` recurs, but the strongest EMG control-favoring gap is still broader (`mean`, `max`, `ptp`, `zero_crossing_rate`)
16. preserve the new pass32 broader morphology ablation as evidence that wholesale deletion is not the fix either: `EMG1-EMG2` still misses both bruxism subjects, `n3` stays above `brux1`, and the same ablation destroys the useful `brux2` recovery on `C4-P4`
17. preserve the new pass33 smaller raw-location ablation as evidence that a narrower deletion is not the fix either: removing only `mean`, `min`, and `max` leaves `C4-P4` essentially unchanged but makes `EMG1-EMG2` worse by collapsing `brux1` while `n3` stays high
18. next, keep the repaired percentile-band `A1-only` scaffold fixed and prefer a record-relative or within-record morphology representation audit before changing timing rules again or adding model complexity
19. only after that consider a new model family

## Files produced by the first runs

- `projects/bruxism-cap/data/window_features_pass1.csv`
- `projects/bruxism-cap/data/window_features_pass2.csv`
- `projects/bruxism-cap/reports/random-window-cv-pass1.json`
- `projects/bruxism-cap/reports/random-window-cv-pass2.json`
- `projects/bruxism-cap/reports/loso-cv-pass2.json`
- `projects/bruxism-cap/reports/random-window-cv-pass3-nosfreq.json`
- `projects/bruxism-cap/reports/loso-cv-pass3-nosfreq.json`
- `projects/bruxism-cap/data/window_features_pass4_s2.csv`
- `projects/bruxism-cap/reports/random-window-cv-pass4-s2.json`
- `projects/bruxism-cap/reports/loso-cv-pass4-s2.json`
- `projects/bruxism-cap/reports/annotation-alignment-audit-pass4-s2.md`
- `projects/bruxism-cap/reports/loso-cv-pass5-pass2-subjectagg.json`
- `projects/bruxism-cap/reports/loso-cv-pass5-pass4-s2-subjectagg.json`
- `projects/bruxism-cap/src/audit_subject_confound.py`
- `projects/bruxism-cap/reports/subject-confound-audit-pass6.json`
- `projects/bruxism-cap/reports/subject-confound-audit-pass6.md`
- `projects/bruxism-cap/src/audit_overlap_event_mix.py`
- `projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.json`
- `projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.md`
- `projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv`
- `projects/bruxism-cap/reports/random-window-cv-pass10-s2-mcap-a3-only.json`
- `projects/bruxism-cap/reports/loso-cv-pass10-s2-mcap-a3-only.json`
- `projects/bruxism-cap/reports/pass10-s2-mcap-a3-only.md`
- `projects/bruxism-cap/src/audit_rule_survival.py`
- `projects/bruxism-cap/reports/rule-survival-audit-pass11.json`
- `projects/bruxism-cap/reports/pass11-rule-survival-audit.md`
- `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a1_only_matched14.csv`
- `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a3_only_matched14.csv`
- `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a1-only-matched14.json`
- `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json`
- `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a3-only-matched14.json`
- `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a3-only-matched14.json`
- `projects/bruxism-cap/reports/pass12-exclusive-a1-vs-a3-matched14.md`
- `projects/bruxism-cap/data/window_features_pass13_emg_s2_mcap_a1_only_matched14.csv`
- `projects/bruxism-cap/reports/random-window-cv-pass13-emg-s2-mcap-a1-only-matched14.json`
- `projects/bruxism-cap/reports/loso-cv-pass13-emg-s2-mcap-a1-only-matched14.json`
- `projects/bruxism-cap/reports/pass13-emg-vs-c4-a1-only-matched14.md`
- `projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv`
- `projects/bruxism-cap/reports/random-window-cv-pass14-emg-s2-mcap-a3-only-matched14.json`
- `projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json`
- `projects/bruxism-cap/reports/pass14-emg-a1-vs-a3-matched14.md`
- `projects/bruxism-cap/src/audit_subject_thresholds.py`
- `projects/bruxism-cap/reports/subject-threshold-audit-pass15-emg-a3-vs-c4-a1.json`
- `projects/bruxism-cap/reports/pass15-emg-a3-threshold-audit.md`
- `projects/bruxism-cap/src/audit_emg_feature_validity.py`
- `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.json`
- `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.md`
- `projects/bruxism-cap/reports/random-window-cv-pass19-emg-a3-envelope-selected-matched14.json`
- `projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json`
- `projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md`
- `projects/bruxism-cap/reports/random-window-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`
- `projects/bruxism-cap/reports/loso-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`
- `projects/bruxism-cap/reports/pass20-emg-a3-envelope-selected-nomean-matched14.md`
- `projects/bruxism-cap/src/audit_emg_envelope_family.py`
- `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.json`
- `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.md`
- `projects/bruxism-cap/src/compare_subject_score_surfaces.py`
- `projects/bruxism-cap/reports/subject-score-comparison-pass23-emg-pass19-vs-c4-pass12.json`
- `projects/bruxism-cap/reports/pass23-emg-pass19-vs-c4-pass12-subject-score-comparison.md`
- `projects/bruxism-cap/data/window_features_pass22_emg_s2_mcap_a3_only_matched14_medianmad.csv`
- `projects/bruxism-cap/reports/random-window-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`
- `projects/bruxism-cap/reports/loso-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`
- `projects/bruxism-cap/reports/pass22-emg-a3-envelope-selected-medianmad-matched14.md`
- `projects/bruxism-cap/src/select_time_position_matched_windows.py`
- `projects/bruxism-cap/data/window_features_pass25_emg_s2_mcap_a3_only_full_envelope.csv`
- `projects/bruxism-cap/data/window_features_pass25_emg_s2_mcap_a3_only_timepos10_envelope.csv`
- `projects/bruxism-cap/reports/time-position-match-pass25-emg-a3.json`
- `projects/bruxism-cap/reports/random-window-cv-pass25-emg-a3-timepos10-selected.json`
- `projects/bruxism-cap/reports/loso-cv-pass25-emg-a3-timepos10-selected.json`
- `projects/bruxism-cap/reports/pass25-emg-a3-time-position-matched-selected.md`
- `projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_full_envelope.csv`
- `projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_timepos10_envelope.csv`
- `projects/bruxism-cap/reports/time-position-match-pass26-c4-a3.json`
- `projects/bruxism-cap/reports/random-window-cv-pass26-c4-a3-timepos10-selected.json`
- `projects/bruxism-cap/reports/loso-cv-pass26-c4-a3-timepos10-selected.json`
- `projects/bruxism-cap/reports/pass26-c4-a3-time-position-matched-vs-emg.md`
- `projects/bruxism-cap/data/window_features_pass27_emg_s2_mcap_a1_only_full_envelope.csv`
- `projects/bruxism-cap/data/window_features_pass27_emg_s2_mcap_a1_only_timepos2_envelope.csv`
- `projects/bruxism-cap/reports/time-position-match-pass27-emg-a1.json`
- `projects/bruxism-cap/reports/pass27-emg-a1-time-position-feasibility.md`
- `projects/bruxism-cap/data/window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`
- `projects/bruxism-cap/reports/time-position-match-pass28-emg-a1-pct10-90.json`
- `projects/bruxism-cap/reports/random-window-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`
- `projects/bruxism-cap/reports/loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`
- `projects/bruxism-cap/reports/pass28-emg-a1-percentile-band-rerun.md`
- `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_full_envelope.csv`
- `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`
- `projects/bruxism-cap/reports/time-position-match-pass29-c4-a1-pct10-90.json`
- `projects/bruxism-cap/reports/random-window-cv-pass29-c4-a1-pct10-90-timepos10-selected.json`
- `projects/bruxism-cap/reports/loso-cv-pass29-c4-a1-pct10-90-timepos10-selected.json`
- `projects/bruxism-cap/reports/pass29-c4-a1-percentile-band-vs-emg.md`
- `projects/bruxism-cap/src/audit_percentile_band_channel_gap.py`
- `projects/bruxism-cap/reports/feature-validity-audit-pass30-a1-pct-channel-gap.json`
- `projects/bruxism-cap/reports/pass30-a1-percentile-band-channel-gap-audit.md`
- `projects/bruxism-cap/src/audit_percentile_band_n3_family_recurrence.py`
- `projects/bruxism-cap/reports/feature-validity-audit-pass31-a1-pct-n3-family.json`
- `projects/bruxism-cap/reports/pass31-a1-percentile-band-n3-family-recurrence.md`
- `projects/bruxism-cap/src/run_pass32_broad_morphology_ablation.py`
- `projects/bruxism-cap/reports/loso-cv-pass32-emg-a1-pct10-90-broad-ablation.json`
- `projects/bruxism-cap/reports/loso-cv-pass32-c4-a1-pct10-90-broad-ablation.json`
- `projects/bruxism-cap/reports/pass32-broad-morphology-ablation-summary.json`
- `projects/bruxism-cap/reports/pass32-broad-morphology-ablation.md`
- `projects/bruxism-cap/src/run_pass33_raw_location_ablation.py`
- `projects/bruxism-cap/reports/loso-cv-pass33-emg-a1-pct10-90-rawloc-ablation.json`
- `projects/bruxism-cap/reports/loso-cv-pass33-c4-a1-pct10-90-rawloc-ablation.json`
- `projects/bruxism-cap/reports/pass33-raw-location-ablation-summary.json`
- `projects/bruxism-cap/reports/pass33-raw-location-ablation.md`

## Short takeaway

The first real `bruxism-cap` runs succeeded as project infrastructure and failed as a trustworthy detector. That is a useful result. After pass4, the follow-up alignment audit, the pass5 subject-level aggregation hardening, the pass6 subject-versus-label confound audit, the pass8 overlap-event mix audit, the new pass11 rule-survival audit, the pass12 matched-family comparison, and the later EMG-first matched reruns plus threshold audit, the repo now has a tighter explanation of the failure surface: simple `SLEEP-S2` matching did not fix held-out-subject transfer, subject-level detection is still the harsher interpretation surface, the current feature tables seem to separate the observed labels inside the seen-subject pool more easily than they separate subject identity, the mixed `S2+MCAP` subset itself is heterogeneous by overlap-event family, overlap-family comparisons must preserve the availability context, and the stronger EMG run fails because two controls still outrank the best bruxism subject. Under matched conditions, exclusive `A1-only` is more promising than exclusive `A3-only` for `C4-P4`, while `EMG1-EMG2` looks less bad under exclusive `A3-only` than under `A1-only`. The later EMG feature work sharpens that again: the pass18 envelope / burst family is more useful when the older spectral / ratio family is excluded at train time, but even pass19 still leaves `n3` and `n5` above `brux1` and keeps subject-level sensitivity at `0.000`. Pass20 then preserves another equally useful negative result: naive `mean` removal does not fix that bottleneck and instead makes `brux1` collapse. Pass21 narrows it one step further without changing the model recipe: the retained family is doing something real, but `sample_entropy` and `burst_fraction` still help the highest-score controls while `brux1`'s larger raw amplitude-envelope features remain net-negative under the learned coefficients. So the EMG-first bottleneck is now narrower still: preserve the pass19 retained family, then test normalization-aware extraction before any new threshold or model change.
