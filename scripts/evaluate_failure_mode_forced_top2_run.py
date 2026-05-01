from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

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

ALLOWED_EVIDENCE_KEYS_BY_LABEL = {
    "no-material-change": {"repeated-no-change", "mixed-fields-no-clear-task-win"},
    "missing-required-detail": {"missing-or-noncanonical-field"},
    "generic-explanation": {"broader-than-reference"},
    "overlap-contaminated-eval": {"overlap-untrustworthy"},
    "phrase-copy-or-template-collapse": {"phrase-copy-distortion"},
    "hallucinated-detail": {"invented-detail"},
    "wrong-causal-point": {"missed-core-cause"},
    "fluency-without-correctness": {"fluency-gain-without-correctness"},
}
EXPECTED_FIELDS = ["primary_label", "primary_evidence_key", "secondary_label", "secondary_evidence_key"]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().lower().split())


def safe_json_loads(text: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def valid_forced_top2(parsed: dict[str, Any] | None) -> tuple[bool, str | None]:
    if parsed is None:
        return False, "invalid-json"
    if list(parsed.keys()) != EXPECTED_FIELDS:
        return False, "wrong-keys"

    primary_label = normalize_text(parsed.get("primary_label"))
    secondary_label = normalize_text(parsed.get("secondary_label"))
    primary_evidence_key = normalize_text(parsed.get("primary_evidence_key"))
    secondary_evidence_key = normalize_text(parsed.get("secondary_evidence_key"))

    if primary_label not in LABELS:
        return False, "bad-primary-label"
    if secondary_label not in LABELS:
        return False, "bad-secondary-label"
    if primary_label == secondary_label:
        return False, "duplicate-labels"
    if primary_evidence_key not in ALLOWED_EVIDENCE_KEYS_BY_LABEL[primary_label]:
        return False, "bad-primary-evidence-key"
    if secondary_evidence_key not in ALLOWED_EVIDENCE_KEYS_BY_LABEL[secondary_label]:
        return False, "bad-secondary-evidence-key"
    return True, None


def score_rows(rows: list[dict[str, Any]], response_key: str) -> dict[str, Any]:
    total = len(rows)
    valid = 0
    exact = 0
    field_hits = {field: 0 for field in EXPECTED_FIELDS}
    invalid_examples: list[dict[str, Any]] = []
    invalid_reasons = Counter()

    for row in rows:
        reference = safe_json_loads(row["reference"])
        candidate = safe_json_loads(row[response_key])
        if reference is None:
            raise ValueError("Reference output is not valid JSON in eval row")
        ok, reason = valid_forced_top2(candidate)
        if not ok:
            invalid_reasons[reason or "invalid"] += 1
            if len(invalid_examples) < 3:
                invalid_examples.append(
                    {
                        "instruction": row["instruction"],
                        "response_key": response_key,
                        "response": row[response_key],
                        "reason": reason,
                    }
                )
            continue
        valid += 1
        row_exact = True
        for field in EXPECTED_FIELDS:
            hit = normalize_text(reference.get(field)) == normalize_text(candidate.get(field))
            if hit:
                field_hits[field] += 1
            else:
                row_exact = False
        if row_exact:
            exact += 1

    return {
        "rows": total,
        "valid_json_rate": valid / total if total else 0.0,
        "exact_row_match_rate": exact / total if total else 0.0,
        "field_accuracy": {field: field_hits[field] / total if total else 0.0 for field in EXPECTED_FIELDS},
        "invalid_reason_counts": dict(invalid_reasons),
        "invalid_examples": invalid_examples,
    }


def forced_top2_metrics(rows: list[dict[str, Any]], metadata_rows: list[dict[str, Any]], response_key: str) -> dict[str, Any]:
    if len(rows) != len(metadata_rows):
        raise ValueError("Eval metadata length does not match full_eval length")

    distinct_label_count = 0
    top2_set_match = 0
    top2_ordered_match = 0
    primary_label_match = 0
    secondary_label_match = 0
    primary_evidence_match = 0
    secondary_evidence_match = 0
    invalid_rows = 0
    label_histogram = Counter()
    mismatches: list[dict[str, Any]] = []
    per_label = defaultdict(lambda: {"gold_primary": 0, "gold_secondary": 0, "pred_primary": 0, "pred_secondary": 0})

    for row, meta in zip(rows, metadata_rows, strict=True):
        reference = safe_json_loads(row["reference"])
        candidate = safe_json_loads(row[response_key])
        if reference is None:
            raise ValueError("Reference output is not valid JSON in eval row")
        ok, reason = valid_forced_top2(candidate)
        if not ok:
            invalid_rows += 1
            if len(mismatches) < 5:
                mismatches.append(
                    {
                        "source_example_index": meta["source_example_index"],
                        "source_run_id": meta["source_run_id"],
                        "gold_pair": meta["gold_pair"],
                        "predicted": row[response_key],
                        "reason": reason,
                    }
                )
            continue

        primary_label = normalize_text(candidate.get("primary_label"))
        secondary_label = normalize_text(candidate.get("secondary_label"))
        primary_key = normalize_text(candidate.get("primary_evidence_key"))
        secondary_key = normalize_text(candidate.get("secondary_evidence_key"))
        predicted_pair = [primary_label, secondary_label]
        predicted_set = set(predicted_pair)
        gold_pair = list(meta["gold_pair"])
        gold_set = set(gold_pair)

        distinct_label_count += 1
        label_histogram.update(predicted_pair)
        per_label[gold_pair[0]]["gold_primary"] += 1
        per_label[gold_pair[1]]["gold_secondary"] += 1
        per_label[primary_label]["pred_primary"] += 1
        per_label[secondary_label]["pred_secondary"] += 1

        if predicted_set == gold_set:
            top2_set_match += 1
        if predicted_pair == gold_pair:
            top2_ordered_match += 1
        if primary_label == gold_pair[0]:
            primary_label_match += 1
        if secondary_label == gold_pair[1]:
            secondary_label_match += 1
        if primary_key == normalize_text(meta["gold_primary_evidence_key"]):
            primary_evidence_match += 1
        if secondary_key == normalize_text(meta["gold_secondary_evidence_key"]):
            secondary_evidence_match += 1

        if (predicted_pair != gold_pair or primary_key != normalize_text(meta["gold_primary_evidence_key"]) or secondary_key != normalize_text(meta["gold_secondary_evidence_key"])) and len(mismatches) < 5:
            mismatches.append(
                {
                    "source_example_index": meta["source_example_index"],
                    "source_run_id": meta["source_run_id"],
                    "gold_pair": gold_pair,
                    "gold_primary_evidence_key": meta["gold_primary_evidence_key"],
                    "gold_secondary_evidence_key": meta["gold_secondary_evidence_key"],
                    "predicted_pair": predicted_pair,
                    "predicted_primary_evidence_key": primary_key,
                    "predicted_secondary_evidence_key": secondary_key,
                }
            )

    total = len(metadata_rows)
    return {
        "source_examples": total,
        "distinct_label_rate": distinct_label_count / total if total else 0.0,
        "top2_set_match_rate": top2_set_match / total if total else 0.0,
        "top2_ordered_match_rate": top2_ordered_match / total if total else 0.0,
        "primary_label_accuracy": primary_label_match / total if total else 0.0,
        "secondary_label_accuracy": secondary_label_match / total if total else 0.0,
        "primary_evidence_key_accuracy": primary_evidence_match / total if total else 0.0,
        "secondary_evidence_key_accuracy": secondary_evidence_match / total if total else 0.0,
        "invalid_row_rate": invalid_rows / total if total else 0.0,
        "predicted_label_histogram": dict(sorted(label_histogram.items())),
        "per_label_role_counts": {label: counts for label, counts in sorted(per_label.items())},
        "example_mismatches": mismatches,
    }


def main(path_str: str, metadata_path_str: str) -> None:
    path = Path(path_str)
    metadata_path = Path(metadata_path_str)
    payload = json.loads(path.read_text())
    rows = payload.get("full_eval") or payload.get("sample_eval")
    if not rows:
        raise ValueError("Run summary does not contain full_eval or sample_eval")
    metadata_rows = json.loads(metadata_path.read_text())

    report = {
        "run_id": payload.get("run_id"),
        "dataset_name": payload.get("dataset_name"),
        "model_name": payload.get("model_name"),
        "task_config": {"expected_fields": EXPECTED_FIELDS},
        "base_row_metrics": score_rows(rows, "base_response"),
        "tuned_row_metrics": score_rows(rows, "tuned_response"),
        "base_forced_top2_metrics": forced_top2_metrics(rows, metadata_rows, "base_response"),
        "tuned_forced_top2_metrics": forced_top2_metrics(rows, metadata_rows, "tuned_response"),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python3 scripts/evaluate_failure_mode_forced_top2_run.py <run_summary.json> <eval_metadata.json>"
        )
    main(sys.argv[1], sys.argv[2])
