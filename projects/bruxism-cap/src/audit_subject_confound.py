from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier, NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


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
}

NON_TRAIN_FEATURE_COLUMNS = {
    "n_samples",
    "duration_s",
}


def load_feature_frame(path: Path) -> tuple[pd.DataFrame, list[str]]:
    df = pd.read_csv(path)
    if df.empty:
        raise SystemExit(f"features CSV is empty: {path}")
    required = {"subject_id", "label"}
    missing = required.difference(df.columns)
    if missing:
        raise SystemExit(f"features CSV missing required columns {sorted(missing)}: {path}")
    feature_columns = [
        col for col in df.columns if col not in METADATA_COLUMNS and col not in NON_TRAIN_FEATURE_COLUMNS
    ]
    if not feature_columns:
        raise SystemExit(f"no trainable feature columns found in {path}")
    return df, feature_columns


def transformed_features(df: pd.DataFrame, feature_columns: list[str]) -> np.ndarray:
    pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    return pipeline.fit_transform(df[feature_columns])


def safe_silhouette(X: np.ndarray, labels: pd.Series) -> float | None:
    unique = pd.Series(labels).nunique()
    if unique < 2 or unique >= len(labels):
        return None
    return float(silhouette_score(X, labels))


def nearest_neighbor_rates(X: np.ndarray, subject_ids: pd.Series, labels: pd.Series) -> dict[str, float]:
    nn = NearestNeighbors(n_neighbors=2, metric="euclidean")
    nn.fit(X)
    neighbor_indices = nn.kneighbors(X, return_distance=False)[:, 1]
    same_subject = (subject_ids.to_numpy() == subject_ids.iloc[neighbor_indices].to_numpy()).mean()
    same_label = (labels.to_numpy() == labels.iloc[neighbor_indices].to_numpy()).mean()
    return {
        "same_subject_rate": float(same_subject),
        "same_label_rate": float(same_label),
        "subject_minus_label_gap": float(same_subject - same_label),
    }


def random_cv_scores(X: np.ndarray, subject_ids: pd.Series, y_label: pd.Series) -> dict[str, float]:
    splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    subject_scores = []
    label_scores = []

    for train_idx, test_idx in splitter.split(X, subject_ids):
        subject_model = KNeighborsClassifier(n_neighbors=1)
        subject_model.fit(X[train_idx], subject_ids.iloc[train_idx])
        subject_scores.append(float((subject_model.predict(X[test_idx]) == subject_ids.iloc[test_idx]).mean()))

    for train_idx, test_idx in splitter.split(X, y_label):
        label_model = KNeighborsClassifier(n_neighbors=1)
        label_model.fit(X[train_idx], y_label.iloc[train_idx])
        label_scores.append(float((label_model.predict(X[test_idx]) == y_label.iloc[test_idx]).mean()))

    subject_cv_acc = float(np.mean(subject_scores))
    label_cv_acc = float(np.mean(label_scores))
    return {
        "subject_1nn_random_cv_accuracy": subject_cv_acc,
        "label_1nn_random_cv_accuracy": label_cv_acc,
        "subject_minus_label_random_cv_gap": float(subject_cv_acc - label_cv_acc),
    }


def pca_summary(X: np.ndarray) -> dict[str, object]:
    n_components = min(5, X.shape[1], X.shape[0])
    pca = PCA(n_components=n_components)
    pca.fit(X)
    return {
        "components": int(n_components),
        "explained_variance_ratio": [float(x) for x in pca.explained_variance_ratio_],
    }


def audit_dataset(path: Path) -> dict[str, object]:
    df, feature_columns = load_feature_frame(path)
    X = transformed_features(df, feature_columns)
    label_binary = (df["label"].str.lower() == "bruxism").astype(int)
    subject_counts = df["subject_id"].value_counts().sort_index()
    label_counts = df["label"].value_counts().sort_index()
    subject_silhouette = safe_silhouette(X, df["subject_id"])
    label_silhouette = safe_silhouette(X, df["label"])
    nn_rates = nearest_neighbor_rates(X, df["subject_id"], df["label"])
    knn_scores = random_cv_scores(X, df["subject_id"], label_binary)

    return {
        "features_csv": str(path.resolve()),
        "rows": int(len(df)),
        "subject_count": int(df["subject_id"].nunique()),
        "label_counts": label_counts.to_dict(),
        "subject_counts": {str(k): int(v) for k, v in subject_counts.items()},
        "feature_count": len(feature_columns),
        "feature_columns": feature_columns,
        "silhouette": {
            "subject_id": subject_silhouette,
            "label": label_silhouette,
            "subject_minus_label_gap": None
            if subject_silhouette is None or label_silhouette is None
            else float(subject_silhouette - label_silhouette),
        },
        "nearest_neighbor": nn_rates,
        "memorization_probe": knn_scores,
        "pca": pca_summary(X),
    }


def render_markdown(audits: list[dict[str, object]]) -> str:
    lines = [
        "# Subject-versus-label confound audit",
        "",
        "This audit checks whether standardized handcrafted feature windows cluster more strongly by `subject_id` than by the target `label`.",
        "Higher subject clustering than label clustering is evidence that random window splits can reward subject memorization rather than transferable bruxism detection.",
        "",
        "## Metrics",
        "",
        "- `silhouette.subject_id` vs `silhouette.label`: larger values mean stronger cluster separation in feature space.",
        "- `nearest_neighbor.same_subject_rate` vs `same_label_rate`: for each window, compare its closest other window after standardization.",
        "- `memorization_probe.subject_1nn_random_cv_accuracy` vs `label_1nn_random_cv_accuracy`: a 5-fold random-window 1-NN probe showing whether subject identity is easier to recover than label under the same leakage-prone split style.",
        "",
    ]
    for audit in audits:
        name = Path(audit["features_csv"]).name
        sil = audit["silhouette"]
        nn = audit["nearest_neighbor"]
        mem = audit["memorization_probe"]
        lines.extend(
            [
                f"## {name}",
                "",
                f"- rows: `{audit['rows']}`",
                f"- subjects: `{audit['subject_count']}`",
                f"- label counts: `{audit['label_counts']}`",
                f"- silhouette(subject): `{sil['subject_id']}`",
                f"- silhouette(label): `{sil['label']}`",
                f"- silhouette gap subject-label: `{sil['subject_minus_label_gap']}`",
                f"- nearest-neighbor same-subject rate: `{nn['same_subject_rate']}`",
                f"- nearest-neighbor same-label rate: `{nn['same_label_rate']}`",
                f"- nearest-neighbor subject-label gap: `{nn['subject_minus_label_gap']}`",
                f"- 1-NN subject random-CV accuracy: `{mem['subject_1nn_random_cv_accuracy']}`",
                f"- 1-NN label random-CV accuracy: `{mem['label_1nn_random_cv_accuracy']}`",
                f"- 1-NN random-CV gap subject-label: `{mem['subject_minus_label_random_cv_gap']}`",
                "",
            ]
        )

    if len(audits) >= 2:
        first, second = audits[0], audits[1]
        lines.extend(
            [
                "## Comparison summary",
                "",
                f"- Subject silhouette changed from `{first['silhouette']['subject_id']}` to `{second['silhouette']['subject_id']}`.",
                f"- Label silhouette changed from `{first['silhouette']['label']}` to `{second['silhouette']['label']}`.",
                f"- Nearest-neighbor subject-label gap changed from `{first['nearest_neighbor']['subject_minus_label_gap']}` to `{second['nearest_neighbor']['subject_minus_label_gap']}`.",
                "",
            ]
        )

    all_label_stronger = all(
        audit["silhouette"]["subject_minus_label_gap"] is not None
        and audit["silhouette"]["subject_minus_label_gap"] < 0
        and audit["nearest_neighbor"]["subject_minus_label_gap"] < 0
        and audit["memorization_probe"]["subject_minus_label_random_cv_gap"] < 0
        for audit in audits
    )
    if all_label_stronger:
        lines.extend(
            [
                "## Verdict",
                "",
                "Across the audited tables, label-separation signals were stronger than subject-separation signals on all three quick probes.",
                "That means the current leakage story is not best summarized as pure subject-ID memorization. The sharper bottleneck is that the label boundary visible inside random window splits does not transfer to held-out subjects.",
            ]
        )
    else:
        lines.extend(
            [
                "## Verdict",
                "",
                "At least one audit showed subject-separation as strong as or stronger than label-separation, so subject/background confounding remains a live explanation to test further.",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit whether CAP feature windows cluster more by subject than by label.")
    parser.add_argument("features_csv", nargs="+", help="One or more feature CSV files to audit")
    parser.add_argument("--out-json", required=True, help="Path to save the JSON audit")
    parser.add_argument("--out-md", required=True, help="Path to save the markdown audit summary")
    args = parser.parse_args()

    audits = [audit_dataset(Path(path)) for path in args.features_csv]
    payload = {"audits": audits}

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(render_markdown(audits), encoding="utf-8")

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
