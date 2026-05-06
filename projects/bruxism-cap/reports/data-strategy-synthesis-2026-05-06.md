# Data strategy synthesis — what should come after the CAP ceiling audit and dataset scout?

Date: 2026-05-06
Status: completed synthesis memo.

## Question
Given the CAP positive-set ceiling, the external dataset scout, and the explicit dataset-decision rubric, what should the broader bruxism-detection project do next?

## Inputs synthesized
1. `projects/bruxism-cap/reports/cap-bruxism-source-audit-2026-05-06.md`
2. `projects/bruxism-cap/reports/methodology-review-dataset-decision-rubric-2026-05-06.md`
3. `wiki/queries/bruxism-scout-results-2026-05-06.md`

## Short answer
Public CAP cannot honestly grow its bruxism-positive class beyond `brux1` and `brux2` for this project.

That does not force an immediate dataset pivot. The strongest honest recommendation now is to open one bounded CAP-adjacent expansion branch: keep `brux1` and `brux2` fixed as the full public positive set, then audit and add only extra healthy controls plus any verified channel/stage compatibility that strengthens specificity pressure without pretending the positive cohort is larger than it is.

No external dataset is currently both scientifically better enough and open/reproducible enough to justify promotion over CAP as the active public benchmark branch.

## 1. Can CAP honestly grow beyond `brux1` and `brux2`?
Precise answer: no on the positive side.

The source audit is decisive:
- the PhysioNet CAP description says the public pathological recordings include only `2` bruxism cases
- the public `RECORDS` surface exposes only `brux1.edf` and `brux2.edf`
- no inspected CAP pathology family outside `brux*` can be relabeled as bruxism without label laundering

So public CAP can still grow only in bounded non-positive ways:
1. more healthy controls
2. alternate channel comparisons on the same positives
3. alternate sleep-stage or CAP-family slices on the same positives
4. auxiliary within-record analyses that stay explicitly non-label-generating

The honest ceiling is therefore: CAP can widen around the benchmark, but not enlarge the public bruxism-positive subject pool.

## 2. Rubric-ranked comparison of the top external alternatives against CAP
Weighted rubric from the methodology memo:
- positive-label validity `25`
- jaw-muscle relevance `20`
- subject-level evaluation honesty `20`
- ecological validity `12`
- openness/reproducibility `10`
- portability to future wearable work `8`
- implementation tractability `5`

Scores below use the explicit `0-5` rubric and were totaled with a small script so the arithmetic stays exact.

### CAP baseline
- CAP public bruxism baseline: `58.2 / 100`
- Why it stays viable:
  - strongest current openness and reproducibility surface
  - real runnable access now
  - still decent positive-label validity for a public benchmark
- Why it is capped:
  - only `2` positive subjects
  - weak ecological validity
  - subject-level evaluation honesty is constrained by tiny positive `N`

### Ranked external alternatives
1. Portable jaw-EMG logger / masseter-EMG branch (Le 2025 style): `72.6 / 100`
   - Strongest scientific non-CAP direction right now
   - Beats CAP on jaw-muscle relevance, ecological validity, and future portability
   - Does NOT clear promotion because openness/access/tractability are currently too weak; it is not a reproducible runnable benchmark branch now

2. Wireless/mmWave branch (Shen 2025 style): `61.4 / 100`
   - Strong ecological-validity story
   - Still weaker than the EMG branch on signal relevance to jaw-muscle physiology
   - Closed/request-only access keeps it below pivot quality

3. Earable branch (Bondareva 2021 style): `52.4 / 100`
   - Interesting ecological direction
   - Still too small/closed and too indirect to beat CAP honestly now

4. Generic open sleep repositories with relabeling ambition: `45.0 / 100`
   - Open and potentially larger
   - But they lack bruxism-positive labels and would require major relabeling effort
   - This fails the project’s anti-fake-progress rule even if raw `N` looks attractive

## 3. Exact primary recommendation now
Choose exactly one primary branch now: open one bounded CAP-adjacent expansion branch.

That branch should be defined narrowly:
- keep the positive class fixed at `brux1` and `brux2`
- do not claim CAP is becoming a larger bruxism dataset
- audit additional `n*` healthy controls for `EMG1-EMG2`, `C4-P4`, and stage/annotation compatibility
- report the result as a control-side specificity stress test inside a bounded public benchmark

## 4. Why this wins over the other two branch options
### Why not “stay on CAP as a bounded pilot”?
Because the source audit still leaves one honest, useful, and bounded CAP move available: expand the control side under a fixed positive ceiling. That is more informative than simply declaring the pilot frozen right now.

### Why not “open one new dataset-acquisition branch” now?
Because no candidate is both:
- better enough scientifically
- open enough to reproduce now
- and operationally real enough to turn into an audited benchmark branch immediately

The best scientific non-CAP option is the portable jaw-EMG direction, but it is still an evidence-pack/deferred-branch candidate rather than an active benchmark branch.

## 5. Deferred backup branch
Deferred backup branch: one portable jaw-EMG dataset-acquisition/evidence-pack branch.

Practical meaning:
- treat portable masseter-EMG cohorts as the most promising next non-CAP family
- do not open the full benchmark branch yet
- first require a concrete access-and-validity pack proving that at least one candidate cohort is truly obtainable and benchmarkable

This is a better backup than wireless or earables because it stays closest to the project’s direct physiology target.

## 6. Activation conditions for the deferred branch
Only activate the deferred portable-EMG branch when all of these are true:
1. exact access path and license are real now, not aspirational or request-only in vague terms
2. the data include direct jaw-muscle or masseter-adjacent sensing with documented label provenance
3. subject identities and sample structure support honest subject-held-out evaluation
4. the candidate scores at least `80 / 100` on the explicit rubric
5. the candidate beats CAP by at least `12` weighted points
6. it is no worse than CAP on subject-level evaluation honesty
7. the bounded CAP-adjacent control expansion has either been completed or shown too weak to justify more CAP effort

Today, those conditions are not met.

## 7. One exact next operational task to create
Create exactly one downstream task:

`data: audit additional CAP healthy controls for a bounded control-side expansion`

Acceptance target:
- inspect a bounded set of additional `n*` CAP controls
- verify `EMG1-EMG2` and `C4-P4` availability
- verify stage/annotation compatibility under the current extraction contract
- update the subject manifest proposal
- produce one report that says exactly which controls are admissible, excluded, or uncertain
- preserve the result in repo plus wiki without changing the positive-label contract

Recommended assignee: the main project-execution profile, not this synthesis worker.

## 8. Exact repo/wiki files to update next
If the bounded CAP-adjacent branch is opened next, the first exact files to update should be:

Repo:
1. `projects/bruxism-cap/README.md`
2. `projects/bruxism-cap/data/README.md`
3. `projects/bruxism-cap/data/subject_manifest.example.csv`
4. `projects/bruxism-cap/reports/cap-control-side-expansion-audit-2026-05-06.md`
5. `projects/bruxism-cap/src/prepare_windows.py` only if the audit proves one small extraction option is truly needed

Wiki:
6. `wiki/concepts/bruxism-cap.md`
7. `wiki/queries/bruxism-cap-next-data-strategy-2026-05-06.md`
8. `wiki/queries/bruxism-cap-control-side-expansion-audit-2026-05-06.md`
9. `wiki/index.md`
10. `wiki/log.md`

## Bottom line
The scientifically honest read is now stable:
- CAP cannot honestly add more public bruxism-positive subjects beyond `brux1` and `brux2`
- no external dataset is both better and sufficiently open enough to replace CAP right now
- therefore the next active branch should be one bounded CAP-adjacent control-side expansion, while portable jaw-EMG stays the deferred backup branch behind explicit activation gates
