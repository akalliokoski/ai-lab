from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from train_baseline import METADATA_COLUMNS, NON_TRAIN_FEATURE_COLUMNS, build_models

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FOCUS_FEATURES = [
    "sample_entropy",
    "rectified_mean",
    "rectified_std",
    "envelope_mean",
    "envelope_std",
    "envelope_cv",
    "burst_fraction",
    "burst_rate_hz",
    "p95_abs",
]
DEFAULT_COMPARE_SUBJECTS = ["n3", "n5", "brux2", "n11"]


def load_feature_frame(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.empty:
        raise SystemExit(f"features CSV is empty: {path}")
    if "subject_id" not in df.columns or "label" not in df.columns:
        raise SystemExit(f"features CSV missing subject_id/label: {path}")
    return df


def select_feature_columns(
    df: pd.DataFrame,
    *,
    include_patterns: list[str],
    exclude_patterns: list[str],
) -> tuple[list[str], list[str]]:
    feature_columns = [
        col for col in df.columns if col not in METADATA_COLUMNS and col not in NON_TRAIN_FEATURE_COLUMNS
    ]
    base_feature_columns = list(feature_columns)
    include_regexes = [re.compile(pattern) for pattern in include_patterns]
    exclude_regexes = [re.compile(pattern) for pattern in exclude_patterns]
    if include_regexes:
        feature_columns = [
            col for col in feature_columns if any(pattern.search(col) for pattern in include_regexes)
        ]
    if exclude_regexes:
        feature_columns = [
            col for col in feature_columns if not any(pattern.search(col) for pattern in exclude_regexes)
        ]
    if not feature_columns:
        raise SystemExit("feature selection removed all trainable columns")
    selection_excluded = [col for col in base_feature_columns if col not in feature_columns]
    return feature_columns, selection_excluded


def summarize_values(values: pd.Series) -> dict[str, float]:
    return {
        "mean": float(values.mean()),
        "std": float(values.std(ddof=0)),
        "median": float(values.median()),
        "p95": float(values.quantile(0.95)),
        "min": float(values.min()),
        "max": float(values.max()),
    }


def fit_subject_rows(
    df: pd.DataFrame,
    feature_columns: list[str],
    *,
    focus_features: list[str],
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

        X_train_imp = pd.DataFrame(imputer.transform(X_train), columns=feature_columns)
        X_test_imp = pd.DataFrame(imputer.transform(X_test), columns=feature_columns)
        X_test_z = pd.DataFrame(scaler.transform(X_test_imp), columns=feature_columns)
        coef = pd.Series(clf.coef_[0], index=feature_columns)
        intercept = float(clf.intercept_[0])
        positive_class_index = list(clf.classes_).index(1)
        proba = clf.predict_proba(X_test_z)[:, positive_class_index]
        contribution_df = X_test_z.mul(coef, axis=1)

        focus_summary: dict[str, Any] = {}
        for feature in focus_features:
            if feature not in X_test_imp.columns:
                continue
            focus_summary[feature] = {
                "raw": summarize_values(X_test_imp[feature]),
                "zscore": summarize_values(X_test_z[feature]),
                "mean_contribution": float(contribution_df[feature].mean()),
                "coefficient": float(coef[feature]),
            }

        rows.append(
            {
                "subject_id": subject_id,
                "true_label": str(test_df["label"].iloc[0]),
                "windows": int(len(test_df)),
                "mean_score": float(proba.mean()),
                "intercept": intercept,
                "focus_features": focus_summary,
            }
        )
    return rows


def build_pairwise_feature_deltas(
    subject_rows: list[dict[str, Any]],
    *,
    reference_subject: str,
    compare_subjects: list[str],
    focus_features: list[str],
) -> list[dict[str, Any]]:
    by_subject = {row["subject_id"]: row for row in subject_rows}
    reference = by_subject.get(reference_subject)
    if reference is None:
        return []

    deltas: list[dict[str, Any]] = []
    for subject_id in compare_subjects:
        other = by_subject.get(subject_id)
        if other is None:
            continue
        features: list[dict[str, Any]] = []
        for feature in focus_features:
            ref_stats = reference["focus_features"].get(feature)
            other_stats = other["focus_features"].get(feature)
            if ref_stats is None or other_stats is None:
                continue
            features.append(
                {
                    "feature": feature,
                    "raw_mean_delta": float(other_stats["raw"]["mean"] - ref_stats["raw"]["mean"]),
                    "zscore_mean_delta": float(other_stats["zscore"]["mean"] - ref_stats["zscore"]["mean"]),
                    "mean_contribution_delta": float(other_stats["mean_contribution"] - ref_stats["mean_contribution"]),
                }
            )
        features.sort(key=lambda item: abs(item["mean_contribution_delta"]), reverse=True)
        deltas.append(
            {
                "higher_subject": subject_id,
                "reference_subject": reference_subject,
                "score_gap": float(other["mean_score"] - reference["mean_score"]),
                "feature_deltas": features,
            }
        )
    return deltas


def render_markdown(audit: dict[str, Any]) -> str:
    rows = sorted(audit["subjects"], key=lambda row: row["mean_score"], reverse=True)
    pairwise = audit["pairwise_vs_brux1"]
    focus_features = audit["focus_features"]

    score_lines = "\n".join(
        f"- `{row['subject_id']}` (`{row['true_label']}`): mean LOSO score `{row['mean_score']:.3f}`"
        for row in rows
    )

    subject_sections: list[str] = []
    for row in rows:
        feature_lines = []
        for feature in focus_features:
            stats = row["focus_features"].get(feature)
            if stats is None:
                continue
            feature_lines.append(
                f"- `{feature}`: raw mean `{stats['raw']['mean']:.6f}`, raw p95 `{stats['raw']['p95']:.6f}`, "
                f"mean z-score `{stats['zscore']['mean']:+.3f}`, mean contribution `{stats['mean_contribution']:+.3f}`"
            )
        subject_sections.append(
            f"### `{row['subject_id']}` ({row['true_label']})\n"
            f"- mean LOSO score: `{row['mean_score']:.3f}`\n"
            f"- focused feature summaries:\n" + "\n".join(feature_lines)
        )

    gap_sections: list[str] = []
    for gap in pairwise:
        ranked = gap["feature_deltas"]
        toward_other = [item for item in ranked if item["mean_contribution_delta"] > 0][:5]
        toward_brux1 = [item for item in ranked if item["mean_contribution_delta"] < 0][:5]
        toward_other_lines = "\n".join(
            f"  - `{item['feature']}` contribution delta `{item['mean_contribution_delta']:+.3f}` | "
            f"z-mean delta `{item['zscore_mean_delta']:+.3f}` | raw-mean delta `{item['raw_mean_delta']:+.6f}`"
            for item in toward_other
        ) or "  - none"
        toward_brux1_lines = "\n".join(
            f"  - `{item['feature']}` contribution delta `{item['mean_contribution_delta']:+.3f}` | "
            f"z-mean delta `{item['zscore_mean_delta']:+.3f}` | raw-mean delta `{item['raw_mean_delta']:+.6f}`"
            for item in toward_brux1
        ) or "  - none"
        gap_sections.append(
            f"### `{gap['higher_subject']}` minus `brux1` (score gap `{gap['score_gap']:+.3f}`)\n"
            f"- focused features pushing toward `{gap['higher_subject']}`:\n{toward_other_lines}\n"
            f"- focused features pushing back toward `brux1`:\n{toward_brux1_lines}"
        )

    subject_block = "\n\n".join(subject_sections)
    gap_block = "\n\n".join(gap_sections)

    return f"""# Pass 21 — EMG envelope-family audit on the retained pass19 working point

Date: 2026-05-04
Status: bounded EMG-first validity audit completed; the retained amplitude / envelope family does change the score surface, but it still does not create a clean `brux1`-over-control separation on the current matched scaffold

## Why this audit exists

Pass20 showed that naive raw-`mean` removal is the wrong next move: it leaves `n3` and `n5` essentially unchanged while collapsing `brux1`.

This pass makes exactly one bounded increment:
- keep the stronger pass19 matched `EMG1-EMG2` `A3-only` scaffold fixed
- keep the same selection-aware exclusions fixed (`^bp_`, `^rel_bp_`, `^ratio_`)
- keep the same model family fixed (`logreg`)
- audit the retained amplitude / envelope family directly instead of doing another deletion-only rerun

## Artifacts
- Audit script: `projects/bruxism-cap/src/audit_emg_envelope_family.py`
- Audit JSON: `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.json`
- Feature CSV: `projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv`
- Context report: `projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json`

## Reproduced score ordering
{score_lines}

This keeps the same pass19 bottleneck in view: `n3` and `n5` still outrank `brux1`, and subject-level sensitivity remains `0.000`.

## Focused per-subject feature summaries

{subject_block}

## Pairwise focused deltas versus `brux1`

{gap_block}

## Interpretation

1. The retained EMG-oriented family is not useless: several envelope / burst features move materially across subjects and do reshape contributions.
2. But the family is not consistently bruxism-aligned on this tiny matched subset. Some retained features still favor controls (`n3` and/or `n5`) more than `brux1`, while others help `brux1` without being large enough to rescue the final ranking.
3. This supports keeping pass19 as the working point but treating the remaining problem as feature-behavior auditing, not threshold tuning and not more blind single-feature deletion.
4. This is another validity note, not a new honest baseline.

## Best next bounded step

Keep the pass19 scaffold fixed again and do one matched comparison next:
- compare the current pass19 selection-aware EMG recipe against the honest pass12 `C4-P4 A1-only` anchor in one shared subject-score table, or
- if staying within EMG only, test one normalization-aware extraction change that preserves the envelope family (for example robust per-window centering / scaling recorded in the feature pipeline) rather than dropping more retained features.

The safer next experiment is the first one if the goal is benchmark clarity; the safer EMG-only experiment is the second one if the goal is still to explain why `brux1` stays below `n3` and `n5`.
"""

def main() -> None:
    parser = argparse.ArgumentParser(description="Audit retained EMG envelope-family features on the current pass19 working point.")
    parser.add_argument("--features-csv", required=True)
    parser.add_argument("--model", default="logreg", choices=sorted(build_models(42).keys()))
    parser.add_argument("--out", required=True)
    parser.add_argument("--include-features-regex", action="append", default=[])
    parser.add_argument("--exclude-features-regex", action="append", default=[])
    parser.add_argument("--focus-feature", action="append", default=[])
    args = parser.parse_args()

    features_path = Path(args.features_csv)
    if not features_path.is_absolute():
        features_path = ROOT / features_path
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path

    df = load_feature_frame(features_path)
    feature_columns, selection_excluded = select_feature_columns(
        df,
        include_patterns=args.include_features_regex,
        exclude_patterns=args.exclude_features_regex,
    )
    focus_features = args.focus_feature or DEFAULT_FOCUS_FEATURES
    missing_focus_features = [feature for feature in focus_features if feature not in feature_columns]
    subject_rows = fit_subject_rows(
        df,
        feature_columns,
        focus_features=[feature for feature in focus_features if feature in feature_columns],
        model_name=args.model,
        random_state=42,
    )
    audit = {
        "features_csv": str(features_path.resolve()),
        "model": args.model,
        "feature_selection": {
            "include_features_regex": args.include_features_regex,
            "exclude_features_regex": args.exclude_features_regex,
            "selected_feature_count": len(feature_columns),
            "selection_excluded_feature_count": len(selection_excluded),
            "selection_excluded_features": selection_excluded,
        },
        "focus_features": [feature for feature in focus_features if feature in feature_columns],
        "missing_focus_features": missing_focus_features,
        "subjects": subject_rows,
        "pairwise_vs_brux1": build_pairwise_feature_deltas(
            subject_rows,
            reference_subject="brux1",
            compare_subjects=DEFAULT_COMPARE_SUBJECTS,
            focus_features=[feature for feature in focus_features if feature in feature_columns],
        ),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    md_path = out_path.with_suffix(".md")
    md_path.write_text(render_markdown(audit), encoding="utf-8")
    print(f"wrote audit to {out_path}")
    print(f"wrote markdown summary to {md_path}")


if __name__ == "__main__":
    main()
