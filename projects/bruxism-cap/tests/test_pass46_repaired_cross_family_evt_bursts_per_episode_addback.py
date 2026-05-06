from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from run_pass44_repaired_a3_event_subset_rebuild import PASS42_EVENT_SUBSET, ROW_ID_COLUMNS  # noqa: E402
from run_pass45_repaired_a3_shape_block_ablation import SHAPE_FEATURES  # noqa: E402
from run_pass46_repaired_cross_family_evt_bursts_per_episode_addback import (  # noqa: E402
    ADD_BACK_FEATURE,
    build_exclude_patterns,
    build_pass46_table,
)


def test_build_exclude_patterns_keeps_pass45_shape_drop_and_restores_only_one_event_feature():
    patterns = build_exclude_patterns()

    assert patterns[:3] == [r"^bp_", r"^rel_bp_", r"^ratio_"]
    for feature in SHAPE_FEATURES:
        assert f"^{feature}$" in patterns
    for feature in PASS42_EVENT_SUBSET:
        assert f"^{feature}$" not in patterns
    assert f"^{ADD_BACK_FEATURE}$" not in patterns
    assert r"^evt_burst_count_30s$" in patterns
    assert r"^evt_episode_count_30s$" in patterns
    assert r"^evt_phasic_like_episode_fraction$" in patterns


def test_build_pass46_table_merges_only_evt_bursts_per_episode_mean_without_changing_frozen_rows():
    frozen_df = pd.DataFrame(
        [
            {
                "subject_id": "brux1",
                "start_s": 10.0,
                "end_s": 40.0,
                "window_index": 11,
                "label": "bruxism",
                "skewness": 0.1,
                "evt_active_fraction": 0.11,
                "evt_burst_duration_median_s": 1.1,
                "evt_interburst_gap_median_s": 2.1,
            },
            {
                "subject_id": "n3",
                "start_s": 50.0,
                "end_s": 80.0,
                "window_index": 21,
                "label": "control",
                "skewness": -0.2,
                "evt_active_fraction": 0.22,
                "evt_burst_duration_median_s": 1.2,
                "evt_interburst_gap_median_s": 2.2,
            },
        ]
    )
    event_df = pd.DataFrame(
        [
            {
                "subject_id": "brux1",
                "start_s": 10.0,
                "end_s": 40.0,
                "window_index": 11,
                "evt_burst_count_30s": 3.0,
                "evt_episode_count_30s": 2.0,
                "evt_bursts_per_episode_mean": 1.5,
            },
            {
                "subject_id": "n3",
                "start_s": 50.0,
                "end_s": 80.0,
                "window_index": 21,
                "evt_burst_count_30s": 1.0,
                "evt_episode_count_30s": 1.0,
                "evt_bursts_per_episode_mean": 1.0,
            },
        ]
    )

    merged_df, summary = build_pass46_table(frozen_pass44_df=frozen_df, event_df=event_df)

    assert merged_df[ROW_ID_COLUMNS].to_dict(orient="records") == frozen_df[ROW_ID_COLUMNS].to_dict(orient="records")
    assert list(merged_df.columns).count(ADD_BACK_FEATURE) == 1
    assert merged_df.loc[merged_df["subject_id"] == "brux1", ADD_BACK_FEATURE].item() == 1.5
    assert merged_df.loc[merged_df["subject_id"] == "n3", ADD_BACK_FEATURE].item() == 1.0
    assert merged_df.loc[merged_df["subject_id"] == "brux1", "evt_active_fraction"].item() == 0.11
    assert merged_df.loc[merged_df["subject_id"] == "n3", "skewness"].item() == -0.2
    assert summary == {
        "merge_keys": ROW_ID_COLUMNS,
        "added_event_feature": ADD_BACK_FEATURE,
        "event_null_count_after_merge": 0,
        "same_row_ids_preserved": True,
    }
