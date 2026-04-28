#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -d .venv ]]; then
  uv venv
fi
source .venv/bin/activate
uv pip install -e '.[train]'
printf '
Bootstrap complete.
'
printf 'Activate with: source %s/.venv/bin/activate
' "$(pwd)"
printf 'Then consider machine-specific installs for Unsloth based on the current docs.
'
