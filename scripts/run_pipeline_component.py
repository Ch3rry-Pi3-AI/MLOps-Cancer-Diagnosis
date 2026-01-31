import argparse
import json
from pathlib import Path

from azure.ai.ml import MLClient, Input
from azure.ai.ml.entities import AzureDataLakeGen2Datastore, Data, NoneCredentialConfiguration
from azure.identity import DefaultAzureCredential

ROOT = Path(__file__).resolve().parents[1]
TERRAFORM_DIR = ROOT / "terraform"


def read_outputs_value(outputs_path: Path, key: str):
    if not outputs_path.exists():
        return None
    data = json.loads(outputs_path.read_text(encoding="utf-8"))
    entry = data.get(key)
    if isinstance(entry, dict) and "value" in entry:
        return entry["value"]
    return None


def extract_subscription_id(resource_id: str) -> str:
    marker = "/subscriptions/"
    if marker not in resource_id:
        raise ValueError("Subscription ID not found in resource ID.")
    return resource_id.split(marker, 1)[1].split("/", 1)[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit an AML pipeline component run.")
    parser.add_argument("--component-name", default="breast_cancer_train_pipeline", help="Pipeline component name")
    parser.add_argument("--component-version", default="1", help="Pipeline component version")
    parser.add_argument(
        "--training-data",
        default="",
        help="Training data URI for the pipeline input",
    )
    parser.add_argument("--experiment-name", default="breast_cancer_experiment", help="AML experiment name")
    parser.add_argument("--datastore-name", default="adls_gold", help="AML datastore name for ADLS Gen2 gold")
    parser.add_argument("--register-data-asset", action="store_true", help="Register a data asset for portal selection")
    parser.add_argument("--data-asset-name", default="breast_cancer_gold_features", help="Data asset name")
    parser.add_argument("--data-asset-version", default="1", help="Data asset version")
    args = parser.parse_args()

    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    aml_outputs = TERRAFORM_DIR / "15_machine_learning_workspace" / "outputs.json"
    storage_outputs = TERRAFORM_DIR / "03_storage_account" / "outputs.json"

    resource_group = read_outputs_value(rg_outputs, "resource_group_name")
    resource_group_id = read_outputs_value(rg_outputs, "resource_group_id")
    workspace_name = read_outputs_value(aml_outputs, "aml_workspace_name")
    storage_account_name = read_outputs_value(storage_outputs, "storage_account_name")
    storage_account_key = read_outputs_value(storage_outputs, "storage_account_primary_access_key")

    if not resource_group or not resource_group_id or not workspace_name:
        raise RuntimeError("Missing outputs. Ensure RG and AML workspace are deployed.")
    if not storage_account_name or not storage_account_key:
        raise RuntimeError("Missing storage outputs. Ensure the ADLS storage account is deployed.")

    subscription_id = extract_subscription_id(resource_group_id)
    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name,
    )

    # Ensure ADLS Gen2 datastore exists (gold container).
    try:
        ml_client.datastores.get(args.datastore_name)
    except Exception:
        datastore = AzureDataLakeGen2Datastore(
            name=args.datastore_name,
            account_name=storage_account_name,
            filesystem="gold",
            credentials=NoneCredentialConfiguration(),
        )
        ml_client.datastores.create_or_update(datastore)

    if not args.training_data:
        args.training_data = f"azureml://datastores/{args.datastore_name}/paths/breast_cancer/features/"

    if args.register_data_asset:
        try:
            ml_client.data.get(name=args.data_asset_name, version=args.data_asset_version)
            print(f"Data asset already exists: {args.data_asset_name}:{args.data_asset_version}")
        except Exception:
            data_asset = Data(
                name=args.data_asset_name,
                version=args.data_asset_version,
                type="uri_folder",
                path=args.training_data,
            )
            ml_client.data.create_or_update(data_asset)
            print(f"Registered data asset {args.data_asset_name}:{args.data_asset_version}")

    component = ml_client.components.get(name=args.component_name, version=args.component_version)
    pipeline_job = component(
        training_data=Input(type="uri_folder", path=args.training_data),
    )
    pipeline_job.experiment_name = args.experiment_name

    created = ml_client.jobs.create_or_update(pipeline_job)
    print(f"Submitted pipeline job: {created.name}")
    print(f"Studio link: {created.studio_url}")


if __name__ == "__main__":
    main()
