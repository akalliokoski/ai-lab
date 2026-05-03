---
title: Artifact Card Forced Top-2 v2 vs v2p1 vs v3
created: 2026-05-01
updated: 2026-05-01
type: comparison
tags: [training, dataset, evaluation, unsloth, modal, experiment, workflow]
sources: [../tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v3-20260501T085312Z/run_summary.json]
---

# Artifact Card Forced Top-2 v2 vs v2p1 vs v3

Side-by-side comparison of the three recent no-abstention forced-top-2 branches, using branch-aware forced-top-2 metrics as the main scoreboard. The durable conclusion is that `artifact-card-failure-modes-forced-top2-v2` remains the strongest semantic anchor, while both `v2p1` and `v3` are useful negative results about output-contract pressure that did not fix selector collapse. [[artifact-card-sft]] [[artifact-driven-experiment-debugging]] [[karpathy-llm-wiki-and-autoresearch-improvements-2026-05-01]]

## What stayed fixed
- training entrypoint: `modal/train_unsloth_artifact_card.py`
- run length: `20` steps
- held-out split size: `8` eval rows
- target object:
  - `primary_label`
  - `primary_evidence_key`
  - `secondary_label`
  - `secondary_evidence_key`
- primary judgment rule: trust branch-aware forced-top-2 reconstruction over train loss or generic JSON validity

## What changed between branches
- `forced-top2-v2`
  - original no-abstention branch with evidence-bound slots
  - no `generation_prefix`
  - strongest known downstream reconstruction so far
- `forced-top2-v2p1`
  - kept the lighter `v2` prompt shape
  - added `generation_prefix = "{"`
  - added light anti-fence wording plus 6 narrow train-only compatibility cases
- `forced-top2-v3`
  - heavier raw-JSON-only contract rewrite
  - shorter `max_new_tokens = 48`
  - also used `generation_prefix = "{"`

## Branch-aware run summary

| branch | run_id | train_rows | train_loss | valid_json_rate | exact_row_match_rate | top2_set_match_rate | top2_ordered_match_rate | invalid_row_rate |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `forced-top2-v2` | `20260501T145949Z` | `34` | `1.8952903985977172` | `0.875` | `0.375` | `0.375` | `0.375` | `0.125` |
| `forced-top2-v2p1` | `20260501T111907Z` | `32` | `1.886918342113495` | `0.75` | `0.125` | `0.125` | `0.125` | `0.25` |
| `forced-top2-v3` | `20260501T085312Z` | `34` | `1.913314300775528` | `0.625` | `0.125` | `0.125` | `0.125` | `0.375` |

## Key readout
- `forced-top2-v2` is still the best actual branch result on the downstream task, not just on format.
- `forced-top2-v2p1` did **not** preserve the stronger `v2` semantics. Its narrower anti-fence patch still fell back to `missing-required-detail + generic-explanation` too often and only reached `top2_set_match_rate = 0.125`.
- `forced-top2-v3` removed the Qwen-style Markdown-fence problem from the earlier stronger-model rerun, but its heavier contract rewrite still regressed the real task to the same `0.125` reconstruction level.
- Lower or similar train loss was not predictive here: `v2p1` had slightly lower loss than `v2`, yet much worse selector behavior.

## Error concentration by branch

### `forced-top2-v2`
- Main fallback pair still overused: `missing-required-detail + generic-explanation`.
- The remaining misses are narrow and auditable:
  - `fluency-without-correctness`
  - `hallucinated-detail`
  - `wrong-causal-point`
- One separate structural miss remained on the overlap example: evidence-key names were copied into label slots, producing `bad-primary-label`.

### `forced-top2-v2p1`
- The narrow anti-fence continuation did not solve the selector.
- Branch-aware invalid rows were concentrated in `bad-secondary-evidence-key` failures, specifically illegal `generic-explanation` pairings with `missing-or-noncanonical-field`.
- The tuned histogram still skewed strongly toward `missing-required-detail` and `generic-explanation`, with only one `wrong-causal-point` prediction surviving outside the fallback pair.

### `forced-top2-v3`
- The heavier contract rewrite did not fail by Markdown wrapping anymore.
- Instead, it shifted failure into contract-compatible but semantically wrong outputs:
  - 3 rows failed as `bad-secondary-evidence-key`
  - the model often predicted `missing-required-detail + generic-explanation`
  - one otherwise valid row replaced the gold `generic-explanation` secondary label with `phrase-copy-or-template-collapse`
- This is the important negative result: stronger JSON-only pressure can clean up one surface failure while worsening the real slot-selection objective.

## Why this matters
- The current bottleneck is no longer “make the model emit parseable JSON.”
- The current bottleneck is comparative semantic slot allocation under a strict label/evidence contract.
- `generation_prefix = "{"` plus extra anti-fence language did not buy enough to justify another rerun on the same family without a sharper semantic patch.

## Practical conclusion
- Keep `artifact-card-failure-modes-forced-top2-v2` as the semantic anchor and best current baseline for this branch family.
- Keep `forced-top2-v2p1` as a first-class negative result: a minimal contract patch plus 6 targeted cases was not enough.
- Keep `forced-top2-v3` as another first-class negative result: heavier raw-JSON hardening removed fence wrapping but still hurt the real downstream objective.
- The next bounded move should be data-side and failure-specific, not another prompt-contract rewrite.

## Best next patch shape
- Start from the `forced-top2-v2` branch, not `v2p1` or `v3`.
- Add a small train-only patch focused on the exact surviving confusion boundaries:
  - `fluency-without-correctness` vs `missing-required-detail`
  - `hallucinated-detail` vs `missing-required-detail`
  - `wrong-causal-point` vs `no-material-change`
  - `overlap-contaminated-eval` / `phrase-copy-or-template-collapse` label-slot confusion
- Keep the patch small enough that the next rerun still isolates selector behavior instead of mixing another contract rewrite with another semantic redesign.

## Learning rule preserved
This comparison is worth keeping because it prevents rediscovery of the same false lesson. The project does **not** currently need more generic JSON hardening. It needs a narrower semantic patch that teaches the model when the tempting fallback pair is wrong. [[artifact-card-sft]] [[fine-tuning-lessons-from-first-project]] [[artifact-driven-experiment-debugging]]
