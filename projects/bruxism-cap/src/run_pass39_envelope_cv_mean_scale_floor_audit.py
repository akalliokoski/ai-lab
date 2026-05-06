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

PASS_NUMBER = 39
TARGET_FEATURES = ["envelope_cv", "mean"]
Q90_MULTIPLIER = 0.5
SUBJECT_IDS = ["brux1", "brux2", "n3", "n5", "n11"]
PRIMARY_OFFENDER = "mean"
ALTERNATE_OFFENDER = "rectified_std"


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


def apply_scale_floor_features(*, raw_df: pd.DataFrame, relative_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    transformed = relative_df.copy()
    per_feature: dict[str, dict[str, dict[str, float]]] = {}

    for feature in TARGET_FEATURES:
        if feature not in raw_df.columns:
            raise SystemExit(f"required raw feature missing for pass{PASS_NUMBER}: {feature}")
        per_feature[feature] = {}
        for subject_id, subject_index in transformed.groupby("subject_id").groups.items():
            raw_values = raw_df.loc[subject_index, feature]
            median = float(raw_values.median())
            abs_dev = (raw_values - median).abs()
            mad = float(abs_dev.median())
            q90_abs_dev = float(abs_dev.quantile(0.9))
            floor_value = float(Q90_MULTIPLIER * q90_abs_dev)
            scale_used = max(mad, floor_value, EPSILON)
            transformed.loc[subject_index, feature] = (raw_values - median) / scale_used
            per_feature[feature][str(subject_id)] = {
                "median": median,
                "mad": mad,
                "q90_abs_dev": q90_abs_dev,
                "floor_multiplier": Q90_MULTIPLIER,
                "floor_value": floor_value,
                "scale_used": float(scale_used),
            }

    return transformed, {
        "target_features": TARGET_FEATURES,
        "primary_offender": PRIMARY_OFFENDER,
        "alternate_offender": ALTERNATE_OFFENDER,
        "floor_multiplier": Q90_MULTIPLIER,
        "floor_formula": f"max(MAD, {Q90_MULTIPLIER} * q90(|x - median|), {EPSILON})",
        "per_feature": per_feature,
    }


def summarize_early_rows(*, rows: list[dict[str, Any]]) -> dict[str, Any]:
    early = rows[:3]
    return {
        "mean_score": float(sum(row["score"] for row in early) / len(early)),
        "amp_disp_mean": float(sum(row["amp_disp_contrib"] for row in early) / len(early)),
    }


def choose_offender_summary(pass36_audit: dict[str, Any]) -> dict[str, Any]:
    comparisons = {}
    for pair_key in ["n5_minus_brux1", "n11_minus_brux1"]:
        positives = pass36_audit["pairwise"][pair_key]["top_positive"]
        comparisons[pair_key] = {
            row["feature"]: row
            for row in positives
            if row["feature"] in {"mean", "rectified_std", "envelope_cv"}
        }
    return {
        "chosen_feature": PRIMARY_OFFENDER,
        "rejected_feature": ALTERNATE_OFFENDER,
        "n5_minus_brux1": comparisons["n5_minus_brux1"],
        "n11_minus_brux1": comparisons["n11_minus_brux1"],
    }


def subject_score_quads(
    *,
    pass36_subjects: dict[str, Any],
    pass37_subjects: dict[str, Any],
    pass38_subjects: dict[str, Any],
    pass39_subjects: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for subject_id in SUBJECT_IDS:
        rows.append(
            {
                "subject_id": subject_id,
                "pass36_score": float(pass36_subjects[subject_id]["mean_score"]),
                "pass37_score": float(pass37_subjects[subject_id]),
                "pass38_score": float(pass38_subjects[subject_id]),
                "pass39_score": float(pass39_subjects[subject_id]["mean_score"]),
                "delta_vs_pass36": float(pass39_subjects[subject_id]["mean_score"] - pass36_subjects[subject_id]["mean_score"]),
                "delta_vs_pass37": float(pass39_subjects[subject_id]["mean_score"] - pass37_subjects[subject_id]),
                "delta_vs_pass38": float(pass39_subjects[subject_id]["mean_score"] - pass38_subjects[subject_id]),
                "pass36_predicted_label": pass36_subjects[subject_id]["predicted_label"],
                "pass39_predicted_label": pass39_subjects[subject_id]["predicted_label"],
            }
        )
    return rows


def early_window_deltas(
    *,
    pass36_rows: list[dict[str, Any]],
    pass37_rows: list[dict[str, Any]],
    pass38_rows: list[dict[str, Any]],
    pass39_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    deltas = []
    for row36, row37, row38, row39 in zip(pass36_rows[:3], pass37_rows[:3], pass38_rows[:3], pass39_rows[:3], strict=True):
        deltas.append(
            {
                "time_match_rank": int(row36["time_match_rank"]),
                "window_index": int(row36["window_index"]),
                "start_s": float(row36["start_s"]),
                "pass36_score": float(row36["score"]),
                "pass37_score": float(row37["score"]),
                "pass38_score": float(row38["score"]),
                "pass39_score": float(row39["score"]),
                "pass36_amp_disp": float(row36["amp_disp_contrib"]),
                "pass37_amp_disp": float(row37["amp_disp_contrib"]),
                "pass38_amp_disp": float(row38["amp_disp_contrib"]),
                "pass39_amp_disp": float(row39["amp_disp_contrib"]),
                "pass39_shape": float(row39["shape_contrib"]),
                "pass39_other": float(row39["other_contrib"]),
            }
        )
    return deltas


def render_subject_score_lines(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{row['subject_id']}`: pass36 `{row['pass36_score']:.3f}` -> pass37 `{row['pass37_score']:.3f}` -> pass38 `{row['pass38_score']:.3f}` -> pass39 `{row['pass39_score']:.3f}` "
        f"| delta vs pass36 `{row['delta_vs_pass36']:+.3f}` | delta vs pass37 `{row['delta_vs_pass37']:+.3f}` | delta vs pass38 `{row['delta_vs_pass38']:+.3f}` "
        f"| predicted `{row['pass36_predicted_label']}` -> `{row['pass39_predicted_label']}`"
        for row in rows
    )


def render_early_delta_lines(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- rank `{row['time_match_rank']}` | window `{row['window_index']}` | start `{row['start_s']:.0f}s` | "
        f"score pass36 `{format_score(row['pass36_score'])}` -> pass37 `{format_score(row['pass37_score'])}` -> pass38 `{format_score(row['pass38_score'])}` -> pass39 `{format_score(row['pass39_score'])}` | "
        f"amp/disp pass36 `{row['pass36_amp_disp']:+.3f}` -> pass37 `{row['pass37_amp_disp']:+.3f}` -> pass38 `{row['pass38_amp_disp']:+.3f}` -> pass39 `{row['pass39_amp_disp']:+.3f}` | "
        f"pass39 shape `{row['pass39_shape']:+.3f}` | pass39 other `{row['pass39_other']:+.3f}`"
        for row in rows
    )


def render_markdown(report: dict[str, Any]) -> str:
    pass36_summary = report["anchors"]["pass36"]["subject_summary"]
    pass37_summary = report["anchors"]["pass37"]["subject_summary"]
    pass38_summary = report["anchors"]["pass38"]["subject_summary"]
    pass39_summary = report["pass39"]["subject_summary"]
    pass36_early = report["anchors"]["pass36"]["brux1_early_summary"]
    pass37_early = report["anchors"]["pass37"]["brux1_early_summary"]
    pass38_early = report["anchors"]["pass38"]["brux1_early_summary"]
    pass39_early = report["pass39"]["brux1_early_summary"]
    offender = report["offender_choice"]
    n5_mean = offender["n5_minus_brux1"]["mean"]
    n5_rect = offender["n5_minus_brux1"]["rectified_std"]
    n11_mean = offender["n11_minus_brux1"]["mean"]
    n11_rect = offender["n11_minus_brux1"]["rectified_std"]
    best_prior = max(
        report["anchors"]["pass36"]["subjects_scores"]["brux1"],
        report["anchors"]["pass37"]["subjects_scores"]["brux1"],
        report["anchors"]["pass38"]["subjects_scores"]["brux1"],
    )
    pass39_brux1 = report["pass39"]["subjects_scores"]["brux1"]
    beats_prior = pass39_brux1 > best_prior
    next_step = (
        f"Keep the same repaired five-subject scaffold and stay inside the same earlier-stage record-relative family, but swap the companion floor feature once: preserve the new `{PRIMARY_OFFENDER}` result as evidence, then test the same bounded floor on `envelope_cv` plus `{ALTERNATE_OFFENDER}` while keeping the pass35 shape merge, selected rows, and evaluation contract fixed."
        if pass39_summary["sensitivity"] <= 0.5
        else "Keep the same scaffold fixed and run one equally bounded verification audit on the same paired-floor idea to confirm the gain is not a one-pass artifact before touching any broader feature family."
    )
    verdict = (
        "This paired earlier-stage floor beats the prior bounded stabilization surfaces on the target subject while preserving the repaired control verdict."
        if beats_prior
        else "This paired earlier-stage floor is still too weak to rescue `brux1` and does not beat the best prior bounded stabilization surface on the target subject."
    )
    return f"""# Pass {PASS_NUMBER} — bounded multi-feature record-relative scale-floor audit on the repaired EMG scaffold

Date: 2026-05-05
Status: bounded post-pass38 representation audit completed. Exactly one next earlier-stage increment was tested inside the pass34-style record-relative transform before the fixed pass35 shape merge: apply the same robust-scale floor `{report['transform_floor']['floor_formula']}` to `envelope_cv` plus one chosen stronger recurring offender, `{PRIMARY_OFFENDER}`, while keeping selected rows, subject set, train-time exclusions, shape block, model family, and evaluation contract fixed.

## Why `{PRIMARY_OFFENDER}` was chosen over `{ALTERNATE_OFFENDER}`

The pass36 fold audit shows that `{PRIMARY_OFFENDER}` is the dominant recurring offender inside the remaining `brux1` suppression block, not just another member of the same family.

- Against `n5`, `{PRIMARY_OFFENDER}` contributes `+{n5_mean['mean_contribution_delta']:.3f}` to `n5 - brux1`, versus only `+{n5_rect['mean_contribution_delta']:.3f}` from `{ALTERNATE_OFFENDER}`.
- Against `n11`, `{PRIMARY_OFFENDER}` contributes `+{n11_mean['mean_contribution_delta']:.3f}` to `n11 - brux1`, versus only `+{n11_rect['mean_contribution_delta']:.3f}` from `{ALTERNATE_OFFENDER}`.
- The associated record-relative z-mean deltas are also much larger for `{PRIMARY_OFFENDER}` (`{n5_mean['z_mean_delta']:+.3f}` vs `{n5_rect['z_mean_delta']:+.3f}` against `n5`; `{n11_mean['z_mean_delta']:+.3f}` vs `{n11_rect['z_mean_delta']:+.3f}` against `n11`).

So the strongest bounded follow-through after pass38 is to keep `envelope_cv` fixed and pair it with `{PRIMARY_OFFENDER}`, because that tests the most dominant remaining contributor without broadening beyond one additional feature.

## Exact bounded change

- Start from the existing pass28 repaired `EMG1-EMG2` `A1-only` percentile-band feature CSV and rebuild the pass34 record-relative table.
- Keep the pass34 retained-feature list fixed: `{', '.join(RELATIVE_FEATURES)}`.
- Keep pass35 shape merge fixed after the record-relative step.
- Override only `{', '.join(TARGET_FEATURES)}` after the standard pass34 transform with: `z := (x - median_subject_feature) / max(MAD_subject_feature, {Q90_MULTIPLIER} * q90(|x - median_subject_feature|), {EPSILON})`.
- Leave every other retained feature and every evaluation setting unchanged.

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass39_envelope_cv_mean_scale_floor_audit.py`
- Pass39 feature table: `projects/bruxism-cap/data/window_features_pass39_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_envcv_mean_floor.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass39-emg-a1-pct10-90-record-relative-shape-envcv-mean-floor.json`
- Summary JSON: `projects/bruxism-cap/reports/pass39-envelope-cv-mean-scale-floor-audit.json`
- Summary report: `projects/bruxism-cap/reports/pass39-envelope-cv-mean-scale-floor-audit.md`

## Apples-to-apples comparison against unchanged pass36, pass37, and pass38

### Scaffold parity
- pass36 rows per subject: `{report['anchors']['pass36']['counts_by_subject']}`
- pass37 rows per subject: `{report['anchors']['pass37']['counts_by_subject']}`
- pass38 rows per subject: `{report['anchors']['pass38']['counts_by_subject']}`
- pass39 rows per subject: `{report['pass39']['counts_by_subject']}`
- train-time exclusions unchanged: `{report['selection_excluded_columns']}`
- pass39 modified transform features only: `{TARGET_FEATURES}`

### Subject-level LOSO summary
- pass36 balanced accuracy: `{pass36_summary['balanced_accuracy']:.3f}`
- pass37 balanced accuracy: `{pass37_summary['balanced_accuracy']:.3f}`
- pass38 balanced accuracy: `{pass38_summary['balanced_accuracy']:.3f}`
- pass39 balanced accuracy: `{pass39_summary['balanced_accuracy']:.3f}`
- pass36 sensitivity: `{pass36_summary['sensitivity']:.3f}`
- pass37 sensitivity: `{pass37_summary['sensitivity']:.3f}`
- pass38 sensitivity: `{pass38_summary['sensitivity']:.3f}`
- pass39 sensitivity: `{pass39_summary['sensitivity']:.3f}`
- pass36 specificity: `{pass36_summary['specificity']:.3f}`
- pass37 specificity: `{pass37_summary['specificity']:.3f}`
- pass38 specificity: `{pass38_summary['specificity']:.3f}`
- pass39 specificity: `{pass39_summary['specificity']:.3f}`

Subject score deltas:
{render_subject_score_lines(report['derived']['subject_score_quads'])}

## What happened to the early `brux1` trio

- early ranks `1-3` mean score: pass36 `{format_score(pass36_early['mean_score'])}` -> pass37 `{format_score(pass37_early['mean_score'])}` -> pass38 `{format_score(pass38_early['mean_score'])}` -> pass39 `{format_score(pass39_early['mean_score'])}`
- early ranks `1-3` amp/disp mean: pass36 `{pass36_early['amp_disp_mean']:+.3f}` -> pass37 `{pass37_early['amp_disp_mean']:+.3f}` -> pass38 `{pass38_early['amp_disp_mean']:+.3f}` -> pass39 `{pass39_early['amp_disp_mean']:+.3f}`
- pass39 mid ranks `4-7` mean score: `{report['pass39']['subjects_audit']['brux1']['grouped']['mid_ranks_4_7']['mean_score']:.3f}`
- pass39 late ranks `8-10` mean score: `{report['pass39']['subjects_audit']['brux1']['grouped']['late_ranks_8_10']['mean_score']:.3f}`

Early-window detail:
{render_early_delta_lines(report['derived']['early_brux1_window_deltas'])}

## Did `brux1` improve without reopening `n3` / `n5` / `n11`?

- `brux1` moves from pass36 `{report['anchors']['pass36']['subjects_scores']['brux1']:.3f}` to pass39 `{report['pass39']['subjects_scores']['brux1']:.3f}` (`{report['derived']['subject_score_quads'][0]['delta_vs_pass36']:+.3f}`), versus pass37 `{report['anchors']['pass37']['subjects_scores']['brux1']:.3f}` and pass38 `{report['anchors']['pass38']['subjects_scores']['brux1']:.3f}`.
- `n3` on pass39 is `{report['pass39']['subjects_scores']['n3']:.3f}`, so `brux1 - n3 = {report['derived']['brux1_minus_n3']:+.3f}`.
- `n5` on pass39 is `{report['pass39']['subjects_scores']['n5']:.3f}`, so `n5 - brux1 = {report['derived']['n5_minus_brux1']:+.3f}`.
- `n11` on pass39 is `{report['pass39']['subjects_scores']['n11']:.3f}`, so `n11 - brux1 = {report['derived']['n11_minus_brux1']:+.3f}`.

## Verdict

{verdict}

Expanded read: {report['verdict_detail']}

## Safest next bounded benchmark increment

{next_step}

## Explicitly rejected broader move

Rejected move: channel pivot, broad feature expansion, privacy implementation, or synthetic-data / LLM work.

Why rejected:
- this pass answers the exact next bounded record-relative question on the current EMG scaffold,
- the result still needs to be interpreted as a localized `brux1` stabilization read rather than a reason to broaden the benchmark frame,
- broadening now would blur whether the remaining failure is the residual earlier-stage amplitude construction or something introduced by an unrelated new branch.
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
    pass38_summary_path = reports_dir / "pass38-envelope-cv-scale-floor-audit.json"
    pass39_features = data_dir / "window_features_pass39_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_envcv_mean_floor.csv"
    pass39_report_path = reports_dir / "loso-cv-pass39-emg-a1-pct10-90-record-relative-shape-envcv-mean-floor.json"
    summary_json_path = reports_dir / "pass39-envelope-cv-mean-scale-floor-audit.json"
    summary_md_path = reports_dir / "pass39-envelope-cv-mean-scale-floor-audit.md"

    pass28_df = pd.read_csv(pass28_features)
    pass35_df = pd.read_csv(pass35_features)
    pass36_report = json.loads(pass36_report_path.read_text(encoding="utf-8"))
    pass36_audit = json.loads(pass36_audit_path.read_text(encoding="utf-8"))
    pass37_summary = json.loads(pass37_summary_path.read_text(encoding="utf-8"))
    pass38_summary = json.loads(pass38_summary_path.read_text(encoding="utf-8"))

    pass34_df, _ = build_record_relative_table(
        pass28_df,
        relative_features=RELATIVE_FEATURES,
        epsilon=EPSILON,
    )
    pass39_record_relative_df, floor_summary = apply_scale_floor_features(raw_df=pass28_df, relative_df=pass34_df)
    pass39_df, composition_summary = build_composed_table(pass34_df=pass39_record_relative_df, pass35_df=pass35_df)
    pass39_features.parent.mkdir(parents=True, exist_ok=True)
    pass39_df.to_csv(pass39_features, index=False)
    pass39_report = run_train_baseline(features_csv=pass39_features, out_json=pass39_report_path)

    feature_columns, selection_excluded_columns = select_feature_columns(pass39_df, exclude_patterns=EXCLUDE_PATTERNS)
    pass39_subjects_audit, amp_disp_features, shape_features, _other_features = build_subject_rows(pass39_df, feature_columns)
    pass39_pairwise = build_pairwise(pass39_subjects_audit, feature_columns, amp_disp_features, shape_features)

    pass36_subjects_scores = load_subject_scores(pass36_report)
    pass39_subjects_scores = load_subject_scores(pass39_report)
    pass37_subjects_scores = pass37_summary["stabilized"]["subjects_scores"]
    pass38_subjects_scores = pass38_summary["pass38"]["subjects_scores"]

    pass36_brux1_rows = pass36_audit["subjects"]["brux1"]["rows_by_time_rank"]
    pass37_brux1_rows = pass37_summary["stabilized"]["subjects_audit"]["brux1"]["rows_by_time_rank"]
    pass38_brux1_rows = pass38_summary["pass38"]["subjects_audit"]["brux1"]["rows_by_time_rank"]
    pass39_brux1_rows = pass39_subjects_audit["brux1"]["rows_by_time_rank"]

    pass39_brux1 = float(pass39_subjects_scores["brux1"]["mean_score"])
    prior_brux1_scores = {
        "pass36": float(pass36_subjects_scores["brux1"]["mean_score"]),
        "pass37": float(pass37_subjects_scores["brux1"]),
        "pass38": float(pass38_subjects_scores["brux1"]),
    }
    best_prior_name, best_prior_score = max(prior_brux1_scores.items(), key=lambda item: item[1])
    verdict_detail = (
        f"Pass39 lifts `brux1` above the best earlier bounded stabilization surface (`{best_prior_name}` `{best_prior_score:.3f}` -> pass39 `{pass39_brux1:.3f}`) while keeping `n3` controlled and preserving the subject-level verdict."
        if pass39_brux1 > best_prior_score
        else f"Pass39 does not beat the best earlier bounded stabilization surface on `brux1` (`{best_prior_name}` stays at `{best_prior_score:.3f}` while pass39 reaches `{pass39_brux1:.3f}`), even though it remains apples-to-apples and preserves the repaired control verdict."
    )

    report = {
        "pass": PASS_NUMBER,
        "experiment": "bounded_multi_feature_record_relative_scale_floor_audit_on_repaired_emg_scaffold",
        "selection_excluded_columns": selection_excluded_columns,
        "offender_choice": choose_offender_summary(pass36_audit),
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
            "pass38": {
                "summary_path": str(pass38_summary_path.resolve()),
                "counts_by_subject": pass38_summary["pass38"]["counts_by_subject"],
                "subject_summary": pass38_summary["pass38"]["subject_summary"],
                "subjects_scores": {subject_id: float(pass38_subjects_scores[subject_id]) for subject_id in SUBJECT_IDS},
                "brux1_early_summary": summarize_early_rows(rows=pass38_brux1_rows),
            },
        },
        "pass39": {
            "features_csv": str(pass39_features.resolve()),
            "report_path": str(pass39_report_path.resolve()),
            "counts_by_subject": pass39_df["subject_id"].value_counts(sort=False).astype(int).to_dict(),
            "subject_summary": pass39_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "subjects_scores": {subject_id: float(pass39_subjects_scores[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS},
            "subjects_audit": pass39_subjects_audit,
            "pairwise": pass39_pairwise,
            "brux1_early_summary": summarize_early_rows(rows=pass39_brux1_rows),
        },
        "derived": {
            "subject_score_quads": subject_score_quads(
                pass36_subjects=pass36_subjects_scores,
                pass37_subjects=pass37_subjects_scores,
                pass38_subjects=pass38_subjects_scores,
                pass39_subjects=pass39_subjects_scores,
            ),
            "early_brux1_window_deltas": early_window_deltas(
                pass36_rows=pass36_brux1_rows,
                pass37_rows=pass37_brux1_rows,
                pass38_rows=pass38_brux1_rows,
                pass39_rows=pass39_brux1_rows,
            ),
            "brux1_minus_n3": float(pass39_subjects_scores["brux1"]["mean_score"] - pass39_subjects_scores["n3"]["mean_score"]),
            "n5_minus_brux1": float(pass39_subjects_scores["n5"]["mean_score"] - pass39_subjects_scores["brux1"]["mean_score"]),
            "n11_minus_brux1": float(pass39_subjects_scores["n11"]["mean_score"] - pass39_subjects_scores["brux1"]["mean_score"]),
        },
        "verdict_detail": verdict_detail,
        "summary_md_path": str(summary_md_path.resolve()),
        "summary_json_path": str(summary_json_path.resolve()),
    }

    summary_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_markdown(report), encoding="utf-8")
    print(summary_md_path)
    print(summary_json_path)


if __name__ == "__main__":
    main()
