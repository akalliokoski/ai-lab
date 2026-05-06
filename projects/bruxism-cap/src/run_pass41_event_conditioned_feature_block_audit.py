from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from audit_percentile_band_channel_gap import select_feature_columns
from features import emg_event_block_features, robust_rectified_reference
from prepare_windows import choose_channel, load_raw
from run_pass34_record_relative_emg_audit import (
    BASE_EXCLUDE_REGEXES,
    EPSILON,
    RELATIVE_FEATURES,
    build_record_relative_table,
)
from run_pass36_record_relative_shape_composition_audit import (
    SHAPE_FEATURES,
    build_composed_table,
    load_subjects,
    summarize_counts,
    validate_same_selected_rows,
)

PASS_NUMBER = 41
SUBJECT_IDS = ["brux1", "brux2", "n3", "n5", "n11"]
ROW_ID_COLUMNS = ["subject_id", "start_s", "end_s"]
EVENT_FEATURES = [
    "evt_burst_count_30s",
    "evt_episode_count_30s",
    "evt_bursts_per_episode_mean",
    "evt_active_fraction",
    "evt_burst_duration_median_s",
    "evt_interburst_gap_median_s",
    "evt_phasic_like_episode_fraction",
]
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
EVENT_CONFIG = {
    "threshold_rule": "max(2.0 * median_rectified, median_rectified + 2.0 * mad_rectified, 1e-6)",
    "min_burst_s": 0.25,
    "merge_gap_s": 0.08,
    "max_episode_gap_s": 3.0,
    "window_container_s": 30.0,
}


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


def best_brux_minus_highest_control(subjects: dict[str, dict[str, Any]]) -> float:
    best_brux = max(subjects["brux1"]["mean_score"], subjects["brux2"]["mean_score"])
    highest_control = max(subjects["n3"]["mean_score"], subjects["n5"]["mean_score"], subjects["n11"]["mean_score"])
    return float(best_brux - highest_control)


def format_score(value: float) -> str:
    if abs(value) < 1e-6:
        return f"{value:.2e}"
    return f"{value:.3f}"


def build_subject_rows(df: pd.DataFrame, feature_columns: list[str]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    amp_disp_features = [feature for feature in AMP_DISP_FEATURES if feature in feature_columns]
    shape_features = [feature for feature in SHAPE_FEATURES if feature in feature_columns]
    event_features = [feature for feature in EVENT_FEATURES if feature in feature_columns]
    other_features = [
        feature
        for feature in feature_columns
        if feature not in amp_disp_features and feature not in shape_features and feature not in event_features
    ]
    subjects: dict[str, Any] = {}

    from train_baseline import build_models

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
        rows["event_contrib"] = contrib[event_features].sum(axis=1)
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
                "event_mean": float(group["event_contrib"].mean()),
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
                "event": float(rows["event_contrib"].mean()),
                "other": float(rows["other_contrib"].mean()),
            },
            "grouped": grouped,
            "rows_by_time_rank": rows.to_dict(orient="records"),
            "feature_means": feature_means,
        }

    return subjects, {
        "amp_disp": amp_disp_features,
        "shape": shape_features,
        "event": event_features,
        "other": other_features,
    }


def build_pairwise(subjects: dict[str, Any], feature_columns: list[str], block_features: dict[str, list[str]]) -> dict[str, Any]:
    pairwise = {}
    for higher_subject in ["n5", "n11"]:
        feature_rows = []
        for feature in feature_columns:
            higher = subjects[higher_subject]["feature_means"][feature]
            lower = subjects["brux1"]["feature_means"][feature]
            if feature in block_features["shape"]:
                block = "shape"
            elif feature in block_features["amp_disp"]:
                block = "amp_disp"
            elif feature in block_features["event"]:
                block = "event"
            else:
                block = "other"
            feature_rows.append(
                {
                    "feature": feature,
                    "mean_contribution_delta": float(higher["mean_contribution"] - lower["mean_contribution"]),
                    "raw_mean_delta": float(higher["raw_mean"] - lower["raw_mean"]),
                    "z_mean_delta": float(higher["z_mean"] - lower["z_mean"]),
                    "block": block,
                }
            )
        feature_rows.sort(key=lambda row: abs(row["mean_contribution_delta"]), reverse=True)
        block_sums = {
            block: float(sum(row["mean_contribution_delta"] for row in feature_rows if row["block"] == block))
            for block in ["amp_disp", "shape", "event", "other"]
        }
        pairwise[f"{higher_subject}_minus_brux1"] = {
            "score_gap": float(subjects[higher_subject]["mean_score"] - subjects["brux1"]["mean_score"]),
            "block_sums": block_sums,
            "top_positive": [row for row in feature_rows if row["mean_contribution_delta"] > 0][:10],
            "top_negative": [row for row in feature_rows if row["mean_contribution_delta"] < 0][:10],
            "event_positive": [
                row for row in feature_rows if row["block"] == "event" and row["mean_contribution_delta"] > 0
            ][:7],
            "event_negative": [
                row for row in feature_rows if row["block"] == "event" and row["mean_contribution_delta"] < 0
            ][:7],
        }
    return pairwise


def render_subject_score_lines(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{row['subject_id']}`: pass36 `{row['pass36_score']:.3f}` -> pass40 `{row['pass40_score']:.3f}` -> pass41 `{row['pass41_score']:.3f}` | "
        f"delta vs pass36 `{row['delta_vs_pass36']:+.3f}` | delta vs pass40 `{row['delta_vs_pass40']:+.3f}` | "
        f"predicted `{row['pass36_predicted_label']}` -> `{row['pass41_predicted_label']}`"
        for row in rows
    )


def render_early_delta_lines(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- rank `{row['time_match_rank']}` | window `{row['window_index']}` | start `{row['start_s']:.0f}s` | "
        f"score pass36 `{format_score(row['pass36_score'])}` -> pass40 `{format_score(row['pass40_score'])}` -> pass41 `{format_score(row['pass41_score'])}` | "
        f"event block pass41 `{row['pass41_event']:+.3f}` | amp/disp pass41 `{row['pass41_amp_disp']:+.3f}` | shape pass41 `{row['pass41_shape']:+.3f}` | other pass41 `{row['pass41_other']:+.3f}`"
        for row in rows
    )


def render_feature_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- none"
    return "\n".join(
        f"- `{row['feature']}` contribution delta `{row['mean_contribution_delta']:+.3f}` | z-mean delta `{row['z_mean_delta']:+.3f}` | raw-mean delta `{row['raw_mean_delta']:+.6f}`"
        for row in rows
    )


def load_event_features(pass28_df: pd.DataFrame, *, root: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    records_dir = root / "data/raw/capslpdb"
    rows: list[dict[str, Any]] = []
    per_subject: dict[str, Any] = {}

    for subject_id, subject_df in pass28_df.groupby("subject_id", sort=False):
        source_file = str(subject_df["source_file"].iloc[0])
        edf_path = records_dir / source_file
        raw = load_raw(edf_path)
        channel_name = choose_channel(raw, str(subject_df["channel"].iloc[0]))
        sfreq = float(raw.info["sfreq"])
        full_signal = raw.get_data(picks=[channel_name])[0]
        reference = robust_rectified_reference(full_signal, floor=EPSILON)
        per_subject[str(subject_id)] = {
            "edf_path": str(edf_path.resolve()),
            "channel": channel_name,
            "sfreq": sfreq,
            "record_duration_s": float(raw.n_times / sfreq),
            **reference,
        }

        for row in subject_df.sort_values(["start_s", "end_s", "window_index"]).to_dict(orient="records"):
            start_sample = int(round(float(row["start_s"]) * sfreq))
            end_sample = int(round(float(row["end_s"]) * sfreq))
            window = raw.get_data(picks=[channel_name], start=start_sample, stop=end_sample)[0]
            event_features = emg_event_block_features(
                window,
                sfreq,
                reference_rectified_median=reference["median_rectified"],
                reference_rectified_mad=reference["mad_rectified"],
                threshold_floor=EPSILON,
                min_burst_s=EVENT_CONFIG["min_burst_s"],
                merge_gap_s=EVENT_CONFIG["merge_gap_s"],
                max_episode_gap_s=EVENT_CONFIG["max_episode_gap_s"],
            )
            rows.append(
                {
                    "subject_id": row["subject_id"],
                    "start_s": float(row["start_s"]),
                    "end_s": float(row["end_s"]),
                    "window_index": int(row["window_index"]),
                    **event_features,
                }
            )
        if hasattr(raw, "close"):
            raw.close()

    return pd.DataFrame(rows), per_subject


def build_subject_score_rows(
    *,
    pass36_subjects: dict[str, Any],
    pass40_subjects: dict[str, Any],
    pass41_subjects: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for subject_id in SUBJECT_IDS:
        rows.append(
            {
                "subject_id": subject_id,
                "pass36_score": float(pass36_subjects[subject_id]["mean_score"]),
                "pass40_score": float(pass40_subjects[subject_id]["mean_score"]),
                "pass41_score": float(pass41_subjects[subject_id]["mean_score"]),
                "delta_vs_pass36": float(pass41_subjects[subject_id]["mean_score"] - pass36_subjects[subject_id]["mean_score"]),
                "delta_vs_pass40": float(pass41_subjects[subject_id]["mean_score"] - pass40_subjects[subject_id]["mean_score"]),
                "pass36_predicted_label": pass36_subjects[subject_id]["predicted_label"],
                "pass41_predicted_label": pass41_subjects[subject_id]["predicted_label"],
            }
        )
    return rows


def build_early_window_deltas(*, pass36_rows: list[dict[str, Any]], pass40_rows: list[dict[str, Any]], pass41_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deltas = []
    for row36, row40, row41 in zip(pass36_rows[:3], pass40_rows[:3], pass41_rows[:3], strict=True):
        deltas.append(
            {
                "time_match_rank": int(row41["time_match_rank"]),
                "window_index": int(row41["window_index"]),
                "start_s": float(row41["start_s"]),
                "pass36_score": float(row36["score"]),
                "pass40_score": float(row40["score"]),
                "pass41_score": float(row41["score"]),
                "pass41_event": float(row41["event_contrib"]),
                "pass41_amp_disp": float(row41["amp_disp_contrib"]),
                "pass41_shape": float(row41["shape_contrib"]),
                "pass41_other": float(row41["other_contrib"]),
            }
        )
    return deltas


def render_markdown(report: dict[str, Any]) -> str:
    pass36_summary = report["anchors"]["pass36"]["subject_summary"]
    pass40_summary = report["anchors"]["pass40"]["subject_summary"]
    pass41_summary = report["pass41"]["subject_summary"]
    pass36_early = report["anchors"]["pass36"]["subjects_audit"]["brux1"]["grouped"]["early_ranks_1_3"]
    pass40_early = report["anchors"]["pass40"]["subjects_audit"]["brux1"]["grouped"]["early_ranks_1_3"]
    pass41_early = report["pass41"]["subjects_audit"]["brux1"]["grouped"]["early_ranks_1_3"]
    pair_n5 = report["pass41"]["pairwise"]["n5_minus_brux1"]
    pair_n11 = report["pass41"]["pairwise"]["n11_minus_brux1"]
    best_prior_brux1 = max(
        report["anchors"]["pass36"]["subjects_scores"]["brux1"],
        report["anchors"]["pass40"]["subjects_scores"]["brux1"],
    )
    pass41_brux1 = report["pass41"]["subjects_scores"]["brux1"]
    improved_brux1 = pass41_brux1 > best_prior_brux1
    controls_reopened = pass41_summary["specificity"] < min(pass36_summary["specificity"], pass40_summary["specificity"])
    if improved_brux1 and not controls_reopened:
        verdict = "Pass41 improves the target subject without reopening the repaired controls, but the gain is still sub-threshold and should be treated as a localization result rather than a solved benchmark."
        next_step = "Keep the same five-subject scaffold fixed and run one equally bounded follow-up that leaves the 7-event block untouched but adds record-relative companions only for the magnitude-like event counts/density features (`evt_burst_count_30s`, `evt_episode_count_30s`, `evt_bursts_per_episode_mean`, `evt_active_fraction`) to test whether the event signal is present but still under-scaled against subject baselines."
    elif improved_brux1:
        verdict = "Pass41 raises `brux1`, but the gain comes with weaker control protection, so the event block is informative but not yet a clean benchmark improvement."
        next_step = "Keep the pass41 event block fixed and do one bounded ablation on the same table: test `pass36 + only the 3 least control-damaging event features` to isolate whether one count/duration component is causing the control reopening."
    else:
        verdict = "Pass41 does not beat the best prior `brux1` subject score, so the raw appended event block is evidence of direction, not a finished rescue."
        next_step = "Keep the 7-event block fixed and do one bounded follow-up that makes only the event-count/density subset record-relative, while leaving duration/gap/phase features raw. That answers whether the failure is feature family mismatch or just event-scale mismatch."

    return f"""# Pass 41 — bounded event-conditioned EMG feature block audit on the repaired CAP scaffold

Date: 2026-05-05
Status: bounded representation audit completed. This pass keeps the repaired five-subject `SLEEP-S2 + MCAP-A1-only` `EMG1-EMG2` percentile-band scaffold, the pass34 record-relative transform, the pass35 compact shape merge, the same train-time exclusions, and the same `logreg` LOSO contract fixed, then appends exactly 7 raw event-conditioned jaw-EMG features to ask one new question outside the closed pass37-pass40 floor family.

## Exact bounded feature logic implemented

Container held fixed:
- 30 s windows from the existing pass28 repaired selected table.
- No selector rerun, no channel pivot, no dataset switch, no model-family change.

Event rule:
- rectified basis: `abs(window_signal - mean(window_signal))`
- per-record threshold reference: `median_rectified` and `mad_rectified` computed from the full selected record channel before window slicing
- active sample threshold: `{report['event_config']['threshold_rule']}`
- burst = contiguous active run lasting `>= {report['event_config']['min_burst_s']:.2f}s`
- merge micro-gaps shorter than `{report['event_config']['merge_gap_s']:.2f}s`
- episode = one or more bursts with inter-burst gap `< {report['event_config']['max_episode_gap_s']:.1f}s`
- phasic-like episode = `>=3` bursts and every burst duration in `[0.25, 2.0]s`

Appended event block:
- `{', '.join(EVENT_FEATURES)}`

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass41_event_conditioned_feature_block_audit.py`
- Feature helper update: `projects/bruxism-cap/src/features.py`
- Pass41 feature table: `projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass41-emg-a1-pct10-90-record-relative-shape-eventblock.json`
- Summary JSON: `projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.json`
- Summary report: `projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.md`

## Scaffold parity checks
- pass36 counts: `{report['anchors']['pass36']['counts_by_subject']}`
- pass40 counts: `{report['anchors']['pass40']['counts_by_subject']}`
- pass41 counts: `{report['pass41']['counts_by_subject']}`
- row-alignment warnings: `{report['warnings']}`
- unchanged train-time exclusions: `{report['pass41']['selection_excluded_columns']}`

## Apples-to-apples subject-level comparison against pass36 and pass40
- pass36 balanced accuracy: `{pass36_summary['balanced_accuracy']:.3f}`
- pass40 balanced accuracy: `{pass40_summary['balanced_accuracy']:.3f}`
- pass41 balanced accuracy: `{pass41_summary['balanced_accuracy']:.3f}`
- pass36 sensitivity: `{pass36_summary['sensitivity']:.3f}`
- pass40 sensitivity: `{pass40_summary['sensitivity']:.3f}`
- pass41 sensitivity: `{pass41_summary['sensitivity']:.3f}`
- pass36 specificity: `{pass36_summary['specificity']:.3f}`
- pass40 specificity: `{pass40_summary['specificity']:.3f}`
- pass41 specificity: `{pass41_summary['specificity']:.3f}`
- pass36 best-bruxism-minus-highest-control margin: `{report['derived']['pass36_best_brux_minus_highest_control']:+.3f}`
- pass40 best-bruxism-minus-highest-control margin: `{report['derived']['pass40_best_brux_minus_highest_control']:+.3f}`
- pass41 best-bruxism-minus-highest-control margin: `{report['derived']['pass41_best_brux_minus_highest_control']:+.3f}`

Subject score deltas:
{render_subject_score_lines(report['derived']['subject_score_rows'])}

## Did `brux1` improve without reopening controls?
- `brux1`: pass36 `{report['anchors']['pass36']['subjects_scores']['brux1']:.3f}` -> pass40 `{report['anchors']['pass40']['subjects_scores']['brux1']:.3f}` -> pass41 `{report['pass41']['subjects_scores']['brux1']:.3f}`
- `n3`: pass36 `{report['anchors']['pass36']['subjects_scores']['n3']:.3f}` -> pass40 `{report['anchors']['pass40']['subjects_scores']['n3']:.3f}` -> pass41 `{report['pass41']['subjects_scores']['n3']:.3f}`
- `n5`: pass36 `{report['anchors']['pass36']['subjects_scores']['n5']:.3f}` -> pass40 `{report['anchors']['pass40']['subjects_scores']['n5']:.3f}` -> pass41 `{report['pass41']['subjects_scores']['n5']:.3f}`
- `n11`: pass36 `{report['anchors']['pass36']['subjects_scores']['n11']:.3f}` -> pass40 `{report['anchors']['pass40']['subjects_scores']['n11']:.3f}` -> pass41 `{report['pass41']['subjects_scores']['n11']:.3f}`
- pass41 `brux1 - n3`: `{report['derived']['brux1_minus_n3_pass41']:+.3f}`
- pass41 `n5 - brux1`: `{report['derived']['n5_minus_brux1_pass41']:+.3f}`
- pass41 `n11 - brux1`: `{report['derived']['n11_minus_brux1_pass41']:+.3f}`

## What happened to the early `brux1` trio?
- early ranks `1-3` mean score: pass36 `{format_score(pass36_early['mean_score'])}` -> pass40 `{format_score(pass40_early['mean_score'])}` -> pass41 `{format_score(pass41_early['mean_score'])}`
- early ranks `1-3` event contribution mean on pass41: `{pass41_early['event_mean']:+.3f}`
- early ranks `1-3` amp/disp mean on pass41: `{pass41_early['amp_disp_mean']:+.3f}`
- early ranks `1-3` shape mean on pass41: `{pass41_early['shape_mean']:+.3f}`

Early-window detail:
{render_early_delta_lines(report['derived']['early_window_deltas'])}

## Event-block deltas against `brux1`
### `n5 - brux1`
- block sums: amp/disp `{pair_n5['block_sums']['amp_disp']:+.3f}` | shape `{pair_n5['block_sums']['shape']:+.3f}` | event `{pair_n5['block_sums']['event']:+.3f}` | other `{pair_n5['block_sums']['other']:+.3f}`
- positive event deltas:
{render_feature_rows(pair_n5['event_positive'])}
- negative event deltas:
{render_feature_rows(pair_n5['event_negative'])}

### `n11 - brux1`
- block sums: amp/disp `{pair_n11['block_sums']['amp_disp']:+.3f}` | shape `{pair_n11['block_sums']['shape']:+.3f}` | event `{pair_n11['block_sums']['event']:+.3f}` | other `{pair_n11['block_sums']['other']:+.3f}`
- positive event deltas:
{render_feature_rows(pair_n11['event_positive'])}
- negative event deltas:
{render_feature_rows(pair_n11['event_negative'])}

## Verdict
{verdict}

## Safest next bounded step
{next_step}
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    reports_dir = root / "reports"

    pass28_features = data_dir / "window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv"
    pass35_features = data_dir / "window_features_pass35_emg_s2_mcap_a1_only_pct10_90_timepos10_shape.csv"
    pass36_features = data_dir / "window_features_pass36_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape.csv"
    pass40_features = data_dir / "window_features_pass40_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_envcv_rectstd_floor.csv"
    pass36_report_path = reports_dir / "loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json"
    pass40_report_path = reports_dir / "loso-cv-pass40-emg-a1-pct10-90-record-relative-shape-envcv-rectstd-floor.json"
    pass41_features = data_dir / "window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv"
    pass41_report_path = reports_dir / "loso-cv-pass41-emg-a1-pct10-90-record-relative-shape-eventblock.json"
    summary_json_path = reports_dir / "pass41-event-conditioned-feature-block-audit.json"
    summary_md_path = reports_dir / "pass41-event-conditioned-feature-block-audit.md"

    pass28_df = pd.read_csv(pass28_features)
    pass35_df = pd.read_csv(pass35_features)
    pass36_df = pd.read_csv(pass36_features)
    pass40_df = pd.read_csv(pass40_features)
    pass36_report = json.loads(pass36_report_path.read_text(encoding="utf-8"))
    pass40_report = json.loads(pass40_report_path.read_text(encoding="utf-8"))

    pass34_df, _ = build_record_relative_table(pass28_df, relative_features=RELATIVE_FEATURES, epsilon=EPSILON)
    recomposed_pass36_df, composition_summary = build_composed_table(pass34_df=pass34_df, pass35_df=pass35_df)

    event_df, event_reference = load_event_features(pass28_df, root=root)
    pass41_df = recomposed_pass36_df.merge(event_df, on=ROW_ID_COLUMNS + ["window_index"], how="left", validate="one_to_one")
    null_event_counts = pass41_df[EVENT_FEATURES].isnull().sum().to_dict()
    if any(count > 0 for count in null_event_counts.values()):
        raise SystemExit(f"pass41 event merge left nulls: {null_event_counts}")
    pass41_df.to_csv(pass41_features, index=False)

    warnings = []
    warnings.extend(validate_same_selected_rows(left_df=pass36_df, right_df=recomposed_pass36_df, label="pass36 recomposition"))
    warnings.extend(validate_same_selected_rows(left_df=pass36_df, right_df=pass41_df, label="pass41 vs pass36"))
    warnings.extend(validate_same_selected_rows(left_df=pass40_df, right_df=pass41_df, label="pass41 vs pass40"))

    pass41_report = run_train_baseline(features_csv=pass41_features, out_json=pass41_report_path)

    pass36_feature_columns, pass36_selection_excluded = select_feature_columns(pass36_df, exclude_patterns=BASE_EXCLUDE_REGEXES)
    pass40_feature_columns, pass40_selection_excluded = select_feature_columns(pass40_df, exclude_patterns=BASE_EXCLUDE_REGEXES)
    pass41_feature_columns, pass41_selection_excluded = select_feature_columns(pass41_df, exclude_patterns=BASE_EXCLUDE_REGEXES)

    pass36_subjects_audit, pass36_blocks = build_subject_rows(pass36_df, pass36_feature_columns)
    pass40_subjects_audit, pass40_blocks = build_subject_rows(pass40_df, pass40_feature_columns)
    pass41_subjects_audit, pass41_blocks = build_subject_rows(pass41_df, pass41_feature_columns)
    pass41_pairwise = build_pairwise(pass41_subjects_audit, pass41_feature_columns, pass41_blocks)

    pass36_subjects = load_subjects(pass36_report)
    pass40_subjects = load_subjects(pass40_report)
    pass41_subjects = load_subjects(pass41_report)

    report = {
        "pass": PASS_NUMBER,
        "experiment": "event_conditioned_feature_block_audit_on_repaired_cap_scaffold",
        "anchors": {
            "pass36": {
                "features_csv": str(pass36_features.resolve()),
                "report_path": str(pass36_report_path.resolve()),
                "subject_summary": pass36_report["models"]["logreg"]["subject_aggregation"]["summary"],
                "subjects_scores": {subject_id: float(pass36_subjects[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS},
                "subjects": pass36_subjects,
                "counts_by_subject": summarize_counts(pass36_df),
                "selection_excluded_columns": pass36_selection_excluded,
                "subjects_audit": pass36_subjects_audit,
                "blocks": pass36_blocks,
            },
            "pass40": {
                "features_csv": str(pass40_features.resolve()),
                "report_path": str(pass40_report_path.resolve()),
                "subject_summary": pass40_report["models"]["logreg"]["subject_aggregation"]["summary"],
                "subjects_scores": {subject_id: float(pass40_subjects[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS},
                "subjects": pass40_subjects,
                "counts_by_subject": summarize_counts(pass40_df),
                "selection_excluded_columns": pass40_selection_excluded,
                "subjects_audit": pass40_subjects_audit,
                "blocks": pass40_blocks,
            },
        },
        "pass41": {
            "features_csv": str(pass41_features.resolve()),
            "report_path": str(pass41_report_path.resolve()),
            "subject_summary": pass41_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "subjects_scores": {subject_id: float(pass41_subjects[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS},
            "subjects": pass41_subjects,
            "counts_by_subject": summarize_counts(pass41_df),
            "selection_excluded_columns": pass41_selection_excluded,
            "feature_columns": pass41_feature_columns,
            "subjects_audit": pass41_subjects_audit,
            "blocks": pass41_blocks,
            "pairwise": pass41_pairwise,
        },
        "event_config": EVENT_CONFIG,
        "event_reference_by_subject": event_reference,
        "composition_summary": composition_summary,
        "warnings": warnings,
        "derived": {
            "subject_score_rows": build_subject_score_rows(
                pass36_subjects=pass36_subjects,
                pass40_subjects=pass40_subjects,
                pass41_subjects=pass41_subjects,
            ),
            "early_window_deltas": build_early_window_deltas(
                pass36_rows=pass36_subjects_audit["brux1"]["rows_by_time_rank"],
                pass40_rows=pass40_subjects_audit["brux1"]["rows_by_time_rank"],
                pass41_rows=pass41_subjects_audit["brux1"]["rows_by_time_rank"],
            ),
            "pass36_best_brux_minus_highest_control": best_brux_minus_highest_control(pass36_subjects),
            "pass40_best_brux_minus_highest_control": best_brux_minus_highest_control(pass40_subjects),
            "pass41_best_brux_minus_highest_control": best_brux_minus_highest_control(pass41_subjects),
            "brux1_minus_n3_pass41": float(pass41_subjects["brux1"]["mean_score"] - pass41_subjects["n3"]["mean_score"]),
            "n5_minus_brux1_pass41": float(pass41_subjects["n5"]["mean_score"] - pass41_subjects["brux1"]["mean_score"]),
            "n11_minus_brux1_pass41": float(pass41_subjects["n11"]["mean_score"] - pass41_subjects["brux1"]["mean_score"]),
        },
        "summary_md_path": str(summary_md_path.resolve()),
        "summary_json_path": str(summary_json_path.resolve()),
    }

    summary_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_markdown(report), encoding="utf-8")
    print(summary_md_path)
    print(summary_json_path)
    print(pass41_features)
    print(pass41_report_path)


if __name__ == "__main__":
    main()
