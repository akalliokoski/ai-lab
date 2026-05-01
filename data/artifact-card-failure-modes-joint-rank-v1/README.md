# artifact-card-failure-modes-joint-rank-v1

Joint-selector branch for the artifact-card failure-mode project.

Goal
- keep the task focused on `primary_failure_modes`
- score all 8 labels together in one output instead of one label per row
- force global normalization: exactly one `primary`, exactly one `secondary`, all remaining labels `out`
- test whether joint scoring fixes the underselection and dominant-label problems that survived the independent rank-select family

Why this branch exists
- `artifact-card-failure-modes-pairwise-v1` is still the strongest downstream branch, but ordered recovery stayed `0.0`
- `artifact-card-failure-modes-rank-select-v1` improved row metrics while reconstruction stayed `0.0`
- `artifact-card-failure-modes-rank-select-v2` fixed schema leakage, but reconstruction still stayed `0.0` and underselection got worse
- the next disciplined branch is to score all labels jointly in one constrained decision object instead of asking the model to score each label independently

What changed from earlier branches
- source rows come from `artifact-card-failure-modes-v1` plus the train-only calibration cases introduced for rank-select-v2
- each source example now becomes one joint ranking row instead of 8 independent candidate rows
- output is one strict JSON object with the 8 label names as fixed keys and values in `primary | secondary | out`
- the prompt includes compact label cards and explicit global constraints so the model must allocate the two positive slots jointly

Current shape
- train examples: 34
- eval examples: 8
- source examples before train-only supplements: 26 train / 8 eval
- train-only supplemental source examples: 8
- mean train input length: 2655.2 chars

Output contract
- keys are fixed to the 8 allowed labels
- values must be exactly one of:
  - `primary`
  - `secondary`
  - `out`
- exactly one key must be `primary`
- exactly one key must be `secondary`
- all remaining keys must be `out`

Success criterion
- exact joint map match should stay interpretable, but it is not the main success condition
- reconstructed top-2 set match should beat the current best downstream baseline from `artifact-card-failure-modes-pairwise-v1` (`0.25`)
- reconstructed ordered top-2 match should beat the current `0.0` pairwise and rank-select results
- if this branch still fails, the next redesign should likely move to an explicitly learned two-pass selector or a smaller learned tournament among pre-shortlisted labels rather than more prompt-only reshaping
