from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from audit_percentile_band_channel_gap import load_feature_frame, select_feature_columns
from run_pass34_record_relative_emg_audit import (
    BASE_EXCLUDE_REGEXES,
    EPSILON,
    RELATIVE_FEATURES,
    build_record_relative_table,
)
from run_pass35_shape_feature_expansion import SUBJECTS
from run_pass36_record_relative_shape_composition_audit import (
    best_brux_minus_highest_control,
    load_subjects,
    summarize_counts,
)
from run_pass41_event_conditioned_feature_block_audit import (
    EVENT_CONFIG,
    EVENT_FEATURES,
    SUBJECT_IDS,
    build_subject_rows,
    load_event_features,
)
from run_pass43_matched_a1_vs_a3_transfer_audit import build_pairwise_gap

PASS_NUMBER = 44
EXPERIMENT = "repaired_a3_only_scaffold_rebuild_with_fixed_pass42_event_subset"
PRIMARY_OBJECTIVE = (
    "test whether the fixed pass42 3-feature event subset improves honest A3-only subject transfer "
    "once rebuilt on the repaired percentile-band/time-aware scaffold"
)
PASS42_EVENT_SUBSET = [
    "evt_active_fraction",
    "evt_burst_duration_median_s",
    "evt_interburst_gap_median_s",
]
PROJECT_PYTHON = Path(__file__).resolve().parents[3] / ".venv/bin/python"
ROW_ID_COLUMNS = ["subject_id", "start_s", "end_s", "window_index"]


def python_executable() -> Path:
    return PROJECT_PYTHON if PROJECT_PYTHON.exists() else Path(sys.executable)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def run_prepare_windows_a3(*, root: Path, out_csv: Path) -> None:
    if out_csv.exists():
        out_csv.unlink()
    script = Path(__file__).with_name("prepare_windows.py")
    raw_dir = root / "data" / "raw" / "capslpdb"
    py = str(python_executable())
    for index, (subject_id, label) in enumerate(SUBJECTS):
        cmd = [
            py,
            str(script),
            "--edf",
            str(raw_dir / f"{subject_id}.edf"),
            "--annotation-txt",
            str(raw_dir / f"{subject_id}.txt"),
            "--annotation-events",
            "SLEEP-S2",
            "--require-overlap-events",
            "MCAP-A3",
            "--exclude-overlap-events",
            "MCAP-A1,MCAP-A2",
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
        str(python_executable()),
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


def build_exclude_patterns() -> list[str]:
    excludes = list(BASE_EXCLUDE_REGEXES)
    for feature in EVENT_FEATURES:
        if feature not in PASS42_EVENT_SUBSET:
            excludes.append(f"^{feature}$")
    return excludes


def ensure_time_metadata(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()
    sort_cols = [col for col in ["subject_id", "start_s", "end_s", "window_index"] if col in enriched.columns]
    enriched = enriched.sort_values(sort_cols).reset_index(drop=True)
    if "time_match_rank" not in enriched.columns:
        enriched["time_match_rank"] = enriched.groupby("subject_id").cumcount() + 1
    if "relative_time_quantile" not in enriched.columns:
        counts = enriched.groupby("subject_id")["time_match_rank"].transform("max")
        enriched["relative_time_quantile"] = (enriched["time_match_rank"] - 0.5) / counts
    return enriched


def build_pass44_repaired_a3_table(*, selected_a3_df: pd.DataFrame, event_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    selected_with_time = ensure_time_metadata(selected_a3_df)
    record_relative_df, record_relative_summary = build_record_relative_table(
        selected_with_time,
        relative_features=RELATIVE_FEATURES,
        epsilon=EPSILON,
    )
    subset_event_df = event_df[ROW_ID_COLUMNS + PASS42_EVENT_SUBSET].copy()
    merged = record_relative_df.merge(subset_event_df, on=ROW_ID_COLUMNS, how="left", validate="one_to_one")
    null_counts = {feature: int(merged[feature].isnull().sum()) for feature in PASS42_EVENT_SUBSET}
    if any(count > 0 for count in null_counts.values()):
        raise SystemExit(f"pass44 repaired A3 event merge left nulls: {null_counts}")
    return merged, {
        "record_relative": record_relative_summary,
        "event_merge_keys": ROW_ID_COLUMNS,
        "event_null_counts_after_merge": null_counts,
        "appended_event_subset": PASS42_EVENT_SUBSET,
    }


def get_subject_scores(subjects: dict[str, dict[str, Any]]) -> dict[str, float]:
    return {subject_id: float(subjects[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS}


def build_subject_comparison_rows(
    *,
    pass42_subjects: dict[str, Any],
    pass43_subjects: dict[str, Any],
    pass44_subjects: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for subject_id in SUBJECT_IDS:
        rows.append(
            {
                "subject_id": subject_id,
                "pass42_a1_score": float(pass42_subjects[subject_id]["mean_score"]),
                "pass43_old_a3_score": float(pass43_subjects[subject_id]["mean_score"]),
                "pass44_repaired_a3_score": float(pass44_subjects[subject_id]["mean_score"]),
                "delta_pass44_vs_pass42": float(pass44_subjects[subject_id]["mean_score"] - pass42_subjects[subject_id]["mean_score"]),
                "delta_pass44_vs_pass43": float(pass44_subjects[subject_id]["mean_score"] - pass43_subjects[subject_id]["mean_score"]),
                "pass42_predicted_label": pass42_subjects[subject_id]["predicted_label"],
                "pass43_predicted_label": pass43_subjects[subject_id]["predicted_label"],
                "pass44_predicted_label": pass44_subjects[subject_id]["predicted_label"],
            }
        )
    return rows


def render_subject_rows(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{row['subject_id']}`: pass42 repaired A1 `{row['pass42_a1_score']:.3f}` -> "
        f"pass43 old-surface A3 `{row['pass43_old_a3_score']:.3f}` -> pass44 repaired-surface A3 `{row['pass44_repaired_a3_score']:.3f}` | "
        f"delta pass44 vs pass42 `{row['delta_pass44_vs_pass42']:+.3f}` | "
        f"delta pass44 vs pass43 `{row['delta_pass44_vs_pass43']:+.3f}` | "
        f"predicted pass42 `{row['pass42_predicted_label']}` -> pass43 `{row['pass43_predicted_label']}` -> pass44 `{row['pass44_predicted_label']}`"
        for row in rows
    )


def render_feature_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- none"
    return "\n".join(
        f"- `{row['feature']}` contribution delta `{row['mean_contribution_delta']:+.3f}` | "
        f"z-mean delta `{row['z_mean_delta']:+.3f}` | raw-mean delta `{row['raw_mean_delta']:+.6f}`"
        for row in rows
    )


def choose_verdict(*, pass42_summary: dict[str, Any], pass44_summary: dict[str, Any], pass42_margin: float, pass44_margin: float) -> str:
    if (
        pass44_summary["sensitivity"] >= pass42_summary["sensitivity"]
        and pass44_summary["balanced_accuracy"] >= pass42_summary["balanced_accuracy"]
        and pass44_margin >= 0
    ):
        return "scaffold mismatch was the main blocker"
    return "the subset still fails honestly even on the repaired A3-only surface"


def render_markdown(report: dict[str, Any]) -> str:
    pass42_summary = report["anchors"]["pass42_repaired_a1"]["subject_summary"]
    pass43_summary = report["anchors"]["pass43_old_surface_a3"]["subject_summary"]
    pass44_summary = report["pass44_repaired_a3"]["subject_summary"]
    pair_n3 = report["pass44_repaired_a3"]["pairwise"]["n3_minus_brux1"]
    pair_n11 = report["pass44_repaired_a3"]["pairwise"]["n11_minus_brux1"]
    verdict = report["derived"]["verdict"]
    return f"""# Pass 44 — repaired A3-only scaffold rebuild with the fixed pass42 event subset

Date: 2026-05-05
Status: bounded scaffold-rebuild test completed. This pass keeps the verified five-subject set, `EMG1-EMG2`, `logreg` LOSO, the pass42 event subset, and the base train-time exclusions fixed while rebuilding `A3-only` on the repaired percentile-band / time-aware scaffold instead of the old matched14 surface.

## Exact implementation path
- fixed pass42 subset carried over unchanged: `{', '.join(PASS42_EVENT_SUBSET)}`
- rebuilt the exclusive `SLEEP-S2 + MCAP-A3-only` full `EMG1-EMG2` pool from raw EDF windows with the current feature extractor so the repaired A3 branch includes the same compact shape descriptors used by the active pass36/pass41/pass42 backbone
- re-applied the repaired percentile-band selector in time-aware mode: `cap=10`, `lower_quantile=0.10`, `upper_quantile=0.90`
- applied the same pass34 within-record robust transform only to the retained record-relative feature family: `{', '.join(report['pass44_repaired_a3']['record_relative']['relative_features_applied'])}`
- appended only the fixed three event features by row key merge: `{report['pass44_repaired_a3']['event_merge_keys']}`
- reran `train_baseline.py --cv loso` with unchanged base exclusions `{BASE_EXCLUDE_REGEXES}` plus regex drops for the four pass41 event terms not kept in pass42/pass44

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass44_repaired_a3_event_subset_rebuild.py`
- Full rebuilt A3 feature pool: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_full_envelope_shape.csv`
- Percentile-band selector report: `projects/bruxism-cap/reports/time-position-match-pass44-emg-a3-pct10-90-shape.json`
- Intermediate repaired A3 selected table: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_shape.csv`
- Final repaired A3 event-subset table: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_record_relative_shape_eventsubset.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass44-emg-a3-pct10-90-record-relative-shape-eventsubset.json`
- Summary JSON: `projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.json`
- Summary memo: `projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.md`

## Scaffold checks: old A3 surface versus repaired A3 surface
- pass42 repaired A1 counts by subject: `{report['anchors']['pass42_repaired_a1']['counts_by_subject']}` | total rows `{report['anchors']['pass42_repaired_a1']['row_count']}`
- pass43 old-surface A3 counts by subject: `{report['anchors']['pass43_old_surface_a3']['counts_by_subject']}` | total rows `{report['anchors']['pass43_old_surface_a3']['row_count']}`
- pass44 rebuilt full A3 counts by subject: `{report['pass44_rebuild']['full_counts_by_subject']}` | total rows `{report['pass44_rebuild']['full_row_count']}`
- pass44 repaired selected A3 counts by subject: `{report['pass44_rebuild']['selected_counts_by_subject']}` | total rows `{report['pass44_rebuild']['selected_row_count']}`
- pass44 final repaired A3 counts by subject: `{report['pass44_repaired_a3']['counts_by_subject']}` | total rows `{report['pass44_repaired_a3']['row_count']}`
- selector mode: `{report['pass44_rebuild']['selector']['match_mode']}` with percentile band `{report['pass44_rebuild']['selector']['percentile_band']}`
- event null counts after repaired A3 merge: `{report['pass44_repaired_a3']['event_null_counts_after_merge']}`
- pass44 channels: `{report['pass44_repaired_a3']['channels']}`

## Subject-level comparison: pass42 repaired A1 vs pass43 old-surface A3 vs pass44 repaired-surface A3
- balanced accuracy: pass42 `{pass42_summary['balanced_accuracy']:.3f}` | pass43 `{pass43_summary['balanced_accuracy']:.3f}` | pass44 `{pass44_summary['balanced_accuracy']:.3f}`
- sensitivity: pass42 `{pass42_summary['sensitivity']:.3f}` | pass43 `{pass43_summary['sensitivity']:.3f}` | pass44 `{pass44_summary['sensitivity']:.3f}`
- specificity: pass42 `{pass42_summary['specificity']:.3f}` | pass43 `{pass43_summary['specificity']:.3f}` | pass44 `{pass44_summary['specificity']:.3f}`
- best-bruxism-minus-highest-control margin: pass42 `{report['derived']['pass42_best_brux_minus_highest_control']:+.3f}` | pass43 `{report['derived']['pass43_best_brux_minus_highest_control']:+.3f}` | pass44 `{report['derived']['pass44_best_brux_minus_highest_control']:+.3f}`
- highest control on pass44: `{report['derived']['pass44_highest_control_subject']}` at `{report['derived']['pass44_highest_control_score']:.3f}`
- pass44 `brux1 - n3`: `{report['derived']['pass44_brux1_minus_n3']:+.3f}`

Subject score rows:
{render_subject_rows(report['derived']['subject_score_rows'])}

## Fixed-subset contributor checks on the repaired A3 surface
### `n3 - brux1`
- block sums: amp/disp `{pair_n3['block_sums']['amp_disp']:+.3f}` | shape `{pair_n3['block_sums']['shape']:+.3f}` | event `{pair_n3['block_sums']['event']:+.3f}` | other `{pair_n3['block_sums']['other']:+.3f}`
- positive event deltas:
{render_feature_rows(pair_n3['event_positive'])}
- negative event deltas:
{render_feature_rows(pair_n3['event_negative'])}

### `n11 - brux1`
- block sums: amp/disp `{pair_n11['block_sums']['amp_disp']:+.3f}` | shape `{pair_n11['block_sums']['shape']:+.3f}` | event `{pair_n11['block_sums']['event']:+.3f}` | other `{pair_n11['block_sums']['other']:+.3f}`
- positive event deltas:
{render_feature_rows(pair_n11['event_positive'])}
- negative event deltas:
{render_feature_rows(pair_n11['event_negative'])}

## Verdict
{verdict}.
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    reports_dir = root / "reports"

    full_features_path = data_dir / "window_features_pass44_emg_s2_mcap_a3_only_full_envelope_shape.csv"
    selected_shape_path = data_dir / "window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_shape.csv"
    selector_json_path = reports_dir / "time-position-match-pass44-emg-a3-pct10-90-shape.json"
    pass44_features_path = data_dir / "window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_record_relative_shape_eventsubset.csv"
    pass44_report_path = reports_dir / "loso-cv-pass44-emg-a3-pct10-90-record-relative-shape-eventsubset.json"
    summary_json_path = reports_dir / "pass44-repaired-a3-event-subset-rebuild.json"
    summary_md_path = reports_dir / "pass44-repaired-a3-event-subset-rebuild.md"

    pass42_report_path = reports_dir / "loso-cv-pass42-emg-a1-pct10-90-record-relative-shape-eventblock-subset.json"
    pass43_report_path = reports_dir / "loso-cv-pass43-emg-a3-matched14-eventsubset.json"
    pass41_a1_features = data_dir / "window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv"
    pass43_old_a3_features = data_dir / "window_features_pass43_emg_s2_mcap_a3_only_matched14_eventsubset.csv"

    run_prepare_windows_a3(root=root, out_csv=full_features_path)
    selector_report = run_selector(features_csv=full_features_path, out_csv=selected_shape_path, out_json=selector_json_path)

    full_df = load_feature_frame(full_features_path)
    selected_shape_df = load_feature_frame(selected_shape_path)
    event_df, event_reference = load_event_features(selected_shape_df, root=root)
    pass44_df, merge_summary = build_pass44_repaired_a3_table(selected_a3_df=selected_shape_df, event_df=event_df)
    pass44_features_path.parent.mkdir(parents=True, exist_ok=True)
    pass44_df.to_csv(pass44_features_path, index=False)

    exclude_patterns = build_exclude_patterns()
    pass44_report = run_train_baseline(
        features_csv=pass44_features_path,
        out_json=pass44_report_path,
        exclude_patterns=exclude_patterns,
    )

    pass42_report = json.loads(pass42_report_path.read_text(encoding="utf-8"))
    pass43_report = json.loads(pass43_report_path.read_text(encoding="utf-8"))
    pass41_a1_df = load_feature_frame(pass41_a1_features)
    pass43_old_a3_df = load_feature_frame(pass43_old_a3_features)

    pass42_subjects = load_subjects(pass42_report)
    pass43_subjects = load_subjects(pass43_report)
    pass44_subjects = load_subjects(pass44_report)

    pass44_feature_columns, pass44_selection_excluded = select_feature_columns(pass44_df, exclude_patterns=exclude_patterns)
    pass44_subjects_audit, pass44_blocks = build_subject_rows(pass44_df, pass44_feature_columns)
    pass44_pairwise = {
        "n3_minus_brux1": build_pairwise_gap(pass44_subjects_audit, pass44_feature_columns, pass44_blocks, higher_subject="n3"),
        "n11_minus_brux1": build_pairwise_gap(pass44_subjects_audit, pass44_feature_columns, pass44_blocks, higher_subject="n11"),
        "n5_minus_brux1": build_pairwise_gap(pass44_subjects_audit, pass44_feature_columns, pass44_blocks, higher_subject="n5"),
    }

    pass44_highest_control_subject = max(
        ["n3", "n5", "n11"],
        key=lambda subject_id: pass44_subjects[subject_id]["mean_score"],
    )

    pass42_summary = pass42_report["models"]["logreg"]["subject_aggregation"]["summary"]
    pass43_summary = pass43_report["models"]["logreg"]["subject_aggregation"]["summary"]
    pass44_summary = pass44_report["models"]["logreg"]["subject_aggregation"]["summary"]
    pass42_margin = best_brux_minus_highest_control(pass42_subjects)
    pass43_margin = best_brux_minus_highest_control(pass43_subjects)
    pass44_margin = best_brux_minus_highest_control(pass44_subjects)
    verdict = choose_verdict(
        pass42_summary=pass42_summary,
        pass44_summary=pass44_summary,
        pass42_margin=pass42_margin,
        pass44_margin=pass44_margin,
    )

    report = {
        "pass": PASS_NUMBER,
        "experiment": EXPERIMENT,
        "objective": PRIMARY_OBJECTIVE,
        "anchors": {
            "pass42_repaired_a1": {
                "features_csv": str(pass41_a1_features.resolve()),
                "report_path": str(pass42_report_path.resolve()),
                "subject_summary": pass42_summary,
                "subjects": pass42_subjects,
                "subjects_scores": get_subject_scores(pass42_subjects),
                "counts_by_subject": summarize_counts(pass41_a1_df),
                "row_count": int(len(pass41_a1_df)),
            },
            "pass43_old_surface_a3": {
                "features_csv": str(pass43_old_a3_features.resolve()),
                "report_path": str(pass43_report_path.resolve()),
                "subject_summary": pass43_summary,
                "subjects": pass43_subjects,
                "subjects_scores": get_subject_scores(pass43_subjects),
                "counts_by_subject": summarize_counts(pass43_old_a3_df),
                "row_count": int(len(pass43_old_a3_df)),
            },
        },
        "pass44_rebuild": {
            "full_features_csv": str(full_features_path.resolve()),
            "selected_shape_csv": str(selected_shape_path.resolve()),
            "selector_report_path": str(selector_json_path.resolve()),
            "selector": selector_report,
            "full_counts_by_subject": summarize_counts(full_df),
            "selected_counts_by_subject": summarize_counts(selected_shape_df),
            "full_row_count": int(len(full_df)),
            "selected_row_count": int(len(selected_shape_df)),
            "event_reference_by_subject": event_reference,
        },
        "pass44_repaired_a3": {
            "features_csv": str(pass44_features_path.resolve()),
            "report_path": str(pass44_report_path.resolve()),
            "subject_summary": pass44_summary,
            "subjects": pass44_subjects,
            "subjects_scores": get_subject_scores(pass44_subjects),
            "counts_by_subject": summarize_counts(pass44_df),
            "row_count": int(len(pass44_df)),
            "channels": sorted(pass44_df["channel"].dropna().astype(str).unique().tolist()),
            "selection_excluded_columns": pass44_selection_excluded,
            "feature_columns": pass44_feature_columns,
            "subjects_audit": pass44_subjects_audit,
            "pairwise": pass44_pairwise,
            **merge_summary,
        },
        "event_config": EVENT_CONFIG,
        "exclude_patterns": exclude_patterns,
        "derived": {
            "subject_score_rows": build_subject_comparison_rows(
                pass42_subjects=pass42_subjects,
                pass43_subjects=pass43_subjects,
                pass44_subjects=pass44_subjects,
            ),
            "pass42_best_brux_minus_highest_control": pass42_margin,
            "pass43_best_brux_minus_highest_control": pass43_margin,
            "pass44_best_brux_minus_highest_control": pass44_margin,
            "pass44_highest_control_subject": pass44_highest_control_subject,
            "pass44_highest_control_score": float(pass44_subjects[pass44_highest_control_subject]["mean_score"]),
            "pass44_brux1_minus_n3": float(pass44_subjects["brux1"]["mean_score"] - pass44_subjects["n3"]["mean_score"]),
            "verdict": verdict,
        },
        "summary_md_path": str(summary_md_path.resolve()),
        "summary_json_path": str(summary_json_path.resolve()),
    }

    summary_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_markdown(report), encoding="utf-8")
    print(summary_md_path)
    print(summary_json_path)
    print(pass44_report_path)
    print(pass44_features_path)


if __name__ == "__main__":
    main()
