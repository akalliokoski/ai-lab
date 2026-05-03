from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, roc_auc_score
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
    bal_acc = balanced_accuracy_score(y_true, y_pred)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    sensitivity = tp / (tp + fn) if (tp + fn) else 0.0
    specificity = tn / (tn + fp) if (tn + fp) else 0.0
    auc = None
    if len(set(y_true)) == 2:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Train classical baselines on window-level CAP features.")
    parser.add_argument("--features-csv", required=True)
    parser.add_argument("--cv", choices=["random", "loso"], default="loso")
    parser.add_argument("--out", required=True)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.features_csv)
    if df.empty:
        raise SystemExit("features CSV is empty")
    if "subject_id" not in df.columns or "label" not in df.columns:
        raise SystemExit("features CSV must include subject_id and label columns")

    feature_columns = [col for col in df.columns if col not in METADATA_COLUMNS]
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
            fold_metrics.append(metrics)

        summary = {
            key: float(sum(m[key] for m in fold_metrics if m[key] is not None) / len(fold_metrics))
            for key in ["balanced_accuracy", "sensitivity", "specificity"]
        }
        auc_values = [m["auroc"] for m in fold_metrics if m["auroc"] is not None]
        summary["auroc"] = float(sum(auc_values) / len(auc_values)) if auc_values else None
        report["models"][model_name] = {
            "summary": summary,
            "folds": fold_metrics,
        }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
