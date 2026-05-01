# artifact-card-failure-modes-forced-top2-v2

Forced-top-2 branch for the artifact-card failure-mode project.

Goal
- keep the task focused on `primary_failure_modes`
- remove the all-`out` escape hatch from `joint-rank-v1`
- force a direct ranked top-2 decision with explicit evidence binding for each slot
- test whether no-abstention direct choice plus evidence grounding beats the current `pairwise-v1` downstream baseline

Why this branch exists
- `artifact-card-failure-modes-top2-v1` forced a final pair directly, but it did not bind each chosen slot to explicit evidence and still collapsed badly
- `artifact-card-failure-modes-pairwise-v1` remains the strongest downstream baseline with top-2 set match `0.25`, but ordered recovery stayed `0.0`
- `artifact-card-failure-modes-joint-rank-v1` failed cleanly because the model could still satisfy most of the object with `out` values
- the next disciplined test is to predict only the final ranked pair and force each chosen slot to bind to a closed evidence key

What changed from earlier branches
- source rows come from `artifact-card-failure-modes-v1` plus the train-only calibration cases introduced for rank-select-v2
- each source example becomes one row with exactly four required fields instead of an 8-label state map or 8 independent candidate rows
- output is one strict JSON object with exactly these keys:
  - `primary_label`
  - `primary_evidence_key`
  - `secondary_label`
  - `secondary_evidence_key`
- labels must be distinct and evidence keys must directly support the chosen labels
- there is no `out`, `none`, or abstention state

Current shape
- train examples: 34
- eval examples: 8
- source examples before train-only supplements: 26 train / 8 eval
- train-only supplemental source examples: 8
- mean train input length: 4366.2 chars

Success criterion
- top-2 set match should beat the current best downstream baseline from `artifact-card-failure-modes-pairwise-v1` (`0.25`)
- ordered top-2 match should finally rise above `0.0`
- evidence-key accuracy matters as a grounding check, but label-pair recovery is the main success criterion
- if this branch still fails, the next redesign should likely become a staged shortlist / tournament selector rather than another flat one-shot target
