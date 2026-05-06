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
SUBJECTS = [
    ("brux1", "bruxism"),
    ("brux2", "bruxism"),
    ("n3", "control"),
    ("n5", "control"),
    ("n11", "control"),
]
EXPECTED_FULL_COUNTS = {"brux1": 27, "brux2": 29, "n3": 29, "n5": 134, "n11": 14}
EXPECTED_SELECTED_COUNTS = {subject_id: 10 for subject_id, _label in SUBJECTS}


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def run_prepare_windows(*, root: Path, out_csv: Path) -> None:
    if out_csv.exists():
        out_csv.unlink()
    script = Path(__file__).with_name("prepare_windows.py")
    raw_dir = root / "data" / "raw" / "capslpdb"
    for index, (subject_id, label) in enumerate(SUBJECTS):
        cmd = [
            sys.executable,
            str(script),
            "--edf",
            str(raw_dir / f"{subject_id}.edf"),
            "--annotation-txt",
            str(raw_dir / f"{subject_id}.txt"),
            "--annotation-events",
            "SLEEP-S2",
            "--require-overlap-events",
            "MCAP-A1",
            "--exclude-overlap-events",
            "MCAP-A2,MCAP-A3",
            "--subject-id",
            subject_id,
            "--label",
            label,
            "--channel",
            "EMG1-EMG2",
            "--window-seconds",
            "30",
            "--out",
            str(out_csv),
        ]
        if index > 0:
            cmd.append("--append")
        run(cmd)


def run_selector(*, features_csv: Path, out_csv: Path, out_json: Path) -> dict[str, Any]:
    script = Path(__file__).with_name("select_time_position_matched_windows.py")
    cmd = [
        sys.executable,
        str(script),
        "--features-csv",
        str(features_csv),
        "--subjects",
        ",".join(subject_id for subject_id, _label in SUBJECTS),
        "--cap",
        "10",
        "--mode",
        "percentile-band",
        "--lower-quantile",
        "0.1",
        "--upper-quantile",
        "0.9",
        "--out-csv",
        str(out_csv),
        "--out-json",
        str(out_json),
    ]
    run(cmd)
    return json.loads(out_json.read_text(encoding="utf-8"))


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
    run(cmd)
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


def build_warning_list(
    *,
    full_counts: dict[str, int],
    selected_counts: dict[str, int],
    baseline_df: pd.DataFrame,
    selected_df: pd.DataFrame,
) -> list[str]:
    warnings: list[str] = []
    if full_counts != EXPECTED_FULL_COUNTS:
        warnings.append(
            f"full exclusive A1-only counts changed from expected pass27 scaffold {EXPECTED_FULL_COUNTS} to {full_counts}"
        )
    if selected_counts != EXPECTED_SELECTED_COUNTS:
        warnings.append(
            f"selected percentile-band counts changed from expected pass28 scaffold {EXPECTED_SELECTED_COUNTS} to {selected_counts}"
        )

    compare_cols = ["subject_id", "start_s", "end_s", "time_match_rank", "relative_time_quantile"]
    baseline_view = baseline_df[compare_cols].sort_values(compare_cols).reset_index(drop=True)
    selected_view = selected_df[compare_cols].sort_values(compare_cols).reset_index(drop=True)
    if not baseline_view.equals(selected_view):
        warnings.append("selected percentile-band rows do not exactly match the pass28 anchor metadata")
    return warnings


def render_subject_delta_lines(
    *,
    baseline_subjects: dict[str, dict[str, Any]],
    new_subjects: dict[str, dict[str, Any]],
) -> str:
    lines = []
    for subject_id in ["brux1", "brux2", "n3", "n5", "n11"]:
        base = baseline_subjects[subject_id]
        new = new_subjects[subject_id]
        lines.append(
            f"- `{subject_id}`: baseline `{base['mean_score']:.3f}` -> pass35 `{new['mean_score']:.3f}` "
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
    baseline_summary = report["anchors"]["pass28"]["subject_summary"]
    new_summary = report["pass35"]["subject_summary"]
    derived = report["derived"]
    gap_n3_brux1 = report["pass35"]["audit"]["pairwise_gaps"]["n3_minus_brux1"]
    gap_brux2_n3 = report["pass35"]["audit"]["pairwise_gaps"]["brux2_minus_n3"]
    warning_lines = "\n".join(f"- {warning}" for warning in report["warnings"]) or "- none"
    return f"""# Pass 35 — compact shape-feature expansion on repaired `A1-only` EMG percentile-band scaffold

Date: 2026-05-05
Status: bounded representation rerun completed; rebuilt the same exclusive `SLEEP-S2 + MCAP-A1-only` EMG scaffold with four added shape descriptors (`skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`) while keeping selector settings, subject set, and `logreg` LOSO fixed.

## Why this pass exists

Pass34 showed that within-record feature-space normalization improved `brux2` but still left `brux1` below `n3`, so the next bounded backup experiment from the synthesis memo was one compact shape-only family on the same repaired scaffold.

This pass makes exactly one primary increment:
- rebuild the uncapped exclusive `A1-only` `EMG1-EMG2` pool from raw EDF windows using the same extraction rule as pass27/pass28
- reapply the same repaired percentile-band selector from pass28 (`0.10` to `0.90`, `10` windows per subject)
- keep train-time exclusions fixed: `{', '.join(BASE_EXCLUDE_REGEXES)}`
- keep the same `logreg` LOSO interpretation surface
- add only `{', '.join(SHAPE_FEATURES)}` to the feature table

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass35_shape_feature_expansion.py`
- Feature patch: `projects/bruxism-cap/src/features.py`
- Full rebuilt EMG pool: `projects/bruxism-cap/data/window_features_pass35_emg_s2_mcap_a1_only_full_envelope_shape.csv`
- Percentile-band selected dataset: `projects/bruxism-cap/data/window_features_pass35_emg_s2_mcap_a1_only_pct10_90_timepos10_shape.csv`
- Selector summary: `projects/bruxism-cap/reports/time-position-match-pass35-emg-a1-pct10-90-shape.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass35-emg-a1-pct10-90-shape.json`
- Summary JSON: `projects/bruxism-cap/reports/pass35-shape-feature-expansion-summary.json`
- Summary report: `projects/bruxism-cap/reports/pass35-shape-feature-expansion.md`

## Anchor comparison path
- pass28 anchor LOSO report: `{report['anchors']['pass28']['report_path']}`
- pass34 mixed-result summary: `{report['anchors']['pass34']['summary_path']}`
- pass35 summary JSON: `{report['summary_json_path']}`

## Reproducibility and scaffold checks
- full-count check versus pass27 expectation: `{report['full_pool']['counts_by_subject']}`
- selected-count check versus pass28 expectation: `{report['selected_pool']['counts_by_subject']}`
- selector mode: `{report['selector']['match_mode']}` with percentile band `{report['selector']['percentile_band']}`
- warnings:
{warning_lines}

## Honest LOSO results
### Window level (`logreg`)
- balanced accuracy: `{report['pass35']['window_summary']['balanced_accuracy']:.3f}`
- sensitivity: `{report['pass35']['window_summary']['sensitivity']:.3f}`
- specificity: `{report['pass35']['window_summary']['specificity']:.3f}`
- AUROC: `{report['pass35']['window_summary']['auroc']}`

### Subject level (`logreg`)
- baseline pass28 balanced accuracy: `{baseline_summary['balanced_accuracy']:.3f}`
- pass35 balanced accuracy: `{new_summary['balanced_accuracy']:.3f}`
- baseline pass28 sensitivity: `{baseline_summary['sensitivity']:.3f}`
- pass35 sensitivity: `{new_summary['sensitivity']:.3f}`
- baseline pass28 specificity: `{baseline_summary['specificity']:.3f}`
- pass35 specificity: `{new_summary['specificity']:.3f}`
- baseline best-bruxism-minus-highest-control margin: `{derived['pass28_best_brux_minus_highest_control']:+.3f}`
- pass35 best-bruxism-minus-highest-control margin: `{derived['pass35_best_brux_minus_highest_control']:+.3f}`

Subject score deltas:
{render_subject_delta_lines(baseline_subjects=report['anchors']['pass28']['subjects'], new_subjects=report['pass35']['subjects'])}

## Shape-feature focused checks
- pass28 `n3 - brux1` gap: `{derived['pass28_n3_minus_brux1']:+.3f}`
- pass35 `n3 - brux1` gap: `{derived['pass35_n3_minus_brux1']:+.3f}`
- pass28 `brux2 - n3` gap: `{derived['pass28_brux2_minus_n3']:+.3f}`
- pass35 `brux2 - n3` gap: `{derived['pass35_brux2_minus_n3']:+.3f}`

Top positive contributors keeping `n3` above `brux1`:
{render_gap_rows([row for row in gap_n3_brux1['feature_deltas'] if row['mean_contribution_delta'] > 0])}

Top negative contributors against `brux2` versus `n3`:
{render_gap_rows([row for row in gap_brux2_n3['feature_deltas'] if row['mean_contribution_delta'] < 0])}

## Interpretation
1. This pass changes extraction only enough to regenerate the feature table with four bounded shape descriptors; the percentile-band row selection and LOSO evaluation surface remain the same repaired scaffold.
2. The main decision question is whether the added shape family moves `brux1` and/or `brux2` above the strongest controls without hiding subject-subset drift.
3. Treat this as a clean backup-branch test against pass28, with pass34 preserved as the intermediate mixed-result representation anchor rather than overwritten.
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    reports_dir = root / "reports"

    full_features = data_dir / "window_features_pass35_emg_s2_mcap_a1_only_full_envelope_shape.csv"
    selected_features = data_dir / "window_features_pass35_emg_s2_mcap_a1_only_pct10_90_timepos10_shape.csv"
    selector_json_path = reports_dir / "time-position-match-pass35-emg-a1-pct10-90-shape.json"
    loso_report_path = reports_dir / "loso-cv-pass35-emg-a1-pct10-90-shape.json"
    summary_json_path = reports_dir / "pass35-shape-feature-expansion-summary.json"
    summary_md_path = reports_dir / "pass35-shape-feature-expansion.md"

    pass28_features = data_dir / "window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv"
    pass28_report_path = reports_dir / "loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json"
    pass34_summary_path = reports_dir / "pass34-record-relative-emg-audit-summary.json"

    run_prepare_windows(root=root, out_csv=full_features)
    selector_report = run_selector(features_csv=full_features, out_csv=selected_features, out_json=selector_json_path)
    loso_report = run_train_baseline(features_csv=selected_features, out_json=loso_report_path)

    full_df = load_feature_frame(full_features)
    selected_df = load_feature_frame(selected_features)
    pass28_df = load_feature_frame(pass28_features)
    pass28_report = json.loads(pass28_report_path.read_text(encoding="utf-8"))
    pass34_summary = json.loads(pass34_summary_path.read_text(encoding="utf-8"))

    feature_columns, selection_excluded = select_feature_columns(selected_df, exclude_patterns=BASE_EXCLUDE_REGEXES)
    audit = audit_channel(
        channel_name="EMG1-EMG2",
        features_csv=selected_features,
        report_path=loso_report_path,
        feature_columns=feature_columns,
        focus_features=SHAPE_FEATURES,
        model_name="logreg",
        random_state=42,
    )

    pass28_subjects = load_subjects(pass28_report)
    pass35_subjects = load_subjects(loso_report)
    full_counts = summarize_counts(full_df)
    selected_counts = summarize_counts(selected_df)
    warnings = build_warning_list(
        full_counts=full_counts,
        selected_counts=selected_counts,
        baseline_df=pass28_df,
        selected_df=selected_df,
    )

    report = {
        "pass": 35,
        "experiment": "compact_shape_feature_expansion_on_repaired_a1_only_emg_percentile_band_scaffold",
        "shape_features_added": SHAPE_FEATURES,
        "full_pool": {
            "features_csv": str(full_features.resolve()),
            "counts_by_subject": full_counts,
            "expected_counts_by_subject": EXPECTED_FULL_COUNTS,
        },
        "selected_pool": {
            "features_csv": str(selected_features.resolve()),
            "counts_by_subject": selected_counts,
            "expected_counts_by_subject": EXPECTED_SELECTED_COUNTS,
            "selected_feature_columns": feature_columns,
            "selection_excluded_columns": selection_excluded,
        },
        "selector": {
            **selector_report,
            "report_path": str(selector_json_path.resolve()),
        },
        "anchors": {
            "pass28": {
                "features_csv": str(pass28_features.resolve()),
                "report_path": str(pass28_report_path.resolve()),
                "window_summary": pass28_report["models"]["logreg"]["summary"],
                "subject_summary": pass28_report["models"]["logreg"]["subject_aggregation"]["summary"],
                "subjects": pass28_subjects,
            },
            "pass34": {
                "summary_path": str(pass34_summary_path.resolve()),
                "record_relative_subject_summary": pass34_summary["record_relative"]["subject_summary"],
                "record_relative_subjects": pass34_summary["record_relative"]["subjects"],
            },
        },
        "pass35": {
            "report_path": str(loso_report_path.resolve()),
            "window_summary": loso_report["models"]["logreg"]["summary"],
            "subject_summary": loso_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "subjects": pass35_subjects,
            "audit": audit,
        },
        "derived": {
            "pass28_n3_minus_brux1": float(pass28_subjects["n3"]["mean_score"] - pass28_subjects["brux1"]["mean_score"]),
            "pass35_n3_minus_brux1": float(pass35_subjects["n3"]["mean_score"] - pass35_subjects["brux1"]["mean_score"]),
            "pass28_brux2_minus_n3": float(pass28_subjects["brux2"]["mean_score"] - pass28_subjects["n3"]["mean_score"]),
            "pass35_brux2_minus_n3": float(pass35_subjects["brux2"]["mean_score"] - pass35_subjects["n3"]["mean_score"]),
            "pass28_best_brux_minus_highest_control": best_brux_minus_highest_control(pass28_subjects),
            "pass35_best_brux_minus_highest_control": best_brux_minus_highest_control(pass35_subjects),
        },
        "warnings": warnings,
        "summary_json_path": str(summary_json_path.resolve()),
        "summary_md_path": str(summary_md_path.resolve()),
    }

    summary_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_markdown(report), encoding="utf-8")
    print(summary_md_path)
    print(summary_json_path)


if __name__ == "__main__":
    main()
