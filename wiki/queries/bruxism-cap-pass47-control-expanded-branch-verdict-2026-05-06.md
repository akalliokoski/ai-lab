---
title: Bruxism CAP pass47 control-expanded branch verdict
created: 2026-05-06
updated: 2026-05-06
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass47-control-expanded-branch-verdict-2026-05-06.md
  - ../projects/bruxism-cap/reports/pass47-control-expanded-rerun.md
  - ../projects/bruxism-cap/reports/pass47-vs-pass45-paired-subject-surface-audit.md
  - ../projects/bruxism-cap/reports/pass47-vs-pass46-paired-subject-surface-audit.md
  - queries/bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06.md
---

# Bruxism CAP pass47 control-expanded branch verdict

Historical note: this page records the pre-`pass48` branch verdict. The chosen repaired `A1-only` replication was later executed as `pass48`, and that final matched run closed the CAP benchmark branch. Read this page as the reasoning that justified the last experiment, not as current marching orders. [[bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06]]

## Question asked at the time
After the first bounded `7`-subject control-expanded rerun on the frozen repaired `A3-only` no-shape contract, should the branch continue, shift to a repaired `A1-only` replication, or stop as too fragile? [[bruxism-cap]] [[bruxism-cap-pass47-control-expanded-rerun-2026-05-06]]

## Historical answer
At that point, the correct next move was the repaired `A1-only` replication: the expanded control set did not collapse specificity, but the benchmark still stayed ambiguous because `brux2` remained below the highest control.

## Why that historical decision was reasonable
Headline subject metrics stayed fixed across the repaired `A3-only` anchors:
- pass45: `0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity
- pass46: `0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity
- pass47: `0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity

Paired subject-surface improvements versus pass45:
- `brux1`: `0.641 -> 0.669`
- `brux2`: `0.178 -> 0.212`
- `n3`: `0.134 -> 0.081`
- `n5`: `0.337 -> 0.334`
- `n11`: `0.345 -> 0.283`
- best-bruxism-minus-highest-control margin: `+0.295 -> +0.335`

New controls stayed below threshold:
- `n1`: `0.196`
- `n2`: `0.120`
- all five controls remained predicted `control`

So pass47 preserved enough specificity to justify exactly one final matched repaired `A1-only` follow-up.

## What later happened
That follow-up was `pass48`, and it failed decisively:
- balanced accuracy `0.400`
- sensitivity `0.000`
- specificity `0.800`
- both bruxism subjects missed
- `n2` reopened as a false positive at `0.614`

This is why pass47 should now be read as the last useful ambiguity before closure, not as an open invitation to continue the branch indefinitely.

## Bottom line
Pass47 was a valid pre-closure branch verdict. It correctly justified one final repaired `A1-only` replication. Once that replication was run and failed in `pass48`, the CAP benchmark loop became complete. [[bruxism-cap-pass47-control-expanded-rerun-2026-05-06]] [[bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06]]
