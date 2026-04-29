#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = REPO_ROOT / ".env"
DEFAULT_VOLUME = "ai-lab-unsloth-artifacts"
DEFAULT_DATASET = "hermes-tutor-v1"


def load_env_file(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def run_modal_json(args: list[str]) -> list[dict[str, str]] | dict:
    env = os.environ.copy()
    env.update(load_env_file(ENV_PATH))
    result = subprocess.run(
        ["modal", *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )
    return json.loads(result.stdout)


def get_summary(volume: str, dataset: str, run_id: str) -> dict:
    env = os.environ.copy()
    env.update(load_env_file(ENV_PATH))
    result = subprocess.run(
        [
            "modal",
            "volume",
            "get",
            volume,
            f"/{dataset}/{run_id}/run_summary.json",
            "-",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
        cwd=REPO_ROOT,
    )
    text = result.stdout
    marker = "✓ Finished downloading files to local!"
    if marker in text:
        text = text.split(marker, 1)[0]
    return json.loads(text.strip())


def main() -> int:
    volume = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_VOLUME
    dataset = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DATASET

    entries = run_modal_json(["volume", "ls", volume, f"/{dataset}", "--json"])
    run_ids = sorted(
        [Path(entry["Filename"]).name for entry in entries if entry.get("Type") == "dir"],
        reverse=True,
    )

    if not run_ids:
        print(f"No runs found in volume={volume} dataset={dataset}")
        return 0

    print(f"volume={volume}")
    print(f"dataset={dataset}")
    print()
    for run_id in run_ids:
        summary = get_summary(volume, dataset, run_id)
        metrics = summary.get("metrics", {})
        print(
            " | ".join(
                [
                    f"run_id={run_id}",
                    f"model={summary.get('model_name')}",
                    f"steps={summary.get('max_steps')}",
                    f"train_rows={summary.get('train_rows')}",
                    f"loss={metrics.get('train_loss')}",
                    f"runtime_s={metrics.get('train_runtime')}",
                ]
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
