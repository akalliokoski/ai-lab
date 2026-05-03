from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
SOURCE_DATASET = "artifact-card-failure-modes-forced-top2-v2"
TARGET_DATASET = "artifact-card-failure-modes-forced-top2-v2p2"
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
        "contrast_note": "Use this when the overall task outcome stayed effectively unchanged, not just because one field is still weak.",
        "allowed_evidence_keys": ["repeated-no-change", "mixed-fields-no-clear-task-win"],
    },
    "missing-required-detail": {
        "meaning": "required fields were missing, too long, non-canonical, or omitted",
        "contrast_note": "Use this only for explicit missing, omitted, overlong, or non-canonical field behavior. Generic weakness alone is not enough.",
        "allowed_evidence_keys": ["missing-or-noncanonical-field"],
    },
    "generic-explanation": {
        "meaning": "the answer became broader, vaguer, or more generic than the reference",
        "contrast_note": "Use this when the answer drifts broader or vaguer than the reference, not just when a field is incomplete.",
        "allowed_evidence_keys": ["broader-than-reference"],
    },
    "overlap-contaminated-eval": {
        "meaning": "train/eval overlap or overlap-heavy rows made the improvement untrustworthy",
        "contrast_note": "Use this only when overlap or overlap-heavy phrasing is explicit in the evidence.",
        "allowed_evidence_keys": ["overlap-untrustworthy"],
    },
    "phrase-copy-or-template-collapse": {
        "meaning": "the output copied prompt phrasing, collapsed into template fragments, or repeated distorted phrases",
        "contrast_note": "Use this only when copied wording, template fragments, or repeated distortion is explicit in the evidence.",
        "allowed_evidence_keys": ["phrase-copy-distortion"],
    },
    "hallucinated-detail": {
        "meaning": "the output invented details not present in the input evidence",
        "contrast_note": "Use this only when blockers, facts, or details are invented beyond the observed evidence.",
        "allowed_evidence_keys": ["invented-detail"],
    },
    "wrong-causal-point": {
        "meaning": "the answer missed the core causal explanation even if structure stayed valid",
        "contrast_note": "Use this when the answer misses the main causal explanation, not just because it is generic or incomplete.",
        "allowed_evidence_keys": ["missed-core-cause"],
    },
    "fluency-without-correctness": {
        "meaning": "a stronger or smoother answer sounded better without becoming more correct",
        "contrast_note": "Use this when wording or fluency improves but correctness does not meaningfully improve.",
        "allowed_evidence_keys": ["fluency-gain-without-correctness"],
    },
}

ALL_EVIDENCE_KEYS = [
    "repeated-no-change",
    "mixed-fields-no-clear-task-win",
    "missing-or-noncanonical-field",
    "broader-than-reference",
    "overlap-untrustworthy",
    "phrase-copy-distortion",
    "invented-detail",
    "missed-core-cause",
    "fluency-gain-without-correctness",
]

TASK_CONFIG = {
    "system_prompt": (
        "You are the Hermes AI Lab forced top-2 selector. Read the evidence and return only one valid JSON object "
        "with exactly these keys: primary_label, primary_evidence_key, secondary_label, secondary_evidence_key. "
        "Both labels must be copied exactly from the allowed failure-mode list and must be distinct. "
        "Each evidence key must be copied exactly from the allowed list for the chosen label. Do not add prose."
    ),
    "expected_fields": ["primary_label", "primary_evidence_key", "secondary_label", "secondary_evidence_key"],
    "list_fields": [],
    "max_new_tokens": 64,
}

INSTRUCTION = (
    "Read the experiment evidence and return one strict JSON object with exactly these keys: "
    "primary_label, primary_evidence_key, secondary_label, secondary_evidence_key. "
    "Choose exactly two distinct failure modes ranked strongest to second strongest. Output JSON only."
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n")


def infer_positive_evidence_key(label: str) -> str:
    allowed = LABEL_SPECS[label]["allowed_evidence_keys"]
    return allowed[0]


def build_output(primary_label: str, secondary_label: str) -> dict[str, str]:
    return {
        "primary_label": primary_label,
        "primary_evidence_key": infer_positive_evidence_key(primary_label),
        "secondary_label": secondary_label,
        "secondary_evidence_key": infer_positive_evidence_key(secondary_label),
    }


def build_input(case: dict[str, Any]) -> str:
    label_cards = "\n".join(
        (
            f"- {label}: {LABEL_SPECS[label]['meaning']} | contrast: {LABEL_SPECS[label]['contrast_note']} "
            f"| allowed evidence keys if selected: {', '.join(LABEL_SPECS[label]['allowed_evidence_keys'])}"
        )
        for label in LABELS
    )
    evidence_block = "\n".join(case["observed_evidence"])
    return (
        "Run metadata:\n"
        f"run_id: {case['run_id']}\n"
        f"dataset_name: {case['dataset_name']}\n"
        f"model_name: {case['model_name']}\n\n"
        f"Run summary:\n{case['summary']}\n\n"
        "Allowed failure modes:\n"
        + "\n".join(f"- {label}" for label in LABELS)
        + "\n\nAllowed evidence keys:\n"
        + "\n".join(f"- {key}" for key in ALL_EVIDENCE_KEYS)
        + "\n\nLabel cards:\n"
        + label_cards
        + "\n\nDecision rule:\n"
        + "- Return valid JSON only.\n"
        + "- Choose exactly two distinct labels: one primary and one secondary.\n"
        + "- primary_label must be the strongest supported failure mode overall.\n"
        + "- secondary_label must be the second strongest supported failure mode overall.\n"
        + "- Do not output out, none, abstain, unknown, or free-form explanations.\n"
        + "- Copy labels and evidence keys exactly from the allowed lists.\n"
        + "- primary_evidence_key must directly support primary_label.\n"
        + "- secondary_evidence_key must directly support secondary_label.\n"
        + "- If all required fields stayed present and parseable, do not choose missing-required-detail.\n"
        + "- Only choose overlap-contaminated-eval when overlap or overlap-heavy phrasing is explicit.\n"
        + "- Only choose phrase-copy-or-template-collapse when copied wording, template fragments, or repeated distortion is explicit.\n"
        + "- Prefer the smallest exact ranked pair directly supported by the evidence.\n\n"
        + "Observed evidence:\n"
        + f"{evidence_block}\n\n"
        + "Output template:\n"
        + '{"primary_label":"<allowed_label>","primary_evidence_key":"<allowed_evidence_key>","secondary_label":"<allowed_label>","secondary_evidence_key":"<allowed_evidence_key>"}'
    )


def build_supplemental_rows(start_index: int) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    cases = json.loads(SUPPLEMENTAL_CASES_PATH.read_text())
    rows: list[dict[str, str]] = []
    metadata_rows: list[dict[str, Any]] = []
    for offset, case in enumerate(cases):
        primary_label, secondary_label = case["gold_pair"]
        output_obj = build_output(primary_label, secondary_label)
        rows.append(
            {
                "instruction": INSTRUCTION,
                "input": build_input(case),
                "output": json.dumps(output_obj, separators=(",", ":")),
            }
        )
        metadata_rows.append(
            {
                "source_example_index": start_index + offset,
                "source_run_id": case["run_id"],
                "gold_pair": case["gold_pair"],
                "gold_primary_label": primary_label,
                "gold_secondary_label": secondary_label,
                "gold_primary_evidence_key": output_obj["primary_evidence_key"],
                "gold_secondary_evidence_key": output_obj["secondary_evidence_key"],
                "source_kind": "supplemental-v2p2",
            }
        )
    return rows, metadata_rows


def build_readme(
    train_count: int,
    eval_count: int,
    mean_train_input_chars: float,
    inherited_train_count: int,
    inherited_eval_count: int,
    supplemental_train_count: int,
) -> str:
    return f"""# {TARGET_DATASET}

Forced-top-2 semantic patch branch for the artifact-card failure-mode project.

Goal
- keep `artifact-card-failure-modes-forced-top2-v2` as the semantic anchor
- add a small train-only semantic patch instead of more contract wording
- target the specific surviving confusion boundaries from the latest branch-aware evals

Why this branch exists
- `forced-top2-v2` is still the strongest current semantic baseline under branch-aware scoring
- `forced-top2-v2p1` and `forced-top2-v3` both regressed toward the same fallback pair `missing-required-detail + generic-explanation`
- the remaining failures are concentrated in four places: `fluency-without-correctness`, `hallucinated-detail`, `wrong-causal-point`, and overlap label-slot confusion

What changed from `forced-top2-v2`
- inherited every original `forced-top2-v2` train/eval row unchanged
- added {supplemental_train_count} new train-only rows with the same four-field target and the same task config
- the new rows sharpen exactly these boundaries:
  - `fluency-without-correctness -> missing-required-detail`
  - `hallucinated-detail -> missing-required-detail`
  - `wrong-causal-point -> no-material-change`
  - `overlap-contaminated-eval -> phrase-copy-or-template-collapse`
- no anti-fence wording or generation-prefix changes were added here; this is a semantic patch only

Current shape
- train examples: {train_count}
- eval examples: {eval_count}
- inherited train / eval examples from `forced-top2-v2`: {inherited_train_count} / {inherited_eval_count}
- new train-only supplemental examples: {supplemental_train_count}
- mean train input length: {mean_train_input_chars:.1f} chars

Success criterion
- beat the current `forced-top2-v2` fallback concentration without losing its stronger top-2 recovery
- keep branch-aware evaluation as the decision surface, especially `top2_set_match_rate`, `top2_ordered_match_rate`, `invalid_row_rate`, and the new selector-collapse metrics
- if this branch does not beat `forced-top2-v2`, keep the anchor and preserve this patch as a negative result instead of stacking more prompt mass
"""


def main() -> None:
    source_dir = DATA_ROOT / SOURCE_DATASET
    target_dir = DATA_ROOT / TARGET_DATASET
    target_dir.mkdir(parents=True, exist_ok=True)

    base_train_rows = load_jsonl(source_dir / "train.jsonl")
    base_eval_rows = load_jsonl(source_dir / "eval.jsonl")
    base_train_metadata = json.loads((source_dir / "train_metadata.json").read_text())
    base_eval_metadata = json.loads((source_dir / "eval_metadata.json").read_text())

    supplemental_rows, supplemental_metadata = build_supplemental_rows(start_index=len(base_train_metadata))

    train_rows = base_train_rows + supplemental_rows
    train_metadata = base_train_metadata + supplemental_metadata

    write_jsonl(target_dir / "train.jsonl", train_rows)
    write_jsonl(target_dir / "eval.jsonl", base_eval_rows)
    (target_dir / "train_metadata.json").write_text(json.dumps(train_metadata, indent=2) + "\n")
    (target_dir / "eval_metadata.json").write_text(json.dumps(base_eval_metadata, indent=2) + "\n")
    (target_dir / "task_config.json").write_text(json.dumps(TASK_CONFIG, indent=2) + "\n")

    mean_train_input_chars = sum(len(row["input"]) for row in train_rows) / len(train_rows)
    readme = build_readme(
        train_count=len(train_rows),
        eval_count=len(base_eval_rows),
        mean_train_input_chars=mean_train_input_chars,
        inherited_train_count=len(base_train_rows),
        inherited_eval_count=len(base_eval_rows),
        supplemental_train_count=len(supplemental_rows),
    )
    (target_dir / "README.md").write_text(readme)

    summary = {
        "dataset_name": TARGET_DATASET,
        "source_dataset": SOURCE_DATASET,
        "train_rows": len(train_rows),
        "eval_rows": len(base_eval_rows),
        "mean_train_input_chars": mean_train_input_chars,
        "inherited_train_examples": len(base_train_rows),
        "inherited_eval_examples": len(base_eval_rows),
        "supplemental_train_examples": len(supplemental_rows),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
