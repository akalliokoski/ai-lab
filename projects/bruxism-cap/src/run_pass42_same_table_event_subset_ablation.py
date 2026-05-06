from __future__ import annotations

import itertools
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from audit_percentile_band_channel_gap import select_feature_columns
from run_pass36_record_relative_shape_composition_audit import load_subjects, summarize_counts, validate_same_selected_rows
from run_pass41_event_conditioned_feature_block_audit import (
    BASE_EXCLUDE_REGEXES,
    EVENT_CONFIG,
    EVENT_FEATURES,
    ROW_ID_COLUMNS,
    SUBJECT_IDS,
    best_brux_minus_highest_control,
    build_pairwise,
    build_subject_rows,
)

PASS_NUMBER = 42
EXPERIMENT = "same_table_event_subset_ablation_on_pass41_table"
PRIMARY_OBJECTIVE = "preserve the small brux1 lift while pushing n11 back below threshold"
SUBSET_SIZE = 3
PASS36_BRUX1 = 0.112
SELECTION_PRIORITY = "maximize brux1 uplift among subsets that keep n11 < 0.5, then best-bruxism-minus-highest-control margin, then balanced accuracy"


PROJECT_PYTHON = Path(__file__).resolve().parents[3] / ".venv/bin/python"


def run_train_baseline(*, features_csv: Path, out_json: Path, exclude_patterns: list[str]) -> dict[str, Any]:
    python_exe = PROJECT_PYTHON if PROJECT_PYTHON.exists() else Path(sys.executable)
    cmd = [
        str(python_exe),
        str(Path(__file__).with_name("train_baseline.py")),
        "--features-csv",
        str(features_csv),
        "--cv",
        "loso",
        "--out",
        str(out_json),
    ]
    for pattern in exclude_patterns:
        cmd.extend(["--exclude-features-regex", pattern])
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    return json.loads(out_json.read_text(encoding="utf-8"))


def build_exclude_patterns(subset: list[str]) -> list[str]:
    excludes = list(BASE_EXCLUDE_REGEXES)
    for feature in EVENT_FEATURES:
        if feature not in subset:
            excludes.append(f"^{re.escape(feature)}$")
    return excludes


def get_subject_scores(subjects: dict[str, dict[str, Any]]) -> dict[str, float]:
    return {subject_id: float(subjects[subject_id]["mean_score"]) for subject_id in SUBJECT_IDS}


def evaluate_subset(pass41_df: pd.DataFrame, subset: list[str], out_json: Path) -> dict[str, Any]:
    exclude_patterns = build_exclude_patterns(subset)
    report = run_train_baseline(features_csv=PASS41_FEATURES, out_json=out_json, exclude_patterns=exclude_patterns)
    subjects = load_subjects(report)
    scores = get_subject_scores(subjects)
    subject_summary = report["models"]["logreg"]["subject_aggregation"]["summary"]
    return {
        "subset": subset,
        "exclude_patterns": exclude_patterns,
        "report": report,
        "subjects": subjects,
        "scores": scores,
        "subject_summary": subject_summary,
        "best_brux_minus_highest_control": best_brux_minus_highest_control(subjects),
        "brux1_lift_vs_pass36": float(scores["brux1"] - PASS36_BRUX1),
        "n11_below_threshold": bool(scores["n11"] < 0.5),
    }


def choose_best_subset(pass41_df: pd.DataFrame, reports_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    diagnostics: list[dict[str, Any]] = []
    for subset_tuple in itertools.combinations(EVENT_FEATURES, SUBSET_SIZE):
        subset = list(subset_tuple)
        tmp_out = reports_dir / f"_tmp_pass42_diag_{'_'.join(subset)}.json"
        result = evaluate_subset(pass41_df, subset, tmp_out)
        diagnostics.append(
            {
                "subset": subset,
                "subject_summary": result["subject_summary"],
                "scores": result["scores"],
                "best_brux_minus_highest_control": result["best_brux_minus_highest_control"],
                "brux1_lift_vs_pass36": result["brux1_lift_vs_pass36"],
                "n11_below_threshold": result["n11_below_threshold"],
            }
        )
        if tmp_out.exists():
            tmp_out.unlink()
    diagnostics.sort(
        key=lambda row: (
            row["n11_below_threshold"],
            row["brux1_lift_vs_pass36"],
            row["best_brux_minus_highest_control"],
            row["subject_summary"]["balanced_accuracy"],
        ),
        reverse=True,
    )
    chosen_subset = diagnostics[0]["subset"]
    final_out = reports_dir / "loso-cv-pass42-emg-a1-pct10-90-record-relative-shape-eventblock-subset.json"
    final = evaluate_subset(pass41_df, chosen_subset, final_out)
    final["report_path"] = final_out
    final["selection_diagnostics"] = diagnostics[:10]
    return final, diagnostics


def build_subject_score_rows(
    *,
    pass36_subjects: dict[str, Any],
    pass40_subjects: dict[str, Any],
    pass41_subjects: dict[str, Any],
    pass42_subjects: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for subject_id in SUBJECT_IDS:
        rows.append(
            {
                "subject_id": subject_id,
                "pass36_score": float(pass36_subjects[subject_id]["mean_score"]),
                "pass40_score": float(pass40_subjects[subject_id]["mean_score"]),
                "pass41_score": float(pass41_subjects[subject_id]["mean_score"]),
                "pass42_score": float(pass42_subjects[subject_id]["mean_score"]),
                "delta_vs_pass36": float(pass42_subjects[subject_id]["mean_score"] - pass36_subjects[subject_id]["mean_score"]),
                "delta_vs_pass40": float(pass42_subjects[subject_id]["mean_score"] - pass40_subjects[subject_id]["mean_score"]),
                "delta_vs_pass41": float(pass42_subjects[subject_id]["mean_score"] - pass41_subjects[subject_id]["mean_score"]),
                "pass36_predicted_label": pass36_subjects[subject_id]["predicted_label"],
                "pass41_predicted_label": pass41_subjects[subject_id]["predicted_label"],
                "pass42_predicted_label": pass42_subjects[subject_id]["predicted_label"],
            }
        )
    return rows


def render_subject_rows(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{row['subject_id']}`: pass36 `{row['pass36_score']:.3f}` -> pass40 `{row['pass40_score']:.3f}` -> pass41 `{row['pass41_score']:.3f}` -> pass42 `{row['pass42_score']:.3f}` | "
        f"delta vs pass36 `{row['delta_vs_pass36']:+.3f}` | delta vs pass40 `{row['delta_vs_pass40']:+.3f}` | delta vs pass41 `{row['delta_vs_pass41']:+.3f}` | "
        f"predicted pass36 `{row['pass36_predicted_label']}` -> pass41 `{row['pass41_predicted_label']}` -> pass42 `{row['pass42_predicted_label']}`"
        for row in rows
    )


def render_top_candidates(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{', '.join(row['subset'])}` | bal acc `{row['subject_summary']['balanced_accuracy']:.3f}` | specificity `{row['subject_summary']['specificity']:.3f}` | brux1 `{row['scores']['brux1']:.3f}` | n11 `{row['scores']['n11']:.3f}` | margin `{row['best_brux_minus_highest_control']:+.3f}`"
        for row in rows
    )


def render_feature_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- none"
    return "\n".join(
        f"- `{row['feature']}` contribution delta `{row['mean_contribution_delta']:+.3f}` | z-mean delta `{row['z_mean_delta']:+.3f}` | raw-mean delta `{row['raw_mean_delta']:+.6f}`"
        for row in rows
    )


def render_markdown(report: dict[str, Any]) -> str:
    pass36_summary = report["anchors"]["pass36"]["subject_summary"]
    pass40_summary = report["anchors"]["pass40"]["subject_summary"]
    pass41_summary = report["anchors"]["pass41"]["subject_summary"]
    pass42_summary = report["pass42"]["subject_summary"]
    pair_n5 = report["pass42"]["pairwise"]["n5_minus_brux1"]
    pair_n11 = report["pass42"]["pairwise"]["n11_minus_brux1"]
    verdict = (
        "Yes: the chosen subset keeps the pass41 brux1 lift directionally alive while moving n11 back below threshold and restoring the pass36/pass40 subject-level surface."
        if report["derived"]["brux1_lift_survives_and_n11_repaired"]
        else "No: the chosen subset does not preserve the desired brux1-vs-n11 trade-off, so the pass41 event idea still needs a narrower reformulation."
    )
    next_step = (
        "Keep the same pass42 subset fixed and compare the exact same subset on matched A1-only vs A3-only EMG tables before changing model family."
        if report["derived"]["brux1_lift_survives_and_n11_repaired"]
        else "Keep the same pass41 table fixed and test one count-only or spacing-only subset that removes active-fraction/duration coupling, rather than broadening the feature family."
    )
    return f"""# Pass 42 — same-table event-subset ablation on the pass41 table

Date: 2026-05-05
Status: bounded same-table ablation completed. This pass reuses the already-generated pass41 feature table, keeps the repaired five-subject `SLEEP-S2 + MCAP-A1-only` `EMG1-EMG2` percentile-band scaffold and `logreg` LOSO contract fixed, and tests exactly one chosen 3-feature event subset instead of the full 7-feature pass41 block.

## Exact subset used
- `{', '.join(report['pass42']['selected_event_subset'])}`

## Exact implementation path
- input table reused directly: `projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv`
- no selector rerun, no new feature invention, no channel pivot, no benchmark-contract change
- subset selection rule: {SELECTION_PRIORITY}
- subset-selection diagnostic sweep size: `{report['selection']['diagnostic_subset_count']}` choose-3 combinations from the existing 7 pass41 event features
- train-time feature removal for this pass: drop the four pass41 event features not in the chosen subset via `train_baseline.py --exclude-features-regex`, while keeping the pass36 backbone and base exclusion list unchanged

Top same-table subset candidates:
{render_top_candidates(report['selection']['top_candidates'])}

## Artifacts
- Runner script: `projects/bruxism-cap/src/run_pass42_same_table_event_subset_ablation.py`
- Reused pass41 feature table: `projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv`
- Pass42 LOSO report: `projects/bruxism-cap/reports/loso-cv-pass42-emg-a1-pct10-90-record-relative-shape-eventblock-subset.json`
- Pass42 summary JSON: `projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.json`
- Pass42 summary report: `projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.md`

## Scaffold parity checks
- pass36 counts: `{report['anchors']['pass36']['counts_by_subject']}`
- pass40 counts: `{report['anchors']['pass40']['counts_by_subject']}`
- pass41 counts: `{report['anchors']['pass41']['counts_by_subject']}`
- pass42 counts: `{report['pass42']['counts_by_subject']}`
- row-alignment warnings: `{report['warnings']}`
- unchanged base train-time exclusions: `{BASE_EXCLUDE_REGEXES}`
- additional pass42 dropped event features: `{report['pass42']['dropped_event_features']}`

## Apples-to-apples subject-level comparison against pass36, pass40, and pass41
- pass36 balanced accuracy: `{pass36_summary['balanced_accuracy']:.3f}`
- pass40 balanced accuracy: `{pass40_summary['balanced_accuracy']:.3f}`
- pass41 balanced accuracy: `{pass41_summary['balanced_accuracy']:.3f}`
- pass42 balanced accuracy: `{pass42_summary['balanced_accuracy']:.3f}`
- pass36 sensitivity: `{pass36_summary['sensitivity']:.3f}`
- pass40 sensitivity: `{pass40_summary['sensitivity']:.3f}`
- pass41 sensitivity: `{pass41_summary['sensitivity']:.3f}`
- pass42 sensitivity: `{pass42_summary['sensitivity']:.3f}`
- pass36 specificity: `{pass36_summary['specificity']:.3f}`
- pass40 specificity: `{pass40_summary['specificity']:.3f}`
- pass41 specificity: `{pass41_summary['specificity']:.3f}`
- pass42 specificity: `{pass42_summary['specificity']:.3f}`
- pass36 best-bruxism-minus-highest-control margin: `{report['derived']['pass36_best_brux_minus_highest_control']:+.3f}`
- pass40 best-bruxism-minus-highest-control margin: `{report['derived']['pass40_best_brux_minus_highest_control']:+.3f}`
- pass41 best-bruxism-minus-highest-control margin: `{report['derived']['pass41_best_brux_minus_highest_control']:+.3f}`
- pass42 best-bruxism-minus-highest-control margin: `{report['derived']['pass42_best_brux_minus_highest_control']:+.3f}`

Subject score deltas:
{render_subject_rows(report['derived']['subject_score_rows'])}

## Did the brux1 lift survive while n11 fell back below threshold?
- `brux1`: pass36 `{report['anchors']['pass36']['subjects_scores']['brux1']:.3f}` -> pass41 `{report['anchors']['pass41']['subjects_scores']['brux1']:.3f}` -> pass42 `{report['pass42']['subjects_scores']['brux1']:.3f}`
- `n11`: pass36 `{report['anchors']['pass36']['subjects_scores']['n11']:.3f}` -> pass41 `{report['anchors']['pass41']['subjects_scores']['n11']:.3f}` -> pass42 `{report['pass42']['subjects_scores']['n11']:.3f}`
- `n5`: pass36 `{report['anchors']['pass36']['subjects_scores']['n5']:.3f}` -> pass41 `{report['anchors']['pass41']['subjects_scores']['n5']:.3f}` -> pass42 `{report['pass42']['subjects_scores']['n5']:.3f}`
- `n3`: pass36 `{report['anchors']['pass36']['subjects_scores']['n3']:.3f}` -> pass41 `{report['anchors']['pass41']['subjects_scores']['n3']:.3f}` -> pass42 `{report['pass42']['subjects_scores']['n3']:.3f}`
- pass42 `brux1 - n3`: `{report['derived']['brux1_minus_n3_pass42']:+.3f}`
- pass42 `n5 - brux1`: `{report['derived']['n5_minus_brux1_pass42']:+.3f}`
- pass42 `n11 - brux1`: `{report['derived']['n11_minus_brux1_pass42']:+.3f}`
- verdict: {verdict}

## Event-feature deltas against brux1 for the chosen subset pass
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

## Safest next bounded step
{next_step}
"""


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    reports_dir = root / "reports"

    pass36_features = root / "data/window_features_pass36_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape.csv"
    pass40_features = root / "data/window_features_pass40_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_envcv_rectstd_floor.csv"
    pass41_report_path = reports_dir / "loso-cv-pass41-emg-a1-pct10-90-record-relative-shape-eventblock.json"
    pass36_report_path = reports_dir / "loso-cv-pass36-emg-a1-pct10-90-record-relative-shape.json"
    pass40_report_path = reports_dir / "loso-cv-pass40-emg-a1-pct10-90-record-relative-shape-envcv-rectstd-floor.json"
    summary_json_path = reports_dir / "pass42-same-table-event-subset-ablation.json"
    summary_md_path = reports_dir / "pass42-same-table-event-subset-ablation.md"

    pass36_df = pd.read_csv(pass36_features)
    pass40_df = pd.read_csv(pass40_features)
    pass41_df = pd.read_csv(PASS41_FEATURES)
    pass36_report = json.loads(pass36_report_path.read_text(encoding="utf-8"))
    pass40_report = json.loads(pass40_report_path.read_text(encoding="utf-8"))
    pass41_report = json.loads(pass41_report_path.read_text(encoding="utf-8"))

    warnings = []
    warnings.extend(validate_same_selected_rows(left_df=pass36_df, right_df=pass41_df, label="pass41 table vs pass36"))
    warnings.extend(validate_same_selected_rows(left_df=pass40_df, right_df=pass41_df, label="pass41 table vs pass40"))

    final, diagnostics = choose_best_subset(pass41_df, reports_dir)
    chosen_subset = final["subset"]
    exclude_patterns = final["exclude_patterns"]
    pass42_report = final["report"]
    pass42_subjects = final["subjects"]

    pass36_subjects = load_subjects(pass36_report)
    pass40_subjects = load_subjects(pass40_report)
    pass41_subjects = load_subjects(pass41_report)

    pass36_feature_columns, pass36_selection_excluded = select_feature_columns(pass36_df, exclude_patterns=BASE_EXCLUDE_REGEXES)
    pass40_feature_columns, pass40_selection_excluded = select_feature_columns(pass40_df, exclude_patterns=BASE_EXCLUDE_REGEXES)
    pass41_feature_columns, pass41_selection_excluded = select_feature_columns(pass41_df, exclude_patterns=BASE_EXCLUDE_REGEXES)
    pass42_feature_columns, pass42_selection_excluded = select_feature_columns(pass41_df, exclude_patterns=exclude_patterns)

    pass36_subjects_audit, pass36_blocks = build_subject_rows(pass36_df, pass36_feature_columns)
    pass40_subjects_audit, pass40_blocks = build_subject_rows(pass40_df, pass40_feature_columns)
    pass41_subjects_audit, pass41_blocks = build_subject_rows(pass41_df, pass41_feature_columns)
    pass42_subjects_audit, pass42_blocks = build_subject_rows(pass41_df, pass42_feature_columns)
    pass42_pairwise = build_pairwise(pass42_subjects_audit, pass42_feature_columns, pass42_blocks)

    report = {
        "pass": PASS_NUMBER,
        "experiment": EXPERIMENT,
        "objective": PRIMARY_OBJECTIVE,
        "anchors": {
            "pass36": {
                "features_csv": str(pass36_features.resolve()),
                "report_path": str(pass36_report_path.resolve()),
                "subject_summary": pass36_report["models"]["logreg"]["subject_aggregation"]["summary"],
                "subjects_scores": get_subject_scores(pass36_subjects),
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
                "subjects_scores": get_subject_scores(pass40_subjects),
                "subjects": pass40_subjects,
                "counts_by_subject": summarize_counts(pass40_df),
                "selection_excluded_columns": pass40_selection_excluded,
                "subjects_audit": pass40_subjects_audit,
                "blocks": pass40_blocks,
            },
            "pass41": {
                "features_csv": str(PASS41_FEATURES.resolve()),
                "report_path": str(pass41_report_path.resolve()),
                "subject_summary": pass41_report["models"]["logreg"]["subject_aggregation"]["summary"],
                "subjects_scores": get_subject_scores(pass41_subjects),
                "subjects": pass41_subjects,
                "counts_by_subject": summarize_counts(pass41_df),
                "selection_excluded_columns": pass41_selection_excluded,
                "subjects_audit": pass41_subjects_audit,
                "blocks": pass41_blocks,
            },
        },
        "selection": {
            "subset_size": SUBSET_SIZE,
            "selection_priority": SELECTION_PRIORITY,
            "diagnostic_subset_count": len(diagnostics),
            "top_candidates": diagnostics[:5],
        },
        "pass42": {
            "features_csv": str(PASS41_FEATURES.resolve()),
            "report_path": str(final['report_path'].resolve()),
            "subject_summary": pass42_report["models"]["logreg"]["subject_aggregation"]["summary"],
            "subjects_scores": get_subject_scores(pass42_subjects),
            "subjects": pass42_subjects,
            "counts_by_subject": summarize_counts(pass41_df),
            "selection_excluded_columns": pass42_selection_excluded,
            "feature_columns": pass42_feature_columns,
            "subjects_audit": pass42_subjects_audit,
            "blocks": pass42_blocks,
            "pairwise": pass42_pairwise,
            "selected_event_subset": chosen_subset,
            "dropped_event_features": [feature for feature in EVENT_FEATURES if feature not in chosen_subset],
            "exclude_patterns": exclude_patterns,
        },
        "event_config": EVENT_CONFIG,
        "warnings": warnings,
        "derived": {
            "subject_score_rows": build_subject_score_rows(
                pass36_subjects=pass36_subjects,
                pass40_subjects=pass40_subjects,
                pass41_subjects=pass41_subjects,
                pass42_subjects=pass42_subjects,
            ),
            "pass36_best_brux_minus_highest_control": best_brux_minus_highest_control(pass36_subjects),
            "pass40_best_brux_minus_highest_control": best_brux_minus_highest_control(pass40_subjects),
            "pass41_best_brux_minus_highest_control": best_brux_minus_highest_control(pass41_subjects),
            "pass42_best_brux_minus_highest_control": best_brux_minus_highest_control(pass42_subjects),
            "brux1_minus_n3_pass42": float(pass42_subjects["brux1"]["mean_score"] - pass42_subjects["n3"]["mean_score"]),
            "n5_minus_brux1_pass42": float(pass42_subjects["n5"]["mean_score"] - pass42_subjects["brux1"]["mean_score"]),
            "n11_minus_brux1_pass42": float(pass42_subjects["n11"]["mean_score"] - pass42_subjects["brux1"]["mean_score"]),
            "brux1_lift_survives_and_n11_repaired": bool(pass42_subjects["brux1"]["mean_score"] > pass41_subjects["brux1"]["mean_score"] and pass42_subjects["n11"]["mean_score"] < 0.5),
        },
        "summary_md_path": str(summary_md_path.resolve()),
        "summary_json_path": str(summary_json_path.resolve()),
    }

    summary_json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_md_path.write_text(render_markdown(report), encoding="utf-8")
    print(summary_md_path)
    print(summary_json_path)
    print(final['report_path'])


PASS41_FEATURES = Path(__file__).resolve().parents[1] / "data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv"


if __name__ == "__main__":
    main()
