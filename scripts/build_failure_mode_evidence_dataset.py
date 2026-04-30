from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
SOURCE_DATASET = "artifact-card-failure-modes-v1"
TARGET_DATASET = "artifact-card-failure-modes-evidence-v1"

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

TASK_CONFIG = {
    "system_prompt": (
        "You are the Hermes AI Lab evidence-conditioned failure-mode judge. Read the user evidence and return only one "
        "valid JSON object with exactly these keys: candidate_label, supported, evidence_key. Copy candidate_label exactly. "
        "Set supported to yes or no. Choose evidence_key from the allowed list shown in the prompt. Do not add prose before or after the JSON."
    ),
    "expected_fields": ["candidate_label", "supported", "evidence_key"],
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
        "Decision rule:\n"
        "- Return valid JSON only.\n"
        "- Copy candidate_label exactly.\n"
        "- If the evidence directly supports the candidate label, set supported to yes.\n"
        "- If the evidence does not directly support the candidate label, set supported to no and evidence_key to not-supported.\n"
        "- Use only the evidence below. Do not infer extra facts.\n\n"
        f"Candidate label: {candidate_label}\n"
        f"Candidate meaning: {spec['meaning']}\n"
        f"Contrast note: {spec['contrast_note']}\n\n"
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
        metadata = extract_run_metadata(source_row["input"])
        evidence_lines = extract_observed_evidence(source_row["input"])

        for candidate_label in LABELS:
            supported = "yes" if candidate_label in gold_pair else "no"
            evidence_key = (
                infer_positive_evidence_key(candidate_label, evidence_lines)
                if supported == "yes"
                else "not-supported"
            )
            output_obj = {
                "candidate_label": candidate_label,
                "supported": supported,
                "evidence_key": evidence_key,
            }
            rows.append(
                {
                    "instruction": (
                        "Read the experiment evidence and judge one candidate failure label. "
                        "Return one strict JSON object with exactly these keys: candidate_label, supported, evidence_key. "
                        "Output JSON only."
                    ),
                    "input": build_input(metadata, evidence_lines, candidate_label),
                    "output": json.dumps(output_obj, separators=(",", ": ")),
                }
            )
            metadata_rows.append(
                {
                    "source_example_index": source_index,
                    "source_run_id": metadata["run_id"],
                    "candidate_label": candidate_label,
                    "gold_pair": gold_pair,
                    "gold_supported": supported,
                    "gold_evidence_key": evidence_key,
                    "confusion_group": infer_confusion_group(candidate_label),
                }
            )
    return rows, metadata_rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n")


def build_readme(train_count: int, eval_count: int) -> str:
    return f"""# {TARGET_DATASET}

Evidence-conditioned per-label scaffold for the artifact-card project.

Goal
- keep the task focused on `primary_failure_modes`
- replace broad pairwise comparisons with one candidate label at a time
- bind each positive label to a tiny canonical evidence key instead of a bare belongs/not-belongs target
- keep prompts shorter than the pairwise branch so more tokens are actual evidence

Why this branch exists
- `artifact-card-failure-modes-pairwise-v1` improved reconstructed held-out top-2 set match to `0.25`, but still failed ordered recovery and over-promoted `missing-required-detail`
- the next strategy memo recommended evidence-conditioned per-label scoring with shorter prompts, confusion-targeted contrast data, and explicit evidence anchoring
- this scaffold turns that recommendation into runnable repo artifacts without changing the shared Unsloth training entrypoint

What changed from earlier branches
- source rows come from `{SOURCE_DATASET}` so the base evidence and gold top-2 labels stay aligned with the current failure-mode task
- each original row is expanded into 8 candidate-label judgments, one per allowed failure mode
- output is now one strict JSON object with exactly three keys: `candidate_label`, `supported`, `evidence_key`
- positive rows carry a tiny canonical evidence key; negative rows use `not-supported`
- prompts keep only the local candidate meaning, a short contrast note, and the observed evidence bullets

Current shape
- train examples: {train_count}
- eval examples: {eval_count}
- source examples: 26 train / 8 eval before expansion
- source format: JSONL with `instruction`, `input`, `output`
- target output: JSON string only
- helper metadata: `train_metadata.json`, `eval_metadata.json`

Success criterion
- row-level exact match should beat the earlier binary branch while staying interpretable by field
- per-label support precision/recall should make `missing-required-detail` over-selection easier to detect
- reconstructed positive-label set match across the original held-out cases should beat the current pairwise downstream result (`0.25`)
- if the scaffold still over-predicts `missing-required-detail`, the next patch should narrow to the four hardest contrast groups instead of expanding the full label space again
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
    (target_dir / "README.md").write_text(build_readme(len(train_rows), len(eval_rows)))

    print(json.dumps({
        "target_dataset": TARGET_DATASET,
        "train_rows": len(train_rows),
        "eval_rows": len(eval_rows),
        "target_dir": str(target_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
