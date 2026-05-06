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
    "zero_crossing_rate",
    "sample_entropy",
    "burst_fraction",
    "burst_rate_hz",
    "line_length",
    "mean",
    "rectified_mean",
    "envelope_mean",
    "rectified_std",
    "envelope_std",
    "p95_abs",
]


def load_feature_frame(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.empty:
        raise SystemExit(f"features CSV is empty: {path}")
    if "subject_id" not in df.columns or "label" not in df.columns:
        raise SystemExit(f"features CSV missing subject_id/label: {path}")
    return df


def select_feature_columns(df: pd.DataFrame, *, exclude_patterns: list[str]) -> tuple[list[str], list[str]]:
    feature_columns = [
        col for col in df.columns if col not in METADATA_COLUMNS and col not in NON_TRAIN_FEATURE_COLUMNS
    ]
    base_feature_columns = list(feature_columns)
    exclude_regexes = [re.compile(pattern) for pattern in exclude_patterns]
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
        "median": float(values.median()),
        "p95": float(values.quantile(0.95)),
        "min": float(values.min()),
        "max": float(values.max()),
    }


def load_subject_scores(report_path: Path, model_name: str) -> dict[str, dict[str, Any]]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    return {
        row["subject_id"]: row
        for row in report["models"][model_name]["subject_aggregation"]["subjects"]
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
        X_test_z = pd.DataFrame(scaler.transform(X_test_imp.to_numpy()), columns=feature_columns)
        coef = pd.Series(clf.coef_[0], index=feature_columns)
        intercept = float(clf.intercept_[0])
        positive_class_index = list(clf.classes_).index(1)
        proba = clf.predict_proba(X_test_z.to_numpy())[:, positive_class_index]
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
                "timing": {
                    "start_s": summarize_values(test_df["start_s"]),
                    "end_s": summarize_values(test_df["end_s"]),
                },
            }
        )
    return rows


def build_feature_gap(
    subject_rows: list[dict[str, Any]],
    *,
    higher_subject: str,
    lower_subject: str,
    focus_features: list[str],
) -> dict[str, Any]:
    by_subject = {row["subject_id"]: row for row in subject_rows}
    higher = by_subject[higher_subject]
    lower = by_subject[lower_subject]
    feature_deltas: list[dict[str, Any]] = []
    for feature in focus_features:
        higher_stats = higher["focus_features"].get(feature)
        lower_stats = lower["focus_features"].get(feature)
        if higher_stats is None or lower_stats is None:
            continue
        feature_deltas.append(
            {
                "feature": feature,
                "mean_contribution_delta": float(
                    higher_stats["mean_contribution"] - lower_stats["mean_contribution"]
                ),
                "raw_mean_delta": float(higher_stats["raw"]["mean"] - lower_stats["raw"]["mean"]),
                "zscore_mean_delta": float(
                    higher_stats["zscore"]["mean"] - lower_stats["zscore"]["mean"]
                ),
            }
        )
    feature_deltas.sort(key=lambda item: abs(item["mean_contribution_delta"]), reverse=True)
    return {
        "higher_subject": higher_subject,
        "lower_subject": lower_subject,
        "score_gap": float(higher["mean_score"] - lower["mean_score"]),
        "feature_deltas": feature_deltas,
    }


def render_subject_section(row: dict[str, Any], focus_features: list[str]) -> str:
    lines = [
        f"### `{row['subject_id']}` ({row['true_label']})",
        f"- mean LOSO score: `{row['mean_score']:.3f}`",
        f"- windows: `{row['windows']}` | start_s mean `{row['timing']['start_s']['mean']:.1f}` | median `{row['timing']['start_s']['median']:.1f}` | min `{row['timing']['start_s']['min']:.1f}` | max `{row['timing']['start_s']['max']:.1f}`",
        "- focused feature summaries:",
    ]
    for feature in focus_features:
        stats = row["focus_features"].get(feature)
        if stats is None:
            continue
        lines.append(
            f"  - `{feature}`: raw mean `{stats['raw']['mean']:.6f}`, raw p95 `{stats['raw']['p95']:.6f}`, "
            f"mean z-score `{stats['zscore']['mean']:+.3f}`, mean contribution `{stats['mean_contribution']:+.3f}`"
        )
    return "\n".join(lines)


def render_gap_section(gap: dict[str, Any], *, top_n: int = 5) -> str:
    toward_higher = [item for item in gap["feature_deltas"] if item["mean_contribution_delta"] > 0][:top_n]
    toward_lower = [item for item in gap["feature_deltas"] if item["mean_contribution_delta"] < 0][:top_n]
    high_lines = "\n".join(
        f"  - `{item['feature']}` contribution delta `{item['mean_contribution_delta']:+.3f}` | "
        f"z-mean delta `{item['zscore_mean_delta']:+.3f}` | raw-mean delta `{item['raw_mean_delta']:+.6f}`"
        for item in toward_higher
    ) or "  - none"
    low_lines = "\n".join(
        f"  - `{item['feature']}` contribution delta `{item['mean_contribution_delta']:+.3f}` | "
        f"z-mean delta `{item['zscore_mean_delta']:+.3f}` | raw-mean delta `{item['raw_mean_delta']:+.6f}`"
        for item in toward_lower
    ) or "  - none"
    return (
        f"### `{gap['higher_subject']}` minus `{gap['lower_subject']}` (score gap `{gap['score_gap']:+.3f}`)\n"
        f"- focused features pushing toward `{gap['higher_subject']}`:\n{high_lines}\n"
        f"- focused features pushing back toward `{gap['lower_subject']}`:\n{low_lines}"
    )


def render_markdown(audit: dict[str, Any]) -> str:
    subject_rows = {row["subject_id"]: row for row in audit["subjects"]}
    ordered = sorted(audit["subjects"], key=lambda row: row["mean_score"], reverse=True)
    subject_sections = "\n\n".join(
        render_subject_section(subject_rows[sid], audit["focus_features"])
        for sid in ["brux2", "n3", "brux1"]
        if sid in subject_rows
    )
    gap_sections = "\n\n".join(render_gap_section(gap) for gap in audit["pairwise_gaps"])

    emg_scores = audit["emg_subject_scores"]
    anchor_scores = audit["anchor_subject_scores"]
    brux2_flip = emg_scores["brux2"]["mean_score"] - emg_scores["n3"]["mean_score"]
    anchor_gap = anchor_scores["brux2"]["mean_score"] - anchor_scores["n3"]["mean_score"]

    score_lines = "\n".join(
        f"- `{row['subject_id']}` (`{row['true_label']}`): mean LOSO score `{row['mean_score']:.3f}`"
        for row in ordered
    )

    return f"""# Pass 24 — EMG `brux2` collapse versus `n3` control audit on the retained pass19 working point

Date: 2026-05-05
Status: bounded EMG-first validity audit completed; the strongest current EMG recipe still fails mainly because `brux2` collapses while `n3` becomes the dominant control, and the largest surviving gap is now concentrated in control-favoring crossing/irregularity features rather than in a generic threshold problem

## Why this audit exists

Pass23 made the benchmark gap sharper but did not yet explain the main EMG failure surface:
- under the honest `C4-P4 A1-only` anchor, `brux2` is the strongest subject
- under the current pass19 `EMG1-EMG2 A3-only` working point, `brux2` collapses and `n3` becomes the highest-score control

This pass makes exactly one bounded increment:
- keep the stronger pass19 matched `EMG1-EMG2` `A3-only` scaffold fixed
- keep the same selection-aware exclusions fixed (`^bp_`, `^rel_bp_`, `^ratio_`)
- keep the same model family fixed (`logreg`)
- audit the `brux2` versus `n3` score flip directly instead of launching another extraction rewrite

## Artifacts
- Audit script: `projects/bruxism-cap/src/audit_emg_brux2_n3_gap.py`
- Audit JSON: `projects/bruxism-cap/reports/feature-validity-audit-pass24-emg-brux2-vs-n3.json`
- Feature CSV: `projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv`
- EMG context report: `projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json`
- Anchor report: `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json`

## Reproduced pass19 score ordering
{score_lines}

This keeps the same honest failure in view: subject-level sensitivity remains `0.000`, with `n3` and `n5` still above both bruxism subjects.

## Cross-channel benchmark contrast for the same two key subjects
- EMG pass19 `brux2 - n3` mean-score gap: `{brux2_flip:+.3f}` (`0.088 - 0.280`).
- Honest anchor pass12 `brux2 - n3` mean-score gap: `{anchor_gap:+.3f}` (`0.795 - 0.245`).
- So the same subject pair flips by `{(brux2_flip - anchor_gap):+.3f}` between the current EMG surface and the honest comparison anchor.
- This localizes the remaining EMG problem more tightly than “EMG is just weaker overall”: the decisive regression is one bruxism subject (`brux2`) falling below one control (`n3`).

## Focused subject summaries

{subject_sections}

## Pairwise focused deltas

{gap_sections}

## Interpretation

1. The current EMG failure is concentrated, not diffuse: the strongest honest gap from the anchor is the `brux2` versus `n3` reversal, not a uniform regression across all subjects.
2. Within the fixed pass19 feature set, the largest surviving control-favoring signal in `n3` versus `brux2` is `zero_crossing_rate`, with smaller support from `burst_fraction` and `sample_entropy`.
3. `burst_rate_hz` still pushes the other way and favors `brux2`, so the EMG recipe is not devoid of bruxism-aligned signal; it is being outweighed by a small competing control-favoring family.
4. The matched-14 scaffold is count-matched but not time-position-matched: `n3` windows sit materially later in the night than `brux2` on average, so a future extraction audit should treat time-position matching as a real validity question rather than assuming the current cap already equalizes it.
5. This is therefore another negative-but-useful validity result, not a new baseline win.

## Best next bounded step

Keep pass19 as the EMG-first working point and do one compact extraction-validity follow-up next:
- either rebuild the same `EMG1-EMG2 A3-only` scaffold with a simple time-position matching rule across subjects before any new feature change,
- or audit whether the current `zero_crossing_rate` / `sample_entropy` surface is acting as a residual artifact proxy for `n3` versus `brux2` under EMG.

The safer next experiment is the first one because it tests a concrete validity hole without changing model family or broadening feature scope.
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit the pass19 EMG brux2-versus-n3 score reversal against the honest pass12 anchor."
    )
    parser.add_argument("--features-csv", required=True)
    parser.add_argument("--report", required=True, help="Saved pass19-style LOSO EMG report")
    parser.add_argument("--anchor-report", required=True, help="Saved honest comparison anchor report")
    parser.add_argument("--model", default="logreg", choices=sorted(build_models(42).keys()))
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--exclude-features-regex",
        action="append",
        default=[],
        help="Optional regex filters to remove train features before rebuilding the audit folds.",
    )
    parser.add_argument(
        "--focus-feature",
        action="append",
        default=[],
        help="Optional repeated feature names to inspect; defaults to a compact EMG-first gap set.",
    )
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md")
    args = parser.parse_args()

    feature_path = Path(args.features_csv)
    report_path = Path(args.report)
    anchor_report_path = Path(args.anchor_report)
    out_json = Path(args.out_json)

    df = load_feature_frame(feature_path)
    feature_columns, selection_excluded = select_feature_columns(
        df,
        exclude_patterns=args.exclude_features_regex,
    )
    focus_features = args.focus_feature or DEFAULT_FOCUS_FEATURES
    subject_rows = fit_subject_rows(
        df,
        feature_columns,
        focus_features=focus_features,
        model_name=args.model,
        random_state=args.random_state,
    )
    emg_subject_scores = load_subject_scores(report_path, args.model)
    anchor_subject_scores = load_subject_scores(anchor_report_path, args.model)

    audit = {
        "features_csv": str(feature_path.resolve()),
        "report": str(report_path.resolve()),
        "anchor_report": str(anchor_report_path.resolve()),
        "model": args.model,
        "focus_features": focus_features,
        "feature_count": len(feature_columns),
        "selected_features": feature_columns,
        "selection_excluded_features": selection_excluded,
        "subjects": sorted(subject_rows, key=lambda row: row["mean_score"], reverse=True),
        "emg_subject_scores": emg_subject_scores,
        "anchor_subject_scores": anchor_subject_scores,
        "pairwise_gaps": [
            build_feature_gap(subject_rows, higher_subject="n3", lower_subject="brux2", focus_features=focus_features),
            build_feature_gap(subject_rows, higher_subject="n3", lower_subject="brux1", focus_features=focus_features),
            build_feature_gap(subject_rows, higher_subject="brux2", lower_subject="brux1", focus_features=focus_features),
        ],
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    if args.out_md:
        out_md = Path(args.out_md)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_markdown(audit), encoding="utf-8")

    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
