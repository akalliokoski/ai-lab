from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
SOURCE_DATASET = "artifact-card-failure-modes-v1"
TARGET_DATASET = "artifact-card-failure-modes-joint-rank-v1"
SUPPLEMENTAL_CASES_PATH = DATA_ROOT / "artifact-card-failure-modes-rank-select-v2" / "supplemental_train_cases.json"

LABELS = [
    "no-material-change",
    "missing-required-detail",
    "generic-explanation",
    "overlap-contaminated-eval",
    "phrase-copy-or-template-collapse",
    "hallucinated-detail",
    "wrong-causal-point",
    "fluency-without-correctness",
]

LABEL_SPECS: dict[str, dict[str, str]] = {
    "no-material-change": {
        "meaning": "overall outcome stayed effectively the same",
        "cue": "repeated-no-change or mixed-fields-no-clear-task-win",
    },
    "missing-required-detail": {
        "meaning": "required fields were missing, omitted, too long, or non-canonical",
        "cue": "missing-or-noncanonical-field",
    },
    "generic-explanation": {
        "meaning": "answer became broader, vaguer, or less tied to the reference",
        "cue": "broader-than-reference",
    },
    "overlap-contaminated-eval": {
        "meaning": "overlap made the apparent gain untrustworthy",
        "cue": "overlap-untrustworthy",
    },
    "phrase-copy-or-template-collapse": {
        "meaning": "copied phrasing, template fragments, or distorted repeats appeared",
        "cue": "phrase-copy-distortion",
    },
    "hallucinated-detail": {
        "meaning": "details were invented beyond the input evidence",
        "cue": "invented-detail",
    },
    "wrong-causal-point": {
        "meaning": "main causal explanation was still missed",
        "cue": "missed-core-cause",
    },
    "fluency-without-correctness": {
        "meaning": "sounded smoother without becoming more correct",
        "cue": "fluency-gain-without-correctness",
    },
}

TASK_CONFIG = {
    "system_prompt": (
        "You are the Hermes AI Lab joint rank selector. Read the evidence and return only one valid JSON object. "
        "The JSON must contain exactly the 8 allowed failure-mode keys. Each value must be one of primary, secondary, or out. "
        "Use exactly one primary label and exactly one secondary label. Set all other labels to out. Do not add prose."
    ),
    "expected_fields": LABELS,
    "list_fields": [],
    "max_new_tokens": 96,
}

INSTRUCTION = (
    "Read the experiment evidence and return one strict JSON object whose keys are the 8 allowed failure modes. "
    "Each value must be primary, secondary, or out. Use exactly one primary label and exactly one secondary label. "
    "Output JSON only."
)

RUN_ID_RE = re.compile(r"run_id:\s*(\S+)")
DATASET_RE = re.compile(r"dataset_name:\s*(\S+)")
MODEL_RE = re.compile(r"model_name:\s*(\S+)")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def extract_run_metadata(text: str) -> dict[str, str]:
    return {
        "run_id": RUN_ID_RE.search(text).group(1),
        "dataset_name": DATASET_RE.search(text).group(1),
        "model_name": MODEL_RE.search(text).group(1),
    }


def extract_summary(text: str) -> str:
    marker = "Run summary:\n"
    start = text.index(marker) + len(marker)
    end = text.index("\n\nObserved evidence:")
    return text[start:end].strip()


def extract_observed_evidence(text: str) -> list[str]:
    marker = "Observed evidence:\n"
    start = text.index(marker) + len(marker)
    end = text.index("\n\nOperator note:")
    return [line.strip() for line in text[start:end].splitlines() if line.strip()]


def render_source_input(case: dict[str, Any]) -> str:
    evidence_block = "\n".join(f"- {line}" for line in case["observed_evidence"])
    return (
        "Run metadata:\n"
        f"run_id: {case['run_id']}\n"
        f"dataset_name: {case['dataset_name']}\n"
        f"model_name: {case['model_name']}\n\n"
        "Decision rule:\n"
        "- Return valid JSON only.\n"
        "- Return exactly 2 labels under primary_failure_modes.\n"
        "- Copy allowed labels exactly. Do not invent synonyms.\n"
        "- Prefer the smallest exact label set directly supported by the evidence.\n\n"
        "Allowed failure modes:\n"
        "- no-material-change\n"
        "- missing-required-detail\n"
        "- generic-explanation\n"
        "- overlap-contaminated-eval\n"
        "- phrase-copy-or-template-collapse\n"
        "- hallucinated-detail\n"
        "- wrong-causal-point\n"
        "- fluency-without-correctness\n\n"
        f"Run summary:\n{case['summary']}\n\n"
        "Observed evidence:\n"
        f"{evidence_block}\n\n"
        "Operator note:\n"
        "Prefer the smallest exact label set that fits the evidence."
    )


def build_supplemental_source_rows() -> list[dict[str, str]]:
    cases = json.loads(SUPPLEMENTAL_CASES_PATH.read_text())
    rows = []
    for case in cases:
        rows.append(
            {
                "instruction": (
                    "Read the experiment evidence and return one strict JSON object with exactly this key: "
                    "primary_failure_modes. Output JSON only."
                ),
                "input": render_source_input(case),
                "output": json.dumps({"primary_failure_modes": case["gold_pair"]}, ensure_ascii=False),
            }
        )
    return rows


def build_joint_output(primary_label: str, secondary_label: str) -> dict[str, str]:
    output = {label: "out" for label in LABELS}
    output[primary_label] = "primary"
    output[secondary_label] = "secondary"
    return output


def build_input(metadata: dict[str, str], summary: str, evidence_lines: list[str]) -> str:
    label_cards = "\n".join(
        f"- {label}: {LABEL_SPECS[label]['meaning']} | positive cue: {LABEL_SPECS[label]['cue']}"
        for label in LABELS
    )
    evidence_block = "\n".join(evidence_lines)
    output_template = "{" + ",".join(f'\"{label}\":\"primary|secondary|out\"' for label in LABELS) + "}"
    return (
        "Run metadata:\n"
        f"run_id: {metadata['run_id']}\n"
        f"dataset_name: {metadata['dataset_name']}\n"
        f"model_name: {metadata['model_name']}\n\n"
        f"Run summary:\n{summary}\n\n"
        "Label cards:\n"
        f"{label_cards}\n\n"
        "Decision rule:\n"
        "- Return valid JSON only.\n"
        "- Use exactly one primary label and exactly one secondary label.\n"
        "- All remaining labels must be out.\n"
        "- Choose the smallest exact pair directly supported by the evidence.\n"
        "- missing-required-detail must be out if all required fields stayed present and parseable.\n"
        "- phrase-copy-or-template-collapse should only be positive when copied wording, template fragments, or distorted repeats are explicit in the evidence.\n"
        "- fluency-without-correctness is only positive when better wording did not become more correct.\n"
        "- overlap-contaminated-eval is only positive when overlap or overlap-heavy phrasing is explicit.\n"
        "- Never output more than one primary or more than one secondary.\n\n"
        "Observed evidence:\n"
        f"{evidence_block}\n\n"
        "Output template:\n"
        f"{output_template}"
    )


def build_rows(split: str) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    source_dir = DATA_ROOT / SOURCE_DATASET
    source_rows = load_jsonl(source_dir / f"{split}.jsonl")
    supplemental_count = 0
    if split == "train":
        supplemental_rows = build_supplemental_source_rows()
        supplemental_count = len(supplemental_rows)
        source_rows = source_rows + supplemental_rows

    rows: list[dict[str, str]] = []
    metadata_rows: list[dict[str, Any]] = []
    original_count = len(source_rows) - supplemental_count

    for source_index, source_row in enumerate(source_rows):
        source_output = json.loads(source_row["output"])
        gold_pair = list(source_output["primary_failure_modes"])
        if len(gold_pair) != 2:
            raise ValueError(f"Expected exactly 2 failure modes, got {gold_pair}")
        primary_label, secondary_label = gold_pair
        metadata = extract_run_metadata(source_row["input"])
        summary = extract_summary(source_row["input"])
        evidence_lines = extract_observed_evidence(source_row["input"])
        source_kind = "supplemental" if split == "train" and source_index >= original_count else "original"
        output_obj = build_joint_output(primary_label, secondary_label)
        rows.append(
            {
                "instruction": INSTRUCTION,
                "input": build_input(metadata, summary, evidence_lines),
                "output": json.dumps(output_obj, separators=(",", ":")),
            }
        )
        metadata_rows.append(
            {
                "source_example_index": source_index,
                "source_run_id": metadata["run_id"],
                "gold_pair": gold_pair,
                "gold_primary_label": primary_label,
                "gold_secondary_label": secondary_label,
                "source_kind": source_kind,
            }
        )
    return rows, metadata_rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n")


def build_readme(train_count: int, eval_count: int, mean_train_input_chars: float, source_train_count: int, source_eval_count: int, supplemental_train_count: int) -> str:
    return f"""# {TARGET_DATASET}

Joint-selector branch for the artifact-card failure-mode project.

Goal
- keep the task focused on `primary_failure_modes`
- score all 8 labels together in one output instead of one label per row
- force global normalization: exactly one `primary`, exactly one `secondary`, all remaining labels `out`
- test whether joint scoring fixes the underselection and dominant-label problems that survived the independent rank-select family

Why this branch exists
- `artifact-card-failure-modes-pairwise-v1` is still the strongest downstream branch, but ordered recovery stayed `0.0`
- `artifact-card-failure-modes-rank-select-v1` improved row metrics while reconstruction stayed `0.0`
- `artifact-card-failure-modes-rank-select-v2` fixed schema leakage, but reconstruction still stayed `0.0` and underselection got worse
- the next disciplined branch is to score all labels jointly in one constrained decision object instead of asking the model to score each label independently

What changed from earlier branches
- source rows come from `{SOURCE_DATASET}` plus the train-only calibration cases introduced for rank-select-v2
- each source example now becomes one joint ranking row instead of 8 independent candidate rows
- output is one strict JSON object with the 8 label names as fixed keys and values in `primary | secondary | out`
- the prompt includes compact label cards and explicit global constraints so the model must allocate the two positive slots jointly

Current shape
- train examples: {train_count}
- eval examples: {eval_count}
- source examples before train-only supplements: {source_train_count} train / {source_eval_count} eval
- train-only supplemental source examples: {supplemental_train_count}
- mean train input length: {mean_train_input_chars:.1f} chars

Output contract
- keys are fixed to the 8 allowed labels
- values must be exactly one of:
  - `primary`
  - `secondary`
  - `out`
- exactly one key must be `primary`
- exactly one key must be `secondary`
- all remaining keys must be `out`

Success criterion
- exact joint map match should stay interpretable, but it is not the main success condition
- reconstructed top-2 set match should beat the current best downstream baseline from `artifact-card-failure-modes-pairwise-v1` (`0.25`)
- reconstructed ordered top-2 match should beat the current `0.0` pairwise and rank-select results
- if this branch still fails, the next redesign should likely move to an explicitly learned two-pass selector or a smaller learned tournament among pre-shortlisted labels rather than more prompt-only reshaping
"""


def main() -> None:
    target_dir = DATA_ROOT / TARGET_DATASET
    target_dir.mkdir(parents=True, exist_ok=True)

    train_rows, train_metadata = build_rows("train")
    eval_rows, eval_metadata = build_rows("eval")

    write_jsonl(target_dir / "train.jsonl", train_rows)
    write_jsonl(target_dir / "eval.jsonl", eval_rows)
    (target_dir / "train_metadata.json").write_text(json.dumps(train_metadata, indent=2) + "\n")
    (target_dir / "eval_metadata.json").write_text(json.dumps(eval_metadata, indent=2) + "\n")
    (target_dir / "task_config.json").write_text(json.dumps(TASK_CONFIG, indent=2) + "\n")

    source_train_count = len(load_jsonl(DATA_ROOT / SOURCE_DATASET / "train.jsonl"))
    source_eval_count = len(load_jsonl(DATA_ROOT / SOURCE_DATASET / "eval.jsonl"))
    supplemental_train_count = len(json.loads(SUPPLEMENTAL_CASES_PATH.read_text()))
    mean_train_input_chars = sum(len(row["input"]) for row in train_rows) / len(train_rows)
    readme = build_readme(
        train_count=len(train_rows),
        eval_count=len(eval_rows),
        mean_train_input_chars=mean_train_input_chars,
        source_train_count=source_train_count,
        source_eval_count=source_eval_count,
        supplemental_train_count=supplemental_train_count,
    )
    (target_dir / "README.md").write_text(readme)

    summary = {
        "dataset_name": TARGET_DATASET,
        "source_dataset": SOURCE_DATASET,
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "mean_train_input_chars": mean_train_input_chars,
        "source_train_examples": source_train_count,
        "source_eval_examples": source_eval_count,
        "supplemental_train_examples": supplemental_train_count,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
