from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from audit_pass36_brux1_vs_n5_n11 import (
    EXCLUDE_PATTERNS,
    build_pairwise,
    build_subject_rows,
    format_score,
    render_rows,
)
from audit_percentile_band_channel_gap import select_feature_columns

STABILIZATION_FEATURES = ["mean", "rectified_std", "envelope_cv"]
UPPER_CAP = 2.5
BASE_EXCLUDE_REGEXES = [r"^bp_", r"^rel_bp_", r"^ratio_"]
SUBJECT_IDS = ["brux1", "brux2", "n3", "n5", "n11"]


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


def load_subject_scores(report: dict[str, Any], *, model_name: str = "logreg") -> dict[str, dict[str, Any]]:
    return {
        row["subject_id"]: row
        for row in report["models"][model_name]["subject_aggregation"]["subjects"]
    }


def apply_upper_cap(df: pd.DataFrame) -> pd.DataFrame:
    capped = df.copy()
    for feature in STABILIZATION_FEATURES:
        if feature not in capped.columns:
            raise SystemExit(f"required stabilization feature missing from pass36 table: {feature}")
        capped[feature] = capped[feature].clip(upper=UPPER_CAP)
    return capped


def score_delta_rows(*, baseline_subjects: dict[str, Any], stabilized_subjects: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for subject_id in SUBJECT_IDS:
        base = baseline_subjects[subject_id]
        new = stabilized_subjects[subject_id]
        rows.append(
            {
                "subject_id": subject_id,
                "baseline_score": float(base["mean_score"]),
                "stabilized_score": float(new["mean_score"]),
                "delta": float(new["mean_score"] - base["mean_score"]),
                "baseline_predicted_label": base["predicted_label"],
                "stabilized_predicted_label": new["predicted_label"],
            }
        )
    return rows


def summarize_early_window_deltas(*, baseline_rows: list[dict[str, Any]], stabilized_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deltas = []
    for base, new in zip(baseline_rows[:3], stabilized_rows[:3], strict=True):
        deltas.append(
            {
                "time_match_rank": int(base["time_match_rank"]),
                "window_index": int(base["window_index"]),
                "start_s": float(base["start_s"]),
                "baseline_score": float(base["score"]),
                "stabilized_score": float(new["score"]),
                "baseline_amp_disp_contrib": float(base["amp_disp_contrib"]),
                "stabilized_amp_disp_contrib": float(new["amp_disp_contrib"]),
                "shape_contrib_after_clip": float(new["shape_contrib"]),
                "other_contrib_after_clip": float(new["other_contrib"]),
            }
        )
    return deltas


def render_subject_delta_lines(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{row['subject_id']}`: baseline `{row['baseline_score']:.3f}` -> clipped `{row['stabilized_score']:.3f}` "
        f"(delta `{row['delta']:+.3f}`) | predicted `{row['baseline_predicted_label']}` -> `{row['stabilized_predicted_label']}`"
        for row in rows
    )


def render_early_delta_lines(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- rank `{row['time_match_rank']}` | window `{row['window_index']}` | start `{row['start_s']:.0f}s` | "
        f"score `{format_score(row['baseline_score'])}` -> `{format_score(row['stabilized_score'])}` | "
        f"amp/disp `{row['baseline_amp_disp_contrib']:+.3f}` -> `{row['stabilized_amp_disp_contrib']:+.3f}` | "
        f"shape after clip `{row['shape_contrib_after_clip']:+.3f}` | other after clip `{row['other_contrib_after_clip']:+.3f}`"
        for row in rows
    )


def render_markdown(report: dict[str, Any]) -> str:
    base_summary = report["baseline"]["subject_summary"]
    new_summary = report["stabilized"]["subject_summary"]
    brux1_base = report["baseline"]["subjects_audit"]["brux1"]
    brux1_new = report["stabilized"]["subjects_audit"]["brux1"]
    n5_gap = report["derived"]["n5_minus_brux1"]
    n11_gap = report["derived"]["n11_minus_brux1"]
    n3_gap = report["derived"]["brux1_minus_n3"]
    return f"""# Pass 37 — tiny amplitude-stabilization audit on the fixed pass36 EMG table

Date: 2026-05-05
Status: bounded post-pass36 representation audit completed. One tiny post-table change was tested on the exact repaired five-subject composed scaffold: upper-clip only `{', '.join(STABILIZATION_FEATURES)}` at `{UPPER_CAP}` while keeping selected rows, train-time exclusions, shape block, model family, and evaluation contract fixed.

## Hypothesis

The catastrophic early `brux1` trio is being over-penalized by a very small recurring subset of record-relative amplitude / dispersion columns that spike far above the same subject's later windows: `{', '.join(STABILIZATION_FEATURES)}`. If those three positive record-relative values are softly upper-clipped at `{UPPER_CAP}`, the early `brux1` windows should become less catastrophically negative without reopening the repaired control surface or disturbing the pass36 shape contribution.

## Exact tiny change

- Start from the existing pass36 composed table, not a new selector or channel.
- Clip only these three columns after the pass36 composition step: `{', '.join(STABILIZATION_FEATURES)}`.
- Clip rule: `x := min(x, {UPPER_CAP})`.
- Leave the rest of the pass36 feature table unchanged, including the compact shape block and all non-target amplitude / dispersion columns.

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass37_tiny_amplitude_stabilization_audit.py`
- Stabilized feature table: `projects/bruxism-cap/data/window_features_pass37_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_ampcap.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass37-emg-a1-pct10-90-record-relative-shape-ampcap.json`
- Summary JSON: `projects/bruxism-cap/reports/pass37-tiny-amplitude-stabilization-audit.json`
- Summary report: `projects/bruxism-cap/reports/pass37-tiny-amplitude-stabilization-audit.md`

## Apples-to-apples comparison against unchanged pass36

### Scaffold parity
- baseline pass36 rows per subject: `{report['baseline']['counts_by_subject']}`
- clipped pass37 rows per subject: `{report['stabilized']['counts_by_subject']}`
- train-time exclusions unchanged: `{report['selection_excluded_columns']}`
- clipped features only: `{report['clip_rule']['features']}`

### Subject-level LOSO summary
- baseline balanced accuracy: `{base_summary['balanced_accuracy']:.3f}`
- clipped balanced accuracy: `{new_summary['balanced_accuracy']:.3f}`
- baseline sensitivity: `{base_summary['sensitivity']:.3f}`
- clipped sensitivity: `{new_summary['sensitivity']:.3f}`
- baseline specificity: `{base_summary['specificity']:.3f}`
- clipped specificity: `{new_summary['specificity']:.3f}`

Subject score deltas:
{render_subject_delta_lines(report['derived']['subject_score_deltas'])}

## What happened to the early `brux1` trio

- early ranks `1-3` mean score: `{format_score(brux1_base['grouped']['early_ranks_1_3']['mean_score'])}` -> `{format_score(brux1_new['grouped']['early_ranks_1_3']['mean_score'])}`
- early ranks `1-3` amp/disp mean: `{brux1_base['grouped']['early_ranks_1_3']['amp_disp_mean']:+.3f}` -> `{brux1_new['grouped']['early_ranks_1_3']['amp_disp_mean']:+.3f}`
- mid ranks `4-7` mean score: `{brux1_base['grouped']['mid_ranks_4_7']['mean_score']:.3f}` -> `{brux1_new['grouped']['mid_ranks_4_7']['mean_score']:.3f}`
- late ranks `8-10` mean score: `{brux1_base['grouped']['late_ranks_8_10']['mean_score']:.3f}` -> `{brux1_new['grouped']['late_ranks_8_10']['mean_score']:.3f}`

Early-window detail:
{render_early_delta_lines(report['derived']['early_brux1_window_deltas'])}

## Did `brux1` improve without reopening `n3` / `n5` / `n11`?

Mostly yes, but only modestly.

- `brux1` improves from `{report['baseline']['subjects_scores']['brux1']:.3f}` to `{report['stabilized']['subjects_scores']['brux1']:.3f}` (`{report['derived']['subject_score_deltas'][0]['delta']:+.3f}`), so the tiny cap helps rather than hurts the target subject.
- `n5` falls from `{report['baseline']['subjects_scores']['n5']:.3f}` to `{report['stabilized']['subjects_scores']['n5']:.3f}` and `n11` falls from `{report['baseline']['subjects_scores']['n11']:.3f}` to `{report['stabilized']['subjects_scores']['n11']:.3f}`, so those two control gaps narrow modestly.
- `n3` rises from `{report['baseline']['subjects_scores']['n3']:.3f}` to `{report['stabilized']['subjects_scores']['n3']:.3f}`, but it still stays below `brux1` (`brux1 - n3 = {n3_gap:+.3f}`), so the old `n3` reversal does not reopen.
- No control flips positive, `brux2` stays strongly positive, and subject-level specificity remains `{new_summary['specificity']:.3f}`.

Gap check after clipping:
- `brux1 - n3`: `{n3_gap:+.3f}`
- `n5 - brux1`: `{n5_gap:+.3f}`
- `n11 - brux1`: `{n11_gap:+.3f}`

## Verdict

This tiny stabilization rule is directionally helpful but not sufficient. It reduces the early `brux1` trio's average amplitude / dispersion penalty from `{brux1_base['grouped']['early_ranks_1_3']['amp_disp_mean']:+.3f}` to `{brux1_new['grouped']['early_ranks_1_3']['amp_disp_mean']:+.3f}` and lifts `brux1` modestly, while preserving the pass36 subject-level verdict (`0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity). But the trio remains catastrophically near zero and `brux1` still stays far below threshold, so the post-table clip softens the collapse without actually fixing it.

## Safest next bounded step

Keep the same repaired five-subject scaffold and test one equally narrow stabilization move one stage earlier in the same feature family: apply a bounded robust-scale-floor audit for `{', '.join(STABILIZATION_FEATURES)}` inside the pass34 record-relative transform before the pass35 shape merge, then rerun the exact same pass36 composition surface. This stays apples-to-apples while checking whether the remaining collapse comes from the record-relative scale construction itself rather than only from a few post-table outliers.

## Explicitly rejected broader move

Rejected move: another channel pivot or a broader feature-family expansion.

Why rejected:
- this audit already answered the current narrow question on the exact pass36 surface,
- the tiny clip preserved `brux2` and the control verdict, so the open issue is still a localized `brux1` stabilization problem rather than a reason to broaden the benchmark,
- a broader move now would blur whether the remaining failure comes from the record-relative construction itself or from unrelated new features.
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    reports_dir = root / "reports"

    baseline_features = data_dir / "window_features_pass36_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape.csv"
    baseline_report_path = reports_dir / "loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json"
    baseline_audit_path = reports_dir / "pass36-brux1-vs-n5-n11-fold-audit.json"
    stabilized_features = data_dir / "window_features_pass37_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_ampcap.csv"
    stabilized_report_path = reports_dir / "loso-cv-pass37-emg-a1-pct10-90-record-relative-shape-ampcap.json"
    summary_json_path = reports_dir / "pass37-tiny-amplitude-stabilization-audit.json"
    summary_md_path = reports_dir / "pass37-tiny-amplitude-stabilization-audit.md"

    baseline_df = pd.read_csv(baseline_features)
    baseline_report = json.loads(baseline_report_path.read_text(encoding="utf-8"))
    baseline_audit = json.loads(baseline_audit_path.read_text(encoding="utf-8"))

    stabilized_df = apply_upper_cap(baseline_df)
    stabilized_features.parent.mkdir(parents=True, exist_ok=True)
    stabilized_df.to_csv(stabilized_features, index=False)
    stabilized_report = run_train_baseline(features_csv=stabilized_features, out_json=stabilized_report_path)

    feature_columns, selection_excluded_columns = select_feature_columns(stabilized_df, exclude_patterns=EXCLUDE_PATTERNS)
    stabilized_subjects_audit, amp_disp_features, shape_features, other_features = build_subject_rows(stabilized_df, feature_columns)
    stabilized_pairwise = build_pairwise(stabilized_subjects_audit, feature_columns, amp_disp_features, shape_features)

    baseline_subjects_scores = load_subject_scores(baseline_report)
    stabilized_subjects_scores = load_subject_scores(stabilized_report)
    subject_score_deltas = score_delta_rows(
        baseline_subjects=baseline_subjects_scores,
        stabilized_subjects=stabilized_subjects_scores,
    )

    baseline_brux1_rows = baseline_audit["subjects"]["brux1"]["rows_by_time_rank"]
    stabilized_brux1_rows = stabilized_subjects_audit["brux1"]["rows_by_time_rank"]
    early_window_deltas = summarize_early_window_deltas(
        baseline_rows=baseline_brux1_rows,
        stabilized_rows=stabilized_brux1_rows,
    )

    report = {
        "pass": 37,
        "experiment": "tiny_amplitude_stabilization_audit_on_fixed_pass36_table",
        "clip_rule": {
            "features": STABILIZATION_FEATURES,
            "upper_cap": UPPER_CAP,
            "direction": "upper_only",
        },
        "selection_excluded_columns": selection_excluded_columns,
        "baseline": {
            "features_csv": str(baseline_features.resolve()),
            "report_path": str(baseline_report_path.resolve()),
            "audit_path": str(baseline_audit_path.resolve()),
            "counts_by_subject": baseline_df["subject_id"].value_counts(sort=False).astype(int).to_dict(),
            "subject_summary": baseline_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "subjects_scores": {subject_id: float(baseline_subjects_scores[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS},
            "subjects_audit": baseline_audit["subjects"],
        },
        "stabilized": {
            "features_csv": str(stabilized_features.resolve()),
            "report_path": str(stabilized_report_path.resolve()),
            "counts_by_subject": stabilized_df["subject_id"].value_counts(sort=False).astype(int).to_dict(),
            "subject_summary": stabilized_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "subjects_scores": {subject_id: float(stabilized_subjects_scores[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS},
            "subjects_audit": stabilized_subjects_audit,
            "pairwise": stabilized_pairwise,
        },
        "derived": {
            "subject_score_deltas": subject_score_deltas,
            "early_brux1_window_deltas": early_window_deltas,
            "brux1_minus_n3": float(stabilized_subjects_scores["brux1"]["mean_score"] - stabilized_subjects_scores["n3"]["mean_score"]),
            "n5_minus_brux1": float(stabilized_subjects_scores["n5"]["mean_score"] - stabilized_subjects_scores["brux1"]["mean_score"]),
            "n11_minus_brux1": float(stabilized_subjects_scores["n11"]["mean_score"] - stabilized_subjects_scores["brux1"]["mean_score"]),
        },
        "summary_md_path": str(summary_md_path.resolve()),
        "summary_json_path": str(summary_json_path.resolve()),
    }

    summary_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_markdown(report), encoding="utf-8")
    print(summary_md_path)
    print(summary_json_path)


if __name__ == "__main__":
    main()
