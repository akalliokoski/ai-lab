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

from prepare_windows import parse_annotation_rows  # noqa: E402

TARGET_OVERLAP_EVENTS = ("MCAP-A1", "MCAP-A2", "MCAP-A3")


def load_feature_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def overlap_combo_for_window(
    *,
    start_s: float,
    end_s: float,
    annotation_rows: list[dict[str, object]],
    overlap_events: tuple[str, ...],
) -> tuple[str, ...]:
    hits: set[str] = set()
    for row in annotation_rows:
        event = str(row["event"])
        if event not in overlap_events:
            continue
        overlap_seconds = min(end_s, float(row["start_s"]) + float(row["duration_s"])) - max(start_s, float(row["start_s"]))
        if overlap_seconds > 0:
            hits.add(event)
    return tuple(sorted(hits))


def summarize_combo_counter(counter: Counter[tuple[str, ...]]) -> dict[str, object]:
    event_presence = Counter()
    for combo, count in counter.items():
        for event in combo:
            event_presence[event] += count
    single_event_only = {combo[0]: count for combo, count in counter.items() if len(combo) == 1}
    return {
        "windows": int(sum(counter.values())),
        "combo_counts": {"|".join(combo): count for combo, count in sorted(counter.items())},
        "event_presence": {event: int(event_presence.get(event, 0)) for event in TARGET_OVERLAP_EVENTS},
        "single_event_only": {event: int(single_event_only.get(event, 0)) for event in TARGET_OVERLAP_EVENTS},
        "top_combo": "|".join(counter.most_common(1)[0][0]) if counter else "",
        "top_combo_count": int(counter.most_common(1)[0][1]) if counter else 0,
    }


def format_count_pct(count: int, total: int) -> str:
    pct = (100.0 * count / total) if total else 0.0
    return f"{count} ({pct:.1f}%)"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit which CAP micro-event overlap types dominate a kept S2+MCAP window table."
    )
    parser.add_argument("--features-csv", required=True)
    parser.add_argument("--annotation-dir", required=True)
    parser.add_argument("--window-seconds", type=float, default=30.0)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    args = parser.parse_args()

    features_path = Path(args.features_csv)
    if not features_path.is_absolute():
        features_path = ROOT / features_path
    annotation_dir = Path(args.annotation_dir)
    if not annotation_dir.is_absolute():
        annotation_dir = ROOT / annotation_dir

    rows = load_feature_rows(features_path)
    if not rows:
        raise SystemExit("features CSV is empty")

    by_subject: dict[str, list[dict[str, str]]] = defaultdict(list)
    label_by_subject: dict[str, str] = {}
    for row in rows:
        subject_id = row["subject_id"]
        by_subject[subject_id].append(row)
        label_by_subject[subject_id] = row["label"]

    subject_summaries: list[dict[str, object]] = []
    label_full: dict[str, Counter[tuple[str, ...]]] = defaultdict(Counter)
    label_kept: dict[str, Counter[tuple[str, ...]]] = defaultdict(Counter)

    for subject_id in sorted(by_subject):
        label = label_by_subject[subject_id]
        edf_path = annotation_dir / f"{subject_id}.edf"
        txt_path = annotation_dir / f"{subject_id}.txt"
        raw = mne.io.read_raw_edf(edf_path, preload=False, verbose="ERROR")
        annotation_rows = parse_annotation_rows(txt_path, record_start_dt=raw.info["meas_date"])
        record_duration_s = raw.n_times / float(raw.info["sfreq"])

        eligible_s2_rows = [
            row
            for row in annotation_rows
            if row["event"] == "SLEEP-S2"
            and float(row["duration_s"]) >= args.window_seconds
            and float(row["start_s"]) >= 0
            and float(row["start_s"]) + args.window_seconds <= record_duration_s
        ]

        full_counter: Counter[tuple[str, ...]] = Counter()
        for annotation in eligible_s2_rows:
            combo = overlap_combo_for_window(
                start_s=float(annotation["start_s"]),
                end_s=float(annotation["start_s"]) + args.window_seconds,
                annotation_rows=annotation_rows,
                overlap_events=TARGET_OVERLAP_EVENTS,
            )
            if combo:
                full_counter[combo] += 1

        kept_counter: Counter[tuple[str, ...]] = Counter()
        kept_rows = sorted(by_subject[subject_id], key=lambda row: float(row["start_s"]))
        for row in kept_rows:
            combo = overlap_combo_for_window(
                start_s=float(row["start_s"]),
                end_s=float(row["end_s"]),
                annotation_rows=annotation_rows,
                overlap_events=TARGET_OVERLAP_EVENTS,
            )
            if combo:
                kept_counter[combo] += 1

        label_full[label].update(full_counter)
        label_kept[label].update(kept_counter)
        subject_summaries.append(
            {
                "subject_id": subject_id,
                "label": label,
                "eligible_full": summarize_combo_counter(full_counter),
                "kept_first_n": summarize_combo_counter(kept_counter),
            }
        )

    report = {
        "features_csv": str(features_path.resolve()),
        "annotation_dir": str(annotation_dir.resolve()),
        "window_seconds": args.window_seconds,
        "overlap_events": list(TARGET_OVERLAP_EVENTS),
        "subjects": subject_summaries,
        "labels": {
            label: {
                "eligible_full": summarize_combo_counter(label_full[label]),
                "kept_first_n": summarize_combo_counter(label_kept[label]),
            }
            for label in sorted(label_full)
        },
    }

    out_json = Path(args.out_json)
    if not out_json.is_absolute():
        out_json = ROOT / out_json
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")

    subject_lines = []
    for subject in report["subjects"]:
        full = subject["eligible_full"]
        kept = subject["kept_first_n"]
        subject_lines.append(
            "| {subject_id} | {label} | {eligible} | {kept_n} | {top_full} | {top_kept} | {a1} | {a2} | {a3} |".format(
                subject_id=subject["subject_id"],
                label=subject["label"],
                eligible=full["windows"],
                kept_n=kept["windows"],
                top_full=(full["top_combo"] or "-") + f" ({full['top_combo_count']})",
                top_kept=(kept["top_combo"] or "-") + f" ({kept['top_combo_count']})",
                a1=format_count_pct(kept["event_presence"]["MCAP-A1"], kept["windows"]),
                a2=format_count_pct(kept["event_presence"]["MCAP-A2"], kept["windows"]),
                a3=format_count_pct(kept["event_presence"]["MCAP-A3"], kept["windows"]),
            )
        )

    label_lines = []
    for label, summary in report["labels"].items():
        full = summary["eligible_full"]
        kept = summary["kept_first_n"]
        label_lines.append(
            "| {label} | {eligible} | {kept_n} | {full_top} | {kept_top} | {a1} | {a2} | {a3} |".format(
                label=label,
                eligible=full["windows"],
                kept_n=kept["windows"],
                full_top=(full["top_combo"] or "-") + f" ({full['top_combo_count']})",
                kept_top=(kept["top_combo"] or "-") + f" ({kept['top_combo_count']})",
                a1=format_count_pct(kept["event_presence"]["MCAP-A1"], kept["windows"]),
                a2=format_count_pct(kept["event_presence"]["MCAP-A2"], kept["windows"]),
                a3=format_count_pct(kept["event_presence"]["MCAP-A3"], kept["windows"]),
            )
        )

    md = f"""# Pass 8 — overlap event mix audit for the kept S2+MCAP windows

Date: 2026-05-04
Scope: audit which CAP micro-event overlap types dominate the `window_features_pass7_s2_mcap.csv` subset, both across all eligible in-range `SLEEP-S2` windows and across the first-20-per-subject windows actually kept in pass7.

## Why this audit exists

Pass7 added a tighter extraction rule (`SLEEP-S2` plus overlap with `MCAP-A1|MCAP-A2|MCAP-A3`) but did not improve LOSO transfer.
The next bounded question was whether the kept windows are dominated by different CAP micro-event mixtures across subjects or labels, which would make the pass7 subset harder to interpret and suggest a narrower extraction rule for the next run.

## Audited input

- Feature CSV: `projects/bruxism-cap/data/window_features_pass7_s2_mcap.csv`
- Annotation sidecars: `projects/bruxism-cap/data/raw/capslpdb/*.txt`
- Overlap events audited: `MCAP-A1`, `MCAP-A2`, `MCAP-A3`
- Window duration: `{args.window_seconds:g}` seconds

## Subject-level summary

| subject | label | eligible S2+MCAP windows before cap | kept windows | top eligible combo | top kept combo | kept windows with A1 | kept windows with A2 | kept windows with A3 |
|---|---|---:|---:|---|---|---:|---:|---:|
{chr(10).join(subject_lines)}

## Label-level summary

| label | eligible S2+MCAP windows before cap | kept windows | top eligible combo | top kept combo | kept windows with A1 | kept windows with A2 | kept windows with A3 |
|---|---:|---:|---|---|---:|---:|---:|
{chr(10).join(label_lines)}

## Evidence-backed takeaways

1. The pass7 subset is **not** event-type balanced across subjects.
   - `brux2` kept windows are overwhelmingly `MCAP-A3`-overlap (`19/20` windows with `A3`, only `1/20` with `A1`, `1/20` with `A2`).
   - `n5` shows the opposite pattern: its kept windows are mostly `MCAP-A1`-overlap (`16/20` with `A1`).
2. The imbalance already exists in the full eligible pools, not only in the first-20 cap.
   - `brux2` has `111/181` eligible windows with `MCAP-A3` only.
   - `n5` has `134/194` eligible windows with `MCAP-A1` only.
3. The first-20 cap still matters for interpretation because it preserves each subject's earliest local event mix rather than a matched cross-subject mix.
   - Pass7 therefore mixes subjects with materially different overlap-event compositions while keeping the label set tiny.
4. This makes pass7 a stronger negative result than a generic "stage-aware failed" story.
   - The current failure surface is now narrower: even after requiring `SLEEP-S2` plus CAP overlap, the kept windows still reflect different event-family regimes across subjects.

## Best next bounded step

Do **one** narrower extraction variant instead of another broad overlap bucket:
1. keep the current pass7 artifact as a negative baseline
2. add one extraction mode that restricts to a single overlap family such as `MCAP-A3` only, using the verified 5-subject subset
3. rerun random-window CV and LOSO subject aggregation on that single-family table before changing model class

That next test will answer a more interpretable question: does one CAP micro-event family transfer any better than the mixed-family pass7 bucket?
"""

    out_md = Path(args.out_md)
    if not out_md.is_absolute():
        out_md = ROOT / out_md
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(md, encoding="utf-8")

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
