# artifact-card-v3

Third pass on the artifact-card starter task.

Goal
- keep the v2 schema and eval split unchanged
- patch the exact v2 bottleneck instead of broadening the task
- improve second-label selection and exact next_action selection

What changed from v2
- added a short selection-hints block to every train and eval prompt
- made the action mapping more explicit:
  - structural gain but mixed semantics -> add automatic field scoring before the next run
  - longer or sparse inputs weakened schema discipline -> shorten the inputs and keep the schema fixed before rerunning
  - repeated unchanged failures -> stop rerunning unchanged data and patch the weak concepts
  - overlap contamination / copied phrasing -> remove overlap-heavy rows and rerun
- added 6 contrast rows targeted to the exact v2 failure patterns
- kept the candidate vocabularies and outer JSON schema fixed for direct comparability

Why this is the next disciplined move
- v2 already solved JSON validity and mostly solved key_evidence
- the remaining misses were concentrated in `primary_failure_modes` and `next_action`
- the v2 run often picked a nearby but wrong action or failure label even when the evidence phrases were correct
- this means the cleanest next patch is better decision boundaries, not a broader dataset rewrite

Current shape
- train examples: 26
- eval examples: 8
- source format: JSONL with `instruction`, `input`, `output`
- target output: JSON string only

Hypothesis
- if the patch works, exact-card match should finally move above `0.0`
- the biggest likely gains should appear in `primary_failure_modes` and `next_action`
- if exact-card match still stays at `0.0`, the next move should probably split the task into smaller supervised subtasks instead of continuing to patch the full card task
