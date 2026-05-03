# ai-lab

Home AI lab for learning by doing with Hermes.

This repo is the working home of the `ai-lab` Hermes profile.

Core themes
- Unsloth fine-tuning and RL learning
- Hugging Face Hub workflows
- Modal serverless GPU experiments
- Reproducible notes, docs, and small experiments
- Smooth movement between VPS, Telegram, and MacBook

Profile facts
- Hermes profile: `ai-lab`
- Workspace: `/home/hermes/work/ai-lab`
- Profile wiki: `/home/hermes/work/ai-lab/wiki`
- Hindsight bank: `hermes-ai-lab`

## Start here

1. Read `docs/start-here.md`
2. Read `docs/unsloth-self-learning-path.md`
3. Read `docs/first-artifact-card-experiment.md`
4. Read `docs/first-unsloth-experiment.md` for the earlier tutor-track history
5. Open the wiki in `wiki/`
6. Start Hermes in this profile with:
   - `ai-lab chat`
   - or `hermes -p ai-lab chat`

## Current first experiment

Default project:
- `artifact-card-sft`

Additional starter project scaffold:
- `projects/bruxism-cap/` — public CAP Sleep Database pilot for tiny EEG/EMG bruxism baselines with subject-aware evaluation

Current repo artifacts:
- dataset scaffold in `data/artifact-card-v1/`
- experiment brief in `docs/first-artifact-card-experiment.md`
- Modal training entrypoint in `modal/train_unsloth_artifact_card.py`
- scoring helper in `scripts/evaluate_artifact_card_run.py`

Previous first-project track retained as a negative result and debugging case study:
- `Hermes AI lab tutor adapter`
- dataset history in `data/hermes-tutor-v1/` and `data/hermes-tutor-v2/`
- run history in `docs/first-unsloth-experiment.md`

## Suggested workflow split

VPS
- Hermes orchestration
- Telegram access
- notes, repo maintenance, automation
- light CPU-safe data preparation and eval scripting

MacBook Pro M3
- local Python work
- notebook exploration
- lightweight local model experiments
- selective Unsloth/local inference tests if compatible

Modal / remote GPU
- real GPU fine-tuning runs
- larger batch jobs
- repeatable training jobs once local prototypes are clear

## Bootstrapping this repo

Core Python tooling:

```bash
cd /home/hermes/work/ai-lab
./scripts/bootstrap-python.sh
```

That sets up a local `.venv` with neutral tooling first.
Machine-specific GPU installs are documented in `docs/start-here.md`.

Then create a local secret file and verify it:

```bash
cp .env.example .env
python3 scripts/check_env.py
```

## GitHub remote

A local git repo is initialized, but no GitHub remote was created automatically because `gh` is not authenticated on this machine.

After logging in with `gh auth login`, create and connect a repo with something like:

```bash
cd /home/hermes/work/ai-lab
gh repo create ai-lab --private --source=. --remote=origin --push
```

Adjust the repo name/visibility as you prefer.

## Portability

For moving the Hermes profile between machines, prefer the hermes-stack portability helpers documented in `docs/profile-portability.md`.
