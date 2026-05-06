# Bruxism CAP — final closure report

Date: 2026-05-06
Status: completed public benchmark branch, closed after pass48

## Executive summary

`bruxism-cap` was a deliberately small, leakage-aware public benchmark project built on the PhysioNet CAP Sleep Database. Its purpose was never to make a clinical detector. Its purpose was to answer a smaller question honestly: with a tiny public subset, a single primary channel, classical handcrafted features, and subject-aware evaluation, is there a reproducible bruxism-versus-control benchmark surface worth preserving?

Yes, there is a benchmark surface worth preserving.

No, the current public CAP subset does not support a stronger stable detector claim.

The final closure result is `pass48`, the matched repaired `A1-only` control-expanded replication on the same `7`-subject contract used by `pass47`. That run fell to subject-level balanced accuracy `0.400`, sensitivity `0.000`, and specificity `0.800`; it missed both bruxism subjects and reopened the control surface through `n2` at `0.614`. That is a stronger stop signal than “the improvements got small.” It means the last meaningful bounded cross-family check failed on both sensitivity and specificity.

Final project verdict:
- preserve CAP as a completed public baseline scaffold
- preserve the benchmark history and the measurement lessons
- stop CAP micro-passes
- move future work to the privacy-preserving wearable jaw-EMG branch and its data/measurement roadmap

## Project goal

The project goal was to build the smallest honest public baseline that could:
- use a reproducible CAP subset
- keep the positive class fixed at `brux1` and `brux2`
- use one jaw-muscle-aligned signal channel as the main line
- extract fixed windows from stage-aware and event-aware slices
- compute classical handcrafted features
- train simple models
- compare leakage-prone random-window validation against honest subject-held-out validation

The repo was explicitly benchmark-first, not deployment-first.

## Why CAP was chosen

CAP was not chosen because it was ideal. It was chosen because it was open, reproducible, and already usable end to end inside the repo.

The most important trade-off was this:
- CAP is open enough to benchmark honestly
- CAP is too small on the positive side to support a strong final detector claim

That trade-off stayed true all the way to the end.

## Glossary

### CAP
The PhysioNet CAP Sleep Database. This is the public source dataset used for the project.

### Benchmark
The repo’s reproducible public baseline task and evaluation contract. In this project, “benchmark” does not mean a production system or a clinically validated detector.

### `brux1`, `brux2`
The only public bruxism-positive records available in the CAP branch used here. They define the entire honest positive subject set for this project.

### `n1`, `n2`, `n3`, `n5`, `n11`
Healthy control records from the CAP `n*` pool that were kept only when they satisfied the repo’s bounded dual-channel and annotation-aware contract.

### `EMG1-EMG2`
The primary benchmark channel. This is the main EMG-first line the project explored.

### `C4-P4`
The comparison EEG channel used to test whether the same scaffold behaved differently on a non-primary channel.

### `SLEEP-S2`
Stage-2 sleep windows extracted from the annotation sidecars. Later passes used this stage-aware slice instead of broad unrestricted windows.

### `MCAP-A1`, `MCAP-A2`, `MCAP-A3`
CAP micro-event family labels used as overlap filters for window selection. In this repo, `A1` and `A3` are selection families, not bruxism labels.

### `A1-only`, `A3-only`
Exclusive overlap rules. An `A1-only` run keeps windows overlapping `MCAP-A1` under the exact rule used in that pass; an `A3-only` run does the same for `MCAP-A3`.

### Random-window CV
A leakage-prone validation surface that splits windows without respecting subject identity. This stayed in the repo only as a reference showing how flattering within-subject leakage can be.

### LOSO
Leave-one-subject-out cross-validation. This is the main honest evaluation surface because all windows from the held-out subject are excluded from training.

### Subject-level score / `mean_positive_probability`
The aggregated held-out score per subject, built from the window predictions in the held-out fold. This is the main surface used for honest interpretation.

### Record-relative features
A within-record robust normalization used on a bounded feature subset. The key transform was:
- `(x - median_subject_feature) / max(MAD_subject_feature, 1e-06)`

This helped remove some subject-specific magnitude distortions without changing the benchmark contract.

### Shape features
A compact set of waveform-shape descriptors added in pass35:
- `skewness`
- `kurtosis`
- `hjorth_mobility`
- `hjorth_complexity`

### No-shape exclusions
The train-time exclusions used in the repaired `A3-only` and final control-expanded lines that dropped those four shape descriptors.

### Event trio
The retained three-feature event-conditioned subset validated in pass42:
- `evt_active_fraction`
- `evt_burst_duration_median_s`
- `evt_interburst_gap_median_s`

### Percentile-band selector
The repaired time-aware selector used from the repaired scaffold phase onward. Within each subject, windows were ordered by `start_s`, restricted to a relative time band `q=[0.10, 0.90]`, then evenly downselected to a fixed cap.

### Control-expanded
The bounded `7`-subject stress-test setup:
- positives: `brux1`, `brux2`
- controls: `n1`, `n2`, `n3`, `n5`, `n11`

## Hard dataset ceiling

The final project decision depends on one simple fact: the positive set never became larger.

From the source audit:
- public CAP filenames: `108`
- prefix counts: `brux=2`, `ins=9`, `n=16`, `narco=5`, `nfle=40`, `plm=10`, `rbd=22`, `sdb=4`
- public bruxism-positive CAP files available to this repo: only `brux1` and `brux2`

That means the honest public positive ceiling for subject-level sensitivity is exactly two subjects.

This is why the project always had to stay careful. Control expansion, channel comparison, and within-record representation changes were possible. Positive-label expansion was not.

## Admissible subject set and data-validity constraints

The project did not simply use all `n*` controls. Controls were admitted only when they satisfied the bounded repo contract:
- dual-channel compatibility where needed
- usable `SLEEP-S2` stage rows
- usable event-overlap rows under the chosen family rule
- annotation-aware extraction without obvious range failures

Important validity finding:
- `n10` was excluded from local stage-aware work because the local EDF was truncated relative to the sidecar
- local `n10.edf`: `61,030,035` bytes
- canonical remote `n10.edf`: `474,168,064` bytes

Verified control core before expansion:
- `n3`, `n5`, `n11`

Bounded additional controls admitted later:
- `n1`, `n2`

Controls excluded from the current dual-channel control-expanded branch:
- `n4`, `n6`, `n7`, `n8`, `n9`, `n12`, `n13`, `n14`, `n15`, `n16`

## Compressed project history

The project ran through many passes, but the history is easier to understand in phases.

### Phase 1 — the first honest lesson: leakage matters more than headline accuracy

The early runs showed a large gap between random-window CV and subject-held-out LOSO. That gap became the project’s first durable lesson.

The core early read was:
- random-window CV looked very strong
- honest subject-level transfer did not
- the benchmark was teaching measurement discipline before it was teaching detection success

### Phase 2 — annotation-aware and event-aware hardening

Later passes restricted the project to stage-aware and event-aware slices:
- `SLEEP-S2` stage filtering
- CAP micro-event overlap filtering
- exclusive `A1-only` and `A3-only` comparisons

This phase established two important facts:
1. The extraction rule itself changes the usable row surface materially.
2. The mixed CAP event buckets were heterogeneous across subjects.

That forced the project toward narrower, auditable family-specific scaffolds instead of broad mixed-event pools.

### Phase 3 — family and channel comparisons

The project then asked whether different family rules and channels behaved differently under matched conditions.

Important outcome:
- matched `A1-only` transferred better than matched `A3-only` in early fair comparisons
- the first `EMG1-EMG2` matched `A1-only` line did not beat the `C4-P4` comparison anchor
- repeated EMG-first reruns narrowed the failure from “generic poor performance” to more specific score-ordering and feature-validity problems

This phase mattered because it changed the project from vague experimentation into bounded hypothesis testing.

### Phase 4 — repaired scaffold: timing-aware selection and within-record representation

The repaired scaffold phase was where the project became technically coherent.

Important steps:
- strict global time matching on `A1-only` collapsed the surface to only `2` windows per subject in pass27
- the repaired percentile-band selector in pass28 restored a usable scaffold with `10` windows per subject
- pass34 introduced the record-relative representation
- pass35 added compact shape features
- pass36 showed that record-relative plus shape composed honestly

Pass36 mattered because it proved the project could produce a cleaner subject-level surface without silently changing the benchmark contract.

Pass36 subject-level result:
- balanced accuracy `0.750`
- sensitivity `0.500`
- specificity `1.000`

But even there, only one bruxism subject was cleanly rescued. The benchmark improved without becoming solved.

### Phase 5 — event-trio validation and repaired family anchors

Pass42 validated the retained event trio on the repaired `A1-only` line.

Pass42 key result:
- balanced accuracy `0.750`
- sensitivity `0.500`
- specificity `1.000`
- best-bruxism-minus-highest-control margin `+0.339`

The event trio became the stable retained event block:
- `evt_active_fraction`
- `evt_burst_duration_median_s`
- `evt_interburst_gap_median_s`

Pass44 and pass45 rebuilt the repaired `A3-only` surface fairly and then tightened it with the no-shape variant.

Pass45 key result:
- balanced accuracy `0.750`
- sensitivity `0.500`
- specificity `1.000`
- best-bruxism-minus-highest-control margin `+0.295`

This was a real improvement inside the repaired `A3-only` branch, but it stayed ambiguous rather than positive because it still rescued only one of the two bruxism subjects.

### Phase 6 — final control expansion and closure

The last open question was not “can one more feature tweak improve a score?”

The last open question was:
- does the repaired story survive bounded control-side expansion and matched cross-family pressure?

That produced the final two decisive passes.

## Final benchmark table

| Pass | Subject set | Family / slice | Channel | Selector / representation | Exclusions | Balanced acc. | Sensitivity | Specificity | Best bruxism | Highest control | Margin | Verdict |
|---|---|---|---|---|---|---:|---:|---:|---|---|---:|---|
| pass42 | `brux1, brux2, n3, n5, n11` | repaired `A1-only`, `SLEEP-S2` | `EMG1-EMG2` | repaired percentile-band + record-relative + event trio | base exclusions | `0.750` | `0.500` | `1.000` | `brux2 0.825` | `n11 0.486` | `+0.339` | strongest repaired `A1-only` anchor |
| pass45 | `brux1, brux2, n3, n5, n11` | repaired `A3-only`, `SLEEP-S2` | `EMG1-EMG2` | repaired percentile-band + record-relative + event trio | base + no-shape | `0.750` | `0.500` | `1.000` | `brux1 0.641` | `n11 0.345` | `+0.295` | strongest repaired `A3-only` anchor |
| pass47 | `brux1, brux2, n1, n2, n3, n5, n11` | repaired `A3-only`, control-expanded | `EMG1-EMG2` | repaired percentile-band + record-relative + event trio | base + no-shape | `0.750` | `0.500` | `1.000` | `brux1 0.669` | `n5 0.334` | `+0.335` | ambiguity survived first specificity stress test |
| pass48 | `brux1, brux2, n1, n2, n3, n5, n11` | repaired `A1-only`, control-expanded | `EMG1-EMG2` | repaired percentile-band + record-relative + event trio | base + no-shape | `0.400` | `0.000` | `0.800` | `brux2 0.311` | `n2 0.614` | `-0.302` | closure artifact; stop signal |

## Final implementation: the frozen pass48 closure contract

Pass48 is the final implementation to preserve when explaining why the branch ended.

### New developer orientation
If you are joining this repo fresh, the important mental model is:
1. `prepare_windows.py` builds per-window handcrafted feature tables from EDF + annotation sidecars.
2. `select_time_position_matched_windows.py` applies the bounded time-aware downselection step.
3. record-relative and event-conditioned augmentations are applied in later pass runners.
4. `train_baseline.py` runs random-window or LOSO baselines and emits JSON reports.
5. pass runners such as `run_pass42_...`, `run_pass45_...`, `run_pass47_...`, and `run_pass48_...` freeze exact benchmark contracts and produce durable artifacts.
6. markdown and JSON reports in `reports/` are part of the benchmark itself, not optional afterthoughts.

### Repo structure for new developers
Top-level structure:

```text
projects/bruxism-cap/
├── README.md                         # project overview and final closure status
├── data/
│   ├── README.md                     # raw-data and derived-data notes
│   ├── raw/capslpdb/                 # expected EDF/TXT CAP source layout
│   ├── subject_manifest.example.csv  # example subject manifest
│   └── window_features_pass*.csv     # per-pass derived feature tables
├── notebooks/
│   └── 00_cap_subset_inspection.ipynb
├── reports/
│   ├── pass*.md / pass*.json         # experiment reports and machine-readable outputs
│   ├── loso-cv-*.json                # subject-aware evaluation artifacts
│   ├── random-window-cv-*.json       # leakage-prone reference artifacts
│   └── time-position-match-*.json    # selector audit artifacts
├── src/
│   ├── features.py                   # feature extraction functions
│   ├── prepare_windows.py            # EDF + annotation -> feature rows
│   ├── select_time_position_matched_windows.py
│   ├── train_baseline.py             # logreg / svm / random_forest training
│   ├── compare_subject_score_surfaces.py
│   └── run_pass*.py                  # frozen benchmark runners and audits
└── tests/
    └── test_pass*.py                 # focused regression tests for key repaired passes
```

Current codebase snapshot relevant to this branch:
- `34` Python files under `src/`
- `89` markdown files under the project tree
- `43` CSV files under `data/`
- `108` JSON files under `reports/`

### Core implementation modules
- `src/features.py`
  - signal normalization
  - envelope and rectified EMG summaries
  - Hjorth parameters, skewness, kurtosis, sample entropy
  - event-conditioned burst / episode features
- `src/prepare_windows.py`
  - EDF loading
  - annotation parsing from CAP sidecar `.txt`
  - stage/event overlap filtering such as `SLEEP-S2`, `MCAP-A1`, `MCAP-A3`
  - per-window feature extraction and CSV writing
- `src/select_time_position_matched_windows.py`
  - bounded time-aware subject-matched row selection
- `src/train_baseline.py`
  - classical baselines with LOSO or random CV
  - feature include/exclude regex support
  - subject-level aggregation and uncertainty intervals
- `src/compare_subject_score_surfaces.py`
  - paired per-subject comparison artifacts between runs
- `src/run_pass48_control_expanded_a1_replication.py`
  - the final frozen closure runner

### Libraries used and what they do
- `pandas`
  - table manipulation, CSV loading/writing, joins, grouped summaries
- `numpy`
  - numeric array operations used inside feature extraction
- `mne`
  - EDF reading and channel access for biosignal data
- `scikit-learn`
  - baseline models (`LogisticRegression`, `SVC`, `RandomForestClassifier`)
  - preprocessing (`SimpleImputer`, `StandardScaler`)
  - evaluation splitters (`LeaveOneGroupOut`, `StratifiedKFold`)
- `scipy`
  - exact/wilson-style interval helpers via statistical functions used in evaluation
- Python standard library
  - `argparse`, `json`, `csv`, `subprocess`, `pathlib`, `typing`, `datetime`, `re`

The main engineering style of the repo is intentionally lightweight:
- plain Python scripts, not a large framework
- CSV/JSON/Markdown artifacts as the reproducibility surface
- exact frozen pass runners instead of hidden configuration drift

### Exact contract
- subjects: `brux1`, `brux2`, `n1`, `n2`, `n3`, `n5`, `n11`
- channel: `EMG1-EMG2`
- slice: exclusive `SLEEP-S2 + MCAP-A1-only`
- selector: repaired percentile-band / time-aware selector with `q=[0.10, 0.90]`
- per-subject cap: `10` windows
- representation: repaired record-relative feature surface plus the fixed pass42 event trio
- train-time exclusions:
  - base exclusions: `^bp_`, `^rel_bp_`, `^ratio_`
  - no-shape exclusions: `skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`
- model/evaluation: `logreg` with subject-level `LOSO` and uncertainty outputs

### Exact table construction facts
- full exclusive `A1-only` candidate pool before selection: `466` rows total
  - `brux1=27`
  - `brux2=29`
  - `n1=139`
  - `n2=94`
  - `n3=29`
  - `n5=134`
  - `n11=14`
- final selected table: `70` rows total
- exactly `10` selected windows per subject
- event merge keys:
  - `subject_id`
  - `start_s`
  - `end_s`
  - `window_index`
- event null counts after merge:
  - `evt_active_fraction=0`
  - `evt_burst_duration_median_s=0`
  - `evt_interburst_gap_median_s=0`

### Record-relative feature block carried forward
The repaired record-relative surface applied the bounded transform to:
- `mean`
- `max`
- `ptp`
- `line_length`
- `zero_crossing_rate`
- `rectified_std`
- `envelope_std`
- `envelope_cv`
- `rectified_mean`
- `envelope_mean`
- `p95_abs`

### Code examples

Example: build the raw exclusive `A1-only` pass48 window pool by iterating subjects through `prepare_windows.py`.

```python
for index, (subject_id, label) in enumerate(SUBJECTS):
    cmd = [
        py,
        str(script),
        "--edf", str(raw_dir / f"{subject_id}.edf"),
        "--annotation-txt", str(raw_dir / f"{subject_id}.txt"),
        "--annotation-events", "SLEEP-S2",
        "--require-overlap-events", "MCAP-A1",
        "--exclude-overlap-events", "MCAP-A2,MCAP-A3",
        "--subject-id", subject_id,
        "--label", label,
        "--channel", "EMG1-EMG2",
        "--window-seconds", "30",
        "--out", str(out_csv),
    ]
```

This is the most concrete definition of the final slice:
- stage constrained
- family constrained
- channel constrained
- subject-labeled
- written as one auditable CSV surface

Example: the pass48 selector call.

```python
cmd = [
    str(python_executable()),
    str(script),
    "--features-csv", str(features_csv),
    "--subjects", ",".join(SUBJECT_IDS),
    "--cap", "10",
    "--mode", "percentile-band",
    "--lower-quantile", "0.1",
    "--upper-quantile", "0.9",
    "--out-csv", str(out_csv),
    "--out-json", str(out_json),
]
```

This is where the repaired time-aware design becomes operational. The selector is not cosmetic; it is one of the key reasons later passes were comparable at all.

Example: the pass48 train-time feature exclusions.

```python
def build_exclude_patterns() -> list[str]:
    excludes = list(BASE_EXCLUDE_REGEXES)
    excludes.extend(f"^{feature}$" for feature in SHAPE_FEATURES)
    for feature in EVENT_FEATURES:
        if feature not in PASS42_EVENT_SUBSET:
            excludes.append(f"^{feature}$")
    return excludes
```

This function freezes the final modeling surface:
- base spectral/ratio exclusions stay out
- shape features are dropped
- only the retained pass42 event trio survives

Example: the exact LOSO training call used by pass48.

```python
cmd = [
    str(python_executable()),
    str(Path(__file__).with_name("train_baseline.py")),
    "--features-csv", str(features_csv),
    "--cv", "loso",
    "--out", str(out_json),
]
```

Example: `train_baseline.py` model construction.

```python
"logreg": Pipeline(
    [
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=random_state)),
    ]
)
```

This is deliberately simple. The repo used classical models to keep the benchmark interpretable and avoid confusing dataset scarcity with model-family complexity.

Example: the record-relative transform carried by the repaired scaffold.

```text
(x - median_subject_feature) / max(MAD_subject_feature, 1e-06)
```

Example: one of the core event-threshold ideas implemented in `features.py`.

```python
threshold = max(
    2.0 * float(reference_rectified_median),
    float(reference_rectified_median) + 2.0 * float(reference_rectified_mad),
    threshold_floor,
)
```

This event-conditioned logic was important because it translated the project from coarse window statistics toward burst/episode summaries while staying inside the handcrafted-feature regime.

### Command-line examples for reproducing the final branch

Run the final closure pass:

```bash
/home/hermes/work/ai-lab/.venv/bin/python \
  /home/hermes/work/ai-lab/projects/bruxism-cap/src/run_pass48_control_expanded_a1_replication.py
```

Train a baseline manually on a prepared features table:

```bash
/home/hermes/work/ai-lab/.venv/bin/python \
  /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass48_emg_s2_mcap_a1_only_control_expanded.csv \
  --cv loso \
  --exclude-features-regex '^bp_' \
  --exclude-features-regex '^rel_bp_' \
  --exclude-features-regex '^ratio_' \
  --out projects/bruxism-cap/reports/manual-loso-pass48-check.json
```

List available channels in one EDF:

```bash
/home/hermes/work/ai-lab/.venv/bin/python \
  /home/hermes/work/ai-lab/projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --list-channels
```

### Why this implementation matters
Pass48 was not an ad hoc run. It was a matched, audited, final discriminating test.

It held fixed:
- the repaired selector idea
- the repaired representation idea
- the retained event subset
- the train-time exclusions
- the subject-level LOSO contract

So when pass48 failed, the project learned something structural, not merely something about a loose experimental branch.

## Pass47: why the branch stayed alive long enough to deserve pass48

Pass47 was the first bounded `7`-subject repaired `A3-only` control-expanded rerun.

Pass47 subject-level result:
- balanced accuracy `0.750`
- sensitivity `0.500`
- specificity `1.000`
- best-bruxism-minus-highest-control margin `+0.335`
- best bruxism subject: `brux1 0.669`
- highest control: `n5 0.334`
- new controls:
  - `n1 0.196`
  - `n2 0.120`

This mattered because it did not immediately collapse under the first control-side specificity stress test. That is why pass48 was worth running: there was still one last meaningful matched cross-family question.

## Pass48: the closure result

Pass48 subject-level result:
- balanced accuracy `0.400`
- sensitivity `0.000`
- specificity `0.800`
- exact sensitivity CI: `0/2`, Clopper-Pearson `95%` CI `[0.0, 0.841886116991581]`
- exact specificity CI: `4/5`, Clopper-Pearson `95%` CI `[0.2835820638819105, 0.9949492366205319]`
- subject-level Brier: `0.2877418017644815`

Subject rows:
- `brux1`: `0.108`, predicted `control`
- `brux2`: `0.311`, predicted `control`
- `n1`: `0.239`, predicted `control`
- `n11`: `0.287`, predicted `control`
- `n2`: `0.614`, predicted `bruxism`
- `n3`: `0.427`, predicted `control`
- `n5`: `0.211`, predicted `control`

Key summary:
- best bruxism subject: `brux2 0.311`
- highest control: `n2 0.614`
- best-bruxism-minus-highest-control margin: `-0.302`

This was the clean stop signal.

## Paired pass48 vs pass47 read

The most important comparison is not pass48 in isolation. It is pass48 against the immediately preceding repaired `A3-only` control-expanded anchor.

Paired deltas from pass47 to pass48:
- balanced accuracy: `0.750 -> 0.400`
- sensitivity: `0.500 -> 0.000`
- specificity: `1.000 -> 0.800`
- subject Brier: `0.1403160015336041 -> 0.2877418017644815`
- margin: `+0.335 -> -0.302`
- margin delta: `-0.637`
- `brux1`: `0.669 -> 0.108`
- `brux2`: `0.212 -> 0.311`
- `n1`: `0.196 -> 0.239`
- `n2`: `0.120 -> 0.614`
- `n3`: `0.081 -> 0.427`
- `n5`: `0.334 -> 0.211`
- `n11`: `0.283 -> 0.287`

Subject prediction flips:
- `brux1`: `bruxism -> control`
- `n2`: `control -> bruxism`

This is why the project should be closed. The final failure is not “still ambiguous.” It breaks the sensitivity story and reopens the specificity story at the same time.

## Why the benchmark is closed

### 1. The positive ceiling never moved
Only `brux1` and `brux2` were honest public positives in this branch. No amount of within-dataset re-slicing can change that.

### 2. The project answered the last meaningful bounded question
Pass47 said the repaired `A3-only` line survived the first control stress test. Pass48 then asked the only remaining sharp question:
- does the same repaired story survive on matched repaired `A1-only` under the same `7`-subject contract?

Answer: no.

### 3. The final failure is stronger than “no further gains”
Pass48 did not merely fail to improve. It:
- missed both bruxism subjects
- created a control false positive at `n2`
- flipped the best-bruxism margin from positive to negative

### 4. The durable scientific read is now stable
The repo can now say, honestly:
- CAP was useful as a public, reproducible, leakage-aware pilot benchmark
- the project learned a great deal about extraction validity, leakage, row-surface drift, and subject-level evaluation
- repaired `A3-only` could preserve an ambiguous `1/2` subject-level signal under first control expansion
- that story does not survive matched repaired `A1-only` control-expanded replication
- therefore the current public CAP branch does not support a stronger stable detector claim

## What the project did accomplish

The branch should not be called a failure in the trivial sense. It accomplished all of these:
- built a reproducible public benchmark pipeline inside the repo
- made the leakage gap visible and central
- hardened the project around subject-level LOSO rather than flattering window-level splits
- preserved negative results instead of overwriting them with vague optimism
- turned extraction, event-family, and representation changes into auditable benchmark artifacts
- established a reusable methodology scaffold for future private or wearable jaw-EMG work

That is meaningful output, even though the benchmark itself is now complete rather than open-ended.

## Recommended forward path

Do not continue CAP micro-passes.

Preserve CAP as:
- a completed public benchmark scaffold
- a measurement-history archive
- a methodological template for future bruxism work

Shift active design energy to:
- the privacy-preserving wearable jaw-EMG branch
- future data acquisition or partnership work for better positive coverage
- benchmark designs where subject-level sensitivity is not capped at two public positives

## Key artifacts

Main closure artifacts:
- `projects/bruxism-cap/src/run_pass48_control_expanded_a1_replication.py`
- `projects/bruxism-cap/reports/pass48-control-expanded-a1-replication.md`
- `projects/bruxism-cap/reports/pass48-control-expanded-a1-replication.json`
- `projects/bruxism-cap/reports/loso-cv-pass48-emg-a1-control-expanded.json`
- `projects/bruxism-cap/reports/time-position-match-pass48-emg-a1-pct10-90-control-expanded.json`
- `projects/bruxism-cap/reports/pass48-vs-pass47-control-expanded-cross-family-audit.md`
- `projects/bruxism-cap/reports/pass48-vs-pass47-control-expanded-cross-family-audit.json`

Supporting repaired anchors:
- `projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.md`
- `projects/bruxism-cap/reports/pass45-honest-benchmark-verdict-2026-05-05.md`
- `projects/bruxism-cap/reports/pass47-control-expanded-rerun.md`

Wiki closure page:
- `wiki/queries/bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06.md`

## Bottom line

`bruxism-cap` should now be treated as a completed public benchmark, not an active CAP tuning loop.

The final honest sentence is:
- CAP gave the repo a reproducible, leakage-aware, subject-level benchmark history.
- It did not give the repo a stable stronger detector claim.
- `pass48` is the reason the branch closes.