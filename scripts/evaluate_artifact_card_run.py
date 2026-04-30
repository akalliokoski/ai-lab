from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_EXPECTED_FIELDS = [
    "run_id",
    "dataset_name",
    "model_name",
    "verdict",
    "primary_failure_modes",
    "key_evidence",
    "next_action",
]
DEFAULT_LIST_FIELDS = ["primary_failure_modes", "key_evidence"]


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().lower().split())


def normalize_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted(normalize_text(item) for item in value)


def safe_json_loads(text: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def field_match(reference: dict[str, Any], candidate: dict[str, Any], field: str, list_fields: set[str]) -> bool:
    if field in list_fields:
        return normalize_list(reference.get(field)) == normalize_list(candidate.get(field))
    return normalize_text(reference.get(field)) == normalize_text(candidate.get(field))


def score_rows(
    rows: list[dict[str, Any]],
    response_key: str,
    expected_fields: list[str],
    list_fields: list[str],
) -> dict[str, Any]:
    total = len(rows)
    valid = 0
    exact = 0
    field_hits = {field: 0 for field in expected_fields}
    invalid_examples: list[dict[str, Any]] = []
    list_field_set = set(list_fields)

    for row in rows:
        reference = safe_json_loads(row["reference"])
        candidate = safe_json_loads(row[response_key])
        if reference is None:
            raise ValueError("Reference output is not valid JSON in eval row")
        if candidate is None:
            invalid_examples.append(
                {
                    "instruction": row["instruction"],
                    "response_key": response_key,
                    "response": row[response_key],
                }
            )
            continue
        valid += 1
        row_exact = True
        for field in expected_fields:
            hit = field_match(reference, candidate, field, list_field_set)
            if hit:
                field_hits[field] += 1
            else:
                row_exact = False
        if row_exact:
            exact += 1

    return {
        "rows": total,
        "valid_json_rate": valid / total if total else 0.0,
        "exact_card_match_rate": exact / total if total else 0.0,
        "field_accuracy": {field: field_hits[field] / total if total else 0.0 for field in expected_fields},
        "invalid_examples": invalid_examples[:3],
    }


def main(path_str: str) -> None:
    path = Path(path_str)
    payload = json.loads(path.read_text())
    rows = payload.get("full_eval") or payload.get("sample_eval")
    if not rows:
        raise ValueError("Run summary does not contain full_eval or sample_eval")

    task_config = payload.get("task_config") or {}
    expected_fields_raw = task_config.get("expected_fields")
    list_fields_raw = task_config.get("list_fields")
    expected_fields = list(DEFAULT_EXPECTED_FIELDS if expected_fields_raw is None else expected_fields_raw)
    list_fields = list(DEFAULT_LIST_FIELDS if list_fields_raw is None else list_fields_raw)

    base_metrics = score_rows(rows, "base_response", expected_fields, list_fields)
    tuned_metrics = score_rows(rows, "tuned_response", expected_fields, list_fields)

    report = {
        "run_id": payload.get("run_id"),
        "dataset_name": payload.get("dataset_name"),
        "model_name": payload.get("model_name"),
        "task_config": {
            "expected_fields": expected_fields,
            "list_fields": list_fields,
        },
        "base_metrics": base_metrics,
        "tuned_metrics": tuned_metrics,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 scripts/evaluate_artifact_card_run.py <run_summary.json>")
    main(sys.argv[1])
