from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from audit_percentile_band_channel_gap import select_feature_columns
from run_pass36_record_relative_shape_composition_audit import (
    best_brux_minus_highest_control,
    load_subjects,
    summarize_counts,
)
from run_pass41_event_conditioned_feature_block_audit import (
    BASE_EXCLUDE_REGEXES,
    SUBJECT_IDS,
    build_subject_rows,
)

PASS_NUMBER = 45
EXPERIMENT = "repaired_a3_same_table_shape_block_ablation_on_frozen_pass44_anchor"
PRIMARY_OBJECTIVE = (
    "test whether removing only the compact shape family rescues brux2 on the repaired A3-only "
    "same-table scaffold while preserving the fixed pass44 event trio and LOSO contract"
)
SHAPE_FEATURES = [
    "skewness",
    "kurtosis",
    "hjorth_mobility",
    "hjorth_complexity",
]
PROJECT_PYTHON = Path(__file__).resolve().parents[3] / ".venv/bin/python"


def python_executable() -> Path:
    return PROJECT_PYTHON if PROJECT_PYTHON.exists() else Path(sys.executable)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def run_train_baseline(*, features_csv: Path, out_json: Path, exclude_patterns: list[str]) -> dict[str, Any]:
    cmd = [
        str(python_executable()),
        str(Path(__file__).with_name("train_baseline.py")),
        "--features-csv",
        str(features_csv),
        "--cv",
        "loso",
        "--out",
        str(out_json),
    ]
    for pattern in exclude_patterns:
        cmd.extend(["--exclude-features-regex", pattern])
    run(cmd)
    return json.loads(out_json.read_text(encoding="utf-8"))


def run_paired_audit(
    *,
    primary_report: Path,
    primary_name: str,
    anchor_report: Path,
    anchor_name: str,
    out_json: Path,
    out_md: Path,
) -> dict[str, Any]:
    cmd = [
        str(python_executable()),
        str(Path(__file__).with_name("compare_subject_score_surfaces.py")),
        "--primary-report",
        str(primary_report),
        "--primary-name",
        primary_name,
        "--anchor-report",
        str(anchor_report),
        "--anchor-name",
        anchor_name,
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    run(cmd)
    return json.loads(out_json.read_text(encoding="utf-8"))


def build_exclude_patterns() -> list[str]:
    excludes = list(BASE_EXCLUDE_REGEXES)
    excludes.extend(f"^{feature}$" for feature in SHAPE_FEATURES)
    return excludes


def get_subject_scores(subjects: dict[str, dict[str, Any]]) -> dict[str, float]:
    return {subject_id: float(subjects[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS}


def build_subject_comparison_rows(
    *,
    pass42_subjects: dict[str, Any],
    pass44_subjects: dict[str, Any],
    pass45_subjects: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for subject_id in SUBJECT_IDS:
        pass42_row = pass42_subjects[subject_id]
        pass44_row = pass44_subjects[subject_id]
        pass45_row = pass45_subjects[subject_id]
        rows.append(
            {
                "subject_id": subject_id,
                "true_label": pass45_row["true_label"],
                "pass42_score": float(pass42_row["mean_score"]),
                "pass44_score": float(pass44_row["mean_score"]),
                "pass45_score": float(pass45_row["mean_score"]),
                "delta_pass45_vs_pass44": float(pass45_row["mean_score"] - pass44_row["mean_score"]),
                "delta_pass45_vs_pass42": float(pass45_row["mean_score"] - pass42_row["mean_score"]),
                "pass42_predicted_label": pass42_row["predicted_label"],
                "pass44_predicted_label": pass44_row["predicted_label"],
                "pass45_predicted_label": pass45_row["predicted_label"],
            }
        )
    return rows


def render_subject_rows(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{row['subject_id']}` ({row['true_label']}): pass42 `{row['pass42_score']:.3f}` -> pass44 `{row['pass44_score']:.3f}` -> pass45 `{row['pass45_score']:.3f}` | "
        f"delta pass45 vs pass44 `{row['delta_pass45_vs_pass44']:+.3f}` | "
        f"delta pass45 vs pass42 `{row['delta_pass45_vs_pass42']:+.3f}` | "
        f"labels pass42 `{row['pass42_predicted_label']}` -> pass44 `{row['pass44_predicted_label']}` -> pass45 `{row['pass45_predicted_label']}`"
        for row in rows
    )


def subject_prediction_flips(rows: list[dict[str, Any]], *, from_key: str, to_key: str) -> list[str]:
    flips = []
    for row in rows:
        before = row[from_key]
        after = row[to_key]
        if before != after:
            flips.append(f"{row['subject_id']}: {before} -> {after}")
    return flips


def shape_feature_presence(feature_columns: list[str]) -> dict[str, bool]:
    return {feature: feature in feature_columns for feature in SHAPE_FEATURES}


def render_markdown(report: dict[str, Any]) -> str:
    pass42_summary = report["anchors"]["pass42_repaired_a1"]["subject_summary"]
    pass44_summary = report["anchors"]["pass44_repaired_a3"]["subject_summary"]
    pass45_summary = report["pass45_repaired_a3_no_shape"]["subject_summary"]
    return f"""# Pass 45 — repaired A3 same-table shape-block ablation

Date: 2026-05-05
Status: bounded same-table ablation completed. This pass reuses the frozen pass44 repaired `A3-only` table, keeps the five-subject benchmark, `EMG1-EMG2`, the fixed 3-feature event trio, train-time exclusions, threshold `0.5`, and `logreg` LOSO contract unchanged, and drops only the compact shape family at train time.

## Why this is the smallest valid test
- no selector rerun, no new row generation, no family change, no channel change, no model-family change, and no event-subset change
- input table reused directly: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_record_relative_shape_eventsubset.csv`
- only additional train-time removals are the four compact shape features: `{', '.join(SHAPE_FEATURES)}`
- this isolates whether existing secondary shape support on the repaired pass44 table is suppressing `brux2` without reopening the stronger amplitude / dispersion carrier or the validated event trio

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass45_repaired_a3_shape_block_ablation.py`
- Reused repaired pass44 table: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_record_relative_shape_eventsubset.csv`
- Pass45 LOSO report: `projects/bruxism-cap/reports/loso-cv-pass45-emg-a3-pct10-90-record-relative-eventsubset-no-shape.json`
- Pass45 summary JSON: `projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.json`
- Pass45 summary memo: `projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.md`
- Paired audit JSON: `projects/bruxism-cap/reports/pass45-vs-pass44-paired-subject-surface-audit.json`
- Paired audit memo: `projects/bruxism-cap/reports/pass45-vs-pass44-paired-subject-surface-audit.md`

## Scaffold parity checks
- pass42 repaired A1 counts by subject: `{report['anchors']['pass42_repaired_a1']['counts_by_subject']}` | total rows `{report['anchors']['pass42_repaired_a1']['row_count']}`
- pass44 repaired A3 counts by subject: `{report['anchors']['pass44_repaired_a3']['counts_by_subject']}` | total rows `{report['anchors']['pass44_repaired_a3']['row_count']}`
- pass45 repaired A3 no-shape counts by subject: `{report['pass45_repaired_a3_no_shape']['counts_by_subject']}` | total rows `{report['pass45_repaired_a3_no_shape']['row_count']}`
- unchanged base exclusions: `{BASE_EXCLUDE_REGEXES}`
- added shape-drop exclusions: `{SHAPE_FEATURES}`
- shape features still present in the reused table before exclusion: `{report['pass45_repaired_a3_no_shape']['shape_features_present_in_table']}`

## Subject-level comparison against pass42 and pass44
- balanced accuracy: pass42 `{pass42_summary['balanced_accuracy']:.3f}` | pass44 `{pass44_summary['balanced_accuracy']:.3f}` | pass45 `{pass45_summary['balanced_accuracy']:.3f}`
- sensitivity: pass42 `{pass42_summary['sensitivity']:.3f}` | pass44 `{pass44_summary['sensitivity']:.3f}` | pass45 `{pass45_summary['sensitivity']:.3f}`
- specificity: pass42 `{pass42_summary['specificity']:.3f}` | pass44 `{pass44_summary['specificity']:.3f}` | pass45 `{pass45_summary['specificity']:.3f}`
- best-bruxism-minus-highest-control margin: pass42 `{report['derived']['pass42_best_brux_minus_highest_control']:+.3f}` | pass44 `{report['derived']['pass44_best_brux_minus_highest_control']:+.3f}` | pass45 `{report['derived']['pass45_best_brux_minus_highest_control']:+.3f}`
- pass45 highest control: `{report['derived']['pass45_highest_control_subject']}` at `{report['derived']['pass45_highest_control_score']:.3f}`
- pass45 exact sensitivity CI: `{pass45_summary['sensitivity_ci_95_exact']}`
- pass45 exact specificity CI: `{pass45_summary['specificity_ci_95_exact']}`
- pass45 subject Brier: `{pass45_summary['subject_probability_brier']:.3f}`

Subject score rows:
{render_subject_rows(report['derived']['subject_score_rows'])}

## Subject prediction flips
- pass45 vs pass44: `{report['derived']['pass45_vs_pass44_prediction_flips']}`
- pass45 vs pass42: `{report['derived']['pass45_vs_pass42_prediction_flips']}`

## Verdict
- `brux2` delta vs pass44: `{report['derived']['brux2_delta_pass45_vs_pass44']:+.3f}`
- `brux1` delta vs pass44: `{report['derived']['brux1_delta_pass45_vs_pass44']:+.3f}`
- no control crossed threshold on pass45: `{report['derived']['no_control_crossed_threshold']}`
- smallest-test verdict: {report['derived']['verdict']}

## Safest next step
{report['derived']['safest_next_step']}
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    reports_dir = root / "reports"
    data_dir = root / "data"

    pass44_features_path = data_dir / "window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_record_relative_shape_eventsubset.csv"
    pass45_report_path = reports_dir / "loso-cv-pass45-emg-a3-pct10-90-record-relative-eventsubset-no-shape.json"
    summary_json_path = reports_dir / "pass45-repaired-a3-shape-block-ablation.json"
    summary_md_path = reports_dir / "pass45-repaired-a3-shape-block-ablation.md"
    paired_json_path = reports_dir / "pass45-vs-pass44-paired-subject-surface-audit.json"
    paired_md_path = reports_dir / "pass45-vs-pass44-paired-subject-surface-audit.md"

    pass42_report_path = reports_dir / "loso-cv-pass42-emg-a1-pct10-90-record-relative-shape-eventblock-subset.json"
    pass44_report_path = reports_dir / "loso-cv-pass44-emg-a3-pct10-90-record-relative-shape-eventsubset.json"

    pass44_df = pd.read_csv(pass44_features_path)
    exclude_patterns = build_exclude_patterns()
    pass45_report = run_train_baseline(
        features_csv=pass44_features_path,
        out_json=pass45_report_path,
        exclude_patterns=exclude_patterns,
    )

    pass42_report = json.loads(pass42_report_path.read_text(encoding="utf-8"))
    pass44_report = json.loads(pass44_report_path.read_text(encoding="utf-8"))

    pass42_subjects = load_subjects(pass42_report)
    pass44_subjects = load_subjects(pass44_report)
    pass45_subjects = load_subjects(pass45_report)

    pass45_feature_columns, pass45_selection_excluded = select_feature_columns(pass44_df, exclude_patterns=exclude_patterns)
    pass45_subjects_audit, pass45_blocks = build_subject_rows(pass44_df, pass45_feature_columns)
    paired_audit = run_paired_audit(
        primary_report=pass45_report_path,
        primary_name="pass45-repaired-a3-no-shape",
        anchor_report=pass44_report_path,
        anchor_name="pass44-repaired-a3-event-subset",
        out_json=paired_json_path,
        out_md=paired_md_path,
    )

    pass45_highest_control_subject = max(
        ["n3", "n5", "n11"],
        key=lambda subject_id: pass45_subjects[subject_id]["mean_score"],
    )
    subject_rows = build_subject_comparison_rows(
        pass42_subjects=pass42_subjects,
        pass44_subjects=pass44_subjects,
        pass45_subjects=pass45_subjects,
    )

    brux2_delta = float(pass45_subjects["brux2"]["mean_score"] - pass44_subjects["brux2"]["mean_score"])
    brux1_delta = float(pass45_subjects["brux1"]["mean_score"] - pass44_subjects["brux1"]["mean_score"])
    no_control_crossed_threshold = all(
        pass45_subjects[subject_id]["predicted_label"] == "control" for subject_id in ["n3", "n5", "n11"]
    )

    if brux2_delta > 0 and no_control_crossed_threshold and brux1_delta > -0.05:
        verdict = "shape-family removal looks directionally useful and should be preserved as the new repaired A3 working point"
        safest_next_step = (
            "Keep the repaired pass45 no-shape table as the new A3 anchor and run the already-preserved paired subject-surface audit against pass42 before considering the backup one-feature event add-back."
        )
    else:
        verdict = "the shape-only ablation did not cleanly rescue brux2 on the repaired A3 scaffold, so the smallest primary test is now closed"
        safest_next_step = (
            "Revert to the saved backup branch: add only `evt_bursts_per_episode_mean` on top of the frozen pass42/pass44 trio while keeping the repaired scaffold, subject set, and LOSO contract fixed."
        )

    report = {
        "pass": PASS_NUMBER,
        "experiment": EXPERIMENT,
        "objective": PRIMARY_OBJECTIVE,
        "anchors": {
            "pass42_repaired_a1": {
                "report_path": str(pass42_report_path.resolve()),
                "features_csv": pass42_report["features_csv"],
                "subject_summary": pass42_report["models"]["logreg"]["subject_aggregation"]["summary"],
                "subjects": pass42_subjects,
                "subjects_scores": get_subject_scores(pass42_subjects),
                "counts_by_subject": summarize_counts(pd.read_csv(Path(pass42_report["features_csv"]))),
                "row_count": int(pass42_report["rows"]),
            },
            "pass44_repaired_a3": {
                "report_path": str(pass44_report_path.resolve()),
                "features_csv": pass44_report["features_csv"],
                "subject_summary": pass44_report["models"]["logreg"]["subject_aggregation"]["summary"],
                "subjects": pass44_subjects,
                "subjects_scores": get_subject_scores(pass44_subjects),
                "counts_by_subject": summarize_counts(pass44_df),
                "row_count": int(pass44_report["rows"]),
            },
        },
        "pass45_repaired_a3_no_shape": {
            "report_path": str(pass45_report_path.resolve()),
            "features_csv": str(pass44_features_path.resolve()),
            "subject_summary": pass45_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "subjects": pass45_subjects,
            "subjects_scores": get_subject_scores(pass45_subjects),
            "counts_by_subject": summarize_counts(pass44_df),
            "row_count": int(pass45_report["rows"]),
            "selection_excluded_columns": pass45_selection_excluded,
            "feature_columns": pass45_feature_columns,
            "shape_features_dropped": SHAPE_FEATURES,
            "shape_features_present_in_table": shape_feature_presence(list(pass44_df.columns)),
            "subjects_audit": pass45_subjects_audit,
            "blocks": pass45_blocks,
        },
        "exclude_patterns": exclude_patterns,
        "paired_audit": paired_audit,
        "paired_audit_paths": {
            "json": str(paired_json_path.resolve()),
            "md": str(paired_md_path.resolve()),
        },
        "derived": {
            "subject_score_rows": subject_rows,
            "pass42_best_brux_minus_highest_control": best_brux_minus_highest_control(pass42_subjects),
            "pass44_best_brux_minus_highest_control": best_brux_minus_highest_control(pass44_subjects),
            "pass45_best_brux_minus_highest_control": best_brux_minus_highest_control(pass45_subjects),
            "pass45_highest_control_subject": pass45_highest_control_subject,
            "pass45_highest_control_score": float(pass45_subjects[pass45_highest_control_subject]["mean_score"]),
            "brux2_delta_pass45_vs_pass44": brux2_delta,
            "brux1_delta_pass45_vs_pass44": brux1_delta,
            "pass45_vs_pass44_prediction_flips": subject_prediction_flips(
                subject_rows,
                from_key="pass44_predicted_label",
                to_key="pass45_predicted_label",
            ),
            "pass45_vs_pass42_prediction_flips": subject_prediction_flips(
                subject_rows,
                from_key="pass42_predicted_label",
                to_key="pass45_predicted_label",
            ),
            "no_control_crossed_threshold": no_control_crossed_threshold,
            "verdict": verdict,
            "safest_next_step": safest_next_step,
        },
        "summary_md_path": str(summary_md_path.resolve()),
        "summary_json_path": str(summary_json_path.resolve()),
    }

    summary_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_markdown(report), encoding="utf-8")
    print(summary_md_path)
    print(summary_json_path)
    print(pass45_report_path)
    print(paired_md_path)
    print(paired_json_path)


if __name__ == "__main__":
    main()
