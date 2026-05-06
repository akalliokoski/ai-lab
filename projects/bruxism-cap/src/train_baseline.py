from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd
from scipy.stats import beta, norm
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, confusion_matrix, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


METADATA_COLUMNS = {
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
    "time_match_rank",
    "relative_time_quantile",
}

# These fields are useful for auditing extraction consistency, but they should not be
# train features because they can encode acquisition differences such as sampling-rate
# mismatches across subjects.
NON_TRAIN_FEATURE_COLUMNS = {
    "n_samples",
    "duration_s",
}


def build_models(random_state: int) -> dict[str, Pipeline]:
    return {
        "logreg": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(max_iter=2000, class_weight="balanced", random_state=random_state),
                ),
            ]
        ),
        "svm": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("model", SVC(kernel="rbf", probability=True, class_weight="balanced", random_state=random_state)),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=300,
                        min_samples_leaf=2,
                        class_weight="balanced",
                        random_state=random_state,
                    ),
                ),
            ]
        ),
    }


def choose_splitter(cv: str, y: pd.Series, groups: pd.Series, random_state: int):
    if cv == "loso":
        splitter = LeaveOneGroupOut()
        return splitter.split(pd.DataFrame(index=y.index), y, groups=groups)
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    return splitter.split(pd.DataFrame(index=y.index), y)


def binary_metrics(y_true, y_pred, y_score) -> dict[str, float | None]:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    sensitivity = tp / (tp + fn) if (tp + fn) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    present_labels = set(y_true)
    if present_labels == {1}:
        bal_acc = sensitivity
    elif present_labels == {0}:
        bal_acc = specificity
    else:
        bal_acc = (sensitivity + specificity) / 2
    auc = None
    if len(present_labels) == 2:
        try:
            auc = float(roc_auc_score(y_true, y_score))
        except ValueError:
            auc = None
    return {
        "balanced_accuracy": float(bal_acc),
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
        "auroc": auc,
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
    }


def clopper_pearson_interval(successes: int, trials: int, *, alpha: float = 0.05) -> dict[str, float | int | str]:
    if trials <= 0:
        return {
            "method": "clopper_pearson",
            "confidence_level": 1.0 - alpha,
            "successes": successes,
            "trials": trials,
            "low": 0.0,
            "high": 1.0,
        }
    low = 0.0 if successes == 0 else float(beta.ppf(alpha / 2, successes, trials - successes + 1))
    high = 1.0 if successes == trials else float(beta.ppf(1 - alpha / 2, successes + 1, trials - successes))
    return {
        "method": "clopper_pearson",
        "confidence_level": 1.0 - alpha,
        "successes": successes,
        "trials": trials,
        "low": low,
        "high": high,
    }


def wilson_interval(successes: int, trials: int, *, alpha: float = 0.05) -> dict[str, float | int | str]:
    if trials <= 0:
        return {
            "method": "wilson",
            "confidence_level": 1.0 - alpha,
            "successes": successes,
            "trials": trials,
            "low": 0.0,
            "high": 1.0,
        }
    p_hat = successes / trials
    z = float(norm.ppf(1 - alpha / 2))
    denom = 1 + (z**2) / trials
    center = (p_hat + (z**2) / (2 * trials)) / denom
    margin = (z / denom) * (((p_hat * (1 - p_hat)) / trials) + ((z**2) / (4 * trials**2))) ** 0.5
    return {
        "method": "wilson",
        "confidence_level": 1.0 - alpha,
        "successes": successes,
        "trials": trials,
        "low": float(max(0.0, center - margin)),
        "high": float(min(1.0, center + margin)),
    }


def add_subject_uncertainty_fields(summary: dict[str, object], y_true_subject: list[int], y_score_subject: list[float]) -> None:
    positive_subject_count = int(sum(y_true_subject))
    negative_subject_count = int(len(y_true_subject) - positive_subject_count)
    summary["subject_probability_brier"] = (
        float(brier_score_loss(y_true_subject, y_score_subject)) if y_true_subject else None
    )
    summary["sensitivity_subject_counts"] = {
        "successes": int(summary["tp"]),
        "trials": positive_subject_count,
    }
    summary["specificity_subject_counts"] = {
        "successes": int(summary["tn"]),
        "trials": negative_subject_count,
    }
    summary["sensitivity_ci_95_exact"] = clopper_pearson_interval(int(summary["tp"]), positive_subject_count)
    summary["sensitivity_ci_95_wilson"] = wilson_interval(int(summary["tp"]), positive_subject_count)
    summary["specificity_ci_95_exact"] = clopper_pearson_interval(int(summary["tn"]), negative_subject_count)
    summary["specificity_ci_95_wilson"] = wilson_interval(int(summary["tn"]), negative_subject_count)


def aggregate_subject_predictions(test_df: pd.DataFrame, *, score_threshold: float = 0.5) -> dict[str, object]:
    subject_rows = []
    for subject_id, subject_df in test_df.groupby("subject_id", sort=True):
        y_true = int(subject_df["y_true"].iloc[0])
        mean_score = float(subject_df["y_score"].mean())
        positive_window_fraction = float(subject_df["y_pred"].mean())
        predicted_positive_windows = int(subject_df["y_pred"].sum())
        y_pred_subject = int(mean_score >= score_threshold)
        subject_rows.append(
            {
                "subject_id": subject_id,
                "true_label": "bruxism" if y_true else "control",
                "predicted_label": "bruxism" if y_pred_subject else "control",
                "windows": int(len(subject_df)),
                "predicted_positive_windows": predicted_positive_windows,
                "positive_window_fraction": positive_window_fraction,
                "mean_score": mean_score,
                "mean_positive_probability": mean_score,
                "correct": bool(y_true == y_pred_subject),
                "y_true": y_true,
                "y_pred": y_pred_subject,
            }
        )

    y_true_subject = [row["y_true"] for row in subject_rows]
    y_pred_subject = [row["y_pred"] for row in subject_rows]
    y_score_subject = [row["mean_score"] for row in subject_rows]
    metrics = binary_metrics(y_true_subject, y_pred_subject, y_score_subject)
    summary = {
        **metrics,
        "subject_count": len(subject_rows),
        "positive_subject_count": int(sum(y_true_subject)),
        "negative_subject_count": int(len(subject_rows) - sum(y_true_subject)),
        "score_threshold": score_threshold,
    }
    add_subject_uncertainty_fields(summary, y_true_subject, y_score_subject)
    return {
        "summary": summary,
        "subjects": [
            {key: value for key, value in row.items() if key not in {"y_true", "y_pred"}}
            for row in subject_rows
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train classical baselines on window-level CAP features.")
    parser.add_argument("--features-csv", required=True)
    parser.add_argument("--cv", choices=["random", "loso"], default="loso")
    parser.add_argument("--out", required=True)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--include-features-regex",
        action="append",
        default=[],
        help="Optional regex filter(s); when provided, only matching feature columns are kept.",
    )
    parser.add_argument(
        "--exclude-features-regex",
        action="append",
        default=[],
        help="Optional regex filter(s); matching feature columns are removed after include filters.",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.features_csv)
    if df.empty:
        raise SystemExit("features CSV is empty")
    if "subject_id" not in df.columns or "label" not in df.columns:
        raise SystemExit("features CSV must include subject_id and label columns")

    feature_columns = [
        col for col in df.columns if col not in METADATA_COLUMNS and col not in NON_TRAIN_FEATURE_COLUMNS
    ]
    base_feature_columns = list(feature_columns)
    include_patterns = [re.compile(pattern) for pattern in args.include_features_regex]
    exclude_patterns = [re.compile(pattern) for pattern in args.exclude_features_regex]
    if include_patterns:
        feature_columns = [
            col for col in feature_columns if any(pattern.search(col) for pattern in include_patterns)
        ]
    if exclude_patterns:
        feature_columns = [
            col for col in feature_columns if not any(pattern.search(col) for pattern in exclude_patterns)
        ]
    if not feature_columns:
        raise SystemExit("feature selection removed all trainable columns")
    excluded_feature_columns = [col for col in df.columns if col in NON_TRAIN_FEATURE_COLUMNS]
    selection_excluded_columns = [col for col in base_feature_columns if col not in feature_columns]
    X = df[feature_columns]
    y = (df["label"].str.lower() == "bruxism").astype(int)
    groups = df["subject_id"]

    report = {
        "features_csv": str(Path(args.features_csv).resolve()),
        "cv": args.cv,
        "rows": int(len(df)),
        "subjects": sorted(groups.unique().tolist()),
        "subject_count": int(groups.nunique()),
        "class_counts": df["label"].value_counts().to_dict(),
        "feature_count": len(feature_columns),
        "feature_columns": feature_columns,
        "excluded_feature_columns": excluded_feature_columns,
        "feature_selection": {
            "include_features_regex": args.include_features_regex,
            "exclude_features_regex": args.exclude_features_regex,
            "selected_feature_count": len(feature_columns),
            "selection_excluded_feature_count": len(selection_excluded_columns),
            "selection_excluded_features": selection_excluded_columns,
        },
        "models": {},
    }

    for model_name, model in build_models(args.random_state).items():
        fold_metrics = []
        for fold_index, (train_idx, test_idx) in enumerate(
            choose_splitter(args.cv, y, groups, args.random_state), start=1
        ):
            X_train = X.iloc[train_idx]
            y_train = y.iloc[train_idx]
            X_test = X.iloc[test_idx]
            y_test = y.iloc[test_idx]
            test_groups = sorted(groups.iloc[test_idx].unique().tolist())

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            if hasattr(model, "predict_proba"):
                y_score = model.predict_proba(X_test)[:, 1]
            else:
                y_score = model.decision_function(X_test)

            metrics = binary_metrics(y_test, y_pred, y_score)
            metrics["fold_index"] = fold_index
            metrics["test_subjects"] = test_groups
            metrics["test_rows"] = int(len(test_idx))
            metrics["subject_aggregation"] = aggregate_subject_predictions(
                pd.DataFrame(
                    {
                        "subject_id": groups.iloc[test_idx].values,
                        "y_true": y_test.values,
                        "y_pred": y_pred,
                        "y_score": y_score,
                    }
                )
            )
            fold_metrics.append(metrics)

        summary = {
            key: float(sum(m[key] for m in fold_metrics if m[key] is not None) / len(fold_metrics))
            for key in ["balanced_accuracy", "sensitivity", "specificity"]
        }
        auc_values = [m["auroc"] for m in fold_metrics if m["auroc"] is not None]
        summary["auroc"] = float(sum(auc_values) / len(auc_values)) if auc_values else None

        subject_rows = []
        for fold in fold_metrics:
            subject_rows.extend(fold["subject_aggregation"]["subjects"])
        y_true_subject = [1 if row["true_label"] == "bruxism" else 0 for row in subject_rows]
        y_pred_subject = [1 if row["predicted_label"] == "bruxism" else 0 for row in subject_rows]
        y_score_subject = [row["mean_score"] for row in subject_rows]
        subject_summary = {
            **binary_metrics(y_true_subject, y_pred_subject, y_score_subject),
            "subject_count": len(subject_rows),
            "positive_subject_count": int(sum(y_true_subject)),
            "negative_subject_count": int(len(subject_rows) - sum(y_true_subject)),
            "score_threshold": 0.5,
        }
        add_subject_uncertainty_fields(subject_summary, y_true_subject, y_score_subject)
        report["models"][model_name] = {
            "summary": summary,
            "folds": fold_metrics,
            "subject_aggregation": {
                "summary": subject_summary,
                "subjects": subject_rows,
            },
        }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
