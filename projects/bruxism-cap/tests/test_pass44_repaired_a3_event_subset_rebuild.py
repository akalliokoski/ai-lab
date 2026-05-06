from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from run_pass44_repaired_a3_event_subset_rebuild import (  # noqa: E402
    PASS42_EVENT_SUBSET,
    build_exclude_patterns,
    build_pass44_repaired_a3_table,
)


def test_build_exclude_patterns_keeps_base_contract_and_drops_unused_event_terms():
    patterns = build_exclude_patterns()

    assert patterns[:3] == [r"^bp_", r"^rel_bp_", r"^ratio_"]
    assert r"^evt_burst_count_30s$" in patterns
    assert r"^evt_episode_count_30s$" in patterns
    assert r"^evt_bursts_per_episode_mean$" in patterns
    assert r"^evt_phasic_like_episode_fraction$" in patterns
    for feature in PASS42_EVENT_SUBSET:
        assert f"^{feature}$" not in patterns


def test_build_pass44_repaired_a3_table_applies_record_relative_transform_and_merges_fixed_event_subset():
    selected_a3_df = pd.DataFrame(
        [
            {
                "subject_id": "brux1",
                "window_index": 11,
                "start_s": 10.0,
                "end_s": 40.0,
                "time_match_rank": 1,
                "relative_time_quantile": 0.25,
                "label": "bruxism",
                "channel": "EMG1-EMG2",
                "source_file": "brux1.edf",
                "mean": 10.0,
                "max": 20.0,
                "ptp": 30.0,
                "line_length": 40.0,
                "zero_crossing_rate": 50.0,
                "rectified_std": 60.0,
                "envelope_std": 70.0,
                "envelope_cv": 80.0,
                "rectified_mean": 90.0,
                "envelope_mean": 100.0,
                "p95_abs": 110.0,
                "skewness": 0.1,
                "kurtosis": 3.1,
                "hjorth_mobility": 1.1,
                "hjorth_complexity": 2.1,
            },
            {
                "subject_id": "brux1",
                "window_index": 12,
                "start_s": 40.0,
                "end_s": 70.0,
                "time_match_rank": 2,
                "relative_time_quantile": 0.75,
                "label": "bruxism",
                "channel": "EMG1-EMG2",
                "source_file": "brux1.edf",
                "mean": 14.0,
                "max": 24.0,
                "ptp": 34.0,
                "line_length": 44.0,
                "zero_crossing_rate": 54.0,
                "rectified_std": 64.0,
                "envelope_std": 74.0,
                "envelope_cv": 84.0,
                "rectified_mean": 94.0,
                "envelope_mean": 104.0,
                "p95_abs": 114.0,
                "skewness": 0.2,
                "kurtosis": 3.2,
                "hjorth_mobility": 1.2,
                "hjorth_complexity": 2.2,
            },
            {
                "subject_id": "n3",
                "window_index": 21,
                "start_s": 15.0,
                "end_s": 45.0,
                "time_match_rank": 1,
                "relative_time_quantile": 0.25,
                "label": "control",
                "channel": "EMG1-EMG2",
                "source_file": "n3.edf",
                "mean": 20.0,
                "max": 30.0,
                "ptp": 40.0,
                "line_length": 50.0,
                "zero_crossing_rate": 60.0,
                "rectified_std": 70.0,
                "envelope_std": 80.0,
                "envelope_cv": 90.0,
                "rectified_mean": 100.0,
                "envelope_mean": 110.0,
                "p95_abs": 120.0,
                "skewness": -0.1,
                "kurtosis": 2.9,
                "hjorth_mobility": 0.9,
                "hjorth_complexity": 1.9,
            },
            {
                "subject_id": "n3",
                "window_index": 22,
                "start_s": 45.0,
                "end_s": 75.0,
                "time_match_rank": 2,
                "relative_time_quantile": 0.75,
                "label": "control",
                "channel": "EMG1-EMG2",
                "source_file": "n3.edf",
                "mean": 24.0,
                "max": 34.0,
                "ptp": 44.0,
                "line_length": 54.0,
                "zero_crossing_rate": 64.0,
                "rectified_std": 74.0,
                "envelope_std": 84.0,
                "envelope_cv": 94.0,
                "rectified_mean": 104.0,
                "envelope_mean": 114.0,
                "p95_abs": 124.0,
                "skewness": -0.2,
                "kurtosis": 2.8,
                "hjorth_mobility": 0.8,
                "hjorth_complexity": 1.8,
            },
        ]
    )
    event_df = pd.DataFrame(
        [
            {
                "subject_id": "brux1",
                "window_index": 11,
                "start_s": 10.0,
                "end_s": 40.0,
                "evt_active_fraction": 0.11,
                "evt_burst_duration_median_s": 1.1,
                "evt_interburst_gap_median_s": 2.1,
            },
            {
                "subject_id": "brux1",
                "window_index": 12,
                "start_s": 40.0,
                "end_s": 70.0,
                "evt_active_fraction": 0.12,
                "evt_burst_duration_median_s": 1.2,
                "evt_interburst_gap_median_s": 2.2,
            },
            {
                "subject_id": "n3",
                "window_index": 21,
                "start_s": 15.0,
                "end_s": 45.0,
                "evt_active_fraction": 0.21,
                "evt_burst_duration_median_s": 1.3,
                "evt_interburst_gap_median_s": 2.3,
            },
            {
                "subject_id": "n3",
                "window_index": 22,
                "start_s": 45.0,
                "end_s": 75.0,
                "evt_active_fraction": 0.22,
                "evt_burst_duration_median_s": 1.4,
                "evt_interburst_gap_median_s": 2.4,
            },
        ]
    )

    rebuilt_df, summary = build_pass44_repaired_a3_table(selected_a3_df=selected_a3_df, event_df=event_df)

    assert len(rebuilt_df) == 4
    assert rebuilt_df["time_match_rank"].tolist() == [1, 2, 1, 2]
    assert rebuilt_df["relative_time_quantile"].tolist() == [0.25, 0.75, 0.25, 0.75]

    brux1_mean_values = rebuilt_df.loc[rebuilt_df["subject_id"] == "brux1", "mean"].tolist()
    n3_mean_values = rebuilt_df.loc[rebuilt_df["subject_id"] == "n3", "mean"].tolist()
    assert brux1_mean_values == [-1.0, 1.0]
    assert n3_mean_values == [-1.0, 1.0]

    assert rebuilt_df.loc[rebuilt_df["window_index"] == 11, "skewness"].item() == 0.1
    assert rebuilt_df.loc[rebuilt_df["window_index"] == 22, "hjorth_complexity"].item() == 1.8

    assert rebuilt_df.loc[rebuilt_df["window_index"] == 11, "evt_active_fraction"].item() == 0.11
    assert rebuilt_df.loc[rebuilt_df["window_index"] == 22, "evt_burst_duration_median_s"].item() == 1.4

    assert summary["event_null_counts_after_merge"] == {
        "evt_active_fraction": 0,
        "evt_burst_duration_median_s": 0,
        "evt_interburst_gap_median_s": 0,
    }
    assert summary["record_relative"]["relative_features_applied"]
    assert summary["appended_event_subset"] == PASS42_EVENT_SUBSET
