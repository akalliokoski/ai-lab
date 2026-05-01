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
EXPECTED_RANKS = {"primary", "secondary", "out"}
RANK_TO_SCORE = {"primary": 2, "secondary": 1, "out": 0}


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


def valid_joint_map(parsed: dict[str, Any] | None) -> bool:
    if parsed is None:
        return False
    if set(parsed.keys()) != set(LABELS):
        return False
    values = [normalize_text(parsed.get(label)) for label in LABELS]
    if any(value not in EXPECTED_RANKS for value in values):
        return False
    return values.count("primary") == 1 and values.count("secondary") == 1 and values.count("out") == len(LABELS) - 2


def score_rows(rows: list[dict[str, Any]], response_key: str) -> dict[str, Any]:
    total = len(rows)
    valid = 0
    exact = 0
    field_hits = {label: 0 for label in LABELS}
    invalid_examples: list[dict[str, Any]] = []

    for row in rows:
        reference = safe_json_loads(row["reference"])
        candidate = safe_json_loads(row[response_key])
        if reference is None:
            raise ValueError("Reference output is not valid JSON in eval row")
        if not valid_joint_map(candidate):
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
        for label in LABELS:
            hit = normalize_text(reference.get(label)) == normalize_text(candidate.get(label))
            if hit:
                field_hits[label] += 1
            else:
                row_exact = False
        if row_exact:
            exact += 1

    return {
        "rows": total,
        "valid_json_rate": valid / total if total else 0.0,
        "exact_row_match_rate": exact / total if total else 0.0,
        "field_accuracy": {label: field_hits[label] / total if total else 0.0 for label in LABELS},
        "invalid_examples": invalid_examples[:3],
    }


def rank_metrics(rows: list[dict[str, Any]], response_key: str) -> dict[str, Any]:
    rank_confusion = Counter()
    by_label = defaultdict(lambda: {"rows": 0, "rank_hits": 0, "positive_gold": 0, "positive_pred": 0, "positive_tp": 0})

    for row in rows:
        reference = safe_json_loads(row["reference"])
        candidate = safe_json_loads(row[response_key])
        if reference is None:
            raise ValueError("Reference output is not valid JSON in eval row")
        for label in LABELS:
            gold_rank = normalize_text(reference.get(label))
            pred_rank = normalize_text(candidate.get(label)) if candidate is not None else "invalid-json"
            rank_confusion[f"{gold_rank}->{pred_rank}"] += 1
            bucket = by_label[label]
            bucket["rows"] += 1
            if gold_rank == pred_rank:
                bucket["rank_hits"] += 1
            gold_positive = gold_rank in {"primary", "secondary"}
            pred_positive = pred_rank in {"primary", "secondary"}
            if gold_positive:
                bucket["positive_gold"] += 1
            if pred_positive:
                bucket["positive_pred"] += 1
            if gold_positive and pred_positive:
                bucket["positive_tp"] += 1

    per_label = {}
    for label, bucket in sorted(by_label.items()):
        precision = bucket["positive_tp"] / bucket["positive_pred"] if bucket["positive_pred"] else 0.0
        recall = bucket["positive_tp"] / bucket["positive_gold"] if bucket["positive_gold"] else 0.0
        per_label[label] = {
            "rows": bucket["rows"],
            "rank_accuracy": bucket["rank_hits"] / bucket["rows"] if bucket["rows"] else 0.0,
            "positive_precision": precision,
            "positive_recall": recall,
        }

    return {
        "rank_confusion": dict(rank_confusion.most_common()),
        "per_label": per_label,
    }


def reconstruct(rows: list[dict[str, Any]], metadata_rows: list[dict[str, Any]], response_key: str) -> dict[str, Any]:
    if len(rows) != len(metadata_rows):
        raise ValueError("Eval metadata length does not match full_eval length")

    exact_positive_set = 0
    exact_positive_count = 0
    top2_set_match = 0
    top2_ordered_match = 0
    first_label_match = 0
    second_label_match = 0
    underselected = 0
    overselected = 0
    selected_positive_count_histogram: Counter[int] = Counter()
    mismatches: list[dict[str, Any]] = []

    for row, meta in zip(rows, metadata_rows, strict=True):
        reference = safe_json_loads(row["reference"])
        candidate = safe_json_loads(row[response_key])
        if reference is None:
            raise ValueError("Reference output is not valid JSON in eval row")

        gold_pair = list(meta["gold_pair"])
        gold_set = set(gold_pair)
        parsed = candidate if candidate is not None else {}
        score_map = {label: RANK_TO_SCORE.get(normalize_text(parsed.get(label)), 0) for label in LABELS}
        selected_positive = {label for label, score in score_map.items() if score > 0}
        selected_positive_count_histogram[len(selected_positive)] += 1
        if selected_positive == gold_set:
            exact_positive_set += 1
        if len(selected_positive) == len(gold_set):
            exact_positive_count += 1
        if len(selected_positive) < len(gold_set):
            underselected += 1
        if len(selected_positive) > len(gold_set):
            overselected += 1

        ranked = sorted(LABELS, key=lambda label: (-score_map[label], label))
        predicted_top2_ordered = ranked[:2]
        predicted_top2_set = set(predicted_top2_ordered)
        if predicted_top2_set == gold_set:
            top2_set_match += 1
        if predicted_top2_ordered == gold_pair:
            top2_ordered_match += 1
        if predicted_top2_ordered[0] == gold_pair[0]:
            first_label_match += 1
        if predicted_top2_ordered[1] == gold_pair[1]:
            second_label_match += 1

        if (predicted_top2_ordered != gold_pair or selected_positive != gold_set) and len(mismatches) < 5:
            mismatches.append(
                {
                    "source_example_index": meta["source_example_index"],
                    "source_run_id": meta["source_run_id"],
                    "gold_pair": gold_pair,
                    "score_map": score_map,
                    "selected_positive": sorted(selected_positive),
                    "predicted_top2_ordered": predicted_top2_ordered,
                }
            )

    total = len(metadata_rows)
    return {
        "source_examples": total,
        "exact_positive_set_match_rate": exact_positive_set / total if total else 0.0,
        "exact_positive_count_match_rate": exact_positive_count / total if total else 0.0,
        "top2_set_match_rate": top2_set_match / total if total else 0.0,
        "top2_ordered_match_rate": top2_ordered_match / total if total else 0.0,
        "first_label_accuracy": first_label_match / total if total else 0.0,
        "second_label_accuracy": second_label_match / total if total else 0.0,
        "underselected_rate": underselected / total if total else 0.0,
        "overselected_rate": overselected / total if total else 0.0,
        "selected_positive_count_histogram": dict(sorted(selected_positive_count_histogram.items())),
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
        "task_config": {"expected_fields": LABELS},
        "base_row_metrics": score_rows(rows, "base_response"),
        "tuned_row_metrics": score_rows(rows, "tuned_response"),
        "base_rank_metrics": rank_metrics(rows, "base_response"),
        "tuned_rank_metrics": rank_metrics(rows, "tuned_response"),
        "base_reconstruction": reconstruct(rows, metadata_rows, "base_response"),
        "tuned_reconstruction": reconstruct(rows, metadata_rows, "tuned_response"),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python3 scripts/evaluate_failure_mode_joint_rank_run.py <run_summary.json> <eval_metadata.json>"
        )
    main(sys.argv[1], sys.argv[2])
