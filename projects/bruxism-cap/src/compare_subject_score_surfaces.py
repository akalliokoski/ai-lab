from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_model_block(report_path: Path, model_name: str) -> dict[str, Any]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    model = report["models"][model_name]
    subject_summary = model["subject_aggregation"]["summary"]
    subjects = []
    for row in model["subject_aggregation"]["subjects"]:
        subjects.append(
            {
                "subject_id": row["subject_id"],
                "true_label": row["true_label"],
                "mean_score": float(row["mean_score"]),
                "windows": int(row["windows"]),
                "predicted_positive_windows": int(row["predicted_positive_windows"]),
                "positive_window_fraction": float(row["positive_window_fraction"]),
                "predicted_label": row["predicted_label"],
                "correct": bool(row["correct"]),
            }
        )

    return {
        "report_path": str(report_path.resolve()),
        "features_csv": report["features_csv"],
        "cv": report["cv"],
        "rows": int(report["rows"]),
        "subject_count": int(report["subject_count"]),
        "subjects": subjects,
        "model_name": model_name,
        "window_level_summary": model["summary"],
        "subject_level_summary": subject_summary,
        "feature_count": int(report.get("feature_count", 0)),
        "feature_selection": report.get("feature_selection", {}),
    }


def summarize_score_surface(block: dict[str, Any]) -> dict[str, Any]:
    subjects = block["subjects"]
    sorted_subjects = sorted(subjects, key=lambda row: row["mean_score"], reverse=True)
    bruxism_subjects = [row for row in sorted_subjects if row["true_label"] == "bruxism"]
    control_subjects = [row for row in sorted_subjects if row["true_label"] == "control"]
    best_bruxism = max(bruxism_subjects, key=lambda row: row["mean_score"])
    worst_bruxism = min(bruxism_subjects, key=lambda row: row["mean_score"])
    highest_control = max(control_subjects, key=lambda row: row["mean_score"])
    lowest_control = min(control_subjects, key=lambda row: row["mean_score"])
    return {
        "sorted_subjects": sorted_subjects,
        "best_bruxism_subject": best_bruxism,
        "worst_bruxism_subject": worst_bruxism,
        "highest_control_subject": highest_control,
        "lowest_control_subject": lowest_control,
        "best_bruxism_minus_highest_control": float(best_bruxism["mean_score"] - highest_control["mean_score"]),
        "default_positive_subjects": [row["subject_id"] for row in subjects if row["predicted_label"] == "bruxism"],
    }


def compare_blocks(primary: dict[str, Any], anchor: dict[str, Any]) -> dict[str, Any]:
    primary_by_subject = {row["subject_id"]: row for row in primary["subjects"]}
    anchor_by_subject = {row["subject_id"]: row for row in anchor["subjects"]}
    shared_subjects = sorted(set(primary_by_subject) & set(anchor_by_subject))
    paired_rows = []
    prediction_flips = []
    for subject_id in shared_subjects:
        primary_row = primary_by_subject[subject_id]
        anchor_row = anchor_by_subject[subject_id]
        paired_row = {
            "subject_id": subject_id,
            "true_label": primary_row["true_label"],
            "primary_mean_score": float(primary_row["mean_score"]),
            "anchor_mean_score": float(anchor_row["mean_score"]),
            "score_delta_primary_minus_anchor": float(primary_row["mean_score"] - anchor_row["mean_score"]),
            "primary_positive_window_fraction": float(primary_row["positive_window_fraction"]),
            "anchor_positive_window_fraction": float(anchor_row["positive_window_fraction"]),
            "primary_predicted_label": primary_row["predicted_label"],
            "anchor_predicted_label": anchor_row["predicted_label"],
        }
        paired_rows.append(paired_row)
        if primary_row["predicted_label"] != anchor_row["predicted_label"]:
            prediction_flips.append(
                {
                    "subject_id": subject_id,
                    "true_label": primary_row["true_label"],
                    "anchor_predicted_label": anchor_row["predicted_label"],
                    "primary_predicted_label": primary_row["predicted_label"],
                }
            )

    label_groups: dict[str, list[dict[str, Any]]] = {"bruxism": [], "control": []}
    for row in paired_rows:
        label_groups[row["true_label"]].append(row)

    primary_surface = summarize_score_surface(primary)
    anchor_surface = summarize_score_surface(anchor)
    return {
        "primary_surface": primary_surface,
        "anchor_surface": anchor_surface,
        "paired_subject_rows": paired_rows,
        "prediction_flips": prediction_flips,
        "label_delta_summary": {
            label: {
                "mean_primary_score": float(sum(row["primary_mean_score"] for row in rows) / len(rows)),
                "mean_anchor_score": float(sum(row["anchor_mean_score"] for row in rows) / len(rows)),
                "mean_score_delta_primary_minus_anchor": float(
                    sum(row["score_delta_primary_minus_anchor"] for row in rows) / len(rows)
                ),
            }
            for label, rows in label_groups.items()
            if rows
        },
        "subject_ordering_change": {
            "primary_top_subject": primary_surface["sorted_subjects"][0]["subject_id"],
            "anchor_top_subject": anchor_surface["sorted_subjects"][0]["subject_id"],
            "primary_best_bruxism_subject": primary_surface["best_bruxism_subject"]["subject_id"],
            "anchor_best_bruxism_subject": anchor_surface["best_bruxism_subject"]["subject_id"],
        },
        "margin_change": {
            "primary_best_bruxism_minus_highest_control": primary_surface["best_bruxism_minus_highest_control"],
            "anchor_best_bruxism_minus_highest_control": anchor_surface["best_bruxism_minus_highest_control"],
            "delta_primary_minus_anchor": float(
                primary_surface["best_bruxism_minus_highest_control"]
                - anchor_surface["best_bruxism_minus_highest_control"]
            ),
        },
        "copied_through_subject_summary": {
            "primary": primary["subject_level_summary"],
            "anchor": anchor["subject_level_summary"],
        },
    }


def render_markdown(primary_name: str, primary: dict[str, Any], anchor_name: str, anchor: dict[str, Any], comparison: dict[str, Any]) -> str:
    primary_surface = comparison["primary_surface"]
    anchor_surface = comparison["anchor_surface"]
    paired_rows = comparison["paired_subject_rows"]
    margin = comparison["margin_change"]
    subject_summaries = comparison["copied_through_subject_summary"]

    lines = [
        f"# Subject-score comparison — {primary_name} vs {anchor_name}",
        "",
        "## Compared reports",
        f"- Primary: `{primary['report_path']}` (`{primary['model_name']}`)",
        f"- Anchor: `{anchor['report_path']}` (`{anchor['model_name']}`)",
        "",
        "## Shared subject score table",
        "| Subject | Label | Primary mean score | Anchor mean score | Delta (primary-anchor) | Primary positive-window fraction | Anchor positive-window fraction | Primary label | Anchor label |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in paired_rows:
        lines.append(
            f"| {row['subject_id']} | {row['true_label']} | {row['primary_mean_score']:.3f} | {row['anchor_mean_score']:.3f} | {row['score_delta_primary_minus_anchor']:+.3f} | {row['primary_positive_window_fraction']:.3f} | {row['anchor_positive_window_fraction']:.3f} | {row['primary_predicted_label']} | {row['anchor_predicted_label']} |"
        )

    lines.extend(
        [
            "",
            "## Score-surface summary",
            f"- Primary best bruxism subject: `{primary_surface['best_bruxism_subject']['subject_id']}` at `{primary_surface['best_bruxism_subject']['mean_score']:.3f}`.",
            f"- Primary highest control: `{primary_surface['highest_control_subject']['subject_id']}` at `{primary_surface['highest_control_subject']['mean_score']:.3f}`.",
            f"- Primary best-bruxism-minus-highest-control margin: `{primary_surface['best_bruxism_minus_highest_control']:+.3f}`.",
            f"- Anchor best bruxism subject: `{anchor_surface['best_bruxism_subject']['subject_id']}` at `{anchor_surface['best_bruxism_subject']['mean_score']:.3f}`.",
            f"- Anchor highest control: `{anchor_surface['highest_control_subject']['subject_id']}` at `{anchor_surface['highest_control_subject']['mean_score']:.3f}`.",
            f"- Anchor best-bruxism-minus-highest-control margin: `{anchor_surface['best_bruxism_minus_highest_control']:+.3f}`.",
            f"- Margin delta (primary-anchor): `{margin['delta_primary_minus_anchor']:+.3f}`.",
            "",
            "## Subject prediction flips",
            f"- `{comparison['prediction_flips']}`",
            "",
            "## Copied-through subject-level summaries",
            f"- Primary balanced accuracy `{subject_summaries['primary']['balanced_accuracy']:.3f}` | sensitivity `{subject_summaries['primary']['sensitivity']:.3f}` | specificity `{subject_summaries['primary']['specificity']:.3f}` | exact sensitivity CI `{subject_summaries['primary'].get('sensitivity_ci_95_exact')}` | exact specificity CI `{subject_summaries['primary'].get('specificity_ci_95_exact')}` | Brier `{subject_summaries['primary'].get('subject_probability_brier')}`.",
            f"- Anchor balanced accuracy `{subject_summaries['anchor']['balanced_accuracy']:.3f}` | sensitivity `{subject_summaries['anchor']['sensitivity']:.3f}` | specificity `{subject_summaries['anchor']['specificity']:.3f}` | exact sensitivity CI `{subject_summaries['anchor'].get('sensitivity_ci_95_exact')}` | exact specificity CI `{subject_summaries['anchor'].get('specificity_ci_95_exact')}` | Brier `{subject_summaries['anchor'].get('subject_probability_brier')}`.",
            "",
            "## Label-level mean deltas",
            f"- `{comparison['label_delta_summary']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare subject-score surfaces between two saved LOSO reports.")
    parser.add_argument("--primary-report", required=True)
    parser.add_argument("--primary-model", default="logreg")
    parser.add_argument("--primary-name", required=True)
    parser.add_argument("--anchor-report", required=True)
    parser.add_argument("--anchor-model", default="logreg")
    parser.add_argument("--anchor-name", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md")
    args = parser.parse_args()

    primary = load_model_block(Path(args.primary_report), args.primary_model)
    anchor = load_model_block(Path(args.anchor_report), args.anchor_model)
    comparison = compare_blocks(primary, anchor)
    result = {
        "primary_name": args.primary_name,
        "anchor_name": args.anchor_name,
        "primary": primary,
        "anchor": anchor,
        "comparison": comparison,
    }

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if args.out_md:
        out_md = Path(args.out_md)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(
            render_markdown(args.primary_name, primary, args.anchor_name, anchor, comparison),
            encoding="utf-8",
        )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
