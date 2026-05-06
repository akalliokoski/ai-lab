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
)
from audit_percentile_band_channel_gap import select_feature_columns
from run_pass34_record_relative_emg_audit import (
    BASE_EXCLUDE_REGEXES,
    EPSILON,
    RELATIVE_FEATURES,
    build_record_relative_table,
)
from run_pass36_record_relative_shape_composition_audit import build_composed_table

PASS_NUMBER = 38
TARGET_FEATURE = "envelope_cv"
Q90_MULTIPLIER = 0.5
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


def apply_envelope_cv_scale_floor(*, raw_df: pd.DataFrame, relative_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    transformed = relative_df.copy()
    per_subject: dict[str, dict[str, float]] = {}

    for subject_id, subject_index in transformed.groupby("subject_id").groups.items():
        raw_values = raw_df.loc[subject_index, TARGET_FEATURE]
        median = float(raw_values.median())
        abs_dev = (raw_values - median).abs()
        mad = float(abs_dev.median())
        q90_abs_dev = float(abs_dev.quantile(0.9))
        floor_value = float(Q90_MULTIPLIER * q90_abs_dev)
        scale_used = max(mad, floor_value, EPSILON)
        transformed.loc[subject_index, TARGET_FEATURE] = (raw_values - median) / scale_used
        per_subject[str(subject_id)] = {
            "median": median,
            "mad": mad,
            "q90_abs_dev": q90_abs_dev,
            "floor_multiplier": Q90_MULTIPLIER,
            "floor_value": floor_value,
            "scale_used": float(scale_used),
        }

    return transformed, {
        "target_feature": TARGET_FEATURE,
        "floor_multiplier": Q90_MULTIPLIER,
        "floor_formula": f"max(MAD, {Q90_MULTIPLIER} * q90(|x - median|), {EPSILON})",
        "per_subject": per_subject,
    }


def subject_score_triples(*, pass36_subjects: dict[str, Any], pass37_subjects: dict[str, Any], pass38_subjects: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for subject_id in SUBJECT_IDS:
        rows.append(
            {
                "subject_id": subject_id,
                "pass36_score": float(pass36_subjects[subject_id]["mean_score"]),
                "pass37_score": float(pass37_subjects[subject_id]),
                "pass38_score": float(pass38_subjects[subject_id]["mean_score"]),
                "delta_vs_pass36": float(pass38_subjects[subject_id]["mean_score"] - pass36_subjects[subject_id]["mean_score"]),
                "delta_vs_pass37": float(pass38_subjects[subject_id]["mean_score"] - pass37_subjects[subject_id]),
                "pass36_predicted_label": pass36_subjects[subject_id]["predicted_label"],
                "pass38_predicted_label": pass38_subjects[subject_id]["predicted_label"],
            }
        )
    return rows


def summarize_early_rows(*, rows: list[dict[str, Any]]) -> dict[str, Any]:
    early = rows[:3]
    return {
        "mean_score": float(sum(row["score"] for row in early) / len(early)),
        "amp_disp_mean": float(sum(row["amp_disp_contrib"] for row in early) / len(early)),
    }


def early_window_deltas(*, pass36_rows: list[dict[str, Any]], pass37_rows: list[dict[str, Any]], pass38_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deltas = []
    for row36, row37, row38 in zip(pass36_rows[:3], pass37_rows[:3], pass38_rows[:3], strict=True):
        deltas.append(
            {
                "time_match_rank": int(row36["time_match_rank"]),
                "window_index": int(row36["window_index"]),
                "start_s": float(row36["start_s"]),
                "pass36_score": float(row36["score"]),
                "pass37_score": float(row37["score"]),
                "pass38_score": float(row38["score"]),
                "pass36_amp_disp": float(row36["amp_disp_contrib"]),
                "pass37_amp_disp": float(row37["amp_disp_contrib"]),
                "pass38_amp_disp": float(row38["amp_disp_contrib"]),
                "pass38_shape": float(row38["shape_contrib"]),
                "pass38_other": float(row38["other_contrib"]),
            }
        )
    return deltas


def render_subject_score_lines(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{row['subject_id']}`: pass36 `{row['pass36_score']:.3f}` -> pass37 `{row['pass37_score']:.3f}` -> pass38 `{row['pass38_score']:.3f}` "
        f"| delta vs pass36 `{row['delta_vs_pass36']:+.3f}` | delta vs pass37 `{row['delta_vs_pass37']:+.3f}` "
        f"| predicted `{row['pass36_predicted_label']}` -> `{row['pass38_predicted_label']}`"
        for row in rows
    )


def render_early_delta_lines(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- rank `{row['time_match_rank']}` | window `{row['window_index']}` | start `{row['start_s']:.0f}s` | "
        f"score pass36 `{format_score(row['pass36_score'])}` -> pass37 `{format_score(row['pass37_score'])}` -> pass38 `{format_score(row['pass38_score'])}` | "
        f"amp/disp pass36 `{row['pass36_amp_disp']:+.3f}` -> pass37 `{row['pass37_amp_disp']:+.3f}` -> pass38 `{row['pass38_amp_disp']:+.3f}` | "
        f"pass38 shape `{row['pass38_shape']:+.3f}` | pass38 other `{row['pass38_other']:+.3f}`"
        for row in rows
    )


def render_markdown(report: dict[str, Any]) -> str:
    pass36_summary = report["anchors"]["pass36"]["subject_summary"]
    pass37_summary = report["anchors"]["pass37"]["subject_summary"]
    pass38_summary = report["pass38"]["subject_summary"]
    pass36_early = report["anchors"]["pass36"]["brux1_early_summary"]
    pass37_early = report["anchors"]["pass37"]["brux1_early_summary"]
    pass38_early = report["pass38"]["brux1_early_summary"]
    return f"""# Pass {PASS_NUMBER} — bounded envelope-CV robust-scale-floor audit on the repaired EMG scaffold

Date: 2026-05-05
Status: bounded post-pass37 representation audit completed. One tiny earlier-stage change was tested inside the pass34-style record-relative transform before the fixed pass35 shape merge: recompute only `{TARGET_FEATURE}` with the scale floor `{report['transform_floor']['floor_formula']}` while keeping selected rows, subject set, train-time exclusions, shape block, model family, and evaluation contract fixed.

## Hypothesis

The remaining catastrophic early `brux1` collapse is not just a post-table outlier problem. Inside the pass34-style record-relative transform, `{TARGET_FEATURE}` appears to be over-amplified because its within-record `MAD` is too small relative to the same subject's sparse high-CV tail. If `{TARGET_FEATURE}` uses a bounded tail-aware robust-scale floor `max(MAD, {Q90_MULTIPLIER} * q90(|x - median|))`, the early `brux1` trio should be penalized less aggressively without reopening the repaired `n3` / `n5` / `n11` control surface.

## Exact tiny change

- Start from the existing pass28 repaired `EMG1-EMG2` `A1-only` percentile-band feature CSV and rebuild the pass34 record-relative table.
- Keep the pass34 retained-feature list fixed: `{', '.join(RELATIVE_FEATURES)}`.
- Keep pass35 shape merge fixed after the record-relative step.
- Override only `{TARGET_FEATURE}` after the standard pass34 transform with: `z := (x - median_subject_feature) / max(MAD_subject_feature, {Q90_MULTIPLIER} * q90(|x - median_subject_feature|), {EPSILON})`.
- Leave every other retained feature and every evaluation setting unchanged.

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass38_envelope_cv_scale_floor_audit.py`
- Pass38 feature table: `projects/bruxism-cap/data/window_features_pass38_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_envcvfloor.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass38-emg-a1-pct10-90-record-relative-shape-envcvfloor.json`
- Summary JSON: `projects/bruxism-cap/reports/pass38-envelope-cv-scale-floor-audit.json`
- Summary report: `projects/bruxism-cap/reports/pass38-envelope-cv-scale-floor-audit.md`

## Apples-to-apples comparison against unchanged pass36 and pass37

### Scaffold parity
- pass36 rows per subject: `{report['anchors']['pass36']['counts_by_subject']}`
- pass37 rows per subject: `{report['anchors']['pass37']['counts_by_subject']}`
- pass38 rows per subject: `{report['pass38']['counts_by_subject']}`
- train-time exclusions unchanged: `{report['selection_excluded_columns']}`
- pass38 modified transform feature only: `{TARGET_FEATURE}`

### Subject-level LOSO summary
- pass36 balanced accuracy: `{pass36_summary['balanced_accuracy']:.3f}`
- pass37 balanced accuracy: `{pass37_summary['balanced_accuracy']:.3f}`
- pass38 balanced accuracy: `{pass38_summary['balanced_accuracy']:.3f}`
- pass36 sensitivity: `{pass36_summary['sensitivity']:.3f}`
- pass37 sensitivity: `{pass37_summary['sensitivity']:.3f}`
- pass38 sensitivity: `{pass38_summary['sensitivity']:.3f}`
- pass36 specificity: `{pass36_summary['specificity']:.3f}`
- pass37 specificity: `{pass37_summary['specificity']:.3f}`
- pass38 specificity: `{pass38_summary['specificity']:.3f}`

Subject score deltas:
{render_subject_score_lines(report['derived']['subject_score_triples'])}

## What happened to the early `brux1` trio

- early ranks `1-3` mean score: pass36 `{format_score(pass36_early['mean_score'])}` -> pass37 `{format_score(pass37_early['mean_score'])}` -> pass38 `{format_score(pass38_early['mean_score'])}`
- early ranks `1-3` amp/disp mean: pass36 `{pass36_early['amp_disp_mean']:+.3f}` -> pass37 `{pass37_early['amp_disp_mean']:+.3f}` -> pass38 `{pass38_early['amp_disp_mean']:+.3f}`
- pass38 mid ranks `4-7` mean score: `{report['pass38']['subjects_audit']['brux1']['grouped']['mid_ranks_4_7']['mean_score']:.3f}`
- pass38 late ranks `8-10` mean score: `{report['pass38']['subjects_audit']['brux1']['grouped']['late_ranks_8_10']['mean_score']:.3f}`

Early-window detail:
{render_early_delta_lines(report['derived']['early_brux1_window_deltas'])}

## Did `brux1` improve without reopening `n3` / `n5` / `n11`?

Only slightly, and not enough to beat the simpler pass37 clip.

- `brux1` rises from `{report['anchors']['pass36']['subjects_scores']['brux1']:.3f}` on pass36 to `{report['pass38']['subjects_scores']['brux1']:.3f}` on pass38 (`{report['derived']['subject_score_triples'][0]['delta_vs_pass36']:+.3f}`), so the earlier-stage floor helps a little.
- `n3` stays below `brux1` on pass38 (`brux1 - n3 = {report['derived']['brux1_minus_n3']:+.3f}`), so the old `n3` reversal does not reopen.
- `n5` and `n11` stay above `brux1` by wide margins (`n5 - brux1 = {report['derived']['n5_minus_brux1']:+.3f}`, `n11 - brux1 = {report['derived']['n11_minus_brux1']:+.3f}`), so the control-side bottleneck is still active.
- Compared with pass37, pass38 is weaker on the target subject: `brux1` falls from `{report['anchors']['pass37']['subjects_scores']['brux1']:.3f}` to `{report['pass38']['subjects_scores']['brux1']:.3f}` while `n5` and `n11` move back upward.

## Verdict

This earlier-stage robust-scale-floor idea is directionally compatible with the current scaffold, but it is too weak and too narrow to materially change the benchmark. It improves `brux1` slightly versus pass36 (`0.112` -> `{report['pass38']['subjects_scores']['brux1']:.3f}`) and preserves the repaired subject-level verdict (`0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity), but it does not beat the simpler pass37 post-table clip and it leaves the early `brux1` trio catastrophically close to zero. That means the remaining instability is probably not explained by `{TARGET_FEATURE}` scale alone.

## Safest next bounded benchmark increment

Keep the repaired five-subject scaffold fixed again, but stay inside the same record-relative amplitude family and widen only one notch beyond this single-feature floor. The safest next increment is to test one equally bounded multi-feature earlier-stage audit that applies the same style of robust-scale floor to `{TARGET_FEATURE}` together with one of the two stronger recurring offenders (`rectified_std` or `mean`), while keeping the pass35 shape merge, selected rows, and evaluation contract fixed.

## Explicitly rejected broader move

Rejected move: channel pivot, broad feature expansion, or privacy / LLM branch activation.

Why rejected:
- this audit kept the question narrow and shows the benchmark is still explainable on the current EMG scaffold,
- the result is informative but small, so broadening now would blur whether the remaining failure is a single-feature scale issue or a slightly wider record-relative amplitude construction issue,
- pass38 does not deliver a stabilization handoff point yet, so the future branches should remain gated.
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    reports_dir = root / "reports"

    pass28_features = data_dir / "window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv"
    pass35_features = data_dir / "window_features_pass35_emg_s2_mcap_a1_only_pct10_90_timepos10_shape.csv"
    pass36_report_path = reports_dir / "loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json"
    pass36_audit_path = reports_dir / "pass36-brux1-vs-n5-n11-fold-audit.json"
    pass37_summary_path = reports_dir / "pass37-tiny-amplitude-stabilization-audit.json"
    pass38_features = data_dir / "window_features_pass38_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_envcvfloor.csv"
    pass38_report_path = reports_dir / "loso-cv-pass38-emg-a1-pct10-90-record-relative-shape-envcvfloor.json"
    summary_json_path = reports_dir / "pass38-envelope-cv-scale-floor-audit.json"
    summary_md_path = reports_dir / "pass38-envelope-cv-scale-floor-audit.md"

    pass28_df = pd.read_csv(pass28_features)
    pass35_df = pd.read_csv(pass35_features)
    pass36_report = json.loads(pass36_report_path.read_text(encoding="utf-8"))
    pass36_audit = json.loads(pass36_audit_path.read_text(encoding="utf-8"))
    pass37_summary = json.loads(pass37_summary_path.read_text(encoding="utf-8"))

    pass34_df, _ = build_record_relative_table(
        pass28_df,
        relative_features=RELATIVE_FEATURES,
        epsilon=EPSILON,
    )
    pass38_record_relative_df, floor_summary = apply_envelope_cv_scale_floor(raw_df=pass28_df, relative_df=pass34_df)
    pass38_df, composition_summary = build_composed_table(pass34_df=pass38_record_relative_df, pass35_df=pass35_df)
    pass38_features.parent.mkdir(parents=True, exist_ok=True)
    pass38_df.to_csv(pass38_features, index=False)
    pass38_report = run_train_baseline(features_csv=pass38_features, out_json=pass38_report_path)

    feature_columns, selection_excluded_columns = select_feature_columns(pass38_df, exclude_patterns=EXCLUDE_PATTERNS)
    pass38_subjects_audit, amp_disp_features, shape_features, _other_features = build_subject_rows(pass38_df, feature_columns)
    pass38_pairwise = build_pairwise(pass38_subjects_audit, feature_columns, amp_disp_features, shape_features)

    pass36_subjects_scores = load_subject_scores(pass36_report)
    pass38_subjects_scores = load_subject_scores(pass38_report)
    pass37_subjects_scores = pass37_summary["stabilized"]["subjects_scores"]

    pass36_brux1_rows = pass36_audit["subjects"]["brux1"]["rows_by_time_rank"]
    pass37_brux1_rows = pass37_summary["stabilized"]["subjects_audit"]["brux1"]["rows_by_time_rank"]
    pass38_brux1_rows = pass38_subjects_audit["brux1"]["rows_by_time_rank"]

    report = {
        "pass": PASS_NUMBER,
        "experiment": "bounded_envelope_cv_record_relative_scale_floor_audit_on_repaired_emg_scaffold",
        "selection_excluded_columns": selection_excluded_columns,
        "transform_floor": floor_summary,
        "composition": composition_summary,
        "anchors": {
            "pass36": {
                "report_path": str(pass36_report_path.resolve()),
                "audit_path": str(pass36_audit_path.resolve()),
                "counts_by_subject": pass28_df["subject_id"].value_counts(sort=False).astype(int).to_dict(),
                "subject_summary": pass36_report["models"]["logreg"]["subject_aggregation"]["summary"],
                "subjects_scores": {subject_id: float(pass36_subjects_scores[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS},
                "brux1_early_summary": summarize_early_rows(rows=pass36_brux1_rows),
            },
            "pass37": {
                "summary_path": str(pass37_summary_path.resolve()),
                "counts_by_subject": pass37_summary["stabilized"]["counts_by_subject"],
                "subject_summary": pass37_summary["stabilized"]["subject_summary"],
                "subjects_scores": {subject_id: float(pass37_subjects_scores[subject_id]) for subject_id in SUBJECT_IDS},
                "brux1_early_summary": summarize_early_rows(rows=pass37_brux1_rows),
            },
        },
        "pass38": {
            "features_csv": str(pass38_features.resolve()),
            "report_path": str(pass38_report_path.resolve()),
            "counts_by_subject": pass38_df["subject_id"].value_counts(sort=False).astype(int).to_dict(),
            "subject_summary": pass38_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "subjects_scores": {subject_id: float(pass38_subjects_scores[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS},
            "subjects_audit": pass38_subjects_audit,
            "pairwise": pass38_pairwise,
            "brux1_early_summary": summarize_early_rows(rows=pass38_brux1_rows),
        },
        "derived": {
            "subject_score_triples": subject_score_triples(
                pass36_subjects=pass36_subjects_scores,
                pass37_subjects=pass37_subjects_scores,
                pass38_subjects=pass38_subjects_scores,
            ),
            "early_brux1_window_deltas": early_window_deltas(
                pass36_rows=pass36_brux1_rows,
                pass37_rows=pass37_brux1_rows,
                pass38_rows=pass38_brux1_rows,
            ),
            "brux1_minus_n3": float(pass38_subjects_scores["brux1"]["mean_score"] - pass38_subjects_scores["n3"]["mean_score"]),
            "n5_minus_brux1": float(pass38_subjects_scores["n5"]["mean_score"] - pass38_subjects_scores["brux1"]["mean_score"]),
            "n11_minus_brux1": float(pass38_subjects_scores["n11"]["mean_score"] - pass38_subjects_scores["brux1"]["mean_score"]),
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
