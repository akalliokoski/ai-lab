from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
SOURCE_DATASET = "artifact-card-failure-modes-v1"
TARGET_DATASET = "artifact-card-failure-modes-rank-select-v1"

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

LABEL_SPECS: dict[str, dict[str, Any]] = {
    "no-material-change": {
        "meaning": "repeated runs changed little or the outcome stayed effectively the same",
        "allowed_evidence_keys": ["repeated-no-change", "mixed-fields-no-clear-task-win", "not-supported"],
        "contrast_note": "Use this when the run did not materially improve the real task outcome. Do not use it only because one field is still weak.",
    },
    "missing-required-detail": {
        "meaning": "required fields were missing, too long, non-canonical, or omitted",
        "allowed_evidence_keys": ["missing-or-noncanonical-field", "not-supported"],
        "contrast_note": "Use this only for missing, long, free-form, or non-canonical field behavior. Generic weakness alone is not enough.",
    },
    "generic-explanation": {
        "meaning": "the answer became broader, vaguer, or more generic than the reference",
        "allowed_evidence_keys": ["broader-than-reference", "not-supported"],
        "contrast_note": "Use this when the answer drifts broader or vaguer than the reference, not just when a field is incomplete.",
    },
    "overlap-contaminated-eval": {
        "meaning": "train/eval overlap or overlap-heavy rows made the improvement untrustworthy",
        "allowed_evidence_keys": ["overlap-untrustworthy", "not-supported"],
        "contrast_note": "Use this only when the evidence says train/eval overlap or overlap-heavy phrasing makes the gain untrustworthy.",
    },
    "phrase-copy-or-template-collapse": {
        "meaning": "the output copied prompt phrasing, collapsed into template fragments, or repeated distorted phrases",
        "allowed_evidence_keys": ["phrase-copy-distortion", "not-supported"],
        "contrast_note": "Use this when copied wording, template fragments, or repeated distortion appears in the output.",
    },
    "hallucinated-detail": {
        "meaning": "the output invented details not present in the input evidence",
        "allowed_evidence_keys": ["invented-detail", "not-supported"],
        "contrast_note": "Use this only when the output adds blockers, facts, or details that are not present in the input evidence.",
    },
    "wrong-causal-point": {
        "meaning": "the answer missed the core causal explanation even if structure stayed valid",
        "allowed_evidence_keys": ["missed-core-cause", "not-supported"],
        "contrast_note": "Use this when the answer misses the main causal explanation, not just because it is generic or incomplete.",
    },
    "fluency-without-correctness": {
        "meaning": "a stronger or smoother answer sounded better without becoming more correct",
        "allowed_evidence_keys": ["fluency-gain-without-correctness", "not-supported"],
        "contrast_note": "Use this when wording or fluency improves but correctness does not meaningfully improve.",
    },
}

RANK_TO_SCORE = {
    "primary": 2,
    "secondary": 1,
    "out": 0,
}

TASK_CONFIG = {
    "system_prompt": (
        "You are the Hermes AI Lab rank-then-select failure-mode scorer. Read the user evidence and return only one valid "
        "JSON object with exactly these keys: candidate_label, support_rank, evidence_key. Copy candidate_label exactly. "
        "Set support_rank to primary, secondary, or out. Choose evidence_key from the allowed list shown in the prompt. "
        "Do not add prose before or after the JSON."
    ),
    "expected_fields": ["candidate_label", "support_rank", "evidence_key"],
    "list_fields": [],
    "max_new_tokens": 48,
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


def infer_positive_evidence_key(label: str, evidence_lines: list[str]) -> str:
    joined = "\n".join(evidence_lines).lower()
    if label == "no-material-change":
        if "repeated runs produced nearly identical outputs" in joined or "loss barely moved" in joined:
            return "repeated-no-change"
        return "mixed-fields-no-clear-task-win"
    if label == "missing-required-detail":
        return "missing-or-noncanonical-field"
    if label == "generic-explanation":
        return "broader-than-reference"
    if label == "overlap-contaminated-eval":
        return "overlap-untrustworthy"
    if label == "phrase-copy-or-template-collapse":
        return "phrase-copy-distortion"
    if label == "hallucinated-detail":
        return "invented-detail"
    if label == "wrong-causal-point":
        return "missed-core-cause"
    if label == "fluency-without-correctness":
        return "fluency-gain-without-correctness"
    raise KeyError(f"Unknown label: {label}")


def infer_confusion_group(label: str) -> str:
    if label == "missing-required-detail":
        return "dominant-default-check"
    if label in {"generic-explanation", "no-material-change", "hallucinated-detail", "overlap-contaminated-eval"}:
        return f"mdr-vs-{label}"
    return "other-boundary"


def build_input(metadata: dict[str, str], evidence_lines: list[str], candidate_label: str) -> str:
    spec = LABEL_SPECS[candidate_label]
    allowed_keys = "\n".join(f"- {key}" for key in spec["allowed_evidence_keys"])
    evidence_block = "\n".join(evidence_lines)
    return (
        "Run metadata:\n"
        f"run_id: {metadata['run_id']}\n"
        f"dataset_name: {metadata['dataset_name']}\n"
        f"model_name: {metadata['model_name']}\n\n"
        "Stage 1 scoring rule:\n"
        "- Return valid JSON only.\n"
        "- Copy candidate_label exactly.\n"
        "- Use support_rank=primary only if this label should rank first in the final 2-label decision.\n"
        "- Use support_rank=secondary only if this label should rank second in the final 2-label decision.\n"
        "- Use support_rank=out if this label should not appear in the final selected top 2.\n"
        "- If support_rank is out, set evidence_key to not-supported.\n"
        "- Use only the evidence below. Do not infer extra facts.\n\n"
        f"Candidate label: {candidate_label}\n"
        f"Candidate meaning: {spec['meaning']}\n"
        f"Contrast note: {spec['contrast_note']}\n\n"
        "Allowed support_rank values:\n"
        "- primary\n"
        "- secondary\n"
        "- out\n\n"
        "Allowed evidence keys:\n"
        f"{allowed_keys}\n\n"
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
        if len(gold_pair) != 2:
            raise ValueError(f"Expected exactly 2 failure modes, got {gold_pair}")
        primary_label, secondary_label = gold_pair
        metadata = extract_run_metadata(source_row["input"])
        evidence_lines = extract_observed_evidence(source_row["input"])

        for candidate_label in LABELS:
            if candidate_label == primary_label:
                support_rank = "primary"
                evidence_key = infer_positive_evidence_key(candidate_label, evidence_lines)
            elif candidate_label == secondary_label:
                support_rank = "secondary"
                evidence_key = infer_positive_evidence_key(candidate_label, evidence_lines)
            else:
                support_rank = "out"
                evidence_key = "not-supported"
            output_obj = {
                "candidate_label": candidate_label,
                "support_rank": support_rank,
                "evidence_key": evidence_key,
            }
            rows.append(
                {
                    "instruction": (
                        "Read the experiment evidence and score one candidate failure label for a later top-2 selection step. "
                        "Return one strict JSON object with exactly these keys: candidate_label, support_rank, evidence_key. "
                        "Output JSON only."
                    ),
                    "input": build_input(metadata, evidence_lines, candidate_label),
                    "output": json.dumps(output_obj, separators=(",", ":")),
                }
            )
            metadata_rows.append(
                {
                    "source_example_index": source_index,
                    "source_run_id": metadata["run_id"],
                    "candidate_label": candidate_label,
                    "gold_pair": gold_pair,
                    "gold_primary_label": primary_label,
                    "gold_secondary_label": secondary_label,
                    "gold_support_rank": support_rank,
                    "gold_score": RANK_TO_SCORE[support_rank],
                    "gold_evidence_key": evidence_key,
                    "confusion_group": infer_confusion_group(candidate_label),
                }
            )
    return rows, metadata_rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n")


def build_readme(train_count: int, eval_count: int, mean_train_input_chars: float) -> str:
    return f"""# {TARGET_DATASET}

Two-stage rank-then-select scaffold for the artifact-card failure-mode branch.

Goal
- keep the task focused on `primary_failure_modes`
- score one candidate label at a time with an explicit rank target
- preserve a deterministic stage-2 selector that picks the final top 2 labels from the stage-1 scores
- test whether explicit `primary` vs `secondary` supervision beats the current pairwise downstream baseline

Why this branch exists
- `artifact-card-failure-modes-pairwise-v1` is still the strongest downstream branch, but it only reached reconstructed top-2 set match `0.25` and ordered recovery stayed `0.0`
- `artifact-card-failure-modes-evidence-v1` improved local row metrics but reconstructed top-2 match stayed `0.0`
- `artifact-card-failure-modes-contrast-v1` and `contrast-v2` both collapsed to singleton `missing-required-detail` on the reconstructable held-out subset
- the next disciplined branch is to supervise the ranking stage directly, then judge the experiment by the final selected top 2 rather than row metrics alone

What changed from earlier branches
- source rows come from `{SOURCE_DATASET}` so the evidence and label vocabulary stay aligned with the decomposed task
- each original row is expanded into 8 candidate-label scoring rows, one per allowed failure mode
- output is now one strict JSON object with exactly three keys: `candidate_label`, `support_rank`, `evidence_key`
- `support_rank` uses an explicit 3-level target: `primary`, `secondary`, or `out`
- `scripts/evaluate_failure_mode_rank_select_run.py` performs stage-2 deterministic selection from the predicted stage-1 scores and reports both ordered and unordered reconstruction metrics

Current shape
- train examples: {train_count}
- eval examples: {eval_count}
- source examples: 26 train / 8 eval before expansion
- source format: JSONL with `instruction`, `input`, `output`
- target output: JSON string only
- helper metadata: `train_metadata.json`, `eval_metadata.json`
- mean train input length: about {mean_train_input_chars:.1f} chars

Success criterion
- row-level exact match should stay interpretable by field, but it is not the main success condition
- stage-2 reconstructed top-2 set match should beat the current best downstream baseline from `artifact-card-failure-modes-pairwise-v1` (`0.25`)
- stage-2 reconstructed ordered-pair match should beat the current `0.0` pairwise result
- if this branch still collapses to `missing-required-detail`, the next redesign should likely combine score supervision with targeted calibration or a separate learned selector instead of more prompt-only rewrites
"""


def main() -> None:
    target_dir = DATA_ROOT / TARGET_DATASET
    target_dir.mkdir(parents=True, exist_ok=True)

    train_rows, train_meta = build_rows("train")
    eval_rows, eval_meta = build_rows("eval")

    write_jsonl(target_dir / "train.jsonl", train_rows)
    write_jsonl(target_dir / "eval.jsonl", eval_rows)
    (target_dir / "train_metadata.json").write_text(json.dumps(train_meta, indent=2) + "\n")
    (target_dir / "eval_metadata.json").write_text(json.dumps(eval_meta, indent=2) + "\n")
    (target_dir / "task_config.json").write_text(json.dumps(TASK_CONFIG, indent=2) + "\n")

    mean_train_input_chars = sum(len(row["input"]) for row in train_rows) / len(train_rows)
    (target_dir / "README.md").write_text(build_readme(len(train_rows), len(eval_rows), mean_train_input_chars))

    summary = {
        "dataset_name": TARGET_DATASET,
        "source_dataset": SOURCE_DATASET,
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "mean_train_input_chars": mean_train_input_chars,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
