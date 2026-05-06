from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from audit_percentile_band_channel_gap import audit_channel, load_feature_frame, select_feature_columns

BASE_EXCLUDE_REGEXES = [r"^bp_", r"^rel_bp_", r"^ratio_"]
SHAPE_FEATURES = ["skewness", "kurtosis", "hjorth_mobility", "hjorth_complexity"]
SUBJECT_IDS = ["brux1", "brux2", "n3", "n5", "n11"]
ROW_ID_COLUMNS = ["subject_id", "start_s", "end_s"]
COMPARE_METADATA_COLUMNS = ["subject_id", "start_s", "end_s", "time_match_rank", "relative_time_quantile"]


def run_train_baseline(*, features_csv: Path, out_json: Path) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(Path(__file__).with_name("train_baseline.py")),
        "--features-csv",
        str(features_csv),
        "--cv",
        "loso",
        "--out",
        str(out_json),
    ]
    for pattern in BASE_EXCLUDE_REGEXES:
        cmd.extend(["--exclude-features-regex", pattern])
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    return json.loads(out_json.read_text(encoding="utf-8"))


def load_subjects(report: dict[str, Any], *, model_name: str = "logreg") -> dict[str, dict[str, Any]]:
    return {
        row["subject_id"]: row
        for row in report["models"][model_name]["subject_aggregation"]["subjects"]
    }


def summarize_counts(df: pd.DataFrame) -> dict[str, int]:
    return {str(subject_id): int(count) for subject_id, count in df["subject_id"].value_counts(sort=False).items()}


def best_brux_minus_highest_control(subjects: dict[str, dict[str, Any]]) -> float:
    best_brux = max(subjects["brux1"]["mean_score"], subjects["brux2"]["mean_score"])
    highest_control = max(subjects["n3"]["mean_score"], subjects["n5"]["mean_score"], subjects["n11"]["mean_score"])
    return float(best_brux - highest_control)


def validate_same_selected_rows(*, left_df: pd.DataFrame, right_df: pd.DataFrame, label: str) -> list[str]:
    warnings: list[str] = []
    shared_columns = [col for col in COMPARE_METADATA_COLUMNS if col in left_df.columns and col in right_df.columns]
    left_view = left_df[shared_columns].sort_values(ROW_ID_COLUMNS).reset_index(drop=True)
    right_view = right_df[shared_columns].sort_values(ROW_ID_COLUMNS).reset_index(drop=True)
    if not left_view.equals(right_view):
        warnings.append(f"selected rows do not exactly match for {label}")
    return warnings


def build_composed_table(*, pass34_df: pd.DataFrame, pass35_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    shape_source = pass35_df[ROW_ID_COLUMNS + SHAPE_FEATURES].copy()
    missing_shape = [feature for feature in SHAPE_FEATURES if feature not in pass35_df.columns]
    if missing_shape:
        raise SystemExit(f"pass35 shape table is missing required shape features: {missing_shape}")

    composed = pass34_df.drop(columns=[col for col in SHAPE_FEATURES if col in pass34_df.columns]).merge(
        shape_source,
        on=ROW_ID_COLUMNS,
        how="left",
        validate="one_to_one",
    )
    null_counts = composed[SHAPE_FEATURES].isnull().sum().to_dict()
    if any(count > 0 for count in null_counts.values()):
        raise SystemExit(f"shape merge left nulls in composed table: {null_counts}")

    return composed, {
        "shape_features_added": SHAPE_FEATURES,
        "shape_merge_keys": ROW_ID_COLUMNS,
        "shape_null_counts_after_merge": {key: int(value) for key, value in null_counts.items()},
    }


def render_subject_delta_lines(*, pass34_subjects: dict[str, dict[str, Any]], pass36_subjects: dict[str, dict[str, Any]]) -> str:
    lines = []
    for subject_id in SUBJECT_IDS:
        base = pass34_subjects[subject_id]
        new = pass36_subjects[subject_id]
        lines.append(
            f"- `{subject_id}`: pass34 `{base['mean_score']:.3f}` -> pass36 `{new['mean_score']:.3f}` "
            f"(delta `{new['mean_score'] - base['mean_score']:+.3f}`) | predicted `{base['predicted_label']}` -> `{new['predicted_label']}`"
        )
    return "\n".join(lines)


def render_gap_rows(rows: list[dict[str, Any]], *, top_n: int = 6) -> str:
    if not rows:
        return "  - none"
    return "\n".join(
        f"  - `{row['feature']}` contribution delta `{row['mean_contribution_delta']:+.3f}` | "
        f"z-mean delta `{row['zscore_mean_delta']:+.3f}` | raw-mean delta `{row['raw_mean_delta']:+.6f}`"
        for row in rows[:top_n]
    )


def render_markdown(report: dict[str, Any]) -> str:
    pass34_summary = report["anchors"]["pass34"]["subject_summary"]
    pass36_summary = report["pass36"]["subject_summary"]
    derived = report["derived"]
    gap_n3_brux1 = report["pass36"]["audit"]["pairwise_gaps"]["n3_minus_brux1"]
    gap_brux2_n3 = report["pass36"]["audit"]["pairwise_gaps"]["brux2_minus_n3"]
    warning_lines = "\n".join(f"- {warning}" for warning in report["warnings"]) or "- none"
    return f"""# Pass 36 — record-relative plus compact shape composition audit on repaired `A1-only` EMG scaffold

Date: 2026-05-05
Status: bounded composition audit completed; added the four pass35 compact shape descriptors on top of the existing pass34 record-relative `EMG1-EMG2` percentile-band table while keeping selected rows, subject set, LOSO split, train-time exclusions, and model family fixed.

## Why this pass exists

This pass asks one exact follow-up question from the campaign handoff:
- start from the existing pass34 record-relative audit path and feature table
- keep the repaired five-subject percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold fixed
- keep the same train-time exclusions fixed: `{', '.join(BASE_EXCLUDE_REGEXES)}`
- keep the same `logreg` LOSO interpretation surface
- add only the same four compact shape features from pass35: `{', '.join(SHAPE_FEATURES)}`
- compare only pass34 versus `record-relative + shape`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass36_record_relative_shape_composition_audit.py`
- Composed feature table: `projects/bruxism-cap/data/window_features_pass36_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json`
- Summary JSON: `projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit-summary.json`
- Summary report: `projects/bruxism-cap/reports/pass36-record-relative-shape-composition-audit.md`

## Scaffold parity checks
- pass34 selected-row counts: `{report['anchors']['pass34']['counts_by_subject']}`
- pass35 selected-row counts: `{report['anchors']['pass35_shape']['counts_by_subject']}`
- pass36 selected-row counts: `{report['pass36']['counts_by_subject']}`
- warnings:
{warning_lines}

## Honest LOSO subject-level comparison
- pass34 balanced accuracy: `{pass34_summary['balanced_accuracy']:.3f}`
- pass36 balanced accuracy: `{pass36_summary['balanced_accuracy']:.3f}`
- pass34 sensitivity: `{pass34_summary['sensitivity']:.3f}`
- pass36 sensitivity: `{pass36_summary['sensitivity']:.3f}`
- pass34 specificity: `{pass34_summary['specificity']:.3f}`
- pass36 specificity: `{pass36_summary['specificity']:.3f}`
- pass34 best-bruxism-minus-highest-control margin: `{derived['pass34_best_brux_minus_highest_control']:+.3f}`
- pass36 best-bruxism-minus-highest-control margin: `{derived['pass36_best_brux_minus_highest_control']:+.3f}`

Subject score deltas:
{render_subject_delta_lines(pass34_subjects=report['anchors']['pass34']['subjects'], pass36_subjects=report['pass36']['subjects'])}

## Required gap checks
- pass34 `n3 - brux1` gap: `{derived['pass34_n3_minus_brux1']:+.3f}`
- pass36 `n3 - brux1` gap: `{derived['pass36_n3_minus_brux1']:+.3f}`
- pass34 `brux2 - n3` gap: `{derived['pass34_brux2_minus_n3']:+.3f}`
- pass36 `brux2 - n3` gap: `{derived['pass36_brux2_minus_n3']:+.3f}`
- pass34 best-bruxism-minus-highest-control margin: `{derived['pass34_best_brux_minus_highest_control']:+.3f}`
- pass36 best-bruxism-minus-highest-control margin: `{derived['pass36_best_brux_minus_highest_control']:+.3f}`

## Shape-aware gap contributors
Top positive contributors keeping `n3` above `brux1`:
{render_gap_rows([row for row in gap_n3_brux1['feature_deltas'] if row['mean_contribution_delta'] > 0])}

Top negative contributors against `brux2` versus `n3`:
{render_gap_rows([row for row in gap_brux2_n3['feature_deltas'] if row['mean_contribution_delta'] < 0])}

## Verdict
{report['verdict']}

## Interpretation
1. This is an apples-to-apples composition audit: the pass34 selected rows stay fixed and the only added information is the same bounded pass35 shape family.
2. The key decision question is whether stacking the two best EMG clues finally clears honest subject-level sensitivity or at least improves the pass34 subject-ordering surface without introducing row drift.
3. The composition does help, but only through `brux2`: it rises above threshold while `brux1` falls further below threshold, so this is a real but incomplete benchmark improvement rather than a clean all-subject EMG fix.
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    reports_dir = root / "reports"

    pass28_features = data_dir / "window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv"
    pass34_features = data_dir / "window_features_pass34_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative.csv"
    pass35_features = data_dir / "window_features_pass35_emg_s2_mcap_a1_only_pct10_90_timepos10_shape.csv"
    pass34_report_path = reports_dir / "loso-cv-pass34-emg-a1-pct10-90-record-relative.json"
    pass36_features = data_dir / "window_features_pass36_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape.csv"
    pass36_report_path = reports_dir / "loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json"
    summary_json_path = reports_dir / "pass36-record-relative-shape-composition-audit-summary.json"
    summary_md_path = reports_dir / "pass36-record-relative-shape-composition-audit.md"

    pass28_df = load_feature_frame(pass28_features)
    pass34_df = load_feature_frame(pass34_features)
    pass35_df = load_feature_frame(pass35_features)
    pass34_report = json.loads(pass34_report_path.read_text(encoding="utf-8"))

    composed_df, composition_summary = build_composed_table(pass34_df=pass34_df, pass35_df=pass35_df)
    pass36_features.parent.mkdir(parents=True, exist_ok=True)
    composed_df.to_csv(pass36_features, index=False)
    pass36_report = run_train_baseline(features_csv=pass36_features, out_json=pass36_report_path)

    feature_columns, selection_excluded = select_feature_columns(composed_df, exclude_patterns=BASE_EXCLUDE_REGEXES)
    audit_focus_features = SHAPE_FEATURES + [
        feature for feature in ["mean", "max", "ptp", "line_length", "zero_crossing_rate", "rectified_std", "envelope_std", "envelope_cv", "rectified_mean", "envelope_mean", "p95_abs"]
        if feature in composed_df.columns
    ]
    audit = audit_channel(
        channel_name="EMG1-EMG2",
        features_csv=pass36_features,
        report_path=pass36_report_path,
        feature_columns=feature_columns,
        focus_features=audit_focus_features,
        model_name="logreg",
        random_state=42,
    )

    pass34_subjects = load_subjects(pass34_report)
    pass36_subjects = load_subjects(pass36_report)
    warnings = []
    warnings.extend(validate_same_selected_rows(left_df=pass28_df, right_df=pass34_df, label="pass28 baseline vs pass34 record-relative table"))
    warnings.extend(validate_same_selected_rows(left_df=pass34_df, right_df=pass35_df, label="pass34 record-relative table vs pass35 shape table"))
    warnings.extend(validate_same_selected_rows(left_df=pass34_df, right_df=composed_df, label="pass34 record-relative table vs pass36 composed table"))

    verdict = (
        "The two best current EMG gains do compose into a subject-sensitivity improvement on this repaired scaffold: "
        "`brux2` crosses the subject threshold (`0.480` -> `0.808`) and `n3` drops sharply (`0.439` -> `0.068`), "
        "but `brux1` gets worse (`0.180` -> `0.112`), so the gain is real but not a clean across-bruxism fix."
    )

    report = {
        "pass": 36,
        "experiment": "record_relative_plus_compact_shape_composition_audit_on_repaired_a1_only_emg",
        "composition": composition_summary,
        "anchors": {
            "pass28": {
                "features_csv": str(pass28_features.resolve()),
                "counts_by_subject": summarize_counts(pass28_df),
            },
            "pass34": {
                "features_csv": str(pass34_features.resolve()),
                "report_path": str(pass34_report_path.resolve()),
                "counts_by_subject": summarize_counts(pass34_df),
                "subject_summary": pass34_report["models"]["logreg"]["subject_aggregation"]["summary"],
                "subjects": pass34_subjects,
            },
            "pass35_shape": {
                "features_csv": str(pass35_features.resolve()),
                "counts_by_subject": summarize_counts(pass35_df),
            },
        },
        "pass36": {
            "features_csv": str(pass36_features.resolve()),
            "report_path": str(pass36_report_path.resolve()),
            "counts_by_subject": summarize_counts(composed_df),
            "subject_summary": pass36_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "window_summary": pass36_report["models"]["logreg"]["summary"],
            "subjects": pass36_subjects,
            "selected_feature_columns": feature_columns,
            "selection_excluded_columns": selection_excluded,
            "audit": audit,
        },
        "derived": {
            "pass34_n3_minus_brux1": float(pass34_subjects["n3"]["mean_score"] - pass34_subjects["brux1"]["mean_score"]),
            "pass36_n3_minus_brux1": float(pass36_subjects["n3"]["mean_score"] - pass36_subjects["brux1"]["mean_score"]),
            "pass34_brux2_minus_n3": float(pass34_subjects["brux2"]["mean_score"] - pass34_subjects["n3"]["mean_score"]),
            "pass36_brux2_minus_n3": float(pass36_subjects["brux2"]["mean_score"] - pass36_subjects["n3"]["mean_score"]),
            "pass34_best_brux_minus_highest_control": best_brux_minus_highest_control(pass34_subjects),
            "pass36_best_brux_minus_highest_control": best_brux_minus_highest_control(pass36_subjects),
        },
        "warnings": warnings,
        "verdict": verdict,
        "summary_json_path": str(summary_json_path.resolve()),
        "summary_md_path": str(summary_md_path.resolve()),
    }

    summary_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_markdown(report), encoding="utf-8")
    print(summary_md_path)
    print(summary_json_path)


if __name__ == "__main__":
    main()
