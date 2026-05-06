from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from audit_percentile_band_channel_gap import (
    audit_channel,
    build_pairwise_gap,
    build_timing_match_summary,
    load_feature_frame,
    select_feature_columns,
)

DEFAULT_FAMILY_FEATURES = ["sample_entropy", "burst_fraction", "envelope_cv"]
DEFAULT_EXCLUDE_REGEXES = [r"^bp_", r"^rel_bp_", r"^ratio_"]


def summarize_family_share(gap: dict[str, Any], family_features: list[str], *, higher_subject: str) -> dict[str, Any]:
    positive_rows = [row for row in gap["feature_deltas"] if row["mean_contribution_delta"] > 0]
    positive_total = float(sum(row["mean_contribution_delta"] for row in positive_rows))
    family_positive_rows = [
        row
        for row in positive_rows
        if row["feature"] in family_features
    ]
    family_positive_total = float(sum(row["mean_contribution_delta"] for row in family_positive_rows))
    family_all_rows = [
        row
        for row in gap["feature_deltas"]
        if row["feature"] in family_features
    ]
    return {
        "higher_subject": higher_subject,
        "score_gap": float(gap["score_gap"]),
        "positive_feature_count": int(len(positive_rows)),
        "positive_contribution_total": positive_total,
        "family_positive_contribution_total": family_positive_total,
        "family_positive_share": float(family_positive_total / positive_total) if positive_total else 0.0,
        "family_positive_features": family_positive_rows,
        "family_all_features": family_all_rows,
        "top_positive_features": positive_rows[:8],
    }


def build_channel_summary(
    *,
    channel_name: str,
    features_csv: Path,
    report_path: Path,
    feature_columns: list[str],
    family_features: list[str],
    model_name: str,
    random_state: int,
) -> dict[str, Any]:
    channel = audit_channel(
        channel_name=channel_name,
        features_csv=features_csv,
        report_path=report_path,
        feature_columns=feature_columns,
        focus_features=feature_columns,
        model_name=model_name,
        random_state=random_state,
    )
    by_subject = {row["subject_id"]: row for row in channel["subjects"]}
    n3_minus_brux1 = build_pairwise_gap(
        by_subject,
        higher_subject="n3",
        lower_subject="brux1",
        focus_features=feature_columns,
    )
    n3_minus_brux2 = build_pairwise_gap(
        by_subject,
        higher_subject="n3",
        lower_subject="brux2",
        focus_features=feature_columns,
    )
    return {
        "channel_name": channel_name,
        "subjects": channel["subjects"],
        "n3_family_checks": {
            "n3_minus_brux1": summarize_family_share(
                n3_minus_brux1,
                family_features,
                higher_subject="n3",
            ),
            "n3_minus_brux2": summarize_family_share(
                n3_minus_brux2,
                family_features,
                higher_subject="n3",
            ),
        },
    }


def render_feature_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "  - none"
    return "\n".join(
        f"  - `{row['feature']}` contribution delta `{row['mean_contribution_delta']:+.3f}` | "
        f"z-mean delta `{row['zscore_mean_delta']:+.3f}` | raw-mean delta `{row['raw_mean_delta']:+.6f}`"
        for row in rows
    )


def render_subject_order(channel: dict[str, Any]) -> str:
    ordered = sorted(channel["subjects"], key=lambda row: row["mean_score"], reverse=True)
    return "\n".join(
        f"- `{row['subject_id']}` ({row['true_label']}): mean LOSO score `{row['mean_score']:.3f}` | positive-window fraction `{row['positive_window_fraction']:.3f}`"
        for row in ordered
    )


def recurrence_table(audit: dict[str, Any]) -> list[dict[str, Any]]:
    counts: dict[str, dict[str, Any]] = {}
    for channel_key in ["emg", "c4"]:
        channel = audit["channels"][channel_key]
        for contrast_name, summary in channel["n3_family_checks"].items():
            for row in summary["family_all_features"]:
                entry = counts.setdefault(
                    row["feature"],
                    {"feature": row["feature"], "positive_contrasts": 0, "negative_contrasts": 0, "net_contribution_delta": 0.0},
                )
                if row["mean_contribution_delta"] > 0:
                    entry["positive_contrasts"] += 1
                elif row["mean_contribution_delta"] < 0:
                    entry["negative_contrasts"] += 1
                entry["net_contribution_delta"] += float(row["mean_contribution_delta"])
    rows = list(counts.values())
    rows.sort(key=lambda row: (row["positive_contrasts"], abs(row["net_contribution_delta"])), reverse=True)
    return rows


def render_markdown(audit: dict[str, Any]) -> str:
    emg = audit["channels"]["emg"]
    c4 = audit["channels"]["c4"]
    emg_b1 = emg["n3_family_checks"]["n3_minus_brux1"]
    emg_b2 = emg["n3_family_checks"]["n3_minus_brux2"]
    c4_b1 = c4["n3_family_checks"]["n3_minus_brux1"]
    c4_b2 = c4["n3_family_checks"]["n3_minus_brux2"]
    recurrence = audit["family_recurrence"]
    recurrence_lines = "\n".join(
        f"- `{row['feature']}`: positive in `{row['positive_contrasts']}/4` contrasts | negative in `{row['negative_contrasts']}/4` | net contribution delta `{row['net_contribution_delta']:+.3f}`"
        for row in recurrence
    )

    return f"""# Pass 31 — recurrence audit of the suspected `n3`-favoring family on the matched percentile-band `A1-only` scaffold

Date: 2026-05-05
Status: bounded cross-channel validity audit completed; the suspected narrow `n3`-favoring family (`sample_entropy`, `burst_fraction`, `envelope_cv`) does recur, but it does **not** dominate the repaired scaffold across both channels. The harder EMG `n3` advantage is still driven more by broader amplitude / crossing features, so a tiny family-only ablation would be under-justified as the next primary experiment.

## Why this audit exists

Pass30 suggested a cautious next question rather than a new model change:
- keep the repaired percentile-band `SLEEP-S2 + MCAP-A1-only` scaffold fixed
- keep `EMG1-EMG2` primary and `C4-P4` comparative
- test whether the remaining `n3` support is really concentrated in one small feature family before patching the training surface

This pass makes exactly one primary increment:
- reuse the same matched pass28/pass29 rows and the same train-time exclusions
- keep the same LOSO `logreg` audit surface
- quantify how much of the positive `n3` gap is explained by the suspected family versus the full surviving feature set

## Artifacts
- Audit script: `projects/bruxism-cap/src/audit_percentile_band_n3_family_recurrence.py`
- Audit JSON: `projects/bruxism-cap/reports/feature-validity-audit-pass31-a1-pct-n3-family.json`
- Audit report: `projects/bruxism-cap/reports/pass31-a1-percentile-band-n3-family-recurrence.md`
- Matched EMG feature CSV: `projects/bruxism-cap/data/window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`
- Matched C4 feature CSV: `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`

## Matched-scaffold verification
- Selected rows are still timing-matched across channels: `{audit['timing_match']['identical_selected_rows']}`.
- Shared columns checked: `{', '.join(audit['timing_match']['shared_columns_checked'])}`.
- This audit therefore stays on the same repaired percentile-band scaffold and isolates feature-behavior interpretation rather than extraction drift.

## Reproduced subject orderings

### `EMG1-EMG2`
{render_subject_order(emg)}

### `C4-P4`
{render_subject_order(c4)}

## Family-share results

### `EMG1-EMG2`: `n3` over `brux1`
- score gap: `{emg_b1['score_gap']:+.3f}`
- total positive contribution toward `n3`: `{emg_b1['positive_contribution_total']:.3f}`
- suspected-family positive contribution: `{emg_b1['family_positive_contribution_total']:.3f}`
- suspected-family share of the positive `n3` gap: `{emg_b1['family_positive_share']:.3%}`
- top positive features overall:
{render_feature_rows(emg_b1['top_positive_features'])}
- suspected-family feature rows:
{render_feature_rows(emg_b1['family_all_features'])}

### `EMG1-EMG2`: `n3` over `brux2`
- score gap: `{emg_b2['score_gap']:+.3f}`
- total positive contribution toward `n3`: `{emg_b2['positive_contribution_total']:.3f}`
- suspected-family positive contribution: `{emg_b2['family_positive_contribution_total']:.3f}`
- suspected-family share of the positive `n3` gap: `{emg_b2['family_positive_share']:.3%}`
- top positive features overall:
{render_feature_rows(emg_b2['top_positive_features'])}
- suspected-family feature rows:
{render_feature_rows(emg_b2['family_all_features'])}

### `C4-P4`: `n3` over `brux1`
- score gap: `{c4_b1['score_gap']:+.3f}`
- total positive contribution toward `n3`: `{c4_b1['positive_contribution_total']:.3f}`
- suspected-family positive contribution: `{c4_b1['family_positive_contribution_total']:.3f}`
- suspected-family share of the positive `n3` gap: `{c4_b1['family_positive_share']:.3%}`
- top positive features overall:
{render_feature_rows(c4_b1['top_positive_features'])}
- suspected-family feature rows:
{render_feature_rows(c4_b1['family_all_features'])}

### `C4-P4`: `n3` over `brux2`
- score gap: `{c4_b2['score_gap']:+.3f}`
- total positive contribution toward `n3`: `{c4_b2['positive_contribution_total']:.3f}`
- suspected-family positive contribution: `{c4_b2['family_positive_contribution_total']:.3f}`
- suspected-family share of the positive `n3` gap: `{c4_b2['family_positive_share']:.3%}`
- top positive features overall:
{render_feature_rows(c4_b2['top_positive_features'])}
- suspected-family feature rows:
{render_feature_rows(c4_b2['family_all_features'])}

## Cross-channel recurrence of the suspected family
{recurrence_lines}

## Interpretation

1. The suspected family is **real but not sufficient**. It shows up repeatedly, but not as the dominant explanation of the repaired scaffold across both channels.
2. The harsher EMG failure surface is broader than `sample_entropy + burst_fraction + envelope_cv`: the biggest positive support for `n3` still comes from wider amplitude / shape / crossing terms, so a family-only ablation would risk underfitting the actual gap.
3. The C4 comparison result is also not a clean family story. `envelope_cv` does recur, but the shared `brux1 < n3` gap on `C4-P4` is still mostly about larger non-family contributors.
4. This is therefore a useful negative audit against over-narrowing the next patch. The repo should preserve the suspected family as part of the story, but not mistake it for the whole explanation.

## Best next bounded step

Keep the repaired percentile-band `A1-only` scaffold fixed and stay EMG-first.

The safest next experiment is now:
- rerun the matched pass28/pass29 scaffold with one **broader but still compact** exclusion family focused on the recurring control-favoring morphology terms (`mean`, `max`, `ptp`, `zero_crossing_rate`, plus the previously suspected trio),
- then compare whether `brux1` clears `n3` on `EMG1-EMG2` without erasing the useful `brux2` behavior on `C4-P4`.

That is better justified than a trio-only ablation because this audit shows the control advantage is not concentrated narrowly enough for the smaller patch to be trusted.
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit whether a suspected n3-favoring feature family really dominates the repaired percentile-band A1-only scaffold."
    )
    parser.add_argument("--emg-features-csv", required=True)
    parser.add_argument("--emg-report", required=True)
    parser.add_argument("--c4-features-csv", required=True)
    parser.add_argument("--c4-report", required=True)
    parser.add_argument("--model", default="logreg")
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--exclude-features-regex",
        action="append",
        default=[],
        help="Optional regex filters; defaults to the repaired scaffold exclusions when omitted.",
    )
    parser.add_argument(
        "--family-feature",
        action="append",
        default=[],
        help="Optional repeated feature names for the suspected family.",
    )
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md")
    args = parser.parse_args()

    exclude_patterns = args.exclude_features_regex or list(DEFAULT_EXCLUDE_REGEXES)
    family_features = args.family_feature or list(DEFAULT_FAMILY_FEATURES)

    emg_path = Path(args.emg_features_csv)
    c4_path = Path(args.c4_features_csv)
    emg_df = load_feature_frame(emg_path)
    c4_df = load_feature_frame(c4_path)
    emg_features, emg_selection_excluded = select_feature_columns(emg_df, exclude_patterns=exclude_patterns)
    c4_features, c4_selection_excluded = select_feature_columns(c4_df, exclude_patterns=exclude_patterns)

    audit = {
        "model": args.model,
        "family_features": family_features,
        "exclude_features_regex": exclude_patterns,
        "timing_match": build_timing_match_summary(emg_df, c4_df),
        "feature_selection": {
            "emg_selected_feature_count": len(emg_features),
            "c4_selected_feature_count": len(c4_features),
            "emg_selection_excluded_features": emg_selection_excluded,
            "c4_selection_excluded_features": c4_selection_excluded,
        },
        "channels": {
            "emg": build_channel_summary(
                channel_name="EMG1-EMG2",
                features_csv=emg_path,
                report_path=Path(args.emg_report),
                feature_columns=emg_features,
                family_features=family_features,
                model_name=args.model,
                random_state=args.random_state,
            ),
            "c4": build_channel_summary(
                channel_name="C4-P4",
                features_csv=c4_path,
                report_path=Path(args.c4_report),
                feature_columns=c4_features,
                family_features=family_features,
                model_name=args.model,
                random_state=args.random_state,
            ),
        },
    }
    audit["family_recurrence"] = recurrence_table(audit)

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
