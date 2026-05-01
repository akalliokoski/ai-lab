# artifact-card-failure-modes-forced-top2-v2p1

Status
- scaffolded and locally verified on 2026-05-01

Goal
- preserve the stronger `forced-top2-v2` branch shape that still has the best downstream reconstruction so far
- avoid the heavier `forced-top2-v3` contract rewrite that removed fences but hurt the real task
- test a narrower patch: light anti-fence pressure plus targeted evidence-key compatibility cases

Why this branch exists
- `artifact-card-failure-modes-forced-top2-v2` is still the best actual run in this family
- `forced-top2-v3` showed that heavy contract hardening can remove Markdown fences while still regressing downstream
- the next disciplined move is to start from the stronger `v2` prompt shape and add only the smallest changes that target the two observed bottlenecks:
  - fenced/prose-wrapped outputs on stronger-model reruns
  - repeated fallback or evidence-key mismatch on `fluency-without-correctness`, `wrong-causal-point`, `hallucinated-detail`, and `generic-explanation` cases

What changed from `forced-top2-v2`
- keeps the same no-abstention four-field target object:
  - `primary_label`
  - `primary_evidence_key`
  - `secondary_label`
  - `secondary_evidence_key`
- keeps the original `v2` response budget of `max_new_tokens = 64`
- adds only light anti-fence pressure instead of the `v3` contract rewrite:
  - system prompt now says `Do not add prose or Markdown fences`
  - instruction now says `Do not use Markdown fences or add prose`
  - task config sets `generation_prefix = "{"`
- adds one short compatibility reminder inside the decision rule:
  - `generic-explanation -> broader-than-reference`
  - `missing-required-detail -> missing-or-noncanonical-field`
  - `fluency-without-correctness -> fluency-gain-without-correctness`
- swaps the old shared supplemental set for a smaller train-only set focused on the real remaining confusions instead of the full `v3` rewrite

Targeted train-only supplements
- `fluency-without-correctness + no-material-change` with all required fields present
- `fluency-without-correctness + missing-required-detail` with explicit missing-field evidence
- `generic-explanation + wrong-causal-point` with all required fields present
- `wrong-causal-point + no-material-change` without missing-field evidence
- `hallucinated-detail + missing-required-detail`
- `phrase-copy-or-template-collapse + no-material-change`

Current shape
- source examples before supplements: `26` train / `8` eval
- train-only supplemental source examples: `6`
- final rows: `32` train / `8` eval
- mean train input length: about `4630.8` chars

Files added or updated for this scaffold
- dataset builder: `scripts/build_failure_mode_forced_top2_v2p1_dataset.py`
- dataset folder: `data/artifact-card-failure-modes-forced-top2-v2p1/`
- smoke artifact: `tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v2p1-smoke-run_summary.json`
- scaffold note: `docs/artifact-card-failure-modes-forced-top2-v2p1-scaffold.md`

Local verification completed
- `python3 -m py_compile scripts/build_failure_mode_forced_top2_v2p1_dataset.py scripts/evaluate_failure_mode_forced_top2_run.py modal/train_unsloth_artifact_card.py` passed
- `python3 scripts/build_failure_mode_forced_top2_v2p1_dataset.py` generated the dataset successfully
- `python3 scripts/preview_dataset.py artifact-card-failure-modes-forced-top2-v2p1` showed the narrower anti-fence wording and the same four-field target contract
- `python3 scripts/evaluate_failure_mode_forced_top2_run.py tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v2p1-smoke-run_summary.json data/artifact-card-failure-modes-forced-top2-v2p1/eval_metadata.json` returned perfect smoke metrics
- `python3 scripts/check_env.py` passed
- `modal run modal/train_unsloth_artifact_card.py --help` still exposes the expected CLI

Recommended first run command
```bash
set -a && source .env && set +a && source .venv/bin/activate && \
modal run modal/train_unsloth_artifact_card.py \
  --dataset-name artifact-card-failure-modes-forced-top2-v2p1 \
  --max-steps 20
```

How to judge the first run
- first compare against the best actual branch result, not against `v3` alone:
  - `forced-top2-v2` 1B baseline: `valid_json_rate = 0.875`, `top2_set_match_rate = 0.375`, `top2_ordered_match_rate = 0.375`
- secondary comparison: avoid the `v3` regression pattern:
  - `forced-top2-v3` 1B: `valid_json_rate = 0.625`, `top2_set_match_rate = 0.125`, `top2_ordered_match_rate = 0.125`
- practical success bar:
  - keep or improve `forced-top2-v2`-level downstream reconstruction
  - preserve or improve strict validity
  - reduce the repeated fallback / bad-secondary-evidence-key pattern on `generic-explanation` and `fluency-without-correctness` cases
- if the run preserves the `v2` downstream performance while improving format obedience, this narrower patch is worth keeping
- if it still collapses toward `missing-required-detail + generic-explanation`, then the next patch should target the label/evidence compatibility rows more directly rather than adding more contract language
