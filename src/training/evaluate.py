import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score


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
    parser = argparse.ArgumentParser(description="Evaluate a trained model.")
    parser.add_argument("--model_dir", required=True, help="Directory containing model.joblib and test.parquet")
    parser.add_argument("--data_path", default=None, help="Optional fallback data path if test.parquet is missing")
    parser.add_argument("--label_col", default="label", help="Label column name")
    args = parser.parse_args()

    model_dir = Path(args.model_dir)
    model_path = model_dir / "model.joblib"
    test_path = model_dir / "test.parquet"

    if test_path.exists():
        df = pd.read_parquet(test_path)
    elif args.data_path:
        df = load_dataset(Path(args.data_path))
    else:
        raise FileNotFoundError("test.parquet not found and no --data_path provided")

    if args.label_col not in df.columns:
        raise ValueError(f"Label column '{args.label_col}' not found in dataset columns")

    df = df.dropna(subset=[args.label_col])
    y = df[args.label_col].astype(int)
    X = df.drop(columns=[args.label_col])
    X = X.apply(pd.to_numeric, errors="coerce")

    model = joblib.load(model_path)
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]

    acc = accuracy_score(y, y_pred)
    roc_auc = roc_auc_score(y, y_prob)
    print(f"Accuracy: {acc:.4f}, ROC-AUC: {roc_auc:.4f}")


if __name__ == "__main__":
    main()
