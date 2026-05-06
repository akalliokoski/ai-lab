from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def binary_metrics(y_true: list[int], y_pred: list[int]) -> dict[str, float | int]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    sensitivity = tp / (tp + fn) if (tp + fn) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "balanced_accuracy": (sensitivity + specificity) / 2,
    }


def load_subject_rows(report_path: Path, model_name: str) -> dict[str, Any]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    model = report["models"][model_name]
    subject_rows = []
    for row in model["subject_aggregation"]["subjects"]:
        subject_rows.append(
            {
                "subject_id": row["subject_id"],
                "true_label": row["true_label"],
                "mean_score": float(row["mean_score"]),
                "windows": int(row["windows"]),
                "positive_window_fraction": float(row["positive_window_fraction"]),
                "predicted_positive_windows": int(row["predicted_positive_windows"]),
            }
        )
    return {
        "report_path": str(report_path.resolve()),
        "features_csv": report["features_csv"],
        "model_name": model_name,
        "subjects": subject_rows,
        "default_subject_summary": model["subject_aggregation"]["summary"],
        "window_level_summary": model["summary"],
    }


def build_threshold_grid(scores: list[float]) -> list[float]:
    unique_scores = sorted(set(float(score) for score in scores))
    thresholds = {0.0, 0.5, 1.0}
    for score in unique_scores:
        thresholds.add(score)
        thresholds.add(max(0.0, score - 1e-6))
        thresholds.add(min(1.0, score + 1e-6))
    for left, right in zip(unique_scores, unique_scores[1:]):
        thresholds.add((left + right) / 2)
    return sorted(thresholds)


def summarize_thresholds(subject_rows: list[dict[str, Any]]) -> dict[str, Any]:
    y_true = [1 if row["true_label"] == "bruxism" else 0 for row in subject_rows]
    scores = [float(row["mean_score"]) for row in subject_rows]
    thresholds = build_threshold_grid(scores)
    threshold_rows = []
    for threshold in thresholds:
        y_pred = [1 if score >= threshold else 0 for score in scores]
        metrics = binary_metrics(y_true, y_pred)
        predicted_positive_subjects = [
            row["subject_id"] for row, pred in zip(subject_rows, y_pred) if pred == 1
        ]
        threshold_rows.append(
            {
                "threshold": threshold,
                **metrics,
                "predicted_positive_subjects": predicted_positive_subjects,
            }
        )

    best_balanced_accuracy = max(row["balanced_accuracy"] for row in threshold_rows)
    best_rows = [
        row for row in threshold_rows if abs(row["balanced_accuracy"] - best_balanced_accuracy) < 1e-12
    ]
    no_false_positive_rows = [row for row in threshold_rows if row["fp"] == 0]
    best_no_fp = max(no_false_positive_rows, key=lambda row: (row["sensitivity"], row["balanced_accuracy"], -row["threshold"]))
    any_positive_sensitivity = [row for row in threshold_rows if row["sensitivity"] > 0]
    best_with_positive_sensitivity = (
        max(any_positive_sensitivity, key=lambda row: (row["balanced_accuracy"], row["specificity"], -row["threshold"]))
        if any_positive_sensitivity
        else None
    )
    return {
        "subject_scores_sorted": sorted(subject_rows, key=lambda row: row["mean_score"], reverse=True),
        "threshold_grid": threshold_rows,
        "best_balanced_accuracy": best_balanced_accuracy,
        "best_balanced_accuracy_rows": best_rows,
        "best_zero_false_positive_row": best_no_fp,
        "best_positive_sensitivity_row": best_with_positive_sensitivity,
    }


def build_comparison(primary: dict[str, Any], anchor: dict[str, Any]) -> dict[str, Any]:
    return {
        "primary": primary,
        "anchor": anchor,
        "subject_score_margin": {
            "primary_best_bruxism_minus_highest_control": max(
                row["mean_score"] for row in primary["subjects"] if row["true_label"] == "bruxism"
            )
            - max(row["mean_score"] for row in primary["subjects"] if row["true_label"] == "control"),
            "anchor_best_bruxism_minus_highest_control": max(
                row["mean_score"] for row in anchor["subjects"] if row["true_label"] == "bruxism"
            )
            - max(row["mean_score"] for row in anchor["subjects"] if row["true_label"] == "control"),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit subject-level threshold behavior for saved LOSO baseline reports.")
    parser.add_argument("--report", required=True, help="Primary LOSO JSON report to audit")
    parser.add_argument("--model", default="logreg", help="Model name inside the LOSO report")
    parser.add_argument("--anchor-report", help="Optional comparison LOSO JSON report")
    parser.add_argument("--anchor-model", default="logreg", help="Model name inside the anchor report")
    parser.add_argument("--out", required=True, help="Output JSON path")
    args = parser.parse_args()

    primary = load_subject_rows(Path(args.report), args.model)
    primary["threshold_audit"] = summarize_thresholds(primary["subjects"])

    result: dict[str, Any] = {"primary": primary}
    if args.anchor_report:
        anchor = load_subject_rows(Path(args.anchor_report), args.anchor_model)
        anchor["threshold_audit"] = summarize_thresholds(anchor["subjects"])
        result["comparison"] = build_comparison(primary, anchor)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
