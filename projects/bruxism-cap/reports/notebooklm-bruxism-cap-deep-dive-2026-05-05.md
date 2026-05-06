# NotebookLM deep dive source: bruxism-cap newcomer briefing

Date: 2026-05-05
Project path: /home/hermes/work/ai-lab/projects/bruxism-cap
Audience: a new contributor who needs the fastest honest understanding of the project so far.

## 1. Executive summary

`bruxism-cap` is the active ai-lab biosignals project. It aims to build the smallest honest, reproducible bruxism-detection benchmark from the public PhysioNet CAP Sleep Database. The project is intentionally not trying to ship a clinical detector. Its main value is methodological: learning how to build an auditable signal pipeline, track leakage, compare misleading window-level results to subject-aware evaluation, and iterate on feature representations without fooling ourselves.

The current framing is EMG-first. `EMG1-EMG2` is the main channel under study, while `C4-P4` is kept as a comparison channel. The benchmark uses simple classical features and small models rather than deep learning because the key bottleneck is still data validity and cross-subject transfer, not model capacity.

The strongest current result is still mixed. The latest pass (`pass36`) shows that two earlier EMG representation improvements do compose honestly on the repaired scaffold, improving subject-level balanced accuracy to 0.750 and subject-level sensitivity to 0.500, but the gain is carried mainly by `brux2`; `brux1` still fails. So the project has made real progress without yet solving the benchmark.

## 2. Why this project exists

The project was chosen as a better first non-LLM lab branch because it is:
- open and reproducible
- small enough to run on the VPS or MacBook
- useful for learning EDF loading, channel inspection, feature extraction, annotation alignment, and leakage-aware evaluation
- concrete enough to produce artifact-rich iteration history

It also creates a future bridge toward privacy-preserving wearable EMG work, but that downstream branch is intentionally not the current benchmark claim.

## 3. Project goals

Primary goals:
- Build a tiny end-to-end benchmark from public data.
- Compare random-window CV against leave-one-subject-out (LOSO) CV.
- Learn whether any apparent bruxism signal survives held-out-subject transfer.
- Keep the benchmark honest enough that each change teaches something.

Non-goals for now:
- clinical performance claims
- deep learning or multimodal fusion
- custom hardware collection
- product-style wearable deployment

## 4. Dataset used and what it actually is

Main dataset:
- PhysioNet CAP Sleep Database (`capslpdb`)
- Current tiny working subset centers on `brux1`, `brux2`, `n3`, `n5`, `n10`, and `n11`
- Current valid annotation-aware subset usually excludes `n10` because its local EDF is truncated relative to the sidecar scoring file
- Labels are binary: `bruxism` vs `control`

Important dataset reality:
- CAP is a sleep-instability dataset, not a purpose-built bruxism benchmark.
- The public bruxism subset is tiny.
- The repo therefore treats this as a reproducible pilot and validity exercise, not definitive evidence.

Key channels:
- Primary benchmark channel: `EMG1-EMG2`
- Comparison channel: `C4-P4`

Typical extraction setup:
- fixed 30-second windows
- stage-aware filtering using RemLogic sidecar `.txt` files
- many passes focus on `SLEEP-S2`
- later passes narrow further using CAP overlap-event families such as `MCAP-A1` and `MCAP-A3`

## 5. Core methodology

The project repeatedly asks the same honest question on increasingly better-controlled scaffolds:
1. Which windows are we really allowed to compare?
2. Are the labels or annotations aligned with the actual local EDF signal?
3. Do random splits exaggerate performance?
4. Under LOSO, do bruxism subjects actually outrank controls at the subject level?
5. If not, is the next fix about extraction validity, representation, or interpretation?

The methodology evolved toward:
- annotation-aware extraction
- subject-level aggregation
- matched per-subject scaffolds
- timing-aware window selection
- channel-matched comparisons
- increasingly narrow feature-validity audits

## 6. Evolution of the project

### Phase A: pipeline shakeout and first leakage lesson
- `pass1` proved the extraction and baseline path worked.
- `pass2` produced the first valid 6-subject baseline.
- Random-window CV looked extremely strong while LOSO was much worse.
- This established the main methodological lesson: naive window-level validation is dangerously optimistic.

### Phase B: remove obvious measurement confounds
- `pass3` removed features like `n_samples` and `duration_s` that acted as sampling-rate proxies.
- This reduced random-split optimism slightly but did not fix held-out-subject failure.
- Lesson: removing one obvious confound does not rescue transfer if the broader measurement scaffold is still weak.

### Phase C: annotation-aware extraction and alignment audits
- `pass4` introduced sidecar-aware `SLEEP-S2` filtering.
- This made the pipeline more valid but performance got worse, not better.
- Alignment audits showed `n10` was unusable and `brux1` only partially usable because sidecar annotations extended beyond available local EDF duration.
- Lesson: better validity often lowers apparent performance, which is a good sign for benchmark honesty.

### Phase D: subject-level hardening and confound interpretation
- `pass5` added subject-level aggregation.
- Subject-level sensitivity fell to zero even when some window-level positives existed.
- `pass6` showed random-split optimism was not best explained by trivial subject-ID clustering alone; label separation looked stronger than subject separation in seen-subject pools, but it still did not transfer.
- Lesson: the problem is not just memorizing subjects. The class boundary itself is unstable across subjects.

### Phase E: event-overlap narrowing
- `pass7` required `SLEEP-S2` windows to overlap CAP micro-events.
- `pass8` audited overlap-family composition and showed the mixed `S2+MCAP` bucket was heterogeneous across subjects.
- `pass9` narrowed to `A3` overlap.
- `pass10` narrowed further to exclusive `A3-only` windows.
- `pass11` quantified how much each overlap rule changed availability by subject and label.
- Lesson: extraction-rule changes also change sampling surfaces, so semantic comparisons must be paired with availability audits.

### Phase F: matched-family and matched-channel comparisons
- `pass12` showed that on a matched scaffold, exclusive `A1-only` transferred better than matched `A3-only` for `C4-P4`.
- `pass13` tested the first EMG-first rerun on the strongest `A1-only` scaffold and it regressed relative to `C4-P4`.
- `pass14` showed EMG did a bit better under `A3-only` than `A1-only`, but still failed the honest subject-level criterion.
- `pass15` showed the issue was not threshold tuning; controls still outranked the best bruxism subject.
- `pass16` localized recurring problematic EMG features.

### Phase G: EMG feature surgery and negative-result accumulation
- `pass17` time-domain ablation failed.
- `pass18` envelope/burst replacement features shifted scores but did not rescue the benchmark.
- `pass19` selective EMG recipe recovered some window-level strength but still failed at the subject level.
- `pass20` mean ablation made things worse.
- `pass21` showed retained envelope-family features were real but still not cleanly bruxism-aligned.
- `pass22` median/MAD normalization also failed.
- Lesson: many plausible EMG tweaks do not help, and those negative results are central knowledge, not dead ends.

### Phase H: sharpen the failure surface and repair the scaffold
- `pass23` compared EMG against the honest C4 anchor and showed EMG improved `brux1` but collapsed `brux2`.
- `pass24` localized the decisive failure to a `brux2` vs `n3` reversal.
- `pass25` added shared time-position matching; both bruxism subjects improved but all controls still outranked them.
- `pass26` showed the stricter scaffold itself hurt `C4-P4` too, meaning not every failure is channel-specific.
- `pass27` showed strict time-position matching made `A1-only` infeasible.
- `pass28` repaired that with a percentile-band selector, restoring a usable 10-window-per-subject scaffold.
- `pass29` rebuilt the repaired scaffold on `C4-P4`, creating the current honest comparison anchor.
- `pass30` showed the repaired scaffold was genuinely timing-matched across channels.
- `pass31` showed the suspected narrow `n3`-favoring trio was real but incomplete.
- `pass32` and `pass33` showed broader or narrower morphology deletion alone was not the fix.

### Phase I: representation improvements that finally helped
- `pass34` record-relative feature scaling removed the `n3` false positive and fixed the `brux2` vs `n3` reversal, but still missed `brux1`.
- `pass35` compact shape features nearly closed the `n3 - brux1` gap and kept `brux2` above `n3`, but still left both bruxism subjects below threshold.
- A matched `C4-P4` comparator showed record-relative scaling was not a universal fix.
- `pass36` combined record-relative scaling with shape features on the repaired scaffold. The gains composed honestly, lifting subject-level balanced accuracy to 0.750 and subject-level sensitivity to 0.500.
- Remaining problem: `brux1` still fails, so the project is better but not solved.

## 7. Most important lessons learned

1. Random-window CV is not the truth surface.
   It repeatedly looked excellent while honest subject-level generalization remained poor.

2. Better validity often makes the benchmark look worse first.
   Annotation-aware extraction and tighter scaffolds commonly reduced apparent performance.

3. Negative results are first-class assets.
   The project has learned as much from failed ablations and failed normalization ideas as from successful passes.

4. Sampling-surface changes must be audited explicitly.
   Event-family filters, time-position rules, and subject caps all alter the data distribution.

5. EMG is not a lost cause, but it is fragile.
   The newer passes show genuine EMG-specific signals can be recovered, yet only under carefully repaired scaffolds and still not for all subjects.

6. The current bottleneck is localized, not vague.
   The repo now knows the remaining failure is concentrated around subject-level threshold-crossing sensitivity, especially `brux1`, rather than generic pipeline chaos.

## 8. Current state of the benchmark

Best current benchmark reading:
- The project should remain CAP-based, EMG-first, and leakage-aware.
- `pass29 C4-P4` is still the honest comparison anchor on the repaired scaffold.
- `pass36` is the best current EMG composition result.
- The benchmark is improved enough to support one more small, interpretable question.

Current honest conclusion:
- Real progress exists.
- No clinical or product claim is justified.
- The benchmark is still tiny, fragile, and dominated by subject-specific instability.

## 9. Limitations and critique

Methodological limitations:
- extremely small number of subjects
- only two bruxism subjects in the tiny working subset
- CAP is not a dedicated bruxism benchmark
- binary labels simplify a more complex phenomenon
- one-night PSG-derived records do not match the multi-night wearable setting emphasized by newer literature

Data limitations:
- local EDF / sidecar mismatches exist (`n10` unusable, `brux1` partially usable)
- some runs depend on tight selection scaffolds with only 10 windows per subject
- subject-level results can swing heavily from one subject's behavior

Modeling limitations:
- classical features may miss richer morphology or temporal context
- the project intentionally avoids deep learning for now, so ceiling is limited
- feature-engineering choices can easily encode non-generalizing artifacts

Interpretation critique a newcomer should keep in mind:
- This benchmark is better read as a scientific debugging object than as an applied detector.
- Improvement from 0.000 to 0.500 subject sensitivity on a tiny repaired scaffold is promising but not robust proof.
- `brux2` recovery alone can make a pass look much better while the project still fails the more important “both bruxism subjects transfer” criterion.

## 10. Why the current framing still makes sense

A fresh translational review did not invalidate the project frame. The field is indeed moving toward wearable, multi-night, intervention-aware EMG. But there is still no clearly better open benchmark than CAP for this repo right now.

So the correct stance is:
- keep `EMG1-EMG2` as the primary scientific direction
- keep CAP as the bounded open benchmark
- keep validity caveats explicit
- avoid pretending the benchmark already matches product-shaped wearable science

## 11. Best next steps

Highest-value next step:
- stay on the repaired five-subject percentile-band `A1-only` scaffold
- localize why `brux1` still fails under the pass36 composition result
- prefer one bounded audit over another broad feature-family expansion

Good improvement ideas:
- subject-specific post-hoc audit focused on `brux1` versus nearest controls
- inspect which pass36 feature contributions remain net-negative for `brux1`
- test whether `brux1` failure is tied more to annotation coverage, timing, or representation than to threshold choice
- preserve `pass29` and `pass36` as the main comparison pair for future reasoning

Ideas to defer until the benchmark is more stable:
- privacy-preserving wearable EMG branch
- intervention-aware or multi-night framing
- LLM/RL or synthetic-data branches
- deep learning / multimodal fusion

## 12. Questions a newcomer should ask first

- Which scaffold is currently considered the fairest one, and why?
- Why is `pass29 C4-P4` still the honest anchor even after EMG improvements?
- What exactly improved from `pass34` to `pass35` to `pass36`?
- Why does `brux1` remain the bottleneck?
- Which negative results should never be forgotten before proposing a new idea?
- Which changes altered the data distribution versus the representation only?

## 13. Suggested NotebookLM prompt topics

- Explain the full evolution from pass1 to pass36 as a sequence of tightening validity controls.
- Compare `pass29`, `pass34`, `pass35`, and `pass36` for a newcomer.
- Summarize the strongest lessons about leakage, subject-aware evaluation, and negative results.
- Critique the benchmark as if reviewing it for a methods-focused workshop.
- Propose a disciplined next-step plan that does not over-claim from the current result.

## 14. Key source files for this briefing

- `/home/hermes/work/ai-lab/projects/bruxism-cap/README.md`
- `/home/hermes/work/ai-lab/projects/bruxism-cap/data/README.md`
- `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/first-baseline.md`
- `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/campaign-handoff-2026-05-05.md`
- `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/periodic-translational-framing-check-2026-05-05.md`
- `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/pass35-patched-emg-vs-matched-c4-anchor-comparison.md`
- `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit.md`
- `/home/hermes/work/ai-lab/wiki/concepts/bruxism-cap.md`
- `/home/hermes/work/ai-lab/wiki/queries/bruxism-cap-campaign-handoff-2026-05-05.md`

## Appendix: raw excerpts used to prepare this briefing


SOURCE: /home/hermes/work/ai-lab/projects/bruxism-cap/README.md
     1|# bruxism-cap
     2|
     3|Minimal starter scaffold for **bruxism detection from EEG / EMG signals** using the public **PhysioNet CAP Sleep Database**.
     4|
     5|This is intentionally a **small reproduction / benchmarking project**, not a clinical detector.
     6|
     7|## Project goal
     8|
     9|Build the smallest honest EMG-first baseline that can:
    10|- load a tiny CAP subset (`brux1`, `brux2`, plus a few controls)
    11|- extract one jaw-muscle-aligned signal channel into fixed windows
    12|- compute classical handcrafted features
    13|- train simple models
    14|- compare **leaky random window splits** vs **subject-aware splits**
    15|
    16|## Why this project exists
    17|
    18|The ai-lab research pass found that the easiest credible starting point is:
    19|- one public dataset
    20|- one channel family
    21|- one binary task
    22|- classical models
    23|- subject-aware evaluation
    24|
    25|CAP is not a purpose-built bruxism benchmark, but it is openly accessible and already used by recent bruxism papers. That makes it good enough for a first reproducible pilot.
    26|
    27|A periodic translational literature check on `2026-05-05` did not overturn that framing. The newer science is more wearable-, multi-night-, and intervention-oriented, but it still does not expose a clearly better open benchmark than CAP. So the repo should stay EMG-first and validity-focused here, while treating portable/home/intervention EMG as a future branch rather than an immediate benchmark pivot.
    28|
    29|## Scope for version 1
    30|
    31|**Do now**
    32|- reproduce a tiny EMG-first window-classification baseline
    33|- keep the task binary: `bruxism` vs `control`
    34|- treat `EMG1-EMG2` as the primary starting channel and `C4-P4` as the comparison channel
    35|- report balanced accuracy, sensitivity, specificity, and AUROC
    36|- report the gap between random window CV and leave-one-subject-out CV
    37|
    38|**Do not do yet**
    39|- deep learning
    40|- multimodal fusion
    41|- clinical claims
    42|- custom hardware collection
    43|
    44|## Folder layout
    45|
    46|- `data/README.md` — raw-data and manifest notes
    47|- `data/subject_manifest.example.csv` — starter manifest format
    48|- `notebooks/00_cap_subset_inspection.ipynb` — first inspection notebook stub
    49|- `src/features.py` — handcrafted window features
    50|- `src/prepare_windows.py` — EDF -> feature CSV pipeline
    51|- `src/train_baseline.py` — baseline training with random vs LOSO CV
    52|- `src/eval.py` — comparison helper for saved metric JSON files
    53|- `reports/first-baseline.md` — experiment checklist / artifact template
    54|
    55|## Environment
    56|
    57|Bootstrap the repo if needed:
    58|
    59|```bash
    60|cd /home/hermes/work/ai-lab
    61|./scripts/bootstrap-python.sh
    62|source .venv/bin/activate
    63|uv pip install -e '.[biosignals]'
    64|```
    65|
    66|The `biosignals` extra is intentionally optional so the main Unsloth/Modal workflow stays lightweight.
    67|
    68|## Step 1: download a tiny CAP subset
    69|
    70|```bash
    71|cd /home/hermes/work/ai-lab
    72|mkdir -p projects/bruxism-cap/data/raw/capslpdb
    73|cd projects/bruxism-cap/data/raw/capslpdb
    74|
    75|wget -nc https://physionet.org/files/capslpdb/1.0.0/brux1.edf
    76|wget -nc https://physionet.org/files/capslpdb/1.0.0/brux2.edf
    77|wget -nc https://physionet.org/files/capslpdb/1.0.0/n3.edf
    78|wget -nc https://physionet.org/files/capslpdb/1.0.0/n5.edf
    79|wget -nc https://physionet.org/files/capslpdb/1.0.0/n10.edf
    80|wget -nc https://physionet.org/files/capslpdb/1.0.0/n11.edf
    81|```
    82|
    83|These controls mirror the small compatible-control set described in one of the recent single-channel EEG papers. If channel availability differs, swap them for other healthy controls.
    84|
    85|## Step 2: inspect channel names first
    86|
    87|```bash
    88|python3 projects/bruxism-cap/src/prepare_windows.py \
    89|  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
    90|  --list-channels
    91|```
    92|
    93|The exact channel name may differ by record. For the current EMG-first pivot, start with `EMG1-EMG2` as the primary channel and use `C4-P4` as the main comparison channel when both are present.
    94|
    95|## Step 3: build a feature CSV
    96|
    97|Example for one record:
    98|
    99|```bash
   100|python3 projects/bruxism-cap/src/prepare_windows.py \
   101|  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
   102|  --subject-id brux1 \
   103|  --label bruxism \
   104|  --channel EMG1-EMG2 \
   105|  --window-seconds 30 \
   106|  --limit-windows 120 \
   107|  --out projects/bruxism-cap/data/window_features.csv
   108|```
   109|
   110|Append more records with `--append`:
   111|
   112|```bash
   113|python3 projects/bruxism-cap/src/prepare_windows.py \
   114|  --edf projects/bruxism-cap/data/raw/capslpdb/n3.edf \
   115|  --subject-id n3 \
   116|  --label control \
   117|  --channel EMG1-EMG2 \
   118|  --window-seconds 30 \
   119|  --limit-windows 120 \
   120|  --append \
   121|  --out projects/bruxism-cap/data/window_features.csv
   122|```
   123|
   124|## Step 4: train a baseline
   125|
   126|Current tracked first-run artifacts in this repo:
   127|- `projects/bruxism-cap/data/window_features_pass1.csv` — 3-subject pilot used to validate the pipeline
   128|- `projects/bruxism-cap/data/window_features_pass2.csv` — first 6-subject feature table with `20` windows per subject from the first `600` seconds
   129|- `projects/bruxism-cap/reports/random-window-cv-pass2.json` and `loso-cv-pass2.json` — first valid 6-subject baseline
   130|- `projects/bruxism-cap/reports/random-window-cv-pass3-nosfreq.json` and `loso-cv-pass3-nosfreq.json` — same data after excluding obvious sampling-rate proxy features from training
   131|- `projects/bruxism-cap/data/window_features_pass4_s2.csv` — first annotation-aware feature table using `SLEEP-S2` windows only on the stage-valid 5-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`)
   132|- `projects/bruxism-cap/reports/random-window-cv-pass4-s2.json` and `loso-cv-pass4-s2.json` — pass4 rerun on the annotation-aware `S2` subset
   133|- `projects/bruxism-cap/reports/annotation-alignment-audit-pass4-s2.md` — per-subject EDF versus sidecar audit explaining why `n10` was excluded and why `brux1` is only partially usable for `SLEEP-S2`
   134|- `projects/bruxism-cap/reports/loso-cv-pass5-pass2-subjectagg.json` and `loso-cv-pass5-pass4-s2-subjectagg.json` — measurement-hardened LOSO reruns that preserve the original window metrics but also aggregate predictions to one verdict per held-out subject
   135|- `projects/bruxism-cap/src/audit_subject_confound.py`, `projects/bruxism-cap/reports/subject-confound-audit-pass6.json`, and `subject-confound-audit-pass6.md` — a bounded pass6 audit checking whether the current feature tables separate windows more by subject or by label
   136|- `projects/bruxism-cap/data/window_features_pass7_s2_mcap.csv`, `projects/bruxism-cap/reports/random-window-cv-pass7-s2-mcap.json`, `loso-cv-pass7-s2-mcap.json`, and `pass7-s2-mcap-overlap.md` — a pass7 rerun that keeps only `SLEEP-S2` windows overlapping CAP micro-events (`MCAP-A1`, `MCAP-A2`, `MCAP-A3`)
   137|- `projects/bruxism-cap/src/audit_overlap_event_mix.py`, `projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.json`, and `overlap-event-mix-audit-pass8.md` — a bounded pass8 audit showing that the kept `S2+MCAP` subset mixes materially different CAP overlap-event families across subjects (for example `brux2` is mostly `A3` while `n5` is mostly `A1`)
   138|- `projects/bruxism-cap/data/window_features_pass9_s2_mcap_a3.csv`, `projects/bruxism-cap/reports/random-window-cv-pass9-s2-mcap-a3.json`, `loso-cv-pass9-s2-mcap-a3.json`, and `pass9-s2-mcap-a3.md` — a pass9 rerun that narrows the overlap rule to `SLEEP-S2` windows with `MCAP-A3` overlap only
   139|- `projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv`, `projects/bruxism-cap/reports/random-window-cv-pass10-s2-mcap-a3-only.json`, `loso-cv-pass10-s2-mcap-a3-only.json`, and `pass10-s2-mcap-a3-only.md` — a pass10 rerun that keeps only `SLEEP-S2` windows with `MCAP-A3` overlap and excludes simultaneous `MCAP-A1` / `MCAP-A2` overlap
   140|- `projects/bruxism-cap/src/audit_rule_survival.py`, `projects/bruxism-cap/reports/rule-survival-audit-pass11.json`, and `projects/bruxism-cap/reports/pass11-rule-survival-audit.md` — a bounded pass11 validity audit showing how aggressively each overlap rule changes per-subject and per-label window availability before any model is rerun
   141|- `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a1_only_matched14.csv`, `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a3_only_matched14.csv`, `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a1-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json`, `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a3-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a3-only-matched14.json`, and `projects/bruxism-cap/reports/pass12-exclusive-a1-vs-a3-matched14.md` — a pass12 matched-family comparison showing that exclusive `S2 + A1-only` transfers better than matched exclusive `S2 + A3-only`, but still misses one held-out bruxism subject
   142|- `projects/bruxism-cap/data/window_features_pass13_emg_s2_mcap_a1_only_matched14.csv`, `projects/bruxism-cap/reports/random-window-cv-pass13-emg-s2-mcap-a1-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass13-emg-s2-mcap-a1-only-matched14.json`, and `projects/bruxism-cap/reports/pass13-emg-vs-c4-a1-only-matched14.md` — a pass13 matched channel comparison showing that the first `EMG1-EMG2` rerun on the strongest current `A1-only` scaffold regressed the honest baseline relative to `C4-P4`
   143|- `projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv`, `projects/bruxism-cap/reports/random-window-cv-pass14-emg-s2-mcap-a3-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json`, and `projects/bruxism-cap/reports/pass14-emg-a1-vs-a3-matched14.md` — a pass14 matched EMG-family comparison showing that `A3-only` improves `EMG1-EMG2` relative to matched `A1-only` on window-level LOSO, but still leaves subject-level bruxism sensitivity at `0.000`
   144|- `projects/bruxism-cap/src/audit_subject_thresholds.py`, `projects/bruxism-cap/reports/subject-threshold-audit-pass15-emg-a3-vs-c4-a1.json`, and `projects/bruxism-cap/reports/pass15-emg-a3-threshold-audit.md` — a pass15 threshold audit showing that the stronger `EMG1-EMG2 A3-only` run fails because two controls still outrank the best bruxism subject, so threshold tuning alone cannot rescue the honest baseline
   145|- `projects/bruxism-cap/src/audit_emg_feature_validity.py`, `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.json`, and `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.md` — a pass16 EMG-first validity audit showing that the same `A3-only` ranking failure is being driven by a recurring high-score-control feature family (`ratio_alpha_delta`, `min`, `sample_entropy`) while `brux1` is dominated by extreme absolute-power / mean terms, narrowing the next patch to one small EMG feature ablation
   146|- `projects/bruxism-cap/reports/random-window-cv-pass17-emg-a3-timeonly-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass17-emg-a3-timeonly-matched14.json`, and `projects/bruxism-cap/reports/pass17-emg-a3-timeonly-ablation.md` — a pass17 matched time-domain ablation showing that simply dropping the spectral / ratio family does not rescue the honest EMG-first baseline and slightly worsens the best LOSO window-level result
   147|- `projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv`, `projects/bruxism-cap/reports/random-window-cv-pass18-emg-a3-envelope-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass18-emg-a3-envelope-matched14.json`, `projects/bruxism-cap/reports/pass18-emg-a3-envelope-replacement.md`, and `projects/bruxism-cap/reports/feature-validity-audit-pass18-emg-a3-envelope-logreg.md` — a pass18 replacement-oriented EMG rerun showing that adding one compact rectified-envelope / burst family slightly reshapes subject scores but still does not rescue the honest EMG-first baseline or beat the stronger pass14 window-level LOSO result
   148|- `projects/bruxism-cap/reports/random-window-cv-pass19-emg-a3-envelope-selected-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json`, and `projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md` — a pass19 selection-aware EMG rerun showing that the pass18 envelope / burst family works better when spectral / ratio features are excluded at train time, but still does not rescue the honest subject-level baseline
   149|- `projects/bruxism-cap/reports/random-window-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`, and `projects/bruxism-cap/reports/pass20-emg-a3-envelope-selected-nomean-matched14.md` — a pass20 mean-ablation rerun showing that once the spectral / ratio family is already excluded, naive raw-`mean` removal makes `brux1` much worse without lowering the two highest-score controls
   150|- `projects/bruxism-cap/src/audit_emg_envelope_family.py`, `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.json`, and `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.md` — a pass21 retained-family audit showing that the pass19 envelope / burst working point is real but still not cleanly bruxism-aligned: `sample_entropy` and `burst_fraction` still lift controls while `rectified_mean`, `envelope_mean`, and `p95_abs` remain net-negative on `brux1`
   151|- `projects/bruxism-cap/data/window_features_pass22_emg_s2_mcap_a3_only_matched14_medianmad.csv`, `projects/bruxism-cap/reports/random-window-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`, and `projects/bruxism-cap/reports/pass22-emg-a3-envelope-selected-medianmad-matched14.md` — a pass22 normalization-aware EMG rerun showing that robust per-window `median_mad` normalization makes the stronger pass19 EMG working point worse rather than better: the best LOSO window-level result regresses and both bruxism subjects rank even lower
   152|- `projects/bruxism-cap/src/compare_subject_score_surfaces.py`, `projects/bruxism-cap/reports/subject-score-comparison-pass23-emg-pass19-vs-c4-pass12.json`, and `projects/bruxism-cap/reports/pass23-emg-pass19-vs-c4-pass12-subject-score-comparison.md` — a pass23 benchmark-clarity comparison showing that the stronger pass19 EMG working point improves `brux1` versus the honest pass12 `C4-P4 A1-only` anchor but still loses decisively overall because `brux2` collapses and `n3` becomes the highest-score control
   153|- `projects/bruxism-cap/src/audit_emg_brux2_n3_gap.py`, `projects/bruxism-cap/reports/feature-validity-audit-pass24-emg-brux2-vs-n3.json`, and `feature-validity-audit-pass24-emg-brux2-vs-n3.md` — a pass24 focused EMG validity audit showing that the strongest remaining failure is the `brux2`-below-`n3` reversal, with `zero_crossing_rate` as the largest surviving control-favoring feature gap and unmatched time position as the next extraction-validity question
   154|- `projects/bruxism-cap/src/select_time_position_matched_windows.py`, `projects/bruxism-cap/data/window_features_pass25_emg_s2_mcap_a3_only_full_envelope.csv`, `projects/bruxism-cap/data/window_features_pass25_emg_s2_mcap_a3_only_timepos10_envelope.csv`, `projects/bruxism-cap/reports/time-position-match-pass25-emg-a3.json`, `projects/bruxism-cap/reports/random-window-cv-pass25-emg-a3-timepos10-selected.json`, `projects/bruxism-cap/reports/loso-cv-pass25-emg-a3-timepos10-selected.json`, and `projects/bruxism-cap/reports/pass25-emg-a3-time-position-matched-selected.md` — a pass25 shared-time-position rerun showing that absolute time-position matching is only feasible at `10` windows per subject on the current verified subset, improves both bruxism subjects relative to pass19, but still leaves all controls above both bruxism subjects and does not beat the honest EMG baseline
   155|- `projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_full_envelope.csv`, `projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_timepos10_envelope.csv`, `projects/bruxism-cap/reports/time-position-match-pass26-c4-a3.json`, `projects/bruxism-cap/reports/random-window-cv-pass26-c4-a3-timepos10-selected.json`, `projects/bruxism-cap/reports/loso-cv-pass26-c4-a3-timepos10-selected.json`, and `projects/bruxism-cap/reports/pass26-c4-a3-time-position-matched-vs-emg.md` — a pass26 matched strict-scaffold comparison showing that rebuilding the exact same shared-time-position `A3-only` subset on `C4-P4` does not rescue the benchmark and actually underperforms matched `EMG1-EMG2` on the honest LOSO surface
   156|- `projects/bruxism-cap/data/window_features_pass27_emg_s2_mcap_a1_only_full_envelope.csv`, `projects/bruxism-cap/data/window_features_pass27_emg_s2_mcap_a1_only_timepos2_envelope.csv`, `projects/bruxism-cap/reports/time-position-match-pass27-emg-a1.json`, and `projects/bruxism-cap/reports/pass27-emg-a1-time-position-feasibility.md` — a pass27 extraction-validity audit showing that the same strict shared-time-position rule collapses `EMG1-EMG2 A1-only` to only `2` windows per subject, so the next timing-aware rerun needs a softer selector before another LOSO benchmark is trusted
   157|- `projects/bruxism-cap/src/select_time_position_matched_windows.py`, `projects/bruxism-cap/src/train_baseline.py`, `projects/bruxism-cap/data/window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`, `projects/bruxism-cap/reports/time-position-match-pass28-emg-a1-pct10-90.json`, `projects/bruxism-cap/reports/random-window-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`, `projects/bruxism-cap/reports/loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`, and `projects/bruxism-cap/reports/pass28-emg-a1-percentile-band-rerun.md` — a pass28 softer-timing-control rerun showing that a percentile-band selector restores a usable `EMG1-EMG2 A1-only` scaffold (`10` windows per subject instead of `2`) but still leaves honest LOSO subject-level sensitivity at `0.000`
   158|- `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_full_envelope.csv`, `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`, `projects/bruxism-cap/reports/time-position-match-pass29-c4-a1-pct10-90.json`, `projects/bruxism-cap/reports/random-window-cv-pass29-c4-a1-pct10-90-timepos10-selected.json`, `projects/bruxism-cap/reports/loso-cv-pass29-c4-a1-pct10-90-timepos10-selected.json`, and `projects/bruxism-cap/reports/pass29-c4-a1-percentile-band-vs-emg.md` — a pass29 matched-channel comparison showing that rebuilding the exact same repaired `A1-only` percentile-band scaffold on `C4-P4` clearly beats matched `EMG1-EMG2` on honest LOSO, but still only ties the older best subject-level baseline because `brux1` remains below `n3`
   159|- `projects/bruxism-cap/src/audit_percentile_band_channel_gap.py`, `projects/bruxism-cap/reports/feature-validity-audit-pass30-a1-pct-channel-gap.json`, and `projects/bruxism-cap/reports/pass30-a1-percentile-band-channel-gap-audit.md` — a pass30 cross-channel validity audit showing that the repaired `A1-only` percentile-band scaffold is truly timing-matched across `EMG1-EMG2` and `C4-P4`, that `brux1` still trails `n3` under both channels, and that the main channel gap is now `brux2`: `C4-P4` flips `brux2` strongly above `n3` while EMG leaves it far below
   160|- `projects/bruxism-cap/src/audit_percentile_band_n3_family_recurrence.py`, `projects/bruxism-cap/reports/feature-validity-audit-pass31-a1-pct-n3-family.json`, and `projects/bruxism-cap/reports/pass31-a1-percentile-band-n3-family-recurrence.md` — a pass31 recurrence audit showing that the suspected narrow `n3`-favoring trio (`sample_entropy`, `burst_fraction`, `envelope_cv`) is real but not sufficient: on the repaired scaffold, the harsher EMG `n3` advantage is still driven mainly by broader morphology terms such as `mean`, `max`, `ptp`, and `zero_crossing_rate`, so a trio-only ablation would be under-justified
   161|- `projects/bruxism-cap/src/run_pass32_broad_morphology_ablation.py`, `projects/bruxism-cap/reports/loso-cv-pass32-emg-a1-pct10-90-broad-ablation.json`, `projects/bruxism-cap/reports/loso-cv-pass32-c4-a1-pct10-90-broad-ablation.json`, and `projects/bruxism-cap/reports/pass32-broad-morphology-ablation.md` — a pass32 matched broader-ablation rerun showing that removing the wider control-favoring morphology family is too destructive: `EMG1-EMG2` still misses both bruxism subjects while `C4-P4` loses its earlier `brux2` recovery, so the result should be preserved as a negative ablation rather than promoted as a new baseline
   162|- `projects/bruxism-cap/src/run_pass33_raw_location_ablation.py`, `projects/bruxism-cap/reports/loso-cv-pass33-emg-a1-pct10-90-rawloc-ablation.json`, `projects/bruxism-cap/reports/loso-cv-pass33-c4-a1-pct10-90-rawloc-ablation.json`, and `projects/bruxism-cap/reports/pass33-raw-location-ablation.md` — a pass33 smaller raw-location ablation showing that removing only `mean`, `min`, and `max` is not the fix either: `C4-P4` stays essentially unchanged, but `EMG1-EMG2` gets markedly worse because `brux1` collapses while `n3` stays high
   163|- `projects/bruxism-cap/src/run_pass34_record_relative_emg_audit.py`, `projects/bruxism-cap/data/window_features_pass34_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative.csv`, `projects/bruxism-cap/reports/loso-cv-pass34-emg-a1-pct10-90-record-relative.json`, and `projects/bruxism-cap/reports/pass34-record-relative-emg-audit.md` — a pass34 record-relative representation audit showing that within-record robust feature scaling removes the `n3` false positive and flips `brux2 - n3` positive, but still leaves `brux1` below threshold so subject-level sensitivity remains `0.000`
   164|- `projects/bruxism-cap/src/features.py`, `projects/bruxism-cap/src/run_pass35_shape_feature_expansion.py`, `projects/bruxism-cap/data/window_features_pass35_emg_s2_mcap_a1_only_full_envelope_shape.csv`, `projects/bruxism-cap/data/window_features_pass35_emg_s2_mcap_a1_only_pct10_90_timepos10_shape.csv`, `projects/bruxism-cap/reports/time-position-match-pass35-emg-a1-pct10-90-shape.json`, `projects/bruxism-cap/reports/loso-cv-pass35-emg-a1-pct10-90-shape.json`, and `projects/bruxism-cap/reports/pass35-shape-feature-expansion.md` — a pass35 compact shape-feature expansion showing that the repaired scaffold can be rebuilt exactly with four new shape descriptors, sharply reducing both the `n3 - brux1` and `brux2 - n3` gaps, but still not enough to push either bruxism subject above threshold at the subject level
   165|- `projects/bruxism-cap/src/run_pass36_record_relative_shape_composition_audit.py`, `projects/bruxism-cap/data/window_features_pass36_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape.csv`, `projects/bruxism-cap/reports/loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json`, and `projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit.md` — a pass36 composition audit showing that the pass34 record-relative and pass35 compact-shape gains do compose honestly on the repaired scaffold, lifting subject-level balanced accuracy to `0.750` and sensitivity to `0.500` via a strong `brux2` recovery, but still leaving `brux1` below threshold
   166|
   167|Leakage-prone reference split:
   168|
   169|```bash
   170|python3 projects/bruxism-cap/src/train_baseline.py \
   171|  --features-csv projects/bruxism-cap/data/window_features.csv \
   172|  --cv random \
   173|  --out projects/bruxism-cap/reports/random-window-cv.json
   174|```
   175|
   176|Subject-aware split:
   177|
   178|```bash
   179|python3 projects/bruxism-cap/src/train_baseline.py \
   180|  --features-csv projects/bruxism-cap/data/window_features.csv \
   181|  --cv loso \
   182|  --out projects/bruxism-cap/reports/loso-cv.json
   183|```
   184|
   185|Compare the two:
   186|
   187|```bash
   188|python3 projects/bruxism-cap/src/eval.py \
   189|  projects/bruxism-cap/reports/random-window-cv.json \
   190|  projects/bruxism-cap/reports/loso-cv.json
   191|```
   192|
   193|## Success criterion for the first pass
   194|
   195|A successful first pass is **not** “95% accuracy.”
   196|
   197|It is:
   198|- a reproducible raw-data subset
   199|- a feature CSV that can be regenerated
   200|- one honest baseline report
   201|- a clear comparison between leaky and subject-aware evaluation
   202|
   203|## Current status after the first runs
   204|
   205|The first real runs now exist and they should be read as a measurement lesson, not a success claim:
   206|- random-window CV stayed extremely high even after removing an obvious sampling-rate proxy feature
   207|- a first annotation-aware rerun on `SLEEP-S2` windows (`pass4`) still kept random CV unrealistically perfect while LOSO regressed further
   208|- `n10` could not be kept in the stage-aware subset because its local EDF is only about `63` minutes long while the sidecar scoring file continues far beyond the available signal, leaving no in-range `SLEEP-S2` windows
   209|- a follow-up alignment audit showed that `brux1` is only partially usable for `SLEEP-S2` locally because many later scored stage rows also exceed the EDF duration
   210|- a follow-up subject-level LOSO aggregation pass (`pass5`) showed that the weak window-level bruxism sensitivity was still flattering the situation: at the subject verdict level, every tested model predicted **zero** held-out bruxism subjects correctly on both the pass3 and pass4 datasets
   211|- a bounded subject-versus-label confound audit (`pass6`) showed that the current handcrafted feature tables are actually **more separable by label than by subject within random window splits**, so the next bottleneck is not just trivial subject-ID clustering; it is a label boundary that does not survive held-out-subject transfer
   212|- a follow-up overlap-event mix audit (`pass8`) showed that the current `S2+MCAP` subset itself is heterogeneous: some subjects are dominated by `MCAP-A3` overlap while others are dominated by `MCAP-A1`, so the next extraction test should be a narrower single-family overlap rule rather than another mixed-event bucket
   213|- a new single-family rerun (`pass9`) narrowed the overlap rule to `MCAP-A3`, which reduced random-window CV from perfect to about `0.921` balanced accuracy but still failed to improve honest transfer: the best LOSO balanced accuracy fell to `0.550` and subject-level bruxism sensitivity stayed `0.000`
   214|- a stricter exclusive-`A3` rerun (`pass10`) then excluded simultaneous `MCAP-A1` / `MCAP-A2` overlap from the kept `SLEEP-S2` windows, making the extraction rule more auditable but not more transferable: random-window balanced accuracy fell slightly further to about `0.908`, the best LOSO balanced accuracy fell again to `0.500`, and subject-level bruxism sensitivity still stayed `0.000`
   215|- a bounded rule-survival audit (`pass11`) then showed why these overlap-filter comparisons need explicit bookkeeping: the bruxism pool keeps `32.1%` of its pass4 `S2` windows under the exclusive-`A3` rule, while the control pool keeps only `15.2%`; `brux2` alone still has `111` eligible exclusive-`A3` windows, but `n5` falls to only `38`
   216|- a matched-family comparison (`pass12`) then showed that the overlap-family choice itself matters under fairer conditions: when both exclusive families are capped to the same `14` windows per subject on the same 5-subject subset, `A1-only` reaches subject-level LOSO balanced accuracy `0.750` with sensitivity `0.500`, while matched `A3-only` still stays at `0.000` subject-level bruxism sensitivity across models
   217|- a first matched EMG-versus-C4 comparison (`pass13`) then tested the new EMG-first framing on that same `A1-only` scaffold and preserved a negative result: `EMG1-EMG2` fell back to LOSO balanced accuracy `0.543` with subject-level sensitivity `0.000`, so it did not beat the current matched `C4-P4` anchor and missed both held-out bruxism subjects
   218|- a matched EMG-family comparison (`pass14`) then tested whether EMG prefers a different overlap family on the same scaffold: exclusive `A3-only` improved EMG LOSO balanced accuracy to `0.629` and reduced several control mean scores, but subject-level sensitivity still stayed `0.000`, so the result is still a validity note rather than a new honest baseline
   219|- a compact threshold audit (`pass15`) then showed that the stronger `EMG1-EMG2 A3-only` run cannot be rescued by lowering the subject threshold alone: two controls still outrank the best bruxism subject, so the next bottleneck is score ordering / feature validity rather than threshold choice
   220|- a compact feature-validity audit (`pass16`) then localized that EMG score-ordering failure more tightly: `n3` and `n5` still outrank `brux1`, the same high-score controls repeatedly surface `ratio_alpha_delta`, `min`, and `sample_entropy` as positive contributors, and `brux1` is dominated by extreme absolute-power / mean terms
   221|
   222|So the next correct step is still to improve extraction / evaluation validity before trying larger models or modality fusion, but the repo now has a sharper lesson than before: generic in-dataset label separation is easy, cross-subject transfer is the real failure surface, and overlap-family choice matters under matched conditions. Exclusive `A1-only` currently looks more transferable than exclusive `A3-only` for `C4-P4`, while `EMG1-EMG2` looks less bad under exclusive `A3-only` than under exclusive `A1-only`. The threshold audit then showed that no subject threshold rescues the stronger EMG run without collapsing specificity, because two controls still outrank the best bruxism subject. The new feature-validity audit narrowed the next move one step further: on the fixed pass14 scaffold, the high-score controls repeatedly benefit from `ratio_alpha_delta`, `min`, and `sample_entropy`, while `brux1` is dragged by extreme absolute-power / mean terms. The new pass17 time-domain ablation then preserved an equally important negative result: simply deleting the spectral / ratio family is not enough, because honest subject-level sensitivity still stays `0.000`, the best LOSO window-level result regresses slightly, and `n3` becomes even harder to separate. Pass18 then tested the complementary replacement idea and preserved the same overall verdict: adding one compact rectified-envelope / burst family slightly improves `brux1` and `brux2` versus pass17 and lowers `n3`, but it still leaves `n5` above `brux1`, keeps subject-level sensitivity at `0.000`, and still trails the stronger pass14 EMG LOSO result. Pass19 refined that one step further: the pass18 EMG family works better when the older spectral / ratio family is excluded at train time, recovering LOSO balanced accuracy `0.629`, but the honest subject-level verdict still stays flat at `0.000` sensitivity because `n3` and `n5` still outrank `brux1`. The next bounded move should therefore keep the selection-aware EMG recipe... [truncated]
   223|
   224|## Annotation-aware extraction example
   225|
   226|To build stage-aware windows from RemLogic sidecar exports, point `prepare_windows.py` at the matching `.txt` file and select the sleep event to keep:
   227|
   228|```bash
   229|python3 projects/bruxism-cap/src/prepare_windows.py \
   230|  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
   231|  --annotation-txt projects/bruxism-cap/data/raw/capslpdb/brux1.txt \
   232|  --annotation-events SLEEP-S2 \
   233|  --subject-id brux1 \
   234|  --label bruxism \
   235|  --channel EMG1-EMG2 \
   236|  --window-seconds 30 \
   237|  --limit-windows 20 \
   238|  --out projects/bruxism-cap/data/window_features_pass4_s2.csv
   239|```
   240|
   241|## Where to extend next
   242|
   243|After this scaffold works, the next sensible directions are:
   244|1. keep future stage-aware reruns restricted to subjects whose chosen events are verified in-range by the audit
   245|2. preserve the new rule-survival audit when reading pass7/pass9/pass10 so event-family comparisons are not mistaken for like-for-like sampling changes
   246|3. audit why `brux1` still fails under the stronger matched `S2 + A1-only` rule and whether the apparent gain over `A3-only` is threshold-fragile or reflects a broader ranking improvement
   247|4. preserve the matched-family comparison alongside the new threshold audit before testing any new overlap family
   248|5. preserve the new pass19 selection-aware EMG rerun as the stronger current EMG-first working point
   249|6. preserve the new pass20 mean-ablation rerun as evidence that naive raw-`mean` removal makes `brux1` much worse without lowering `n3` or `n5`
   250|7. preserve the new pass21 retained-family audit as evidence that the next EMG-only move should be normalization-aware extraction rather than more blind feature deletion
   251|8. preserve the new pass22 normalization-aware rerun as evidence that simple per-window `median_mad` normalization is **not** that fix: it makes the stronger pass19 EMG working point worse and pushes both bruxism subjects lower
   252|9. preserve the new pass23 shared subject-score comparison as evidence that the current EMG gap is now concentrated in `brux2` collapse plus `n3` as the dominant control, not in a vague overall underperformance story
   253|10. preserve the new pass24 focused gap audit as evidence that the current EMG failure is now localized to a `brux2`-below-`n3` reversal, with `zero_crossing_rate` as the largest surviving control-favoring gap on the fixed pass19 scaffold
   254|11. preserve the new pass25 shared-time-position rerun as evidence that the timing concern was real but not sufficient: both bruxism subjects rise, yet all controls still outrank them on the honest LOSO subject surface
   255|12. preserve the new pass26 matched strict-scaffold comparison as evidence that `C4-P4` does **not** rescue the stricter `A3-only` benchmark and that the timing-matched scaffold itself is now the bigger bottleneck than channel choice alone
   256|13. preserve the new pass27 feasibility audit as evidence that the current hard shared-interval selector collapses `EMG1-EMG2 A1-only` to only `2` windows per subject, so extraction validity blocks a meaningful rerun before modeling begins
   257|14. preserve the new pass28 percentile-band rerun as evidence that softer timing control fixes the extraction-collapse problem (`10` windows per subject again) but still does not rescue honest subject transfer on `EMG1-EMG2 A1-only`
   258|15. preserve the new pass29 matched percentile-band comparison as evidence that channel choice still matters on the repaired `A1-only` scaffold: `C4-P4` recovers `brux2` cleanly, but `brux1` still trails `n3`
   259|16. preserve the new pass30 cross-channel gap audit as evidence that the scaffold itself is now matched and the remaining honest failure is a narrower subject/control overlap problem rather than a timing-selection problem
   260|17. preserve the new pass31 recurrence audit as evidence that the suspected narrow `n3`-favoring trio is not the whole story on the repaired scaffold: `burst_fraction` recurs, but the strongest EMG control-favoring gap is still broader (`mean`, `max`, `ptp`, `zero_crossing_rate`), so a trio-only ablation would have been under-justified
   261|18. preserve the new pass32 broader morphology ablation as evidence that wholesale deletion is also not the fix: `EMG1-EMG2` still misses both bruxism subjects, `n3` stays above `brux1`, and `C4-P4` loses its earlier `brux2` recovery
   262|19. preserve the new pass33 smaller raw-location ablation as evidence that a narrower deletion is not the fix either: removing only `mean`, `min`, and `max` leaves `C4-P4` essentially unchanged but makes `EMG1-EMG2` worse by collapsing `brux1` while `n3` stays high
   263|20. preserve the new pass34 record-relative audit as evidence that one representation change can fix the worst `brux2` versus `n3` reversal without fixing the harder `brux1` bottleneck
   264|21. preserve the new pass35 shape-feature expansion as evidence that compact waveform-shape descriptors also improve the repaired scaffold's control/bruxism margins, but still do not clear the honest subject-level sensitivity bar
   265|22. preserve the new pass36 composition audit as evidence that the two best EMG representation clues do compose honestly on the repaired scaffold, recovering `brux2` and matching the stronger subject-level metric surface, but still leaving `brux1` as the remaining bottleneck
   266|23. next, keep the repaired five-subject scaffold fixed and localize the remaining `brux1` failure before any channel pivot, broad feature stack, or neural-model branch
   267|24. only after that consider REM-only filtering, channel fusion, or a small neural baseline
   268|

SOURCE: /home/hermes/work/ai-lab/projects/bruxism-cap/data/README.md
     1|# Data notes for bruxism-cap
     2|
     3|## Raw data layout
     4|
     5|Expected raw EDF files live under:
     6|
     7|- `projects/bruxism-cap/data/raw/capslpdb/`
     8|
     9|Suggested starter subset:
    10|- bruxism: `brux1.edf`, `brux2.edf`
    11|- controls: `n3.edf`, `n5.edf`, `n10.edf`, `n11.edf`
    12|
    13|Keep this first pass tiny. The goal is to exercise the pipeline, not to maximize sample count.
    14|
    15|## Manifest file
    16|
    17|Copy `subject_manifest.example.csv` to `subject_manifest.csv` and edit it for the exact files / channels you decide to use.
    18|
    19|Suggested columns:
    20|- `subject_id`
    21|- `label`
    22|- `edf_path`
    23|- `channel`
    24|- `notes`
    25|
    26|## Derived data files
    27|
    28|Typical derived outputs:
    29|- `window_features.csv` — one row per signal window
    30|- `random-window-cv.json` — leakage-prone reference result
    31|- `loso-cv.json` — subject-aware result
    32|
    33|## Label discipline
    34|
    35|Keep labels binary for version 1:
    36|- `bruxism`
    37|- `control`
    38|
    39|Do not mix in other CAP pathology groups for the first baseline.
    40|
    41|## Important caveat
    42|
    43|CAP is primarily a sleep-instability database, not a bruxism benchmark. The public bruxism subset is tiny.
    44|
    45|That means:
    46|- treat this as a reproducible pilot
    47|- prefer transparent feature engineering over aggressive modeling
    48|- document every evaluation shortcut explicitly
    49|

SOURCE: /home/hermes/work/ai-lab/projects/bruxism-cap/reports/first-baseline.md
     1|# First bruxism-cap baseline report
     2|
     3|Date: 2026-05-03
     4|Status: first real baseline runs completed; current result is a strong leakage warning, not a credible detector
     5|
     6|## Goal
     7|
     8|Produce the first honest CAP-based bruxism baseline with both:
     9|- random window cross-validation
    10|- leave-one-subject-out cross-validation
    11|
    12|Then document what failed, what was fixed, and what the next bounded step should be.
    13|
    14|## Pre-run checklist
    15|
    16|- [x] Raw EDF subset downloaded under `projects/bruxism-cap/data/raw/capslpdb/`
    17|- [x] Chosen channel exists for all included subjects
    18|- [x] Feature CSV regenerated from raw data
    19|- [x] Class balance checked
    20|- [x] Subject counts checked
    21|- [x] Random-window CV result saved
    22|- [x] LOSO CV result saved
    23|- [x] Gap between the two documented
    24|- [x] First measurement fix from the autoresearch pass tested
    25|- [x] First annotation-aware rerun tested and documented
    26|
    27|## Dataset used for the first real runs
    28|
    29|- Subjects: `brux1`, `brux2`, `n3`, `n5`, `n10`, `n11`
    30|- Labels: `2` bruxism subjects, `4` control subjects
    31|- Channel: `C4-P4` for the original baseline history; `EMG1-EMG2` is now the primary next-pass channel
    32|- Window seconds: `30`
    33|- Window count per subject: `20`
    34|- Total windows: `120`
    35|- Time slice: first `600` seconds of each record (current known weakness)
    36|- Feature CSV: `projects/bruxism-cap/data/window_features_pass2.csv`
    37|
    38|## Run history
    39|
    40|### Pass 1 — tiny pilot / pipeline shakeout
    41|- Subjects: `brux1`, `brux2`, `n10`
    42|- Feature CSV: `projects/bruxism-cap/data/window_features_pass1.csv`
    43|- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass1.json`
    44|- Outcome:
    45|  - random-window CV looked unrealistically perfect or near-perfect
    46|  - LOSO was not valid yet because the lone control fold left the training split with only bruxism examples
    47|- Value of this pass:
    48|  - proved the extraction + baseline path worked end to end
    49|  - exposed the need for more controls before claiming any subject-aware result
    50|
    51|### Pass 2 — first valid 6-subject baseline
    52|- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass2.json`
    53|- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass2.json`
    54|- Best random-window result:
    55|  - logistic regression balanced accuracy / sensitivity / specificity / AUROC:
    56|    `1.000 / 1.000 / 1.000 / 1.000`
    57|- Best LOSO result:
    58|  - SVM balanced accuracy / sensitivity / specificity / AUROC:
    59|    `0.783 / 0.167 / 0.617 / n/a`
    60|- Interpretation:
    61|  - adding controls made LOSO runnable, but the leakage gap remained huge
    62|  - held-out bruxism sensitivity was still very poor
    63|
    64|### Pass 3 — first autoresearch-motivated measurement fix
    65|- Change tested:
    66|  - excluded `n_samples` and `duration_s` from model features in `src/train_baseline.py`
    67|  - reason: `n_samples` was directly encoding sampling-rate differences across subjects, especially `brux2` (`256 Hz`) versus the `512 Hz` records
    68|- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass3-nosfreq.json`
    69|- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass3-nosfreq.json`
    70|- Best random-window result:
    71|  - logistic regression balanced accuracy / sensitivity / specificity / AUROC:
    72|    `0.963 / 0.950 / 0.975 / 0.996875`
    73|- Best LOSO result:
    74|  - SVM balanced accuracy / sensitivity / specificity / AUROC:
    75|    `0.733 / 0.117 / 0.617 / n/a`
    76|- Interpretation:
    77|  - removing the obvious sampling-rate proxy reduced the random-window score slightly
    78|  - it did not solve the real problem: LOSO still generalizes poorly to held-out bruxism subjects
    79|
    80|### Pass 4 — first annotation-aware rerun on sleep-stage windows
    81|- Change tested:
    82|  - patched `src/prepare_windows.py` to accept RemLogic `.txt` sidecars and select windows by scored events such as `SLEEP-S2`
    83|  - downloaded local annotation sidecars `brux1.txt`, `brux2.txt`, `n3.txt`, `n5.txt`, `n10.txt`, `n11.txt`
    84|  - built a stage-aware CSV using the first `20` in-range `SLEEP-S2` windows for each usable subject
    85|- Important scope note:
    86|  - `n10` could not be included because its local EDF is only about `3783` seconds long while its scoring file continues far beyond the available signal, leaving `0` in-range `SLEEP-S2` windows
    87|  - `brux1` also has many late scoring entries beyond the available EDF duration, but it still has enough in-range `SLEEP-S2` windows for this bounded test
    88|- Feature CSV: `projects/bruxism-cap/data/window_features_pass4_s2.csv`
    89|- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass4-s2.json`
    90|- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass4-s2.json`
    91|- Dataset used:
    92|  - subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
    93|  - labels: `2` bruxism subjects, `3` control subjects
    94|  - channel: `C4-P4` in the original stage-aware history; `EMG1-EMG2` is now the primary next-pass channel
    95|  - windows: `20` per subject, all tagged `SLEEP-S2`
    96|- Best random-window result:
    97|  - logistic regression balanced accuracy / sensitivity / specificity / AUROC:
    98|    `1.000 / 1.000 / 1.000 / 1.000`
    99|- Best LOSO result:
   100|  - SVM balanced accuracy / sensitivity / specificity / AUROC:
   101|    `0.600 / 0.030 / 0.570 / n/a`
   102|- Interpretation:
   103|  - annotation-aware extraction is now reproducible in the repo, which is a real infrastructure improvement
   104|  - the result is still a negative one scientifically: stage-matching alone did not reduce the leakage gap and in this small subset it made honest held-out performance even worse
   105|  - this strongly suggests the remaining problem is not just “first 10 minutes” slicing; it is deeper subject/background separability plus tiny-subject instability and possibly record/annotation mismatches
   106|
   107|### Pass 5 — subject-level LOSO aggregation hardening
   108|- Change tested:
   109|  - patched `src/train_baseline.py` so evaluation reports now preserve the original window-level metrics and also add a `subject_aggregation` block that collapses each held-out subject to one verdict using the mean positive score across that subject's windows
   110|  - reran LOSO on the pass3 and pass4 feature tables into `loso-cv-pass5-pass2-subjectagg.json` and `loso-cv-pass5-pass4-s2-subjectagg.json`
   111|- Why this matters:
   112|  - the earlier LOSO summaries could look slightly less bad because a held-out bruxism subject might get a few positive windows without ever crossing a subject-level positive verdict
   113|  - for this project, subject-level detection is the more honest reading of whether a held-out person is actually being recognized
   114|- Key subject-level results:
   115|  - pass3 best window-level LOSO model remained SVM at `0.733` balanced accuracy and `0.117` window sensitivity, but its subject-level summary fell to `0.375` balanced accuracy with `0.000` subject sensitivity and `0.750` subject specificity
   116|  - pass4 best window-level LOSO model remained SVM at `0.600` balanced accuracy and `0.030` window sensitivity, while subject-level aggregation was `0.500` balanced accuracy with `0.000` subject sensitivity and `1.000` subject specificity
   117|- Interpretation:
   118|  - none of the current models actually identifies a held-out bruxism subject at the subject verdict level on either pass3 or pass4
   119|  - the earlier small window-level true-positive counts were therefore not a meaningful sign of subject recognition
   120|
   121|### Pass 6 — subject-versus-label confound audit
   122|- Change tested:
   123|  - added `src/audit_subject_confound.py` to compare the current pass3/pass4 feature tables on a bounded unsupervised/semi-supervised audit surface
   124|  - saved artifacts to `projects/bruxism-cap/reports/subject-confound-audit-pass6.json` and `projects/bruxism-cap/reports/subject-confound-audit-pass6.md`
   125|- Why this matters:
   126|  - the repo had already shown a large random-vs-LOSO gap, but the next bottleneck was still ambiguous: are the handcrafted features mostly clustering by person, or do they separate the current labels inside the seen-subject pool while failing to transfer?
   127|  - this audit checks that directly with subject-vs-label silhouette scores, nearest-neighbor agreement, and a random-window 1-NN probe
   128|- Key results:
   129|  - pass3 (`window_features_pass2.csv`) showed stronger label than subject separation: silhouette `0.364` for label vs `0.195` for subject, nearest-neighbor same-label rate `0.967` vs same-subject rate `0.817`, and random-window 1-NN label accuracy `0.958` vs subject-ID accuracy `0.800`
   130|  - pass4 (`window_features_pass4_s2.csv`) showed the same pattern after annotation-aware `SLEEP-S2` extraction: silhouette `0.327` for label vs `0.147` for subject, nearest-neighbor same-label rate `1.000` vs same-subject rate `0.830`, and random-window 1-NN label accuracy `1.000` vs subject-ID accuracy `0.810`
   131|- Interpretation:
   132|  - this does **not** support the narrow story that random-window optimism is mainly coming from trivial subject-ID recovery inside the current feature space
   133|  - instead, the data now point to a different bottleneck: the current windows contain an easy label-separation pattern inside the seen-subject pool, but that pattern is not stable enough to survive held-out-subject transfer
   134|  - annotation-aware `SLEEP-S2` filtering alone did not make the class boundary more transferable
   135|
   136|### Pass 7 — SLEEP-S2 plus CAP micro-event overlap
   137|- Change tested:
   138|  - patched `src/prepare_windows.py` with `--require-overlap-events` and `--min-overlap-seconds`
   139|  - rebuilt the annotation-aware feature table so every kept `SLEEP-S2` window also overlaps at least one `MCAP-A1`, `MCAP-A2`, or `MCAP-A3` row
   140|  - saved the new artifacts to `projects/bruxism-cap/data/window_features_pass7_s2_mcap.csv`, `projects/bruxism-cap/reports/random-window-cv-pass7-s2-mcap.json`, `projects/bruxism-cap/reports/loso-cv-pass7-s2-mcap.json`, and `projects/bruxism-cap/reports/pass7-s2-mcap-overlap.md`
   141|- Important scope note:
   142|  - `n10` is still excluded because the local EDF still has `0` in-range `SLEEP-S2` windows, so it also has `0` usable `S2+MCAP` windows
   143|  - the other five subjects all had more than `20` eligible overlap windows, so the bounded rerun kept the same `5`-subject / `20`-windows-per-subject shape as pass4
   144|- Best random-window result:
   145|  - logistic regression balanced accuracy / sensitivity / specificity / AUROC:
   146|    `1.000 / 1.000 / 1.000 / 1.000`
   147|- Best LOSO result:
   148|  - logistic regression balanced accuracy / sensitivity / specificity / AUROC:
   149|    `0.590 / 0.000 / 0.590 / n/a`
   150|- Subject-level result:
   151|  - all three models stayed at subject balanced accuracy `0.500` with subject sensitivity `0.000` and subject specificity `1.000`
   152|- Interpretation:
   153|  - this tighter event-aware extraction rule is a useful infrastructure addition and a useful negative result, but not a performance improvement
   154|  - random-window CV remained effectively perfect while held-out bruxism detection regressed to zero sensitivity even at the window level
   155|  - the failure surface is therefore now tighter again: simple stage restriction plus CAP micro-event overlap is still not enough to produce a transferable cross-subject boundary
   156|
   157|### Pass 8 — overlap event mix audit for the kept S2+MCAP subset
   158|- Change tested:
   159|  - added `src/audit_overlap_event_mix.py` to audit which CAP micro-event overlap families (`MCAP-A1`, `MCAP-A2`, `MCAP-A3`) dominate the pass7 subset, both before the `20`-window cap and inside the final kept windows
   160|  - saved artifacts to `projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.json` and `projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.md`
   161|- Why this matters:
   162|  - pass7 proved that the mixed `S2+MCAP` bucket did not transfer better, but it still left an ambiguity: are all subjects contributing roughly the same CAP overlap-event regime, or is the kept subset itself heterogeneous in a way that makes the next extraction variant hard to interpret?
   163|- Key results:
   164|  - `brux2` kept windows were overwhelmingly `MCAP-A3`-overlap (`19/20` with `A3`), while `n5` kept windows were mostly `MCAP-A1`-overlap (`16/20` with `A1`)
   165|  - that imbalance already existed in the full eligible pools, not only in the first-`20` cap: `brux2` had `111/181` eligible windows with `MCAP-A3` only, while `n5` had `134/194` eligible windows with `MCAP-A1` only
   166|  - at the label level, the eligible bruxism pool was `A3`-dominated (`142/258` `A3`-only windows), while the eligible control pool was `A1`-dominated (`177/456` `A1`-only windows)
   167|- Interpretation:
   168|  - the pass7 negative result is now easier to read: the current mixed-event `S2+MCAP` subset is not one homogeneous physiological bucket
   169|  - a narrower single-family overlap extraction rule is a better next step than another broad mixed-event rerun
   170|
   171|### Pass 9 — narrower single-family `S2 + MCAP-A3` rerun
   172|- Change tested:
   173|  - rebuilt the stage-aware subset so every kept window had to be in-range `SLEEP-S2` and overlap `MCAP-A3`
   174|  - saved artifacts to `projects/bruxism-cap/data/window_features_pass9_s2_mcap_a3.csv`, `projects/bruxism-cap/reports/random-window-cv-pass9-s2-mcap-a3.json`, `projects/bruxism-cap/reports/loso-cv-pass9-s2-mcap-a3.json`, and `projects/bruxism-cap/reports/pass9-s2-mcap-a3.md`
   175|- Dataset used:
   176|  - subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
   177|  - labels: `2` bruxism subjects, `3` control subjects
   178|  - windows: `20` per subject, all tagged `SLEEP-S2` with `MCAP-A3` overlap
   179|- Best random-window result:
   180|  - logistic regression balanced accuracy / sensitivity / specificity / AUROC:
   181|    `0.921 / 0.875 / 0.967 / 0.950`
   182|- Best LOSO result:
   183|  - random forest balanced accuracy / sensitivity / specificity / AUROC:
   184|    `0.550 / 0.010 / 0.540 / n/a`
   185|- Subject-level result:
   186|  - all three models again stayed at subject balanced accuracy `0.500` with subject sensitivity `0.000` and subject specificity `1.000`
   187|- Interpretation:
   188|  - narrowing from the mixed `S2+MCAP` bucket to `S2+A3` reduced random-split optimism, which is directionally useful
   189|  - but honest held-out transfer still did not improve, so the pass7 failure was not simply caused by mixing `A1`, `A2`, and `A3` together
   190|  - the next extraction test should become more auditable still, for example by making the overlap rule exclusive (`A3` without simultaneous `A1/A2`) rather than only requiring `A3` presence
   191|
   192|### Pass 10 — exclusive `S2 + MCAP-A3-only` rerun
   193|- Change tested:
   194|  - patched `src/prepare_windows.py` to accept `--exclude-overlap-events` so annotation-selected windows can require one overlap family while forbidding others
   195|  - rebuilt the stage-aware subset so every kept window had to be in-range `SLEEP-S2`, overlap `MCAP-A3`, and avoid simultaneous `MCAP-A1` / `MCAP-A2` overlap
   196|  - saved artifacts to `projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv`, `projects/bruxism-cap/reports/random-window-cv-pass10-s2-mcap-a3-only.json`, `projects/bruxism-cap/reports/loso-cv-pass10-s2-mcap-a3-only.json`, and `projects/bruxism-cap/reports/pass10-s2-mcap-a3-only.md`
   197|- Feasibility check:
   198|  - all five already-verified subjects still had at least `20` eligible exclusive-`A3` windows locally (`brux1` `31`, `brux2` `111`, `n3` `76`, `n5` `38`, `n11` `42`), so the bounded rerun preserved the same `5`-subject / `20`-windows-per-subject shape as pass9
   199|- Best random-window result:
   200|  - random forest balanced accuracy / sensitivity / specificity / AUROC:
   201|    `0.908 / 0.850 / 0.967 / 0.9791666666666666`
   202|- Best LOSO result:
   203|  - SVM balanced accuracy / sensitivity / specificity / AUROC:
   204|    `0.500 / 0.000 / 0.500 / n/a`
   205|- Subject-level result:
   206|  - all three models again stayed at subject balanced accuracy `0.500` with subject sensitivity `0.000` and subject specificity `1.000`
   207|- Interpretation:
   208|  - the extraction rule is now more auditable because the kept `A3` windows can no longer mix with simultaneous `A1/A2` overlap
   209|  - but honest held-out transfer still did not improve; it regressed again to chance-level balanced accuracy
   210|  - this is therefore another useful negative result: even exclusive `A3` windows do not produce a transferable cross-subject boundary in the current tiny subset
   211|
   212|### Pass 11 — rule-survival audit across overlap filters
   213|- Change tested:
   214|  - added `src/audit_rule_survival.py` to summarize how many eligible windows each verified subject and label keeps under the current stage-aware overlap rules before any new model rerun
   215|  - saved artifacts to `projects/bruxism-cap/reports/rule-survival-audit-pass11.json` and `projects/bruxism-cap/reports/pass11-rule-survival-audit.md`
   216|- Why this matters:
   217|  - pass7, pass9, and pass10 changed event semantics, but they also changed per-subject and per-label window availability
   218|  - without an explicit availability audit, later run-to-run comparisons can look like physiology changes when they are partly sampling-surface changes
   219|- Key results:
   220|  - the bruxism pool keeps `258/442` eligible pass4 `S2` windows (`58.4%`) under the mixed `S2+MCAP` rule, `161/442` (`36.4%`) under `S2+A3`, and `142/442` (`32.1%`) under exclusive `S2+A3-only`
   221|  - the control pool thins much faster: `456/1026` (`44.4%`) under mixed `S2+MCAP`, `177/1026` (`17.3%`) under `S2+A3`, and `156/1026` (`15.2%`) under exclusive `S2+A3-only`
   222|  - the imbalance is also sharp at the subject level: `brux2` still has `111` eligible exclusive-`A3` windows, while `n5` falls to `38`
   223|- Interpretation:
   224|  - the later overlap-filter reruns are still useful negative results, but they are not availability-neutral comparisons
   225|  - the stricter `A3` rules preserve relatively more bruxism windows than control windows, so future family-to-family comparisons need explicit survival bookkeeping
   226|
   227|### Pass 12 — matched exclusive `S2 + A1-only` versus `S2 + A3-only`
   228|- Change tested:
   229|  - built one matched exclusive-family comparison on the same verified 5-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`)
   230|  - generated `A1-only` and `A3-only` feature tables capped to the same `14` windows per subject because `n11` has only `14` eligible `A1-only` windows locally
   231|  - saved artifacts to `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a1_only_matched14.csv`, `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a3_only_matched14.csv`, `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a1-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json`, `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a3-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a3-only-matched14.json`, and `projects/bruxism-cap/reports/pass12-exclusive-a1-vs-a3-matched14.md`
   232|- Why this matters:
   233|  - pass10 showed that exclusive `A3` windows were still not transferable, while pass11 showed that overlap-rule comparisons were also availability comparisons
   234|  - this pass answers the next validity question directly by holding the subject set and per-subject cap constant while changing only the exclusive overlap family
   235|- Key results:
   236|  - matched `A1-only` achieved the best LOSO window-level balanced accuracy at `0.686` (`logreg`) with held-out bruxism sensitivity `0.186`
   237|  - matched `A1-only` also achieved the best subject-level LOSO summary at balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
   238|  - matched `A3-only` remained weak even under the same `14`-window cap: best LOSO balanced accuracy was only `0.514`, and subject-level bruxism sensitivity stayed `0.000` for every model
   239|  - the `A1-only` gain is still incomplete and fragile because only `brux2` crossed the subject threshold; `brux1` remained missed
   240|- Interpretation:
   241|  - the earlier focus on exclusive `A3` windows was too narrow; under matched conditions, exclusive `A1-only` is the stronger transfer candidate in the current tiny subset
   242|  - this is still not a trustworthy detector, because subject-level sensitivity only improved from `0.000` to `0.500` and still depends on one of two bruxism subjects being recognized
   243|  - the next bounded question should therefore stay on score/threshold auditing for pass12 rather than on model-family expansion
   244|
   245|### Pass 13 — first matched `EMG1-EMG2` versus `C4-P4` channel comparison on the strongest current `A1-only` scaffold
   246|- Change tested:
   247|  - kept the same verified 5-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`), the same exclusive `SLEEP-S2 + MCAP-A1-only` rule, and the same `14`-windows-per-subject cap as pass12
   248|  - regenerated the matched feature table using `EMG1-EMG2` instead of `C4-P4`
   249|  - saved artifacts to `projects/bruxism-cap/data/window_features_pass13_emg_s2_mcap_a1_only_matched14.csv`, `projects/bruxism-cap/reports/random-window-cv-pass13-emg-s2-mcap-a1-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass13-emg-s2-mcap-a1-only-matched14.json`, and `projects/bruxism-cap/reports/pass13-emg-vs-c4-a1-only-matched14.md`
   250|- Why this matters:
   251|  - the repo had just been reframed as EMG-first, but that framing still needed one real matched channel comparison inside the current verified CAP scaffold
   252|  - this pass changes only the signal channel, so it is the cleanest first test of whether the current honest `A1-only` result transfers to `EMG1-EMG2`
   253|- Key results:
   254|  - best random-window EMG balanced accuracy stayed superficially strong at `0.882` (`svm`), which means random splits remain a misleading comparison surface
   255|  - best EMG LOSO balanced accuracy fell to only `0.543` (`logreg`), with held-out bruxism sensitivity `0.043`
   256|  - subject-level EMG sensitivity fell back to `0.000` for every model; unlike pass12 `C4-P4`, the EMG rerun missed both `brux1` and `brux2`
   257|- Interpretation:
   258|  - this is a first-class negative result, not an EMG win: the first matched `EMG1-EMG2` rerun did **not** beat the current `C4-P4` anchor under the same rule and subset
   259|  - the main failure is honest transfer, not in-dataset separability: random CV stayed high while LOSO subject detection regressed
   260|  - the next bounded EMG-first question should be whether `EMG1-EMG2` prefers a different overlap family (for example exclusive `A3-only`) rather than assuming the current strongest `C4-P4` family transfers unchanged
   261|
   262|### Pass 14 — matched `EMG1-EMG2` exclusive `A1-only` versus exclusive `A3-only`
   263|- Change tested:
   264|  - kept the same verified 5-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`), the same `14`-windows-per-subject cap, and the same EMG channel (`EMG1-EMG2`)
   265|  - changed only the exclusive overlap family from `MCAP-A1-only` to `MCAP-A3-only`
   266|  - saved artifacts to `projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv`, `projects/bruxism-cap/reports/random-window-cv-pass14-emg-s2-mcap-a3-only-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json`, and `projects/bruxism-cap/reports/pass14-emg-a1-vs-a3-matched14.md`
   267|- Why this matters:
   268|  - pass13 showed that the strongest current `C4-P4` family did not transfer cleanly to EMG
   269|  - this pass answers the narrower EMG-first validity question directly: does `EMG1-EMG2` prefer a different exclusive overlap family on the same matched scaffold?
   270|- Key results:
   271|  - best random-window EMG balanced accuracy improved from `0.882` on `A1-only` to `0.954` on `A3-only` (`svm`), which is still not the trustworthy surface
   272|  - best EMG LOSO balanced accuracy improved from `0.543` to `0.629` (`logreg`), with sensitivity rising only from `0.043` to `0.057`
   273|  - subject-level EMG sensitivity still stayed `0.000` for every model, so both `brux1` and `brux2` remained missed at the default subject threshold
   274|- Interpretation:
   275|  - overlap-family choice matters inside EMG too: `A3-only` is less bad than `A1-only` on the current matched scaffold
   276|  - but this is still not a baseline win, because the honest subject-level criterion did not improve at all
   277|  - the next bounded EMG-first question should now be score / threshold auditing on the stronger `A3-only` EMG run rather than another model-family change
   278|
   279|### Pass 15 — subject-threshold audit on the stronger EMG `A3-only` run
   280|- Change tested:
   281|  - added `src/audit_subject_thresholds.py` to sweep subject-score thresholds over a saved LOSO report and compare the resulting subject-level metrics against an anchor report
   282|  - saved artifacts to `projects/bruxism-cap/reports/subject-threshold-audit-pass15-emg-a3-vs-c4-a1.json` and `projects/bruxism-cap/reports/pass15-emg-a3-threshold-audit.md`
   283|- Why this matters:
   284|  - pass14 still left one ambiguity: does the current EMG-first failure come from a bad default subject threshold, or from a deeper score-ordering problem that threshold tuning cannot fix?
   285|- Key results:
   286|  - in the stronger EMG run (`EMG1-EMG2` `A3-only` `logreg`), the best bruxism subject score is only `0.176` (`brux1`), while two controls still score higher: `n3` `0.267` and `n5` `0.266`
   287|  - any threshold low enough to recover `brux1` also flips both `n3` and `n5` positive, dropping subject specificity to `0.333` and balanced accuracy to `0.417`
   288|  - any threshold low enough to recover both bruxism subjects predicts every subject positive, collapsing specificity to `0.000`
   289|  - the current honest anchor (`C4-P4` `A1-only` `logreg`) still has a positive best-bruxism minus highest-control margin of `+0.362`, while the EMG run has a negative margin of `-0.091`
   290|- Interpretation:
   291|  - this preserves a sharper negative result than pass14 alone: the current EMG-first failure is **not** mainly a threshold-choice problem
   292|  - the bottleneck is now better localized to score ordering / feature validity on the fixed matched EMG scaffold
   293|  - the next bounded step should therefore move to one compact EMG feature-validity audit rather than more threshold tweaking
   294|
   295|### Pass 16 — EMG feature-validity audit on the stronger matched `A3-only` run
   296|- Change tested:
   297|  - added `src/audit_emg_feature_validity.py` to rebuild the saved pass14 `EMG1-EMG2 A3-only` `logreg` LOSO folds and summarize per-subject feature contributions
   298|  - saved artifacts to `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.json` and `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.md`
   299|- Why this matters:
   300|  - pass15 showed that threshold tuning was a dead end, so the next bounded question became which handcrafted features were actually lifting `n3` and `n5` above `brux1`
   301|- Key results:
   302|  - the problematic subject ranking reproduced exactly under the audit rebuild: `n3` `0.267`, `n5` `0.266`, `brux1` `0.176`, `n11` `0.095`, `brux2` `0.074`
   303|  - the same recurring high-score-control feature family kept appearing: `ratio_alpha_delta`, `min`, and `sample_entropy`
   304|  - `brux1` looked like a different instability surface because its fold was dominated by extreme absolute-power / mean terms rather than the same control-favoring pattern
   305|- Interpretation:
   306|  - this preserved a useful EMG-first validity result: the failure survives a fold-by-fold rebuild and is not a reporting artifact
   307|  - the next bounded step should be one small feature-family ablation on the fixed pass14 scaffold rather than more threshold schedules or larger models
   308|
   309|### Pass 17 — matched `EMG1-EMG2` `A3-only` time-domain ablation
   310|- Change tested:
   311|  - patched `src/train_baseline.py` so the baseline runner can optionally include or exclude feature families by regex without changing the saved feature table
   312|  - reran the same matched pass14 `EMG1-EMG2 A3-only` scaffold after dropping only the spectral / ratio family (`bp_*`, `rel_bp_*`, `ratio_*`), leaving `9` time-domain features
   313|  - saved artifacts to `projects/bruxism-cap/reports/random-window-cv-pass17-emg-a3-timeonly-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass17-emg-a3-timeonly-matched14.json`, and `projects/bruxism-cap/reports/pass17-emg-a3-timeonly-ablation.md`
   314|- Why this matters:
   315|  - pass16 suggested the safest next patch was a single deletion-style ablation before trying new EMG-specific features
   316|- Key results:
   317|  - random-window CV stayed superficially high: best balanced accuracy improved slightly from `0.954` to `0.967`, so random splits remain a misleading surface
   318|  - best LOSO window-level balanced accuracy regressed slightly from `0.629` to `0.614` (`logreg`), while sensitivity fell from `0.057` to `0.043`
   319|  - subject-level sensitivity still stayed `0.000` for every model, so the honest subject-level verdict did not improve at all
   320|  - the score ordering stayed hostile and in one respect worsened: `n3` rose from `0.267` to `0.328`, while `brux1` fell from `0.176` to `0.148` and `brux2` fell from `0.074` to `0.055`
   321|- Interpretation:
   322|  - this preserves another important negative result: the current EMG-first failure is **not** fixed by simply deleting the EEG-shaped spectral family
   323|  - deletion-only ablation removes some suspect features, but it also weakens both bruxism subjects and leaves `n3` even harder to separate
   324|  - the next bounded EMG-first step should therefore move from subtraction-only patches to one compact EMG-specific replacement family such as burst / envelope / amplitude-variability features
   325|
   326|### Pass 18 — matched `EMG1-EMG2` `A3-only` envelope / burst replacement family
   327|- Change tested:
   328|  - patched `src/features.py` to add `8` compact EMG-oriented summaries: `rectified_mean`, `rectified_std`, `envelope_mean`, `envelope_std`, `envelope_cv`, `burst_fraction`, `burst_rate_hz`, and `p95_abs`
   329|  - regenerated the same matched `EMG1-EMG2 A3-only` feature table on the verified `5`-subject / `14`-windows-per-subject scaffold
   330|  - saved artifacts to `projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv`, `projects/bruxism-cap/reports/random-window-cv-pass18-emg-a3-envelope-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass18-emg-a3-envelope-matched14.json`, `projects/bruxism-cap/reports/pass18-emg-a3-envelope-replacement.md`, and `projects/bruxism-cap/reports/feature-validity-audit-pass18-emg-a3-envelope-logreg.md`
   331|- Why this matters:
   332|  - pass17 showed that subtraction-only cleanup was not enough, so the next bounded EMG-first question became whether one compact replacement-oriented EMG family could help on the same matched scaffold
   333|- Key results:
   334|  - random-window CV stayed unrealistically high: best balanced accuracy was still `0.933` (`logreg`)
   335|  - best LOSO window-level balanced accuracy regressed again from `0.629` on pass14 and `0.614` on pass17 to `0.600` on pass18 (`logreg`)
   336|  - subject-level sensitivity still stayed `0.000` for every model, so the honest verdict remained unchanged
   337|  - the score ordering shifted but did not improve enough: `brux1` recovered slightly from `0.148` to `0.158`, `brux2` from `0.055` to `0.092`, and `n3` dropped from `0.328` to `0.245`, but `n5` stayed above `brux1` at `0.267`
   338|- Interpretation:
   339|  - this is another useful EMG-first negative result: adding one compact rectified-envelope / burst family is not enough by itself to rescue honest transfer
   340|  - the new features do enter the model, but the same older feature family still dominates the wrong subject ordering, especially the large negative `mean` / bandpower burden on `brux1`
   341|  - the next bounded step should therefore keep the new EMG family but test it under stricter feature selection rather than simple add-only expansion
   342|
   343|### Pass 19 — matched `EMG1-EMG2` `A3-only` envelope family under stricter train-time feature selection
   344|- Change tested:
   345|  - kept the same pass18 feature table and reran the same matched `EMG1-EMG2 A3-only` scaffold while excluding only `bp_*`, `rel_bp_*`, and `ratio_*` at train time
   346|  - saved artifacts to `projects/bruxism-cap/reports/random-window-cv-pass19-emg-a3-envelope-selected-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json`, and `projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md`
   347|- Why this matters:
   348|  - pass18 suggested that the new EMG-oriented family might be useful only if the older EEG-shaped spectral family stopped dominating the same matched scaffold
   349|- Key results:
   350|  - random-window CV stayed unrealistically high again: best balanced accuracy stayed `0.933` (`logreg`)
   351|  - best LOSO window-level balanced accuracy recovered from `0.600` on pass18 to `0.629` on pass19 (`logreg`), matching pass14 while slightly improving specificity from `0.571` to `0.586`
   352|  - subject-level sensitivity still stayed `0.000` for every model, so the honest verdict remained unchanged
   353|  - the score ordering became slightly less hostile than pass18 on one edge (`n5` fell from `0.267` to `0.222` and `n11` stayed below `brux1`), but `n3` (`0.280`) and `n5` (`0.222`) still outranked `brux1` (`0.151`)
   354|- Interpretation:
   355|  - this is a useful partial-validity result, not a baseline win: the pass18 envelope / burst family behaves better under stricter feature selection than under add-only expansion
   356|  - but the honest bottleneck still survives because the subject ordering remains wrong and subject-level bruxism sensitivity stays `0.000`
   357|  - the next bounded step should now focus on one remaining score-ordering driver such as `mean`, rather than broader feature growth or model complexity
   358|
   359|### Pass 20 — matched `EMG1-EMG2` `A3-only` envelope family with stricter selection plus `mean` ablation
   360|- Change tested:
   361|  - kept the same pass18 feature table and reran the same matched `EMG1-EMG2 A3-only` scaffold with the same pass19 exclusions for `bp_*`, `rel_bp_*`, and `ratio_*`
   362|  - also excluded only one additional feature at train time: raw `mean`
   363|  - saved artifacts to `projects/bruxism-cap/reports/random-window-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`, and `projects/bruxism-cap/reports/pass20-emg-a3-envelope-selected-nomean-matched14.md`
   364|- Why this matters:
   365|  - pass19 narrowed the remaining EMG-first suspicion to whether raw `mean` was still the one removable scalar dragging `brux1` down after the older spectral / ratio family had already been excluded
   366|- Key results:
   367|  - random-window CV stayed unrealistically high again: best balanced accuracy stayed `0.933` (`logreg`)
   368|  - best LOSO window-level balanced accuracy regressed from `0.629` on pass19 to `0.600` overall (`svm`), while pass20 `logreg` fell further to `0.571` with sensitivity collapsing from `0.043` to `0.000`
   369|  - subject-level sensitivity still stayed `0.000` for every model, so the honest verdict remained unchanged
   370|  - the score ordering got materially worse for the key bruxism subject: `brux1` fell from `0.151` to `0.018`, while `n3` (`0.280`) and `n5` (`0.223`) barely moved
   371|- Interpretation:
   372|  - this is another useful EMG-first negative result: direct `mean` removal does **not** rescue the pass19 scaffold and instead makes `brux1` much less separable
   373|  - the next bounded step should therefore stop doing blind deletion-only tweaks and instead audit the retained amplitude / envelope family directly
   374|
   375|### Pass 21 — retained amplitude / envelope family audit on the pass19 working point
   376|- Change tested:
   377|  - kept the stronger pass19 matched `EMG1-EMG2 A3-only` scaffold fixed
   378|  - kept the same pass19 train-time exclusions for `bp_*`, `rel_bp_*`, and `ratio_*`
   379|  - added `projects/bruxism-cap/src/audit_emg_envelope_family.py` and audited the retained focused family (`sample_entropy`, `rectified_*`, `envelope_*`, `burst_*`, `p95_abs`) without changing the model recipe itself
   380|  - saved artifacts to `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.json` and `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.md`
   381|- Why this matters:
   382|  - pass20 showed that naive raw-`mean` removal was the wrong next move, but the repo still needed one compact explanation of what the retained pass19 EMG family is actually doing subject by subject
   383|- Key results:
   384|  - the audit reproduced the pass19 ordering exactly: `n3` `0.280`, `n5` `0.222`, `brux1` `0.151`, `n11` `0.147`, `brux2` `0.088`
   385|  - among the retained focused features, `sample_entropy` and `burst_fraction` still push `n3` and `n5` upward relative to `brux1`
   386|  - `brux1` does look distinct on raw amplitude scale (`rectified_mean`, `envelope_mean`, `p95_abs` all much larger), but those same features remain net-negative contributors under the pass19 learned coefficients, so larger raw amplitude alone does not rescue the ranking
   387|  - `burst_rate_hz` is the main retained feature that still pushes back toward `brux1`, but not strongly enough to overcome the control-favoring pieces
   388|- Interpretation:
   389|  - this is a useful EMG-first validity increment, not a baseline win: the retained family is active, but it is not cleanly bruxism-aligned on the current tiny matched subset
   390|  - the next bounded EMG-only move should therefore be normalization-aware extraction or scaling work that preserves the retained family, not more blind single-feature deletion
   391|
   392|### Pass 22 — selection-aware `EMG1-EMG2 A3-only` rerun with robust per-window `median_mad` normalization
   393|- Change tested:
   394|  - kept the stronger pass19 matched `EMG1-EMG2 A3-only` scaffold fixed
   395|  - kept the same pass19 train-time exclusions for `bp_*`, `rel_bp_*`, and `ratio_*`
   396|  - patched the extraction path so each kept window can be robust-centered and scaled before feature computation using `median` plus `MAD`, then regenerated the matched 5-subject / 14-windows-per-subject EMG table with `signal_transform=median_mad`
   397|  - saved artifacts to `projects/bruxism-cap/data/window_features_pass22_emg_s2_mcap_a3_only_matched14_medianmad.csv`, `projects/bruxism-cap/reports/random-window-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`, `projects/bruxism-cap/reports/loso-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`, and `projects/bruxism-cap/reports/pass22-emg-a3-envelope-selected-medianmad-matched14.md`
   398|- Why this matters:
   399|  - pass21 said the safest EMG-only next move was one normalization-aware extraction test rather than more blind feature deletion
   400|- Key results:
   401|  - random-window CV stayed unrealistically high again: best balanced accuracy stayed `0.933` (`logreg`)
   402|  - best LOSO window-level balanced accuracy regressed from `0.629` on pass19 to only `0.571` on pass22 (`svm`), with sensitivity collapsing to `0.000`
   403|  - subject-level sensitivity still stayed `0.000` for every model, so the honest verdict remained unchanged
   404|  - the subject ranking became harsher than pass19: pass22 `logreg` scored `n11` `0.270`, `n5` `0.251`, `n3` `0.195`, `brux2` `0.033`, `brux1` `0.009`
   405|- Interpretation:
   406|  - this preserves another useful EMG-first negative result: simple per-window robust normalization is **not** the fix for the current matched EMG scaffold
   407|  - the stronger EMG-first working point remains pass19, and the next bounded step should shift back toward benchmark clarity rather than another extraction rewrite
   408|
   409|A new project-framing decision now sits on top of that history: keep CAP as the reproducible benchmark dataset, but pivot the next active extraction path to `EMG1-EMG2` as the primary channel and treat `C4-P4` as the comparison channel. That keeps the anti-leakage lessons from the first 14 passes while aligning the next experiments more closely with the newer portable-EMG literature.
   410|
   411|## Key evidence from the first runs
   412|
   413|### 0. Current project framing changed after the first 12 passes
   414|As of `2026-05-04`, the repo still preserves the original `C4-P4`-based baseline history exactly as run, but the project itself is now documented as an **EMG-first** benchmark. `EMG1-EMG2` is the primary next-pass channel, and `C4-P4` is now the comparison channel for matched reruns rather than the default extraction target.
   415|
   416|### 1. Random-window CV is still overly optimistic
   417|Even after dropping the explicit sampling-rate proxy feature, random-window CV remained extremely high (`0.963` balanced accuracy). That is too strong to trust on `120` windows from `6` people when LOSO remains weak.
   418|
   419|### 2. The strongest current result is a leakage warning, not a bruxism detector
   420|The best honest subject-aware result after the first measurement fix was only:
   421|- balanced accuracy: `0.733`
   422|- sensitivity on held-out bruxism subjects: `0.117`
   423|- specificity on held-out control subjects: `0.617`
   424|
   425|That means the model mostly fails to recognize held-out bruxism subjects.
   426|
   427|### 3. Annotation-aware stage matching alone did not fix generalization
   428|The first stage-aware rerun used only `SLEEP-S2` windows from a 5-subject subset and still produced perfect random-window CV while LOSO fell to only `0.600` balanced accuracy and `0.030` held-out bruxism sensitivity. That is a stronger negative result than pass3, not an improvement.
   429|
   430|### 4. Subject-level aggregation makes the honest result even harsher
   431|After pass5, every tested LOSO model still produced `0.000` held-out bruxism sensitivity once predictions were collapsed to one verdict per held-out subject. In other words, the models sometimes emitted a few positive windows, but never enough to call a bruxism subject positive overall at the default threshold.
   432|
   433|### 5. The local record/annotation pairing itself now needs scrutiny
   434|The annotation-aware pass exposed a concrete data-validity issue: `n10.edf` is only about `3783` seconds long, but `n10.txt` contains later scored sleep events that fall outside the available signal. `brux1` shows a milder version of the same mismatch. So the next bottleneck is now narrower and better defined: validate record completeness / scoring alignment before trusting more stage-aware comparisons.
   435|
   436|### 6. An obvious acquisition confound was real
   437|A quick coefficient check on the pass2 logistic-regression fit showed that `n_samples` had the largest absolute coefficient. That was a useful first autoresearch catch, but removing it only slightly reduced the random-split optimism. So the confound was real, just not the only one.
   438|
   439|### 7. The pass4 alignment audit narrowed the data-validity problem further
   440|A follow-up EDF-versus-sidecar audit is now saved in `projects/bruxism-cap/reports/annotation-alignment-audit-pass4-s2.md`. The key finding is that `n10` has `0` in-range `SLEEP-S2` windows for the local files, while `brux1` has enough usable early `S2` windows but hundreds of later scored `S2` rows beyond the available EDF duration. So pass4 was still useful, but the next bottleneck is now more precise than before: preserve the annotation-aware path, keep explicit subject exclusions, and audit local record completeness before trying to interpret more stage-aware results.
   441|
   442|### 8. The new confound audit narrowed the failure story again
   443|The new pass6 artifact (`projects/bruxism-cap/reports/subject-confound-audit-pass6.md`) did **not** find stronger subject clustering than label clustering in the current handcrafted feature tables. On both the pass3 and pass4 datasets, label silhouette and nearest-neighbor agreement were higher than the subject versions. That means the leakage story is now more specific: random window splits still flatter the project, but the current feature tables are not winning only by memorizing subject identity. They appear to capture a label-separation pattern that holds within the seen-subject pool and breaks under held-out-subject transfer.
   444|
   445|### 9. The pass7 mixed-event bucket is heterogeneous by subject and label
   446|The new pass8 artifact (`projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.md`) showed that the current `SLEEP-S2 + (MCAP-A1|A2|A3)` subset mixes materially different overlap-event families across subjects. `brux2` is heavily `A3`-dominated while `n5` is heavily `A1`-dominated, and that mismatch already exists in the full eligible pools before the first-`20` cap. So the next extraction test should be a narrower single-family overlap rule rather than another broad mixed-event bucket.
   447|
   448|### 10. Narrowing to `S2 + A3` reduced random optimism but still did not transfer
   449|The new pass9 artifact (`projects/bruxism-cap/reports/pass9-s2-mcap-a3.md`) showed that moving from the mixed `S2+MCAP` bucket to an `S2 + A3` overlap rule reduced random-window balanced accuracy from `1.000` to `0.921`, which is directionally healthier. But the honest result did not improve: the best LOSO balanced accuracy fell from `0.590` to `0.550`, and subject-level bruxism sensitivity still stayed `0.000` for every model. So the failure is not explained just by mixing `A1`, `A2`, and `A3` together; the next extraction step needs to be even more auditable.
   450|
   451|### 11. Exclusive `A3` windows were cleaner but still not transferable
   452|The new pass10 artifact (`projects/bruxism-cap/reports/pass10-s2-mcap-a3-only.md`) made the overlap rule more auditable by excluding simultaneous `MCAP-A1` and `MCAP-A2` overlap from the kept `SLEEP-S2 + A3` windows. But the honest result still did not improve: the best LOSO balanced accuracy fell again to `0.500`, and subject-level bruxism sensitivity still stayed `0.000` for every model. So even exclusive `A3` windows do not isolate a transferable cross-subject boundary in the current tiny subset.
   453|
   454|### 12. The overlap rules also change availability, not just event meaning
   455|The new pass11 artifact (`projects/bruxism-cap/reports/pass11-rule-survival-audit.md`) showed that the later overlap filters are not availability-neutral. Relative to pass4 `S2`, the bruxism pool keeps `32.1%` of its eligible windows under exclusive `A3`, while the control pool keeps only `15.2%`. `brux2` still has `111` eligible exclusive-`A3` windows, but `n5` falls to `38`. So future overlap-family comparisons need to preserve the rule-survival context rather than reading each rerun as a like-for-like subset.
   456|
   457|### 13. Under matched conditions, exclusive `A1-only` transfers better than exclusive `A3-only`
   458|The new pass12 comparison (`projects/bruxism-cap/reports/pass12-exclusive-a1-vs-a3-matched14.md`) controlled the subject set and per-subject cap by matching both exclusive families to `14` windows per subject. Under that fairer comparison, `A1-only` improved the honest measurement surface: best LOSO balanced accuracy rose to `0.686`, and subject-level bruxism sensitivity rose to `0.500`, while matched `A3-only` still stayed at `0.000` subject-level sensitivity. That is an important validity clue, but not yet a stable baseline win, because `brux1` still failed and the gain is carried by only one of the two bruxism subjects.
   459|
   460|### 14. EMG prefers `A3-only` over `A1-only`, but still fails the honest subject test
   461|The new pass14 comparison (`projects/bruxism-cap/reports/pass14-emg-a1-vs-a3-matched14.md`) held the same verified subject set, cap, channel, and model family constant while changing only the exclusive overlap family inside `EMG1-EMG2`. That improved the best EMG LOSO balanced accuracy from `0.543` on `A1-only` to `0.629` on `A3-only`, and it reduced several control-subject mean scores. But subject-level bruxism sensitivity still stayed `0.000` for every model, so the best honest baseline in the repo remains the pass12 `C4-P4 A1-only` run rather than any EMG family.
   462|
   463|### 15. The stronger EMG run fails because subject ordering is wrong, not because `0.5` is too strict
   464|The new pass15 threshold audit (`projects/bruxism-cap/reports/pass15-emg-a3-threshold-audit.md`) showed that the stronger `EMG1-EMG2 A3-only` run cannot be rescued by retuning the subject threshold alone. The best bruxism subject score (`brux1` `0.176`) still sits below two controls (`n3` `0.267`, `n5` `0.266`), so any threshold that recovers `brux1` also creates at least two control false positives. Thresholds that recover both bruxism subjects collapse specificity entirely. That makes the next bottleneck sharper: feature validity / score ordering, not subject-threshold choice.
   465|
   466|### 16. The EMG score-ordering failure is now localized to one small feature family plus one brux1-specific instability
   467|The new pass16 audit (`projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.md`) rebuilt the saved pass14 `logreg` LOSO folds and explained which standardized features are pushing each held-out subject up or down. It reproduced the same subject ordering as pass15 (`n3` `0.267`, `n5` `0.266`, `brux1` `0.176`, `n11` `0.095`, `brux2` `0.074`), so the negative result is stable. The useful new narrowing is that the high-score controls repeatedly surface `ratio_alpha_delta`, `min`, and `sample_entropy` as positive contributors, while `brux1` is dominated by extreme absolute-power / mean terms. So the next EMG-first move should be one small feature-family ablation, not more threshold schedules.
   468|
   469|### 17. The new EMG family works better under stricter feature selection, but the honest subject verdict still does not move
   470|The new pass19 rerun (`projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md`) kept the pass18 envelope / burst family and excluded the older `bp_*`, `rel_bp_*`, and `ratio_*` family at train time on the same matched `EMG1-EMG2 A3-only` scaffold. That recovered the best pass14 LOSO balanced accuracy (`0.629`) and slightly improved specificity (`0.586`), which is useful evidence that the EMG-oriented family should not just be stacked on top of the older spectral features. But the honest baseline verdict still did not improve: subject-level sensitivity remained `0.000`, and both `n3` and `n5` still outranked `brux1`. So the next bottleneck is now narrower again: one remaining score-ordering driver, not a broad feature-family choice.
   471|
   472|### 18. Naive `mean` removal makes the strongest current EMG recipe worse
   473|The new pass20 rerun (`projects/bruxism-cap/reports/pass20-emg-a3-envelope-selected-nomean-matched14.md`) tested that narrowed suspicion directly by taking the pass19 selection-aware recipe and excluding only raw `mean` in addition to the existing spectral / ratio removals. The result is a preserved negative one: best LOSO window-level balanced accuracy regressed to `0.600` overall, pass20 `logreg` fell to `0.571`, subject-level sensitivity stayed `0.000`, and `brux1` collapsed from `0.151` to `0.018` while `n3` and `n5` barely moved. So `mean` is not safe to delete naively on the current EMG-first scaffold; if it is revisited at all, it should be through normalization-aware extraction rather than another simple ablation.
   474|
   475|### 19. The retained pass19 envelope family is active, but still not cleanly bruxism-aligned
   476|The new pass21 audit (`projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.md`) then checked the retained pass19 family directly instead of launching another rerun. That audit preserved the same honest ranking and made the remaining failure shape more specific: `sample_entropy` and `burst_fraction` still help the highest-score controls, while `brux1`'s much larger raw `rectified_mean`, `envelope_mean`, and `p95_abs` remain net-negative under the current learned coefficients. So the next EMG-only step should be normalization-aware extraction or scaling that preserves the retained family, not more blind deletion-only feature tweaks.
   477|
   478|### 20. Direct `median_mad` normalization also fails on the same matched EMG scaffold
   479|The new pass22 rerun (`projects/bruxism-cap/reports/pass22-emg-a3-envelope-selected-medianmad-matched14.md`) tested that exact normalization-aware hypothesis by robust-centering and scaling each kept EMG window before feature extraction while leaving the pass19 subject subset, overlap rule, and train-time feature exclusions fixed. That did **not** improve the honest result. Best LOSO balanced accuracy regressed from `0.629` to `0.571`, subject-level sensitivity stayed `0.000`, and both bruxism subjects fell even lower in the ranking under `logreg` (`brux1` `0.151 -> 0.009`, `brux2` `0.088 -> 0.033`). So the stronger EMG-first working point still remains pass19, and the next bounded step should return to benchmark-clarity comparison rather than another extraction rewrite.
   480|
   481|### 21. Shared subject-score comparison makes the remaining EMG gap explicit
   482|The new pass23 comparison (`projects/bruxism-cap/reports/pass23-emg-pass19-vs-c4-pass12-subject-score-comparison.md`) finally put the stronger pass19 `EMG1-EMG2 A3-only` working point and the honest pass12 `C4-P4 A1-only` anchor into one shared subject-score table on the same verified `5`-subject / `14`-windows-per-subject scaffold. That clarified the benchmark gap more sharply than aggregate metrics alone. The EMG working point does improve one hard case—`brux1` rises from `0.018` on the anchor to `0.151` on EMG—but the overall honest baseline still belongs to the anchor because `brux2` collapses from `0.795` to `0.088` and the highest-score control shifts from `n5` (`0.433`) to `n3` (`0.280`). The net best-bruxism-minus-highest-control margin therefore swings from `+0.362` on the anchor to `-0.129` on EMG. So the next bounded EMG-first step should focus specifically on why `brux2` collapses under `EMG1-EMG2` and why `n3` becomes the dominant control, not on another broad extraction rewrite.
   483|
   484|### 22. Shared-time-position matching improves bruxism scores but still does not rescue EMG transfer
   485|The new pass25 rerun (`projects/bruxism-cap/reports/pass25-emg-a3-time-position-matched-selected.md`) tested the pass24 timing concern directly by regenerating the uncapped exclusive `SLEEP-S2 + MCAP-A3-only` `EMG1-EMG2` pool for the same verified `5`-subject subset, then forcing every subject onto the same shared absolute `start_s` interval before rerunning the pass19-style feature exclusions. That stricter scaffold turned out to be feasible only at `10` windows per subject because `n3` and `n5` each have just `10` valid candidate windows inside the common interval. The result is another useful negative-but-informative EMG note: both bruxism subjects do rise (`brux1` `0.151` -> `0.282`, `brux2` `0.088` -> `0.215`), so time-position mismatch was contributing something real, but all three controls rise too (`n11` `0.417`, `n5` `0.416`, `n3` `0.400`) and honest subject-level sensitivity still stays `0.000`. Best LOSO window-level balanced accuracy also fails to beat pass19 (`0.600` best on pass25 versus `0.629` on pass19). So the stricter time-position match changes the failure surface but does not overturn the current best honest EMG working point.
   486|
   487|### 23. Rebuilding the same strict scaffold on `C4-P4` does not rescue the benchmark either
   488|The new pass26 comparison (`projects/bruxism-cap/reports/pass26-c4-a3-time-position-matched-vs-emg.md`) reused the exact same shared-time-position `SLEEP-S2 + MCAP-A3-only` scaffold from pass25—same `5` subjects, same `3210.0` to `12230.0` interval, same `10` windows per subject, and same train-time feature exclusions—but swapped only the extracted channel from `EMG1-EMG2` to `C4-P4`. This clarified the channel-vs-scaffold question directly. Random-window CV favored `C4-P4` again (`0.883` vs `0.808` balanced accuracy), but the honest LOSO surface did **not**: strict-scaffold `C4-P4` reached only `0.520` best LOSO balanced accuracy and `0.333` subject-level balanced accuracy, versus `0.600` and `0.500` for strict-scaffold `EMG1-EMG2`. Both channels still failed with `0.000` subject-level sensitivity, but `C4-P4` was worse because it also turned `n3` into a subject-level false positive. That preserves the EMG-first framing: the stricter `A3-only` / time-position-matched scaffold itself now looks like the larger bottleneck than channel choice alone.
   489|
   490|### 24. The same strict time-position rule is too brittle for `EMG1-EMG2 A1-only`
   491|The new pass27 feasibility audit (`projects/bruxism-cap/reports/pass27-emg-a1-time-position-feasibility.md`) followed the exact next question from pass26 without reverting away from the EMG-first frame: keep the same verified `5`-subject subset, keep `EMG1-EMG2`, switch to exclusive `SLEEP-S2 + MCAP-A1-only`, and reuse the same simple shared-absolute-interval selector before any new model rerun. The uncapped `A1-only` pool is large enough overall (`233` rows total: `27` for `brux1`, `29` for `brux2`, `29` for `n3`, `134` for `n5`, `14` for `n11`), so the overlap family itself is not missing locally. But once the strict common interval is enforced, the scaffold collapses to `7650.0`–`12650.0` seconds and only `2` windows per subject remain feasible because `n3` and `n11` each contribute just `2` candidate rows there while `brux2` contributes only `3`. I therefore preserved this as an extraction-validity result and intentionally did **not** trust a new LOSO rerun on the resulting `10`-row subset. The lesson is useful and specific: the current hard shared-interval matching rule is itself too brittle for `A1-only`, so the next timing-aware EMG pass should soften the selector rather than pretending a `2`-windows-per-subject scaffold is a meaningful benchmark.
   492|
   493|### 25. A softer percentile-band timing scaffold fixes the extraction collapse but not the honest EMG transfer failure
   494|The new pass28 rerun (`projects/bruxism-cap/reports/pass28-emg-a1-percentile-band-rerun.md`) made the next bounded move from pass27 rather than abandoning the EMG-first frame: patch the selector itself, keep the same verified `5` subjects and exclusive `SLEEP-S2 + MCAP-A1-only`, and test one softer timing-control scaffold before any bigger modeling change. The new `percentile-band` mode in `select_time_position_matched_windows.py` keeps windows by relative within-subject time position (`0.10` to `0.90`) instead of forcing one hard shared absolute interval, and `train_baseline.py` now treats the new `relative_time_quantile` field as metadata so the selector does not leak its own coordinate into training. That patch solves the immediate pass27 validity problem: the scaffold expands from only `2` windows per subject (`10` rows total) to a reproducible `10` windows per subject (`50` rows total). But the honest result stays negative. Best LOSO window-level balanced accuracy reaches `0.600` (`svm`), which only ties the stricter pass25 EMG result, and subject-level sensitivity still stays `0.000` with both bruxism subjects below all three controls in mean score order (`n3` `0.422`, `n11` `0.319`, `n5` `0.264`, `brux1` `0.222`, `brux2` `0.209`). So the softer timing-control patch is real progress in extraction validity and reproducibility, but it still does not produce a better honest EMG benchmark.
   495|
   496|### 26. A matched cross-channel audit shows the repaired scaffold is real and localizes the remaining gap to `brux1` versus `n3`
   497|The new pass30 audit (`projects/bruxism-cap/reports/pass30-a1-percentile-band-channel-gap-audit.md`) followed directly from pass29 without reverting the EMG-first frame or launching another rerun. It kept the same repaired percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold fixed, verified that the selected rows are timing-matched across `EMG1-EMG2` and `C4-P4`, and rebuilt the same `logreg` LOSO folds with the same train-time feature exclusions to inspect the remaining subject-score gaps. This preserved two sharper conclusions. First, the pass28/pass29 comparison is a real channel / feature-behavior difference rather than a hidden row-selection change: the same `10` windows per subject are being compared. Second, `brux1` remains the shared hard case under both channels, but the gap is much smaller on `C4-P4` (`n3 - brux1 = +0.012`) than on `EMG1-EMG2` (`+0.260`), while the main channel-level separation is now concentrated in `brux2`: EMG leaves `brux2` far below `n3` (`brux2 - n3 = -0.494`), whereas `C4-P4` flips that decisively positive (`+0.542`). The feature summaries also preserve a useful negative result for EMG-first work: on the repaired scaffold, the stubborn overlap is now narrow enough to audit directly, with recurring support for `n3` from irregularity / burst-style features and hostile amplitude / crossing behavior on the bruxism folds. So the next bounded move should stay validity-first and target the shared `brux1`-versus-`n3` overlap before changing model family.
   498|
   499|## Failure notes
   500|
   501|Record weak results honestly:
   502|- What failed first:
   503|  - the original extraction path was too expensive for large CAP EDFs until loading and entropy computation were made lighter
   504|- What failed next:
   505|  - the initial `3`-subject pilot could not support a valid LOSO baseline
   506|- What still fails now:
   507|  - the `6`-subject baseline still shows a large random-vs-LOSO gap and near-collapse on held-out bruxism sensitivity
   508|- How it showed up in artifacts:
   509|  - pass2 random CV was effectively perfect while LOSO was poor
   510|  - pass3 removed an obvious feature leak, but LOSO stayed weak
   511|- Why that matters:
   512|  - the current task setup is still too vulnerable to subject-specific or acquisition-specific cues
   513|
   514|## Current best explanation
   515|
   516|The current project bottleneck is still not model capacity. It is now the combination of:
   517|- tiny subject count
   518|- a label-separation pattern that looks strong under random window mixing but does not survive held-out-subject transfer
   519|- a harsher subject-level failure mode where partial positive windows do not translate into correct held-out subject calls
   520|- possible EDF / scoring-file mismatches for at least `n10` and partly `brux1`
   521|- annotation-aware `SLEEP-S2` filtering that is reproducible but still too coarse to isolate a more transferable physiological signature
   522|- a mixed `S2+MCAP` bucket whose overlap-event composition differs materially across subjects
   523|- window-level evaluation on single-subject folds
   524|
   525|## Best next bounded step
   526|
   527|Do not add model complexity yet.
   528|
   529|Next experiment:
   530|1. preserve `n10` as excluded from local `SLEEP-S2` reruns unless a fuller matching EDF is found
   531|2. keep `brux1` in the stage-aware subset only with explicitly in-range windows
   532|3. preserve the new overlap-event audit as evidence that the current mixed `S2+MCAP` bucket is heterogeneous by subject
   533|4. preserve the new matched EMG-family comparison as evidence that `A3-only` is currently the less-bad EMG overlap family on the verified subset
   534|5. preserve the new subject-threshold audit as evidence that the stronger EMG run fails because two controls still outrank the best bruxism subject
   535|6. preserve the new pass19 selection-aware rerun as the stronger current EMG-first working point
   536|7. preserve the new pass22 normalization-aware rerun as evidence that simple per-window `median_mad` extraction is **not** the fix for that working point
   537|8. preserve the new shared subject-score comparison as evidence that the current EMG gap is dominated by `brux2` collapse plus `n3` as the highest-score control
   538|9. preserve the new shared-time-position rerun as evidence that the timing concern was real but not sufficient: both bruxism subjects rise, yet all controls still outrank them and honest subject-level sensitivity stays `0.000`
   539|10. preserve the new matched strict-scaffold comparison as evidence that `C4-P4` does **not** rescue the stricter `A3-only` benchmark and that the timing-matched scaffold itself is now the bigger bottleneck than channel choice alone
   540|11. preserve the new strict-`A1-only` feasibility audit as evidence that the current hard shared-interval selector collapses `EMG1-EMG2 A1-only` to only `2` windows per subject and should not be treated as a trustworthy new benchmark surface
   541|12. preserve the new pass28 percentile-band rerun as evidence that softer timing control fixes the extraction-collapse problem but still leaves both bruxism subjects below all three controls on the honest LOSO subject surface
   542|13. preserve the new pass29 matched percentile-band comparison as evidence that `C4-P4` does beat matched `EMG1-EMG2` on the repaired `A1-only` scaffold, but only partially: `brux2` is recovered cleanly while `brux1` still trails `n3`, so the result ties rather than beats the older best honest subject-level baseline
   543|14. preserve the new pass30 cross-channel gap audit as evidence that the repaired percentile-band scaffold itself is now genuinely matched across channels and that the remaining honest bottleneck is narrower than “EMG is worse”: `brux1` still trails `n3` under both channels, while the main channel gap is `brux2` flipping only on `C4-P4`
   544|15. preserve the new pass31 recurrence audit as evidence that the suspected narrow `n3`-favoring trio is not the whole story on the repaired scaffold: `burst_fraction` recurs, but the strongest EMG control-favoring gap is still broader (`mean`, `max`, `ptp`, `zero_crossing_rate`)
   545|16. preserve the new pass32 broader morphology ablation as evidence that wholesale deletion is not the fix either: `EMG1-EMG2` still misses both bruxism subjects, `n3` stays above `brux1`, and the same ablation destroys the useful `brux2` recovery on `C4-P4`
   546|17. preserve the new pass33 smaller raw-location ablation as evidence that a narrower deletion is not the fix either: removing only `mean`, `min`, and `max` leaves `C4-P4` essentially unchanged but makes `EMG1-EMG2` worse by collapsing `brux1` while `n3` stays high
   547|18. next, keep the repaired percentile-band `A1-only` scaffold fixed and prefer a record-relative or within-record morphology representation audit before changing timing rules again or adding model complexity
   548|19. only after that consider a new model family
   549|
   550|## Files produced by the first runs
   551|
   552|- `projects/bruxism-cap/data/window_features_pass1.csv`
   553|- `projects/bruxism-cap/data/window_features_pass2.csv`
   554|- `projects/bruxism-cap/reports/random-window-cv-pass1.json`
   555|- `projects/bruxism-cap/reports/random-window-cv-pass2.json`
   556|- `projects/bruxism-cap/reports/loso-cv-pass2.json`
   557|- `projects/bruxism-cap/reports/random-window-cv-pass3-nosfreq.json`
   558|- `projects/bruxism-cap/reports/loso-cv-pass3-nosfreq.json`
   559|- `projects/bruxism-cap/data/window_features_pass4_s2.csv`
   560|- `projects/bruxism-cap/reports/random-window-cv-pass4-s2.json`
   561|- `projects/bruxism-cap/reports/loso-cv-pass4-s2.json`
   562|- `projects/bruxism-cap/reports/annotation-alignment-audit-pass4-s2.md`
   563|- `projects/bruxism-cap/reports/loso-cv-pass5-pass2-subjectagg.json`
   564|- `projects/bruxism-cap/reports/loso-cv-pass5-pass4-s2-subjectagg.json`
   565|- `projects/bruxism-cap/src/audit_subject_confound.py`
   566|- `projects/bruxism-cap/reports/subject-confound-audit-pass6.json`
   567|- `projects/bruxism-cap/reports/subject-confound-audit-pass6.md`
   568|- `projects/bruxism-cap/src/audit_overlap_event_mix.py`
   569|- `projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.json`
   570|- `projects/bruxism-cap/reports/overlap-event-mix-audit-pass8.md`
   571|- `projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv`
   572|- `projects/bruxism-cap/reports/random-window-cv-pass10-s2-mcap-a3-only.json`
   573|- `projects/bruxism-cap/reports/loso-cv-pass10-s2-mcap-a3-only.json`
   574|- `projects/bruxism-cap/reports/pass10-s2-mcap-a3-only.md`
   575|- `projects/bruxism-cap/src/audit_rule_survival.py`
   576|- `projects/bruxism-cap/reports/rule-survival-audit-pass11.json`
   577|- `projects/bruxism-cap/reports/pass11-rule-survival-audit.md`
   578|- `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a1_only_matched14.csv`
   579|- `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a3_only_matched14.csv`
   580|- `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a1-only-matched14.json`
   581|- `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json`
   582|- `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a3-only-matched14.json`
   583|- `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a3-only-matched14.json`
   584|- `projects/bruxism-cap/reports/pass12-exclusive-a1-vs-a3-matched14.md`
   585|- `projects/bruxism-cap/data/window_features_pass13_emg_s2_mcap_a1_only_matched14.csv`
   586|- `projects/bruxism-cap/reports/random-window-cv-pass13-emg-s2-mcap-a1-only-matched14.json`
   587|- `projects/bruxism-cap/reports/loso-cv-pass13-emg-s2-mcap-a1-only-matched14.json`
   588|- `projects/bruxism-cap/reports/pass13-emg-vs-c4-a1-only-matched14.md`
   589|- `projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv`
   590|- `projects/bruxism-cap/reports/random-window-cv-pass14-emg-s2-mcap-a3-only-matched14.json`
   591|- `projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json`
   592|- `projects/bruxism-cap/reports/pass14-emg-a1-vs-a3-matched14.md`
   593|- `projects/bruxism-cap/src/audit_subject_thresholds.py`
   594|- `projects/bruxism-cap/reports/subject-threshold-audit-pass15-emg-a3-vs-c4-a1.json`
   595|- `projects/bruxism-cap/reports/pass15-emg-a3-threshold-audit.md`
   596|- `projects/bruxism-cap/src/audit_emg_feature_validity.py`
   597|- `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.json`
   598|- `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.md`
   599|- `projects/bruxism-cap/reports/random-window-cv-pass19-emg-a3-envelope-selected-matched14.json`
   600|- `projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json`
   601|- `projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md`
   602|- `projects/bruxism-cap/reports/random-window-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`
   603|- `projects/bruxism-cap/reports/loso-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`
   604|- `projects/bruxism-cap/reports/pass20-emg-a3-envelope-selected-nomean-matched14.md`
   605|- `projects/bruxism-cap/src/audit_emg_envelope_family.py`
   606|- `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.json`
   607|- `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.md`
   608|- `projects/bruxism-cap/src/compare_subject_score_surfaces.py`
   609|- `projects/bruxism-cap/reports/subject-score-comparison-pass23-emg-pass19-vs-c4-pass12.json`
   610|- `projects/bruxism-cap/reports/pass23-emg-pass19-vs-c4-pass12-subject-score-comparison.md`
   611|- `projects/bruxism-cap/data/window_features_pass22_emg_s2_mcap_a3_only_matched14_medianmad.csv`
   612|- `projects/bruxism-cap/reports/random-window-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`
   613|- `projects/bruxism-cap/reports/loso-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`
   614|- `projects/bruxism-cap/reports/pass22-emg-a3-envelope-selected-medianmad-matched14.md`
   615|- `projects/bruxism-cap/src/select_time_position_matched_windows.py`
   616|- `projects/bruxism-cap/data/window_features_pass25_emg_s2_mcap_a3_only_full_envelope.csv`
   617|- `projects/bruxism-cap/data/window_features_pass25_emg_s2_mcap_a3_only_timepos10_envelope.csv`
   618|- `projects/bruxism-cap/reports/time-position-match-pass25-emg-a3.json`
   619|- `projects/bruxism-cap/reports/random-window-cv-pass25-emg-a3-timepos10-selected.json`
   620|- `projects/bruxism-cap/reports/loso-cv-pass25-emg-a3-timepos10-selected.json`
   621|- `projects/bruxism-cap/reports/pass25-emg-a3-time-position-matched-selected.md`
   622|- `projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_full_envelope.csv`
   623|- `projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_timepos10_envelope.csv`
   624|- `projects/bruxism-cap/reports/time-position-match-pass26-c4-a3.json`
   625|- `projects/bruxism-cap/reports/random-window-cv-pass26-c4-a3-timepos10-selected.json`
   626|- `projects/bruxism-cap/reports/loso-cv-pass26-c4-a3-timepos10-selected.json`
   627|- `projects/bruxism-cap/reports/pass26-c4-a3-time-position-matched-vs-emg.md`
   628|- `projects/bruxism-cap/data/window_features_pass27_emg_s2_mcap_a1_only_full_envelope.csv`
   629|- `projects/bruxism-cap/data/window_features_pass27_emg_s2_mcap_a1_only_timepos2_envelope.csv`
   630|- `projects/bruxism-cap/reports/time-position-match-pass27-emg-a1.json`
   631|- `projects/bruxism-cap/reports/pass27-emg-a1-time-position-feasibility.md`
   632|- `projects/bruxism-cap/data/window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`
   633|- `projects/bruxism-cap/reports/time-position-match-pass28-emg-a1-pct10-90.json`
   634|- `projects/bruxism-cap/reports/random-window-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`
   635|- `projects/bruxism-cap/reports/loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`
   636|- `projects/bruxism-cap/reports/pass28-emg-a1-percentile-band-rerun.md`
   637|- `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_full_envelope.csv`
   638|- `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`
   639|- `projects/bruxism-cap/reports/time-position-match-pass29-c4-a1-pct10-90.json`
   640|- `projects/bruxism-cap/reports/random-window-cv-pass29-c4-a1-pct10-90-timepos10-selected.json`
   641|- `projects/bruxism-cap/reports/loso-cv-pass29-c4-a1-pct10-90-timepos10-selected.json`
   642|- `projects/bruxism-cap/reports/pass29-c4-a1-percentile-band-vs-emg.md`
   643|- `projects/bruxism-cap/src/audit_percentile_band_channel_gap.py`
   644|- `projects/bruxism-cap/reports/feature-validity-audit-pass30-a1-pct-channel-gap.json`
   645|- `projects/bruxism-cap/reports/pass30-a1-percentile-band-channel-gap-audit.md`
   646|- `projects/bruxism-cap/src/audit_percentile_band_n3_family_recurrence.py`
   647|- `projects/bruxism-cap/reports/feature-validity-audit-pass31-a1-pct-n3-family.json`
   648|- `projects/bruxism-cap/reports/pass31-a1-percentile-band-n3-family-recurrence.md`
   649|- `projects/bruxism-cap/src/run_pass32_broad_morphology_ablation.py`
   650|- `projects/bruxism-cap/reports/loso-cv-pass32-emg-a1-pct10-90-broad-ablation.json`
   651|- `projects/bruxism-cap/reports/loso-cv-pass32-c4-a1-pct10-90-broad-ablation.json`
   652|- `projects/bruxism-cap/reports/pass32-broad-morphology-ablation-summary.json`
   653|- `projects/bruxism-cap/reports/pass32-broad-morphology-ablation.md`
   654|- `projects/bruxism-cap/src/run_pass33_raw_location_ablation.py`
   655|- `projects/bruxism-cap/reports/loso-cv-pass33-emg-a1-pct10-90-rawloc-ablation.json`
   656|- `projects/bruxism-cap/reports/loso-cv-pass33-c4-a1-pct10-90-rawloc-ablation.json`
   657|- `projects/bruxism-cap/reports/pass33-raw-location-ablation-summary.json`
   658|- `projects/bruxism-cap/reports/pass33-raw-location-ablation.md`
   659|
   660|## Short takeaway
   661|
   662|The first real `bruxism-cap` runs succeeded as project infrastructure and failed as a trustworthy detector. That is a useful result. After pass4, the follow-up alignment audit, the pass5 subject-level aggregation hardening, the pass6 subject-versus-label confound audit, the pass8 overlap-event mix audit, the new pass11 rule-survival audit, the pass12 matched-family comparison, and the later EMG-first matched reruns plus threshold audit, the repo now has a tighter explanation of the failure surface: simple `SLEEP-S2` matching did not fix held-out-subject transfer, subject-level detection is still the harsher interpretation surface, the current feature tables seem to separate the observed labels inside the seen-subject pool more easily than they separate subject identity, the mixed `S2+MCAP` subset itself is heterogeneous by overlap-event family, overlap-family comparisons must preserve the availability context, and the stronger EMG run fails because two controls still outrank the best bruxism subject. Under matched conditions, exclusive `A1-only` is more promising than exclusive `A3-only` for `C4-P4`, while `EMG1-EMG2` looks less bad under exclusive `A3-only` than under `A1-only`. The later EMG feature work sharpens that again: the pass18 envelope / burst family is more useful when the older spectral / ratio family is excluded at train time, but even pass19 still leaves `n3` and `n5` above `brux1` and keeps subject-level sensitivity at `0.000`. Pass20 then preserves another equally useful negative result: naive `mean` removal does not fix that bottleneck and instead makes `brux1` collapse. Pass21 narrows it one step further without changing the model recipe: the retained family is doing something real, but `sample_entropy` and `burst_fraction` still help the highest-score controls while `brux1`'s larger raw amplitude-envelope features remain net-negative under the learned coefficients. So the EMG-first bottleneck is now narrower still: preserve the pass19 retained fa... [truncated]
   663|

SOURCE: /home/hermes/work/ai-lab/projects/bruxism-cap/reports/campaign-handoff-2026-05-05.md
     1|# Bruxism CAP campaign handoff
     2|
     3|Date: 2026-05-05
     4|Status: campaign-level synthesis completed after the matched comparator branch, honest-anchor verdict branch, and periodic literature framing review.
     5|
     6|## Campaign verdict
     7|
     8|Continue the current autoresearch loop.
     9|
    10|But continue it narrowly and honestly: do not read the latest EMG passes as a breakthrough, and do not pause for a benchmark reframing pivot.
    11|
    12|The durable verdict is:
    13|- keep the repo on the current CAP, EMG-first, leakage-aware benchmark framing
    14|- keep `pass29 C4-P4` as the honest comparison-channel anchor
    15|- preserve `pass34` record-relative and `pass35` shape as mixed-result EMG clues, not as settled benchmark wins
    16|- queue exactly one more bounded EMG representation composition test before reopening channel choice, extraction, privacy, or LLM/RL branches
    17|
    18|## What the board learned
    19|
    20|### 1. The framing held up
    21|The literature branch did not invalidate the current project shape. Newer translational bruxism work is more wearable-, multi-night-, and intervention-oriented, but it still does not expose a clearly better open benchmark than CAP.
    22|
    23|So the repo should stay:
    24|- EMG-first
    25|- CAP-based
    26|- explicit about validity limits
    27|- separated from future wearable/intervention ambitions
    28|
    29|### 2. The repaired `A1-only` scaffold is now good enough to ask small representation questions
    30|The board already paid down the extraction-validity confusion:
    31|- strict shared-time-position matching was too brittle on `EMG1-EMG2 A1-only`
    32|- the softer percentile-band selector restored a reproducible five-subject / ten-windows-per-subject scaffold
    33|- the matched `C4-P4` comparator on the same rows showed that channel effects and scaffold effects can now be discussed separately
    34|
    35|That does not make the benchmark solved, but it does make one-step representation tests interpretable.
    36|
    37|### 3. Negative EMG results became more precise, not less useful
    38|The current negative result is no longer a vague “EMG loses.” It is now:
    39|- `pass34` record-relative fixes the `brux2` versus `n3` reversal and removes the `n3` false positive, but still leaves `brux1` below threshold
    40|- `pass35` shape nearly closes `n3 - brux1` and keeps `brux2` above `n3`, but still leaves both bruxism subjects below threshold
    41|- neither pass materially improves the honest subject-level decision outcome beyond `balanced_accuracy 0.500`, `sensitivity 0.000`, `specificity 1.000`
    42|
    43|So the benchmark has learned something real: the remaining blocker is threshold-crossing subject sensitivity, especially `brux1`, not just generic score inversion.
    44|
    45|### 4. The comparator story stayed important
    46|`pass29 C4-P4` remains the only repaired-scaffold anchor with positive subject-level sensitivity (`0.500`) and clean specificity (`1.000`).
    47|
    48|At the same time, the matched record-relative `C4-P4` rebuild regressed, which means the EMG record-relative gain is not a channel-agnostic scaffold fix. That is why the right next question is compositional EMG testing, not “switch to C4 forever” and not “declare EMG fixed.”
    49|
    50|### 5. Future branches are real, but not yet the next board move
    51|The privacy/PET and LLM/RL roadmap notes are now legitimate downstream branches, but the board learned they should remain wiki-first until the current benchmark reaches a more stable handoff point. Promoting them now would blur the current experiment interpretation surface.
    52|
    53|## Should the autoresearch loop continue or pause?
    54|
    55|Continue.
    56|
    57|Reason:
    58|- the literature branch says no benchmark pivot is required
    59|- the experiment branch produced a sharper bounded hypothesis rather than a dead end
    60|- the current benchmark still has one clean next representation question that can be asked on a fixed scaffold
    61|
    62|Do not pause for reframing yet.
    63|
    64|But the loop should continue on a narrowed anchor definition:
    65|- external honest comparator: `pass29 C4-P4`
    66|- EMG clue set: `pass34` record-relative plus `pass35` compact shape
    67|- benchmark frame: repaired five-subject percentile-band `A1-only` scaffold, same LOSO decision surface
    68|
    69|## Single best next bounded task
    70|
    71|Run one strict composition audit on the same repaired scaffold:
    72|- start from the `pass34` record-relative `EMG1-EMG2` feature table / audit path
    73|- add the same four compact shape features used in `pass35`
    74|- keep subject set, selected rows, LOSO split, model family, and decision checks fixed
    75|- compare only `pass34` versus `record-relative + shape`
    76|
    77|This is the best next task because it tests the exact remaining campaign hypothesis: whether the two best mixed EMG gains compose honestly on the same benchmark.
    78|
    79|## What should not be queued next
    80|
    81|Do not queue any of these before the composition audit:
    82|- another deletion-first ablation
    83|- a new channel switch or fusion branch
    84|- a benchmark pivot away from CAP
    85|- a privacy/PET implementation task
    86|- an LLM/RL prototype task
    87|
    88|Those branches may still matter later, but they are less justified than the one unresolved composition question now sitting directly on the current benchmark.
    89|
    90|## Bottom line
    91|
    92|The campaign did not produce a win claim. It produced a disciplined narrowing.
    93|
    94|The repo now knows that:
    95|- CAP plus `EMG1-EMG2` still makes sense as the bounded open benchmark
    96|- the repaired scaffold is valid enough for one more small representation test
    97|- `pass34` and `pass35` are both useful mixed results but neither is an honest standalone EMG breakthrough
    98|- the best next move is one bounded `record-relative + shape` audit, not a pivot
    99|

SOURCE: /home/hermes/work/ai-lab/projects/bruxism-cap/reports/periodic-translational-framing-check-2026-05-05.md
     1|# Periodic translational framing check
     2|
     3|Date: 2026-05-05
     4|Status: literature framing review completed; current CAP EMG-first benchmark framing still holds as a bounded open-data benchmark, with no immediate experiment pivot required
     5|
     6|## Objective
     7|
     8|Check whether the repo's current framing still makes scientific sense:
     9|- CAP kept as the open benchmark scaffold
    10|- `EMG1-EMG2` treated as the primary channel
    11|- benchmark read as a leakage-aware reproducibility exercise, not a clinical detector
    12|
    13|The question is not whether newer wearable science is more exciting in the abstract.
    14|The question is whether that newer translational literature now makes the current repo framing misleading or obsolete.
    15|
    16|## Sources inspected
    17|
    18|Previously ingested repo sources:
    19|- `wiki/raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md`
    20|- `wiki/raw/articles/portable-emg-temporal-patterns-2026.md`
    21|- `wiki/raw/articles/home-vs-lab-wearable-emg-2022.md`
    22|- `wiki/raw/articles/sleep-bruxism-emg-only-setups-2020.md`
    23|- `wiki/raw/articles/advanced-sensing-system-sleep-bruxism-emg-2024.md`
    24|- `wiki/raw/articles/imu-sleep-bruxism-field-detection-2026.md`
    25|
    26|Newly inspected this pass:
    27|- `wiki/raw/articles/sleep-bruxism-analysis-window-portable-emg-2026.md`
    28|- `wiki/raw/articles/sleep-bruxism-emg-frequency-spectrum-pilot-2026.md`
    29|- `wiki/raw/articles/sleep-bruxism-contingent-electrical-stimulation-2024.md`
    30|- `wiki/raw/articles/sleep-bruxism-vibratory-feedback-2024.md`
    31|
    32|Repo framing inspected against:
    33|- `projects/bruxism-cap/README.md`
    34|- `projects/bruxism-cap/reports/first-baseline.md`
    35|- `wiki/concepts/bruxism-cap.md`
    36|- `wiki/queries/bruxism-better-project-and-data-options-2026-05-04.md`
    37|
    38|## Short verdict
    39|
    40|Yes: the current CAP EMG-first framing still makes sense.
    41|
    42|More precisely:
    43|1. `EMG1-EMG2` still looks like the right translationally aligned primary signal family.
    44|2. CAP still looks acceptable as a small open benchmark, even though it is clearly not the ideal clinical or product-shaped dataset.
    45|3. The stronger gap is still between open benchmark science and real wearable/intervention science, not between EMG and some obviously better open replacement inside the repo.
    46|4. The literature supports better future project shape more strongly than it supports a better immediate public benchmark.
    47|
    48|## What still looks justified
    49|
    50|### 1. EMG-first is still the right translational framing
    51|The 2024 meta-analysis still supports portable EMG as the practical sensing modality, even though evidence quality is limited by study heterogeneity and design weaknesses. The newer 2026 portable-EMG literature pushes even harder in the same direction rather than reversing it.
    52|
    53|This means the repo would now look less aligned with the field if it moved back toward an EEG-first story.
    54|
    55|### 2. CAP is still defensible as a benchmark scaffold
    56|Nothing in the new sources produced a clearly better open benchmark that should replace CAP now.
    57|
    58|The alternative directions are scientifically interesting but operationally weaker for this repo today:
    59|- portable EMG validation studies are usually proprietary or cohort-limited
    60|- home/wearable studies are often not openly downloadable as a reusable benchmark
    61|- IMU/jaw-motion work is promising but still tiny and custom
    62|- intervention papers depend on device-specific setups rather than shared public corpora
    63|
    64|So CAP remains a reasonable compromise between openness, auditability, and bounded scope.
    65|
    66|### 3. The repo's caution about labels and validity remains scientifically correct
    67|The 2020 EMG-only scoring warning still matters: EMG is the practical sensor, not the gold-standard label source.
    68|
    69|That matches the repo's current posture well. The benchmark is not claiming clinical event truth from raw EMG alone; it is using a public polysomnography-derived dataset to test whether a small reproducible EMG-first pipeline transfers honestly across subjects.
    70|
    71|### 4. The repo is right to distinguish benchmark clarity from product realism
    72|The newest translational papers are more wearable-minded, more longitudinal, and more intervention-aware. But that does not automatically create a better open benchmark.
    73|
    74|So the repo's distinction still holds:
    75|- better project shape in the long run: portable, home, multi-night, possibly intervention-linked EMG
    76|- better open benchmark right now: not clearly available beyond CAP
    77|
    78|## What the newer literature adds
    79|
    80|### 1. Multi-night and home context matter more than one-night lab framing
    81|The 2026 multi-day portable EMG paper and the earlier home-vs-lab wearable study both push toward ecological monitoring rather than single-night lab-only inference.
    82|
    83|Implication: CAP should continue to be framed as a proxy benchmark, not as a miniature version of the final real-world task.
    84|
    85|### 2. Window-definition choices matter in wearable-style scoring
    86|The 2026 masseter-EMG analysis-window paper showed that event rates change depending on whether likely wakefulness near bedtime and final awakening is excluded.
    87|
    88|Implication: the repo's obsession with explicit extraction windows, overlap rules, and matched scaffolds is scientifically well aligned. This is not over-engineering; translational papers are also sensitive to analysis-period definition.
    89|
    90|### 3. EMG may matter for more than crude event counts
    91|The 2026 frequency-spectrum pilot suggests that EMG spectral descriptors may separate clinically relevant phenotypes better than conventional event/time indices alone.
    92|
    93|Implication: an EMG-first framing does not mean the repo should only favor simplistic count-like features. Some frequency-domain structure may still be translationally meaningful, even if the current tiny benchmark has not yet converted that into honest subject transfer.
    94|
    95|### 4. The field is moving toward intervention-aware wearables
    96|The 2024 contingent electrical stimulation and vibratory-feedback papers reinforce that wearable EMG is increasingly tied to closed-loop management, not only passive detection.
    97|
    98|Implication: future science may care about longitudinal responsiveness and symptom coupling, not just binary event classification. But that is a future branch, not a reason to distort the current benchmark into an intervention claim.
    99|
   100|## Remaining gaps between the repo and stronger wearable/intervention science
   101|
   102|1. Single-night open CAP benchmarking is still far from the multi-night ecological monitoring setup that newer portable-EMG work prefers.
   103|2. The repo still lacks symptom, pain, or intervention outcomes, so it cannot speak to management-oriented utility.
   104|3. CAP-derived labels are still a compromise relative to carefully validated PSG plus audio/video or device-specific intervention studies.
   105|4. The current task is still binary `bruxism` vs `control`, while newer translational work increasingly cares about phenotype, severity, timing context, and response to feedback.
   106|5. Open benchmark availability still lags far behind the conceptual maturity of the wearable science.
   107|
   108|These are real gaps, but they are exactly the kind that justify keeping the repo modest rather than forcing a premature pivot.
   109|
   110|## One concrete repo-level implication
   111|
   112|Keep the current benchmark loop fixed, but preserve translational claims more explicitly as a separate future branch:
   113|- current branch: open, leakage-aware CAP benchmark for honest subject transfer
   114|- future branch: portable/home/multi-night/intervention-aware EMG science once a suitable dataset or recording path exists
   115|
   116|In practice, this means the repo should not treat every wearable/intervention paper as a reason to rewrite the immediate benchmark task.
   117|
   118|## Immediate experiment decision
   119|
   120|No immediate experiment should change.
   121|
   122|Specifically:
   123|- do not abandon CAP
   124|- do not demote `EMG1-EMG2` back behind `C4-P4`
   125|- do not force an intervention-oriented metric into the current benchmark loop
   126|- do not pivot away from benchmark-validity work just because the translational literature is more product-shaped
   127|
   128|## Bottom line
   129|
   130|The translational literature has become more strongly wearable, longitudinal, and intervention-aware, but it has not invalidated the repo's current framing.
   131|
   132|If anything, it sharpens it:
   133|- keep `EMG1-EMG2` as the primary scientific direction
   134|- keep CAP as the bounded open benchmark
   135|- keep explicit validity caveats
   136|- keep benchmark improvement separate from claims about real wearable usefulness
   137|
   138|So the right read is not "pivot now."
   139|It is "stay EMG-first, stay honest about CAP's limits, and postpone the wearable/intervention jump until data access catches up."
   140|

SOURCE: /home/hermes/work/ai-lab/projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit.md
     1|# Pass 36 — record-relative plus compact shape composition audit on repaired `A1-only` EMG scaffold
     2|
     3|Date: 2026-05-05
     4|Status: bounded composition audit completed; added the four pass35 compact shape descriptors on top of the existing pass34 record-relative `EMG1-EMG2` percentile-band table while keeping selected rows, subject set, LOSO split, train-time exclusions, and model family fixed.
     5|
     6|## Why this pass exists
     7|
     8|This pass asks one exact follow-up question from the campaign handoff:
     9|- start from the existing pass34 record-relative audit path and feature table
    10|- keep the repaired five-subject percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold fixed
    11|- keep the same train-time exclusions fixed: `^bp_, ^rel_bp_, ^ratio_`
    12|- keep the same `logreg` LOSO interpretation surface
    13|- add only the same four compact shape features from pass35: `skewness, kurtosis, hjorth_mobility, hjorth_complexity`
    14|- compare only pass34 versus `record-relative + shape`
    15|
    16|## Artifacts
    17|- Runner script: `projects/bruxism-cap/src/run_pass36_record_relative_shape_composition_audit.py`
    18|- Composed feature table: `projects/bruxism-cap/data/window_features_pass36_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape.csv`
    19|- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json`
    20|- Summary JSON: `projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit-summary.json`
    21|- Summary report: `projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit.md`
    22|
    23|## Scaffold parity checks
    24|- pass34 selected-row counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
    25|- pass35 selected-row counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
    26|- pass36 selected-row counts: `{'brux1': 10, 'brux2': 10, 'n11': 10, 'n3': 10, 'n5': 10}`
    27|- warnings:
    28|- none
    29|
    30|## Honest LOSO subject-level comparison
    31|- pass34 balanced accuracy: `0.500`
    32|- pass36 balanced accuracy: `0.750`
    33|- pass34 sensitivity: `0.000`
    34|- pass36 sensitivity: `0.500`
    35|- pass34 specificity: `1.000`
    36|- pass36 specificity: `1.000`
    37|- pass34 best-bruxism-minus-highest-control margin: `+0.041`
    38|- pass36 best-bruxism-minus-highest-control margin: `+0.319`
    39|
    40|Subject score deltas:
    41|- `brux1`: pass34 `0.180` -> pass36 `0.112` (delta `-0.068`) | predicted `control` -> `control`
    42|- `brux2`: pass34 `0.480` -> pass36 `0.808` (delta `+0.328`) | predicted `control` -> `bruxism`
    43|- `n3`: pass34 `0.439` -> pass36 `0.068` (delta `-0.370`) | predicted `control` -> `control`
    44|- `n5`: pass34 `0.379` -> pass36 `0.385` (delta `+0.006`) | predicted `control` -> `control`
    45|- `n11`: pass34 `0.376` -> pass36 `0.489` (delta `+0.112`) | predicted `control` -> `control`
    46|
    47|## Required gap checks
    48|- pass34 `n3 - brux1` gap: `+0.259`
    49|- pass36 `n3 - brux1` gap: `-0.043`
    50|- pass34 `brux2 - n3` gap: `+0.041`
    51|- pass36 `brux2 - n3` gap: `+0.740`
    52|- pass34 best-bruxism-minus-highest-control margin: `+0.041`
    53|- pass36 best-bruxism-minus-highest-control margin: `+0.319`
    54|
    55|## Shape-aware gap contributors
    56|Top positive contributors keeping `n3` above `brux1`:
    57|  - `mean` contribution delta `+46.577` | z-mean delta `-655.647` | raw-mean delta `-0.783179`
    58|  - `rectified_std` contribution delta `+3.803` | z-mean delta `-13.880` | raw-mean delta `-10.538216`
    59|  - `envelope_cv` contribution delta `+1.422` | z-mean delta `-11.682` | raw-mean delta `-32.462936`
    60|  - `p95_abs` contribution delta `+0.854` | z-mean delta `-4.196` | raw-mean delta `-6.312733`
    61|  - `ptp` contribution delta `+0.831` | z-mean delta `-20.358` | raw-mean delta `-85.551894`
    62|  - `kurtosis` contribution delta `+0.674` | z-mean delta `-1.626` | raw-mean delta `-27.241218`
    63|
    64|Top negative contributors against `brux2` versus `n3`:
    65|  - `hjorth_complexity` contribution delta `-0.612` | z-mean delta `+1.495` | raw-mean delta `+1.014378`
    66|  - `skewness` contribution delta `-0.180` | z-mean delta `-0.273` | raw-mean delta `-0.307258`
    67|  - `kurtosis` contribution delta `-0.143` | z-mean delta `+0.095` | raw-mean delta `+2.197268`
    68|  - `p95_abs` contribution delta `-0.028` | z-mean delta `-0.177` | raw-mean delta `-0.920743`
    69|  - `rectified_mean` contribution delta `-0.027` | z-mean delta `-0.100` | raw-mean delta `-0.208240`
    70|  - `envelope_mean` contribution delta `-0.027` | z-mean delta `-0.100` | raw-mean delta `-0.207593`
    71|
    72|## Verdict
    73|The two best current EMG gains do compose into a subject-sensitivity improvement on this repaired scaffold: `brux2` crosses the subject threshold (`0.480` -> `0.808`) and `n3` drops sharply (`0.439` -> `0.068`), but `brux1` gets worse (`0.180` -> `0.112`), so the gain is real but not a clean across-bruxism fix.
    74|
    75|## Interpretation
    76|1. This is an apples-to-apples composition audit: the pass34 selected rows stay fixed and the only added information is the same bounded pass35 shape family.
    77|2. The key decision question is whether stacking the two best EMG clues finally clears honest subject-level sensitivity or at least improves the pass34 subject-ordering surface without introducing row drift.
    78|3. The composition does help, but only through `brux2`: it rises above threshold while `brux1` falls further below threshold, so this is a real but incomplete benchmark improvement rather than a clean all-subject EMG fix.
    79|

SOURCE: /home/hermes/work/ai-lab/projects/bruxism-cap/reports/pass35-patched-emg-vs-matched-c4-anchor-comparison.md
     1|# Pass 35/34 synthesis — patched EMG vs matched C4 on the repaired `A1-only` scaffold
     2|
     3|Date: 2026-05-05
     4|Status: comparison/synthesis completed; compared the two mixed EMG repair paths against the matched `C4-P4` comparator to separate channel effects from scaffold effects before choosing the next anchor.
     5|
     6|## Runs compared
     7|- `pass34` `EMG1-EMG2` record-relative audit on the repaired percentile-band `A1-only` scaffold
     8|- `pass35` `EMG1-EMG2` compact shape-feature expansion on the same scaffold
     9|- `pass29` `C4-P4` matched percentile-band baseline comparator
    10|- `pass35` `C4-P4` record-relative comparator rebuild on the same scaffold
    11|
    12|## Honest subject-level verdict
    13|`C4-P4` still wins on the narrow subject-level benchmark, but only weakly and not cleanly after the matched transform test.
    14|
    15|- best EMG mixed results:
    16|  - `pass34` subject balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`
    17|  - `pass35` shape subject balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`
    18|- matched transformed `C4-P4`:
    19|  - `pass35` subject balanced accuracy `0.583`, sensitivity `0.500`, specificity `0.667`
    20|- clean matched comparison-channel anchor still remains the pre-transform `pass29 C4-P4` result:
    21|  - subject balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
    22|
    23|So the channel story is now: `C4-P4` still beats EMG on honest subject-level detection, but the matched record-relative comparator shows that this is not because the repaired scaffold was universally fixed. The transform helps EMG more than it helps `C4-P4`, yet neither transformed branch resolves the benchmark cleanly.
    24|
    25|## What the comparison says about channel effects vs scaffold effects
    26|### Channel effect that survives
    27|`C4-P4` remains the only channel that actually produces a positive held-out bruxism subject on this scaffold. Even after the transform regression, it still has subject sensitivity `0.500` while both EMG mixed results stay at `0.000`.
    28|
    29|### Scaffold bottleneck that survives
    30|Both channels are still bottlenecked by the same repaired `A1-only` benchmark rather than only by feature family choice:
    31|- EMG still cannot push either `brux1` or `brux2` above the `0.5` subject threshold.
    32|- `C4-P4` can no longer keep both the `brux2` separator and clean controls once the matched transform is applied.
    33|- The original matched audit already showed the shared bottleneck: `brux1` versus `n3` stayed unresolved under both channels on the same selected rows.
    34|
    35|This means the repo should not read the latest evidence as either:
    36|- “EMG is now fixed”, or
    37|- “C4 is universally better regardless of representation.”
    38|
    39|Instead, the scaffold is still fragile enough that each representation tweak repairs one failure surface while exposing another.
    40|
    41|## EMG anchor decision
    42|For the next EMG-first representation step, promote `pass35` shape to the new mixed-result EMG anchor.
    43|
    44|Why `pass35` shape beats `pass34` record-relative as the working anchor:
    45|- same honest subject-level headline (`0.500` balanced accuracy, `0.000` sensitivity, `1.000` specificity)
    46|- better symmetric gap repair:
    47|  - `pass34`: `brux2 - n3 = +0.041`, `n3 - brux1 = +0.259`
    48|  - `pass35` shape: `brux2 - n3 = +0.174`, `n3 - brux1 = +0.009`
    49|- keeps all controls below threshold, unlike transformed `C4-P4`
    50|- does not depend on a transform that the matched comparator just showed to be non-portable across channels
    51|
    52|So `pass34` should be preserved as an important clue about EMG-specific normalization, but `pass35` shape is the stronger anchor for the next bounded EMG-only increment because it improves both named score gaps at once on the unchanged scaffold.
    53|
    54|## Comparator-anchor decision
    55|Do not replace the comparison-channel anchor with transformed `pass35 C4-P4`.
    56|Keep `pass29 C4-P4` as the clean comparison anchor, and keep `pass35 C4-P4` only as evidence that the record-relative transform is not a channel-agnostic scaffold upgrade.
    57|
    58|## Exact next bounded step
    59|Run one EMG-only follow-up from the new `pass35` shape anchor:
    60|- keep the repaired percentile-band `A1-only` scaffold fixed
    61|- keep `logreg` LOSO and the same train-time exclusions fixed
    62|- keep the compact shape family already added
    63|- add exactly one small within-record normalization layer to the shape-sensitive EMG features only, then compare against `pass35` shape
    64|
    65|The key discipline is not to reopen channel choice or extraction yet. The bounded question should be: can the EMG shape anchor recover the remaining `brux1` deficit without losing the cleaner control ordering that `pass35` shape achieved?
    66|

SOURCE: /home/hermes/work/ai-lab/wiki/concepts/bruxism-cap.md
     1|---
     2|title: Bruxism CAP
     3|created: 2026-05-03
     4|updated: 2026-05-05
     5|type: concept
     6|tags: [dataset, evaluation, experiment, workflow, notes]
     7|sources:
     8|  - raw/articles/cap-sleep-database-physionet-2012.md
     9|  - raw/articles/bruxism-single-channel-eeg-2024.md
    10|  - raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md
    11|---
    12|
    13|# Bruxism CAP
    14|
    15|`bruxism-cap` is now the main active `ai-lab` project. It is a deliberately small public-data pilot for bruxism detection from EEG/EMG signals using the PhysioNet CAP Sleep Database. The goal is not a clinical claim or a deep model; the goal is to build a reproducible, leakage-aware baseline that can be extended later. As of `2026-05-04`, the project is now explicitly framed as an EMG-first benchmark: `EMG1-EMG2` is the primary next-pass channel and `C4-P4` is the comparison channel. [[bruxism-eeg-emg-starter-project-2026-05-03]] [[bruxism-cap-first-baseline-lessons-2026-05-03]] [[bruxism-cap-annotation-alignment-audit-2026-05-03]] [[ai-lab-learning-path]] [[artifact-card-sft]]
    16|
    17|## Why this is the current focus
    18|- It is grounded in open data that can be reproduced end to end.
    19|- It is small enough to run locally on the VPS or MacBook without needing a GPU first.
    20|- It teaches EDF loading, channel inspection, feature extraction, and subject-aware evaluation.
    21|- It is a better immediate lab target than continuing another fine-tuning branch before a new non-text pipeline is running.
    22|
    23|## Current scope
    24|- Dataset: CAP Sleep Database subset beginning with `brux1`, `brux2`, and a few controls.
    25|- Task: binary `bruxism` vs `control` classification.
    26|- Modeling: classical handcrafted features plus simple baselines such as logistic regression, random forest, and SVM.
    27|- Evaluation: compare random-window cross-validation against leave-one-subject-out cross-validation.
    28|
    29|## Current repo status
    30|- Scaffold exists under `projects/bruxism-cap/`.
    31|- The first baseline report now records ten concrete stages:
    32|  - a `3`-subject pilot (`pass1`)
    33|  - the first valid `6`-subject baseline (`pass2`)
    34|  - a first autoresearch-motivated rerun that excludes explicit sampling-rate proxy features from training (`pass3`)
    35|  - a first annotation-aware rerun using `SLEEP-S2` windows from RemLogic sidecars on a stage-valid `5`-subject subset (`pass4`)
    36|  - a subject-level LOSO hardening rerun (`pass5`)
    37|  - a subject-versus-label confound audit (`pass6`)
    38|  - a tighter event-aware rerun that keeps only `SLEEP-S2` windows overlapping CAP micro-events (`pass7`)
    39|  - a narrower single-family rerun that keeps only `SLEEP-S2` windows overlapping `MCAP-A3` (`pass9`)
    40|  - a stricter exclusive single-family rerun that keeps only `SLEEP-S2` windows with `MCAP-A3` overlap and excludes simultaneous `MCAP-A1/A2` overlap (`pass10`)
    41|  - a compact rule-survival audit that tracks how much each overlap rule changes per-subject and per-label window availability before any model rerun (`pass11`)
    42|- Current saved artifacts include:
    43|  - `projects/bruxism-cap/data/window_features_pass1.csv`
    44|  - `projects/bruxism-cap/data/window_features_pass2.csv`
    45|  - `projects/bruxism-cap/reports/random-window-cv-pass1.json`
    46|  - `projects/bruxism-cap/reports/random-window-cv-pass2.json`
    47|  - `projects/bruxism-cap/reports/loso-cv-pass2.json`
    48|  - `projects/bruxism-cap/reports/random-window-cv-pass3-nosfreq.json`
    49|  - `projects/bruxism-cap/reports/loso-cv-pass3-nosfreq.json`
    50|  - `projects/bruxism-cap/data/window_features_pass4_s2.csv`
    51|  - `projects/bruxism-cap/reports/random-window-cv-pass4-s2.json`
    52|  - `projects/bruxism-cap/reports/loso-cv-pass4-s2.json`
    53|  - `projects/bruxism-cap/reports/annotation-alignment-audit-pass4-s2.md`
    54|  - `projects/bruxism-cap/reports/subject-confound-audit-pass6.json`
    55|  - `projects/bruxism-cap/reports/subject-confound-audit-pass6.md`
    56|  - `projects/bruxism-cap/data/window_features_pass7_s2_mcap.csv`
    57|  - `projects/bruxism-cap/reports/random-window-cv-pass7-s2-mcap.json`
    58|  - `projects/bruxism-cap/reports/loso-cv-pass7-s2-mcap.json`
    59|  - `projects/bruxism-cap/reports/pass7-s2-mcap-overlap.md`
    60|  - `projects/bruxism-cap/data/window_features_pass9_s2_mcap_a3.csv`
    61|  - `projects/bruxism-cap/reports/random-window-cv-pass9-s2-mcap-a3.json`
    62|  - `projects/bruxism-cap/reports/loso-cv-pass9-s2-mcap-a3.json`
    63|  - `projects/bruxism-cap/reports/pass9-s2-mcap-a3.md`
    64|  - `projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv`
    65|  - `projects/bruxism-cap/reports/random-window-cv-pass10-s2-mcap-a3-only.json`
    66|  - `projects/bruxism-cap/reports/loso-cv-pass10-s2-mcap-a3-only.json`
    67|  - `projects/bruxism-cap/reports/pass10-s2-mcap-a3-only.md`
    68|  - `projects/bruxism-cap/reports/rule-survival-audit-pass11.json`
    69|  - `projects/bruxism-cap/reports/pass11-rule-survival-audit.md`
    70|  - `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a1_only_matched14.csv`
    71|  - `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a3_only_matched14.csv`
    72|  - `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a1-only-matched14.json`
    73|  - `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json`
    74|  - `projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a3-only-matched14.json`
    75|  - `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a3-only-matched14.json`
    76|  - `projects/bruxism-cap/reports/pass12-exclusive-a1-vs-a3-matched14.md`
    77|  - `projects/bruxism-cap/src/audit_subject_thresholds.py`
    78|  - `projects/bruxism-cap/reports/subject-threshold-audit-pass15-emg-a3-vs-c4-a1.json`
    79|  - `projects/bruxism-cap/reports/pass15-emg-a3-threshold-audit.md`
    80|  - `projects/bruxism-cap/src/audit_emg_feature_validity.py`
    81|  - `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.json`
    82|  - `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.md`
    83|- The current result is useful but weak: random-window CV remains very high, while LOSO stays poor on held-out bruxism sensitivity.
    84|- A pass5 measurement-hardening rerun added subject-level LOSO aggregation and made the current failure mode harsher: on both the pass3 and pass4 datasets, none of the tested models actually produced a positive held-out bruxism subject verdict at the default threshold.
    85|- A follow-up alignment audit made the data-validity issue more specific:
    86|  - `n10.edf` appears truncated relative to `n10.txt`, leaving no in-range `SLEEP-S2` windows
    87|  - `brux1` has enough early `S2` windows to keep, but many later scored events also exceed the local EDF duration
    88|  - `brux2`, `n3`, `n5`, and `n11` look clean enough for the current bounded `SLEEP-S2` extraction rule
    89|- A new pass6 confound audit further refined the interpretation:
    90|  - on both the pass3 and pass4 feature tables, label-separation metrics were stronger than subject-separation metrics inside leakage-prone random window splits
    91|  - so the current failure is not best explained as trivial subject-ID memorization alone; the harder problem is that the observed class boundary does not survive held-out-subject transfer
    92|- The new pass7 event-overlap rerun tightened the extraction rule again without improving transfer:
    93|  - it kept only in-range `SLEEP-S2` windows that overlapped `MCAP-A1`, `MCAP-A2`, or `MCAP-A3`
    94|  - random-window CV still stayed effectively perfect
    95|  - LOSO window sensitivity fell to `0.000`, and subject-level bruxism sensitivity stayed `0.000`
    96|  - so simple stage restriction plus CAP micro-event overlap is still not enough to make the boundary transferable
    97|- A new pass8 overlap-event audit narrowed the next extraction question again:
    98|  - `brux2` is heavily `MCAP-A3`-dominated while `n5` is heavily `MCAP-A1`-dominated within the kept pass7 windows
    99|  - that mismatch already exists in the full eligible pools, not only in the first-20 cap
   100|  - so the mixed `S2+MCAP` bucket is not one homogeneous physiological subset, and the next bounded rerun should try one single overlap family rather than another broad mixed-event bucket
   101|- The new pass9 single-family rerun narrowed the overlap rule but still did not improve honest transfer:
   102|  - random-window balanced accuracy fell from perfect to about `0.921`, which is directionally healthier than pass7
   103|  - best LOSO balanced accuracy still fell to only `0.550`
   104|  - subject-level bruxism sensitivity still stayed `0.000` for every model
   105|  - so simply requiring `A3` overlap is not enough; the next extraction step should be even more auditable, such as exclusive `A3` windows rather than any window that merely contains `A3`
   106|- The new pass10 exclusive-`A3` rerun made that next step explicit and still failed:
   107|  - random-window balanced accuracy fell slightly further to about `0.908`
   108|  - best LOSO balanced accuracy fell again to only `0.500`
   109|  - subject-level bruxism sensitivity still stayed `0.000` for every model
   110|  - so even exclusive `A3` windows do not isolate a transferable cross-subject boundary in the current tiny subset
   111|- A new pass11 rule-survival audit clarified how much the overlap rules themselves change sampling availability:
   112|  - the bruxism pool keeps `142/442` eligible pass4 `S2` windows (`32.1%`) under exclusive `A3`, while the control pool keeps only `156/1026` (`15.2%`)
   113|  - `brux2` still has `111` eligible exclusive-`A3` windows, while `n5` falls to `38`
   114|  - so pass7/pass9/pass10 should be read not only as semantic event-family changes but also as progressively less balanced sampling surfaces [[bruxism-cap-rule-survival-audit-2026-05-04]]
   115|- A new pass12 matched-family comparison changed the overlap-family interpretation again:
   116|  - when exclusive `A1-only` and exclusive `A3-only` are compared on the same verified 5-subject subset with the same `14` windows per subject, `A1-only` becomes the stronger honest transfer candidate
   117|  - best `A1-only` LOSO balanced accuracy rose to `0.686`, and subject-level bruxism sensitivity rose to `0.500`
   118|  - matched `A3-only` still stayed at `0.000` subject-level bruxism sensitivity across models
   119|  - this is still not a stable baseline win, because `brux1` remains missed and the gain is carried by only one of the two bruxism subjects [[bruxism-cap-exclusive-a1-vs-a3-matched14-2026-05-04]]
   120|- A new pass13 matched channel comparison added the first real EMG-first check on the same scaffold:
   121|  - exclusive `A1-only` on `EMG1-EMG2` did **not** beat the existing matched `C4-P4` baseline on the same 5-subject / 14-window subset
   122|  - best EMG LOSO balanced accuracy fell to only `0.543`, and subject-level bruxism sensitivity fell back to `0.000`
   123|  - unlike the pass12 `C4-P4` run, the EMG rerun missed both `brux1` and `brux2`, so the first EMG-first comparison is a preserved negative result rather than a new honest baseline [[bruxism-cap-emg-vs-c4-a1-only-matched14-2026-05-04]]
   124|- A new pass14 matched EMG-family comparison refined that EMG-first reading:
   125|  - on the same matched `5`-subject / `14`-windows-per-subject scaffold, exclusive `A3-only` improved `EMG1-EMG2` LOSO balanced accuracy from `0.543` to `0.629` relative to exclusive `A1-only`
   126|  - but subject-level bruxism sensitivity still stayed `0.000` for every tested model, so neither EMG family yet beats the honest baseline criterion
   127|  - this is therefore a narrower validity result, not an EMG breakthrough: family choice matters inside `EMG1-EMG2`, but the current handcrafted EMG recipe still misses both held-out bruxism subjects [[bruxism-cap-emg-a1-vs-a3-matched14-2026-05-04]]
   128|- A new pass15 subject-threshold audit tightened the EMG-first failure mode again:
   129|  - the stronger `EMG1-EMG2 A3-only` run does **not** fail mainly because the subject threshold is too high
   130|  - the best bruxism subject score (`brux1` `0.176`) still sits below two controls (`n3` `0.267`, `n5` `0.266`), so any threshold that recovers `brux1` also creates at least two control false positives
   131|  - thresholds that recover both bruxism subjects collapse specificity entirely, so the next bottleneck is score ordering / feature validity rather than threshold choice [[bruxism-cap-emg-a3-threshold-audit-2026-05-04]]
   132|- A new pass16 feature-validity audit tightened the EMG-first failure mode again:
   133|  - the pass14 `EMG1-EMG2 A3-only` score ordering reproduces exactly under a fold-by-fold `logreg` rebuild: `n3` `0.267`, `n5` `0.266`, `brux1` `0.176`, `n11` `0.095`, `brux2` `0.074`
   134|  - among the controls that still outrank `brux1`, the same small feature family keeps recurring as positive contributors: `ratio_alpha_delta`, `min`, and `sample_entropy`
   135|  - `brux1` looks like a different instability surface because its fold is dominated by extreme absolute-power / mean terms, so the next EMG-first move should be one small feature-family ablation rather than more threshold tweaking [[bruxism-cap-emg-feature-validity-audit-2026-05-04]]
   136|- A new pass17 time-domain ablation preserved another useful EMG-first negative result:
   137|  - on the same matched `EMG1-EMG2 A3-only` scaffold, dropping `bp_*`, `rel_bp_*`, and `ratio_*` features does **not** improve the honest subject-level verdict; subject-level sensitivity stays `0.000`
   138|  - the best LOSO window-level result also regresses slightly from `0.629` to `0.614`, and `n3` becomes even more dominant in the subject ranking (`0.328` vs `brux1` `0.148`)
   139|  - so the next bounded patch should be replacement-oriented rather than subtraction-only: add one compact EMG-specific burst / envelope / amplitude-variability family instead of only deleting spectral features [[bruxism-cap-emg-time-only-ablation-2026-05-04]]
   140|- A new pass18 replacement-family rerun preserved the same honest verdict while sharpening the next feature-selection question again:
   141|  - on the same matched `EMG1-EMG2 A3-only` scaffold, adding one compact rectified-envelope / burst family does **not** improve the honest subject-level verdict; subject-level sensitivity stays `0.000`
   142|  - the best LOSO window-level result regresses again from `0.614` to `0.600`, but the score ordering shifts in a useful mixed way: `brux1` rises from `0.148` to `0.158`, `brux2` from `0.055` to `0.092`, and `n3` falls from `0.328` to `0.245`
   143|  - the remaining blocker is that `n5` still outranks `brux1` (`0.267` vs `0.158`), so add-only EMG features are not enough while the older spectral family still dominates the decision surface [[bruxism-cap-emg-envelope-replacement-2026-05-04]]
   144|
   145|## Practical next step
   146|- Keep the current model family fixed.
   147|- Preserve the annotation-aware extraction path and treat EDF/sidecar alignment as part of the measurement pipeline.
   148|- Keep `n10` excluded from local `SLEEP-S2` reruns unless a fuller matching EDF is found, and keep `brux1` only with explicit in-range filtering.
   149|- Use the new subject-level LOSO summaries as the main interpretation surface for honest baseline quality.
   150|- Keep the new event-overlap extraction support in `prepare_windows.py`, but treat pass7 as a negative result rather than a win.
   151|- Preserve the new overlap-event audit as evidence that the mixed `S2+MCAP` bucket is heterogeneous by subject.
   152|- Preserve the new rule-survival audit as evidence that the later `A3`-focused overlap filters also change per-subject and per-label availability.
   153|- Preserve the new pass12 matched-family result as evidence that exclusive `A1-only` currently transfers better than matched exclusive `A3-only`, even though `brux1` still fails.
   154|- Preserve the new pass13 matched channel result as evidence that the first `EMG1-EMG2` rerun on the strongest current `A1-only` scaffold did **not** beat `C4-P4`; it missed both bruxism subjects under LOSO and should be treated as a first-class negative result [[bruxism-cap-emg-vs-c4-a1-only-matched14-2026-05-04]].
   155|- Preserve the new pass14 EMG-family result as evidence that `EMG1-EMG2` prefers exclusive `A3-only` over exclusive `A1-only` on window-level LOSO, but still fails the honest subject-level test under both families [[bruxism-cap-emg-a1-vs-a3-matched14-2026-05-04]].
   156|- Preserve the new pass15 threshold audit as evidence that the stronger `EMG1-EMG2 A3-only` run fails because subject score ordering is wrong, not because the default `0.5` threshold is too strict [[bruxism-cap-emg-a3-threshold-audit-2026-05-04]].
   157|- Preserve the new pass16 feature-validity audit as evidence that the high-score controls repeatedly benefit from `ratio_alpha_delta`, `min`, and `sample_entropy`, while `brux1` is dragged by extreme absolute-power / mean terms [[bruxism-cap-emg-feature-validity-audit-2026-05-04]].
   158|- Preserve the new pass17 time-domain ablation as evidence that simply deleting the spectral / ratio family is not enough: honest subject-level sensitivity stays `0.000`, the best LOSO window-level result regresses slightly, and `n3` becomes even harder to separate [[bruxism-cap-emg-time-only-ablation-2026-05-04]].
   159|- Preserve the new pass18 replacement-family rerun as evidence that add-only EMG-oriented envelope / burst features are also not enough by themselves: `brux1` and `brux2` recover slightly relative to pass17 and `n3` falls, but `n5` still outranks `brux1`, subject-level sensitivity stays `0.000`, and the stronger pass14 LOSO window-level result is still not beaten [[bruxism-cap-emg-envelope-replacement-2026-05-04]].
   160|- Preserve the new pass19 selection-aware rerun as evidence that the pass18 envelope / burst family works better when the older spectral / ratio family is excluded at train time, but still does not cross the honest subject-level bar: `n5` improves relative to pass18 and the best LOSO balanced accuracy recovers to `0.629`, yet `n3` and `n5` still outrank `brux1` and subject-level sensitivity remains `0.000` [[bruxism-cap-emg-envelope-selection-2026-05-04]].
   161|- Preserve the new pass20 mean-ablation rerun as evidence that the next bottleneck is **not** solved by one more naive deletion: once the older spectral / ratio family is already excluded, removing raw `mean` leaves `n3` and `n5` essentially unchanged but makes `brux1` collapse from `0.151` to `0.018`, so the stronger pass19 recipe should remain the EMG-first working point [[bruxism-cap-emg-mean-ablation-2026-05-04]].
   162|- Preserve the new pass21 retained-family audit as evidence that the pass19 envelope / burst working point is doing something real but still not cleanly bruxism-aligned: `sample_entropy` and `burst_fraction` still help the highest-score controls, while `brux1`'s larger raw `rectified_mean`, `envelope_mean`, and `p95_abs` remain net-negative under the learned coefficients, so the next EMG-only move should be normalization-aware rather than another blind deletion [[bruxism-cap-emg-envelope-family-audit-2026-05-04]].
   163|- Preserve the new pass22 normalization-aware rerun as evidence that simple per-window `median_mad` extraction is **not** that fix: on the same matched `EMG1-EMG2 A3-only` scaffold with the same pass19 train-time exclusions, best LOSO balanced accuracy regresses from `0.629` to `0.571`, subject-level sensitivity stays `0.000`, and both bruxism subjects rank even lower than under pass19 [[bruxism-cap-emg-median-mad-normalization-2026-05-04]].
   164|- Preserve the new pass23 shared subject-score comparison as evidence that the current EMG gap is now sharper than “EMG is just worse”: pass19 does improve `brux1` relative to the honest pass12 `C4-P4 A1-only` anchor, but it loses decisively overall because `brux2` collapses (`0.795` -> `0.088`) and `n3` becomes the highest-score control, swinging the best-bruxism-minus-highest-control margin from `+0.362` to `-0.129` [[bruxism-cap-emg-pass19-vs-c4-pass12-subject-scores-2026-05-05]].
   165|- Preserve the new pass24 focused gap audit as evidence that the current EMG failure is now localized more tightly than a generic channel loss: the decisive reversal is `brux2` falling below `n3`, `zero_crossing_rate` is the largest surviving control-favoring feature gap on the fixed pass19 scaffold, and the matched-14 extraction is still count-matched but not time-position-matched [[bruxism-cap-emg-brux2-vs-n3-gap-2026-05-05]].
   166|- Preserve the new pass25 shared-time-position rerun as evidence that the pass24 timing concern was real but incomplete: forcing a shared absolute time interval improves both bruxism subjects (`brux1` `0.151` -> `0.282`, `brux2` `0.088` -> `0.215`) yet still leaves all three controls above both bruxism subjects and does not improve honest subject-level sensitivity beyond `0.000` [[bruxism-cap-emg-a3-time-position-matched-rerun-2026-05-05]].
   167|- Preserve the new pass26 matched strict-scaffold comparison as evidence that the pass25 negative result is **not** a reason to abandon the EMG-first framing: rebuilding the exact same shared-time-position `A3-only` scaffold on `C4-P4` leaves subject-level sensitivity at `0.000`, worsens subject-level balanced accuracy from `0.500` to `0.333`, and turns `n3` into a hard false positive, so the stricter scaffold itself now looks like the bigger problem rather than `EMG1-EMG2` alone [[bruxism-cap-c4-vs-emg-timepos-a3-2026-05-05]].
   168|- Preserve the new pass27 strict-`A1-only` feasibility audit as evidence that the pass25/pass26-style global shared-time-position rule is itself too brittle for the current `EMG1-EMG2 A1-only` subset: the uncapped pool exists (`233` rows total), but the common interval leaves only `2` windows per subject, so the next timing-aware rerun should soften the selector rather than pretending a `10`-row benchmark is informative [[bruxism-cap-emg-a1-time-position-feasibility-2026-05-05]].
   169|- Research update on 2026-05-04: the latest translational literature is pushing harder toward portable jaw-muscle EMG, multi-night monitoring, and wearable sensing, but I did not find a clearly better open benchmark dataset than CAP. All 6 current local CAP EDFs do contain `EMG1-EMG2`, so the next project shape should likely be an EMG-first pivot inside the same reproducible CAP scaffold rather than a full dataset switch. [[bruxism-better-project-and-data-options-2026-05-04]].
   170|- Preserve the new pass28 percentile-band rerun as evidence that softer timing control was the right extraction-validity patch for `EMG1-EMG2 A1-only`: the selector recovers a reproducible `10`-windows-per-subject scaffold, but the honest LOSO subject surface still fully collapses with both bruxism subjects below all controls [[bruxism-cap-emg-a1-percentile-band-rerun-2026-05-05]].
   171|- Preserve the new pass29 matched percentile-band comparison as evidence that channel choice still matters on that repaired scaffold: rebuilding the exact same `A1-only` percentile-band subset on `C4-P4` raises honest subject-level balanced accuracy from `0.500` to `0.750` and recovers `brux2` without false positives, yet still only ties the older best honest baseline because `brux1` remains just below `n3` [[bruxism-cap-c4-a1-percentile-band-vs-emg-2026-05-05]].
   172|- Preserve the new pass30 cross-channel gap audit as evidence that the repaired percentile-band `A1-only` scaffold is genuinely timing-matched across `EMG1-EMG2` and `C4-P4`, so the remaining honest bottleneck is now narrower than a channel-only story: `brux1` still trails `n3` under both channels, while the main matched gap is `brux2` recovering only on `C4-P4` [[bruxism-cap-a1-percentile-band-channel-gap-audit-2026-05-05]].
   173|- Preserve the new pass31 recurrence audit as evidence that the suspected narrow `n3`-favoring trio (`sample_entropy`, `burst_fraction`, `envelope_cv`) is real but not sufficient on the repaired percentile-band scaffold: `burst_fraction` recurs, but the strongest EMG control-favoring gap is still broader and led by `mean`, `max`, `ptp`, and `zero_crossing_rate` [[bruxism-cap-a1-percentile-band-n3-family-recurrence-2026-05-05]].
   174|- Preserve the new pass32 broader morphology ablation as evidence that the obvious wider deletion is not the fix either: on the same repaired `A1-only` scaffold, removing `mean`, `max`, `ptp`, `zero_crossing_rate`, `sample_entropy`, `burst_fraction`, and `envelope_cv` still leaves `EMG1-EMG2` below the honest baseline and also destroys the useful `brux2` recovery on `C4-P4` [[bruxism-cap-emg-a1-broad-morphology-ablation-2026-05-05]].
   175|- Preserve the new pass33 smaller raw-location ablation as evidence that a narrower deletion is not the fix either: on the same repaired `A1-only` scaffold, removing only `mean`, `min`, and `max` leaves `C4-P4` essentially unchanged but makes `EMG1-EMG2` markedly worse by collapsing `brux1` (`0.270` -> `0.030`) while `n3` stays high (`0.530` -> `0.527`) [[bruxism-cap-emg-a1-raw-location-ablation-2026-05-05]].
   176|- Preserve the new pass34 record-relative audit as evidence that representation changes can help one part of the repaired scaffold without solving the whole benchmark: within-record robust feature scaling removes the `n3` false positive and flips `brux2 - n3` from `-0.494` to `+0.041`, but `brux1` still falls from `0.270` to `0.180`, so subject-level sensitivity remains `0.000` [[bruxism-cap-emg-a1-record-relative-audit-2026-05-05]].
   177|- Preserve the new pass35 matched `C4-P4` comparator as evidence that the same record-relative transform is not a channel-agnostic fix: it lifts `brux1` above threshold but collapses the earlier `brux2` recovery (`0.959` -> `0.262`) and turns `n3` into a new false positive, so the pass34 gain now looks more EMG-specific than universal [[bruxism-cap-c4-record-relative-comparator-2026-05-05]].
   178|- Preserve the new pass35 EMG shape-feature expansion as evidence that a compact waveform-shape family can also improve the repaired scaffold without subject-subset drift: the rebuilt pass27/pass28 counts and selected rows match exactly, `n3 - brux1` shrinks from `+0.260` to `+0.009`, and `brux2 - n3` flips to `+0.174`, but both bruxism subjects still stay below threshold so subject-level sensitivity remains `0.000` [[bruxism-cap-emg-a1-shape-feature-expansion-2026-05-05]].
   179|- Preserve the new pass36 composition audit as evidence that the two best current EMG representation clues really do compose on the repaired scaffold: stacking pass35 shape on top of the pass34 record-relative table lifts subject-level balanced accuracy from `0.500` to `0.750`, recovers subject-level sensitivity to `0.500`, and pushes `brux2` clearly above threshold, but `brux1` still regresses and remains the remaining bottleneck [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]].
   180|- Preserve the new patched-EMG versus matched-`C4-P4` synthesis as scaffold evidence rather than as the final EMG anchor decision: `C4-P4` still wins the narrow honest subject-level criterion and both channels remain bottlenecked by the repaired scaffold, but the later honest-anchor verdict shows that the useful forward question is whether the pass34 and pass35 EMG gains compose honestly, not whether `pass35` alone should be promoted as the settled EMG anchor [[bruxism-cap-patched-emg-vs-matched-c4-anchor-comparison-2026-05-05]] [[bruxism-cap-pass35-shape-vs-honest-anchors-verdict-2026-05-05]].
   181|- Research update on 2026-05-05: a periodic translational framing check still supports the current repo posture. The newer literature is more strongly wearable, multi-night, and intervention-aware, but it still does not provide a clearly better open benchmark than CAP, so `EMG1-EMG2` should remain the primary benchmark channel while portable/home/intervention EMG stays a future branch rather than an immediate pivot [[bruxism-cap-translational-framing-check-2026-05-05]].
   182|- Future-branch note on 2026-05-05: privacy-preserving wearable EMG design is now an explicitly captured downstream branch for this project and should be treated as one of the main ways this work stands apart from generic bruxism-detection projects. It belongs in the wiki first as architecture/threat-model/prototype planning, then should move onto the board promptly once the current benchmark reaches a good-enough state [[bruxism-cap-privacy-pets-roadmap-2026-05-05]].
   183|- Second future-branch note on 2026-05-05: LLM/fine-tuning/RL work is also now an explicitly captured downstream branch, but it should be framed as privacy-aware adaptive wearable intelligence rather than generic AI garnish. It belongs in the wiki first as roadmap/design/prototype planning, then should move onto the board through one bounded memo or prototype task at a time once the benchmark stabilizes [[bruxism-cap-llm-rl-roadmap-2026-05-05]].
   184|- After the new pass33 smaller raw-location ablation, the next bounded target should stay leakage-aware and EMG-first but shift more clearly from deletion toward representation: keep the repaired `A1-only` scaffold fixed and prefer a record-relative or within-record morphology audit before another feature-removal pass.
   185|- After the new pass34 record-relative audit, the next bounded target should stay on the same repaired scaffold but move to the backup shape-family test: preserve the mixed normalization result, keep the selector/model family fixed again, and add one compact shape-only family (`skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`) rather than stacking more normalization variants.
   186|- After the new pass35 matched `C4-P4` comparator, the next bounded target should remain EMG-first: preserve the comparator as evidence that record-relative normalization is not a universal cross-channel fix, and test the compact shape-family backup on the repaired EMG scaffold rather than promoting the transform itself to the default matched benchmark.
   187|- After the new pass35 honest-anchor verdict, the next bounded target should preserve both mixed representation results but stop treating pass34-versus-pass35 as the whole question: add the same four compact shape features on top of the pass34 record-relative scaffold, then run a strict pass34 versus `record-relative + shape` LOSO comparison on the same repaired five-subject split before any broader feature, normalization, or channel change.
   188|- Campaign-level synthesis on 2026-05-05 preserved the stronger board read: do not pause or pivot yet. Keep CAP plus `EMG1-EMG2` as the bounded benchmark frame, keep `pass29 C4-P4` as the honest comparison anchor, and continue the autoresearch loop narrowly through one `record-relative + shape` composition audit before promoting privacy/PET, LLM/RL, or broader benchmark-reframing branches [[bruxism-cap-campaign-handoff-2026-05-05]].
   189|- After the new pass36 composition audit, the next bounded target should stay on the same repaired five-subject scaffold and localize why `brux1` still fails while `brux2` now clears threshold, rather than pivoting immediately to another channel or stacking a broader feature family.
   190|- After the first matched EMG rerun, the sharper next target is narrower: keep the same verified subset but compare `EMG1-EMG2` exclusive `A1-only` against exclusive `A3-only` before changing model family.
   191|- After the new feature-validity audit, the next bounded target is narrower still: keep the matched `EMG1-EMG2 A3-only` scaffold fixed and test one small feature-family ablation before changing model family.
   192|- After the time-domain ablation, the next bounded target is narrower again: keep the same matched `EMG1-EMG2 A3-only` scaffold, but move from deletion-only patches to one compact EMG-specific replacement family such as burst / envelope / amplitude-variability features.
   193|- After the pass20 mean-ablation rerun, the next bounded target is narrower again: keep the stronger pass19 selection-aware EMG recipe fixed and audit the retained amplitude / envelope family directly (`rectified_*`, `envelope_*`, `p95_abs`, `sample_entropy`) because naive raw-`mean` removal does not lower the highest-score controls and instead makes `brux1` much worse.
   194|- After the new pass21 retained-family audit, the next bounded EMG-only target is narrower again: keep the stronger pass19 selection-aware recipe fixed, preserve the retained envelope family, and test one normalization-aware extraction change before deleting more features or changing model family.
   195|- After the new pass22 normalization-aware rerun, the next bounded target should shift back toward benchmark clarity: keep pass19 as the EMG-first working point and compare it directly against the honest pass12 `C4-P4 A1-only` anchor in one shared subject-score table before trying another extraction rewrite.
   196|- After the new pass23 shared subject-score comparison, the next bounded target should narrow again: keep pass19 fixed and audit why `brux2` collapses under `EMG1-EMG2` while `n3` becomes the dominant control, instead of launching another broad feature or normalization rewrite.
   197|- After the new pass24 focused gap audit, the next bounded target should narrow again without abandoning the EMG-first frame: keep pass19 fixed, treat the `brux2`-below-`n3` reversal as the main failure surface, and test a simple time-position-matched extraction variant before another broad feature rewrite.
   198|- After the new pass25 shared-time-position rerun, the next bounded target should stay scaffold-matched but become channel-comparative again: rebuild the same shared-interval `10`-windows-per-subject subset on `C4-P4` so the repo can separate a channel effect from a stricter time-position-matched scaffold effect.
   199|- After the new pass26 matched strict-scaffold comparison, the next bounded target stayed EMG-first and checked strict `EMG1-EMG2 A1-only` feasibility directly.
   200|- After the new pass27 feasibility audit, the next bounded target should still stay EMG-first but soften the timing control: extend the current selector beyond one hard shared interval so `EMG1-EMG2 A1-only` can be audited with more than `2` windows per subject before another matched channel comparison.
   201|
   202|## Relationship to other tracks
   203|- [[artifact-card-sft]] is paused, not deleted.
   204|- The older tutor adapter remains a negative-result case study.
   205|- The lab's current learning path now treats a reproducible biosignal baseline as the main active experiment.
   206|

SOURCE: /home/hermes/work/ai-lab/wiki/queries/bruxism-cap-campaign-handoff-2026-05-05.md
     1|---
     2|title: Bruxism CAP campaign handoff (2026-05-05)
     3|created: 2026-05-05
     4|updated: 2026-05-05
     5|type: query
     6|tags: [research, dataset, evaluation, experiment, notes]
     7|sources:
     8|  - ../projects/bruxism-cap/reports/campaign-handoff-2026-05-05.md
     9|  - queries/bruxism-cap-pass35-shape-vs-honest-anchors-verdict-2026-05-05.md
    10|  - comparisons/bruxism-cap-patched-emg-vs-matched-c4-anchor-comparison-2026-05-05.md
    11|  - queries/bruxism-cap-translational-framing-check-2026-05-05.md
    12|  - concepts/bruxism-cap.md
    13|---
    14|
    15|# Question
    16|After the matched-comparator branch, the direct honest-anchor verdict, and the periodic literature framing review, should the current `bruxism-cap` autoresearch loop continue, pause for reframing, or pivot to another branch?
    17|
    18|# Short answer
    19|Continue, but continue narrowly.
    20|
    21|Do not read the latest EMG work as a breakthrough, and do not pause for a benchmark pivot. The durable campaign-level read is that the repo should keep the current CAP, `EMG1-EMG2`, leakage-aware benchmark framing, preserve `pass29 C4-P4` as the honest comparison anchor, and ask exactly one more bounded EMG composition question on the repaired scaffold. [[bruxism-cap]] [[bruxism-cap-pass35-shape-vs-honest-anchors-verdict-2026-05-05]] [[bruxism-cap-translational-framing-check-2026-05-05]]
    22|
    23|# Why the loop should continue
    24|
    25|## 1. The literature branch did not force a pivot
    26|The translational review still supports the current benchmark posture: newer work is more wearable-, multi-night-, and intervention-oriented, but it still does not expose a clearly better open benchmark than CAP.^[queries/bruxism-cap-translational-framing-check-2026-05-05.md]
    27|
    28|So the current repo frame remains valid:
    29|- keep CAP as the bounded public scaffold
    30|- keep `EMG1-EMG2` as the primary benchmark channel
    31|- keep the validity caveats explicit
    32|- keep wearable/intervention ambitions as future branches rather than current benchmark claims
    33|
    34|## 2. The experiment branch produced a sharper hypothesis, not a dead end
    35|The repaired five-subject percentile-band `A1-only` scaffold is now stable enough that one-step representation tests mean something. On that scaffold, the board learned that the two most interesting EMG repairs are complementary rather than decisive:
    36|- `pass34` record-relative fixes the `brux2` versus `n3` reversal and removes the `n3` false positive, but still leaves `brux1` below threshold
    37|- `pass35` shape nearly closes `n3 - brux1` and keeps `brux2` above `n3`, but still leaves both bruxism subjects below threshold
    38|
    39|That is a real narrowing of the problem. The remaining blocker is threshold-crossing subject sensitivity, especially `brux1`, not generic extraction chaos. [[bruxism-cap-patched-emg-vs-matched-c4-anchor-comparison-2026-05-05]] [[bruxism-cap-pass35-shape-vs-honest-anchors-verdict-2026-05-05]]
    40|
    41|# What the campaign learned
    42|
    43|## 1. Honest comparator discipline mattered
    44|`pass29 C4-P4` still remains the only repaired-scaffold anchor with positive subject-level sensitivity and clean specificity. That means EMG still has not won the honest subject-level benchmark.
    45|
    46|But the matched record-relative `C4-P4` regression also matters: it shows the record-relative gain is not a universal scaffold repair. So the repo should not simplify the story to either “EMG is fixed” or “C4 is just better forever.”
    47|
    48|## 2. Negative results became more useful
    49|The latest negative results are sharper than the earlier ones. They show exactly which failure surfaces moved and which did not. That makes one more bounded representation composition test more justified than a broad reframing move.
    50|
    51|## 3. Future branches should wait one step longer
    52|The privacy/PET and LLM/RL roadmap notes now belong in the long-term project map, but not yet as the next board action. Promoting them before the current composition test would blur the benchmark campaign before its cleanest remaining question is answered. [[bruxism-cap-privacy-pets-roadmap-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]]
    53|
    54|# Continue or pause?
    55|Continue.
    56|
    57|But continue on a narrowed anchor definition:
    58|- honest comparison anchor: `pass29 C4-P4`
    59|- EMG clue set: `pass34` record-relative plus `pass35` compact shape
    60|- fixed benchmark surface: repaired five-subject percentile-band `A1-only` LOSO scaffold
    61|
    62|Do not pause for reframing until that composition question has been tested.
    63|
    64|# Best next bounded task
    65|Queue one implementation/run task on the current board:
    66|- start from the `pass34` record-relative audit path
    67|- add the same four compact shape features used in `pass35`
    68|- keep selected rows, subject set, LOSO split, model family, and decision checks fixed
    69|- compare only `pass34` versus `record-relative + shape`
    70|
    71|That is the highest-value next task because it directly tests whether the two best mixed EMG gains compose honestly on the same repaired scaffold. If that combined pass still fails to recover subject-level sensitivity, then the board will have a stronger basis for pausing the benchmark loop or promoting one future branch. [[bruxism-cap]] [[bruxism-cap-pass35-shape-vs-honest-anchors-verdict-2026-05-05]]
    72|