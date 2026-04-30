---
source_url: local-session-research
ingested: 2026-04-30
sha256: 285258c8d2095ace465b6b9b5b8f4922aaab3bf119d8659dc6b13f719c70b929
---

# First fine-tuning use case research

Research summary prepared from:
- local project run history in `docs/first-unsloth-experiment.md`
- local failure review in `docs/fine-tuning-no-improvement-root-cause-review-2026-04-29.md`
- external references:
  - LIMA: https://arxiv.org/abs/2305.11206
  - LoRA: https://arxiv.org/abs/2106.09685
  - QLoRA: https://arxiv.org/abs/2305.14314
  - Hugging Face PEFT docs: https://huggingface.co/docs/peft/index
  - OpenAI fine-tuning best practices: https://platform.openai.com/docs/guides/fine-tuning-best-practices

Main findings:
- tiny SFT datasets are a better fit for behavior steering, format control, extraction, and narrow transformation than for broad knowledge injection
- the current repo-tutor project is a poor first fit because it mixes knowledge, style, workflow heuristics, and causal explanation in one tiny dataset
- the best replacement use case for this repo is converting run artifacts and operator notes into a strict experiment card schema
- a strong second option is a failure-mode classifier for eval outputs

Recommendation:
- use `artifact-card-sft` as the next first-project candidate
- treat the tutor project as a useful negative result rather than the default path forward
