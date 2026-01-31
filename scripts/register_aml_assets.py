import argparse
import json
from pathlib import Path

from azure.ai.ml import MLClient, load_component
from azure.ai.ml.entities import Environment
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


def render_pipeline_yaml(path: Path, replacements: dict) -> str:
    content = path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def main() -> None:
    parser = argparse.ArgumentParser(description="Register AML environment and pipeline assets.")
    parser.add_argument("--env-name", default="mlops-cancer-train-env", help="AML environment name")
    parser.add_argument("--env-version", default="1", help="AML environment version")
    parser.add_argument("--compute-name", default="cpu-cluster", help="AML compute name")
    parser.add_argument("--image-tag", default="0.1.0", help="Training image tag")
    parser.add_argument("--register-pipeline-component", action="store_true", help="Register pipeline component for one-click run in Studio")
    parser.add_argument("--pipeline-component-name", default="breast_cancer_train_pipeline", help="Pipeline component name")
    parser.add_argument("--pipeline-component-version", default="1", help="Pipeline component version")
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
    credential = DefaultAzureCredential()
    ml_client = MLClient(credential, subscription_id=subscription_id, resource_group_name=resource_group, workspace_name=workspace_name)

    image = f"{acr_login_server}/mlops-cancer-train:{args.image_tag}"
    env = Environment(name=args.env_name, version=args.env_version, image=image, description="Training environment")
    ml_client.environments.create_or_update(env)

    pipeline_template = ROOT / "pipelines" / "aml" / "pipeline.yml"
    rendered = render_pipeline_yaml(
        pipeline_template,
        {
            "COMPUTE_NAME": args.compute_name,
            "ENV_NAME": args.env_name,
            "ENV_VERSION": args.env_version,
        },
    )

    rendered_path = ROOT / "pipelines" / "aml" / "pipeline.rendered.yml"
    rendered_path.write_text(rendered, encoding="utf-8")

    print(f"Registered environment {args.env_name}:{args.env_version}")
    print(f"Wrote rendered pipeline YAML to {rendered_path}")
    if args.register_pipeline_component:
        component_template = ROOT / "pipelines" / "aml" / "pipeline.component.yml"
        component_rendered = render_pipeline_yaml(
            component_template,
            {
                "COMPUTE_NAME": args.compute_name,
                "ENV_NAME": args.env_name,
                "ENV_VERSION": args.env_version,
                "COMPONENT_NAME": args.pipeline_component_name,
                "COMPONENT_VERSION": args.pipeline_component_version,
            },
        )
        component_rendered_path = ROOT / "pipelines" / "aml" / "pipeline.component.rendered.yml"
        component_rendered_path.write_text(component_rendered, encoding="utf-8")

        component_name = args.pipeline_component_name.replace("-", "_")
        if component_name != args.pipeline_component_name:
            print(f"Adjusted component name to {component_name} (underscores only).")
        pipeline_component = load_component(component_rendered_path)
        pipeline_component.name = component_name
        ml_client.components.create_or_update(pipeline_component)
        print(f"Registered pipeline component {component_name}:{args.pipeline_component_version}")
        print(f"Wrote rendered pipeline component YAML to {component_rendered_path}")
        print("In AML Studio: Components -> select pipeline -> Create job (Run).")
    else:
        print("Import the YAML in AML Studio and click Run when ready.")


if __name__ == "__main__":
    main()
