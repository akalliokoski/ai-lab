from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from train_baseline import METADATA_COLUMNS, NON_TRAIN_FEATURE_COLUMNS, build_models

DEFAULT_FOCUS_FEATURES = [
    "mean",
    "std",
    "min",
    "max",
    "ptp",
    "line_length",
    "zero_crossing_rate",
    "sample_entropy",
    "rectified_mean",
    "envelope_mean",
    "envelope_cv",
    "burst_fraction",
    "burst_rate_hz",
    "p95_abs",
]


def load_feature_frame(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.empty:
        raise SystemExit(f"features CSV is empty: {path}")
    required = {"subject_id", "label", "start_s", "end_s"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"features CSV missing required columns {missing}: {path}")
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
                "predicted_positive_windows": int((proba >= 0.5).sum()),
                "positive_window_fraction": float((proba >= 0.5).mean()),
                "timing": {
                    "start_s": summarize_values(test_df["start_s"]),
                    "end_s": summarize_values(test_df["end_s"]),
                },
                "focus_features": focus_summary,
            }
        )
    return rows


def build_pairwise_gap(
    by_subject: dict[str, dict[str, Any]],
    *,
    higher_subject: str,
    lower_subject: str,
    focus_features: list[str],
) -> dict[str, Any]:
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


def audit_channel(
    *,
    channel_name: str,
    features_csv: Path,
    report_path: Path,
    feature_columns: list[str],
    focus_features: list[str],
    model_name: str,
    random_state: int,
) -> dict[str, Any]:
    df = load_feature_frame(features_csv)
    subject_rows = fit_subject_rows(
        df,
        feature_columns,
        focus_features=focus_features,
        model_name=model_name,
        random_state=random_state,
    )
    subject_rows.sort(key=lambda row: row["mean_score"], reverse=True)
    by_subject = {row["subject_id"]: row for row in subject_rows}
    report_subject_scores = load_subject_scores(report_path, model_name)
    return {
        "channel_name": channel_name,
        "features_csv": str(features_csv.resolve()),
        "report_path": str(report_path.resolve()),
        "subjects": subject_rows,
        "report_subject_scores": report_subject_scores,
        "pairwise_gaps": {
            "n3_minus_brux1": build_pairwise_gap(
                by_subject, higher_subject="n3", lower_subject="brux1", focus_features=focus_features
            ),
            "brux2_minus_n3": build_pairwise_gap(
                by_subject, higher_subject="brux2", lower_subject="n3", focus_features=focus_features
            ),
            "brux2_minus_brux1": build_pairwise_gap(
                by_subject, higher_subject="brux2", lower_subject="brux1", focus_features=focus_features
            ),
        },
    }


def build_timing_match_summary(emg_df: pd.DataFrame, c4_df: pd.DataFrame) -> dict[str, Any]:
    compare_cols = ["subject_id", "window_index", "start_s", "end_s", "relative_time_quantile", "time_match_rank"]
    emg_cols = [col for col in compare_cols if col in emg_df.columns]
    c4_cols = [col for col in compare_cols if col in c4_df.columns]
    shared_cols = [col for col in emg_cols if col in c4_cols]
    emg_view = emg_df[shared_cols].copy().sort_values(shared_cols).reset_index(drop=True)
    c4_view = c4_df[shared_cols].copy().sort_values(shared_cols).reset_index(drop=True)
    identical = emg_view.equals(c4_view)
    per_subject = []
    for subject_id in sorted(set(emg_df["subject_id"]) & set(c4_df["subject_id"])):
        emg_subject = emg_df.loc[emg_df["subject_id"] == subject_id]
        c4_subject = c4_df.loc[c4_df["subject_id"] == subject_id]
        per_subject.append(
            {
                "subject_id": subject_id,
                "rows": int(len(emg_subject)),
                "start_s_match": bool(emg_subject["start_s"].reset_index(drop=True).equals(c4_subject["start_s"].reset_index(drop=True))),
                "start_s_summary": summarize_values(emg_subject["start_s"]),
            }
        )
    return {
        "shared_columns_checked": shared_cols,
        "identical_selected_rows": bool(identical),
        "per_subject": per_subject,
    }


def top_features(gap: dict[str, Any], *, positive: bool, top_n: int = 5) -> list[dict[str, Any]]:
    filtered = [
        row
        for row in gap["feature_deltas"]
        if (row["mean_contribution_delta"] > 0 if positive else row["mean_contribution_delta"] < 0)
    ]
    return filtered[:top_n]


def render_gap_list(gap: dict[str, Any], *, positive: bool) -> str:
    rows = top_features(gap, positive=positive)
    if not rows:
        return "  - none"
    return "\n".join(
        f"  - `{row['feature']}` contribution delta `{row['mean_contribution_delta']:+.3f}` | "
        f"z-mean delta `{row['zscore_mean_delta']:+.3f}` | raw-mean delta `{row['raw_mean_delta']:+.6f}`"
        for row in rows
    )


def render_subject_line(channel: dict[str, Any], subject_id: str) -> str:
    row = next(row for row in channel["subjects"] if row["subject_id"] == subject_id)
    return (
        f"- `{subject_id}` ({row['true_label']}): mean LOSO score `{row['mean_score']:.3f}` | "
        f"positive-window fraction `{row['positive_window_fraction']:.3f}` | "
        f"start_s mean `{row['timing']['start_s']['mean']:.1f}`"
    )


def render_markdown(audit: dict[str, Any]) -> str:
    emg = audit["channels"]["emg"]
    c4 = audit["channels"]["c4"]
    emg_n3_brux1 = emg["pairwise_gaps"]["n3_minus_brux1"]
    c4_n3_brux1 = c4["pairwise_gaps"]["n3_minus_brux1"]
    emg_brux2_n3 = emg["pairwise_gaps"]["brux2_minus_n3"]
    c4_brux2_n3 = c4["pairwise_gaps"]["brux2_minus_n3"]

    return f"""# Pass 30 — percentile-band `A1-only` cross-channel gap audit (`EMG1-EMG2` vs `C4-P4`)

Date: 2026-05-05
Status: bounded validity audit completed; on the same repaired percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold, `brux1` still trails `n3` under both channels, but only `C4-P4` strongly flips `brux2` above `n3`, while `EMG1-EMG2` stays control-dominant because `mean` and crossing/amplitude terms remain hostile on the held-out `bruxism` folds

## Why this audit exists

Pass29 narrowed the remaining benchmark question sharply:
- the repaired percentile-band selector is usable and matched across channels
- `C4-P4` beats matched `EMG1-EMG2` on the honest LOSO surface without overturning the EMG-first project framing
- the remaining failure is now specific: `brux1` remains just below `n3` under both channels, while `brux2` recovers only under `C4-P4`

This pass makes exactly one bounded increment:
- keep the same verified `5`-subject exclusive `SLEEP-S2 + MCAP-A1-only` percentile-band scaffold fixed
- keep the same train-time exclusions fixed (`^bp_`, `^rel_bp_`, `^ratio_`)
- keep the same model family fixed (`logreg`)
- audit the subject-score gaps directly instead of launching another extraction rewrite

## Artifacts
- Audit script: `projects/bruxism-cap/src/audit_percentile_band_channel_gap.py`
- Audit JSON: `projects/bruxism-cap/reports/feature-validity-audit-pass30-a1-pct-channel-gap.json`
- EMG feature CSV: `projects/bruxism-cap/data/window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`
- C4 feature CSV: `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`
- EMG context report: `projects/bruxism-cap/reports/loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`
- C4 context report: `projects/bruxism-cap/reports/loso-cv-pass29-c4-a1-pct10-90-timepos10-selected.json`

## Matched-scaffold verification
- Selected rows are timing-matched across channels: `{audit['timing_match']['identical_selected_rows']}`.
- Shared columns checked: `{', '.join(audit['timing_match']['shared_columns_checked'])}`.
- Every subject keeps the same `10` selected windows, so this audit compares channel behavior rather than hidden availability drift.

## Reproduced subject score surfaces

### `EMG1-EMG2` (`logreg`)
{render_subject_line(emg, 'n3')}
{render_subject_line(emg, 'brux1')}
{render_subject_line(emg, 'brux2')}

### `C4-P4` (`logreg`)
{render_subject_line(c4, 'brux2')}
{render_subject_line(c4, 'n3')}
{render_subject_line(c4, 'brux1')}

## Key score-gap findings
- EMG `n3 - brux1` gap: `{emg_n3_brux1['score_gap']:+.3f}`.
- C4 `n3 - brux1` gap: `{c4_n3_brux1['score_gap']:+.3f}`.
- EMG `brux2 - n3` gap: `{emg_brux2_n3['score_gap']:+.3f}`.
- C4 `brux2 - n3` gap: `{c4_brux2_n3['score_gap']:+.3f}`.

So the repaired scaffold still leaves one shared hard case (`brux1 < n3`) under both channels, but the channel-level separation is now mostly about `brux2`: `C4-P4` pushes it decisively above `n3`, whereas `EMG1-EMG2` still leaves it far below.

## Focused feature deltas

### `EMG1-EMG2`: why `n3` stays above `brux1`
- features pushing toward `n3`:
{render_gap_list(emg_n3_brux1, positive=True)}
- features pushing back toward `brux1`:
{render_gap_list(emg_n3_brux1, positive=False)}

### `C4-P4`: why `n3` still barely stays above `brux1`
- features pushing toward `n3`:
{render_gap_list(c4_n3_brux1, positive=True)}
- features pushing back toward `brux1`:
{render_gap_list(c4_n3_brux1, positive=False)}

### `EMG1-EMG2`: why `brux2` fails to clear `n3`
- features pushing toward `brux2`:
{render_gap_list(emg_brux2_n3, positive=True)}
- features pushing back toward `n3`:
{render_gap_list(emg_brux2_n3, positive=False)}

### `C4-P4`: why `brux2` clears `n3`
- features pushing toward `brux2`:
{render_gap_list(c4_brux2_n3, positive=True)}
- features pushing back toward `n3`:
{render_gap_list(c4_brux2_n3, positive=False)}

## Interpretation

1. The repaired percentile-band scaffold is not the blocker anymore: selected rows are timing-matched across channels, so the pass28/pass29 difference is a real channel / feature-behavior difference.
2. `brux1` remains the shared unresolved subject. On both channels it stays below `n3`, but the gap is much smaller on `C4-P4` (`{c4_n3_brux1['score_gap']:+.3f}`) than on `EMG1-EMG2` (`{emg_n3_brux1['score_gap']:+.3f}`).
3. The EMG failure is harsher because `brux1` and especially `brux2` are still pulled down by hostile amplitude / crossing terms, while `n3` keeps support from control-favoring irregularity / burst features.
4. The C4 comparison-channel gain is concentrated in `brux2`: `zero_crossing_rate` becomes a large positive separator for `brux2` over `n3`, and the net `brux2 - n3` margin flips from negative on EMG to strongly positive on C4.
5. This preserves the EMG-first framing but sharpens the next validity target: the current open benchmark should explain or constrain the stubborn `brux1`-vs-`n3` overlap before trying larger models.

## Best next bounded step

Keep the repaired percentile-band `A1-only` scaffold fixed and do one compact audit or patch next on the shared `brux1`-vs-`n3` failure surface:
- safest: audit whether `n3`'s remaining support is concentrated in one narrow feature family (`sample_entropy`, `burst_fraction`, `envelope_cv`) across both channels,
- higher-upside but still bounded: rerun the same scaffold with one tiny cross-channel exclusion set targeted only at the recurring `n3`-favoring family, then compare whether `brux1` finally clears `n3` without breaking `brux2`.

The safer next move is the first one because this pass shows the project is now blocked more by one stubborn subject/control overlap than by global scaffold validity.
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit the repaired percentile-band A1-only subject-score gaps across EMG and C4 channels."
    )
    parser.add_argument("--emg-features-csv", required=True)
    parser.add_argument("--emg-report", required=True)
    parser.add_argument("--c4-features-csv", required=True)
    parser.add_argument("--c4-report", required=True)
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
        help="Optional repeated feature names to inspect; defaults to a compact cross-channel gap set.",
    )
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md")
    args = parser.parse_args()

    emg_path = Path(args.emg_features_csv)
    c4_path = Path(args.c4_features_csv)
    emg_df = load_feature_frame(emg_path)
    c4_df = load_feature_frame(c4_path)
    emg_features, emg_selection_excluded = select_feature_columns(
        emg_df, exclude_patterns=args.exclude_features_regex
    )
    c4_features, c4_selection_excluded = select_feature_columns(
        c4_df, exclude_patterns=args.exclude_features_regex
    )
    focus_features = args.focus_feature or DEFAULT_FOCUS_FEATURES

    audit = {
        "model": args.model,
        "focus_features": focus_features,
        "exclude_features_regex": args.exclude_features_regex,
        "timing_match": build_timing_match_summary(emg_df, c4_df),
        "channels": {
            "emg": audit_channel(
                channel_name="EMG1-EMG2",
                features_csv=emg_path,
                report_path=Path(args.emg_report),
                feature_columns=emg_features,
                focus_features=focus_features,
                model_name=args.model,
                random_state=args.random_state,
            ),
            "c4": audit_channel(
                channel_name="C4-P4",
                features_csv=c4_path,
                report_path=Path(args.c4_report),
                feature_columns=c4_features,
                focus_features=focus_features,
                model_name=args.model,
                random_state=args.random_state,
            ),
        },
        "feature_selection": {
            "emg_selected_features": emg_features,
            "emg_selection_excluded_features": emg_selection_excluded,
            "c4_selected_features": c4_features,
            "c4_selection_excluded_features": c4_selection_excluded,
        },
    }

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(audit, indent=2), encoding="utf-8")

    if args.out_md:
        out_md = Path(args.out_md)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_markdown(audit), encoding="utf-8")

    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
