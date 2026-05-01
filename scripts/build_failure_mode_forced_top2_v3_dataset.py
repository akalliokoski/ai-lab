from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
SOURCE_DATASET = "artifact-card-failure-modes-v1"
TARGET_DATASET = "artifact-card-failure-modes-forced-top2-v3"
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
        "You are the Hermes AI Lab forced top-2 selector. Read the evidence and return only one raw JSON object "
        "with exactly these keys: primary_label, primary_evidence_key, secondary_label, secondary_evidence_key. "
        "Never wrap the JSON in Markdown, never start with ```json, never end with ```, and never add prose. "
        "Both labels must be copied exactly from the allowed failure-mode list and must be distinct. "
        "Each evidence key must be copied exactly from the allowed list for the chosen label."
    ),
    "expected_fields": ["primary_label", "primary_evidence_key", "secondary_label", "secondary_evidence_key"],
    "list_fields": [],
    "max_new_tokens": 48,
    "generation_prefix": "{",
}

INSTRUCTION = (
    "Read the experiment evidence and return one strict raw JSON object with exactly these keys: "
    "primary_label, primary_evidence_key, secondary_label, secondary_evidence_key. "
    "Choose exactly two distinct failure modes ranked strongest to second strongest. "
    "Output raw JSON only. Do not use Markdown fences, do not write ```json, and do not add any prose."
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


def build_output(primary_label: str, secondary_label: str, evidence_lines: list[str]) -> dict[str, str]:
    return {
        "primary_label": primary_label,
        "primary_evidence_key": infer_positive_evidence_key(primary_label, evidence_lines),
        "secondary_label": secondary_label,
        "secondary_evidence_key": infer_positive_evidence_key(secondary_label, evidence_lines),
    }


def build_input(metadata: dict[str, str], summary: str, evidence_lines: list[str]) -> str:
    label_cards = "\n".join(
        (
            f"- {label}: {LABEL_SPECS[label]['meaning']} | contrast: {LABEL_SPECS[label]['contrast_note']} "
            f"| allowed evidence keys if selected: {', '.join(LABEL_SPECS[label]['allowed_evidence_keys'])}"
        )
        for label in LABELS
    )
    evidence_block = "\n".join(evidence_lines)
    return (
        "Run metadata:\n"
        f"run_id: {metadata['run_id']}\n"
        f"dataset_name: {metadata['dataset_name']}\n"
        f"model_name: {metadata['model_name']}\n\n"
        f"Run summary:\n{summary}\n\n"
        "Allowed failure modes:\n"
        + "\n".join(f"- {label}" for label in LABELS)
        + "\n\nAllowed evidence keys:\n"
        + "\n".join(f"- {key}" for key in ALL_EVIDENCE_KEYS)
        + "\n\nLabel cards:\n"
        + label_cards
        + "\n\nDecision rule:\n"
        + "- Return raw JSON only.\n"
        + "- The first character of the answer must be {.\n"
        + "- Do not wrap the answer in Markdown or code fences.\n"
        + "- Do not output ```json, ```, json, or any prose before or after the object.\n"
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
        + "Invalid output examples:\n"
        + "- ```json {\"primary_label\":\"no-material-change\",...} ```\n"
        + "- Here is the JSON: {\"primary_label\":\"no-material-change\",...}\n"
        + "- json {\"primary_label\":\"no-material-change\",...}\n\n"
        + "Observed evidence:\n"
        + f"{evidence_block}\n\n"
        + "Output template:\n"
        + '{"primary_label":"<allowed_label>","primary_evidence_key":"<allowed_evidence_key>","secondary_label":"<allowed_label>","secondary_evidence_key":"<allowed_evidence_key>"}'
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
        if primary_label == secondary_label:
            raise ValueError(f"Expected distinct labels, got {gold_pair}")
        metadata = extract_run_metadata(source_row["input"])
        summary = extract_summary(source_row["input"])
        evidence_lines = extract_observed_evidence(source_row["input"])
        source_kind = "supplemental" if split == "train" and source_index >= original_count else "original"
        output_obj = build_output(primary_label, secondary_label, evidence_lines)
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
                "gold_primary_evidence_key": output_obj["primary_evidence_key"],
                "gold_secondary_evidence_key": output_obj["secondary_evidence_key"],
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

Forced-top-2 anti-fence patch branch for the artifact-card failure-mode project.

Goal
- keep the task focused on `primary_failure_modes`
- preserve the no-abstention forced top-2 target that first beat the `pairwise-v1` downstream baseline
- harden strict raw-JSON compliance after the Qwen3 comparison regressed by wrapping answers in Markdown fences
- test whether prompt-level anti-fence pressure plus generation-prefix steering improves raw output validity without redesigning the target

Why this branch exists
- `artifact-card-failure-modes-forced-top2-v2` was the first decomposition branch to beat `pairwise-v1` downstream, so the target shape itself is worth keeping
- the direct Qwen3 rerun on `forced-top2-v2` did not fail mainly on label semantics; it failed because 5/8 tuned rows wrapped plausible JSON in Markdown code fences
- the next disciplined patch is to harden the output contract before spending more budget on more model swaps or a fresh target redesign

What changed from `forced-top2-v2`
- source rows still come from `{SOURCE_DATASET}` plus the same train-only calibration cases introduced for rank-select-v2
- labels, evidence keys, and reconstruction metadata stay the same so downstream comparisons remain apples-to-apples
- the instruction, system prompt, and decision rules now explicitly ban Markdown fences and prose wrappers
- the task config now sets `generation_prefix` to `{{` so inference starts inside a JSON object instead of leaving room for ```json preambles
- `max_new_tokens` is reduced from `64` to `48` to tighten the response budget around the fixed four-field object

Current shape
- train examples: {train_count}
- eval examples: {eval_count}
- source examples before train-only supplements: {source_train_count} train / {source_eval_count} eval
- train-only supplemental source examples: {supplemental_train_count}
- mean train input length: {mean_train_input_chars:.1f} chars

Success criterion
- top-2 set match should beat the current best downstream baseline from `artifact-card-failure-modes-pairwise-v1` (`0.25`)
- ordered top-2 match should finally rise above `0.0`
- evidence-key accuracy matters as a grounding check, but label-pair recovery is the main success criterion
- if this branch still fails, the next redesign should likely become a staged shortlist / tournament selector rather than another flat one-shot target
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
