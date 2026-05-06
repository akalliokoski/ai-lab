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

PASS_NUMBER = 47
SUBJECTS = [
    ("brux1", "bruxism"),
    ("brux2", "bruxism"),
    ("n1", "control"),
    ("n2", "control"),
    ("n3", "control"),
    ("n5", "control"),
    ("n11", "control"),
]
SUBJECT_IDS = [subject_id for subject_id, _label in SUBJECTS]
BRUX_SUBJECTS = ["brux1", "brux2"]
CONTROL_SUBJECTS = ["n1", "n2", "n3", "n5", "n11"]
PROJECT_PYTHON = Path(__file__).resolve().parents[3] / ".venv/bin/python"


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


def build_pass47_table(*, selected_df: pd.DataFrame, event_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
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
        raise SystemExit(f"pass47 repaired A3 event merge left nulls: {null_counts}")
    return merged, {
        "record_relative": record_relative_summary,
        "event_merge_keys": ROW_ID_COLUMNS,
        "event_null_counts_after_merge": null_counts,
        "appended_event_subset": PASS42_EVENT_SUBSET,
    }


def counts_by_subject(df: pd.DataFrame) -> dict[str, int]:
    return {str(subject_id): int(count) for subject_id, count in df.groupby("subject_id").size().items()}


def load_subject_block(report: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    model = report["models"]["logreg"]
    subject_rows = model["subject_aggregation"]["subjects"]
    return {row["subject_id"]: row for row in subject_rows}, model["subject_aggregation"]["summary"]


def best_brux_minus_highest_control(subjects: dict[str, dict[str, Any]], *, controls: list[str]) -> float:
    best_brux = max(float(subjects[subject_id]["mean_score"]) for subject_id in BRUX_SUBJECTS)
    highest_control = max(float(subjects[subject_id]["mean_score"]) for subject_id in controls)
    return best_brux - highest_control


def highest_control(subjects: dict[str, dict[str, Any]], *, controls: list[str]) -> tuple[str, float]:
    subject_id = max(controls, key=lambda candidate: float(subjects[candidate]["mean_score"]))
    return subject_id, float(subjects[subject_id]["mean_score"])


def best_brux(subjects: dict[str, dict[str, Any]]) -> tuple[str, float]:
    subject_id = max(BRUX_SUBJECTS, key=lambda candidate: float(subjects[candidate]["mean_score"]))
    return subject_id, float(subjects[subject_id]["mean_score"])


def ordered_subject_rows(subjects: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for subject_id in SUBJECT_IDS:
        row = subjects[subject_id]
        rows.append(
            {
                "subject_id": subject_id,
                "true_label": row["true_label"],
                "mean_score": float(row["mean_score"]),
                "predicted_label": row["predicted_label"],
                "windows": int(row["windows"]),
                "predicted_positive_windows": int(row["predicted_positive_windows"]),
                "positive_window_fraction": float(row["positive_window_fraction"]),
            }
        )
    return rows


def shared_subject_deltas(pass47_subjects: dict[str, dict[str, Any]], anchor_subjects: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for subject_id in ["brux1", "brux2", "n3", "n5", "n11"]:
        rows.append(
            {
                "subject_id": subject_id,
                "true_label": pass47_subjects[subject_id]["true_label"],
                "pass47_score": float(pass47_subjects[subject_id]["mean_score"]),
                "anchor_score": float(anchor_subjects[subject_id]["mean_score"]),
                "delta_pass47_minus_anchor": float(
                    float(pass47_subjects[subject_id]["mean_score"]) - float(anchor_subjects[subject_id]["mean_score"])
                ),
                "pass47_predicted_label": pass47_subjects[subject_id]["predicted_label"],
                "anchor_predicted_label": anchor_subjects[subject_id]["predicted_label"],
            }
        )
    return rows


def choose_verdict(*, summary: dict[str, Any], subjects: dict[str, dict[str, Any]], pass45_margin: float, pass46_margin: float) -> tuple[str, str]:
    new_controls_below_threshold = all(subjects[subject_id]["predicted_label"] == "control" for subject_id in ["n1", "n2"])
    all_controls_below_threshold = all(subjects[subject_id]["predicted_label"] == "control" for subject_id in CONTROL_SUBJECTS)
    pass47_margin = best_brux_minus_highest_control(subjects, controls=CONTROL_SUBJECTS)
    pass47_highest_control_subject, pass47_highest_control_score = highest_control(subjects, controls=CONTROL_SUBJECTS)
    brux2_gap = float(subjects["brux2"]["mean_score"] - pass47_highest_control_score)

    if new_controls_below_threshold and all_controls_below_threshold and pass47_margin >= max(pass45_margin - 0.10, pass46_margin - 0.10):
        verdict = (
            "The first 7-subject control-expanded rerun preserves the repaired-A3 specificity story tightly enough to keep this branch alive: "
            f"both new controls stay below threshold, all five controls remain predicted control, and the best-bruxism-minus-highest-control margin stays {pass47_margin:+.3f} even after adding `n1` and `n2`."
        )
        next_step = (
            "A matched `A1-only` replication now looks justified as the next exact task because the first control-side stress test did not immediately collapse the repaired-A3 read; keep the same 7-subject subject set and frozen no-shape contract, and ask whether the control-expanded result is channel/stage-family specific or transfers honestly to the repaired `A1-only` scaffold."
        )
        return verdict, next_step

    verdict = (
        "The first 7-subject control-expanded rerun shows the repaired-A3 anchor is too fragile to treat as stable on this branch: "
        f"highest control is `{pass47_highest_control_subject}` at {pass47_highest_control_score:.3f}, `brux2 - highest_control` is {brux2_gap:+.3f}, and the expanded margin falls to {pass47_margin:+.3f}."
    )
    next_step = (
        "Do not open an `A1-only` replication yet. First preserve this as the branch verdict and, if the board continues the branch at all, spend the next exact task on a narrow interpretation/audit step explaining which added control changed the repaired-A3 control surface and whether the failure comes from selection timing or subject-specific event geometry."
    )
    return verdict, next_step


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["pass47"]["subject_summary"]
    pass45_summary = report["anchors"]["pass45"]["subject_summary"]
    pass46_summary = report["anchors"]["pass46"]["subject_summary"]
    selector = report["pass47"]["selector_report"]
    pass47_rows = report["derived"]["pass47_subject_rows"]
    new_controls = report["derived"]["new_controls"]
    shared_vs_pass45 = report["derived"]["shared_vs_pass45_rows"]
    shared_vs_pass46 = report["derived"]["shared_vs_pass46_rows"]
    return f"""# Pass 47 — first bounded 7-subject repaired-A3 control-expanded rerun

Date: 2026-05-06
Status: completed exact 7-subject control-expanded rerun on the frozen repaired `A3-only` no-shape contract.

## Exact contract held fixed
- channel: `EMG1-EMG2`
- slice: exclusive `SLEEP-S2 + MCAP-A3-only`
- scaffold family: repaired percentile-band / time-aware record-relative event-subset surface
- train-time exclusions: unchanged base exclusions `{BASE_EXCLUDE_REGEXES}` plus pass45 shape-drop exclusions `{SHAPE_FEATURES}`
- kept event subset: `{PASS42_EVENT_SUBSET}`
- model/eval contract: `logreg` with LOSO subject-level reporting and uncertainty outputs
- exact subjects: `{SUBJECT_IDS}`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass47_control_expanded_rerun.py`
- Full rebuilt A3 candidate pool: `projects/bruxism-cap/data/window_features_pass47_emg_s2_mcap_a3_only_full_envelope_shape_control_expanded.csv`
- Percentile-band selector report: `projects/bruxism-cap/reports/time-position-match-pass47-emg-a3-pct10-90-control-expanded.json`
- Intermediate selected table: `projects/bruxism-cap/data/window_features_pass47_emg_s2_mcap_a3_only_pct10_90_timepos10_shape_control_expanded.csv`
- Final expanded table: `projects/bruxism-cap/data/window_features_pass47_emg_s2_mcap_a3_only_control_expanded.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass47-emg-a3-control-expanded.json`
- Summary JSON: `projects/bruxism-cap/reports/pass47-control-expanded-rerun.json`
- Paired pass45 audit JSON/MD: `projects/bruxism-cap/reports/pass47-vs-pass45-paired-subject-surface-audit.json`, `projects/bruxism-cap/reports/pass47-vs-pass45-paired-subject-surface-audit.md`
- Paired pass46 audit JSON/MD: `projects/bruxism-cap/reports/pass47-vs-pass46-paired-subject-surface-audit.json`, `projects/bruxism-cap/reports/pass47-vs-pass46-paired-subject-surface-audit.md`
- Summary memo: `projects/bruxism-cap/reports/pass47-control-expanded-rerun.md`

## Row-count and contract checks
- full exclusive `A3-only` candidate rows by subject before percentile-band selection: `{report['pass47']['full_candidate_counts_by_subject']}` | total `{report['pass47']['full_candidate_row_count']}`
- selector kept subjects: `{selector['subjects']}`
- selector rows written: `{selector['rows_written']}`
- selected rows by subject: `{report['pass47']['selected_counts_by_subject']}`
- final expanded table rows by subject: `{report['pass47']['final_counts_by_subject']}` | total `{report['pass47']['final_row_count']}`
- record-relative features applied: `{report['pass47']['table_build']['record_relative']['relative_features_applied']}`
- event merge keys: `{report['pass47']['table_build']['event_merge_keys']}`
- event null counts after merge: `{report['pass47']['table_build']['event_null_counts_after_merge']}`

Selector per-subject candidate rows after percentile-band filter:
- `{selector['subjects_summary']}`

## Subject-level result vs pass45 and pass46 anchors
- balanced accuracy: pass45 `{pass45_summary['balanced_accuracy']:.3f}` | pass46 `{pass46_summary['balanced_accuracy']:.3f}` | pass47 `{summary['balanced_accuracy']:.3f}`
- sensitivity: pass45 `{pass45_summary['sensitivity']:.3f}` | pass46 `{pass46_summary['sensitivity']:.3f}` | pass47 `{summary['sensitivity']:.3f}`
- specificity: pass45 `{pass45_summary['specificity']:.3f}` | pass46 `{pass46_summary['specificity']:.3f}` | pass47 `{summary['specificity']:.3f}`
- best-bruxism-minus-highest-control margin: pass45 `{report['anchors']['pass45']['best_brux_minus_highest_control']:+.3f}` | pass46 `{report['anchors']['pass46']['best_brux_minus_highest_control']:+.3f}` | pass47 `{report['derived']['pass47_best_brux_minus_highest_control']:+.3f}`
- highest control: pass45 `{report['anchors']['pass45']['highest_control_subject']}` `{report['anchors']['pass45']['highest_control_score']:.3f}` | pass46 `{report['anchors']['pass46']['highest_control_subject']}` `{report['anchors']['pass46']['highest_control_score']:.3f}` | pass47 `{report['derived']['pass47_highest_control_subject']}` `{report['derived']['pass47_highest_control_score']:.3f}`
- best bruxism subject: pass47 `{report['derived']['pass47_best_brux_subject']}` `{report['derived']['pass47_best_brux_score']:.3f}`
- `brux2 - highest_control`: pass45 `{report['anchors']['pass45']['brux2_minus_highest_control']:+.3f}` | pass46 `{report['anchors']['pass46']['brux2_minus_highest_control']:+.3f}` | pass47 `{report['derived']['pass47_brux2_minus_highest_control']:+.3f}`
- exact sensitivity CI: `{summary['sensitivity_ci_95_exact']}`
- exact specificity CI: `{summary['specificity_ci_95_exact']}`
- subject Brier: `{summary['subject_probability_brier']:.3f}`

Pass47 subject rows:
{chr(10).join(f"- `{row['subject_id']}` ({row['true_label']}): score `{row['mean_score']:.3f}` | predicted `{row['predicted_label']}` | positive-window fraction `{row['positive_window_fraction']:.3f}` | windows `{row['windows']}`" for row in pass47_rows)}

## New controls verdict
{chr(10).join(f"- `{row['subject_id']}`: score `{row['mean_score']:.3f}` | predicted `{row['predicted_label']}` | below threshold `{row['predicted_label'] == 'control'}`" for row in new_controls)}
- all controls below threshold: `{report['derived']['all_controls_below_threshold']}`

## Shared-subject deltas vs the two 5-subject anchors
Against pass45:
{chr(10).join(f"- `{row['subject_id']}` ({row['true_label']}): pass47 `{row['pass47_score']:.3f}` vs pass45 `{row['anchor_score']:.3f}` | delta `{row['delta_pass47_minus_anchor']:+.3f}` | labels pass47 `{row['pass47_predicted_label']}` / pass45 `{row['anchor_predicted_label']}`" for row in shared_vs_pass45)}

Against pass46:
{chr(10).join(f"- `{row['subject_id']}` ({row['true_label']}): pass47 `{row['pass47_score']:.3f}` vs pass46 `{row['anchor_score']:.3f}` | delta `{row['delta_pass47_minus_anchor']:+.3f}` | labels pass47 `{row['pass47_predicted_label']}` / pass46 `{row['anchor_predicted_label']}`" for row in shared_vs_pass46)}

## Verdict
{report['derived']['verdict']}

## A1-only replication note
{report['derived']['a1_replication_note']}
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    reports_dir = root / "reports"
    data_dir = root / "data"

    full_pool_path = data_dir / "window_features_pass47_emg_s2_mcap_a3_only_full_envelope_shape_control_expanded.csv"
    selected_shape_path = data_dir / "window_features_pass47_emg_s2_mcap_a3_only_pct10_90_timepos10_shape_control_expanded.csv"
    final_features_path = data_dir / "window_features_pass47_emg_s2_mcap_a3_only_control_expanded.csv"
    selector_report_path = reports_dir / "time-position-match-pass47-emg-a3-pct10-90-control-expanded.json"
    loso_report_path = reports_dir / "loso-cv-pass47-emg-a3-control-expanded.json"
    summary_json_path = reports_dir / "pass47-control-expanded-rerun.json"
    summary_md_path = reports_dir / "pass47-control-expanded-rerun.md"
    pass47_vs_pass45_json = reports_dir / "pass47-vs-pass45-paired-subject-surface-audit.json"
    pass47_vs_pass45_md = reports_dir / "pass47-vs-pass45-paired-subject-surface-audit.md"
    pass47_vs_pass46_json = reports_dir / "pass47-vs-pass46-paired-subject-surface-audit.json"
    pass47_vs_pass46_md = reports_dir / "pass47-vs-pass46-paired-subject-surface-audit.md"

    pass45_report_path = reports_dir / "loso-cv-pass45-emg-a3-pct10-90-record-relative-eventsubset-no-shape.json"
    pass46_report_path = reports_dir / "loso-cv-pass46-emg-a3-pct10-90-record-relative-eventsubset-no-shape-plus-bursts-per-episode.json"

    run_prepare_windows_a3(root=root, out_csv=full_pool_path)
    selector_report = run_selector(features_csv=full_pool_path, out_csv=selected_shape_path, out_json=selector_report_path)

    selected_df = pd.read_csv(selected_shape_path)
    event_df, event_reference = load_event_features(selected_df, root=root)
    pass47_df, table_build = build_pass47_table(selected_df=selected_df, event_df=event_df)
    final_features_path.parent.mkdir(parents=True, exist_ok=True)
    pass47_df.to_csv(final_features_path, index=False)

    exclude_patterns = build_exclude_patterns()
    pass47_report = run_train_baseline(features_csv=final_features_path, out_json=loso_report_path, exclude_patterns=exclude_patterns)
    pass45_report = json.loads(pass45_report_path.read_text(encoding="utf-8"))
    pass46_report = json.loads(pass46_report_path.read_text(encoding="utf-8"))

    pass47_vs_pass45 = run_paired_audit(
        primary_report=loso_report_path,
        primary_name="pass47-repaired-a3-control-expanded",
        anchor_report=pass45_report_path,
        anchor_name="pass45-repaired-a3-no-shape",
        out_json=pass47_vs_pass45_json,
        out_md=pass47_vs_pass45_md,
    )
    pass47_vs_pass46 = run_paired_audit(
        primary_report=loso_report_path,
        primary_name="pass47-repaired-a3-control-expanded",
        anchor_report=pass46_report_path,
        anchor_name="pass46-repaired-a3-no-shape-plus-bursts-per-episode",
        out_json=pass47_vs_pass46_json,
        out_md=pass47_vs_pass46_md,
    )

    pass47_subjects, pass47_summary = load_subject_block(pass47_report)
    pass45_subjects, pass45_summary = load_subject_block(pass45_report)
    pass46_subjects, pass46_summary = load_subject_block(pass46_report)

    pass45_highest_control_subject, pass45_highest_control_score = highest_control(pass45_subjects, controls=["n3", "n5", "n11"])
    pass46_highest_control_subject, pass46_highest_control_score = highest_control(pass46_subjects, controls=["n3", "n5", "n11"])
    pass47_highest_control_subject, pass47_highest_control_score = highest_control(pass47_subjects, controls=CONTROL_SUBJECTS)
    pass47_best_brux_subject, pass47_best_brux_score = best_brux(pass47_subjects)
    pass45_margin = best_brux_minus_highest_control(pass45_subjects, controls=["n3", "n5", "n11"])
    pass46_margin = best_brux_minus_highest_control(pass46_subjects, controls=["n3", "n5", "n11"])
    pass47_margin = best_brux_minus_highest_control(pass47_subjects, controls=CONTROL_SUBJECTS)
    pass45_brux2_gap = float(pass45_subjects["brux2"]["mean_score"] - pass45_highest_control_score)
    pass46_brux2_gap = float(pass46_subjects["brux2"]["mean_score"] - pass46_highest_control_score)
    pass47_brux2_gap = float(pass47_subjects["brux2"]["mean_score"] - pass47_highest_control_score)
    verdict, a1_replication_note = choose_verdict(
        summary=pass47_summary,
        subjects=pass47_subjects,
        pass45_margin=pass45_margin,
        pass46_margin=pass46_margin,
    )

    new_controls = [
        {
            "subject_id": subject_id,
            "mean_score": float(pass47_subjects[subject_id]["mean_score"]),
            "predicted_label": pass47_subjects[subject_id]["predicted_label"],
        }
        for subject_id in ["n1", "n2"]
    ]

    result = {
        "pass47": {
            "subject_ids": SUBJECT_IDS,
            "full_candidate_counts_by_subject": counts_by_subject(pd.read_csv(full_pool_path)),
            "full_candidate_row_count": int(len(pd.read_csv(full_pool_path))),
            "selected_counts_by_subject": counts_by_subject(selected_df),
            "selected_row_count": int(len(selected_df)),
            "final_counts_by_subject": counts_by_subject(pass47_df),
            "final_row_count": int(len(pass47_df)),
            "selector_report": selector_report,
            "event_reference": event_reference,
            "table_build": table_build,
            "subject_summary": pass47_summary,
            "feature_count": int(pass47_report.get("feature_count", 0)),
            "feature_selection": pass47_report.get("feature_selection", {}),
        },
        "anchors": {
            "pass45": {
                "subject_summary": pass45_summary,
                "best_brux_minus_highest_control": pass45_margin,
                "highest_control_subject": pass45_highest_control_subject,
                "highest_control_score": pass45_highest_control_score,
                "brux2_minus_highest_control": pass45_brux2_gap,
            },
            "pass46": {
                "subject_summary": pass46_summary,
                "best_brux_minus_highest_control": pass46_margin,
                "highest_control_subject": pass46_highest_control_subject,
                "highest_control_score": pass46_highest_control_score,
                "brux2_minus_highest_control": pass46_brux2_gap,
            },
        },
        "paired_audits": {
            "pass45": pass47_vs_pass45,
            "pass46": pass47_vs_pass46,
        },
        "derived": {
            "pass47_subject_rows": ordered_subject_rows(pass47_subjects),
            "new_controls": new_controls,
            "all_controls_below_threshold": all(pass47_subjects[subject_id]["predicted_label"] == "control" for subject_id in CONTROL_SUBJECTS),
            "pass47_highest_control_subject": pass47_highest_control_subject,
            "pass47_highest_control_score": pass47_highest_control_score,
            "pass47_best_brux_subject": pass47_best_brux_subject,
            "pass47_best_brux_score": pass47_best_brux_score,
            "pass47_best_brux_minus_highest_control": pass47_margin,
            "pass47_brux2_minus_highest_control": pass47_brux2_gap,
            "shared_vs_pass45_rows": shared_subject_deltas(pass47_subjects, pass45_subjects),
            "shared_vs_pass46_rows": shared_subject_deltas(pass47_subjects, pass46_subjects),
            "verdict": verdict,
            "a1_replication_note": a1_replication_note,
        },
    }

    summary_json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary_md_path.write_text(render_markdown(result), encoding="utf-8")


if __name__ == "__main__":
    main()
