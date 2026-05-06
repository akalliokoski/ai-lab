# Autoresearch-style workflow for artifact-card SFT

Historical note: this document started before a local `autoresearch` skill existed for the ai-lab profile.

Current status:
- a local profile skill named `autoresearch` is now installed
- use that skill first for new repo-grounded research loops
- keep this file as artifact-card-specific background and example scaffolding rather than the primary source of truth for autoresearch behavior

So the practical way to run this workflow now is to load the local `autoresearch` skill and, when useful, pair it with the existing skills and delegation stack.

Recommended skill set
- `unsloth`
- `hermes-stateless-worker-orchestration`
- `hermes-agent`

Recommended use
- repo-grounded training review
- prompt-contract review
- config-surface review
- next-experiment proposal grounded in saved run artifacts

## One-shot CLI command

Run this from `/home/hermes/work/ai-lab`:

```bash
hermes -s unsloth,hermes-stateless-worker-orchestration,hermes-agent chat -q '
Act as an autoresearch optimizer for this repo. Inspect the current artifact-card training pipeline, latest run artifacts, and dataset task config. Focus on improving training settings, generation contract, prompt shape, evaluation, and next experiments. Ground every recommendation in the local files and run summaries. Return:
1. current bottleneck
2. top 5 train/config/prompt changes ranked by expected value
3. one safest next experiment
4. one riskier but higher-upside experiment
5. exact files to edit
'
```

## Best current target files

- `modal/train_unsloth_artifact_card.py`
- `data/artifact-card-failure-modes-forced-top2-v2p1/task_config.json`
- latest run summaries under `tmp/modal-artifacts/`

## What the first autoresearch-style pass found

### Training/config pipeline findings
1. Eval is too generic for this strict task.
   - Current scoring checks JSON parseability and field equality.
   - It does not fully enforce:
     - exact key set
     - distinct primary vs secondary labels
     - label legality
     - evidence-key compatibility with each label
2. `generation_prefix = "{"` is applied at inference, but the train target still contains the full JSON object including the opening brace.
   - That creates a train/infer mismatch around the first generated token.
3. Important knobs are hardcoded instead of being surfaced through config.
   - batch size
   - grad accumulation
   - warmup
   - LoRA rank/alpha/dropout
   - generation-time contract controls
4. The dataset is tiny, but the run uses a fixed short schedule with no eval-driven model selection.
5. The scorer does not strictly enforce the prompt claim of "exactly these keys".

### Run-evidence findings
1. `forced-top2-v2` is still the best semantic baseline.
2. `forced-top2-v3` fixed raw JSON validity but collapsed semantically toward fallback labels.
3. `forced-top2-v2p1` kept JSON validity at 1.0 but regressed more on semantic selection.
4. The main failure is not formatting anymore; it is label/evidence fallback collapse.

## Best next experiment

Use `forced-top2-v2` as the semantic anchor and make the smallest possible raw-JSON fix.

Specifically:
1. keep the stronger v2 task shape
2. keep only minimal anti-fence pressure
3. add targeted hard negatives where `missing-required-detail` looks plausible but is wrong
4. add contrast rows for the weak semantic boundaries
5. add collapse-detection metrics so a run fails early if it overpredicts one fallback pair

## Concrete edit shortlist

### Highest-value code edits
- `modal/train_unsloth_artifact_card.py`
  - add strict schema validation
  - add label/evidence compatibility validation
  - expose more train/decode knobs through task config
  - reconcile `generation_prefix` between training and inference

### Highest-value data edits
- `data/artifact-card-failure-modes-forced-top2-v2p1/task_config.json`
  - extend with stricter contract metadata
- next dataset branch
  - add hard negatives against fallback `missing-required-detail`
  - add boundary-specific contrast examples

## Minimal follow-up command after code/data edits

```bash
python3 scripts/check_env.py
source .venv/bin/activate
modal run modal/train_unsloth_artifact_card.py --dataset-name <next-dataset-name> --max-steps 20
```

## Notes

This file documents an autoresearch-style workflow, not a true installed Hermes skill. If this pattern proves useful, turn it into a real local skill later so it can be loaded with `/skill autoresearch` or `hermes -s autoresearch`.
