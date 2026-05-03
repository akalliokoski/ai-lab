from __future__ import annotations

import argparse
import csv
import sys
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
    return mne.io.read_raw_edf(edf_path, preload=True, verbose="ERROR")


def choose_channel(raw, channel_name: str):
    if channel_name in raw.ch_names:
        return channel_name
    lowered = {name.lower(): name for name in raw.ch_names}
    if channel_name.lower() in lowered:
        return lowered[channel_name.lower()]
    raise SystemExit(
        f"Channel '{channel_name}' not found. Available channels: {', '.join(raw.ch_names)}"
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
    parser.add_argument("--start-seconds", type=float, default=0.0)
    parser.add_argument("--stop-seconds", type=float)
    parser.add_argument("--limit-windows", type=int)
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
    signal = raw.get_data(picks=[channel_name])[0][start_sample:stop_sample]

    window_size = int(args.window_seconds * sfreq)
    if window_size <= 0:
        raise SystemExit("window size must be positive")

    rows: list[dict[str, object]] = []
    total_windows = len(signal) // window_size
    if args.limit_windows is not None:
        total_windows = min(total_windows, args.limit_windows)

    for window_index in range(total_windows):
        start = window_index * window_size
        end = start + window_size
        window = signal[start:end]
        feats = extract_window_features(window, sfreq=sfreq)
        rows.append(
            {
                "subject_id": args.subject_id,
                "label": args.label,
                "source_file": edf_path.name,
                "channel": channel_name,
                "window_index": window_index,
                "start_s": round((start_sample + start) / sfreq, 3),
                "end_s": round((start_sample + end) / sfreq, 3),
                **feats,
            }
        )

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    write_rows(rows, out_path, append=args.append)
    print(f"wrote {len(rows)} windows to {out_path}")
    print(f"subject={args.subject_id} label={args.label} channel={channel_name} sfreq={sfreq}")


if __name__ == "__main__":
    main()
