from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def summarize(series: pd.Series) -> dict[str, float]:
    return {
        "count": int(series.shape[0]),
        "min": float(series.min()),
        "median": float(series.median()),
        "mean": float(series.mean()),
        "max": float(series.max()),
    }


def choose_evenly_spaced_rows(subject_df: pd.DataFrame, *, cap: int) -> pd.DataFrame:
    if len(subject_df) < cap:
        raise SystemExit(
            f"subject {subject_df['subject_id'].iloc[0]} has only {len(subject_df)} candidate rows after filtering; need {cap}"
        )
    ordered = subject_df.sort_values(["start_s", "window_index"]).reset_index(drop=True)
    if cap == 1:
        selected = ordered.iloc[[len(ordered) // 2]].copy()
    else:
        positions = [round(i * (len(ordered) - 1) / (cap - 1)) for i in range(cap)]
        # Deduplicate while preserving order, then fill gaps with nearest unused rows.
        chosen = []
        used = set()
        for pos in positions:
            candidate = pos
            if candidate in used:
                left = right = candidate
                while left in used and left > 0:
                    left -= 1
                while right in used and right < len(ordered) - 1:
                    right += 1
                options = [idx for idx in (left, right) if idx not in used]
                candidate = min(options, key=lambda idx: abs(idx - pos)) if options else candidate
            used.add(candidate)
            chosen.append(candidate)
        selected = ordered.iloc[chosen].copy()
    selected["time_match_rank"] = list(range(1, len(selected) + 1))
    return selected


def add_relative_time_quantile(subject_df: pd.DataFrame) -> pd.DataFrame:
    ordered = subject_df.sort_values(["start_s", "window_index"]).reset_index(drop=True).copy()
    if len(ordered) == 1:
        ordered["relative_time_quantile"] = 0.5
    else:
        ordered["relative_time_quantile"] = ordered.index / (len(ordered) - 1)
    return ordered


def filter_shared_interval(by_subject: dict[str, pd.DataFrame]) -> tuple[dict[str, pd.DataFrame], dict[str, object]]:
    common_start = max(float(subject_df["start_s"].min()) for subject_df in by_subject.values())
    common_end = min(float(subject_df["start_s"].max()) for subject_df in by_subject.values())
    if common_end <= common_start:
        raise SystemExit("no shared start_s interval exists across the requested subjects")

    filtered = {}
    for subject_id, subject_df in by_subject.items():
        kept = subject_df[(subject_df["start_s"] >= common_start) & (subject_df["start_s"] <= common_end)].copy()
        if kept.empty:
            raise SystemExit(f"subject {subject_id} has no rows inside the shared interval")
        filtered[subject_id] = kept
    return filtered, {
        "match_mode": "shared-interval",
        "shared_interval": {"start_s": common_start, "end_s": common_end},
    }


def filter_percentile_band(
    by_subject: dict[str, pd.DataFrame], *, lower_quantile: float, upper_quantile: float
) -> tuple[dict[str, pd.DataFrame], dict[str, object]]:
    if not 0.0 <= lower_quantile < upper_quantile <= 1.0:
        raise SystemExit("percentile-band mode requires 0.0 <= lower < upper <= 1.0")

    filtered = {}
    for subject_id, subject_df in by_subject.items():
        with_quantiles = add_relative_time_quantile(subject_df)
        kept = with_quantiles[
            (with_quantiles["relative_time_quantile"] >= lower_quantile)
            & (with_quantiles["relative_time_quantile"] <= upper_quantile)
        ].copy()
        if kept.empty:
            raise SystemExit(
                f"subject {subject_id} has no rows inside percentile band [{lower_quantile}, {upper_quantile}]"
            )
        filtered[subject_id] = kept

    return filtered, {
        "match_mode": "percentile-band",
        "percentile_band": {"lower_quantile": lower_quantile, "upper_quantile": upper_quantile},
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Select a simple shared-time-position-matched subset from an uncapped feature CSV."
    )
    parser.add_argument("--features-csv", required=True)
    parser.add_argument("--subjects", required=True, help="Comma-separated subject ids to keep")
    parser.add_argument("--cap", type=int, required=True, help="Windows per subject after matching")
    parser.add_argument(
        "--mode",
        choices=["shared-interval", "percentile-band"],
        default="shared-interval",
        help="How to constrain time position before the per-subject evenly spaced selection step.",
    )
    parser.add_argument(
        "--lower-quantile",
        type=float,
        default=0.0,
        help="Lower inclusive relative-time quantile for --mode percentile-band.",
    )
    parser.add_argument(
        "--upper-quantile",
        type=float,
        default=1.0,
        help="Upper inclusive relative-time quantile for --mode percentile-band.",
    )
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--out-json")
    args = parser.parse_args()

    df = pd.read_csv(args.features_csv)
    subject_ids = [item.strip() for item in args.subjects.split(",") if item.strip()]
    if not subject_ids:
        raise SystemExit("--subjects parsed to an empty set")

    df = df[df["subject_id"].isin(subject_ids)].copy()
    if df.empty:
        raise SystemExit("no rows remain after subject filtering")

    missing = sorted(set(subject_ids) - set(df["subject_id"].unique().tolist()))
    if missing:
        raise SystemExit(f"missing requested subjects: {', '.join(missing)}")

    by_subject = {subject_id: df[df["subject_id"] == subject_id].copy() for subject_id in subject_ids}
    if args.mode == "shared-interval":
        filtered, mode_report = filter_shared_interval(by_subject)
    else:
        filtered, mode_report = filter_percentile_band(
            by_subject,
            lower_quantile=args.lower_quantile,
            upper_quantile=args.upper_quantile,
        )

    selected_parts = []
    report = {
        "features_csv": str(Path(args.features_csv).resolve()),
        "subjects": subject_ids,
        **mode_report,
        "cap_per_subject": args.cap,
        "pre_filter_rows": int(len(df)),
        "subjects_summary": {},
    }
    for subject_id in subject_ids:
        kept = filtered[subject_id]
        chosen = choose_evenly_spaced_rows(kept, cap=args.cap)
        selected_parts.append(chosen)
        report["subjects_summary"][subject_id] = {
            "label": str(chosen["label"].iloc[0]),
            "candidate_rows_after_match_filter": int(len(kept)),
            "candidate_start_s": summarize(kept["start_s"]),
            "selected_start_s": summarize(chosen["start_s"]),
            "selected_start_s_values": [float(value) for value in chosen["start_s"].tolist()],
        }
        if "relative_time_quantile" in kept.columns:
            report["subjects_summary"][subject_id]["candidate_relative_time_quantile"] = summarize(
                kept["relative_time_quantile"]
            )
            report["subjects_summary"][subject_id]["selected_relative_time_quantile"] = summarize(
                chosen["relative_time_quantile"]
            )
            report["subjects_summary"][subject_id]["selected_relative_time_quantile_values"] = [
                float(value) for value in chosen["relative_time_quantile"].tolist()
            ]

    out_df = pd.concat(selected_parts, ignore_index=True)
    out_df = out_df.sort_values(["subject_id", "time_match_rank", "start_s", "window_index"]).reset_index(drop=True)

    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False)

    report["out_csv"] = str(out_path.resolve())
    report["rows_written"] = int(len(out_df))
    report["selected_subject_means"] = {
        subject_id: report["subjects_summary"][subject_id]["selected_start_s"]["mean"]
        for subject_id in subject_ids
    }

    if args.out_json:
        out_json = Path(args.out_json)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
