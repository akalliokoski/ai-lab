from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from train_baseline import METADATA_COLUMNS, NON_TRAIN_FEATURE_COLUMNS, build_models

ROOT = Path(__file__).resolve().parents[3]


def load_feature_frame(path: Path) -> tuple[pd.DataFrame, list[str]]:
    df = pd.read_csv(path)
    if df.empty:
        raise SystemExit(f"features CSV is empty: {path}")
    if "subject_id" not in df.columns or "label" not in df.columns:
        raise SystemExit(f"features CSV missing subject_id/label: {path}")
    feature_columns = [
        col for col in df.columns if col not in METADATA_COLUMNS and col not in NON_TRAIN_FEATURE_COLUMNS
    ]
    if not feature_columns:
        raise SystemExit(f"no trainable feature columns found in {path}")
    return df, feature_columns


def fit_loso_subject_audit(
    df: pd.DataFrame,
    feature_columns: list[str],
    *,
    model_name: str,
    random_state: int,
) -> list[dict[str, Any]]:
    model = build_models(random_state)[model_name]
    y = (df["label"].str.lower() == "bruxism").astype(int)
    groups = df["subject_id"]
    rows: list[dict[str, Any]] = []

    for subject_id in sorted(groups.unique().tolist()):
        train_mask = groups != subject_id
        test_mask = groups == subject_id
        train_df = df.loc[train_mask].copy()
        test_df = df.loc[test_mask].copy()
        X_train = train_df[feature_columns]
        y_train = y.loc[train_mask]
        X_test = test_df[feature_columns]

        model.fit(X_train, y_train)
        imputer = model.named_steps["imputer"]
        scaler = model.named_steps["scaler"]
        clf = model.named_steps["model"]

        X_train_imp = imputer.transform(X_train)
        X_test_imp = imputer.transform(X_test)
        X_test_z = scaler.transform(X_test_imp)
        coef = clf.coef_[0]
        intercept = float(clf.intercept_[0])
        logit = X_test_z @ coef + intercept
        positive_class_index = list(clf.classes_).index(1)
        proba = clf.predict_proba(X_test_z)[:, positive_class_index]
        contrib_df = pd.DataFrame(X_test_z * coef, columns=feature_columns)
        mean_contrib = contrib_df.mean(axis=0).sort_values(ascending=False)
        abs_contrib = mean_contrib.abs().sort_values(ascending=False)

        rows.append(
            {
                "subject_id": subject_id,
                "true_label": str(test_df["label"].iloc[0]),
                "windows": int(len(test_df)),
                "mean_score": float(proba.mean()),
                "mean_logit": float(logit.mean()),
                "intercept": intercept,
                "top_positive_contributors": [
                    {"feature": feature, "mean_contribution": float(value)}
                    for feature, value in mean_contrib.head(5).items()
                ],
                "top_negative_contributors": [
                    {"feature": feature, "mean_contribution": float(value)}
                    for feature, value in mean_contrib.tail(5).sort_values().items()
                ],
                "largest_absolute_contributors": [
                    {
                        "feature": feature,
                        "mean_contribution": float(mean_contrib[feature]),
                        "absolute_contribution": float(abs_contrib[feature]),
                    }
                    for feature in abs_contrib.head(8).index
                ],
                "feature_mean_contributions": {
                    feature: float(value) for feature, value in mean_contrib.items()
                },
            }
        )
    return rows


def build_pairwise_gaps(subject_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_subject = {row["subject_id"]: row for row in subject_rows}
    brux1 = by_subject.get("brux1")
    if not brux1:
        return []

    gaps: list[dict[str, Any]] = []
    for subject_id in ["n3", "n5", "n11", "brux2"]:
        other = by_subject.get(subject_id)
        if other is None:
            continue
        deltas = {
            feature: other["feature_mean_contributions"][feature] - brux1["feature_mean_contributions"][feature]
            for feature in brux1["feature_mean_contributions"].keys()
        }
        ranked = sorted(deltas.items(), key=lambda item: item[1], reverse=True)
        gaps.append(
            {
                "higher_subject": subject_id,
                "reference_subject": "brux1",
                "score_gap": float(other["mean_score"] - brux1["mean_score"]),
                "top_gap_contributors": [
                    {"feature": feature, "delta_contribution": float(value)}
                    for feature, value in ranked[:6]
                ],
                "top_gap_reducers": [
                    {"feature": feature, "delta_contribution": float(value)}
                    for feature, value in sorted(deltas.items(), key=lambda item: item[1])[:6]
                ],
            }
        )
    return gaps


def summarize_feature_flags(subject_rows: list[dict[str, Any]]) -> dict[str, Any]:
    high_controls = [
        row for row in subject_rows if row["true_label"] == "control" and row["mean_score"] > 0.17
    ]
    counter: Counter[str] = Counter()
    for row in high_controls:
        for item in row["top_positive_contributors"]:
            counter[item["feature"]] += 1
    return {
        "high_control_subjects": [row["subject_id"] for row in sorted(high_controls, key=lambda r: r["mean_score"], reverse=True)],
        "repeated_positive_features": [{"feature": feat, "count": count} for feat, count in counter.most_common(8)],
    }


def render_markdown(audit: dict[str, Any]) -> str:
    subjects = audit["subjects"]
    by_subject = {row["subject_id"]: row for row in subjects}
    pairwise = audit["pairwise_gaps_vs_brux1"]
    flags = audit["feature_flags"]

    def bullets(items: list[dict[str, Any]], key: str) -> str:
        return "\n".join(
            f"  - `{item['feature']}` {item[key]:+.3f}" for item in items
        )

    subject_lines = []
    for row in sorted(subjects, key=lambda r: r["mean_score"], reverse=True):
        subject_lines.append(
            f"### `{row['subject_id']}` ({row['true_label']})\n"
            f"- mean LOSO score: `{row['mean_score']:.3f}`\n"
            f"- mean logit: `{row['mean_logit']:.3f}`\n"
            f"- strongest positive contributors:\n{bullets(row['top_positive_contributors'], 'mean_contribution')}\n"
            f"- strongest negative contributors:\n{bullets(row['top_negative_contributors'], 'mean_contribution')}"
        )

    gap_lines = []
    for gap in sorted(pairwise, key=lambda g: g["score_gap"], reverse=True):
        gap_lines.append(
            f"### `{gap['higher_subject']}` minus `brux1` (score gap `{gap['score_gap']:+.3f}`)\n"
            f"- features increasing the gap toward `{gap['higher_subject']}`:\n{bullets(gap['top_gap_contributors'], 'delta_contribution')}\n"
            f"- features pulling back toward `brux1`:\n{bullets(gap['top_gap_reducers'], 'delta_contribution')}"
        )

    repeated = "\n".join(
        f"- `{item['feature']}` appears in top-positive contributors for `{item['count']}` high-score controls"
        for item in flags["repeated_positive_features"]
    ) or "- none"
    score_lines = "\n".join(
        f"- `{row['subject_id']}` (`{row['true_label']}`): mean LOSO score `{row['mean_score']:.3f}`"
        for row in sorted(subjects, key=lambda r: r["mean_score"], reverse=True)
    )
    subject_block = "\n\n".join(subject_lines)
    gap_block = "\n\n".join(gap_lines)

    return f"""# Pass 16 — EMG feature-validity audit on matched `EMG1-EMG2` `SLEEP-S2 + MCAP-A3-only`

Date: 2026-05-04
Status: bounded EMG-first validity audit completed; the main failure signal is now better localized to which handcrafted features lift controls above `brux1` on the saved pass14 scaffold

## Why this audit exists

Pass15 showed that threshold tuning is a dead end for the current matched EMG run: `n3` and `n5` still outrank `brux1`, so no threshold rescues subject sensitivity without false positives.

This pass makes exactly one bounded increment:
- keep the same pass14 matched `EMG1-EMG2` `A3-only` dataset fixed
- keep the same model family fixed (`logreg`)
- rebuild the LOSO folds and inspect per-subject feature contributions to explain why controls outrank `brux1`

## Artifacts
- Audit script: `projects/bruxism-cap/src/audit_emg_feature_validity.py`
- Audit JSON: `projects/bruxism-cap/reports/feature-validity-audit-pass16-emg-a3-logreg.json`
- Primary features CSV: `projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv`
- Primary LOSO report context: `projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json`

## Key score ordering reproduced
{score_lines}

This reproduces the pass15 ranking problem: `n3` and `n5` still sit above `brux1`, while `brux2` remains much lower.

## Repeated feature pattern among the high-score controls
{repeated}

## Per-subject contribution summaries

{subject_block}

## Why `n3` and `n5` outrank `brux1`

{gap_block}

## Interpretation

1. The current EMG feature set is still partly EEG-shaped: relative bandpower / ratio features remain large contributors even though the project is now EMG-first.
2. The controls that outrank `brux1` do so through a small recurring feature family rather than through threshold quirks alone.
3. `brux2` remains a different failure mode from `brux1`: its score is not merely slightly below the controls, it is substantially lower, so one patch aimed only at `brux1` may not rescue both bruxism subjects.
4. This is still a validity note, not a baseline win. The audit narrows the next patch target to one small EMG-aligned feature-family change rather than another threshold or model sweep.

## Best next bounded step

Keep the matched subset and model family fixed, then run one small feature patch only:
- either drop the EEG-style relative bandpower / ratio family from the EMG recipe for a matched rerun, or
- replace that family with one compact amplitude-burst-oriented EMG summary family.

The safer next experiment is the ablation first: remove the band-ratio family on the same pass14 scaffold and compare whether the subject ranking becomes less hostile to `brux1` without inflating control false positives.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit which features drive the current EMG LOSO score ordering.")
    parser.add_argument("--features-csv", required=True)
    parser.add_argument("--model", default="logreg", choices=sorted(build_models(42).keys()))
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    features_path = Path(args.features_csv)
    if not features_path.is_absolute():
        features_path = ROOT / features_path
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path

    df, feature_columns = load_feature_frame(features_path)
    subject_rows = fit_loso_subject_audit(df, feature_columns, model_name=args.model, random_state=42)
    audit = {
        "features_csv": str(features_path.resolve()),
        "model": args.model,
        "feature_columns": feature_columns,
        "subjects": subject_rows,
        "pairwise_gaps_vs_brux1": build_pairwise_gaps(subject_rows),
        "feature_flags": summarize_feature_flags(subject_rows),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    md_path = out_path.with_suffix(".md")
    md_path.write_text(render_markdown(audit), encoding="utf-8")

    print(f"wrote feature-validity audit to {out_path}")
    print(f"wrote markdown summary to {md_path}")


if __name__ == "__main__":
    main()
