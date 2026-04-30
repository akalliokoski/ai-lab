from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
SOURCE_DATASET = "artifact-card-failure-modes-v1"
TARGET_DATASET = "artifact-card-failure-modes-contrast-v1"
ANCHOR_LABEL = "missing-required-detail"

RIVAL_SPECS: list[dict[str, str]] = [
    {
        "rival_label": "generic-explanation",
        "contrast_group": "missing-required-detail-vs-generic-explanation",
        "rival_meaning": "the answer became broader, vaguer, or more generic than the reference",
        "rival_evidence_key": "broader-than-reference",
        "contrast_note": "Use missing-required-detail for missing, omitted, overlong, or non-canonical field behavior. Use generic-explanation for broader or vaguer answers that still cover the field slot.",
    },
    {
        "rival_label": "no-material-change",
        "contrast_group": "missing-required-detail-vs-no-material-change",
        "rival_meaning": "repeated runs changed little or the outcome stayed effectively the same",
        "rival_evidence_key": "repeated-no-change",
        "contrast_note": "Use missing-required-detail for field-level omission or non-canonical output. Use no-material-change when the overall outcome stayed effectively unchanged even if the structure looked cleaner.",
    },
    {
        "rival_label": "hallucinated-detail",
        "contrast_group": "missing-required-detail-vs-hallucinated-detail",
        "rival_meaning": "the output invented details not present in the input evidence",
        "rival_evidence_key": "invented-detail",
        "contrast_note": "Use missing-required-detail for omitted or malformed required content. Use hallucinated-detail only when the output adds unsupported facts or blockers.",
    },
    {
        "rival_label": "overlap-contaminated-eval",
        "contrast_group": "missing-required-detail-vs-overlap-contaminated-eval",
        "rival_meaning": "train/eval overlap or overlap-heavy rows made the apparent gain untrustworthy",
        "rival_evidence_key": "overlap-untrustworthy",
        "contrast_note": "Use missing-required-detail for local field defects. Use overlap-contaminated-eval only when the evidence says the improvement is untrustworthy because of train/eval overlap.",
    },
]

ANCHOR_MEANING = "required fields were missing, too long, non-canonical, or omitted"
ANCHOR_EVIDENCE_KEY = "missing-or-noncanonical-field"
BOTH_KEY = "both-supported"
NEITHER_KEY = "other-label-dominates"
CONTRAST_UNIVERSE = {ANCHOR_LABEL} | {spec["rival_label"] for spec in RIVAL_SPECS}

TASK_CONFIG = {
    "system_prompt": (
        "You are the Hermes AI Lab contrast-group failure-mode judge. Read the evidence and return only one valid JSON object "
        "with exactly these keys: contrast_group, decision, evidence_key. Copy contrast_group exactly. "
        "Set decision to one allowed value shown in the prompt. Choose evidence_key from the allowed list shown in the prompt. "
        "Do not add prose before or after the JSON."
    ),
    "expected_fields": ["contrast_group", "decision", "evidence_key"],
    "list_fields": [],
    "max_new_tokens": 56,
}

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


def extract_observed_evidence(text: str) -> list[str]:
    marker = "Observed evidence:\n"
    start = text.index(marker) + len(marker)
    end = text.index("\n\nOperator note:")
    return [line.strip() for line in text[start:end].splitlines() if line.strip()]


def decision_for_group(gold_pair: list[str], rival_label: str) -> str:
    gold = set(gold_pair)
    has_anchor = ANCHOR_LABEL in gold
    has_rival = rival_label in gold
    if has_anchor and has_rival:
        return "both"
    if has_anchor:
        return ANCHOR_LABEL
    if has_rival:
        return rival_label
    return "neither"


def evidence_key_for_decision(decision: str, rival_evidence_key: str) -> str:
    if decision == ANCHOR_LABEL:
        return ANCHOR_EVIDENCE_KEY
    if decision == "both":
        return BOTH_KEY
    if decision == "neither":
        return NEITHER_KEY
    return rival_evidence_key


def build_input(metadata: dict[str, str], evidence_lines: list[str], spec: dict[str, str]) -> str:
    evidence_block = "\n".join(evidence_lines)
    contrast_group = spec["contrast_group"]
    rival_label = spec["rival_label"]
    return (
        f"run_id: {metadata['run_id']}\n"
        f"dataset_name: {metadata['dataset_name']}\n\n"
        f"contrast_group: {contrast_group}\n"
        f"anchor_label: {ANCHOR_LABEL} = {ANCHOR_MEANING}\n"
        f"rival_label: {rival_label} = {spec['rival_meaning']}\n"
        f"contrast_note: {spec['contrast_note']}\n\n"
        "Return JSON only with keys contrast_group, decision, evidence_key.\n"
        f"Allowed decisions: {ANCHOR_LABEL} | {rival_label} | both | neither\n"
        f"- {ANCHOR_LABEL} = anchor supported, rival not supported\n"
        f"- {rival_label} = rival supported, anchor not supported\n"
        "- both = both labels supported\n"
        "- neither = another outside label fits better\n"
        f"Allowed evidence keys: {ANCHOR_EVIDENCE_KEY} | {spec['rival_evidence_key']} | {BOTH_KEY} | {NEITHER_KEY}\n\n"
        "Observed evidence:\n"
        f"{evidence_block}"
    )


def build_rows(split: str) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    source_dir = DATA_ROOT / SOURCE_DATASET
    source_rows = load_jsonl(source_dir / f"{split}.jsonl")
    rows: list[dict[str, str]] = []
    metadata_rows: list[dict[str, Any]] = []

    for source_index, source_row in enumerate(source_rows):
        source_output = json.loads(source_row["output"])
        gold_pair = list(source_output["primary_failure_modes"])
        metadata = extract_run_metadata(source_row["input"])
        evidence_lines = extract_observed_evidence(source_row["input"])
        reconstructable = set(gold_pair).issubset(CONTRAST_UNIVERSE)

        for group_index, spec in enumerate(RIVAL_SPECS):
            decision = decision_for_group(gold_pair, spec["rival_label"])
            evidence_key = evidence_key_for_decision(decision, spec["rival_evidence_key"])
            output_obj = {
                "contrast_group": spec["contrast_group"],
                "decision": decision,
                "evidence_key": evidence_key,
            }
            rows.append(
                {
                    "instruction": (
                        "Read the experiment evidence and make one local contrast-group decision. "
                        "Return one strict JSON object with exactly these keys: contrast_group, decision, evidence_key. "
                        "Output JSON only."
                    ),
                    "input": build_input(metadata, evidence_lines, spec),
                    "output": json.dumps(output_obj, separators=(",", ": ")),
                }
            )
            metadata_rows.append(
                {
                    "source_example_index": source_index,
                    "source_run_id": metadata["run_id"],
                    "group_index": group_index,
                    "contrast_group": spec["contrast_group"],
                    "anchor_label": ANCHOR_LABEL,
                    "rival_label": spec["rival_label"],
                    "gold_pair": gold_pair,
                    "gold_decision": decision,
                    "gold_evidence_key": evidence_key,
                    "reconstructable": reconstructable,
                }
            )
    return rows, metadata_rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n")


def build_readme(train_count: int, eval_count: int, reconstructable_train: int, reconstructable_eval: int) -> str:
    return f"""# {TARGET_DATASET}

Confusion-targeted contrast scaffold for the artifact-card failure-mode project.

Goal
- keep the task focused on `primary_failure_modes`
- shrink the supervision space to the four hardest `missing-required-detail` confusion boundaries
- require exactly one local decision per contrast group before reconstruction
- keep tiny canonical evidence keys, but only inside those narrow contrast tasks

Why this branch exists
- `artifact-card-failure-modes-pairwise-v1` was the strongest downstream decomposition result so far, but it still over-promoted `missing-required-detail`
- `artifact-card-failure-modes-evidence-v1` improved row-level structure, but reconstructed held-out top-2 set match fell back to `0.0` because the model over-accepted too many labels
- the next strategy after that negative result was to narrow the supervision to the exact confusion boundaries instead of keeping full 8-label expansion

What changed from earlier branches
- source rows still come from `{SOURCE_DATASET}` so the evidence and gold pairs stay aligned with the current failure-mode task
- each original row now becomes exactly 4 contrast-group judgments instead of 8 candidate-label judgments or 28 pairwise comparisons
- each row targets one local contrast group with output keys `contrast_group`, `decision`, and `evidence_key`
- decisions are now one of four local states: anchor label, rival label, `both`, or `neither`
- reconstruction is only scored on source examples whose gold pair stays inside the 5-label contrast universe

Contrast groups
- `missing-required-detail` vs `generic-explanation`
- `missing-required-detail` vs `no-material-change`
- `missing-required-detail` vs `hallucinated-detail`
- `missing-required-detail` vs `overlap-contaminated-eval`

Current shape
- train examples: {train_count}
- eval examples: {eval_count}
- source examples before expansion: 26 train / 8 eval
- contrast rows per source example: 4
- reconstructable source examples inside the contrast universe: {reconstructable_train} train / {reconstructable_eval} eval
- source format: JSONL with `instruction`, `input`, and `output`
- target output: JSON string only
- helper metadata: `train_metadata.json`, `eval_metadata.json`

Success criterion
- row-level exact match should beat the noisy comparison behavior from the full pairwise branch while staying interpretable by contrast group
- reconstruction on the in-universe held-out subset should recover the original 2-label set more reliably than the broad evidence branch
- if this branch still fails, the next move should likely be targeted source-case additions or a two-stage rank-then-select scheme rather than another broad prompt rewrite
"""


def main() -> None:
    target_dir = DATA_ROOT / TARGET_DATASET
    target_dir.mkdir(parents=True, exist_ok=True)

    train_rows, train_meta = build_rows("train")
    eval_rows, eval_meta = build_rows("eval")
    reconstructable_train = len({(row['source_example_index'], row['source_run_id']) for row in train_meta if row['reconstructable']})
    reconstructable_eval = len({(row['source_example_index'], row['source_run_id']) for row in eval_meta if row['reconstructable']})

    write_jsonl(target_dir / "train.jsonl", train_rows)
    write_jsonl(target_dir / "eval.jsonl", eval_rows)
    (target_dir / "train_metadata.json").write_text(json.dumps(train_meta, indent=2) + "\n")
    (target_dir / "eval_metadata.json").write_text(json.dumps(eval_meta, indent=2) + "\n")
    (target_dir / "task_config.json").write_text(json.dumps(TASK_CONFIG, indent=2) + "\n")
    (target_dir / "README.md").write_text(
        build_readme(len(train_rows), len(eval_rows), reconstructable_train, reconstructable_eval)
    )

    print(json.dumps({
        "target_dataset": TARGET_DATASET,
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "reconstructable_train_examples": reconstructable_train,
        "reconstructable_eval_examples": reconstructable_eval,
        "target_dir": str(target_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
