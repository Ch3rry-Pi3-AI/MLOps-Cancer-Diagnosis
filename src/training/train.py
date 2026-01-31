import argparse
from pathlib import Path

import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV, StratifiedKFold


def load_dataset(data_path: Path) -> pd.DataFrame:
    if data_path.is_dir():
        files = list(data_path.glob("*.parquet"))
        if not files:
            raise FileNotFoundError(f"No parquet files found in {data_path}")
        frames = [pd.read_parquet(file) for file in files]
        return pd.concat(frames, ignore_index=True)
    if data_path.suffix.lower() == ".parquet":
        return pd.read_parquet(data_path)
    if data_path.suffix.lower() == ".csv":
        return pd.read_csv(data_path)
    raise ValueError(f"Unsupported data format: {data_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a breast cancer classifier.")
    parser.add_argument("--data_path", required=True, help="Path to gold dataset (file or folder)")
    parser.add_argument("--model_output", required=True, help="Output directory for the trained model")
    parser.add_argument("--label_col", default="label", help="Label column name")
    parser.add_argument("--test_size", type=float, default=0.2, help="Test split ratio")
    parser.add_argument("--random_state", type=int, default=42, help="Random seed")
    parser.add_argument("--use_grid_search", action="store_true", help="Enable GridSearchCV for LogisticRegression")
    args = parser.parse_args()

    data_path = Path(args.data_path)
    model_output = Path(args.model_output)
    model_output.mkdir(parents=True, exist_ok=True)

    df = load_dataset(data_path)
    if args.label_col not in df.columns:
        raise ValueError(f"Label column '{args.label_col}' not found in dataset columns")

    df = df.dropna(subset=[args.label_col])
    y = df[args.label_col].astype(int)
    X = df.drop(columns=[args.label_col])
    X = X.apply(pd.to_numeric, errors="coerce")
    X = X.dropna(axis=1, how="all")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y
    )

    base_model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("model", RandomForestClassifier(random_state=args.random_state)),
        ]
    )

    if args.use_grid_search:
        param_grid = {
            "model__n_estimators": [200, 400],
            "model__max_depth": [None, 8, 16],
            "model__min_samples_split": [2, 5],
        }
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=args.random_state)
        search = GridSearchCV(
            base_model,
            param_grid=param_grid,
            scoring="roc_auc",
            cv=cv,
            n_jobs=-1,
        )
        search.fit(X_train, y_train)
        model = search.best_estimator_
        mlflow.log_param("best_params", str(search.best_params_))
        mlflow.log_metric("cv_best_roc_auc", search.best_score_)
    else:
        model = base_model
        model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_prob)

    mlflow.log_param("model_type", "random_forest")
    mlflow.log_param("test_size", args.test_size)
    mlflow.log_metric("accuracy", acc)
    mlflow.log_metric("roc_auc", roc_auc)

    model_path = model_output / "model.joblib"
    joblib.dump(model, model_path)

    test_path = model_output / "test.parquet"
    test_df = X_test.copy()
    test_df[args.label_col] = y_test.values
    test_df.to_parquet(test_path, index=False)

    metrics_path = model_output / "metrics.json"
    metrics_path.write_text(
        f'{{"accuracy": {acc:.6f}, "roc_auc": {roc_auc:.6f}}}\n',
        encoding="utf-8",
    )

    print(f"Saved model to {model_path}")
    print(f"Accuracy: {acc:.4f}, ROC-AUC: {roc_auc:.4f}")


if __name__ == "__main__":
    main()
