import argparse
import json
from pathlib import Path
from uuid import uuid4

from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    CodeConfiguration,
    Environment,
    ManagedOnlineDeployment,
    ManagedOnlineEndpoint,
    Model,
)
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


def get_latest_model_version(ml_client: MLClient, model_name: str) -> str:
    versions = [m.version for m in ml_client.models.list(name=model_name)]
    if not versions:
        raise RuntimeError(f"No models found with name '{model_name}'")
    return sorted(versions, key=lambda v: int(v) if str(v).isdigit() else str(v))[-1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy AML online endpoint with latest model.")
    default_endpoint = f"breast-cancer-endpoint-{uuid4().hex[:6]}"
    parser.add_argument("--endpoint-name", default=default_endpoint, help="Online endpoint name")
    parser.add_argument("--deployment-name", default="blue", help="Deployment name")
    parser.add_argument("--model-name", default="breast-cancer-classifier", help="Registered model name")
    parser.add_argument("--model-version", default=None, help="Model version (defaults to latest)")
    parser.add_argument("--instance-type", default="Standard_DS3_v2", help="VM size for deployment")
    parser.add_argument("--instance-count", type=int, default=1, help="Number of instances")
    parser.add_argument("--image-tag", default="0.1.0", help="Inference image tag")
    args = parser.parse_args()

    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    aml_outputs = TERRAFORM_DIR / "15_machine_learning_workspace" / "outputs.json"
    acr_outputs = TERRAFORM_DIR / "06_container_registry" / "outputs.json"

    resource_group = read_outputs_value(rg_outputs, "resource_group_name")
    resource_group_id = read_outputs_value(rg_outputs, "resource_group_id")
    workspace_name = read_outputs_value(aml_outputs, "aml_workspace_name")
    acr_login_server = read_outputs_value(acr_outputs, "acr_login_server")

    if not resource_group or not resource_group_id or not workspace_name or not acr_login_server:
        raise RuntimeError("Missing outputs. Ensure RG, AML workspace, and ACR are deployed.")

    subscription_id = extract_subscription_id(resource_group_id)
    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name,
    )

    model_version = args.model_version or get_latest_model_version(ml_client, args.model_name)
    model = ml_client.models.get(name=args.model_name, version=model_version)

    env = Environment(
        name="mlops-cancer-inference-env",
        version="1",
        image=f"{acr_login_server}/mlops-cancer-infer:{args.image_tag}",
    )
    ml_client.environments.create_or_update(env)

    endpoint = ManagedOnlineEndpoint(name=args.endpoint_name, auth_mode="key")
    ml_client.online_endpoints.begin_create_or_update(endpoint).result()

    deployment = ManagedOnlineDeployment(
        name=args.deployment_name,
        endpoint_name=args.endpoint_name,
        model=model,
        environment=env,
        code_configuration=CodeConfiguration(
            code=str(ROOT),
            scoring_script="src/inference/score.py",
        ),
        instance_type=args.instance_type,
        instance_count=args.instance_count,
    )
    ml_client.online_deployments.begin_create_or_update(deployment).result()

    ml_client.online_endpoints.begin_update(
        ManagedOnlineEndpoint(name=args.endpoint_name, traffic={args.deployment_name: 100})
    ).result()

    print(f"Endpoint '{args.endpoint_name}' deployed with model {args.model_name}:{model_version}.")


if __name__ == "__main__":
    main()
