# Start Here

Date: 2026-04-28

## What this profile is for

`ai-lab` is your practical AI learning workspace. The goal is not just reading docs, but turning them into:
- runnable scripts
- small notebooks
- documented experiments
- wiki notes that compound over time

## Current machine strategy

### VPS
Use the VPS as the always-on control plane:
- run Hermes
- manage the repo
- chat over Telegram
- maintain the wiki
- launch remote jobs
- prepare data and prompts

### MacBook Pro M3 32GB
Use the Mac for interactive local experimentation:
- local Python and notebooks
- small model inference and preprocessing
- reading docs and editing artifacts
- selective local Unsloth-compatible experiments if the dependency stack behaves well on Apple Silicon

### Modal
Use Modal when you need actual GPU training or reproducible serverless GPU execution:
- fine-tuning jobs
- batch inference
- packaging experiments as Python-first cloud jobs

## Immediate setup checklist

1. Confirm the profile works:
   - `ai-lab chat`
2. On the VPS, review the profile:
   - `hermes profile show ai-lab`
3. On the Mac, clone this repo and run the machine bootstrap from `hermes-stack`:
   - `bash scripts/bootstrap-machine.sh --env-id macbook --service-mode remote`
4. Create a GitHub remote after `gh auth login`.
5. Copy `.env.example` to `.env` and add secrets as needed:
   - `HF_TOKEN`
   - `MODAL_TOKEN_ID`
   - `MODAL_TOKEN_SECRET`
6. Run `./scripts/bootstrap-python.sh`
7. Run `python3 scripts/check_env.py`
8. Start the Unsloth learning path in `docs/unsloth-self-learning-path.md`

## Hugging Face setup

Docs checked:
- Hugging Face CLI uses the modern `hf` command.
- Install on macOS/Linux with `curl -LsSf https://hf.co/cli/install.sh | bash`
- Alternative: `pip install -U huggingface_hub`
- Login: `hf auth login` or `hf auth login --token $HF_TOKEN`

Recommended here:
- keep `HF_TOKEN` in your shell or `.envrc`/secret manager
- use `hf auth whoami` to verify

## Modal setup

Docs checked:
- install with `pip install modal`
- authenticate with `modal setup` or `modal token set`
- env vars `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET` override `~/.modal.toml`

Recommended here:
- use env vars for automation/CI
- use `modal setup` locally for interactive setup
- keep training code in `modal/`

## Hermes portability recommendation

For this profile, prefer the repo's portability flow over raw copy-paste of profile internals:
- machine bootstrap: `/home/hermes/work/hermes-stack/scripts/bootstrap-machine.sh`
- export profile bundle: `/home/hermes/work/hermes-stack/scripts/export-profile.sh --profile ai-lab`
- import profile bundle: `/home/hermes/work/hermes-stack/scripts/import-profile.sh --archive <bundle.tar.gz>`
- Hindsight restore helper exists at `/home/hermes/work/hermes-stack/scripts/restore-hindsight.sh`

Hermes built-in backup/export/import can still help, but the hermes-stack wrappers are better aligned with this multi-machine setup because they preserve shared SOUL sources, rendered environment context, and profile-local Hindsight wiring.
