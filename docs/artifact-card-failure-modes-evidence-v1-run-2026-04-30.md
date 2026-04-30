# artifact-card-failure-modes-evidence-v1 run review

Date: 2026-04-30
Run id: `20260430T161302Z`
Dataset: `artifact-card-failure-modes-evidence-v1`
Model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
Artifacts: `/artifacts/artifact-card-failure-modes-evidence-v1/20260430T161302Z`
Local summary: `tmp/modal-artifacts/artifact-card-failure-modes-evidence-v1-20260430T161302Z/run_summary.json`

## What was tested
This run executed the new evidence-conditioned per-label branch. Each eval row asked for:
- `candidate_label`
- `supported`
- `evidence_key`

The intended advantage over the pairwise branch was shorter prompts plus explicit evidence binding.

## Basic training result
- train rows: `208`
- eval rows: `64`
- max steps: `20`
- train loss: `2.563367021083832`
- train runtime: `38.7223` seconds

## Auto-eval from the training run
Base model:
- valid JSON: `0.796875`
- exact row match: `0.484375`
- `candidate_label` accuracy: `0.796875`
- `supported` accuracy: `0.484375`
- `evidence_key` accuracy: `0.625`

Tuned model:
- valid JSON: `1.0`
- exact row match: `0.5`
- `candidate_label` accuracy: `0.984375`
- `supported` accuracy: `0.59375`
- `evidence_key` accuracy: `0.671875`

Immediate interpretation:
- structure and label copying are strong
- support judgment improved over base
- evidence-key grounding is still weak, especially on positive rows

## Branch-specific evaluation
From `scripts/evaluate_failure_mode_evidence_run.py`:

Tuned support metrics:
- positive-only evidence-key accuracy: `0.0625`
- `missing-required-detail`: precision `1.0`, recall `0.5`, f1 `0.6667`
- `fluency-without-correctness`: precision `0.5`, recall `1.0`, f1 `0.6667`
- `no-material-change`: precision `0.3333`, recall `0.3333`, f1 `0.3333`
- `generic-explanation`: precision `0.0`, recall `0.0`, f1 `0.0`
- `hallucinated-detail`: precision `0.0`, recall `0.0`, f1 `0.0`
- `overlap-contaminated-eval`: precision `0.0`, recall `0.0`, f1 `0.0`
- `phrase-copy-or-template-collapse`: precision `0.0`, recall `0.0`, f1 `0.0`
- `wrong-causal-point`: precision `0.0`, recall `0.0`, f1 `0.0`

Reconstructed held-out example metrics:
- exact positive-label set match: `0.0`
- exact positive-count match: `0.125`
- top-2 set match: `0.0`
- overpredict rate: `0.375`
- underpredict rate: `0.5`
- predicted positive-count histogram: `0 -> 4`, `2 -> 1`, `6 -> 1`, `7 -> 2`

## What failed
The run did not beat the pairwise branch on the real downstream objective.

The key failure was not JSON validity or label copying. It was support calibration and evidence-key grounding:
- the model often predicted many labels as supported on the same source example
- positive evidence keys were usually wrong even when `supported=yes` was correct
- several hardest labels still had zero recall and zero precision
- reconstructed outputs became too wide rather than too collapsed

This means the new branch traded one failure mode for another:
- pairwise-v1 failure: dominant-label collapse, especially toward `missing-required-detail`
- evidence-v1 failure: over-acceptance of many labels plus shallow evidence-key use

## Comparison against pairwise-v1
Pairwise-v1 downstream baseline:
- reconstructed exact top-2 set match: `0.25`
- reconstructed exact ordered top-2 match: `0.0`

Evidence-v1 downstream result:
- reconstructed exact positive-label set match: `0.0`
- reconstructed top-2 set match: `0.0`

So the shorter prompt and explicit evidence-key target improved row-level behavior but did not improve the real task.

## Best current interpretation
The branch suggests that evidence conditioning alone is not enough when every example still expands to the full 8-label space.

The likely remaining issue is that the model is still being asked to solve too broad a contrast space per source example. Even with shorter prompts, it can satisfy local row supervision without learning the boundary between the few labels that actually matter for reconstruction.

## Recommended next step
Do not continue broad 8-label evidence expansion as-is.

Instead:
1. keep `artifact-card-v2` as the full-card baseline
2. keep `artifact-card-failure-modes-pairwise-v1` as the strongest downstream decomposition result so far
3. build a smaller contrastive branch limited to the hardest confusion groups:
   - `missing-required-detail` vs `generic-explanation`
   - `missing-required-detail` vs `no-material-change`
   - `missing-required-detail` vs `hallucinated-detail`
   - `missing-required-detail` vs `overlap-contaminated-eval`
4. require exactly one local decision per contrast group before reconstructing the final label set
5. keep evidence keys, but only within those narrow contrast groups rather than across all 8 labels at once

## Why this matters
This is a useful negative result. It narrows the diagnosis:
- prompt shortening helped format control
- per-label evidence conditioning helped some local fields
- but the remaining bottleneck is still label-boundary learning under broad contrast pressure, not trainer wiring or JSON generation
