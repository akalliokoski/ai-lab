from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from audit_percentile_band_channel_gap import select_feature_columns
from run_pass36_record_relative_shape_composition_audit import load_subjects, summarize_counts
from run_pass41_event_conditioned_feature_block_audit import (
    BASE_EXCLUDE_REGEXES,
    EVENT_CONFIG,
    EVENT_FEATURES,
    ROW_ID_COLUMNS,
    SUBJECT_IDS,
    best_brux_minus_highest_control,
    build_subject_rows,
    load_event_features,
)

PASS_NUMBER = 43
EXPERIMENT = "matched_a1_vs_a3_transfer_audit_for_fixed_pass42_event_subset"
PRIMARY_OBJECTIVE = "test whether the verified pass42 3-feature event subset transfers from repaired A1-only EMG to the closest matched A3-only EMG surface"
PASS42_EVENT_SUBSET = [
    "evt_active_fraction",
    "evt_burst_duration_median_s",
    "evt_interburst_gap_median_s",
]
PROJECT_PYTHON = Path(__file__).resolve().parents[3] / ".venv/bin/python"


def run_train_baseline(*, features_csv: Path, out_json: Path, exclude_patterns: list[str]) -> dict[str, Any]:
    python_exe = PROJECT_PYTHON if PROJECT_PYTHON.exists() else Path(sys.executable)
    cmd = [
        str(python_exe),
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
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    return json.loads(out_json.read_text(encoding="utf-8"))


def get_subject_scores(subjects: dict[str, dict[str, Any]]) -> dict[str, float]:
    return {subject_id: float(subjects[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS}


def build_exclude_patterns() -> list[str]:
    excludes = list(BASE_EXCLUDE_REGEXES)
    for feature in EVENT_FEATURES:
        if feature not in PASS42_EVENT_SUBSET:
            excludes.append(f"^{feature}$")
    return excludes


def build_pass43_a3_table(*, pass14_df: pd.DataFrame, root: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    event_df, event_reference = load_event_features(pass14_df, root=root)
    merge_keys = ["subject_id", "start_s", "end_s", "window_index"]
    subset_event_df = event_df[merge_keys + PASS42_EVENT_SUBSET].copy()
    merged = pass14_df.merge(subset_event_df, on=merge_keys, how="left", validate="one_to_one")
    null_counts = {feature: int(merged[feature].isnull().sum()) for feature in PASS42_EVENT_SUBSET}
    if any(count > 0 for count in null_counts.values()):
        raise SystemExit(f"pass43 A3 event merge left nulls: {null_counts}")

    if "time_match_rank" not in merged.columns:
        merged = merged.sort_values(["subject_id", "start_s", "end_s", "window_index"]).copy()
        merged["time_match_rank"] = merged.groupby("subject_id").cumcount() + 1
    if "relative_time_quantile" not in merged.columns:
        counts = merged.groupby("subject_id")["time_match_rank"].transform("max")
        merged["relative_time_quantile"] = (merged["time_match_rank"] - 0.5) / counts

    return merged, {
        "event_reference_by_subject": event_reference,
        "event_merge_keys": merge_keys,
        "event_null_counts_after_merge": null_counts,
        "appended_event_subset": PASS42_EVENT_SUBSET,
        "derived_time_metadata": {
            "time_match_rank": "per-subject rank by start_s/end_s/window_index added because pass14 matched14 table lacked this column",
            "relative_time_quantile": "(time_match_rank - 0.5) / subject_window_count added because pass14 matched14 table lacked this column",
        },
    }


def compare_subject_sets(left: pd.DataFrame, right: pd.DataFrame) -> list[str]:
    warnings: list[str] = []
    left_subjects = sorted(left["subject_id"].unique().tolist())
    right_subjects = sorted(right["subject_id"].unique().tolist())
    if left_subjects != right_subjects:
        warnings.append(f"subject sets differ: left={left_subjects} right={right_subjects}")
    left_channel = sorted(left["channel"].dropna().astype(str).unique().tolist())
    right_channel = sorted(right["channel"].dropna().astype(str).unique().tolist())
    if left_channel != right_channel:
        warnings.append(f"channels differ: left={left_channel} right={right_channel}")
    return warnings


def build_subject_comparison_rows(
    *,
    pass14_subjects: dict[str, Any],
    pass42_subjects: dict[str, Any],
    pass43_subjects: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for subject_id in SUBJECT_IDS:
        rows.append(
            {
                "subject_id": subject_id,
                "pass14_score": float(pass14_subjects[subject_id]["mean_score"]),
                "pass42_a1_score": float(pass42_subjects[subject_id]["mean_score"]),
                "pass43_a3_score": float(pass43_subjects[subject_id]["mean_score"]),
                "delta_pass43_vs_pass14": float(pass43_subjects[subject_id]["mean_score"] - pass14_subjects[subject_id]["mean_score"]),
                "delta_pass43_vs_pass42": float(pass43_subjects[subject_id]["mean_score"] - pass42_subjects[subject_id]["mean_score"]),
                "pass14_predicted_label": pass14_subjects[subject_id]["predicted_label"],
                "pass42_predicted_label": pass42_subjects[subject_id]["predicted_label"],
                "pass43_predicted_label": pass43_subjects[subject_id]["predicted_label"],
            }
        )
    return rows


def render_subject_rows(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{row['subject_id']}`: pass14 A3 `{row['pass14_score']:.3f}` -> pass42 A1 `{row['pass42_a1_score']:.3f}` -> pass43 A3 `{row['pass43_a3_score']:.3f}` | "
        f"delta pass43 vs pass14 `{row['delta_pass43_vs_pass14']:+.3f}` | delta pass43 vs pass42 `{row['delta_pass43_vs_pass42']:+.3f}` | "
        f"predicted pass14 `{row['pass14_predicted_label']}` -> pass42 `{row['pass42_predicted_label']}` -> pass43 `{row['pass43_predicted_label']}`"
        for row in rows
    )


def render_feature_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- none"
    return "\n".join(
        f"- `{row['feature']}` contribution delta `{row['mean_contribution_delta']:+.3f}` | z-mean delta `{row['z_mean_delta']:+.3f}` | raw-mean delta `{row['raw_mean_delta']:+.6f}`"
        for row in rows
    )


def build_pairwise_gap(
    subjects: dict[str, Any],
    feature_columns: list[str],
    block_features: dict[str, list[str]],
    *,
    higher_subject: str,
    lower_subject: str = "brux1",
) -> dict[str, Any]:
    feature_rows = []
    for feature in feature_columns:
        higher = subjects[higher_subject]["feature_means"][feature]
        lower = subjects[lower_subject]["feature_means"][feature]
        if feature in block_features["shape"]:
            block = "shape"
        elif feature in block_features["amp_disp"]:
            block = "amp_disp"
        elif feature in block_features["event"]:
            block = "event"
        else:
            block = "other"
        feature_rows.append(
            {
                "feature": feature,
                "mean_contribution_delta": float(higher["mean_contribution"] - lower["mean_contribution"]),
                "raw_mean_delta": float(higher["raw_mean"] - lower["raw_mean"]),
                "z_mean_delta": float(higher["z_mean"] - lower["z_mean"]),
                "block": block,
            }
        )
    feature_rows.sort(key=lambda row: abs(row["mean_contribution_delta"]), reverse=True)
    block_sums = {
        block: float(sum(row["mean_contribution_delta"] for row in feature_rows if row["block"] == block))
        for block in ["amp_disp", "shape", "event", "other"]
    }
    return {
        "score_gap": float(subjects[higher_subject]["mean_score"] - subjects[lower_subject]["mean_score"]),
        "block_sums": block_sums,
        "top_positive": [row for row in feature_rows if row["mean_contribution_delta"] > 0][:10],
        "top_negative": [row for row in feature_rows if row["mean_contribution_delta"] < 0][:10],
        "event_positive": [
            row for row in feature_rows if row["block"] == "event" and row["mean_contribution_delta"] > 0
        ][:7],
        "event_negative": [
            row for row in feature_rows if row["block"] == "event" and row["mean_contribution_delta"] < 0
        ][:7],
    }


def classify_transfer(*, pass42_subjects: dict[str, Any], pass43_subjects: dict[str, Any]) -> str:
    a1_brux1 = float(pass42_subjects["brux1"]["mean_score"])
    a3_brux1 = float(pass43_subjects["brux1"]["mean_score"])
    if a3_brux1 >= a1_brux1 - 0.02:
        return "holds"
    if a3_brux1 >= 0.5 * a1_brux1:
        return "weakens"
    return "collapses"


def classify_overall_transfer(*, pass42_summary: dict[str, Any], pass43_summary: dict[str, Any]) -> str:
    if (
        pass43_summary["sensitivity"] >= pass42_summary["sensitivity"]
        and pass43_summary["balanced_accuracy"] >= pass42_summary["balanced_accuracy"] - 0.05
    ):
        return "holds"
    if pass43_summary["sensitivity"] > 0 or pass43_summary["balanced_accuracy"] >= 0.6:
        return "weakens"
    return "collapses"


def render_markdown(report: dict[str, Any]) -> str:
    pass14_summary = report["anchors"]["pass14_a3_baseline"]["subject_summary"]
    pass42_summary = report["anchors"]["pass42_a1_verified_subset"]["subject_summary"]
    pass43_summary = report["pass43_a3_transfer"]["subject_summary"]
    pair_n3 = report["pass43_a3_transfer"]["pairwise"]["n3_minus_brux1"]
    pair_n5 = report["pass43_a3_transfer"]["pairwise"]["n5_minus_brux1"]
    pair_n11 = report["pass43_a3_transfer"]["pairwise"]["n11_minus_brux1"]
    transfer_status = report["derived"]["brux1_transfer_status"]
    overall_status = report["derived"]["overall_transfer_status"]
    if overall_status == "holds":
        transfer_verdict = "The fixed pass42 event subset broadly transfers on the matched A3 surface: brux1 stays near the repaired A1 score and the honest subject-level verdict also stays competitive."
        next_step = "Keep the same 3-feature event subset fixed and rebuild the A3 comparison on the repaired percentile-band/time-matched scaffold before any broader feature or model change."
    elif overall_status == "weakens":
        transfer_verdict = "The fixed pass42 event subset weakens on the matched A3 surface: some event-signal behavior survives, but the honest subject-level verdict slips enough that one scaffold-parity rebuild is still needed before drawing a family-level conclusion."
        next_step = "Keep the subset fixed and run one bounded scaffold-parity rebuild for A3-only on the repaired percentile-band/time-aware EMG path so the next comparison changes scaffold less than this pass did."
    else:
        transfer_verdict = "The fixed pass42 event subset does not transfer honestly on the matched A3 surface: brux1 itself roughly holds, but subject-level sensitivity collapses back to zero and the overall A3 surface remains below the repaired A1 result."
        next_step = "Do not broaden the feature family. Keep the same 3-feature subset fixed and rebuild only the A3-only table on the repaired percentile-band/time-aware EMG scaffold to separate family-transfer failure from old-surface mismatch."

    return f"""# Pass 43 — matched A1-vs-A3 transfer audit for the verified pass42 event subset

Date: 2026-05-05
Status: bounded transfer audit completed. This pass keeps the verified pass42 3-feature event subset fixed, reuses the repaired A1-only pass42 result as the source anchor, appends the same subset onto the closest existing matched A3-only EMG surface, and compares subject-level LOSO behavior without changing model family.

## Exact implementation path
- fixed pass42 subset carried over unchanged: `{', '.join(PASS42_EVENT_SUBSET)}`
- repaired A1 anchor reused directly from `projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv` plus the saved pass42 LOSO report
- closest matched A3 surface started from `projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv`
- new work in this pass: recompute only the same three event features for each existing pass14 A3 row, merge them onto that saved matched14 table, then rerun `train_baseline.py --cv loso` with the same base regex exclusions and no broader feature changes
- unchanged base train-time exclusions: `{BASE_EXCLUDE_REGEXES}`
- additional dropped pass41 event features not kept in this transfer audit: `{report['pass43_a3_transfer']['dropped_event_features']}`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass43_matched_a1_vs_a3_transfer_audit.py`
- New pass43 A3 feature table: `projects/bruxism-cap/data/window_features_pass43_emg_s2_mcap_a3_only_matched14_eventsubset.csv`
- New pass43 A3 LOSO report: `projects/bruxism-cap/reports/loso-cv-pass43-emg-a3-matched14-eventsubset.json`
- Summary JSON: `projects/bruxism-cap/reports/pass43-matched-a1-vs-a3-transfer-audit.json`
- Summary report: `projects/bruxism-cap/reports/pass43-matched-a1-vs-a3-transfer-audit.md`

## Verified counts and parity checks
- repaired A1 pass42 counts by subject: `{report['anchors']['pass42_a1_verified_subset']['counts_by_subject']}`
- matched A3 pass14 baseline counts by subject: `{report['anchors']['pass14_a3_baseline']['counts_by_subject']}`
- matched A3 pass43 counts by subject: `{report['pass43_a3_transfer']['counts_by_subject']}`
- shared subjects: `{report['derived']['shared_subjects']}`
- A1 channel(s): `{report['anchors']['pass42_a1_verified_subset']['channels']}`
- A3 channel(s): `{report['pass43_a3_transfer']['channels']}`
- event merge keys: `{report['pass43_a3_transfer']['event_merge_keys']}`
- event null counts after A3 merge: `{report['pass43_a3_transfer']['event_null_counts_after_merge']}`
- parity warnings: `{report['warnings']}`

## Apples-to-apples subject-level comparison of the fixed subset
- pass14 A3 baseline balanced accuracy: `{pass14_summary['balanced_accuracy']:.3f}`
- pass42 A1 fixed-subset balanced accuracy: `{pass42_summary['balanced_accuracy']:.3f}`
- pass43 A3 fixed-subset balanced accuracy: `{pass43_summary['balanced_accuracy']:.3f}`
- pass14 A3 baseline sensitivity: `{pass14_summary['sensitivity']:.3f}`
- pass42 A1 fixed-subset sensitivity: `{pass42_summary['sensitivity']:.3f}`
- pass43 A3 fixed-subset sensitivity: `{pass43_summary['sensitivity']:.3f}`
- pass14 A3 baseline specificity: `{pass14_summary['specificity']:.3f}`
- pass42 A1 fixed-subset specificity: `{pass42_summary['specificity']:.3f}`
- pass43 A3 fixed-subset specificity: `{pass43_summary['specificity']:.3f}`
- pass14 A3 baseline best-bruxism-minus-highest-control margin: `{report['derived']['pass14_best_brux_minus_highest_control']:+.3f}`
- pass42 A1 fixed-subset best-bruxism-minus-highest-control margin: `{report['derived']['pass42_best_brux_minus_highest_control']:+.3f}`
- pass43 A3 fixed-subset best-bruxism-minus-highest-control margin: `{report['derived']['pass43_best_brux_minus_highest_control']:+.3f}`

Subject score deltas:
{render_subject_rows(report['derived']['subject_score_rows'])}

## Did brux1 improve, hold, or collapse on A3?
- `brux1`: pass14 A3 baseline `{report['anchors']['pass14_a3_baseline']['subjects_scores']['brux1']:.3f}` -> pass42 repaired A1 subset `{report['anchors']['pass42_a1_verified_subset']['subjects_scores']['brux1']:.3f}` -> pass43 A3 subset `{report['pass43_a3_transfer']['subjects_scores']['brux1']:.3f}`
- `brux2`: pass14 A3 baseline `{report['anchors']['pass14_a3_baseline']['subjects_scores']['brux2']:.3f}` -> pass42 repaired A1 subset `{report['anchors']['pass42_a1_verified_subset']['subjects_scores']['brux2']:.3f}` -> pass43 A3 subset `{report['pass43_a3_transfer']['subjects_scores']['brux2']:.3f}`
- highest A3 control after transfer: `{report['derived']['pass43_highest_control_subject']}` at `{report['derived']['pass43_highest_control_score']:.3f}`
- pass43 `brux1 - highest_control`: `{report['derived']['pass43_brux1_minus_highest_control']:+.3f}`
- pass43 `brux1 - n3`: `{report['derived']['pass43_brux1_minus_n3']:+.3f}`
- transfer status: `{transfer_status}`
- overall honest transfer verdict: `{overall_status}`
- verdict: {transfer_verdict}

## A3 control-side contributors against `brux1` on the fixed subset transfer run
### `n3 - brux1`
- block sums: amp/disp `{pair_n3['block_sums']['amp_disp']:+.3f}` | shape `{pair_n3['block_sums']['shape']:+.3f}` | event `{pair_n3['block_sums']['event']:+.3f}` | other `{pair_n3['block_sums']['other']:+.3f}`
- positive event deltas:
{render_feature_rows(pair_n3['event_positive'])}
- negative event deltas:
{render_feature_rows(pair_n3['event_negative'])}

### `n5 - brux1`
- block sums: amp/disp `{pair_n5['block_sums']['amp_disp']:+.3f}` | shape `{pair_n5['block_sums']['shape']:+.3f}` | event `{pair_n5['block_sums']['event']:+.3f}` | other `{pair_n5['block_sums']['other']:+.3f}`
- positive event deltas:
{render_feature_rows(pair_n5['event_positive'])}
- negative event deltas:
{render_feature_rows(pair_n5['event_negative'])}

### `n11 - brux1`
- block sums: amp/disp `{pair_n11['block_sums']['amp_disp']:+.3f}` | shape `{pair_n11['block_sums']['shape']:+.3f}` | event `{pair_n11['block_sums']['event']:+.3f}` | other `{pair_n11['block_sums']['other']:+.3f}`
- positive event deltas:
{render_feature_rows(pair_n11['event_positive'])}
- negative event deltas:
{render_feature_rows(pair_n11['event_negative'])}

## Safest next bounded step
{next_step}
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    reports_dir = root / "reports"

    pass41_a1_features = data_dir / "window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv"
    pass14_a3_features = data_dir / "window_features_pass14_emg_s2_mcap_a3_only_matched14.csv"
    pass42_report_path = reports_dir / "loso-cv-pass42-emg-a1-pct10-90-record-relative-shape-eventblock-subset.json"
    pass14_report_path = reports_dir / "loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json"
    pass43_features_path = data_dir / "window_features_pass43_emg_s2_mcap_a3_only_matched14_eventsubset.csv"
    pass43_report_path = reports_dir / "loso-cv-pass43-emg-a3-matched14-eventsubset.json"
    summary_json_path = reports_dir / "pass43-matched-a1-vs-a3-transfer-audit.json"
    summary_md_path = reports_dir / "pass43-matched-a1-vs-a3-transfer-audit.md"

    exclude_patterns = build_exclude_patterns()
    pass41_a1_df = pd.read_csv(pass41_a1_features)
    pass14_a3_df = pd.read_csv(pass14_a3_features)
    pass42_report = json.loads(pass42_report_path.read_text(encoding="utf-8"))
    pass14_report = json.loads(pass14_report_path.read_text(encoding="utf-8"))

    pass43_a3_df, merge_summary = build_pass43_a3_table(pass14_df=pass14_a3_df, root=root)
    pass43_features_path.parent.mkdir(parents=True, exist_ok=True)
    pass43_a3_df.to_csv(pass43_features_path, index=False)
    pass43_report = run_train_baseline(features_csv=pass43_features_path, out_json=pass43_report_path, exclude_patterns=exclude_patterns)

    warnings = compare_subject_sets(pass41_a1_df, pass43_a3_df)
    if len(pass41_a1_df) != len(pass43_a3_df):
        warnings.append(
            f"row counts differ across compared surfaces: repaired A1 rows={len(pass41_a1_df)} matched A3 rows={len(pass43_a3_df)}"
        )

    pass42_subjects = load_subjects(pass42_report)
    pass14_subjects = load_subjects(pass14_report)
    pass43_subjects = load_subjects(pass43_report)

    pass42_feature_columns, pass42_selection_excluded = select_feature_columns(pass41_a1_df, exclude_patterns=exclude_patterns)
    pass43_feature_columns, pass43_selection_excluded = select_feature_columns(pass43_a3_df, exclude_patterns=exclude_patterns)

    pass42_subjects_audit, pass42_blocks = build_subject_rows(pass41_a1_df, pass42_feature_columns)
    pass43_subjects_audit, pass43_blocks = build_subject_rows(pass43_a3_df, pass43_feature_columns)
    pass43_pairwise = {
        "n3_minus_brux1": build_pairwise_gap(pass43_subjects_audit, pass43_feature_columns, pass43_blocks, higher_subject="n3"),
        "n5_minus_brux1": build_pairwise_gap(pass43_subjects_audit, pass43_feature_columns, pass43_blocks, higher_subject="n5"),
        "n11_minus_brux1": build_pairwise_gap(pass43_subjects_audit, pass43_feature_columns, pass43_blocks, higher_subject="n11"),
    }

    pass43_highest_control_subject = max(
        ["n3", "n5", "n11"], key=lambda subject_id: pass43_subjects[subject_id]["mean_score"]
    )

    report = {
        "pass": PASS_NUMBER,
        "experiment": EXPERIMENT,
        "objective": PRIMARY_OBJECTIVE,
        "anchors": {
            "pass42_a1_verified_subset": {
                "features_csv": str(pass41_a1_features.resolve()),
                "report_path": str(pass42_report_path.resolve()),
                "subject_summary": pass42_report["models"]["logreg"]["subject_aggregation"]["summary"],
                "subjects": pass42_subjects,
                "subjects_scores": get_subject_scores(pass42_subjects),
                "counts_by_subject": summarize_counts(pass41_a1_df),
                "channels": sorted(pass41_a1_df["channel"].dropna().astype(str).unique().tolist()),
                "selection_excluded_columns": pass42_selection_excluded,
                "feature_columns": pass42_feature_columns,
                "selected_event_subset": PASS42_EVENT_SUBSET,
            },
            "pass14_a3_baseline": {
                "features_csv": str(pass14_a3_features.resolve()),
                "report_path": str(pass14_report_path.resolve()),
                "subject_summary": pass14_report["models"]["logreg"]["subject_aggregation"]["summary"],
                "subjects": pass14_subjects,
                "subjects_scores": get_subject_scores(pass14_subjects),
                "counts_by_subject": summarize_counts(pass14_a3_df),
                "channels": sorted(pass14_a3_df["channel"].dropna().astype(str).unique().tolist()),
            },
        },
        "pass43_a3_transfer": {
            "features_csv": str(pass43_features_path.resolve()),
            "report_path": str(pass43_report_path.resolve()),
            "subject_summary": pass43_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "subjects": pass43_subjects,
            "subjects_scores": get_subject_scores(pass43_subjects),
            "counts_by_subject": summarize_counts(pass43_a3_df),
            "channels": sorted(pass43_a3_df["channel"].dropna().astype(str).unique().tolist()),
            "selection_excluded_columns": pass43_selection_excluded,
            "feature_columns": pass43_feature_columns,
            "subjects_audit": pass43_subjects_audit,
            "blocks": pass43_blocks,
            "pairwise": pass43_pairwise,
            "appended_event_subset": PASS42_EVENT_SUBSET,
            "dropped_event_features": [feature for feature in EVENT_FEATURES if feature not in PASS42_EVENT_SUBSET],
            **merge_summary,
        },
        "event_config": EVENT_CONFIG,
        "warnings": warnings,
        "derived": {
            "shared_subjects": sorted(pass41_a1_df["subject_id"].dropna().astype(str).unique().tolist()),
            "subject_score_rows": build_subject_comparison_rows(
                pass14_subjects=pass14_subjects,
                pass42_subjects=pass42_subjects,
                pass43_subjects=pass43_subjects,
            ),
            "pass14_best_brux_minus_highest_control": best_brux_minus_highest_control(pass14_subjects),
            "pass42_best_brux_minus_highest_control": best_brux_minus_highest_control(pass42_subjects),
            "pass43_best_brux_minus_highest_control": best_brux_minus_highest_control(pass43_subjects),
            "pass43_highest_control_subject": pass43_highest_control_subject,
            "pass43_highest_control_score": float(pass43_subjects[pass43_highest_control_subject]["mean_score"]),
            "pass43_brux1_minus_highest_control": float(
                pass43_subjects["brux1"]["mean_score"] - pass43_subjects[pass43_highest_control_subject]["mean_score"]
            ),
            "pass43_brux1_minus_n3": float(pass43_subjects["brux1"]["mean_score"] - pass43_subjects["n3"]["mean_score"]),
            "brux1_transfer_status": classify_transfer(pass42_subjects=pass42_subjects, pass43_subjects=pass43_subjects),
            "overall_transfer_status": classify_overall_transfer(
                pass42_summary=pass42_report["models"]["logreg"]["subject_aggregation"]["summary"],
                pass43_summary=pass43_report["models"]["logreg"]["subject_aggregation"]["summary"],
            ),
        },
        "summary_md_path": str(summary_md_path.resolve()),
        "summary_json_path": str(summary_json_path.resolve()),
    }

    summary_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_markdown(report), encoding="utf-8")
    print(summary_md_path)
    print(summary_json_path)
    print(pass43_report_path)
    print(pass43_features_path)


if __name__ == "__main__":
    main()
