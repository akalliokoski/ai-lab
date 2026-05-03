# Karpathy alignment and training-pipeline patch (2026-05-01)

## Why this note exists
This repo now has a local `autoresearch` skill, but the original inspiration is closer to Andrej Karpathy's `LLM Wiki` pattern than to a pure autonomous training loop. The important idea is not “let the agent run forever”; it is “keep a persistent compiled artifact between raw evidence and future questions.”

For `ai-lab`, that means:
- Modal run artifacts and dataset files are the immutable evidence layer
- repo docs plus `wiki/` are the maintained knowledge layer
- Hermes skills and cron prompts are the operating schema for how the agent should inspect, patch, evaluate, and record results

## Core lessons extracted from Karpathy's note
1. Persistent compiled artifact beats rediscovery.
   - Do not leave conclusions only in chat.
   - File them into repo docs or wiki pages.

2. Raw sources should stay immutable.
   - For this project, treat saved `run_summary.json`, dataset branches, and generated metadata as the source layer.
   - Avoid rewriting history inside those artifacts; record interpretation separately.

3. Valuable answers should be filed back.
   - If a debugging pass or comparison was expensive to derive, save it as a durable note.
   - This makes later optimization passes compound instead of repeating the same analysis.

4. Navigation and chronology matter.
   - Keep `wiki/index.md` and `wiki/log.md` current.
   - A research loop without indexing and a timeline becomes expensive to resume.

5. Lint the knowledge surface, not just the code.
   - Look for stale baselines, undocumented regressions, orphan docs, or a mismatch between what the artifacts show and what the current notes claim.

## Concrete improvements applied in this pass
### 1. Training/inference contract alignment for `generation_prefix`
File: `modal/train_unsloth_artifact_card.py`

Problem:
- the forced-top-2 datasets use `generation_prefix = "{"` via task config
- inference prefilled the opening brace
- but training still supervised assistant targets that already began with `{`
- this created a train/infer mismatch right at the first output token

Change:
- when a dataset sets `generation_prefix`, the training records now strip that prefix from the assistant target before chat-template rendering
- inference still pre-fills the prefix and post-normalizes outputs to start with the prefix

Effect:
- the model is now trained to continue after the prefilled prefix instead of redundantly relearning the prefix token in the assistant target

### 2. Built-in task-aware evaluation for forced-top-2 runs
File: `modal/train_unsloth_artifact_card.py`

Problem:
- generic `auto_eval` counted parseable JSON and field matches, but it could not enforce branch-specific legality such as exact key order, distinct labels, and label/evidence compatibility
- this previously hid real regressions

Change:
- local payload loading now includes `eval_metadata.json` and `train_metadata.json` when present
- the training entrypoint now computes `task_aware_eval` automatically for forced-top-2 datasets
- the report includes branch-aware metrics such as:
  - `top2_set_match_rate`
  - `top2_ordered_match_rate`
  - `invalid_row_rate`
  - `invalid_reason_counts`
  - evidence-key slot accuracy

Effect:
- future run summaries surface the real task contract directly, without needing a separate manual evaluator step to notice label/evidence legality failures

### 3. Autoresearch skill alignment with the original Karpathy pattern
File: `~/.hermes/profiles/ai-lab/skills/research/autoresearch/SKILL.md`

Change:
- the skill now states explicitly that autoresearch passes should preserve a persistent compiled artifact
- it distinguishes raw evidence from maintained knowledge
- it requires filing valuable findings back into docs/wiki
- it calls out wiki navigation and periodic linting as part of the research loop

## Recommended operating rule going forward
For this repo, every meaningful optimization pass should leave behind all three layers:
1. evidence: dataset files, metadata, run summaries
2. compiled knowledge: repo docs and wiki notes
3. operating schema: skill instructions, prompt templates, and evaluator logic

If one of those layers is missing, the next pass will be weaker than it needs to be.

## Verification run after the patch
- Run: `20260501T111907Z` on `artifact-card-failure-modes-forced-top2-v2p1` with `max_steps = 20`
- The new `task_aware_eval` block appeared directly in the Modal result payload, so the evaluator wiring worked end-to-end.
- Tuned branch-aware metrics were still weak: `valid_json_rate = 0.75`, `top2_set_match_rate = 0.125`, `top2_ordered_match_rate = 0.125`, `invalid_row_rate = 0.25`.
- This means the patch improved measurement fidelity immediately, but it did not by itself solve the semantic selector collapse.
- The main remaining concrete error is secondary evidence mismatch on `generic-explanation`, plus persistent fallback toward `missing-required-detail`.
