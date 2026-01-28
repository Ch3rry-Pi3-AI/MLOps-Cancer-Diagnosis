import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERRAFORM_DIR = ROOT / "terraform"

DEFAULTS = {
    "RESOURCE_GROUP_NAME": None,
    "RESOURCE_GROUP_NAME_PREFIX": "rg-mlops-cancer",
    "LOCATION": "eastus2",
    "VNET_NAME": None,
    "VNET_NAME_PREFIX": "vnet-mlops-cancer",
    "ADDRESS_SPACE": ["10.40.0.0/16"],
    "SUBNET_PREFIXES": {
        "default": "10.40.1.0/24",
        "private_endpoints": "10.40.2.0/24",
        "aml": "10.40.3.0/24",
        "adf": "10.40.4.0/24",
    },
    "STORAGE_ACCOUNT_NAME": None,
    "STORAGE_ACCOUNT_NAME_PREFIX": "stmlopscancer",
    "ACCOUNT_REPLICATION_TYPE": "LRS",
    "ACCOUNT_TIER": "Standard",
    "PUBLIC_NETWORK_ACCESS_ENABLED": True,
    "IS_HNS_ENABLED": True,
    "CONTAINER_NAMES": ["bronze", "silver", "gold"],
    "STORAGE_BLOB_CONTRIBUTOR_OBJECT_ID": None,
    "KEY_VAULT_NAME": None,
    "KEY_VAULT_NAME_PREFIX": "kvmlopscancer",
    "KEY_VAULT_SKU_NAME": "standard",
    "KEY_VAULT_ENABLE_RBAC": True,
    "KEY_VAULT_PUBLIC_NETWORK_ACCESS_ENABLED": True,
    "KEY_VAULT_SOFT_DELETE_RETENTION_DAYS": 7,
    "KEY_VAULT_PURGE_PROTECTION_ENABLED": False,
    "KEY_VAULT_ADMIN_OBJECT_ID": None,
    "LOG_ANALYTICS_NAME": None,
    "LOG_ANALYTICS_NAME_PREFIX": "law-mlops-cancer",
    "LOG_ANALYTICS_SKU": "PerGB2018",
    "LOG_ANALYTICS_RETENTION_IN_DAYS": 30,
    "APP_INSIGHTS_NAME": None,
    "APP_INSIGHTS_NAME_PREFIX": "appi-mlops-cancer",
    "APP_INSIGHTS_APPLICATION_TYPE": "web",
    "ACR_NAME": None,
    "ACR_NAME_PREFIX": "acrmlopscancer",
    "ACR_SKU": "Basic",
    "ACR_ADMIN_ENABLED": False,
    "ACR_PUBLIC_NETWORK_ACCESS_ENABLED": True,
}


def run(cmd, cwd=None):
    print("\n$ " + " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd)


def hcl_value(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        rendered = ", ".join(hcl_value(item) for item in value)
        return f"[{rendered}]"
    if isinstance(value, dict):
        rendered = ", ".join(f"{key} = {hcl_value(val)}" for key, val in value.items())
        return f"{{{rendered}}}"
    escaped = str(value).replace("\"", "\\\"")
    return f"\"{escaped}\""


def write_tfvars(path, items):
    lines = [f"{key} = {hcl_value(value)}" for key, value in items]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_env_file(path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def env_or_default(key, default):
    value = os.environ.get(key)
    if value is None:
        return default
    if value.strip() == "" or value.strip().lower() == "null":
        return None
    if isinstance(default, bool):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y"}:
            return True
        if lowered in {"false", "0", "no", "n"}:
            return False
        raise ValueError(f"Invalid boolean for {key}: {value}")
    if isinstance(default, (list, tuple)):
        items = [item.strip() for item in value.split(",") if item.strip()]
        return items
    if isinstance(default, dict):
        parsed = json.loads(value)
        if not isinstance(parsed, dict):
            raise ValueError(f"Invalid map for {key}: {value}")
        return parsed
    return value


def get_terraform_exe():
    env_path = os.environ.get("TERRAFORM_EXE")
    if env_path:
        return env_path
    exe = shutil.which("terraform")
    if not exe:
        raise RuntimeError("terraform not found on PATH. Set TERRAFORM_EXE or install Terraform.")
    exe_lower = exe.lower()
    if exe_lower.endswith(r"\chocolatey\bin\terraform.exe"):
        candidate = r"C:\ProgramData\chocolatey\lib\terraform\tools\terraform.exe"
        if Path(candidate).exists():
            return candidate
    return exe


def read_outputs_value(outputs_path, key):
    if not outputs_path.exists():
        return None
    data = json.loads(outputs_path.read_text(encoding="utf-8"))
    entry = data.get(key)
    if isinstance(entry, dict) and "value" in entry:
        return entry["value"]
    return None


def write_resource_group_tfvars():
    rg_dir = TERRAFORM_DIR / "01_resource_group"
    write_tfvars(
        rg_dir / "terraform.tfvars",
        [
            ("resource_group_name", env_or_default("RESOURCE_GROUP_NAME", DEFAULTS["RESOURCE_GROUP_NAME"])),
            ("resource_group_name_prefix", env_or_default("RESOURCE_GROUP_NAME_PREFIX", DEFAULTS["RESOURCE_GROUP_NAME_PREFIX"])),
            ("location", env_or_default("LOCATION", DEFAULTS["LOCATION"])),
        ],
    )


def write_storage_account_tfvars():
    storage_dir = TERRAFORM_DIR / "03_storage_account"
    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    rg_name = read_outputs_value(rg_outputs, "resource_group_name")
    rg_location = read_outputs_value(rg_outputs, "resource_group_location")
    resolved_rg_name = env_or_default("RESOURCE_GROUP_NAME", rg_name)
    if not resolved_rg_name:
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Set RESOURCE_GROUP_NAME or keep outputs.json from apply.")
    write_tfvars(
        storage_dir / "terraform.tfvars",
        [
            ("resource_group_name", resolved_rg_name),
            ("location", env_or_default("LOCATION", rg_location)),
            ("storage_account_name", env_or_default("STORAGE_ACCOUNT_NAME", DEFAULTS["STORAGE_ACCOUNT_NAME"])),
            ("storage_account_name_prefix", env_or_default("STORAGE_ACCOUNT_NAME_PREFIX", DEFAULTS["STORAGE_ACCOUNT_NAME_PREFIX"])),
            ("account_replication_type", env_or_default("ACCOUNT_REPLICATION_TYPE", DEFAULTS["ACCOUNT_REPLICATION_TYPE"])),
            ("account_tier", env_or_default("ACCOUNT_TIER", DEFAULTS["ACCOUNT_TIER"])),
            ("public_network_access_enabled", env_or_default("PUBLIC_NETWORK_ACCESS_ENABLED", DEFAULTS["PUBLIC_NETWORK_ACCESS_ENABLED"])),
            ("is_hns_enabled", env_or_default("IS_HNS_ENABLED", DEFAULTS["IS_HNS_ENABLED"])),
            ("container_names", env_or_default("CONTAINER_NAMES", DEFAULTS["CONTAINER_NAMES"])),
            ("storage_blob_contributor_object_id", env_or_default("STORAGE_BLOB_CONTRIBUTOR_OBJECT_ID", DEFAULTS["STORAGE_BLOB_CONTRIBUTOR_OBJECT_ID"])),
        ],
    )


def write_networking_tfvars():
    networking_dir = TERRAFORM_DIR / "02_networking"
    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    rg_name = read_outputs_value(rg_outputs, "resource_group_name")
    rg_location = read_outputs_value(rg_outputs, "resource_group_location")
    resolved_rg_name = env_or_default("RESOURCE_GROUP_NAME", rg_name)
    if not resolved_rg_name:
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Set RESOURCE_GROUP_NAME or keep outputs.json from apply.")
    write_tfvars(
        networking_dir / "terraform.tfvars",
        [
            ("resource_group_name", resolved_rg_name),
            ("location", env_or_default("LOCATION", rg_location)),
            ("vnet_name", env_or_default("VNET_NAME", DEFAULTS["VNET_NAME"])),
            ("vnet_name_prefix", env_or_default("VNET_NAME_PREFIX", DEFAULTS["VNET_NAME_PREFIX"])),
            ("address_space", env_or_default("ADDRESS_SPACE", DEFAULTS["ADDRESS_SPACE"])),
            ("subnet_prefixes", env_or_default("SUBNET_PREFIXES", DEFAULTS["SUBNET_PREFIXES"])),
        ],
    )


def write_key_vault_tfvars():
    kv_dir = TERRAFORM_DIR / "04_key_vault"
    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    rg_name = read_outputs_value(rg_outputs, "resource_group_name")
    rg_location = read_outputs_value(rg_outputs, "resource_group_location")
    resolved_rg_name = env_or_default("RESOURCE_GROUP_NAME", rg_name)
    if not resolved_rg_name:
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Set RESOURCE_GROUP_NAME or keep outputs.json from apply.")
    write_tfvars(
        kv_dir / "terraform.tfvars",
        [
            ("resource_group_name", resolved_rg_name),
            ("location", env_or_default("LOCATION", rg_location)),
            ("key_vault_name", env_or_default("KEY_VAULT_NAME", DEFAULTS["KEY_VAULT_NAME"])),
            ("key_vault_name_prefix", env_or_default("KEY_VAULT_NAME_PREFIX", DEFAULTS["KEY_VAULT_NAME_PREFIX"])),
            ("sku_name", env_or_default("KEY_VAULT_SKU_NAME", DEFAULTS["KEY_VAULT_SKU_NAME"])),
            ("enable_rbac_authorization", env_or_default("KEY_VAULT_ENABLE_RBAC", DEFAULTS["KEY_VAULT_ENABLE_RBAC"])),
            ("public_network_access_enabled", env_or_default("KEY_VAULT_PUBLIC_NETWORK_ACCESS_ENABLED", DEFAULTS["KEY_VAULT_PUBLIC_NETWORK_ACCESS_ENABLED"])),
            ("soft_delete_retention_days", env_or_default("KEY_VAULT_SOFT_DELETE_RETENTION_DAYS", DEFAULTS["KEY_VAULT_SOFT_DELETE_RETENTION_DAYS"])),
            ("purge_protection_enabled", env_or_default("KEY_VAULT_PURGE_PROTECTION_ENABLED", DEFAULTS["KEY_VAULT_PURGE_PROTECTION_ENABLED"])),
            ("key_vault_admin_object_id", env_or_default("KEY_VAULT_ADMIN_OBJECT_ID", DEFAULTS["KEY_VAULT_ADMIN_OBJECT_ID"])),
        ],
    )


def write_log_analytics_tfvars():
    obs_dir = TERRAFORM_DIR / "05_log_analytics_app_insights"
    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    rg_name = read_outputs_value(rg_outputs, "resource_group_name")
    rg_location = read_outputs_value(rg_outputs, "resource_group_location")
    resolved_rg_name = env_or_default("RESOURCE_GROUP_NAME", rg_name)
    if not resolved_rg_name:
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Set RESOURCE_GROUP_NAME or keep outputs.json from apply.")
    write_tfvars(
        obs_dir / "terraform.tfvars",
        [
            ("resource_group_name", resolved_rg_name),
            ("location", env_or_default("LOCATION", rg_location)),
            ("log_analytics_name", env_or_default("LOG_ANALYTICS_NAME", DEFAULTS["LOG_ANALYTICS_NAME"])),
            ("log_analytics_name_prefix", env_or_default("LOG_ANALYTICS_NAME_PREFIX", DEFAULTS["LOG_ANALYTICS_NAME_PREFIX"])),
            ("sku", env_or_default("LOG_ANALYTICS_SKU", DEFAULTS["LOG_ANALYTICS_SKU"])),
            ("retention_in_days", env_or_default("LOG_ANALYTICS_RETENTION_IN_DAYS", DEFAULTS["LOG_ANALYTICS_RETENTION_IN_DAYS"])),
            ("app_insights_name", env_or_default("APP_INSIGHTS_NAME", DEFAULTS["APP_INSIGHTS_NAME"])),
            ("app_insights_name_prefix", env_or_default("APP_INSIGHTS_NAME_PREFIX", DEFAULTS["APP_INSIGHTS_NAME_PREFIX"])),
            ("application_type", env_or_default("APP_INSIGHTS_APPLICATION_TYPE", DEFAULTS["APP_INSIGHTS_APPLICATION_TYPE"])),
        ],
    )


def write_acr_tfvars():
    acr_dir = TERRAFORM_DIR / "06_container_registry"
    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    rg_name = read_outputs_value(rg_outputs, "resource_group_name")
    rg_location = read_outputs_value(rg_outputs, "resource_group_location")
    resolved_rg_name = env_or_default("RESOURCE_GROUP_NAME", rg_name)
    if not resolved_rg_name:
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Set RESOURCE_GROUP_NAME or keep outputs.json from apply.")
    write_tfvars(
        acr_dir / "terraform.tfvars",
        [
            ("resource_group_name", resolved_rg_name),
            ("location", env_or_default("LOCATION", rg_location)),
            ("acr_name", env_or_default("ACR_NAME", DEFAULTS["ACR_NAME"])),
            ("acr_name_prefix", env_or_default("ACR_NAME_PREFIX", DEFAULTS["ACR_NAME_PREFIX"])),
            ("sku", env_or_default("ACR_SKU", DEFAULTS["ACR_SKU"])),
            ("admin_enabled", env_or_default("ACR_ADMIN_ENABLED", DEFAULTS["ACR_ADMIN_ENABLED"])),
            ("public_network_access_enabled", env_or_default("ACR_PUBLIC_NETWORK_ACCESS_ENABLED", DEFAULTS["ACR_PUBLIC_NETWORK_ACCESS_ENABLED"])),
        ],
    )


def terraform_destroy(module_dir):
    terraform_exe = get_terraform_exe()
    run([terraform_exe, "init", "-upgrade"], cwd=module_dir)
    run([terraform_exe, "destroy", "-auto-approve"], cwd=module_dir)


def cleanup_outputs(module_dir):
    outputs_path = module_dir / "outputs.json"
    if outputs_path.exists():
        outputs_path.unlink()


def main():
    parser = argparse.ArgumentParser(description="Destroy Terraform resources for the MLOps project.")
    parser.add_argument("--rg-only", action="store_true", help="Destroy only the resource group")
    parser.add_argument("--networking-only", action="store_true", help="Destroy only the networking resources")
    parser.add_argument("--storage-only", action="store_true", help="Destroy only the storage account")
    parser.add_argument("--keyvault-only", action="store_true", help="Destroy only the key vault")
    parser.add_argument("--observability-only", action="store_true", help="Destroy only Log Analytics + App Insights")
    parser.add_argument("--acr-only", action="store_true", help="Destroy only the container registry")
    args = parser.parse_args()

    load_env_file(ROOT / ".env")

    modules = [
        TERRAFORM_DIR / "06_container_registry",
        TERRAFORM_DIR / "05_log_analytics_app_insights",
        TERRAFORM_DIR / "04_key_vault",
        TERRAFORM_DIR / "03_storage_account",
        TERRAFORM_DIR / "02_networking",
        TERRAFORM_DIR / "01_resource_group",
    ]
    if args.rg_only:
        modules = [TERRAFORM_DIR / "01_resource_group"]
    if args.networking_only:
        modules = [TERRAFORM_DIR / "02_networking"]
    if args.storage_only:
        modules = [TERRAFORM_DIR / "03_storage_account"]
    if args.keyvault_only:
        modules = [TERRAFORM_DIR / "04_key_vault"]
    if args.observability_only:
        modules = [TERRAFORM_DIR / "05_log_analytics_app_insights"]
    if args.acr_only:
        modules = [TERRAFORM_DIR / "06_container_registry"]

    for module_dir in modules:
        if module_dir.name == "05_log_analytics_app_insights":
            write_log_analytics_tfvars()
        if module_dir.name == "04_key_vault":
            write_key_vault_tfvars()
        if module_dir.name == "06_container_registry":
            write_acr_tfvars()
        if module_dir.name == "03_storage_account":
            write_storage_account_tfvars()
        if module_dir.name == "02_networking":
            write_networking_tfvars()
        if module_dir.name == "01_resource_group":
            write_resource_group_tfvars()
        terraform_destroy(module_dir)
        cleanup_outputs(module_dir)


if __name__ == "__main__":
    main()
