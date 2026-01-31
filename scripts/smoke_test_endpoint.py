import argparse
import json
from pathlib import Path
from urllib import request

from azure.ai.ml import MLClient
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
    parser = argparse.ArgumentParser(description="Smoke test AML online endpoint.")
    parser.add_argument("--endpoint-name", default="breast-cancer-endpoint", help="Endpoint name")
    args = parser.parse_args()

    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    aml_outputs = TERRAFORM_DIR / "15_machine_learning_workspace" / "outputs.json"
    resource_group = read_outputs_value(rg_outputs, "resource_group_name")
    resource_group_id = read_outputs_value(rg_outputs, "resource_group_id")
    workspace_name = read_outputs_value(aml_outputs, "aml_workspace_name")

    if not resource_group or not resource_group_id or not workspace_name:
        raise RuntimeError("Missing outputs. Ensure RG and AML workspace are deployed.")

    subscription_id = extract_subscription_id(resource_group_id)
    ml_client = MLClient(
        DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name,
    )

    endpoint = ml_client.online_endpoints.get(args.endpoint_name)
    keys = ml_client.online_endpoints.get_keys(args.endpoint_name)

    sample = {
        "data": [
            {
                "age_mid": 45.0,
                "tumor_size_mid": 20.0,
                "inv_nodes_mid": 2.0,
                "deg_malig_num": 2,
                "node_caps_num": 0,
                "irradiat_num": 0,
                "breast_right": 1,
                "menopause_lt40": 0,
                "menopause_ge40": 1,
                "menopause_premeno": 0,
                "breast_quad_left_up": 0,
                "breast_quad_left_low": 0,
                "breast_quad_right_up": 1,
                "breast_quad_right_low": 0,
                "breast_quad_central": 0,
            }
        ]
    }

    payload = json.dumps(sample).encode("utf-8")
    req = request.Request(endpoint.scoring_uri, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {keys.primary_key}")

    with request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        print(body)


if __name__ == "__main__":
    main()
