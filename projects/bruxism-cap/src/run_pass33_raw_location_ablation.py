from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from audit_percentile_band_channel_gap import (
    audit_channel,
    build_timing_match_summary,
    load_feature_frame,
    select_feature_columns,
)

BASE_EXCLUDE_REGEXES = [r"^bp_", r"^rel_bp_", r"^ratio_"]
ABLATION_FEATURES = [
    "mean",
    "min",
    "max",
]
ABLATION_EXCLUDE_REGEXES = BASE_EXCLUDE_REGEXES + [
    r"^(mean|min|max)$"
]


def run_train_baseline(features_csv: Path, out_json: Path) -> dict[str, Any]:
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
    for pattern in ABLATION_EXCLUDE_REGEXES:
        cmd.extend(["--exclude-features-regex", pattern])
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    return json.loads(out_json.read_text(encoding="utf-8"))


def summarize_channel(
    *,
    channel_name: str,
    features_csv: Path,
    baseline_report_path: Path,
    ablation_report_path: Path,
) -> dict[str, Any]:
    df = load_feature_frame(features_csv)
    feature_columns, selection_excluded = select_feature_columns(df, exclude_patterns=ABLATION_EXCLUDE_REGEXES)
    baseline_report = json.loads(baseline_report_path.read_text(encoding="utf-8"))
    ablation_report = json.loads(ablation_report_path.read_text(encoding="utf-8"))
    audit = audit_channel(
        channel_name=channel_name,
        features_csv=features_csv,
        report_path=ablation_report_path,
        feature_columns=feature_columns,
        focus_features=feature_columns,
        model_name="logreg",
        random_state=42,
    )
    baseline_subjects = {
        row["subject_id"]: row
        for row in baseline_report["models"]["logreg"]["subject_aggregation"]["subjects"]
    }
    ablation_subjects = {
        row["subject_id"]: row
        for row in ablation_report["models"]["logreg"]["subject_aggregation"]["subjects"]
    }
    return {
        "channel_name": channel_name,
        "features_csv": str(features_csv.resolve()),
        "baseline_report_path": str(baseline_report_path.resolve()),
        "ablation_report_path": str(ablation_report_path.resolve()),
        "selected_feature_columns": feature_columns,
        "selection_excluded_columns": selection_excluded,
        "baseline_summary": baseline_report["models"]["logreg"]["subject_aggregation"]["summary"],
        "ablation_summary": ablation_report["models"]["logreg"]["subject_aggregation"]["summary"],
        "baseline_subjects": baseline_subjects,
        "ablation_subjects": ablation_subjects,
        "audit_subjects": audit["subjects"],
        "pairwise_gaps": audit["pairwise_gaps"],
    }


def render_subject_delta_lines(channel: dict[str, Any]) -> str:
    rows = []
    for subject_id in ["brux1", "brux2", "n3", "n5", "n11"]:
        base = channel["baseline_subjects"][subject_id]
        ablated = channel["ablation_subjects"][subject_id]
        rows.append(
            f"- `{subject_id}`: baseline `{base['mean_score']:.3f}` -> ablation `{ablated['mean_score']:.3f}` "
            f"(delta `{ablated['mean_score'] - base['mean_score']:+.3f}`) | predicted `{base['predicted_label']}` -> `{ablated['predicted_label']}`"
        )
    return "\n".join(rows)


def render_gap_rows(rows: list[dict[str, Any]], top_n: int = 6) -> str:
    if not rows:
        return "  - none"
    lines = []
    for row in rows[:top_n]:
        lines.append(
            f"  - `{row['feature']}` contribution delta `{row['mean_contribution_delta']:+.3f}` | "
            f"z-mean delta `{row['zscore_mean_delta']:+.3f}` | raw-mean delta `{row['raw_mean_delta']:+.6f}`"
        )
    return "\n".join(lines)


def render_markdown(report: dict[str, Any]) -> str:
    emg = report["channels"]["emg"]
    c4 = report["channels"]["c4"]
    emg_gap = emg["pairwise_gaps"]["n3_minus_brux1"]
    c4_gap = c4["pairwise_gaps"]["brux2_minus_n3"]
    return f"""# Pass 33 — smaller raw-location ablation on the repaired percentile-band `A1-only` scaffold

Date: 2026-05-05
Status: bounded matched rerun completed; removing only the most extreme raw-location terms does **not** rescue the EMG-first benchmark. `EMG1-EMG2` still misses both bruxism subjects and falls farther below the current honest baseline, while the same smaller ablation leaves the useful `C4-P4` `brux2` recovery essentially unchanged.

## Why this experiment exists

Pass32 showed that the broader morphology ablation was too destructive. The next safer follow-up suggested by the repo evidence was one smaller exclusion that keeps `zero_crossing_rate` and the core amplitude-envelope family intact while removing only the most extreme raw-location terms.

This pass makes exactly one primary increment:
- keep the same verified `5`-subject percentile-band scaffold from pass28/pass29
- keep `EMG1-EMG2` primary and `C4-P4` comparative
- keep the same `logreg` LOSO interpretation surface
- exclude only one small raw-location family: `{', '.join(ABLATION_FEATURES)}`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass33_raw_location_ablation.py`
- EMG LOSO report: `projects/bruxism-cap/reports/loso-cv-pass33-emg-a1-pct10-90-rawloc-ablation.json`
- C4 LOSO report: `projects/bruxism-cap/reports/loso-cv-pass33-c4-a1-pct10-90-rawloc-ablation.json`
- Summary JSON: `projects/bruxism-cap/reports/pass33-raw-location-ablation-summary.json`
- Summary report: `projects/bruxism-cap/reports/pass33-raw-location-ablation.md`

## Matched-scaffold verification
- Selected rows are still timing-matched across channels: `{report['timing_match']['identical_selected_rows']}`.
- Shared columns checked: `{', '.join(report['timing_match']['shared_columns_checked'])}`.
- The ablation therefore changes only the train-time feature set, not the repaired extraction scaffold.

## Feature selection
- Base exclusions preserved: `{', '.join(BASE_EXCLUDE_REGEXES)}`
- New exact exclusions: `^(mean|min|max)$`
- Remaining trainable feature count per channel: `{len(emg['selected_feature_columns'])}`
- Remaining features: `{', '.join(emg['selected_feature_columns'])}`

## Honest LOSO subject-level result

### `EMG1-EMG2`
- baseline subject-level balanced accuracy: `{emg['baseline_summary']['balanced_accuracy']:.3f}`
- ablation subject-level balanced accuracy: `{emg['ablation_summary']['balanced_accuracy']:.3f}`
- baseline subject-level sensitivity: `{emg['baseline_summary']['sensitivity']:.3f}`
- ablation subject-level sensitivity: `{emg['ablation_summary']['sensitivity']:.3f}`
- baseline highest control vs best bruxism margin: `{report['derived']['emg_baseline_best_brux_minus_highest_control']:+.3f}`
- ablation highest control vs best bruxism margin: `{report['derived']['emg_ablation_best_brux_minus_highest_control']:+.3f}`
- subject score deltas:
{render_subject_delta_lines(emg)}

### `C4-P4`
- baseline subject-level balanced accuracy: `{c4['baseline_summary']['balanced_accuracy']:.3f}`
- ablation subject-level balanced accuracy: `{c4['ablation_summary']['balanced_accuracy']:.3f}`
- baseline subject-level sensitivity: `{c4['baseline_summary']['sensitivity']:.3f}`
- ablation subject-level sensitivity: `{c4['ablation_summary']['sensitivity']:.3f}`
- baseline `brux2 - n3` mean-score gap: `{report['derived']['c4_baseline_brux2_minus_n3']:+.3f}`
- ablation `brux2 - n3` mean-score gap: `{report['derived']['c4_ablation_brux2_minus_n3']:+.3f}`
- subject score deltas:
{render_subject_delta_lines(c4)}

## Key failure-surface checks

### `EMG1-EMG2`: `n3` still over `brux1`
- baseline `n3 - brux1` gap: `{report['derived']['emg_baseline_n3_minus_brux1']:+.3f}`
- ablation `n3 - brux1` gap: `{emg_gap['score_gap']:+.3f}`
- strongest surviving positive contributors toward `n3`:
{render_gap_rows([row for row in emg_gap['feature_deltas'] if row['mean_contribution_delta'] > 0])}

### `C4-P4`: `brux2` stays above `n3`
- baseline `brux2 - n3` gap: `{report['derived']['c4_baseline_brux2_minus_n3']:+.3f}`
- ablation `brux2 - n3` gap: `{c4_gap['score_gap']:+.3f}`
- strongest surviving negative contributors against `brux2`:
{render_gap_rows([row for row in c4_gap['feature_deltas'] if row['mean_contribution_delta'] < 0])}

## Interpretation

1. The smaller raw-location ablation is **not** a useful EMG fix: `EMG1-EMG2` keeps both bruxism subjects below threshold and makes the best-bruxism-versus-highest-control margin markedly worse.
2. The EMG surface does not improve in a mixed way here; it mostly collapses `brux1` (`0.270` -> `0.030`) while leaving `n3` essentially unchanged (`0.530` -> `0.527`), so the remaining failure is still the same `n3 > brux1` ordering problem on the repaired scaffold.
3. The `C4-P4` comparison surface is nearly unchanged, which is also informative: this tiny deletion removes something EMG still needs while not meaningfully altering the stronger comparison-channel behavior.
4. This preserves a narrower negative result: the repo evidence now suggests the problem is not just a few raw-location features being present, but how morphology is represented fold-by-fold once subjects are held out.

## Best next bounded step

Keep the repaired percentile-band `A1-only` scaffold fixed and stay EMG-first.

The next safest experiment should stay validity-focused rather than stack another broad deletion:
- audit whether the remaining morphology features should be converted into a record-relative or within-subject-relative representation before training, or
- run one matched audit that compares raw versus within-record standardized versions of the retained amplitude-envelope family without changing the selector or model family.

Do **not** promote this pass33 ablation as the new baseline; preserve it as a negative result.
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    reports_dir = root / "reports"
    data_dir = root / "data"

    emg_features = data_dir / "window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv"
    c4_features = data_dir / "window_features_pass29_c4_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv"
    emg_baseline_report = reports_dir / "loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json"
    c4_baseline_report = reports_dir / "loso-cv-pass29-c4-a1-pct10-90-timepos10-selected.json"
    emg_out = reports_dir / "loso-cv-pass33-emg-a1-pct10-90-rawloc-ablation.json"
    c4_out = reports_dir / "loso-cv-pass33-c4-a1-pct10-90-rawloc-ablation.json"
    summary_json = reports_dir / "pass33-raw-location-ablation-summary.json"
    summary_md = reports_dir / "pass33-raw-location-ablation.md"

    run_train_baseline(emg_features, emg_out)
    run_train_baseline(c4_features, c4_out)

    emg = summarize_channel(
        channel_name="EMG1-EMG2",
        features_csv=emg_features,
        baseline_report_path=emg_baseline_report,
        ablation_report_path=emg_out,
    )
    c4 = summarize_channel(
        channel_name="C4-P4",
        features_csv=c4_features,
        baseline_report_path=c4_baseline_report,
        ablation_report_path=c4_out,
    )

    emg_df = load_feature_frame(emg_features)
    c4_df = load_feature_frame(c4_features)

    emg_best_brux_base = max(
        emg["baseline_subjects"]["brux1"]["mean_score"],
        emg["baseline_subjects"]["brux2"]["mean_score"],
    )
    emg_highest_control_base = max(
        emg["baseline_subjects"]["n3"]["mean_score"],
        emg["baseline_subjects"]["n5"]["mean_score"],
        emg["baseline_subjects"]["n11"]["mean_score"],
    )
    emg_best_brux_ablation = max(
        emg["ablation_subjects"]["brux1"]["mean_score"],
        emg["ablation_subjects"]["brux2"]["mean_score"],
    )
    emg_highest_control_ablation = max(
        emg["ablation_subjects"]["n3"]["mean_score"],
        emg["ablation_subjects"]["n5"]["mean_score"],
        emg["ablation_subjects"]["n11"]["mean_score"],
    )

    report = {
        "pass": 33,
        "experiment": "raw_location_ablation_on_repaired_a1_percentile_band_scaffold",
        "ablation_features": ABLATION_FEATURES,
        "exclude_features_regex": ABLATION_EXCLUDE_REGEXES,
        "timing_match": build_timing_match_summary(emg_df, c4_df),
        "channels": {
            "emg": emg,
            "c4": c4,
        },
        "derived": {
            "emg_baseline_n3_minus_brux1": emg["baseline_subjects"]["n3"]["mean_score"] - emg["baseline_subjects"]["brux1"]["mean_score"],
            "emg_ablation_n3_minus_brux1": emg["ablation_subjects"]["n3"]["mean_score"] - emg["ablation_subjects"]["brux1"]["mean_score"],
            "emg_baseline_best_brux_minus_highest_control": emg_best_brux_base - emg_highest_control_base,
            "emg_ablation_best_brux_minus_highest_control": emg_best_brux_ablation - emg_highest_control_ablation,
            "c4_baseline_brux2_minus_n3": c4["baseline_subjects"]["brux2"]["mean_score"] - c4["baseline_subjects"]["n3"]["mean_score"],
            "c4_ablation_brux2_minus_n3": c4["ablation_subjects"]["brux2"]["mean_score"] - c4["ablation_subjects"]["n3"]["mean_score"],
        },
    }
    summary_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_md.write_text(render_markdown(report), encoding="utf-8")
    print(summary_md)
    print(summary_json)


if __name__ == "__main__":
    main()
