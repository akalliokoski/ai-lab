from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from run_pass34_record_relative_emg_audit import BASE_EXCLUDE_REGEXES, EPSILON, RELATIVE_FEATURES, build_record_relative_table
from run_pass41_event_conditioned_feature_block_audit import EVENT_FEATURES, load_event_features
from run_pass44_repaired_a3_event_subset_rebuild import PASS42_EVENT_SUBSET, ROW_ID_COLUMNS
from run_pass45_repaired_a3_shape_block_ablation import SHAPE_FEATURES
from run_pass47_control_expanded_rerun import (
    BRUX_SUBJECTS,
    CONTROL_SUBJECTS,
    SUBJECTS,
    SUBJECT_IDS,
    best_brux,
    best_brux_minus_highest_control,
    counts_by_subject,
    ensure_time_metadata,
    highest_control,
    load_subject_block,
    ordered_subject_rows,
    shared_subject_deltas,
)

PASS_NUMBER = 48
PROJECT_PYTHON = Path(__file__).resolve().parents[3] / ".venv/bin/python"


def python_executable() -> Path:
    return PROJECT_PYTHON if PROJECT_PYTHON.exists() else Path(sys.executable)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


def run_prepare_windows_a1(*, root: Path, out_csv: Path) -> None:
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
        str(python_executable()),
        str(script),
        "--features-csv",
        str(features_csv),
        "--subjects",
        ",".join(SUBJECT_IDS),
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
        if feature not in PASS42_EVENT_SUBSET:
            excludes.append(f"^{feature}$")
    return excludes


def build_pass48_table(*, selected_df: pd.DataFrame, event_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    selected_with_time = ensure_time_metadata(selected_df)
    record_relative_df, record_relative_summary = build_record_relative_table(
        selected_with_time,
        relative_features=RELATIVE_FEATURES,
        epsilon=EPSILON,
    )
    subset_event_df = event_df[ROW_ID_COLUMNS + PASS42_EVENT_SUBSET].copy()
    merged = record_relative_df.merge(subset_event_df, on=ROW_ID_COLUMNS, how="left", validate="one_to_one")
    null_counts = {feature: int(merged[feature].isnull().sum()) for feature in PASS42_EVENT_SUBSET}
    if any(count > 0 for count in null_counts.values()):
        raise SystemExit(f"pass48 repaired A1 event merge left nulls: {null_counts}")
    return merged, {
        "record_relative": record_relative_summary,
        "event_merge_keys": ROW_ID_COLUMNS,
        "event_null_counts_after_merge": null_counts,
        "appended_event_subset": PASS42_EVENT_SUBSET,
    }


def choose_decision(*, pass48_summary: dict[str, Any], pass48_subjects: dict[str, dict[str, Any]], pass47_margin: float) -> tuple[str, str]:
    pass48_margin = best_brux_minus_highest_control(pass48_subjects, controls=CONTROL_SUBJECTS)
    pass48_highest_control_subject, pass48_highest_control_score = highest_control(pass48_subjects, controls=CONTROL_SUBJECTS)
    brux2_gap = float(pass48_subjects["brux2"]["mean_score"] - pass48_highest_control_score)
    all_controls_below_threshold = all(pass48_subjects[sid]["predicted_label"] == "control" for sid in CONTROL_SUBJECTS)
    both_brux_above_highest_control = all(
        float(pass48_subjects[sid]["mean_score"]) > pass48_highest_control_score for sid in BRUX_SUBJECTS
    )

    if (
        all_controls_below_threshold
        and pass48_summary["sensitivity"] > 0.5
        and both_brux_above_highest_control
        and pass48_margin > pass47_margin
    ):
        return (
            "The repaired A1-only control-expanded replication is a meaningful benchmark improvement: both bruxism subjects now clear the highest control while all controls stay below threshold.",
            "continue",
        )

    return (
        "The repaired A1-only control-expanded replication does not clear the honest tiny-N benchmark bar strongly enough to justify more CAP passes: the headline remains capped, or one bruxism subject still trails the control ceiling, so the CAP benchmark should be treated as complete rather than extended further.",
        "close",
    )


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["pass48"]["subject_summary"]
    pass47_summary = report["anchors"]["pass47"]["subject_summary"]
    pass42_summary = report["anchors"]["pass42"]["subject_summary"]
    rows = report["derived"]["pass48_subject_rows"]
    shared_vs_pass47 = report["derived"]["shared_vs_pass47_rows"]
    shared_vs_pass42 = report["derived"]["shared_vs_pass42_rows"]
    return f"""# Pass 48 — final bounded 7-subject repaired-A1 control-expanded replication

Date: 2026-05-06
Status: completed final bounded replication on the repaired `A1-only` control-expanded scaffold.

## Exact contract held fixed
- channel: `EMG1-EMG2`
- slice: exclusive `SLEEP-S2 + MCAP-A1-only`
- scaffold family: repaired percentile-band / time-aware record-relative event-subset surface
- train-time exclusions: unchanged base exclusions `{BASE_EXCLUDE_REGEXES}` plus no-shape exclusions `{SHAPE_FEATURES}`
- kept event subset: `{PASS42_EVENT_SUBSET}`
- model/eval contract: `logreg` with LOSO subject-level reporting and uncertainty outputs
- exact subjects: `{SUBJECT_IDS}`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass48_control_expanded_a1_replication.py`
- Full rebuilt A1 candidate pool: `projects/bruxism-cap/data/window_features_pass48_emg_s2_mcap_a1_only_full_envelope_shape_control_expanded.csv`
- Percentile-band selector report: `projects/bruxism-cap/reports/time-position-match-pass48-emg-a1-pct10-90-control-expanded.json`
- Intermediate selected table: `projects/bruxism-cap/data/window_features_pass48_emg_s2_mcap_a1_only_pct10_90_timepos10_shape_control_expanded.csv`
- Final expanded table: `projects/bruxism-cap/data/window_features_pass48_emg_s2_mcap_a1_only_control_expanded.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass48-emg-a1-control-expanded.json`
- Summary JSON: `projects/bruxism-cap/reports/pass48-control-expanded-a1-replication.json`
- Cross-family audit JSON/MD: `projects/bruxism-cap/reports/pass48-vs-pass47-control-expanded-cross-family-audit.json`, `projects/bruxism-cap/reports/pass48-vs-pass47-control-expanded-cross-family-audit.md`
- Summary memo: `projects/bruxism-cap/reports/pass48-control-expanded-a1-replication.md`

## Row-count and contract checks
- full exclusive `A1-only` candidate rows by subject before percentile-band selection: `{report['pass48']['full_candidate_counts_by_subject']}` | total `{report['pass48']['full_candidate_row_count']}`
- selector kept subjects: `{report['pass48']['selector_report']['subjects']}`
- selector rows written: `{report['pass48']['selector_report']['rows_written']}`
- selected rows by subject: `{report['pass48']['selected_counts_by_subject']}`
- final expanded table rows by subject: `{report['pass48']['final_counts_by_subject']}` | total `{report['pass48']['final_row_count']}`
- record-relative features applied: `{report['pass48']['table_build']['record_relative']['relative_features_applied']}`
- event merge keys: `{report['pass48']['table_build']['event_merge_keys']}`
- event null counts after merge: `{report['pass48']['table_build']['event_null_counts_after_merge']}`

## Subject-level result vs pass47 and legacy pass42 A1 anchor
- balanced accuracy: pass42 `{pass42_summary['balanced_accuracy']:.3f}` | pass47 `{pass47_summary['balanced_accuracy']:.3f}` | pass48 `{summary['balanced_accuracy']:.3f}`
- sensitivity: pass42 `{pass42_summary['sensitivity']:.3f}` | pass47 `{pass47_summary['sensitivity']:.3f}` | pass48 `{summary['sensitivity']:.3f}`
- specificity: pass42 `{pass42_summary['specificity']:.3f}` | pass47 `{pass47_summary['specificity']:.3f}` | pass48 `{summary['specificity']:.3f}`
- best-bruxism-minus-highest-control margin: pass42 `{report['anchors']['pass42']['best_brux_minus_highest_control']:+.3f}` | pass47 `{report['anchors']['pass47']['best_brux_minus_highest_control']:+.3f}` | pass48 `{report['derived']['pass48_best_brux_minus_highest_control']:+.3f}`
- highest control: pass47 `{report['anchors']['pass47']['highest_control_subject']}` `{report['anchors']['pass47']['highest_control_score']:.3f}` | pass48 `{report['derived']['pass48_highest_control_subject']}` `{report['derived']['pass48_highest_control_score']:.3f}`
- best bruxism subject: pass48 `{report['derived']['pass48_best_brux_subject']}` `{report['derived']['pass48_best_brux_score']:.3f}`
- `brux2 - highest_control`: pass47 `{report['anchors']['pass47']['brux2_minus_highest_control']:+.3f}` | pass48 `{report['derived']['pass48_brux2_minus_highest_control']:+.3f}`
- exact sensitivity CI: `{summary['sensitivity_ci_95_exact']}`
- exact specificity CI: `{summary['specificity_ci_95_exact']}`
- subject Brier: `{summary['subject_probability_brier']:.3f}`

Pass48 subject rows:
{chr(10).join(f"- `{row['subject_id']}` ({row['true_label']}): score `{row['mean_score']:.3f}` | predicted `{row['predicted_label']}` | positive-window fraction `{row['positive_window_fraction']:.3f}` | windows `{row['windows']}`" for row in rows)}

## Shared-subject deltas vs pass47
{chr(10).join(f"- `{row['subject_id']}` ({row['true_label']}): pass48 `{row['pass47_score']:.3f}` vs pass47 `{row['anchor_score']:.3f}` | delta `{row['delta_pass47_minus_anchor']:+.3f}` | labels pass48 `{row['pass47_predicted_label']}` / pass47 `{row['anchor_predicted_label']}`" for row in shared_vs_pass47)}

## Shared-core deltas vs pass42
{chr(10).join(f"- `{row['subject_id']}` ({row['true_label']}): pass48 `{row['pass47_score']:.3f}` vs pass42 `{row['anchor_score']:.3f}` | delta `{row['delta_pass47_minus_anchor']:+.3f}` | labels pass48 `{row['pass47_predicted_label']}` / pass42 `{row['anchor_predicted_label']}`" for row in shared_vs_pass42)}

## Final decision
- verdict: {report['derived']['verdict']}
- recommendation: `{report['derived']['recommendation']}`
- final note: {report['derived']['final_note']}
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    reports_dir = root / "reports"
    data_dir = root / "data"

    full_pool_path = data_dir / "window_features_pass48_emg_s2_mcap_a1_only_full_envelope_shape_control_expanded.csv"
    selected_shape_path = data_dir / "window_features_pass48_emg_s2_mcap_a1_only_pct10_90_timepos10_shape_control_expanded.csv"
    final_features_path = data_dir / "window_features_pass48_emg_s2_mcap_a1_only_control_expanded.csv"
    selector_report_path = reports_dir / "time-position-match-pass48-emg-a1-pct10-90-control-expanded.json"
    loso_report_path = reports_dir / "loso-cv-pass48-emg-a1-control-expanded.json"
    summary_json_path = reports_dir / "pass48-control-expanded-a1-replication.json"
    summary_md_path = reports_dir / "pass48-control-expanded-a1-replication.md"
    paired_json_path = reports_dir / "pass48-vs-pass47-control-expanded-cross-family-audit.json"
    paired_md_path = reports_dir / "pass48-vs-pass47-control-expanded-cross-family-audit.md"

    pass47_report_path = reports_dir / "loso-cv-pass47-emg-a3-control-expanded.json"
    pass42_report_path = reports_dir / "loso-cv-pass42-emg-a1-pct10-90-record-relative-shape-eventblock-subset.json"

    run_prepare_windows_a1(root=root, out_csv=full_pool_path)
    selector_report = run_selector(features_csv=full_pool_path, out_csv=selected_shape_path, out_json=selector_report_path)

    selected_df = pd.read_csv(selected_shape_path)
    event_df, event_reference = load_event_features(selected_df, root=root)
    pass48_df, table_build = build_pass48_table(selected_df=selected_df, event_df=event_df)
    final_features_path.parent.mkdir(parents=True, exist_ok=True)
    pass48_df.to_csv(final_features_path, index=False)

    exclude_patterns = build_exclude_patterns()
    pass48_report = run_train_baseline(features_csv=final_features_path, out_json=loso_report_path, exclude_patterns=exclude_patterns)
    pass47_report = json.loads(pass47_report_path.read_text(encoding="utf-8"))
    pass42_report = json.loads(pass42_report_path.read_text(encoding="utf-8"))

    paired_audit = run_paired_audit(
        primary_report=loso_report_path,
        primary_name="pass48-repaired-a1-control-expanded",
        anchor_report=pass47_report_path,
        anchor_name="pass47-repaired-a3-control-expanded",
        out_json=paired_json_path,
        out_md=paired_md_path,
    )

    pass48_subjects, pass48_summary = load_subject_block(pass48_report)
    pass47_subjects, pass47_summary = load_subject_block(pass47_report)
    pass42_subjects, pass42_summary = load_subject_block(pass42_report)

    pass47_highest_control_subject, pass47_highest_control_score = highest_control(pass47_subjects, controls=CONTROL_SUBJECTS)
    pass48_highest_control_subject, pass48_highest_control_score = highest_control(pass48_subjects, controls=CONTROL_SUBJECTS)
    pass48_best_brux_subject, pass48_best_brux_score = best_brux(pass48_subjects)
    pass47_margin = best_brux_minus_highest_control(pass47_subjects, controls=CONTROL_SUBJECTS)
    pass48_margin = best_brux_minus_highest_control(pass48_subjects, controls=CONTROL_SUBJECTS)
    pass42_margin = best_brux_minus_highest_control(pass42_subjects, controls=["n3", "n5", "n11"])
    pass47_brux2_gap = float(pass47_subjects["brux2"]["mean_score"] - pass47_highest_control_score)
    pass48_brux2_gap = float(pass48_subjects["brux2"]["mean_score"] - pass48_highest_control_score)
    verdict, recommendation = choose_decision(pass48_summary=pass48_summary, pass48_subjects=pass48_subjects, pass47_margin=pass47_margin)

    shared_vs_pass47 = shared_subject_deltas(pass48_subjects, pass47_subjects)
    shared_vs_pass42 = []
    for subject_id in ["brux1", "brux2", "n3", "n5", "n11"]:
        shared_vs_pass42.append(
            {
                "subject_id": subject_id,
                "true_label": pass48_subjects[subject_id]["true_label"],
                "pass47_score": float(pass48_subjects[subject_id]["mean_score"]),
                "anchor_score": float(pass42_subjects[subject_id]["mean_score"]),
                "delta_pass47_minus_anchor": float(float(pass48_subjects[subject_id]["mean_score"]) - float(pass42_subjects[subject_id]["mean_score"])),
                "pass47_predicted_label": pass48_subjects[subject_id]["predicted_label"],
                "anchor_predicted_label": pass42_subjects[subject_id]["predicted_label"],
            }
        )

    result = {
        "pass48": {
            "subject_ids": SUBJECT_IDS,
            "full_candidate_counts_by_subject": counts_by_subject(pd.read_csv(full_pool_path)),
            "full_candidate_row_count": int(len(pd.read_csv(full_pool_path))),
            "selected_counts_by_subject": counts_by_subject(selected_df),
            "selected_row_count": int(len(selected_df)),
            "final_counts_by_subject": counts_by_subject(pass48_df),
            "final_row_count": int(len(pass48_df)),
            "selector_report": selector_report,
            "event_reference": event_reference,
            "table_build": table_build,
            "subject_summary": pass48_summary,
            "feature_count": int(pass48_report.get("feature_count", 0)),
            "feature_selection": pass48_report.get("feature_selection", {}),
        },
        "anchors": {
            "pass47": {
                "subject_summary": pass47_summary,
                "best_brux_minus_highest_control": pass47_margin,
                "highest_control_subject": pass47_highest_control_subject,
                "highest_control_score": pass47_highest_control_score,
                "brux2_minus_highest_control": pass47_brux2_gap,
            },
            "pass42": {
                "subject_summary": pass42_summary,
                "best_brux_minus_highest_control": pass42_margin,
            },
        },
        "paired_audits": {
            "pass47": paired_audit,
        },
        "derived": {
            "pass48_subject_rows": ordered_subject_rows(pass48_subjects),
            "pass48_highest_control_subject": pass48_highest_control_subject,
            "pass48_highest_control_score": pass48_highest_control_score,
            "pass48_best_brux_subject": pass48_best_brux_subject,
            "pass48_best_brux_score": pass48_best_brux_score,
            "pass48_best_brux_minus_highest_control": pass48_margin,
            "pass48_brux2_minus_highest_control": pass48_brux2_gap,
            "shared_vs_pass47_rows": shared_vs_pass47,
            "shared_vs_pass42_rows": shared_vs_pass42,
            "verdict": verdict,
            "recommendation": recommendation,
            "final_note": "If this final repaired A1 replication still fails to produce a clear two-bruxism-subject separation above the control ceiling, the CAP benchmark should be closed as scientifically informative but exhausted for further bounded passes.",
        },
    }

    summary_json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary_md_path.write_text(render_markdown(result), encoding="utf-8")


if __name__ == "__main__":
    main()
