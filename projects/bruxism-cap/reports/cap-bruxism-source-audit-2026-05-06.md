# CAP source audit — bruxism-side expansion beyond `brux1` and `brux2`

Date: 2026-05-06
Status: source audit completed; this memo checks whether the public CAP Sleep Database contains any scientifically defensible way to enlarge the bruxism-positive side of `bruxism-cap` beyond the explicit `brux1` and `brux2` records without proxy relabeling.

## Question
Can the public CAP Sleep Database support any honest bruxism-positive expansion beyond `brux1` and `brux2`, or are those two records the full public positive set for this repo?

## Short answer
Effectively no. In the public CAP release, `brux1.edf` and `brux2.edf` are the only explicitly bruxism-labeled records discoverable in `RECORDS`, and the PhysioNet dataset description says the 92 pathological recordings include only `2` affected by bruxism. The repo can still expand channels, controls, and within-record slicing, but not the count of honest bruxism-positive subjects without introducing relabeling or label laundering.

## Exact evidence for the positive-label ceiling

### 1. PhysioNet dataset-level evidence
- The public CAP page states: the dataset has `16` healthy subjects and `92` pathological recordings, including `40` NFLE, `22` RBD, `10` PLM, `9` insomnia, `5` narcolepsy, `4` SDB, and `2` bruxism.
- That diagnosis breakdown already implies a hard public positive ceiling of `2` bruxism recordings.

### 2. Public `RECORDS` surface evidence
A fresh fetch of `https://physionet.org/files/capslpdb/1.0.0/RECORDS` returns `108` filenames with these prefixes:
- `brux`: `2`
- `ins`: `9`
- `n`: `16`
- `narco`: `5`
- `nfle`: `40`
- `plm`: `10`
- `rbd`: `22`
- `sdb`: `4`

The only `brux*` entries are:
- `brux1.edf`
- `brux2.edf`

There are no `brux3+` records and no other filename family that is publicly labeled as bruxism.

### 3. Repo/wiki cross-checks
- `wiki/raw/articles/cap-sleep-database-physionet-2012.md` already notes that PhysioNet `RECORDS` includes `brux1.edf` and `brux2.edf` and frames CAP as a tiny bruxism subset rather than a purpose-built benchmark.
- `wiki/raw/articles/bruxism-single-channel-eeg-2024.md` says the paper could use only `2` bruxism patients and `4` healthy controls with compatible channels for its chosen single-channel analysis.
- `projects/bruxism-cap/data/README.md` already warns that the public bruxism subset is tiny.

Verdict: `brux1` and `brux2` are the only explicit public CAP bruxism positives available to this repo.

## Channel and annotation compatibility evidence
These facts matter, but they do not create new positive labels:

### Channel compatibility on the locally active subset
Local inspection of the six currently downloaded EDFs shows that all six expose both:
- `C4-P4`
- `EMG1-EMG2`

Records checked locally:
- `brux1`, `brux2`, `n3`, `n5`, `n10`, `n11`

So channel availability is not the main blocker on the current tiny subset. It supports alternate feature views of the same subjects, not more bruxism-positive subjects.

### Annotation compatibility on the locally active subset
`projects/bruxism-cap/reports/annotation-alignment-audit-pass4-s2.md` shows:
- `brux1`: only partially usable for local `SLEEP-S2` extraction because many later sidecar rows exceed local EDF duration
- `brux2`: stage-aligned and usable
- `n10`: unusable for local `SLEEP-S2` because the EDF is only about `63` minutes while the sidecar continues much later
- `n3`, `n5`, `n11`: usable under the current bounded stage-aware path

So annotation compatibility narrows usable windows and controls, but it still does not produce any new bruxism-positive subject beyond `brux1` and `brux2`.

## Candidate CAP-internal expansion ideas

| idea | verdict | why |
|---|---|---|
| Treat other pathology groups (`ins*`, `narco*`, `nfle*`, `plm*`, `rbd*`, `sdb*`) as additional bruxism positives | not usable | They have different public diagnoses. Reassigning them to `bruxism` would be direct relabeling with no source support. |
| Add more healthy controls from the `n*` pool | only as negative-control or auxiliary analysis | This can enlarge the negative side if channels and annotations work, but it does not expand the bruxism-positive class. |
| Use alternate channels (`C4-P4`, `EMG1-EMG2`, maybe others present in the same records) | usable only as alternate views of the same two positives | Channel changes can improve measurement or benchmarking, but they do not increase positive subject count. |
| Restrict to alternate sleep stages such as `REM` instead of `S2` | only as auxiliary analysis | Stage restriction changes which windows are sampled. It does not create new bruxism labels, and it inherits compatibility issues. |
| Restrict to CAP families such as `A1-only`, `A3-only`, or other overlap slices | only as auxiliary analysis | Repo pass7/pass9/pass10/pass11 already show these rules change window availability and event semantics unevenly across subjects. They are sampling/physiology filters, not positive labels. |
| Use CAP micro-events or burst-rich windows as proxy bruxism labels | not usable | `MCAP-A1/A2/A3` are CAP phenomena, not bruxism annotations. Using them as positive labels would be label laundering. |
| Use EMG burst, episode, or RMMA-like handcrafted features to infer extra positives | not usable as label expansion; usable only as within-record features | Features may help discrimination, but they are model inputs, not ground truth labels. |
| Split `brux1` and `brux2` into more pseudo-subjects by window clusters, nights, or stage slices | not usable for subject-level expansion | This would inflate sample count without adding independent labeled subjects. At best it is a within-subject auxiliary analysis. |
| Expand controls plus keep positives fixed at `2` | usable for control-side stress tests only | This is the one bounded CAP-internal expansion that is honest, but it expands specificity pressure, not the bruxism side. |

## Is any CAP-internal positive expansion scientifically defensible?
No defensible positive expansion is visible in the public CAP materials inspected here.

The only honest CAP-internal expansions are:
1. more negative controls, if channel and annotation compatibility are verified
2. alternate channels on the same two bruxism subjects
3. alternate stage/event slices on the same two bruxism subjects
4. auxiliary within-record analyses that stay explicitly non-label-generating

None of those increases the number of public bruxism-positive subjects.

## Hard limit: what exactly blocks expansion?
The primary hard limit is labels.

More precisely:
1. Label limit
   - Public CAP exposes only `2` bruxism-labeled records.
   - This is the decisive blocker.

2. Evaluation-honesty limit
   - With only `2` positive subjects, subject-level sensitivity has only `2` trials under LOSO.
   - Splitting windows or stage slices cannot honestly convert that into more positive subjects.

3. Annotation-compatibility limit
   - `brux1` is only partially usable under local stage-aware extraction.
   - `n10` is unusable for local `SLEEP-S2`.
   - These issues constrain analysis surfaces further rather than enlarging them.

4. Event-semantics limit
   - CAP `A1/A2/A3` overlap rules and sleep-stage filters alter window pools and physiological context.
   - They are useful controlled slices, but not substitute disease labels.

5. Channel-compatibility limit
   - Important for comparators and controls, but secondary here.
   - The current local subset already has both `EMG1-EMG2` and `C4-P4`, so channel availability is not the reason the positive class stays tiny.

## Smallest honest next step if CAP must remain tiny
Formalize the ceiling instead of hand-waving around it.

Recommended bounded follow-up:
- add an explicit repo note that the public CAP bruxism-positive set is exactly `brux1` and `brux2`
- state that any further CAP work is control-side expansion, channel comparison, or within-subject auxiliary analysis only
- preserve this as a hard benchmark constraint in the README/wiki so future passes do not drift into proxy-positive language

## Smallest follow-up if a bounded CAP expansion is still justified
Expand only the negative/control side under a fixed contract.

Recommended bounded follow-up:
- audit additional `n*` controls for `EMG1-EMG2`, `C4-P4`, and chosen annotation compatibility
- keep the positive class fixed at `brux1` and `brux2`
- report the result explicitly as a control-side specificity stress test, not as a larger bruxism dataset

That is the only CAP-internal expansion path here that looks both bounded and honest.

## Exact files likely to touch next
If preserving the hard ceiling:
- `projects/bruxism-cap/README.md`
- `projects/bruxism-cap/data/README.md`
- `wiki/concepts/bruxism-cap.md`
- `wiki/queries/bruxism-cap-source-audit-cap-expansion-2026-05-06.md`

If running the bounded control-side expansion:
- `projects/bruxism-cap/data/subject_manifest.example.csv`
- `projects/bruxism-cap/src/prepare_windows.py` only if a new audited extraction option is truly needed
- a new report under `projects/bruxism-cap/reports/` for channel/annotation verification of added controls
- `wiki/concepts/bruxism-cap.md`

## Bottom line
The public CAP dataset can still support careful benchmarking work, but not a larger honest bruxism-positive cohort. `brux1` and `brux2` are the public bruxism ceiling. Anything beyond that is either a control-side expansion, a channel/view change, or a proxy-label mistake.