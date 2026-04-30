from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_EXPECTED_FIELDS = ["contrast_group", "decision", "evidence_key"]
CONTRAST_UNIVERSE = {
    "missing-required-detail",
    "generic-explanation",
    "no-material-change",
    "hallucinated-detail",
    "overlap-contaminated-eval",
}


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


def group_metrics(rows: list[dict[str, Any]], metadata_rows: list[dict[str, Any]], response_key: str) -> dict[str, Any]:
    by_group = defaultdict(lambda: {"rows": 0, "decision_hits": 0, "evidence_hits": 0, "decision_confusion": Counter()})

    for row, meta in zip(rows, metadata_rows, strict=True):
        reference = safe_json_loads(row["reference"])
        candidate = safe_json_loads(row[response_key])
        group_name = str(meta["contrast_group"])
        bucket = by_group[group_name]
        bucket["rows"] += 1
        if reference is None or candidate is None:
            bucket["decision_confusion"]["invalid-json"] += 1
            continue
        gold_decision = normalize_text(reference.get("decision"))
        pred_decision = normalize_text(candidate.get("decision"))
        if gold_decision == pred_decision:
            bucket["decision_hits"] += 1
        if normalize_text(reference.get("evidence_key")) == normalize_text(candidate.get("evidence_key")):
            bucket["evidence_hits"] += 1
        bucket["decision_confusion"][f"{gold_decision}->{pred_decision}"] += 1

    report = {}
    for group_name, bucket in sorted(by_group.items()):
        rows_count = bucket["rows"]
        report[group_name] = {
            "rows": rows_count,
            "decision_accuracy": bucket["decision_hits"] / rows_count if rows_count else 0.0,
            "evidence_key_accuracy": bucket["evidence_hits"] / rows_count if rows_count else 0.0,
            "decision_confusion": dict(bucket["decision_confusion"].most_common()),
        }
    return report


def decision_to_score_updates(meta: dict[str, Any], parsed: dict[str, Any] | None) -> dict[str, int]:
    updates = {label: 0 for label in CONTRAST_UNIVERSE}
    if parsed is None:
        return updates
    decision = normalize_text(parsed.get("decision"))
    anchor = str(meta["anchor_label"])
    rival = str(meta["rival_label"])
    if decision == normalize_text(anchor):
        updates[anchor] += 1
    elif decision == normalize_text(rival):
        updates[rival] += 1
    elif decision == "both":
        updates[anchor] += 1
        updates[rival] += 1
    return updates


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
                "reconstructable": bool(meta["reconstructable"]),
                "predictions": [],
            },
        )
        group["predictions"].append((meta, safe_json_loads(row[response_key])))

    total_examples = len(grouped)
    reconstructable_groups = [(key, group) for key, group in grouped.items() if group["reconstructable"]]
    total_reconstructable = len(reconstructable_groups)
    exact_positive_set = 0
    top2_set_match = 0
    predicted_positive_histogram: Counter[int] = Counter()
    mismatches: list[dict[str, Any]] = []

    for (source_index, run_id), group in reconstructable_groups:
        scores = {label: 0 for label in CONTRAST_UNIVERSE}
        for meta, parsed in group["predictions"]:
            for label, delta in decision_to_score_updates(meta, parsed).items():
                scores[label] += delta
        predicted_positive = sorted([label for label, score in scores.items() if score > 0])
        gold_set = set(group["gold_pair"])
        predicted_positive_histogram[len(predicted_positive)] += 1
        if set(predicted_positive) == gold_set:
            exact_positive_set += 1

        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        predicted_top2 = {label for label, score in ranked[:2] if score > 0}
        if predicted_top2 == gold_set:
            top2_set_match += 1
        if (set(predicted_positive) != gold_set or predicted_top2 != gold_set) and len(mismatches) < 5:
            mismatches.append(
                {
                    "source_example_index": source_index,
                    "source_run_id": run_id,
                    "gold_pair": group["gold_pair"],
                    "score_map": scores,
                    "predicted_positive": predicted_positive,
                    "predicted_top2": sorted(predicted_top2),
                }
            )

    return {
        "source_examples_total": total_examples,
        "reconstructable_source_examples": total_reconstructable,
        "contrast_universe": sorted(CONTRAST_UNIVERSE),
        "exact_positive_set_match_rate": exact_positive_set / total_reconstructable if total_reconstructable else 0.0,
        "top2_set_match_rate": top2_set_match / total_reconstructable if total_reconstructable else 0.0,
        "predicted_positive_count_histogram": dict(sorted(predicted_positive_histogram.items())),
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
        "task_config": {"expected_fields": expected_fields},
        "base_row_metrics": score_rows(rows, "base_response", expected_fields),
        "tuned_row_metrics": score_rows(rows, "tuned_response", expected_fields),
        "base_group_metrics": group_metrics(rows, metadata_rows, "base_response"),
        "tuned_group_metrics": group_metrics(rows, metadata_rows, "tuned_response"),
        "base_reconstruction": reconstruct(rows, metadata_rows, "base_response"),
        "tuned_reconstruction": reconstruct(rows, metadata_rows, "tuned_response"),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python3 scripts/evaluate_failure_mode_contrast_run.py <run_summary.json> <eval_metadata.json>"
        )
    main(sys.argv[1], sys.argv[2])
