---
title: Bruxism CAP Control-Side Expansion Audit (2026-05-06)
created: 2026-05-06
updated: 2026-05-06
type: query
tags: [research, dataset, evaluation, workflow, notes]
sources:
  - queries/bruxism-cap-next-data-strategy-2026-05-06.md
  - queries/bruxism-cap-source-audit-cap-expansion-2026-05-06.md
---

# Bruxism CAP Control-Side Expansion Audit

## Question
If the public CAP positive set stays fixed at `brux1` and `brux2`, which bounded healthy `n*` controls can be added honestly under the repo's current dual-channel, annotation-aware contract?

## Answer
Only `n1` and `n2` should be admitted as the next control additions.

Keep `n3`, `n5`, and `n11` as the already verified local control core.

Treat `n10` as `refresh_needed`, not as currently admissible, because the canonical PhysioNet record looks full-length and dual-channel compatible while the current local `n10.edf` is truncated (`61,030,035` local bytes versus `474,168,064` canonical bytes, about `63.05` local minutes versus `490.0` canonical minutes). [[bruxism-cap]]

Exclude `n4`, `n6`, `n7`, `n8`, `n9`, `n12`, `n13`, `n14`, `n15`, and `n16` from this branch because they do not satisfy the current dual-channel control contract: they are missing `EMG1-EMG2`, `C4-P4`, or both. `n16` also has `2` out-of-range `SLEEP-S2` rows, but that is secondary to the channel mismatch. [[bruxism-cap-source-audit-cap-expansion-2026-05-06]]

## Contract used
A control is admissible only if it:
1. leaves the positive class fixed at `brux1` and `brux2`
2. exposes both `EMG1-EMG2` and `C4-P4`
3. has usable in-range `SLEEP-S2` rows relative to the EDF actually available to the repo
4. keeps usable `MCAP-A1` and `MCAP-A3` overlap rows for the current event-conditioned branch
5. is reported as a control-side specificity stress test rather than a larger bruxism dataset

## Per-subject verdicts
- Admit next: `n1`, `n2`
- Keep already verified: `n3`, `n5`, `n11`
- Conditional / refresh-needed: `n10`
- Exclude from this branch: `n4`, `n6`, `n7`, `n8`, `n9`, `n12`, `n13`, `n14`, `n15`, `n16`

## Why this matters
The earlier data-strategy note said the best next branch was one bounded CAP-adjacent control-side expansion. This audit narrows that abstract branch into an exact admissible set.

The result is smaller than the whole `n*` pool:
- `n1` and `n2` are the only clean new dual-channel additions
- `n10` stays out until the local file is refreshed and re-audited
- the rest of the healthy controls are outside the current branch because they are not dual-channel compatible, not because CAP itself lacks healthy subjects

## Exact repo consequence
The repo should now preserve one explicit bounded control-side contract:
- fixed positives: `brux1`, `brux2`
- current verified controls: `n3`, `n5`, `n11`
- next admissible additions after download: `n1`, `n2`
- refresh-needed candidate: `n10`

That keeps the benchmark honest: the project is still tiny, still positive-capped, and still not a larger public bruxism dataset. It is only a slightly stronger specificity stress test inside CAP. [[bruxism-cap-next-data-strategy-2026-05-06]] [[bruxism-cap]]

## Repo artifact
Detailed repo memo: `projects/bruxism-cap/reports/cap-control-side-expansion-audit-2026-05-06.md`

## Bottom line
The bounded CAP control-side expansion is real but narrow. Admit `n1` and `n2`, keep `n3` / `n5` / `n11`, require a canonical refresh before reconsidering `n10`, and exclude the rest of the `n*` pool from the current dual-channel branch.