#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
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


def modal_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(load_env_file(ENV_PATH))
    return env


def run_modal_json(args: list[str]) -> list[dict[str, str]] | dict:
    result = subprocess.run(
        ["modal", *args],
        check=True,
        capture_output=True,
        text=True,
        env=modal_env(),
        cwd=REPO_ROOT,
    )
    return json.loads(result.stdout)


def get_summary(volume: str, dataset: str, run_id: str) -> dict:
    result = subprocess.run(
        ["modal", "volume", "get", volume, f"/{dataset}/{run_id}/run_summary.json", "-"],
        check=True,
        capture_output=True,
        text=True,
        env=modal_env(),
        cwd=REPO_ROOT,
    )
    text = result.stdout
    marker = "✓ Finished downloading files to local!"
    if marker in text:
        text = text.split(marker, 1)[0]
    return json.loads(text.strip())


def latest_run_id(volume: str, dataset: str) -> str:
    entries = run_modal_json(["volume", "ls", volume, f"/{dataset}", "--json"])
    run_ids = sorted(
        [Path(entry["Filename"]).name for entry in entries if entry.get("Type") == "dir"],
        reverse=True,
    )
    if not run_ids:
        raise SystemExit(f"No runs found in volume={volume} dataset={dataset}")
    return run_ids[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Show one Modal run summary for the tutor adapter.")
    parser.add_argument("run_id", nargs="?", default="latest", help="Run ID like 20260429T093147Z, or 'latest'")
    parser.add_argument("--volume", default=DEFAULT_VOLUME)
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--json", action="store_true", help="Print raw JSON")
    args = parser.parse_args()

    run_id = latest_run_id(args.volume, args.dataset) if args.run_id == "latest" else args.run_id
    summary = get_summary(args.volume, args.dataset, run_id)

    if args.json:
        print(json.dumps(summary, indent=2))
        return 0

    metrics = summary.get("metrics", {})
    print(f"run_id: {summary.get('run_id')}")
    print(f"dataset: {summary.get('dataset_name')}")
    print(f"model: {summary.get('model_name')}")
    print(f"steps: {summary.get('max_steps')}")
    print(f"train_rows: {summary.get('train_rows')}")
    print(f"eval_rows: {summary.get('eval_rows')}")
    print(f"artifact_dir: {summary.get('artifact_dir')}")
    print(f"adapter_dir: {summary.get('adapter_dir')}")
    print(f"train_loss: {metrics.get('train_loss')}")
    print(f"train_runtime_s: {metrics.get('train_runtime')}")
    print()
    print("sample_eval:")
    for idx, sample in enumerate(summary.get("sample_eval", []), start=1):
        print(f"  [{idx}] instruction: {sample.get('instruction')}")
        print(f"      reference: {sample.get('reference')}")
        print(f"      base: {sample.get('base_response')}")
        print(f"      tuned: {sample.get('tuned_response')}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
