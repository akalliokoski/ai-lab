from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from audit_percentile_band_channel_gap import audit_channel, load_feature_frame, select_feature_columns

BASE_EXCLUDE_REGEXES = [r"^bp_", r"^rel_bp_", r"^ratio_"]
RELATIVE_FEATURES = [
    "mean",
    "max",
    "ptp",
    "line_length",
    "zero_crossing_rate",
    "rectified_std",
    "envelope_std",
    "envelope_cv",
    "rectified_mean",
    "envelope_mean",
    "p95_abs",
]
EPSILON = 1e-6


def run_train_baseline(features_csv: Path, out_json: Path) -> dict[str, Any]:
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


def median_absolute_deviation(values: pd.Series) -> float:
    median = float(values.median())
    return float((values - median).abs().median())


def build_record_relative_table(df: pd.DataFrame, *, relative_features: list[str], epsilon: float) -> tuple[pd.DataFrame, dict[str, Any]]:
    transformed = df.copy()
    available = [feature for feature in relative_features if feature in transformed.columns]
    missing = [feature for feature in relative_features if feature not in transformed.columns]
    subject_stats: dict[str, dict[str, dict[str, float]]] = {}

    for subject_id, subject_index in transformed.groupby("subject_id").groups.items():
        subject_rows = transformed.loc[subject_index, available]
        medians = subject_rows.median()
        mads = subject_rows.apply(median_absolute_deviation, axis=0)
        safe_scale = mads.clip(lower=epsilon)
        transformed.loc[subject_index, available] = (subject_rows - medians) / safe_scale
        subject_stats[str(subject_id)] = {
            feature: {
                "median": float(medians[feature]),
                "mad": float(mads[feature]),
                "scale_used": float(safe_scale[feature]),
            }
            for feature in available
        }

    return transformed, {
        "relative_features_requested": relative_features,
        "relative_features_applied": available,
        "relative_features_missing": missing,
        "epsilon": float(epsilon),
        "per_subject_reference": subject_stats,
    }


def load_subjects(report: dict[str, Any], *, model_name: str = "logreg") -> dict[str, dict[str, Any]]:
    return {
        row["subject_id"]: row
        for row in report["models"][model_name]["subject_aggregation"]["subjects"]
    }


def subject_score_table(*, baseline_subjects: dict[str, dict[str, Any]], transformed_subjects: dict[str, dict[str, Any]]) -> dict[str, Any]:
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


def best_brux_minus_highest_control(subjects: dict[str, dict[str, Any]]) -> float:
    best_brux = max(subjects["brux1"]["mean_score"], subjects["brux2"]["mean_score"])
    highest_control = max(subjects["n3"]["mean_score"], subjects["n5"]["mean_score"], subjects["n11"]["mean_score"])
    return float(best_brux - highest_control)


def render_subject_delta_lines(subject_rows: dict[str, Any]) -> str:
    lines = []
    for subject_id in ["brux1", "brux2", "n3", "n5", "n11"]:
        row = subject_rows[subject_id]
        lines.append(
            f"- `{subject_id}`: baseline `{row['baseline_mean_score']:.3f}` -> relative `{row['transformed_mean_score']:.3f}` "
            f"(delta `{row['delta_mean_score']:+.3f}`) | predicted `{row['baseline_predicted_label']}` -> `{row['transformed_predicted_label']}`"
        )
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    derived = report["derived"]
    baseline_summary = report["baseline"]["subject_summary"]
    transformed_summary = report["record_relative"]["subject_summary"]
    return f"""# Pass 34 — record-relative robust feature-space normalization audit on repaired `A1-only` EMG

Date: 2026-05-05
Status: bounded representation audit completed; one post-extraction feature-table transform tested the retained `EMG1-EMG2` morphology-envelope family without changing selector rules, labels, subject set, or model family.

## Why this is the smallest valid test

This pass implements exactly one representation change from the pass34 synthesis memo:
- start from the existing pass28 `EMG1-EMG2` feature CSV
- keep the repaired `SLEEP-S2 + MCAP-A1-only` percentile-band selected rows fixed
- keep the same train-time exclusions fixed: `{', '.join(BASE_EXCLUDE_REGEXES)}`
- keep the same model family fixed: `logreg` LOSO
- replace only a bounded retained feature subset with within-record robust relative values using `(x - median_subject_feature) / max(MAD_subject_feature, {report['transform']['epsilon']})`

## What changed

Transformed retained features:
- `{', '.join(report['transform']['relative_features_applied'])}`

Intentionally left unchanged:
- window extraction and selector logic
- non-transformed retained features (`std`, `min`, `rms`, `sample_entropy`, `burst_fraction`, `burst_rate_hz`)
- model family, thresholding surface, and subject set
- all `bp_`, `rel_bp_`, and `ratio_` exclusions from the anchor

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass34_record_relative_emg_audit.py`
- Transformed feature table: `projects/bruxism-cap/data/window_features_pass34_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass34-emg-a1-pct10-90-record-relative.json`
- Summary JSON: `projects/bruxism-cap/reports/pass34-record-relative-emg-audit-summary.json`
- Summary report: `projects/bruxism-cap/reports/pass34-record-relative-emg-audit.md`

## Honest LOSO subject-level comparison
- baseline subject-level balanced accuracy: `{baseline_summary['balanced_accuracy']:.3f}`
- relative subject-level balanced accuracy: `{transformed_summary['balanced_accuracy']:.3f}`
- baseline subject-level sensitivity: `{baseline_summary['sensitivity']:.3f}`
- relative subject-level sensitivity: `{transformed_summary['sensitivity']:.3f}`
- baseline best-bruxism-minus-highest-control margin: `{derived['baseline_best_brux_minus_highest_control']:+.3f}`
- relative best-bruxism-minus-highest-control margin: `{derived['record_relative_best_brux_minus_highest_control']:+.3f}`

Subject score deltas:
{render_subject_delta_lines(report['subject_score_deltas'])}

## Anchor-focused score checks
- baseline `n3 - brux1` gap: `{derived['baseline_n3_minus_brux1']:+.3f}`
- relative `n3 - brux1` gap: `{derived['record_relative_n3_minus_brux1']:+.3f}`
- baseline `brux2 - n3` gap: `{derived['baseline_brux2_minus_n3']:+.3f}`
- relative `brux2 - n3` gap: `{derived['record_relative_brux2_minus_n3']:+.3f}`
- baseline best-bruxism-minus-highest-control margin: `{derived['baseline_best_brux_minus_highest_control']:+.3f}`
- relative best-bruxism-minus-highest-control margin: `{derived['record_relative_best_brux_minus_highest_control']:+.3f}`

## Interpretation

1. This was a pure post-extraction audit: the selector scaffold stayed fixed, so any movement is attributable to one within-record robust representation change rather than extraction drift.
2. The key decision target is whether `brux1` moves closer to or above `n3` without collapsing `brux2` or inflating controls.
3. Regardless of outcome, this pass preserves an auditable anchor comparison because only one bounded feature-family transform changed and the unchanged retained features remain visible.

## What was intentionally left for later

- no broad waveform-level normalization rewrite
- no backup shape-family expansion (`skewness`, `kurtosis`, Hjorth features)
- no train-time include/exclude rewrite beyond the existing anchor exclusions
- no `C4-P4` comparison rerun in this pass
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    reports_dir = root / "reports"

    baseline_features = data_dir / "window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv"
    baseline_report_path = reports_dir / "loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json"
    transformed_features = data_dir / "window_features_pass34_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative.csv"
    transformed_report_path = reports_dir / "loso-cv-pass34-emg-a1-pct10-90-record-relative.json"
    summary_json_path = reports_dir / "pass34-record-relative-emg-audit-summary.json"
    summary_md_path = reports_dir / "pass34-record-relative-emg-audit.md"

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
        channel_name="EMG1-EMG2",
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

    report = {
        "pass": 34,
        "experiment": "record_relative_robust_feature_space_normalization_audit_on_repaired_a1_only_emg",
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
        "derived": {
            "baseline_n3_minus_brux1": float(baseline_subjects["n3"]["mean_score"] - baseline_subjects["brux1"]["mean_score"]),
            "record_relative_n3_minus_brux1": float(transformed_subjects["n3"]["mean_score"] - transformed_subjects["brux1"]["mean_score"]),
            "baseline_brux2_minus_n3": float(baseline_subjects["brux2"]["mean_score"] - baseline_subjects["n3"]["mean_score"]),
            "record_relative_brux2_minus_n3": float(transformed_subjects["brux2"]["mean_score"] - transformed_subjects["n3"]["mean_score"]),
            "baseline_best_brux_minus_highest_control": best_brux_minus_highest_control(baseline_subjects),
            "record_relative_best_brux_minus_highest_control": best_brux_minus_highest_control(transformed_subjects),
        },
    }
    summary_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_markdown(report), encoding="utf-8")
    print(summary_md_path)
    print(summary_json_path)


if __name__ == "__main__":
    main()
