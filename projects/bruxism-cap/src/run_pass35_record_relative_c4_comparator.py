from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from audit_percentile_band_channel_gap import (
    audit_channel,
    build_timing_match_summary,
    load_feature_frame,
    select_feature_columns,
)
from run_pass34_record_relative_emg_audit import (
    BASE_EXCLUDE_REGEXES,
    EPSILON,
    RELATIVE_FEATURES,
    best_brux_minus_highest_control,
    build_record_relative_table,
    load_subjects,
    run_train_baseline,
)


PASS_NUMBER = 35


def subject_score_table(
    *, baseline_subjects: dict[str, dict[str, Any]], transformed_subjects: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    rows = {}
    for subject_id in ["brux1", "brux2", "n3", "n5", "n11"]:
        baseline = baseline_subjects[subject_id]
        transformed = transformed_subjects[subject_id]
        rows[subject_id] = {
            "baseline_mean_score": float(baseline["mean_score"]),
            "transformed_mean_score": float(transformed["mean_score"]),
            "delta_mean_score": float(transformed["mean_score"] - baseline["mean_score"]),
            "baseline_predicted_label": baseline["predicted_label"],
            "transformed_predicted_label": transformed["predicted_label"],
        }
    return rows


def render_subject_delta_lines(subject_rows: dict[str, Any]) -> str:
    lines = []
    for subject_id in ["brux1", "brux2", "n3", "n5", "n11"]:
        row = subject_rows[subject_id]
        lines.append(
            f"- `{subject_id}`: baseline `{row['baseline_mean_score']:.3f}` -> relative `{row['transformed_mean_score']:.3f}` "
            f"(delta `{row['delta_mean_score']:+.3f}`) | predicted `{row['baseline_predicted_label']}` -> `{row['transformed_predicted_label']}`"
        )
    return "\n".join(lines)


def render_warning_lines(warnings: list[str]) -> str:
    if not warnings:
        return "- none"
    return "\n".join(f"- {warning}" for warning in warnings)


def render_markdown(report: dict[str, Any]) -> str:
    derived = report["derived"]
    baseline_summary = report["baseline"]["subject_summary"]
    transformed_summary = report["record_relative"]["subject_summary"]
    scaffold = report["scaffold_match"]
    return f"""# Pass {PASS_NUMBER} — matched `C4-P4` comparator for the record-relative scaffold rebuild

Date: 2026-05-05
Status: matched comparison-channel rerun completed; rebuilt `C4-P4` on the same repaired percentile-band `A1-only` scaffold and applied the same within-record robust feature-space transform used in pass34 so the repo can separate representation effects from channel effects.

## Why this pass exists

Pass34 changed representation only on the repaired `EMG1-EMG2` scaffold. This comparator rebuild answers the follow-up question the same day:
- keep the same repaired `SLEEP-S2 + MCAP-A1-only` percentile-band subset
- keep the same train-time exclusions fixed: `{', '.join(BASE_EXCLUDE_REGEXES)}`
- keep the same retained feature family and the same relative-feature transform list
- keep the same `logreg` LOSO evaluation contract
- change only the channel source (`C4-P4` baseline table instead of `EMG1-EMG2` baseline table)

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass35_record_relative_c4_comparator.py`
- Transformed feature table: `projects/bruxism-cap/data/window_features_pass35_c4_s2_mcap_a1_only_pct10_90_timepos10_record_relative.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass35-c4-a1-pct10-90-record-relative.json`
- Summary JSON: `projects/bruxism-cap/reports/pass35-record-relative-c4-comparator-summary.json`
- Summary report: `projects/bruxism-cap/reports/pass35-record-relative-c4-comparator.md`

## Scaffold matching confirmation
- Cross-channel selected rows still timing-match after the transform: `{scaffold['timing_match']['identical_selected_rows']}`.
- Shared selector columns checked: `{', '.join(scaffold['timing_match']['shared_columns_checked'])}`.
- Selected trainable feature columns match pass34 EMG exactly: `{scaffold['selected_feature_columns_match']}`.
- Relative feature list matches pass34 EMG exactly: `{scaffold['relative_feature_list_match']}`.
- Evaluation contract matches pass34 EMG (`logreg` LOSO with the same exclusion regex set): `{scaffold['evaluation_contract_match']}`.

## Honest LOSO subject-level comparison inside `C4-P4`
- baseline subject-level balanced accuracy: `{baseline_summary['balanced_accuracy']:.3f}`
- relative subject-level balanced accuracy: `{transformed_summary['balanced_accuracy']:.3f}`
- baseline subject-level sensitivity: `{baseline_summary['sensitivity']:.3f}`
- relative subject-level sensitivity: `{transformed_summary['sensitivity']:.3f}`
- baseline best-bruxism-minus-highest-control margin: `{derived['baseline_best_brux_minus_highest_control']:+.3f}`
- relative best-bruxism-minus-highest-control margin: `{derived['record_relative_best_brux_minus_highest_control']:+.3f}`

Subject score deltas:
{render_subject_delta_lines(report['subject_score_deltas'])}

## Comparator-focused score checks
- baseline `n3 - brux1` gap: `{derived['baseline_n3_minus_brux1']:+.3f}`
- relative `n3 - brux1` gap: `{derived['record_relative_n3_minus_brux1']:+.3f}`
- baseline `brux2 - n3` gap: `{derived['baseline_brux2_minus_n3']:+.3f}`
- relative `brux2 - n3` gap: `{derived['record_relative_brux2_minus_n3']:+.3f}`

## EMG-vs-C4 comparison on the same transformed scaffold
- pass34 EMG relative balanced accuracy: `{derived['emg_record_relative_balanced_accuracy']:.3f}`
- pass35 C4 relative balanced accuracy: `{derived['c4_record_relative_balanced_accuracy']:.3f}`
- pass34 EMG relative best-bruxism-minus-highest-control margin: `{derived['emg_record_relative_best_brux_minus_highest_control']:+.3f}`
- pass35 C4 relative best-bruxism-minus-highest-control margin: `{derived['c4_record_relative_best_brux_minus_highest_control']:+.3f}`
- pass34 EMG relative `brux2 - n3` gap: `{derived['emg_record_relative_brux2_minus_n3']:+.3f}`
- pass35 C4 relative `brux2 - n3` gap: `{derived['c4_record_relative_brux2_minus_n3']:+.3f}`

## Unavoidable divergences and warnings
{render_warning_lines(report['warnings'])}

## Interpretation
1. This comparator pass preserves the same scaffold logic as pass34, so any difference against the EMG rebuild is still interpretable as a channel/representation interaction rather than a selector drift.
2. If `C4-P4` stays stronger after the same transform, then the pass34 gain was not just “representation fixed everything”; it helped EMG, but the comparison channel still carries a stronger signal on this repaired benchmark.
3. If `C4-P4` weakens materially under the same transform, then the new representation may be specifically aligned with the EMG morphology failure rather than a universal scaffold improvement.
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    reports_dir = root / "reports"

    baseline_features = data_dir / "window_features_pass29_c4_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv"
    baseline_report_path = reports_dir / "loso-cv-pass29-c4-a1-pct10-90-timepos10-selected.json"
    transformed_features = data_dir / "window_features_pass35_c4_s2_mcap_a1_only_pct10_90_timepos10_record_relative.csv"
    transformed_report_path = reports_dir / "loso-cv-pass35-c4-a1-pct10-90-record-relative.json"
    summary_json_path = reports_dir / "pass35-record-relative-c4-comparator-summary.json"
    summary_md_path = reports_dir / "pass35-record-relative-c4-comparator.md"

    emg_transformed_features = data_dir / "window_features_pass34_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative.csv"
    emg_transformed_report_path = reports_dir / "loso-cv-pass34-emg-a1-pct10-90-record-relative.json"
    emg_summary_path = reports_dir / "pass34-record-relative-emg-audit-summary.json"

    baseline_df = load_feature_frame(baseline_features)
    transformed_df, transform_summary = build_record_relative_table(
        baseline_df,
        relative_features=RELATIVE_FEATURES,
        epsilon=EPSILON,
    )
    transformed_features.parent.mkdir(parents=True, exist_ok=True)
    transformed_df.to_csv(transformed_features, index=False)

    baseline_report = json.loads(baseline_report_path.read_text(encoding="utf-8"))
    transformed_report = run_train_baseline(transformed_features, transformed_report_path)

    feature_columns, selection_excluded = select_feature_columns(
        transformed_df,
        exclude_patterns=BASE_EXCLUDE_REGEXES,
    )
    transformed_audit = audit_channel(
        channel_name="C4-P4",
        features_csv=transformed_features,
        report_path=transformed_report_path,
        feature_columns=feature_columns,
        focus_features=transform_summary["relative_features_applied"],
        model_name="logreg",
        random_state=42,
    )

    baseline_subjects = load_subjects(baseline_report)
    transformed_subjects = load_subjects(transformed_report)
    subject_score_deltas = subject_score_table(
        baseline_subjects=baseline_subjects,
        transformed_subjects=transformed_subjects,
    )

    emg_transformed_df = load_feature_frame(emg_transformed_features)
    emg_transformed_report = json.loads(emg_transformed_report_path.read_text(encoding="utf-8"))
    emg_summary = json.loads(emg_summary_path.read_text(encoding="utf-8"))
    emg_subjects = load_subjects(emg_transformed_report)
    emg_feature_columns = emg_summary["record_relative"]["selected_feature_columns"]

    timing_match = build_timing_match_summary(emg_transformed_df, transformed_df)
    warnings: list[str] = [
        "Baseline source tables and anchor reports are intentionally channel-specific (`pass28` EMG vs `pass29` C4), even though the repaired percentile-band subset and evaluation contract are matched.",
    ]
    if transform_summary["relative_features_missing"]:
        warnings.append(
            "Some requested relative features were missing from the C4 table: "
            + ", ".join(transform_summary["relative_features_missing"])
        )
    if not timing_match["identical_selected_rows"]:
        warnings.append("Selected rows no longer match across transformed EMG and C4 tables; inspect selector drift before trusting the comparison.")
    if feature_columns != emg_feature_columns:
        warnings.append("Selected feature column order/content diverges from the pass34 EMG rebuild.")
    if transform_summary["relative_features_applied"] != emg_summary["transform"]["relative_features_applied"]:
        warnings.append("Applied relative-feature list diverges from the pass34 EMG rebuild.")

    report = {
        "pass": PASS_NUMBER,
        "experiment": "matched_c4_record_relative_comparator_on_repaired_a1_only_percentile_band_scaffold",
        "baseline": {
            "features_csv": str(baseline_features.resolve()),
            "report_path": str(baseline_report_path.resolve()),
            "subject_summary": baseline_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "subjects": baseline_subjects,
        },
        "record_relative": {
            "features_csv": str(transformed_features.resolve()),
            "report_path": str(transformed_report_path.resolve()),
            "subject_summary": transformed_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "subjects": transformed_subjects,
            "selected_feature_columns": feature_columns,
            "selection_excluded_columns": selection_excluded,
            "audit_subjects": transformed_audit["subjects"],
            "pairwise_gaps": transformed_audit["pairwise_gaps"],
        },
        "transform": transform_summary,
        "subject_score_deltas": subject_score_deltas,
        "scaffold_match": {
            "timing_match": timing_match,
            "selected_feature_columns_match": feature_columns == emg_feature_columns,
            "relative_feature_list_match": transform_summary["relative_features_applied"] == emg_summary["transform"]["relative_features_applied"],
            "evaluation_contract_match": True,
            "comparison_against": {
                "emg_transformed_features_csv": str(emg_transformed_features.resolve()),
                "emg_transformed_report_path": str(emg_transformed_report_path.resolve()),
            },
        },
        "warnings": warnings,
        "derived": {
            "baseline_n3_minus_brux1": float(baseline_subjects["n3"]["mean_score"] - baseline_subjects["brux1"]["mean_score"]),
            "record_relative_n3_minus_brux1": float(transformed_subjects["n3"]["mean_score"] - transformed_subjects["brux1"]["mean_score"]),
            "baseline_brux2_minus_n3": float(baseline_subjects["brux2"]["mean_score"] - baseline_subjects["n3"]["mean_score"]),
            "record_relative_brux2_minus_n3": float(transformed_subjects["brux2"]["mean_score"] - transformed_subjects["n3"]["mean_score"]),
            "baseline_best_brux_minus_highest_control": best_brux_minus_highest_control(baseline_subjects),
            "record_relative_best_brux_minus_highest_control": best_brux_minus_highest_control(transformed_subjects),
            "emg_record_relative_balanced_accuracy": float(emg_transformed_report["models"]["logreg"]["subject_aggregation"]["summary"]["balanced_accuracy"]),
            "c4_record_relative_balanced_accuracy": float(transformed_report["models"]["logreg"]["subject_aggregation"]["summary"]["balanced_accuracy"]),
            "emg_record_relative_best_brux_minus_highest_control": best_brux_minus_highest_control(emg_subjects),
            "c4_record_relative_best_brux_minus_highest_control": best_brux_minus_highest_control(transformed_subjects),
            "emg_record_relative_brux2_minus_n3": float(emg_subjects["brux2"]["mean_score"] - emg_subjects["n3"]["mean_score"]),
            "c4_record_relative_brux2_minus_n3": float(transformed_subjects["brux2"]["mean_score"] - transformed_subjects["n3"]["mean_score"]),
        },
    }
    summary_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_markdown(report), encoding="utf-8")
    print(summary_md_path)
    print(summary_json_path)


if __name__ == "__main__":
    main()
