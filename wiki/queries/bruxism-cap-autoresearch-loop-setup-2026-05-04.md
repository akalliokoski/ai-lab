---
title: Best native setup for the bruxism-cap autoresearch loop (2026-05-04)
created: 2026-05-04
updated: 2026-05-04
type: query
tags: [agent, workflow, infrastructure, vps, research, notes]
sources:
  - ../docs/autoresearch-artifact-card-playbook.md
  - ../../.hermes/profiles/ai-lab/skills/research/autoresearch/SKILL.md
  - ../../.hermes/profiles/ai-lab/skills/research/autoresearch/references/cron-modal-vps.md
---

# Question
What is the best native, patch-free way to run the `bruxism-cap` autoresearch loop on this VPS?

# Short answer
Use a profile-local recurring cron job plus a profile-local ticker service, not Hermes source patches and not the generic gateway service. The recurring job should stay self-contained, repo-grounded, and limited to one primary increment per pass; the ticker should be a durable system service that runs `hermes --profile ai-lab cron tick --accept-hooks` from `/home/hermes/work/ai-lab` with `HERMES_HOME=/home/hermes/.hermes/profiles/ai-lab`. [[bruxism-cap]] [[karpathy-llm-wiki-and-autoresearch-improvements-2026-05-01]] [[ai-lab-learning-path]]

# Why this is the best current setup

## 1. It stays inside Hermes-native extension points
- The job logic lives in the cron prompt, loaded skills, repo files, and wiki updates.
- The scheduler drive loop uses the built-in `hermes cron tick --accept-hooks` command.
- No local Hermes source edits are required.

## 2. It matches how this VPS actually behaves
- The generic `hermes-gateway.service` on this host is active, but it is configured with `HERMES_HOME=/home/hermes/.hermes`, not the ai-lab profile home.
- User-level systemd was not available from the ai-lab shell session, so an ad-hoc `bash` background loop worked as an emergency repair but is not the most durable operating mode.
- System-level systemd is available and already used for Hermes services on this VPS, so the most reliable repair is an ai-lab-specific ticker service under `/etc/systemd/system/`.

## 3. It separates the two concerns correctly
- The cron job defines what research work to do.
- The ticker service defines how scheduled jobs get advanced.
- That separation makes it easier to inspect failures: prompt mistakes, repo errors, and scheduler liveness are different problems.

# Recommended architecture

## A. Recurring loop job
Keep one main recurring job with these properties:
- profile: `ai-lab`
- workdir: `/home/hermes/work/ai-lab`
- skills: `autoresearch`, `llm-wiki`
- enabled toolsets: `terminal`, `file`
- deliver: `local`
- schedule: `every 30m` while the project is active
- prompt contract:
  - inspect repo and wiki state first
  - do exactly one primary increment per pass
  - always update `wiki/log.md`
  - update the active project docs/wiki when understanding changes
  - leave a clear next-step handoff

## B. Immediate kickoff job
When starting or restarting a campaign, create a separate one-shot kickoff run a minute or two ahead instead of waiting for the next interval slot. This is especially important here because overdue interval jobs can fast-forward to the next future slot after ticker downtime instead of replaying the missed pass.

## C. Dedicated ai-lab ticker service
Best durable host-side setup:
- create one service dedicated to ai-lab cron ticking
- run it as user `hermes`
- set:
  - `HOME=/home/hermes`
  - `HERMES_HOME=/home/hermes/.hermes/profiles/ai-lab`
  - `WorkingDirectory=/home/hermes/work/ai-lab`
- exec either:
  - `/home/hermes/work/ai-lab/scripts/cron_tick_loop.sh`
  - or an inline equivalent that explicitly calls `/home/hermes/.local/bin/hermes --profile ai-lab cron tick --accept-hooks`
- use `Restart=always`

This is better than the current ad-hoc background shell because it survives shell exit, reboot, and accidental process loss more cleanly.

# Important corrections to the current loop state

## 1. Do not rely on generic gateway status as the health signal
For this profile, real scheduler health should be checked in this order:
1. ai-lab `session_cron_*.json` files
2. live ticker process or service state
3. repo/wiki/artifact outputs
4. only then `cron list` or gateway status output

## 2. The current recurring job is still bounded to only six total runs
The current `bruxism-cap-autoresearch-loop` job is configured as `every 30m` with `repeat.times = 6` and only `1` completed run recorded so far. That is good for a short campaign, but it is not the best long-lived default if the user wants an ongoing loop. In that case, the repeat cap should be removed and stopping should happen via pause/remove, or via a fresh bounded campaign created intentionally.

## 3. Prefer `deliver: local` unless user-visible notifications are explicitly needed
For repo-grounded ai-lab work, local delivery plus wiki/repo updates is the safest default. Add messaging delivery only when the user wants live reports routed to chat.

# Recommended operating pattern
1. Keep the main loop recurring at `every 30m` during active debugging.
2. Remove the repeat cap if the goal is continuous unattended progress rather than a six-pass campaign.
3. On this VPS, back the loop with a dedicated ai-lab systemd ticker service.
4. When restarting after downtime, create a fresh one-shot kickoff job immediately.
5. Judge success from session files and generated artifacts, not only surfaced scheduler metadata.

# Bottom line
The best native setup is: profile-local recurring cron job + dedicated ai-lab ticker service + one-shot kickoff on restart + wiki-first bookkeeping. That gives reliable unattended progress without depending on patched Hermes Agent code. [[artifact-driven-experiment-debugging]] [[bruxism-cap]] [[karpathy-llm-wiki-and-autoresearch-improvements-2026-05-01]]
