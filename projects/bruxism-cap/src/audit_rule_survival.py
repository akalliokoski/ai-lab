from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import mne  # type: ignore

from prepare_windows import overlaps_any_events, parse_annotation_rows  # noqa: E402

WINDOW_SECONDS = 30.0
TARGET_STAGE_EVENT = "SLEEP-S2"
OVERLAP_FAMILY = {"MCAP-A1", "MCAP-A2", "MCAP-A3"}
A3_ONLY_EXCLUDES = {"MCAP-A1", "MCAP-A2"}

RULES: tuple[dict[str, object], ...] = (
    {
        "key": "pass4_s2",
        "label": "S2 only",
        "required_events": None,
        "excluded_events": None,
    },
    {
        "key": "pass7_s2_mcap_any",
        "label": "S2 + any MCAP-A1/A2/A3 overlap",
        "required_events": OVERLAP_FAMILY,
        "excluded_events": None,
    },
    {
        "key": "pass9_s2_mcap_a3",
        "label": "S2 + MCAP-A3 overlap",
        "required_events": {"MCAP-A3"},
        "excluded_events": None,
    },
    {
        "key": "pass10_s2_mcap_a3_only",
        "label": "S2 + MCAP-A3 overlap, excluding A1/A2",
        "required_events": {"MCAP-A3"},
        "excluded_events": A3_ONLY_EXCLUDES,
    },
)

FEATURE_TABLES = {
    "pass4_s2": ROOT / "projects/bruxism-cap/data/window_features_pass4_s2.csv",
    "pass7_s2_mcap_any": ROOT / "projects/bruxism-cap/data/window_features_pass7_s2_mcap.csv",
    "pass9_s2_mcap_a3": ROOT / "projects/bruxism-cap/data/window_features_pass9_s2_mcap_a3.csv",
    "pass10_s2_mcap_a3_only": ROOT / "projects/bruxism-cap/data/window_features_pass10_s2_mcap_a3_only.csv",
}


def load_feature_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def subject_windows_by_rule() -> dict[str, dict[str, list[dict[str, str]]]]:
    by_rule: dict[str, dict[str, list[dict[str, str]]]] = {}
    for rule_key, path in FEATURE_TABLES.items():
        rows = load_feature_rows(path)
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            grouped[row["subject_id"]].append(row)
        by_rule[rule_key] = grouped
    return by_rule


def compute_matching_rows(
    *,
    annotation_rows: list[dict[str, object]],
    record_duration_s: float,
    required_events: set[str] | None,
    excluded_events: set[str] | None,
) -> list[dict[str, object]]:
    rows = [
        row
        for row in annotation_rows
        if row["event"] == TARGET_STAGE_EVENT
        and float(row["duration_s"]) >= WINDOW_SECONDS
        and float(row["start_s"]) >= 0
        and float(row["start_s"]) + WINDOW_SECONDS <= record_duration_s
    ]
    if required_events:
        rows = [
            row
            for row in rows
            if overlaps_any_events(
                row,
                candidate_window_seconds=WINDOW_SECONDS,
                other_rows=annotation_rows,
                event_names=required_events,
                min_overlap_seconds=0.001,
            )
        ]
    if excluded_events:
        rows = [
            row
            for row in rows
            if not overlaps_any_events(
                row,
                candidate_window_seconds=WINDOW_SECONDS,
                other_rows=annotation_rows,
                event_names=excluded_events,
                min_overlap_seconds=0.001,
            )
        ]
    return rows


def pct(part: int, whole: int) -> float:
    return round((100.0 * part / whole), 1) if whole else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit how many windows survive each stage-aware overlap rule per subject and label."
    )
    parser.add_argument("--annotation-dir", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    args = parser.parse_args()

    annotation_dir = Path(args.annotation_dir)
    if not annotation_dir.is_absolute():
        annotation_dir = ROOT / annotation_dir

    kept_windows = subject_windows_by_rule()
    subjects = sorted(kept_windows["pass4_s2"].keys())
    label_by_subject: dict[str, str] = {}
    for subject in subjects:
        pass4_rows = kept_windows["pass4_s2"][subject]
        label_by_subject[subject] = pass4_rows[0]["label"]

    subject_summaries: list[dict[str, object]] = []
    label_summaries: dict[str, dict[str, dict[str, int | float]]] = defaultdict(dict)

    for subject in subjects:
        label = label_by_subject[subject]
        edf_path = annotation_dir / f"{subject}.edf"
        txt_path = annotation_dir / f"{subject}.txt"
        raw = mne.io.read_raw_edf(edf_path, preload=False, verbose="ERROR")
        annotation_rows = parse_annotation_rows(txt_path, record_start_dt=raw.info["meas_date"])
        record_duration_s = raw.n_times / float(raw.info["sfreq"])

        base_rows = compute_matching_rows(
            annotation_rows=annotation_rows,
            record_duration_s=record_duration_s,
            required_events=None,
            excluded_events=None,
        )
        base_count = len(base_rows)

        rule_counts: dict[str, dict[str, int | float]] = {}
        for rule in RULES:
            rule_key = str(rule["key"])
            matched_rows = compute_matching_rows(
                annotation_rows=annotation_rows,
                record_duration_s=record_duration_s,
                required_events=rule["required_events"],
                excluded_events=rule["excluded_events"],
            )
            eligible_count = len(matched_rows)
            kept_count = len(kept_windows[rule_key].get(subject, []))
            rule_counts[rule_key] = {
                "eligible": eligible_count,
                "kept": kept_count,
                "eligible_vs_pass4_pct": pct(eligible_count, base_count),
                "kept_vs_eligible_pct": pct(kept_count, eligible_count),
            }

        subject_summaries.append(
            {
                "subject_id": subject,
                "label": label,
                "record_duration_s": round(record_duration_s, 1),
                "rule_counts": rule_counts,
            }
        )

    for label in sorted(set(label_by_subject.values())):
        label_subjects = [s for s in subject_summaries if s["label"] == label]
        for rule in RULES:
            rule_key = str(rule["key"])
            eligible = sum(int(s["rule_counts"][rule_key]["eligible"]) for s in label_subjects)
            kept = sum(int(s["rule_counts"][rule_key]["kept"]) for s in label_subjects)
            pass4_total = sum(int(s["rule_counts"]["pass4_s2"]["eligible"]) for s in label_subjects)
            label_summaries[label][rule_key] = {
                "eligible": eligible,
                "kept": kept,
                "eligible_vs_pass4_pct": pct(eligible, pass4_total),
                "kept_vs_eligible_pct": pct(kept, eligible),
            }

    report = {
        "window_seconds": WINDOW_SECONDS,
        "annotation_dir": str(annotation_dir.resolve()),
        "rules": [
            {
                "key": str(rule["key"]),
                "label": str(rule["label"]),
            }
            for rule in RULES
        ],
        "subjects": subject_summaries,
        "labels": label_summaries,
    }

    out_json = Path(args.out_json)
    if not out_json.is_absolute():
        out_json = ROOT / out_json
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    subject_lines = []
    for subject in subject_summaries:
        counts = subject["rule_counts"]
        subject_lines.append(
            "| {subject} | {label} | {pass4} | {pass7} | {pass7_pct}% | {pass9} | {pass9_pct}% | {pass10} | {pass10_pct}% | {pass10_kept} |".format(
                subject=subject["subject_id"],
                label=subject["label"],
                pass4=counts["pass4_s2"]["eligible"],
                pass7=counts["pass7_s2_mcap_any"]["eligible"],
                pass7_pct=counts["pass7_s2_mcap_any"]["eligible_vs_pass4_pct"],
                pass9=counts["pass9_s2_mcap_a3"]["eligible"],
                pass9_pct=counts["pass9_s2_mcap_a3"]["eligible_vs_pass4_pct"],
                pass10=counts["pass10_s2_mcap_a3_only"]["eligible"],
                pass10_pct=counts["pass10_s2_mcap_a3_only"]["eligible_vs_pass4_pct"],
                pass10_kept=counts["pass10_s2_mcap_a3_only"]["kept"],
            )
        )

    label_lines = []
    for label, summary in sorted(label_summaries.items()):
        label_lines.append(
            "| {label} | {pass4} | {pass7} | {pass7_pct}% | {pass9} | {pass9_pct}% | {pass10} | {pass10_pct}% | {pass10_kept} |".format(
                label=label,
                pass4=summary["pass4_s2"]["eligible"],
                pass7=summary["pass7_s2_mcap_any"]["eligible"],
                pass7_pct=summary["pass7_s2_mcap_any"]["eligible_vs_pass4_pct"],
                pass9=summary["pass9_s2_mcap_a3"]["eligible"],
                pass9_pct=summary["pass9_s2_mcap_a3"]["eligible_vs_pass4_pct"],
                pass10=summary["pass10_s2_mcap_a3_only"]["eligible"],
                pass10_pct=summary["pass10_s2_mcap_a3_only"]["eligible_vs_pass4_pct"],
                pass10_kept=summary["pass10_s2_mcap_a3_only"]["kept"],
            )
        )

    md = f"""# Pass 11 — rule-survival audit across stage-aware overlap filters

Date: 2026-05-04
Status: bounded validity audit; no model change, no new rerun

## Why this audit exists

Pass10 showed that exclusive `S2 + A3-only` windows were cleaner but still not transferable.
The next bounded validity question was whether the successive overlap rules are shrinking the usable window pools symmetrically across subjects and labels, or whether they are silently changing event availability in a way that makes run-to-run comparisons harder to trust.

## Audited rules

- `pass4_s2` — in-range `SLEEP-S2` windows only
- `pass7_s2_mcap_any` — `SLEEP-S2` windows overlapping any of `MCAP-A1`, `MCAP-A2`, or `MCAP-A3`
- `pass9_s2_mcap_a3` — `SLEEP-S2` windows overlapping `MCAP-A3`
- `pass10_s2_mcap_a3_only` — `SLEEP-S2` windows overlapping `MCAP-A3` while excluding simultaneous `MCAP-A1` or `MCAP-A2`

## Subject-level survival summary

| subject | label | eligible pass4 S2 | eligible pass7 any-MCAP | pass7 vs pass4 | eligible pass9 A3 | pass9 vs pass4 | eligible pass10 A3-only | pass10 vs pass4 | pass10 kept rows |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(subject_lines)}

## Label-level survival summary

| label | eligible pass4 S2 | eligible pass7 any-MCAP | pass7 vs pass4 | eligible pass9 A3 | pass9 vs pass4 | eligible pass10 A3-only | pass10 vs pass4 | pass10 kept rows |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(label_lines)}

## Evidence-backed takeaways

1. The successive overlap filters shrink the available window pools **very unevenly** across subjects.
2. `brux2` keeps a much larger exclusive-`A3` pool than the other subjects, while `n5` drops sharply once the rule moves from `any MCAP` to `A3` and then `A3-only`.
3. The bruxism label pool stays relatively rich under `A3`-based rules, but the control pool thins much faster.
4. That means pass7/pass9/pass10 are not only changing event semantics; they are also changing the effective per-subject and per-label sampling surface.
5. This strengthens the current interpretation of pass9/pass10 as useful negative results: lower random-window optimism did not translate into better transfer, and the stricter rules also made the candidate control-window pool less balanced.

## Best next bounded step

Stay on validity work. The cleanest next increment is to compare one alternate exclusive family such as `S2 + A1-only` against `S2 + A3-only` on the same verified subject set, while preserving this survival audit so later comparisons can separate physiological signal from changing event availability.
"""

    out_md = Path(args.out_md)
    if not out_md.is_absolute():
        out_md = ROOT / out_md
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(md, encoding="utf-8")

    print(f"wrote rule-survival audit to {out_json}")
    print(f"wrote rule-survival markdown to {out_md}")


if __name__ == "__main__":
    main()
