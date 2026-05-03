#!/usr/bin/env bash
set -euo pipefail

cd /home/hermes/work/ai-lab

while true; do
  printf '[%s] hermes cron tick\n' "$(date --iso-8601=seconds)"
  hermes cron tick --accept-hooks || true
  sleep 30
done
