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
    EVENT_FEATURES,
    SUBJECT_IDS,
    build_subject_rows,
    load_event_features,
)
from run_pass44_repaired_a3_event_subset_rebuild import PASS42_EVENT_SUBSET, ROW_ID_COLUMNS
from run_pass45_repaired_a3_shape_block_ablation import SHAPE_FEATURES

PASS_NUMBER = 46
EXPERIMENT = "repaired_cross_family_one_feature_evt_bursts_per_episode_mean_addback_on_frozen_pass45_anchor"
PRIMARY_OBJECTIVE = (
    "test whether restoring only evt_bursts_per_episode_mean on top of the frozen pass42/pass45 event scaffold "
    "improves brux2 on the repaired A3 anchor without reopening the control surface"
)
ADD_BACK_FEATURE = "evt_bursts_per_episode_mean"
KEPT_EVENT_FEATURES = [*PASS42_EVENT_SUBSET, ADD_BACK_FEATURE]
PROJECT_PYTHON = Path(__file__).resolve().parents[3] / ".venv/bin/python"
CONTROL_SUBJECTS = ["n3", "n5", "n11"]
BRUX_SUBJECTS = ["brux1", "brux2"]


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
    for feature in EVENT_FEATURES:
        if feature not in KEPT_EVENT_FEATURES:
            excludes.append(f"^{feature}$")
    return excludes


def build_pass46_table(*, frozen_pass44_df: pd.DataFrame, event_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    subset_event_df = event_df[ROW_ID_COLUMNS + [ADD_BACK_FEATURE]].copy()
    merged = frozen_pass44_df.merge(subset_event_df, on=ROW_ID_COLUMNS, how="left", validate="one_to_one")
    null_count = int(merged[ADD_BACK_FEATURE].isnull().sum())
    if null_count > 0:
        raise SystemExit(f"pass46 add-back merge left nulls for {ADD_BACK_FEATURE}: {null_count}")

    base_row_ids = frozen_pass44_df[ROW_ID_COLUMNS].to_dict(orient="records")
    merged_row_ids = merged[ROW_ID_COLUMNS].to_dict(orient="records")
    if base_row_ids != merged_row_ids:
        raise SystemExit("pass46 add-back merge changed the frozen repaired row order or row identity")

    return merged, {
        "merge_keys": ROW_ID_COLUMNS,
        "added_event_feature": ADD_BACK_FEATURE,
        "event_null_count_after_merge": null_count,
        "same_row_ids_preserved": True,
    }


def get_subject_scores(subjects: dict[str, dict[str, Any]]) -> dict[str, float]:
    return {subject_id: float(subjects[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS}


def highest_control(subjects: dict[str, dict[str, Any]]) -> tuple[str, float]:
    subject_id = max(CONTROL_SUBJECTS, key=lambda candidate: subjects[candidate]["mean_score"])
    return subject_id, float(subjects[subject_id]["mean_score"])


def best_brux(subjects: dict[str, dict[str, Any]]) -> tuple[str, float]:
    subject_id = max(BRUX_SUBJECTS, key=lambda candidate: subjects[candidate]["mean_score"])
    return subject_id, float(subjects[subject_id]["mean_score"])


def brux2_minus_highest_control(subjects: dict[str, dict[str, Any]]) -> float:
    _, control_score = highest_control(subjects)
    return float(subjects["brux2"]["mean_score"] - control_score)


def build_subject_comparison_rows(
    *,
    pass42_subjects: dict[str, Any],
    pass45_subjects: dict[str, Any],
    pass46_subjects: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for subject_id in SUBJECT_IDS:
        pass42_row = pass42_subjects[subject_id]
        pass45_row = pass45_subjects[subject_id]
        pass46_row = pass46_subjects[subject_id]
        rows.append(
            {
                "subject_id": subject_id,
                "true_label": pass46_row["true_label"],
                "pass42_score": float(pass42_row["mean_score"]),
                "pass45_score": float(pass45_row["mean_score"]),
                "pass46_score": float(pass46_row["mean_score"]),
                "delta_pass46_vs_pass45": float(pass46_row["mean_score"] - pass45_row["mean_score"]),
                "delta_pass46_vs_pass42": float(pass46_row["mean_score"] - pass42_row["mean_score"]),
                "pass42_predicted_label": pass42_row["predicted_label"],
                "pass45_predicted_label": pass45_row["predicted_label"],
                "pass46_predicted_label": pass46_row["predicted_label"],
            }
        )
    return rows


def render_subject_rows(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{row['subject_id']}` ({row['true_label']}): pass42 `{row['pass42_score']:.3f}` -> pass45 `{row['pass45_score']:.3f}` -> pass46 `{row['pass46_score']:.3f}` | "
        f"delta pass46 vs pass45 `{row['delta_pass46_vs_pass45']:+.3f}` | "
        f"delta pass46 vs pass42 `{row['delta_pass46_vs_pass42']:+.3f}` | "
        f"labels pass42 `{row['pass42_predicted_label']}` -> pass45 `{row['pass45_predicted_label']}` -> pass46 `{row['pass46_predicted_label']}`"
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


def choose_verdict(*, pass45_subjects: dict[str, Any], pass46_subjects: dict[str, Any]) -> tuple[str, str]:
    pass45_brux2_gap = brux2_minus_highest_control(pass45_subjects)
    pass46_brux2_gap = brux2_minus_highest_control(pass46_subjects)
    no_control_crossed_threshold = all(
        pass46_subjects[subject_id]["predicted_label"] == "control" for subject_id in CONTROL_SUBJECTS
    )
    brux1_delta = float(pass46_subjects["brux1"]["mean_score"] - pass45_subjects["brux1"]["mean_score"])

    if pass46_brux2_gap > pass45_brux2_gap and no_control_crossed_threshold and brux1_delta > -0.05:
        return (
            "the one-feature add-back is directionally useful on repaired A3 because brux2 improves relative to the highest control without reopening controls",
            "Keep pass45 and pass46 side by side as the repaired A3 no-shape base and one-feature add-back variant, then run one bounded interpretation pass that compares whether the add-back meaningfully changes the pass42-vs-A3 subject split enough to justify preserving it as the new repaired A3 anchor.",
        )
    return (
        "the one-feature add-back does not beat the frozen pass45 repaired A3 anchor cleanly enough to promote",
        "Stop this event add-back micro-branch here, preserve pass45 as the repaired A3 anchor, and only continue with another bounded change if it targets the remaining brux2 miss more directly than this one-feature event restoration.",
    )


def render_markdown(report: dict[str, Any]) -> str:
    pass42_summary = report["anchors"]["pass42_repaired_a1"]["subject_summary"]
    pass45_summary = report["anchors"]["pass45_repaired_a3_no_shape"]["subject_summary"]
    pass46_summary = report["pass46_repaired_a3_no_shape_plus_evt_bursts_per_episode_mean"]["subject_summary"]
    return f"""# Pass 46 — repaired cross-family one-feature `evt_bursts_per_episode_mean` add-back on the frozen pass42/pass45 scaffold

Date: 2026-05-05
Status: bounded one-feature add-back completed. This pass keeps the repaired selected rows, five-subject benchmark, `EMG1-EMG2`, threshold `0.5`, `logreg` LOSO contract, pass45 shape-drop exclusions, and the validated pass42 event trio fixed, and restores only `evt_bursts_per_episode_mean`.

## Why this is the smallest valid next test
- no selector rerun, no row regeneration, no scaffold rewrite, no family change, no channel change, and no model-family change
- frozen repaired A3 base table reused directly from pass44/pass45: `projects/bruxism-cap/data/window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_record_relative_shape_eventsubset.csv`
- pass45 contract preserved at train time: compact shape family still excluded: `{', '.join(SHAPE_FEATURES)}`
- fixed validated event trio preserved: `{', '.join(PASS42_EVENT_SUBSET)}`
- exactly one event feature restored by row-key merge: `{ADD_BACK_FEATURE}`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass46_repaired_cross_family_evt_bursts_per_episode_addback.py`
- Pass46 merged feature table: `projects/bruxism-cap/data/window_features_pass46_emg_s2_mcap_a3_only_pct10_90_record_relative_shape_eventsubset_plus_evt_bursts_per_episode_mean.csv`
- Pass46 LOSO report: `projects/bruxism-cap/reports/loso-cv-pass46-emg-a3-pct10-90-record-relative-eventsubset-no-shape-plus-bursts-per-episode.json`
- Pass46 summary JSON: `projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.json`
- Pass46 summary memo: `projects/bruxism-cap/reports/pass46-repaired-cross-family-one-feature-addback.md`
- Paired audit JSON: `projects/bruxism-cap/reports/pass46-vs-pass45-paired-subject-surface-audit.json`
- Paired audit memo: `projects/bruxism-cap/reports/pass46-vs-pass45-paired-subject-surface-audit.md`

## Scaffold and merge checks
- pass42 repaired A1 counts by subject: `{report['anchors']['pass42_repaired_a1']['counts_by_subject']}` | total rows `{report['anchors']['pass42_repaired_a1']['row_count']}`
- pass45 repaired A3 counts by subject: `{report['anchors']['pass45_repaired_a3_no_shape']['counts_by_subject']}` | total rows `{report['anchors']['pass45_repaired_a3_no_shape']['row_count']}`
- pass46 repaired A3 counts by subject: `{report['pass46_repaired_a3_no_shape_plus_evt_bursts_per_episode_mean']['counts_by_subject']}` | total rows `{report['pass46_repaired_a3_no_shape_plus_evt_bursts_per_episode_mean']['row_count']}`
- unchanged base exclusions: `{BASE_EXCLUDE_REGEXES}`
- retained pass45 shape-drop exclusions: `{SHAPE_FEATURES}`
- event features kept at train time: `{KEPT_EVENT_FEATURES}`
- add-back merge keys: `{report['pass46_repaired_a3_no_shape_plus_evt_bursts_per_episode_mean']['merge_keys']}`
- add-back null count after merge: `{report['pass46_repaired_a3_no_shape_plus_evt_bursts_per_episode_mean']['event_null_count_after_merge']}`
- frozen row ids preserved: `{report['pass46_repaired_a3_no_shape_plus_evt_bursts_per_episode_mean']['same_row_ids_preserved']}`

## Subject-level comparison against pass42 and pass45 anchors
- balanced accuracy: pass42 `{pass42_summary['balanced_accuracy']:.3f}` | pass45 `{pass45_summary['balanced_accuracy']:.3f}` | pass46 `{pass46_summary['balanced_accuracy']:.3f}`
- sensitivity: pass42 `{pass42_summary['sensitivity']:.3f}` | pass45 `{pass45_summary['sensitivity']:.3f}` | pass46 `{pass46_summary['sensitivity']:.3f}`
- specificity: pass42 `{pass42_summary['specificity']:.3f}` | pass45 `{pass45_summary['specificity']:.3f}` | pass46 `{pass46_summary['specificity']:.3f}`
- best-bruxism-minus-highest-control margin: pass42 `{report['derived']['pass42_best_brux_minus_highest_control']:+.3f}` | pass45 `{report['derived']['pass45_best_brux_minus_highest_control']:+.3f}` | pass46 `{report['derived']['pass46_best_brux_minus_highest_control']:+.3f}`
- pass46 highest control: `{report['derived']['pass46_highest_control_subject']}` at `{report['derived']['pass46_highest_control_score']:.3f}`
- pass46 best bruxism subject: `{report['derived']['pass46_best_brux_subject']}` at `{report['derived']['pass46_best_brux_score']:.3f}`
- pass46 exact sensitivity CI: `{pass46_summary['sensitivity_ci_95_exact']}`
- pass46 exact specificity CI: `{pass46_summary['specificity_ci_95_exact']}`
- pass46 subject Brier: `{pass46_summary['subject_probability_brier']:.3f}`

Subject score rows:
{render_subject_rows(report['derived']['subject_score_rows'])}

## Paired subject-surface comparison against pass45
- paired margin delta (pass46 - pass45): `{report['paired_audit']['comparison']['margin_change']['delta_primary_minus_anchor']:+.3f}`
- subject prediction flips: `{report['derived']['pass46_vs_pass45_prediction_flips']}`
- pass46 vs pass42 prediction flips: `{report['derived']['pass46_vs_pass42_prediction_flips']}`

## Did `brux2` improve relative to the highest control?
- pass42 `brux2 - highest_control`: `{report['derived']['pass42_brux2_minus_highest_control']:+.3f}`
- pass45 `brux2 - highest_control`: `{report['derived']['pass45_brux2_minus_highest_control']:+.3f}`
- pass46 `brux2 - highest_control`: `{report['derived']['pass46_brux2_minus_highest_control']:+.3f}`
- delta vs pass45: `{report['derived']['brux2_gap_delta_pass46_vs_pass45']:+.3f}`
- delta vs pass42: `{report['derived']['brux2_gap_delta_pass46_vs_pass42']:+.3f}`
- no control crossed threshold on pass46: `{report['derived']['no_control_crossed_threshold']}`

## Verdict
{report['derived']['verdict']}

## Safest next bounded step
{report['derived']['safest_next_step']}
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    reports_dir = root / "reports"
    data_dir = root / "data"

    pass44_features_path = data_dir / "window_features_pass44_emg_s2_mcap_a3_only_pct10_90_timepos10_record_relative_shape_eventsubset.csv"
    pass46_features_path = data_dir / "window_features_pass46_emg_s2_mcap_a3_only_pct10_90_record_relative_shape_eventsubset_plus_evt_bursts_per_episode_mean.csv"
    pass46_report_path = reports_dir / "loso-cv-pass46-emg-a3-pct10-90-record-relative-eventsubset-no-shape-plus-bursts-per-episode.json"
    summary_json_path = reports_dir / "pass46-repaired-cross-family-one-feature-addback.json"
    summary_md_path = reports_dir / "pass46-repaired-cross-family-one-feature-addback.md"
    paired_json_path = reports_dir / "pass46-vs-pass45-paired-subject-surface-audit.json"
    paired_md_path = reports_dir / "pass46-vs-pass45-paired-subject-surface-audit.md"

    pass42_report_path = reports_dir / "loso-cv-pass42-emg-a1-pct10-90-record-relative-shape-eventblock-subset.json"
    pass45_report_path = reports_dir / "loso-cv-pass45-emg-a3-pct10-90-record-relative-eventsubset-no-shape.json"

    frozen_pass44_df = pd.read_csv(pass44_features_path)
    event_df, event_reference = load_event_features(frozen_pass44_df, root=root)
    pass46_df, merge_summary = build_pass46_table(frozen_pass44_df=frozen_pass44_df, event_df=event_df)
    pass46_df.to_csv(pass46_features_path, index=False)

    exclude_patterns = build_exclude_patterns()
    pass46_report = run_train_baseline(
        features_csv=pass46_features_path,
        out_json=pass46_report_path,
        exclude_patterns=exclude_patterns,
    )
    pass42_report = json.loads(pass42_report_path.read_text(encoding="utf-8"))
    pass45_report = json.loads(pass45_report_path.read_text(encoding="utf-8"))

    pass42_subjects = load_subjects(pass42_report)
    pass45_subjects = load_subjects(pass45_report)
    pass46_subjects = load_subjects(pass46_report)

    pass46_feature_columns, pass46_selection_excluded = select_feature_columns(pass46_df, exclude_patterns=exclude_patterns)
    pass46_subjects_audit, pass46_blocks = build_subject_rows(pass46_df, pass46_feature_columns)
    paired_audit = run_paired_audit(
        primary_report=pass46_report_path,
        primary_name="pass46-repaired-a3-no-shape-plus-evt-bursts-per-episode-mean",
        anchor_report=pass45_report_path,
        anchor_name="pass45-repaired-a3-no-shape",
        out_json=paired_json_path,
        out_md=paired_md_path,
    )

    subject_rows = build_subject_comparison_rows(
        pass42_subjects=pass42_subjects,
        pass45_subjects=pass45_subjects,
        pass46_subjects=pass46_subjects,
    )
    pass46_highest_control_subject, pass46_highest_control_score = highest_control(pass46_subjects)
    pass46_best_brux_subject, pass46_best_brux_score = best_brux(pass46_subjects)
    verdict, safest_next_step = choose_verdict(pass45_subjects=pass45_subjects, pass46_subjects=pass46_subjects)
    no_control_crossed_threshold = all(
        pass46_subjects[subject_id]["predicted_label"] == "control" for subject_id in CONTROL_SUBJECTS
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
            "pass45_repaired_a3_no_shape": {
                "report_path": str(pass45_report_path.resolve()),
                "features_csv": pass45_report["features_csv"],
                "subject_summary": pass45_report["models"]["logreg"]["subject_aggregation"]["summary"],
                "subjects": pass45_subjects,
                "subjects_scores": get_subject_scores(pass45_subjects),
                "counts_by_subject": summarize_counts(pd.read_csv(Path(pass45_report["features_csv"]))),
                "row_count": int(pass45_report["rows"]),
            },
        },
        "pass46_repaired_a3_no_shape_plus_evt_bursts_per_episode_mean": {
            "report_path": str(pass46_report_path.resolve()),
            "features_csv": str(pass46_features_path.resolve()),
            "subject_summary": pass46_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "subjects": pass46_subjects,
            "subjects_scores": get_subject_scores(pass46_subjects),
            "counts_by_subject": summarize_counts(pass46_df),
            "row_count": int(pass46_report["rows"]),
            "selection_excluded_columns": pass46_selection_excluded,
            "feature_columns": pass46_feature_columns,
            "merge_keys": merge_summary["merge_keys"],
            "added_event_feature": merge_summary["added_event_feature"],
            "event_null_count_after_merge": merge_summary["event_null_count_after_merge"],
            "same_row_ids_preserved": merge_summary["same_row_ids_preserved"],
            "event_reference": event_reference,
            "subjects_audit": pass46_subjects_audit,
            "blocks": pass46_blocks,
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
            "pass45_best_brux_minus_highest_control": best_brux_minus_highest_control(pass45_subjects),
            "pass46_best_brux_minus_highest_control": best_brux_minus_highest_control(pass46_subjects),
            "pass42_brux2_minus_highest_control": brux2_minus_highest_control(pass42_subjects),
            "pass45_brux2_minus_highest_control": brux2_minus_highest_control(pass45_subjects),
            "pass46_brux2_minus_highest_control": brux2_minus_highest_control(pass46_subjects),
            "brux2_gap_delta_pass46_vs_pass45": brux2_minus_highest_control(pass46_subjects) - brux2_minus_highest_control(pass45_subjects),
            "brux2_gap_delta_pass46_vs_pass42": brux2_minus_highest_control(pass46_subjects) - brux2_minus_highest_control(pass42_subjects),
            "pass46_highest_control_subject": pass46_highest_control_subject,
            "pass46_highest_control_score": pass46_highest_control_score,
            "pass46_best_brux_subject": pass46_best_brux_subject,
            "pass46_best_brux_score": pass46_best_brux_score,
            "pass46_vs_pass45_prediction_flips": subject_prediction_flips(
                subject_rows,
                from_key="pass45_predicted_label",
                to_key="pass46_predicted_label",
            ),
            "pass46_vs_pass42_prediction_flips": subject_prediction_flips(
                subject_rows,
                from_key="pass42_predicted_label",
                to_key="pass46_predicted_label",
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
    print(pass46_features_path)
    print(pass46_report_path)
    print(paired_md_path)
    print(paired_json_path)


if __name__ == "__main__":
    main()
