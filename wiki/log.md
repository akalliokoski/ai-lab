# Wiki Log

> Chronological record of wiki actions.

## [2026-04-28] create | ai-lab wiki initialized
- Domain: home AI lab learning and experiments
- Files created:
  - SCHEMA.md
  - index.md
  - log.md
  - entities/unsloth.md
  - concepts/ai-lab-learning-path.md
  - raw/articles/unsloth-docs-2026-04-28.md

## [2026-04-29] update | first unsloth experiment scaffold
- Files created:
  - concepts/hermes-ai-lab-tutor-adapter.md
- Files updated:
  - index.md
  - log.md

## [2026-04-29] update | first modal unsloth training run saved durable artifacts
- Files updated:
  - concepts/hermes-ai-lab-tutor-adapter.md
  - log.md
- Notes:
  - Fixed the Modal training entrypoint to match current TRL APIs.
  - Pinned the Modal image to Python 3.10, Torch 2.10.0, and xFormers 0.0.35 so Unsloth used xFormers correctly.
  - Successful run saved adapter artifacts into Modal volume `ai-lab-unsloth-artifacts` under `/artifacts/hermes-tutor-v1/20260429T093147Z/`.

## [2026-04-29] update | second dataset pass and artifact inspection helpers
- Files updated:
  - concepts/hermes-ai-lab-tutor-adapter.md
  - log.md
- Files created:
  - scripts/list_modal_runs.py
  - scripts/show_modal_run_summary.py
- Notes:
  - Expanded the tutor dataset to 40 train rows after a second quality pass based on real base-vs-tuned outputs.
  - Added local helper scripts to inspect Modal run summaries stored in the artifact volume.
  - Latest successful run saved artifacts under `/artifacts/hermes-tutor-v1/20260429T094629Z/`.
