from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
SOURCE_DATASET = "artifact-card-failure-modes-v1"
TARGET_DATASET = "artifact-card-failure-modes-rank-select-v2"
SUPPLEMENTAL_CASES_PATH = DATA_ROOT / TARGET_DATASET / "supplemental_train_cases.json"

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
        "contrast_note": "Do not use this only because one field is still weak. Use it when the overall task outcome stayed effectively unchanged.",
    },
    "missing-required-detail": {
        "meaning": "required fields were missing, too long, non-canonical, or omitted",
        "contrast_note": "Use this only for explicit missing, omitted, overlong, or non-canonical field behavior. Generic weakness alone is not enough.",
    },
    "generic-explanation": {
        "meaning": "the answer became broader, vaguer, or more generic than the reference",
        "contrast_note": "Use this when the answer drifts broader or vaguer than the reference, not just when a field is incomplete.",
    },
    "overlap-contaminated-eval": {
        "meaning": "train/eval overlap or overlap-heavy rows made the improvement untrustworthy",
        "contrast_note": "Use this only when the evidence says train/eval overlap or overlap-heavy phrasing makes the gain untrustworthy.",
    },
    "phrase-copy-or-template-collapse": {
        "meaning": "the output copied prompt phrasing, collapsed into template fragments, or repeated distorted phrases",
        "contrast_note": "Use this when copied wording, template fragments, or repeated distortion appears in the output.",
    },
    "hallucinated-detail": {
        "meaning": "the output invented details not present in the input evidence",
        "contrast_note": "Use this only when the output adds blockers, facts, or details that are not present in the input evidence.",
    },
    "wrong-causal-point": {
        "meaning": "the answer missed the core causal explanation even if structure stayed valid",
        "contrast_note": "Use this when the answer misses the main causal explanation, not just because it is generic or incomplete.",
    },
    "fluency-without-correctness": {
        "meaning": "a stronger or smoother answer sounded better without becoming more correct",
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
        "You are the Hermes AI Lab rank calibration scorer. Read the user evidence and return only one valid JSON object "
        "with exactly these keys: candidate_label, support_rank, evidence_key. Copy candidate_label exactly. "
        "Use support_rank=primary only when this label should rank first overall, secondary only when it should rank second overall, "
        "and out otherwise. Never add extra keys or prose."
    ),
    "expected_fields": ["candidate_label", "support_rank", "evidence_key"],
    "list_fields": [],
    "max_new_tokens": 40,
}

INSTRUCTION = (
    "Read the experiment evidence and score one candidate failure label for a later top-2 selection step. "
    "Return one strict JSON object with exactly these keys: candidate_label, support_rank, evidence_key. "
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
        return "rank-calibration-target"
    if label in {"generic-explanation", "no-material-change", "hallucinated-detail", "overlap-contaminated-eval"}:
        return f"mdr-vs-{label}"
    if label in {"fluency-without-correctness", "phrase-copy-or-template-collapse"}:
        return "false-positive-suppression"
    return "other-boundary"


def build_input(metadata: dict[str, str], evidence_lines: list[str], candidate_label: str, positive_evidence_key: str) -> str:
    spec = LABEL_SPECS[candidate_label]
    evidence_block = "\n".join(evidence_lines)
    return (
        "Run metadata:\n"
        f"run_id: {metadata['run_id']}\n"
        f"dataset_name: {metadata['dataset_name']}\n"
        f"model_name: {metadata['model_name']}\n\n"
        "Candidate card:\n"
        f"candidate_label: {candidate_label}\n"
        f"candidate_meaning: {spec['meaning']}\n"
        f"contrast_note: {spec['contrast_note']}\n"
        f"positive_evidence_key_if_selected: {positive_evidence_key}\n\n"
        "Decision rule:\n"
        "- Exactly 2 labels are positive overall: one primary label and one secondary label.\n"
        "- primary = this candidate should rank first overall.\n"
        "- secondary = this candidate should rank second overall.\n"
        "- out = this candidate should not appear in the final top 2.\n"
        "- If support_rank is primary or secondary, set evidence_key to the exact positive_evidence_key_if_selected value.\n"
        "- If support_rank is out, set evidence_key to not-supported.\n"
        "- Return exactly one JSON object with exactly 3 keys: candidate_label, support_rank, evidence_key.\n"
        "- Never add extra keys, lists, or copied policy text.\n\n"
        "Observed evidence:\n"
        f"{evidence_block}\n\n"
        "Output template:\n"
        f'{{"candidate_label":"{candidate_label}","support_rank":"primary|secondary|out","evidence_key":"{positive_evidence_key}|not-supported"}}'
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
        evidence_lines = extract_observed_evidence(source_row["input"])
        source_kind = "supplemental" if split == "train" and source_index >= original_count else "original"

        for candidate_label in LABELS:
            positive_evidence_key = infer_positive_evidence_key(candidate_label, evidence_lines)
            if candidate_label == primary_label:
                support_rank = "primary"
                evidence_key = positive_evidence_key
            elif candidate_label == secondary_label:
                support_rank = "secondary"
                evidence_key = positive_evidence_key
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
                    "instruction": INSTRUCTION,
                    "input": build_input(metadata, evidence_lines, candidate_label, positive_evidence_key),
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
                    "positive_evidence_key_if_selected": positive_evidence_key,
                    "confusion_group": infer_confusion_group(candidate_label),
                    "source_kind": source_kind,
                }
            )
    return rows, metadata_rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n")


def build_readme(
    train_count: int,
    eval_count: int,
    mean_train_input_chars: float,
    source_train_count: int,
    source_eval_count: int,
    supplemental_train_count: int,
) -> str:
    return f"""# {TARGET_DATASET}

Rank-calibration patch for the artifact-card failure-mode branch.

Goal
- keep the task focused on `primary_failure_modes`
- keep one-label-at-a-time supervision, but reduce schema leakage and sharpen rank calibration
- make `missing-required-detail` easier to select when field-omission evidence is explicit
- reduce false positives on `fluency-without-correctness` and `phrase-copy-or-template-collapse`

Why this branch exists
- `artifact-card-failure-modes-rank-select-v1` improved row metrics but still failed the real downstream objective
- the strongest repeated errors were calibration errors, not label-copying errors
- the first rank-select run underselected to zero positives on 5 of 8 held-out source examples and overselected noisy style labels on others
- one tuned row also leaked prompt schema by copying an `allowed_evidence_keys` tail into the JSON, so the next patch should shorten and harden the output contract directly

What changed from v1
- training now adds {supplemental_train_count} train-only source cases targeted at:
  - stronger `missing-required-detail` primary or secondary evidence
  - harder negative control against spurious `fluency-without-correctness`
  - harder negative control against spurious `phrase-copy-or-template-collapse`
- the row prompt now uses a much smaller candidate card instead of a long `allowed_evidence_keys` list
- each row names exactly one `positive_evidence_key_if_selected` value and forces `not-supported` for `out`
- the prompt explicitly says there are exactly 2 positive labels overall and bans extra keys or copied policy text
- `max_new_tokens` is reduced to `40` to discourage policy echoing and extra JSON tails

Current shape
- train examples: {train_count}
- eval examples: {eval_count}
- source examples before expansion: {source_train_count} train / {source_eval_count} eval
- supplemental train-only source examples: {supplemental_train_count}
- source format: JSONL with `instruction`, `input`, `output`
- target output: JSON string only
- helper metadata: `train_metadata.json`, `eval_metadata.json`
- mean train input length: about {mean_train_input_chars:.1f} chars

Success criterion
- row-level exact match should stay interpretable by field, but it is not the main success condition
- stage-2 reconstructed top-2 set match should beat the current best downstream baseline from `artifact-card-failure-modes-pairwise-v1` (`0.25`)
- stage-2 reconstructed ordered-pair match should beat the current `0.0` pairwise result
- if this branch still fails, the next redesign should likely separate stage-1 scoring from stage-2 selection more explicitly instead of relying on prompt-only calibration
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
    source_train_count = len({(item['source_example_index'], item['source_run_id']) for item in train_meta if item['source_kind'] == 'original'})
    supplemental_train_count = len({(item['source_example_index'], item['source_run_id']) for item in train_meta if item['source_kind'] == 'supplemental'})
    source_eval_count = len({(item['source_example_index'], item['source_run_id']) for item in eval_meta})
    (target_dir / "README.md").write_text(
        build_readme(
            len(train_rows),
            len(eval_rows),
            mean_train_input_chars,
            source_train_count,
            source_eval_count,
            supplemental_train_count,
        )
    )

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
