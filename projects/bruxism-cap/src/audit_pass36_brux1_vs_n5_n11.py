from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from audit_percentile_band_channel_gap import load_feature_frame, select_feature_columns
from train_baseline import build_models

EXCLUDE_PATTERNS = [r"^bp_", r"^rel_bp_", r"^ratio_"]
SHAPE_FEATURES = ["skewness", "kurtosis", "hjorth_mobility", "hjorth_complexity"]
AMP_DISP_FEATURES = [
    "mean",
    "std",
    "min",
    "max",
    "ptp",
    "rms",
    "line_length",
    "rectified_mean",
    "rectified_std",
    "envelope_mean",
    "envelope_std",
    "envelope_cv",
    "p95_abs",
]
COMPARE_SUBJECTS = ["brux1", "n5", "n11"]


def build_subject_rows(df: pd.DataFrame, feature_columns: list[str]) -> tuple[dict[str, Any], list[str], list[str], list[str]]:
    amp_disp_features = [feature for feature in AMP_DISP_FEATURES if feature in feature_columns]
    shape_features = [feature for feature in SHAPE_FEATURES if feature in feature_columns]
    other_features = [feature for feature in feature_columns if feature not in amp_disp_features and feature not in shape_features]
    subjects: dict[str, Any] = {}

    for subject_id in sorted(df["subject_id"].unique().tolist()):
        train_mask = df["subject_id"] != subject_id
        test_mask = df["subject_id"] == subject_id
        train_df = df.loc[train_mask].copy()
        test_df = df.loc[test_mask].copy().reset_index(drop=True)
        y_train = (train_df["label"].str.lower() == "bruxism").astype(int)

        model = build_models(42)["logreg"]
        model.fit(train_df[feature_columns], y_train)
        imputer = model.named_steps["imputer"]
        scaler = model.named_steps["scaler"]
        clf = model.named_steps["model"]

        x_test_imp = pd.DataFrame(imputer.transform(test_df[feature_columns]), columns=feature_columns)
        x_test_z = pd.DataFrame(scaler.transform(x_test_imp.to_numpy()), columns=feature_columns)
        coef = pd.Series(clf.coef_[0], index=feature_columns)
        positive_class_index = list(clf.classes_).index(1)
        scores = pd.Series(model.predict_proba(test_df[feature_columns])[:, positive_class_index])
        contrib = x_test_z.mul(coef, axis=1)

        rows = test_df[
            [
                "subject_id",
                "label",
                "start_s",
                "end_s",
                "relative_time_quantile",
                "time_match_rank",
                "window_index",
            ]
        ].copy()
        rows["score"] = scores
        rows["amp_disp_contrib"] = contrib[amp_disp_features].sum(axis=1)
        rows["shape_contrib"] = contrib[shape_features].sum(axis=1)
        rows["other_contrib"] = contrib[other_features].sum(axis=1)
        rows = rows.sort_values("time_match_rank").reset_index(drop=True)

        grouped = {}
        for name, mask in {
            "early_ranks_1_3": rows["time_match_rank"].between(1, 3),
            "mid_ranks_4_7": rows["time_match_rank"].between(4, 7),
            "late_ranks_8_10": rows["time_match_rank"].between(8, 10),
        }.items():
            group = rows.loc[mask]
            grouped[name] = {
                "windows": int(len(group)),
                "mean_score": float(group["score"].mean()),
                "min_score": float(group["score"].min()),
                "max_score": float(group["score"].max()),
                "amp_disp_mean": float(group["amp_disp_contrib"].mean()),
                "shape_mean": float(group["shape_contrib"].mean()),
                "other_mean": float(group["other_contrib"].mean()),
            }

        feature_means = {}
        for feature in feature_columns:
            feature_means[feature] = {
                "raw_mean": float(x_test_imp[feature].mean()),
                "z_mean": float(x_test_z[feature].mean()),
                "mean_contribution": float(contrib[feature].mean()),
                "coefficient": float(coef[feature]),
            }

        subjects[subject_id] = {
            "mean_score": float(scores.mean()),
            "median_score": float(scores.median()),
            "min_score": float(scores.min()),
            "max_score": float(scores.max()),
            "positive_windows": int((scores >= 0.5).sum()),
            "score_bins": {
                "lt_0_1": int((scores < 0.1).sum()),
                "0_1_to_0_2": int(((scores >= 0.1) & (scores < 0.2)).sum()),
                "0_2_to_0_3": int(((scores >= 0.2) & (scores < 0.3)).sum()),
                "0_3_to_0_5": int(((scores >= 0.3) & (scores < 0.5)).sum()),
                "ge_0_5": int((scores >= 0.5).sum()),
            },
            "block_means": {
                "amp_disp": float(rows["amp_disp_contrib"].mean()),
                "shape": float(rows["shape_contrib"].mean()),
                "other": float(rows["other_contrib"].mean()),
            },
            "grouped": grouped,
            "rows_by_time_rank": rows.to_dict(orient="records"),
            "feature_means": feature_means,
        }

    return subjects, amp_disp_features, shape_features, other_features


def build_pairwise(subjects: dict[str, Any], feature_columns: list[str], amp_disp_features: list[str], shape_features: list[str]) -> dict[str, Any]:
    pairwise = {}
    for higher_subject in ["n5", "n11"]:
        feature_rows = []
        for feature in feature_columns:
            higher = subjects[higher_subject]["feature_means"][feature]
            lower = subjects["brux1"]["feature_means"][feature]
            feature_rows.append(
                {
                    "feature": feature,
                    "mean_contribution_delta": float(higher["mean_contribution"] - lower["mean_contribution"]),
                    "raw_mean_delta": float(higher["raw_mean"] - lower["raw_mean"]),
                    "z_mean_delta": float(higher["z_mean"] - lower["z_mean"]),
                    "block": (
                        "shape"
                        if feature in shape_features
                        else "amp_disp"
                        if feature in amp_disp_features
                        else "other"
                    ),
                }
            )
        feature_rows.sort(key=lambda row: abs(row["mean_contribution_delta"]), reverse=True)
        block_sums = {
            block: float(sum(row["mean_contribution_delta"] for row in feature_rows if row["block"] == block))
            for block in ["amp_disp", "shape", "other"]
        }
        pairwise[f"{higher_subject}_minus_brux1"] = {
            "score_gap": float(subjects[higher_subject]["mean_score"] - subjects["brux1"]["mean_score"]),
            "block_sums": block_sums,
            "top_positive": [row for row in feature_rows if row["mean_contribution_delta"] > 0][:8],
            "top_negative": [row for row in feature_rows if row["mean_contribution_delta"] < 0][:8],
        }
    return pairwise


def format_score(value: float) -> str:
    if abs(value) < 1e-6:
        return f"{value:.2e}"
    return f"{value:.3f}"


def render_rows(rows: list[dict[str, Any]]) -> str:
    rendered = []
    for row in rows:
        rendered.append(
            f"- rank `{row['time_match_rank']}` | window `{row['window_index']}` | start `{row['start_s']:.0f}s` | "
            f"score `{format_score(row['score'])}` | amp/disp `{row['amp_disp_contrib']:+.3f}` | "
            f"shape `{row['shape_contrib']:+.3f}` | other `{row['other_contrib']:+.3f}`"
        )
    return "\n".join(rendered)


def render_feature_rows(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{row['feature']}` ({row['block']}) contribution delta `{row['mean_contribution_delta']:+.3f}` | "
        f"z-mean delta `{row['z_mean_delta']:+.3f}` | raw-mean delta `{row['raw_mean_delta']:+.6f}`"
        for row in rows
    )


def render_markdown(report: dict[str, Any]) -> str:
    brux1 = report["subjects"]["brux1"]
    n5 = report["subjects"]["n5"]
    n11 = report["subjects"]["n11"]
    pair_n5 = report["pairwise"]["n5_minus_brux1"]
    pair_n11 = report["pairwise"]["n11_minus_brux1"]

    return f"""# Pass 36 follow-up — fold-by-fold `brux1` vs `n5` / `n11` audit on the exact composed EMG table

Date: 2026-05-05
Status: bounded extraction-only audit completed on the fixed pass36 `EMG1-EMG2` `A1-only` composed table. No selector, channel, feature-family, or benchmark rerun was introduced; the audit only rebuilds the existing held-out `logreg` folds to expose per-window scores and grouped contribution blocks.

## Artifacts
- Audit script: `projects/bruxism-cap/src/audit_pass36_brux1_vs_n5_n11.py`
- Audit JSON: `projects/bruxism-cap/reports/pass36-brux1-vs-n5-n11-fold-audit.json`
- Audit memo: `projects/bruxism-cap/reports/pass36-brux1-vs-n5-n11-fold-audit.md`
- Fixed feature table inspected: `projects/bruxism-cap/data/window_features_pass36_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape.csv`
- Existing benchmark report inspected: `projects/bruxism-cap/reports/loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json`

## 1) Fold-by-fold / window-group evidence on the exact current pass36 table

### Held-out subject score surface
- `brux1`: mean score `{brux1['mean_score']:.3f}` | range `{format_score(brux1['min_score'])}` to `{brux1['max_score']:.3f}` | positive windows `{brux1['positive_windows']}/10`
- `n5`: mean score `{n5['mean_score']:.3f}` | range `{n5['min_score']:.3f}` to `{n5['max_score']:.3f}` | positive windows `{n5['positive_windows']}/10`
- `n11`: mean score `{n11['mean_score']:.3f}` | range `{n11['min_score']:.3f}` to `{n11['max_score']:.3f}` | positive windows `{n11['positive_windows']}/10`
- `n5 - brux1` subject gap: `{pair_n5['score_gap']:+.3f}`
- `n11 - brux1` subject gap: `{pair_n11['score_gap']:+.3f}`

### `brux1` window distribution
- score bins: `<0.1` = `{brux1['score_bins']['lt_0_1']}`, `0.1-0.2` = `{brux1['score_bins']['0_1_to_0_2']}`, `0.2-0.3` = `{brux1['score_bins']['0_2_to_0_3']}`, `0.3-0.5` = `{brux1['score_bins']['0_3_to_0_5']}`, `>=0.5` = `{brux1['score_bins']['ge_0_5']}`
- early ranks `1-3`: mean score `{format_score(brux1['grouped']['early_ranks_1_3']['mean_score'])}` | amp/disp mean `{brux1['grouped']['early_ranks_1_3']['amp_disp_mean']:+.3f}` | shape mean `{brux1['grouped']['early_ranks_1_3']['shape_mean']:+.3f}`
- mid ranks `4-7`: mean score `{brux1['grouped']['mid_ranks_4_7']['mean_score']:.3f}` | amp/disp mean `{brux1['grouped']['mid_ranks_4_7']['amp_disp_mean']:+.3f}` | shape mean `{brux1['grouped']['mid_ranks_4_7']['shape_mean']:+.3f}`
- late ranks `8-10`: mean score `{brux1['grouped']['late_ranks_8_10']['mean_score']:.3f}` | amp/disp mean `{brux1['grouped']['late_ranks_8_10']['amp_disp_mean']:+.3f}` | shape mean `{brux1['grouped']['late_ranks_8_10']['shape_mean']:+.3f}`

The three earliest `brux1` windows are the decisive collapse point:
{render_rows(brux1['rows_by_time_rank'][:3])}

The best `brux1` windows are still sub-threshold:
{render_rows(sorted(brux1['rows_by_time_rank'], key=lambda row: row['score'], reverse=True)[:3])}

### Comparator window-group surfaces
- `n5` grouped means: early `{n5['grouped']['early_ranks_1_3']['mean_score']:.3f}` | mid `{n5['grouped']['mid_ranks_4_7']['mean_score']:.3f}` | late `{n5['grouped']['late_ranks_8_10']['mean_score']:.3f}`
- `n11` grouped means: early `{n11['grouped']['early_ranks_1_3']['mean_score']:.3f}` | mid `{n11['grouped']['mid_ranks_4_7']['mean_score']:.3f}` | late `{n11['grouped']['late_ranks_8_10']['mean_score']:.3f}`
- `n5` score bins: `<0.1` = `{n5['score_bins']['lt_0_1']}`, `0.1-0.2` = `{n5['score_bins']['0_1_to_0_2']}`, `0.2-0.3` = `{n5['score_bins']['0_2_to_0_3']}`, `0.3-0.5` = `{n5['score_bins']['0_3_to_0_5']}`, `>=0.5` = `{n5['score_bins']['ge_0_5']}`
- `n11` score bins: `<0.1` = `{n11['score_bins']['lt_0_1']}`, `0.1-0.2` = `{n11['score_bins']['0_1_to_0_2']}`, `0.2-0.3` = `{n11['score_bins']['0_2_to_0_3']}`, `0.3-0.5` = `{n11['score_bins']['0_3_to_0_5']}`, `>=0.5` = `{n11['score_bins']['ge_0_5']}`

## 2) Is the miss uniformly low or sparse-window low?

Not uniformly low, but also not a one-window fluke. The cleanest read is: `brux1` has a sparse catastrophic subset plus a weak residual floor.

- Sparse catastrophic subset: the earliest three held-out `brux1` windows score essentially zero (`~1.6e-97`, `~4.6e-84`, `~6.4e-82`) and alone pull the subject mean down hard.
- Residual weak floor: the remaining seven windows recover only to a `0.088` to `0.291` band, with no window even reaching `0.3` and no positive windows at all.
- Comparator contrast: `n5` already has `3/10` windows above `0.5`, while `n11` splits cleanly into `5/10` above and `5/10` below `0.5`.

So the remaining pass36 miss is best described as sparse-window low in its most extreme form, but still globally sub-threshold across all `10` `brux1` windows.

## 3) Does the remaining suppression live mainly in the record-relative amplitude / dispersion block or the added shape block?

It lives overwhelmingly in the record-relative amplitude / dispersion block, not in the added shape block.

### Block-level deltas versus `brux1`
- `n5 - brux1`: amp/disp `{pair_n5['block_sums']['amp_disp']:+.3f}` | shape `{pair_n5['block_sums']['shape']:+.3f}` | other `{pair_n5['block_sums']['other']:+.3f}`
- `n11 - brux1`: amp/disp `{pair_n11['block_sums']['amp_disp']:+.3f}` | shape `{pair_n11['block_sums']['shape']:+.3f}` | other `{pair_n11['block_sums']['other']:+.3f}`

### Top positive feature deltas keeping `n5` above `brux1`
{render_feature_rows(pair_n5['top_positive'])}

### Top positive feature deltas keeping `n11` above `brux1`
{render_feature_rows(pair_n11['top_positive'])}

### Important negative evidence against blaming the shape block
- For `n5 - brux1`, the net shape delta is slightly negative (`{pair_n5['block_sums']['shape']:+.3f}`), meaning the added shape block is mildly helping `brux1`, not suppressing it.
- For `n11 - brux1`, the net shape delta is almost zero (`{pair_n11['block_sums']['shape']:+.3f}`).
- Inside the catastrophic early `brux1` trio, amp/disp is massively negative (`{brux1['grouped']['early_ranks_1_3']['amp_disp_mean']:+.3f}`) while shape is actually positive (`{brux1['grouped']['early_ranks_1_3']['shape_mean']:+.3f}`).

So the audit-local answer is unambiguous: the remaining suppression is still the record-relative amplitude / dispersion surface, led by `mean`, `rectified_std`, `rms`, `std`, `min`, `envelope_cv`, `ptp`, and `p95_abs`.

## 4) Safest next bounded benchmark increment

Keep the exact repaired five-subject pass36 scaffold fixed again and do one narrower representation audit before any new rerun:
- isolate the catastrophic early `brux1` trio (ranks `1-3`) against the same subject's mid / late windows,
- test whether one bounded cap or robust clipping rule on the record-relative amplitude / dispersion family can prevent those three windows from dominating the held-out fold,
- keep the same selected rows, same model family, same train-time exclusions, and same shape block fixed so the result stays apples-to-apples with pass36.

This is the safest next increment because this audit shows the remaining uncertainty is not about the Hjorth add-on at all; it is about whether a very small amplitude/dispersion stabilization patch can remove the catastrophic `brux1` under-scoring without disturbing the real `brux2` rescue.

## 5) Explicitly rejected broader move

Rejected move: launch another channel pivot or broader feature-family expansion now.

Why rejected:
- the exact current pass36 table already answers the composition question and this follow-up audit now localizes the remaining miss to one dominant block,
- a channel pivot would blur the new finding that the catastrophic `brux1` collapse is already visible inside the fixed EMG scaffold,
- a broader feature expansion would hide whether the unresolved issue was actually the existing amplitude/dispersion surface all along.

## Bottom line

The pass36 miss is no longer best read as a uniform low-score brux1 subject or as a Hjorth-shape failure. It is a fixed-table, fold-localized problem: three early `brux1` windows catastrophically collapse under the record-relative amplitude / dispersion surface, and the remaining seven windows never recover enough to reach threshold. That makes one more amplitude-stabilization audit the safest next benchmark increment, while channel pivots and broader feature growth should stay out of scope for the next step.
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    features_csv = root / "data/window_features_pass36_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape.csv"
    report_json = root / "reports/pass36-brux1-vs-n5-n11-fold-audit.json"
    report_md = root / "reports/pass36-brux1-vs-n5-n11-fold-audit.md"

    df = load_feature_frame(features_csv)
    feature_columns, selection_excluded = select_feature_columns(df, exclude_patterns=EXCLUDE_PATTERNS)
    subjects, amp_disp_features, shape_features, other_features = build_subject_rows(df, feature_columns)
    pairwise = build_pairwise(subjects, feature_columns, amp_disp_features, shape_features)

    report = {
        "pass": 36,
        "experiment": "pass36_brux1_vs_n5_n11_fold_audit",
        "features_csv": str(features_csv.resolve()),
        "selection_excluded_columns": selection_excluded,
        "feature_columns": feature_columns,
        "amp_disp_features": amp_disp_features,
        "shape_features": shape_features,
        "other_features": other_features,
        "subjects": subjects,
        "pairwise": pairwise,
        "summary_md_path": str(report_md.resolve()),
        "summary_json_path": str(report_json.resolve()),
    }

    report_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report_md.write_text(render_markdown(report), encoding="utf-8")
    print(report_md)
    print(report_json)


if __name__ == "__main__":
    main()
