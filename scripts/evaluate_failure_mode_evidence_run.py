from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_EXPECTED_FIELDS = ["candidate_label", "supported", "evidence_key"]
DEFAULT_LIST_FIELDS: list[str] = []


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


def field_match(reference: dict[str, Any], candidate: dict[str, Any], field: str) -> bool:
    return normalize_text(reference.get(field)) == normalize_text(candidate.get(field))


def support_to_bool(value: Any) -> bool:
    normalized = normalize_text(value)
    return normalized in {"yes", "true", "1"}


def score_rows(rows: list[dict[str, Any]], response_key: str, expected_fields: list[str]) -> dict[str, Any]:
    total = len(rows)
    valid = 0
    exact = 0
    field_hits = {field: 0 for field in expected_fields}
    invalid_examples: list[dict[str, Any]] = []

    for row in rows:
        reference = safe_json_loads(row["reference"])
        candidate = safe_json_loads(row[response_key])
        if reference is None:
            raise ValueError("Reference output is not valid JSON in eval row")
        if candidate is None:
            invalid_examples.append({
                "instruction": row["instruction"],
                "response_key": response_key,
                "response": row[response_key],
            })
            continue
        valid += 1
        row_exact = True
        for field in expected_fields:
            hit = field_match(reference, candidate, field)
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
        "field_accuracy": {field: field_hits[field] / total if total else 0.0 for field in expected_fields},
        "invalid_examples": invalid_examples[:3],
    }


def support_metrics(rows: list[dict[str, Any]], response_key: str) -> dict[str, Any]:
    by_label = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "tn": 0})
    evidence_key_hits_on_positive = 0
    positive_rows = 0

    for row in rows:
        reference = safe_json_loads(row["reference"])
        candidate = safe_json_loads(row[response_key])
        if reference is None or candidate is None:
            continue
        label = normalize_text(reference.get("candidate_label"))
        gold = support_to_bool(reference.get("supported"))
        pred = support_to_bool(candidate.get("supported"))
        bucket = by_label[label]
        if gold and pred:
            bucket["tp"] += 1
        elif (not gold) and pred:
            bucket["fp"] += 1
        elif gold and (not pred):
            bucket["fn"] += 1
        else:
            bucket["tn"] += 1

        if gold:
            positive_rows += 1
            if normalize_text(reference.get("evidence_key")) == normalize_text(candidate.get("evidence_key")):
                evidence_key_hits_on_positive += 1

    per_label = {}
    for label, counts in sorted(by_label.items()):
        tp = counts["tp"]
        fp = counts["fp"]
        fn = counts["fn"]
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        per_label[label] = {
            **counts,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    return {
        "positive_evidence_key_accuracy": evidence_key_hits_on_positive / positive_rows if positive_rows else 0.0,
        "per_label": per_label,
    }


def reconstruct(rows: list[dict[str, Any]], metadata_rows: list[dict[str, Any]], response_key: str) -> dict[str, Any]:
    if len(rows) != len(metadata_rows):
        raise ValueError("Eval metadata length does not match full_eval length")

    grouped: dict[tuple[int, str], dict[str, Any]] = {}
    for row, meta in zip(rows, metadata_rows, strict=True):
        key = (int(meta["source_example_index"]), str(meta["source_run_id"]))
        group = grouped.setdefault(
            key,
            {
                "gold_pair": list(meta["gold_pair"]),
                "predictions": {},
            },
        )
        group["predictions"][str(meta["candidate_label"])] = safe_json_loads(row[response_key])

    exact_positive_set = 0
    exact_positive_count = 0
    top2_set_match = 0
    overpredict = 0
    underpredict = 0
    positive_count_histogram: Counter[int] = Counter()
    mismatches: list[dict[str, Any]] = []

    for (source_index, run_id), group in grouped.items():
        gold_pair = list(group["gold_pair"])
        gold_set = set(gold_pair)
        predictions = group["predictions"]
        predicted_positive = {
            label
            for label, parsed in predictions.items()
            if parsed is not None and support_to_bool(parsed.get("supported"))
        }
        positive_count_histogram[len(predicted_positive)] += 1
        if predicted_positive == gold_set:
            exact_positive_set += 1
        if len(predicted_positive) == len(gold_set):
            exact_positive_count += 1
        if len(predicted_positive) > len(gold_set):
            overpredict += 1
        if len(predicted_positive) < len(gold_set):
            underpredict += 1

        ranked = sorted(
            predictions.items(),
            key=lambda item: (
                1 if item[1] is not None and support_to_bool(item[1].get("supported")) else 0,
                1 if item[1] is not None and normalize_text(item[1].get("evidence_key")) != "not-supported" else 0,
                normalize_text(item[1].get("evidence_key")) if item[1] is not None else "",
                item[0],
            ),
            reverse=True,
        )
        predicted_top2 = {label for label, _ in ranked[:2]}
        if predicted_top2 == gold_set:
            top2_set_match += 1
        if predicted_positive != gold_set and len(mismatches) < 5:
            mismatches.append(
                {
                    "source_example_index": source_index,
                    "source_run_id": run_id,
                    "gold_pair": gold_pair,
                    "predicted_positive": sorted(predicted_positive),
                    "predicted_top2": sorted(predicted_top2),
                }
            )

    total = len(grouped)
    return {
        "source_examples": total,
        "exact_positive_set_match_rate": exact_positive_set / total if total else 0.0,
        "exact_positive_count_match_rate": exact_positive_count / total if total else 0.0,
        "top2_set_match_rate": top2_set_match / total if total else 0.0,
        "overpredict_rate": overpredict / total if total else 0.0,
        "underpredict_rate": underpredict / total if total else 0.0,
        "positive_count_histogram": dict(sorted(positive_count_histogram.items())),
        "example_mismatches": mismatches,
    }


def main(path_str: str, metadata_path_str: str) -> None:
    path = Path(path_str)
    metadata_path = Path(metadata_path_str)
    payload = json.loads(path.read_text())
    rows = payload.get("full_eval") or payload.get("sample_eval")
    if not rows:
        raise ValueError("Run summary does not contain full_eval or sample_eval")

    task_config = payload.get("task_config") or {}
    expected_fields_raw = task_config.get("expected_fields")
    expected_fields = list(DEFAULT_EXPECTED_FIELDS if expected_fields_raw is None else expected_fields_raw)
    metadata_rows = json.loads(metadata_path.read_text())

    report = {
        "run_id": payload.get("run_id"),
        "dataset_name": payload.get("dataset_name"),
        "model_name": payload.get("model_name"),
        "task_config": {
            "expected_fields": expected_fields,
        },
        "base_row_metrics": score_rows(rows, "base_response", expected_fields),
        "tuned_row_metrics": score_rows(rows, "tuned_response", expected_fields),
        "base_support_metrics": support_metrics(rows, "base_response"),
        "tuned_support_metrics": support_metrics(rows, "tuned_response"),
        "base_reconstruction": reconstruct(rows, metadata_rows, "base_response"),
        "tuned_reconstruction": reconstruct(rows, metadata_rows, "tuned_response"),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python3 scripts/evaluate_failure_mode_evidence_run.py <run_summary.json> <eval_metadata.json>"
        )
    main(sys.argv[1], sys.argv[2])
