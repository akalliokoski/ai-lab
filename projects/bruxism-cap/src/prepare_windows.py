from __future__ import annotations

import argparse
import csv
import sys
from datetime import timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from features import extract_window_features, feature_column_order  # noqa: E402


def load_raw(edf_path: Path):
    try:
        import mne
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise SystemExit(
            "mne is required for EDF loading. Activate the repo venv and run: uv pip install -e '.[biosignals]'"
        ) from exc
    # Avoid preloading the full EDF into memory; CAP recordings are large and this
    # starter project usually needs only channel names or one channel slice at a time.
    return mne.io.read_raw_edf(edf_path, preload=False, verbose="ERROR")


def choose_channel(raw, channel_name: str):
    if channel_name in raw.ch_names:
        return channel_name
    lowered = {name.lower(): name for name in raw.ch_names}
    if channel_name.lower() in lowered:
        return lowered[channel_name.lower()]
    raise SystemExit(
        f"Channel '{channel_name}' not found. Available channels: {', '.join(raw.ch_names)}"
    )


def parse_annotation_rows(annotation_path: Path, *, record_start_dt) -> list[dict[str, object]]:
    text = annotation_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    try:
        header_index = next(i for i, line in enumerate(lines) if line.startswith("Sleep Stage"))
    except StopIteration as exc:
        raise SystemExit(f"Could not find scored-event table in annotation file: {annotation_path}") from exc

    if record_start_dt.tzinfo is None:
        record_start_dt = record_start_dt.replace(tzinfo=timezone.utc)
    else:
        record_start_dt = record_start_dt.astimezone(timezone.utc)

    rows: list[dict[str, object]] = []
    for raw_line in lines[header_index + 1 :]:
        if not raw_line.strip():
            continue
        parts = raw_line.split("\t")
        if len(parts) == 6:
            sleep_stage, _position, time_str, event, duration_s, location = parts
        elif len(parts) == 5:
            sleep_stage, time_str, event, duration_s, location = parts
        else:
            continue

        normalized_time = time_str.replace(".", ":")
        hour, minute, second = (int(piece) for piece in normalized_time.split(":"))
        event_dt = record_start_dt.replace(hour=hour, minute=minute, second=second)
        if event_dt < record_start_dt:
            event_dt += timedelta(days=1)
        onset_s = (event_dt - record_start_dt).total_seconds()
        rows.append(
            {
                "sleep_stage": sleep_stage,
                "event": event,
                "duration_s": float(duration_s),
                "location": location,
                "start_s": onset_s,
            }
        )
    return rows


def overlaps_required_events(
    candidate_row: dict[str, object],
    *,
    candidate_window_seconds: float,
    other_rows: list[dict[str, object]],
    required_events: set[str],
    min_overlap_seconds: float,
) -> bool:
    candidate_start = float(candidate_row["start_s"])
    candidate_end = candidate_start + candidate_window_seconds
    for row in other_rows:
        if row["event"] not in required_events:
            continue
        other_start = float(row["start_s"])
        other_end = other_start + float(row["duration_s"])
        overlap_seconds = min(candidate_end, other_end) - max(candidate_start, other_start)
        if overlap_seconds >= min_overlap_seconds:
            return True
    return False


def overlaps_any_events(
    candidate_row: dict[str, object],
    *,
    candidate_window_seconds: float,
    other_rows: list[dict[str, object]],
    event_names: set[str],
    min_overlap_seconds: float,
) -> bool:
    return overlaps_required_events(
        candidate_row,
        candidate_window_seconds=candidate_window_seconds,
        other_rows=other_rows,
        required_events=event_names,
        min_overlap_seconds=min_overlap_seconds,
    )


def write_rows(rows: list[dict[str, object]], out_path: Path, append: bool) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "subject_id",
        "label",
        "source_file",
        "channel",
        "window_index",
        "start_s",
        "end_s",
        "annotation_event",
        "annotation_stage",
        "annotation_location",
        "signal_transform",
    ] + feature_column_order()

    mode = "a" if append and out_path.exists() else "w"
    with out_path.open(mode, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if mode == "w":
            writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert one EDF record into fixed-window handcrafted features.")
    parser.add_argument("--edf", required=True, help="Path to EDF file")
    parser.add_argument("--subject-id", help="Subject / record id, e.g. brux1")
    parser.add_argument("--label", choices=["bruxism", "control"], help="Binary label for this record")
    parser.add_argument("--channel", help="Exact or case-insensitive channel name to extract")
    parser.add_argument("--window-seconds", type=float, default=30.0)
    parser.add_argument(
        "--normalize-mode",
        choices=["none", "median_mad"],
        default="none",
        help="Optional per-window signal normalization before feature extraction.",
    )
    parser.add_argument("--start-seconds", type=float, default=0.0)
    parser.add_argument("--stop-seconds", type=float)
    parser.add_argument("--limit-windows", type=int)
    parser.add_argument("--annotation-txt", help="Optional RemLogic event-export .txt sidecar for annotation-aware window selection")
    parser.add_argument(
        "--annotation-events",
        help="Comma-separated event names to extract as windows, e.g. SLEEP-S2 or SLEEP-REM",
    )
    parser.add_argument(
        "--require-overlap-events",
        help="Optional comma-separated event names that each extracted annotation window must overlap, e.g. MCAP-A1,MCAP-A2,MCAP-A3",
    )
    parser.add_argument(
        "--min-overlap-seconds",
        type=float,
        default=0.001,
        help="Minimum positive overlap required between an extracted annotation window and any required overlap event",
    )
    parser.add_argument(
        "--exclude-overlap-events",
        help="Optional comma-separated event names that must NOT overlap a kept annotation window, e.g. MCAP-A1,MCAP-A2",
    )
    parser.add_argument("--out", help="Output CSV path")
    parser.add_argument("--append", action="store_true", help="Append rows to output CSV if it exists")
    parser.add_argument("--list-channels", action="store_true", help="Print channel names and exit")
    args = parser.parse_args()

    edf_path = Path(args.edf)
    if not edf_path.is_absolute():
        edf_path = ROOT / edf_path
    raw = load_raw(edf_path)

    if args.list_channels:
        for name in raw.ch_names:
            print(name)
        return

    if not args.subject_id or not args.label or not args.channel or not args.out:
        raise SystemExit("--subject-id, --label, --channel, and --out are required unless --list-channels is used")

    channel_name = choose_channel(raw, args.channel)
    sfreq = float(raw.info["sfreq"])
    start_sample = int(args.start_seconds * sfreq)
    stop_sample = int(args.stop_seconds * sfreq) if args.stop_seconds is not None else raw.n_times

    window_size = int(args.window_seconds * sfreq)
    if window_size <= 0:
        raise SystemExit("window size must be positive")

    if args.limit_windows is not None:
        requested_stop = start_sample + args.limit_windows * window_size
        stop_sample = min(stop_sample, requested_stop)

    rows: list[dict[str, object]] = []

    annotation_events = None
    if args.annotation_events:
        annotation_events = {item.strip() for item in args.annotation_events.split(",") if item.strip()}
        if not annotation_events:
            raise SystemExit("--annotation-events was provided but no event names were parsed")

    required_overlap_events = None
    if args.require_overlap_events:
        required_overlap_events = {item.strip() for item in args.require_overlap_events.split(",") if item.strip()}
        if not required_overlap_events:
            raise SystemExit("--require-overlap-events was provided but no event names were parsed")
        if not annotation_events:
            raise SystemExit("--require-overlap-events requires --annotation-events because overlap is checked against extracted annotation windows")
        if args.min_overlap_seconds <= 0:
            raise SystemExit("--min-overlap-seconds must be positive when overlap filtering is used")

    excluded_overlap_events = None
    if args.exclude_overlap_events:
        excluded_overlap_events = {item.strip() for item in args.exclude_overlap_events.split(",") if item.strip()}
        if not excluded_overlap_events:
            raise SystemExit("--exclude-overlap-events was provided but no event names were parsed")
        if not annotation_events:
            raise SystemExit("--exclude-overlap-events requires --annotation-events because exclusion is checked against extracted annotation windows")
        if args.min_overlap_seconds <= 0:
            raise SystemExit("--min-overlap-seconds must be positive when overlap filtering is used")

    if annotation_events:
        annotation_path = Path(args.annotation_txt) if args.annotation_txt else edf_path.with_suffix(".txt")
        if not annotation_path.is_absolute():
            annotation_path = ROOT / annotation_path
        if not annotation_path.exists():
            raise SystemExit(f"annotation file not found: {annotation_path}")
        annotation_rows = parse_annotation_rows(annotation_path, record_start_dt=raw.info["meas_date"])
        record_duration_s = raw.n_times / sfreq
        matching_rows = [
            row
            for row in annotation_rows
            if row["event"] in annotation_events
            and row["duration_s"] >= args.window_seconds
            and row["start_s"] >= args.start_seconds
            and row["start_s"] + args.window_seconds <= record_duration_s
            and (args.stop_seconds is None or row["start_s"] + args.window_seconds <= args.stop_seconds)
        ]
        if required_overlap_events:
            matching_rows = [
                row
                for row in matching_rows
                if overlaps_any_events(
                    row,
                    candidate_window_seconds=args.window_seconds,
                    other_rows=annotation_rows,
                    event_names=required_overlap_events,
                    min_overlap_seconds=args.min_overlap_seconds,
                )
            ]
        if excluded_overlap_events:
            matching_rows = [
                row
                for row in matching_rows
                if not overlaps_any_events(
                    row,
                    candidate_window_seconds=args.window_seconds,
                    other_rows=annotation_rows,
                    event_names=excluded_overlap_events,
                    min_overlap_seconds=args.min_overlap_seconds,
                )
            ]
        if args.limit_windows is not None:
            matching_rows = matching_rows[: args.limit_windows]

        for window_index, annotation in enumerate(matching_rows):
            start_sample = int(annotation["start_s"] * sfreq)
            end_sample = start_sample + window_size
            window = raw.get_data(picks=[channel_name], start=start_sample, stop=end_sample)[0]
            feats = extract_window_features(window, sfreq=sfreq, normalize_mode=args.normalize_mode)
            rows.append(
                {
                    "subject_id": args.subject_id,
                    "label": args.label,
                    "source_file": edf_path.name,
                    "channel": channel_name,
                    "window_index": window_index,
                    "start_s": round(annotation["start_s"], 3),
                    "end_s": round(annotation["start_s"] + args.window_seconds, 3),
                    "annotation_event": annotation["event"],
                    "annotation_stage": annotation["sleep_stage"],
                    "annotation_location": annotation["location"],
                    "signal_transform": args.normalize_mode,
                    **feats,
                }
            )
    else:
        signal = raw.get_data(picks=[channel_name], start=start_sample, stop=stop_sample)[0]
        total_windows = len(signal) // window_size
        if args.limit_windows is not None:
            total_windows = min(total_windows, args.limit_windows)

        for window_index in range(total_windows):
            start = window_index * window_size
            end = start + window_size
            window = signal[start:end]
            feats = extract_window_features(window, sfreq=sfreq, normalize_mode=args.normalize_mode)
            rows.append(
                {
                    "subject_id": args.subject_id,
                    "label": args.label,
                    "source_file": edf_path.name,
                    "channel": channel_name,
                    "window_index": window_index,
                    "start_s": round((start_sample + start) / sfreq, 3),
                    "end_s": round((start_sample + end) / sfreq, 3),
                    "annotation_event": "",
                    "annotation_stage": "",
                    "annotation_location": "",
                    "signal_transform": args.normalize_mode,
                    **feats,
                }
            )

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    write_rows(rows, out_path, append=args.append)
    print(f"wrote {len(rows)} windows to {out_path}")
    print(
        f"subject={args.subject_id} label={args.label} channel={channel_name} sfreq={sfreq} normalize_mode={args.normalize_mode}"
    )


if __name__ == "__main__":
    main()
