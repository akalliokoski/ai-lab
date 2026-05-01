from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_NAME = "hermes-tutor-v1"
DATA_ROOT = ROOT / "data"


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def preview(dataset_name: str, split: str) -> None:
    data_dir = DATA_ROOT / dataset_name
    rows = load_jsonl(data_dir / f"{split}.jsonl")
    print(f"dataset: {dataset_name} | {split}: {len(rows)} rows")
    print("-" * 60)
    for idx, row in enumerate(rows[:3], start=1):
        print(f"Example {idx}")
        print(f"instruction: {row['instruction']}")
        print(f"input: {row['input'] or '<empty>'}")
        print(f"output: {row['output']}")
        print("-" * 60)


if __name__ == "__main__":
    dataset_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATASET_NAME
    preview(dataset_name, "train")
    preview(dataset_name, "eval")
