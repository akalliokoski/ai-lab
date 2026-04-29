from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "hermes-tutor-v1"


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def preview(split: str) -> None:
    rows = load_jsonl(DATA_DIR / f"{split}.jsonl")
    print(f"{split}: {len(rows)} rows")
    print("-" * 60)
    for idx, row in enumerate(rows[:3], start=1):
        print(f"Example {idx}")
        print(f"instruction: {row['instruction']}")
        print(f"input: {row['input'] or '<empty>'}")
        print(f"output: {row['output']}")
        print("-" * 60)


if __name__ == "__main__":
    preview("train")
    preview("eval")
