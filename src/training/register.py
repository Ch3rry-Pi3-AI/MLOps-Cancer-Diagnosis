import argparse
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn


def main() -> None:
    parser = argparse.ArgumentParser(description="Register a trained model with MLflow.")
    parser.add_argument("--model_path", required=True, help="Path to model.joblib")
    parser.add_argument("--model_name", default="breast-cancer-classifier", help="Model name to register")
    args = parser.parse_args()

    model_path = Path(args.model_path)
    model = joblib.load(model_path)

    with mlflow.start_run():
        mlflow.sklearn.log_model(model, artifact_path="model")
        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/model"
        mlflow.register_model(model_uri, args.model_name)
        print(f"Registered model '{args.model_name}' from {model_uri}")


if __name__ == "__main__":
    main()
