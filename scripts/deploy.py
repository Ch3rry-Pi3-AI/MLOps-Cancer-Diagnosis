import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERRAFORM_DIR = ROOT / "terraform"

DEFAULTS = {
    "BACKEND_RESOURCE_GROUP_NAME": None,
    "BACKEND_RESOURCE_GROUP_NAME_PREFIX": "rg-mlops-cancer-tfstate",
    "BACKEND_STORAGE_ACCOUNT_NAME": None,
    "BACKEND_STORAGE_ACCOUNT_NAME_PREFIX": "stmlopstfstate",
    "BACKEND_CONTAINER_NAME": "tfstate",
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
    "ACR_ADMIN_ENABLED": True,
    "ACR_PUBLIC_NETWORK_ACCESS_ENABLED": True,
    "DATA_FACTORY_NAME": None,
    "DATA_FACTORY_NAME_PREFIX": "adf-mlops-cancer",
    "HTTP_LINKED_SERVICE_NAME": None,
    "HTTP_LINKED_SERVICE_NAME_PREFIX": "ls-http-mlops-cancer",
    "HTTP_BASE_URL": "https://raw.githubusercontent.com",
    "HTTP_AUTHENTICATION_TYPE": "Anonymous",
    "HTTP_ENABLE_CERTIFICATE_VALIDATION": True,
    "INTEGRATION_RUNTIME_NAME": None,
    "ADLS_LINKED_SERVICE_NAME": None,
    "ADLS_LINKED_SERVICE_NAME_PREFIX": "ls-adls-mlops-cancer",
    "LINKED_SERVICE_DESCRIPTION": "Linked services for HTTP source and ADLS Gen2 sink",
    "ADF_PIPELINE_NAME": None,
    "ADF_PIPELINE_NAME_PREFIX": "pl-mlops-cancer-http",
    "HTTP_DATASET_NAME": None,
    "HTTP_DATASET_NAME_PREFIX": "ds_http_mlopscancer",
    "SINK_DATASET_NAME": None,
    "SINK_DATASET_NAME_PREFIX": "ds_adls_bronze_mlopscancer",
    "HTTP_RELATIVE_URL": "Ch3rry-Pi3-AI/MLOps-Cancer-Diagnosis/refs/heads/main/data/breast-cancer.data",
    "SINK_FILE_SYSTEM": "bronze",
    "SINK_FOLDER": "breast_cancer/raw",
    "SINK_FILE": "breast_cancer.csv",
    "ADF_DATAFLOW_NAME": None,
    "ADF_DATAFLOW_NAME_PREFIX": "df-mlops-cancer-bronze-silver",
    "BRONZE_SOURCE_DATASET_NAME": None,
    "BRONZE_SOURCE_DATASET_NAME_PREFIX": "ds_bronze_mlopscancer",
    "BRONZE_SOURCE_CONTAINER": "bronze",
    "BRONZE_SOURCE_FOLDER": "breast_cancer/raw",
    "BRONZE_SOURCE_FILE": "breast_cancer.csv",
    "SILVER_SINK_CONTAINER": "silver",
    "SILVER_SINK_FOLDER": "breast_cancer/clean",
    "SILVER_SINK_FORMAT": "parquet",
    "ADF_SILVER_PIPELINE_NAME": None,
    "ADF_SILVER_PIPELINE_NAME_PREFIX": "pl-mlops-cancer-silver-dataflow",
    "ADF_DATAFLOW_COMPUTE_TYPE": "General",
    "ADF_DATAFLOW_CORE_COUNT": 8,
    "ADF_DATAFLOW_TRACE_LEVEL": "None",
    "ADF_GOLD_DATAFLOW_NAME": None,
    "ADF_GOLD_DATAFLOW_NAME_PREFIX": "df-mlops-cancer-silver-gold",
    "SILVER_SOURCE_DATASET_NAME": None,
    "SILVER_SOURCE_DATASET_NAME_PREFIX": "ds_silver_mlopscancer",
    "SILVER_SOURCE_CONTAINER": "silver",
    "SILVER_SOURCE_FOLDER": "breast_cancer/clean",
    "GOLD_SINK_CONTAINER": "gold",
    "GOLD_SINK_FOLDER": "breast_cancer/features",
    "GOLD_SINK_FORMAT": "parquet",
    "ADF_GOLD_PIPELINE_NAME": None,
    "ADF_GOLD_PIPELINE_NAME_PREFIX": "pl-mlops-cancer-gold-dataflow",
    "ADF_MASTER_PIPELINE_NAME": None,
    "ADF_MASTER_PIPELINE_NAME_PREFIX": "pl-mlops-cancer-master",
    "AML_WORKSPACE_NAME": None,
    "AML_WORKSPACE_NAME_PREFIX": "mlw-mlops-cancer",
    "AML_PUBLIC_NETWORK_ACCESS_ENABLED": True,
    "AML_STORAGE_ACCOUNT_NAME": None,
    "AML_STORAGE_ACCOUNT_NAME_PREFIX": "stmlopscancerml",
    "AML_STORAGE_ACCOUNT_REPLICATION_TYPE": "LRS",
    "AML_STORAGE_ACCOUNT_TIER": "Standard",
    "AML_STORAGE_PUBLIC_NETWORK_ACCESS_ENABLED": True,
    "AML_COMPUTE_NAME": "cpu-cluster",
    "AML_TRAIN_IMAGE_TAG": "0.1.0",
    "AML_COMPUTE_VM_SIZE": "Standard_DS3_v2",
    "AML_COMPUTE_VM_PRIORITY": "Dedicated",
    "AML_COMPUTE_MIN_INSTANCES": 0,
    "AML_COMPUTE_MAX_INSTANCES": 2,
    "AML_COMPUTE_IDLE_TIME": "PT2M",
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


def get_az_cmd():
    az_cmd = shutil.which("az")
    if az_cmd:
        return az_cmd
    candidates = [
        r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
        r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    raise RuntimeError("Azure CLI not found. Install az CLI or add it to PATH.")


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


def write_backend_tfvars():
    backend_dir = TERRAFORM_DIR / "00_backend"
    container_name = env_or_default("BACKEND_CONTAINER_NAME", DEFAULTS["BACKEND_CONTAINER_NAME"])
    if container_name is None:
        container_name = DEFAULTS["BACKEND_CONTAINER_NAME"]
    backend_rg, backend_storage = resolve_backend_names()
    write_tfvars(
        backend_dir / "terraform.tfvars",
        [
            ("backend_resource_group_name", backend_rg),
            ("backend_resource_group_name_prefix", env_or_default("BACKEND_RESOURCE_GROUP_NAME_PREFIX", DEFAULTS["BACKEND_RESOURCE_GROUP_NAME_PREFIX"])),
            ("location", env_or_default("LOCATION", DEFAULTS["LOCATION"])),
            ("storage_account_name", backend_storage),
            ("storage_account_name_prefix", env_or_default("BACKEND_STORAGE_ACCOUNT_NAME_PREFIX", DEFAULTS["BACKEND_STORAGE_ACCOUNT_NAME_PREFIX"])),
            ("container_name", container_name),
        ],
    )


def resolve_backend_names():
    explicit_rg = env_or_default("BACKEND_RESOURCE_GROUP_NAME", DEFAULTS["BACKEND_RESOURCE_GROUP_NAME"])
    explicit_storage = env_or_default("BACKEND_STORAGE_ACCOUNT_NAME", DEFAULTS["BACKEND_STORAGE_ACCOUNT_NAME"])
    if explicit_rg and explicit_storage:
        return explicit_rg, explicit_storage
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    if not subscription_id:
        raise RuntimeError("AZURE_SUBSCRIPTION_ID must be set to compute backend names.")
    sub_compact = subscription_id.replace("-", "")
    suffix = sub_compact[-6:]
    rg_name = f"{DEFAULTS['BACKEND_RESOURCE_GROUP_NAME_PREFIX']}-{suffix}"
    storage_name = f"{DEFAULTS['BACKEND_STORAGE_ACCOUNT_NAME_PREFIX']}{suffix}"
    return rg_name, storage_name


def ensure_backend_container(backend_rg, backend_storage, container_name):
    az_cmd = get_az_cmd()
    key = subprocess.check_output(
        [
            az_cmd,
            "storage",
            "account",
            "keys",
            "list",
            "--resource-group",
            backend_rg,
            "--account-name",
            backend_storage,
            "--query",
            "[0].value",
            "-o",
            "tsv",
        ],
        text=True,
    ).strip()
    if not key:
        raise RuntimeError("Unable to read storage account key for backend.")
    run(
        [
            az_cmd,
            "storage",
            "container",
            "create",
            "--name",
            container_name,
            "--account-name",
            backend_storage,
            "--account-key",
            key,
        ]
    )


def backend_resource_group_exists(backend_rg):
    az_cmd = get_az_cmd()
    try:
        subprocess.check_output([az_cmd, "group", "show", "--name", backend_rg], text=True)
        return True
    except subprocess.CalledProcessError:
        return False


def backend_storage_exists(backend_rg, backend_storage):
    az_cmd = get_az_cmd()
    try:
        subprocess.check_output(
            [az_cmd, "storage", "account", "show", "--resource-group", backend_rg, "--name", backend_storage],
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def write_backend_outputs_from_env(backend_rg, backend_storage, backend_container):
    outputs = {
        "backend_resource_group_name": {"value": backend_rg},
        "backend_storage_account_name": {"value": backend_storage},
        "backend_container_name": {"value": backend_container},
    }
    outputs_path = TERRAFORM_DIR / "00_backend" / "outputs.json"
    outputs_path.write_text(json.dumps(outputs, indent=2) + "\n", encoding="utf-8")


def write_storage_account_tfvars():
    storage_dir = TERRAFORM_DIR / "03_storage_account"
    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    rg_name = read_outputs_value(rg_outputs, "resource_group_name")
    rg_location = read_outputs_value(rg_outputs, "resource_group_location")
    resolved_rg_name = env_or_default("RESOURCE_GROUP_NAME", rg_name)
    if not resolved_rg_name:
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Deploy the resource group first or set RESOURCE_GROUP_NAME.")
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
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Deploy the resource group first or set RESOURCE_GROUP_NAME.")
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
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Deploy the resource group first or set RESOURCE_GROUP_NAME.")
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
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Deploy the resource group first or set RESOURCE_GROUP_NAME.")
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
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Deploy the resource group first or set RESOURCE_GROUP_NAME.")
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


def write_data_factory_tfvars():
    adf_dir = TERRAFORM_DIR / "07_data_factory"
    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    rg_name = read_outputs_value(rg_outputs, "resource_group_name")
    rg_location = read_outputs_value(rg_outputs, "resource_group_location")
    resolved_rg_name = env_or_default("RESOURCE_GROUP_NAME", rg_name)
    if not resolved_rg_name:
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Deploy the resource group first or set RESOURCE_GROUP_NAME.")
    write_tfvars(
        adf_dir / "terraform.tfvars",
        [
            ("resource_group_name", resolved_rg_name),
            ("location", env_or_default("LOCATION", rg_location)),
            ("data_factory_name", env_or_default("DATA_FACTORY_NAME", DEFAULTS["DATA_FACTORY_NAME"])),
            ("data_factory_name_prefix", env_or_default("DATA_FACTORY_NAME_PREFIX", DEFAULTS["DATA_FACTORY_NAME_PREFIX"])),
        ],
    )


def write_adf_linked_services_tfvars():
    ls_dir = TERRAFORM_DIR / "08_adf_linked_services"
    adf_outputs = TERRAFORM_DIR / "07_data_factory" / "outputs.json"
    storage_outputs = TERRAFORM_DIR / "03_storage_account" / "outputs.json"
    data_factory_id = read_outputs_value(adf_outputs, "data_factory_id")
    storage_dfs_endpoint = read_outputs_value(storage_outputs, "primary_dfs_endpoint")
    storage_key = read_outputs_value(storage_outputs, "storage_account_primary_access_key")
    if not data_factory_id:
        raise RuntimeError("data_factory_id not found. Deploy the data factory first.")
    if not storage_dfs_endpoint or not storage_key:
        raise RuntimeError("Storage outputs not found. Deploy the storage account first.")
    write_tfvars(
        ls_dir / "terraform.tfvars",
        [
            ("data_factory_id", data_factory_id),
            ("http_linked_service_name", env_or_default("HTTP_LINKED_SERVICE_NAME", DEFAULTS["HTTP_LINKED_SERVICE_NAME"])),
            ("http_linked_service_name_prefix", env_or_default("HTTP_LINKED_SERVICE_NAME_PREFIX", DEFAULTS["HTTP_LINKED_SERVICE_NAME_PREFIX"])),
            ("http_base_url", env_or_default("HTTP_BASE_URL", DEFAULTS["HTTP_BASE_URL"])),
            ("http_authentication_type", env_or_default("HTTP_AUTHENTICATION_TYPE", DEFAULTS["HTTP_AUTHENTICATION_TYPE"])),
            ("http_enable_certificate_validation", env_or_default("HTTP_ENABLE_CERTIFICATE_VALIDATION", DEFAULTS["HTTP_ENABLE_CERTIFICATE_VALIDATION"])),
            ("integration_runtime_name", env_or_default("INTEGRATION_RUNTIME_NAME", DEFAULTS["INTEGRATION_RUNTIME_NAME"])),
            ("adls_linked_service_name", env_or_default("ADLS_LINKED_SERVICE_NAME", DEFAULTS["ADLS_LINKED_SERVICE_NAME"])),
            ("adls_linked_service_name_prefix", env_or_default("ADLS_LINKED_SERVICE_NAME_PREFIX", DEFAULTS["ADLS_LINKED_SERVICE_NAME_PREFIX"])),
            ("storage_dfs_endpoint", storage_dfs_endpoint),
            ("storage_account_key", storage_key),
            ("description", env_or_default("LINKED_SERVICE_DESCRIPTION", DEFAULTS["LINKED_SERVICE_DESCRIPTION"])),
        ],
    )


def write_adf_pipeline_http_tfvars():
    pipeline_dir = TERRAFORM_DIR / "09_adf_pipeline_http"
    adf_outputs = TERRAFORM_DIR / "07_data_factory" / "outputs.json"
    ls_outputs = TERRAFORM_DIR / "08_adf_linked_services" / "outputs.json"
    data_factory_id = read_outputs_value(adf_outputs, "data_factory_id")
    http_linked_service_name = read_outputs_value(ls_outputs, "http_linked_service_name")
    adls_linked_service_name = read_outputs_value(ls_outputs, "adls_linked_service_name")
    if not data_factory_id:
        raise RuntimeError("data_factory_id not found. Deploy the data factory first.")
    if not http_linked_service_name or not adls_linked_service_name:
        raise RuntimeError("Linked service outputs not found. Deploy linked services first.")
    write_tfvars(
        pipeline_dir / "terraform.tfvars",
        [
            ("data_factory_id", data_factory_id),
            ("http_linked_service_name", http_linked_service_name),
            ("adls_linked_service_name", adls_linked_service_name),
            ("pipeline_name", env_or_default("ADF_PIPELINE_NAME", DEFAULTS["ADF_PIPELINE_NAME"])),
            ("pipeline_name_prefix", env_or_default("ADF_PIPELINE_NAME_PREFIX", DEFAULTS["ADF_PIPELINE_NAME_PREFIX"])),
            ("http_dataset_name", env_or_default("HTTP_DATASET_NAME", DEFAULTS["HTTP_DATASET_NAME"])),
            ("http_dataset_name_prefix", env_or_default("HTTP_DATASET_NAME_PREFIX", DEFAULTS["HTTP_DATASET_NAME_PREFIX"])),
            ("sink_dataset_name", env_or_default("SINK_DATASET_NAME", DEFAULTS["SINK_DATASET_NAME"])),
            ("sink_dataset_name_prefix", env_or_default("SINK_DATASET_NAME_PREFIX", DEFAULTS["SINK_DATASET_NAME_PREFIX"])),
            ("http_relative_url", env_or_default("HTTP_RELATIVE_URL", DEFAULTS["HTTP_RELATIVE_URL"])),
            ("sink_file_system", env_or_default("SINK_FILE_SYSTEM", DEFAULTS["SINK_FILE_SYSTEM"])),
            ("sink_folder", env_or_default("SINK_FOLDER", DEFAULTS["SINK_FOLDER"])),
            ("sink_file", env_or_default("SINK_FILE", DEFAULTS["SINK_FILE"])),
        ],
    )


def write_adf_dataflow_tfvars():
    dataflow_dir = TERRAFORM_DIR / "10_adf_dataflow_bronze_silver"
    adf_outputs = TERRAFORM_DIR / "07_data_factory" / "outputs.json"
    ls_outputs = TERRAFORM_DIR / "08_adf_linked_services" / "outputs.json"
    data_factory_id = read_outputs_value(adf_outputs, "data_factory_id")
    adls_linked_service_name = read_outputs_value(ls_outputs, "adls_linked_service_name")
    if not data_factory_id:
        raise RuntimeError("data_factory_id not found. Deploy the data factory first.")
    if not adls_linked_service_name:
        raise RuntimeError("ADLS linked service not found. Deploy linked services first.")
    write_tfvars(
        dataflow_dir / "terraform.tfvars",
        [
            ("data_factory_id", data_factory_id),
            ("adls_linked_service_name", adls_linked_service_name),
            ("dataflow_name", env_or_default("ADF_DATAFLOW_NAME", DEFAULTS["ADF_DATAFLOW_NAME"])),
            ("dataflow_name_prefix", env_or_default("ADF_DATAFLOW_NAME_PREFIX", DEFAULTS["ADF_DATAFLOW_NAME_PREFIX"])),
            ("bronze_source_dataset_name", env_or_default("BRONZE_SOURCE_DATASET_NAME", DEFAULTS["BRONZE_SOURCE_DATASET_NAME"])),
            ("bronze_source_dataset_name_prefix", env_or_default("BRONZE_SOURCE_DATASET_NAME_PREFIX", DEFAULTS["BRONZE_SOURCE_DATASET_NAME_PREFIX"])),
            ("source_container", env_or_default("BRONZE_SOURCE_CONTAINER", DEFAULTS["BRONZE_SOURCE_CONTAINER"])),
            ("source_folder", env_or_default("BRONZE_SOURCE_FOLDER", DEFAULTS["BRONZE_SOURCE_FOLDER"])),
            ("source_file", env_or_default("BRONZE_SOURCE_FILE", DEFAULTS["BRONZE_SOURCE_FILE"])),
            ("sink_container", env_or_default("SILVER_SINK_CONTAINER", DEFAULTS["SILVER_SINK_CONTAINER"])),
            ("sink_folder", env_or_default("SILVER_SINK_FOLDER", DEFAULTS["SILVER_SINK_FOLDER"])),
            ("sink_format", env_or_default("SILVER_SINK_FORMAT", DEFAULTS["SILVER_SINK_FORMAT"])),
        ],
    )


def write_adf_pipeline_silver_tfvars():
    pipeline_dir = TERRAFORM_DIR / "11_adf_pipeline_silver_dataflow"
    adf_outputs = TERRAFORM_DIR / "07_data_factory" / "outputs.json"
    dataflow_outputs = TERRAFORM_DIR / "10_adf_dataflow_bronze_silver" / "outputs.json"
    data_factory_id = read_outputs_value(adf_outputs, "data_factory_id")
    dataflow_name = read_outputs_value(dataflow_outputs, "dataflow_name")
    if not data_factory_id:
        raise RuntimeError("data_factory_id not found. Deploy the data factory first.")
    if not dataflow_name:
        raise RuntimeError("dataflow_name not found. Deploy the data flow first.")
    write_tfvars(
        pipeline_dir / "terraform.tfvars",
        [
            ("data_factory_id", data_factory_id),
            ("dataflow_name", dataflow_name),
            ("pipeline_name", env_or_default("ADF_SILVER_PIPELINE_NAME", DEFAULTS["ADF_SILVER_PIPELINE_NAME"])),
            ("pipeline_name_prefix", env_or_default("ADF_SILVER_PIPELINE_NAME_PREFIX", DEFAULTS["ADF_SILVER_PIPELINE_NAME_PREFIX"])),
            ("compute_type", env_or_default("ADF_DATAFLOW_COMPUTE_TYPE", DEFAULTS["ADF_DATAFLOW_COMPUTE_TYPE"])),
            ("core_count", env_or_default("ADF_DATAFLOW_CORE_COUNT", DEFAULTS["ADF_DATAFLOW_CORE_COUNT"])),
            ("trace_level", env_or_default("ADF_DATAFLOW_TRACE_LEVEL", DEFAULTS["ADF_DATAFLOW_TRACE_LEVEL"])),
        ],
    )


def write_adf_dataflow_gold_tfvars():
    dataflow_dir = TERRAFORM_DIR / "12_adf_dataflow_silver_gold"
    adf_outputs = TERRAFORM_DIR / "07_data_factory" / "outputs.json"
    ls_outputs = TERRAFORM_DIR / "08_adf_linked_services" / "outputs.json"
    data_factory_id = read_outputs_value(adf_outputs, "data_factory_id")
    adls_linked_service_name = read_outputs_value(ls_outputs, "adls_linked_service_name")
    if not data_factory_id:
        raise RuntimeError("data_factory_id not found. Deploy the data factory first.")
    if not adls_linked_service_name:
        raise RuntimeError("ADLS linked service not found. Deploy linked services first.")
    write_tfvars(
        dataflow_dir / "terraform.tfvars",
        [
            ("data_factory_id", data_factory_id),
            ("adls_linked_service_name", adls_linked_service_name),
            ("dataflow_name", env_or_default("ADF_GOLD_DATAFLOW_NAME", DEFAULTS["ADF_GOLD_DATAFLOW_NAME"])),
            ("dataflow_name_prefix", env_or_default("ADF_GOLD_DATAFLOW_NAME_PREFIX", DEFAULTS["ADF_GOLD_DATAFLOW_NAME_PREFIX"])),
            ("silver_source_dataset_name", env_or_default("SILVER_SOURCE_DATASET_NAME", DEFAULTS["SILVER_SOURCE_DATASET_NAME"])),
            ("silver_source_dataset_name_prefix", env_or_default("SILVER_SOURCE_DATASET_NAME_PREFIX", DEFAULTS["SILVER_SOURCE_DATASET_NAME_PREFIX"])),
            ("source_container", env_or_default("SILVER_SOURCE_CONTAINER", DEFAULTS["SILVER_SOURCE_CONTAINER"])),
            ("source_folder", env_or_default("SILVER_SOURCE_FOLDER", DEFAULTS["SILVER_SOURCE_FOLDER"])),
            ("sink_container", env_or_default("GOLD_SINK_CONTAINER", DEFAULTS["GOLD_SINK_CONTAINER"])),
            ("sink_folder", env_or_default("GOLD_SINK_FOLDER", DEFAULTS["GOLD_SINK_FOLDER"])),
            ("sink_format", env_or_default("GOLD_SINK_FORMAT", DEFAULTS["GOLD_SINK_FORMAT"])),
        ],
    )


def write_adf_pipeline_gold_tfvars():
    pipeline_dir = TERRAFORM_DIR / "13_adf_pipeline_gold_dataflow"
    adf_outputs = TERRAFORM_DIR / "07_data_factory" / "outputs.json"
    dataflow_outputs = TERRAFORM_DIR / "12_adf_dataflow_silver_gold" / "outputs.json"
    data_factory_id = read_outputs_value(adf_outputs, "data_factory_id")
    dataflow_name = read_outputs_value(dataflow_outputs, "dataflow_name")
    if not data_factory_id:
        raise RuntimeError("data_factory_id not found. Deploy the data factory first.")
    if not dataflow_name:
        raise RuntimeError("dataflow_name not found. Deploy the data flow first.")
    write_tfvars(
        pipeline_dir / "terraform.tfvars",
        [
            ("data_factory_id", data_factory_id),
            ("dataflow_name", dataflow_name),
            ("pipeline_name", env_or_default("ADF_GOLD_PIPELINE_NAME", DEFAULTS["ADF_GOLD_PIPELINE_NAME"])),
            ("pipeline_name_prefix", env_or_default("ADF_GOLD_PIPELINE_NAME_PREFIX", DEFAULTS["ADF_GOLD_PIPELINE_NAME_PREFIX"])),
            ("compute_type", env_or_default("ADF_DATAFLOW_COMPUTE_TYPE", DEFAULTS["ADF_DATAFLOW_COMPUTE_TYPE"])),
            ("core_count", env_or_default("ADF_DATAFLOW_CORE_COUNT", DEFAULTS["ADF_DATAFLOW_CORE_COUNT"])),
            ("trace_level", env_or_default("ADF_DATAFLOW_TRACE_LEVEL", DEFAULTS["ADF_DATAFLOW_TRACE_LEVEL"])),
        ],
    )


def write_adf_pipeline_master_tfvars():
    pipeline_dir = TERRAFORM_DIR / "14_adf_pipeline_master"
    adf_outputs = TERRAFORM_DIR / "07_data_factory" / "outputs.json"
    ingest_outputs = TERRAFORM_DIR / "09_adf_pipeline_http" / "outputs.json"
    silver_outputs = TERRAFORM_DIR / "11_adf_pipeline_silver_dataflow" / "outputs.json"
    gold_outputs = TERRAFORM_DIR / "13_adf_pipeline_gold_dataflow" / "outputs.json"
    data_factory_id = read_outputs_value(adf_outputs, "data_factory_id")
    ingest_name = read_outputs_value(ingest_outputs, "pipeline_name")
    silver_name = read_outputs_value(silver_outputs, "pipeline_name")
    gold_name = read_outputs_value(gold_outputs, "pipeline_name")
    if not data_factory_id:
        raise RuntimeError("data_factory_id not found. Deploy the data factory first.")
    if not ingest_name or not silver_name or not gold_name:
        raise RuntimeError("Pipeline outputs not found. Deploy ingest/silver/gold pipelines first.")
    write_tfvars(
        pipeline_dir / "terraform.tfvars",
        [
            ("data_factory_id", data_factory_id),
            ("pipeline_name", env_or_default("ADF_MASTER_PIPELINE_NAME", DEFAULTS["ADF_MASTER_PIPELINE_NAME"])),
            ("pipeline_name_prefix", env_or_default("ADF_MASTER_PIPELINE_NAME_PREFIX", DEFAULTS["ADF_MASTER_PIPELINE_NAME_PREFIX"])),
            ("ingest_pipeline_name", ingest_name),
            ("silver_pipeline_name", silver_name),
            ("gold_pipeline_name", gold_name),
        ],
    )


def write_aml_workspace_tfvars():
    aml_dir = TERRAFORM_DIR / "15_machine_learning_workspace"
    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    aml_storage_outputs = TERRAFORM_DIR / "16_aml_storage_account" / "outputs.json"
    kv_outputs = TERRAFORM_DIR / "04_key_vault" / "outputs.json"
    obs_outputs = TERRAFORM_DIR / "05_log_analytics_app_insights" / "outputs.json"
    acr_outputs = TERRAFORM_DIR / "06_container_registry" / "outputs.json"
    rg_name = read_outputs_value(rg_outputs, "resource_group_name")
    rg_location = read_outputs_value(rg_outputs, "resource_group_location")
    storage_id = read_outputs_value(aml_storage_outputs, "storage_account_id")
    kv_id = read_outputs_value(kv_outputs, "key_vault_id")
    appi_id = read_outputs_value(obs_outputs, "app_insights_id")
    acr_id = read_outputs_value(acr_outputs, "acr_id")
    resolved_rg_name = env_or_default("RESOURCE_GROUP_NAME", rg_name)
    if not resolved_rg_name:
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Deploy the resource group first or set RESOURCE_GROUP_NAME.")
    if not storage_id or not kv_id or not appi_id or not acr_id:
        raise RuntimeError("Missing dependency outputs. Deploy AML storage, key vault, app insights, and ACR first.")
    write_tfvars(
        aml_dir / "terraform.tfvars",
        [
            ("resource_group_name", resolved_rg_name),
            ("location", env_or_default("LOCATION", rg_location)),
            ("workspace_name", env_or_default("AML_WORKSPACE_NAME", DEFAULTS["AML_WORKSPACE_NAME"])),
            ("workspace_name_prefix", env_or_default("AML_WORKSPACE_NAME_PREFIX", DEFAULTS["AML_WORKSPACE_NAME_PREFIX"])),
            ("storage_account_id", storage_id),
            ("key_vault_id", kv_id),
            ("application_insights_id", appi_id),
            ("container_registry_id", acr_id),
            ("public_network_access_enabled", env_or_default("AML_PUBLIC_NETWORK_ACCESS_ENABLED", DEFAULTS["AML_PUBLIC_NETWORK_ACCESS_ENABLED"])),
        ],
    )


def write_aml_storage_tfvars():
    storage_dir = TERRAFORM_DIR / "16_aml_storage_account"
    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    rg_name = read_outputs_value(rg_outputs, "resource_group_name")
    rg_location = read_outputs_value(rg_outputs, "resource_group_location")
    resolved_rg_name = env_or_default("RESOURCE_GROUP_NAME", rg_name)
    if not resolved_rg_name:
        raise RuntimeError("RESOURCE_GROUP_NAME not found. Deploy the resource group first or set RESOURCE_GROUP_NAME.")
    write_tfvars(
        storage_dir / "terraform.tfvars",
        [
            ("resource_group_name", resolved_rg_name),
            ("location", env_or_default("LOCATION", rg_location)),
            ("storage_account_name", env_or_default("AML_STORAGE_ACCOUNT_NAME", DEFAULTS["AML_STORAGE_ACCOUNT_NAME"])),
            ("storage_account_name_prefix", env_or_default("AML_STORAGE_ACCOUNT_NAME_PREFIX", DEFAULTS["AML_STORAGE_ACCOUNT_NAME_PREFIX"])),
            ("account_replication_type", env_or_default("AML_STORAGE_ACCOUNT_REPLICATION_TYPE", DEFAULTS["AML_STORAGE_ACCOUNT_REPLICATION_TYPE"])),
            ("account_tier", env_or_default("AML_STORAGE_ACCOUNT_TIER", DEFAULTS["AML_STORAGE_ACCOUNT_TIER"])),
            ("public_network_access_enabled", env_or_default("AML_STORAGE_PUBLIC_NETWORK_ACCESS_ENABLED", DEFAULTS["AML_STORAGE_PUBLIC_NETWORK_ACCESS_ENABLED"])),
        ],
    )


def update_aml_train_job_yaml():
    job_path = ROOT / "pipelines" / "aml" / "jobs" / "train.yml"
    if not job_path.exists():
        raise RuntimeError(f"AML job YAML not found at {job_path}")

    acr_outputs = TERRAFORM_DIR / "06_container_registry" / "outputs.json"
    login_server = read_outputs_value(acr_outputs, "acr_login_server")
    if not login_server:
        raise RuntimeError("acr_login_server not found. Deploy ACR first.")

    compute_name = env_or_default("AML_COMPUTE_NAME", DEFAULTS["AML_COMPUTE_NAME"])
    image_tag = env_or_default("AML_TRAIN_IMAGE_TAG", DEFAULTS["AML_TRAIN_IMAGE_TAG"])
    image_value = f"{login_server}/mlops-cancer-train:{image_tag}"

    lines = job_path.read_text(encoding="utf-8").splitlines()
    updated = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("image:"):
            indent = line[: len(line) - len(stripped)]
            updated.append(f"{indent}image: {image_value}")
            continue
        if stripped.startswith("compute:"):
            indent = line[: len(line) - len(stripped)]
            updated.append(f"{indent}compute: azureml:{compute_name}")
            continue
        updated.append(line)
    job_path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def write_aml_compute_tfvars():
    compute_dir = TERRAFORM_DIR / "17_aml_compute"
    aml_outputs = TERRAFORM_DIR / "15_machine_learning_workspace" / "outputs.json"
    workspace_id = read_outputs_value(aml_outputs, "aml_workspace_id")
    workspace_location = read_outputs_value(aml_outputs, "aml_workspace_location")
    if not workspace_id or not workspace_location:
        raise RuntimeError("AML workspace outputs not found. Deploy the AML workspace first.")
    write_tfvars(
        compute_dir / "terraform.tfvars",
        [
            ("workspace_id", workspace_id),
            ("location", workspace_location),
            ("compute_name", env_or_default("AML_COMPUTE_NAME", DEFAULTS["AML_COMPUTE_NAME"])),
            ("vm_size", env_or_default("AML_COMPUTE_VM_SIZE", DEFAULTS["AML_COMPUTE_VM_SIZE"])),
            ("vm_priority", env_or_default("AML_COMPUTE_VM_PRIORITY", DEFAULTS["AML_COMPUTE_VM_PRIORITY"])),
            ("min_instances", env_or_default("AML_COMPUTE_MIN_INSTANCES", DEFAULTS["AML_COMPUTE_MIN_INSTANCES"])),
            ("max_instances", env_or_default("AML_COMPUTE_MAX_INSTANCES", DEFAULTS["AML_COMPUTE_MAX_INSTANCES"])),
            ("idle_time_before_scaledown", env_or_default("AML_COMPUTE_IDLE_TIME", DEFAULTS["AML_COMPUTE_IDLE_TIME"])),
        ],
    )


def write_acr_rbac_tfvars():
    rbac_dir = TERRAFORM_DIR / "18_acr_rbac"
    acr_outputs = TERRAFORM_DIR / "06_container_registry" / "outputs.json"
    compute_outputs = TERRAFORM_DIR / "17_aml_compute" / "outputs.json"
    acr_id = read_outputs_value(acr_outputs, "acr_id")
    compute_principal_id = read_outputs_value(compute_outputs, "compute_principal_id")
    if not acr_id or not compute_principal_id:
        raise RuntimeError("Missing outputs for ACR or AML compute. Deploy those first.")
    write_tfvars(
        rbac_dir / "terraform.tfvars",
        [
            ("acr_id", acr_id),
            ("compute_principal_id", compute_principal_id),
        ],
    )


def write_storage_rbac_tfvars():
    rbac_dir = TERRAFORM_DIR / "19_storage_rbac"
    storage_outputs = TERRAFORM_DIR / "03_storage_account" / "outputs.json"
    compute_outputs = TERRAFORM_DIR / "17_aml_compute" / "outputs.json"
    storage_account_id = read_outputs_value(storage_outputs, "storage_account_id")
    compute_principal_id = read_outputs_value(compute_outputs, "compute_principal_id")
    if not storage_account_id or not compute_principal_id:
        raise RuntimeError("Missing outputs for storage or AML compute. Deploy those first.")
    write_tfvars(
        rbac_dir / "terraform.tfvars",
        [
            ("storage_account_id", storage_account_id),
            ("compute_principal_id", compute_principal_id),
        ],
    )


def write_outputs(module_dir):
    terraform_exe = get_terraform_exe()
    output = subprocess.check_output([terraform_exe, "output", "-json"], cwd=module_dir, text=True)
    (module_dir / "outputs.json").write_text(output + "\n", encoding="utf-8")


def terraform_state_has(module_dir, address):
    terraform_exe = get_terraform_exe()
    try:
        output = subprocess.check_output([terraform_exe, "state", "list"], cwd=module_dir, text=True)
    except subprocess.CalledProcessError:
        return False
    return any(line.strip() == address for line in output.splitlines())


def ensure_role_assignment_import(module_dir, address, principal_id, scope, backend_config=None):
    if terraform_state_has(module_dir, address):
        return
    az_cmd = get_az_cmd()
    result = subprocess.check_output(
        [az_cmd, "role", "assignment", "list", "--assignee", principal_id, "--scope", scope, "--query", "[0].id", "-o", "tsv"],
        text=True,
    ).strip()
    if result:
        terraform_import(module_dir, address, result, backend_config)


def backend_config_for(module_dir):
    if os.environ.get("GITHUB_ACTIONS") == "true":
        backend_rg = env_or_default("BACKEND_RESOURCE_GROUP_NAME", None)
        backend_storage = env_or_default("BACKEND_STORAGE_ACCOUNT_NAME", None)
        backend_container = env_or_default("BACKEND_CONTAINER_NAME", DEFAULTS["BACKEND_CONTAINER_NAME"])
        if not backend_rg or not backend_storage:
            return None
    else:
        backend_outputs = TERRAFORM_DIR / "00_backend" / "outputs.json"
        backend_rg = read_outputs_value(backend_outputs, "backend_resource_group_name")
        backend_storage = read_outputs_value(backend_outputs, "backend_storage_account_name")
        if not backend_rg or not backend_storage:
            backend_rg, backend_storage = resolve_backend_names()
        backend_container = read_outputs_value(backend_outputs, "backend_container_name") or env_or_default(
            "BACKEND_CONTAINER_NAME", DEFAULTS["BACKEND_CONTAINER_NAME"]
        )
        if not backend_rg or not backend_storage or not backend_container:
            return None
    return {
        "resource_group_name": backend_rg,
        "storage_account_name": backend_storage,
        "container_name": backend_container,
        "key": f"{module_dir.name}.tfstate",
    }


def terraform_init(module_dir, backend_config=None):
    terraform_exe = get_terraform_exe()
    cmd = [terraform_exe, "init", "-upgrade"]
    if backend_config:
        if (module_dir / "terraform.tfstate").exists():
            cmd.append("-migrate-state")
        else:
            cmd.append("-reconfigure")
        cmd.extend([
            f"-backend-config=resource_group_name={backend_config['resource_group_name']}",
            f"-backend-config=storage_account_name={backend_config['storage_account_name']}",
            f"-backend-config=container_name={backend_config['container_name']}",
            f"-backend-config=key={backend_config['key']}",
        ])
    run(cmd, cwd=module_dir)


def terraform_apply(module_dir, backend_config=None):
    terraform_exe = get_terraform_exe()
    terraform_init(module_dir, backend_config)
    run([terraform_exe, "apply", "-auto-approve"], cwd=module_dir)


def terraform_import(module_dir, address, resource_id, backend_config=None):
    terraform_exe = get_terraform_exe()
    terraform_init(module_dir, backend_config)
    run([terraform_exe, "import", address, resource_id], cwd=module_dir)


def sync_aml_workspace_keys():
    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    aml_outputs = TERRAFORM_DIR / "15_machine_learning_workspace" / "outputs.json"
    resource_group = read_outputs_value(rg_outputs, "resource_group_name")
    resource_group_id = read_outputs_value(rg_outputs, "resource_group_id")
    workspace_name = read_outputs_value(aml_outputs, "aml_workspace_name")
    if not resource_group or not resource_group_id or not workspace_name:
        raise RuntimeError("Missing outputs for AML workspace sync. Deploy RG and AML workspace first.")
    az_cmd = get_az_cmd()
    subscription_id = resource_group_id.split("/subscriptions/", 1)[1].split("/", 1)[0]
    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.MachineLearningServices"
        f"/workspaces/{workspace_name}/resyncKeys?api-version=2024-04-01"
    )
    run([az_cmd, "rest", "--method", "post", "--url", url])


def run_adf_master_pipeline():
    rg_outputs = TERRAFORM_DIR / "01_resource_group" / "outputs.json"
    adf_outputs = TERRAFORM_DIR / "07_data_factory" / "outputs.json"
    master_outputs = TERRAFORM_DIR / "14_adf_pipeline_master" / "outputs.json"
    resource_group = read_outputs_value(rg_outputs, "resource_group_name")
    data_factory_name = read_outputs_value(adf_outputs, "data_factory_name")
    pipeline_name = read_outputs_value(master_outputs, "pipeline_name")
    if not resource_group or not data_factory_name or not pipeline_name:
        print("Skipping ADF master pipeline run (missing outputs).")
        return False
    az_cmd = get_az_cmd()
    run([
        az_cmd, "datafactory", "pipeline", "create-run",
        "--resource-group", resource_group,
        "--factory-name", data_factory_name,
        "--name", pipeline_name,
    ])
    return True


def main():
    parser = argparse.ArgumentParser(description="Deploy Terraform resources for the MLOps project.")
    parser.add_argument("--rg-only", action="store_true", help="Deploy only the resource group")
    parser.add_argument("--networking-only", action="store_true", help="Deploy only the networking resources")
    parser.add_argument("--storage-only", action="store_true", help="Deploy only the storage account")
    parser.add_argument("--keyvault-only", action="store_true", help="Deploy only the key vault")
    parser.add_argument("--observability-only", action="store_true", help="Deploy only Log Analytics + App Insights")
    parser.add_argument("--acr-only", action="store_true", help="Deploy only the container registry")
    parser.add_argument("--datafactory-only", action="store_true", help="Deploy only the data factory")
    parser.add_argument("--adf-links-only", action="store_true", help="Deploy only the ADF linked services")
    parser.add_argument("--adf-pipeline-only", action="store_true", help="Deploy only the ADF HTTP pipeline")
    parser.add_argument("--adf-dataflow-only", action="store_true", help="Deploy only the ADF bronze->silver data flow")
    parser.add_argument("--adf-silver-pipeline-only", action="store_true", help="Deploy only the ADF silver pipeline")
    parser.add_argument("--adf-gold-dataflow-only", action="store_true", help="Deploy only the ADF silver->gold data flow")
    parser.add_argument("--adf-gold-pipeline-only", action="store_true", help="Deploy only the ADF gold pipeline")
    parser.add_argument("--adf-master-pipeline-only", action="store_true", help="Deploy only the ADF master pipeline")
    parser.add_argument("--aml-only", action="store_true", help="Deploy only the Azure ML workspace")
    parser.add_argument("--aml-storage-only", action="store_true", help="Deploy only AML storage account (non-HNS)")
    parser.add_argument("--aml-job-config-only", action="store_true", help="Update AML job YAML from outputs")
    parser.add_argument("--acr-build-train-image", action="store_true", help="Build/push training image in ACR (no local Docker)")
    parser.add_argument("--docker-build-train-image", action="store_true", help="Build/push training image using local Docker")
    parser.add_argument("--docker-build-infer-image", action="store_true", help="Build/push inference image using local Docker")
    parser.add_argument("--aml-compute-only", action="store_true", help="Deploy only AML compute cluster")
    parser.add_argument("--acr-rbac-only", action="store_true", help="Assign AcrPull to AML workspace identity")
    parser.add_argument("--storage-rbac-only", action="store_true", help="Assign Storage Blob Data Contributor to AML compute identity")
    parser.add_argument("--skip-adf-run", action="store_true", help="Skip triggering the ADF master pipeline after deploy")
    args = parser.parse_args()

    load_env_file(ROOT / ".env")

    modules = [
        TERRAFORM_DIR / "01_resource_group",
        TERRAFORM_DIR / "02_networking",
        TERRAFORM_DIR / "03_storage_account",
        TERRAFORM_DIR / "04_key_vault",
        TERRAFORM_DIR / "05_log_analytics_app_insights",
        TERRAFORM_DIR / "06_container_registry",
        TERRAFORM_DIR / "16_aml_storage_account",
        TERRAFORM_DIR / "15_machine_learning_workspace",
        TERRAFORM_DIR / "17_aml_compute",
        TERRAFORM_DIR / "18_acr_rbac",
        TERRAFORM_DIR / "19_storage_rbac",
        TERRAFORM_DIR / "07_data_factory",
        TERRAFORM_DIR / "08_adf_linked_services",
        TERRAFORM_DIR / "09_adf_pipeline_http",
        TERRAFORM_DIR / "10_adf_dataflow_bronze_silver",
        TERRAFORM_DIR / "11_adf_pipeline_silver_dataflow",
        TERRAFORM_DIR / "12_adf_dataflow_silver_gold",
        TERRAFORM_DIR / "13_adf_pipeline_gold_dataflow",
        TERRAFORM_DIR / "14_adf_pipeline_master",
    ]
    if os.environ.get("GITHUB_ACTIONS") != "true":
        modules.insert(0, TERRAFORM_DIR / "00_backend")
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
    if args.datafactory_only:
        modules = [TERRAFORM_DIR / "07_data_factory"]
    if args.adf_links_only:
        modules = [TERRAFORM_DIR / "08_adf_linked_services"]
    if args.adf_pipeline_only:
        modules = [TERRAFORM_DIR / "09_adf_pipeline_http"]
    if args.adf_dataflow_only:
        modules = [TERRAFORM_DIR / "10_adf_dataflow_bronze_silver"]
    if args.adf_silver_pipeline_only:
        modules = [TERRAFORM_DIR / "11_adf_pipeline_silver_dataflow"]
    if args.adf_gold_dataflow_only:
        modules = [TERRAFORM_DIR / "12_adf_dataflow_silver_gold"]
    if args.adf_gold_pipeline_only:
        modules = [TERRAFORM_DIR / "13_adf_pipeline_gold_dataflow"]
    if args.adf_master_pipeline_only:
        modules = [TERRAFORM_DIR / "14_adf_pipeline_master"]
    if args.aml_only:
        modules = [TERRAFORM_DIR / "15_machine_learning_workspace"]
    if args.aml_storage_only:
        modules = [TERRAFORM_DIR / "16_aml_storage_account"]
    if args.aml_job_config_only:
        modules = []
    if args.acr_build_train_image:
        modules = []
    if args.aml_compute_only:
        modules = [TERRAFORM_DIR / "17_aml_compute"]
    if args.acr_rbac_only:
        modules = [TERRAFORM_DIR / "18_acr_rbac"]
    if args.storage_rbac_only:
        modules = [TERRAFORM_DIR / "19_storage_rbac"]

    for module_dir in modules:
        backend_config = None
        if module_dir.name == "00_backend":
            write_backend_tfvars()
            backend_rg, backend_storage = resolve_backend_names()
            backend_container = env_or_default("BACKEND_CONTAINER_NAME", DEFAULTS["BACKEND_CONTAINER_NAME"])
            if os.environ.get("GITHUB_ACTIONS") == "true" and backend_rg and backend_storage:
                if backend_resource_group_exists(backend_rg) and backend_storage_exists(backend_rg, backend_storage):
                    ensure_backend_container(backend_rg, backend_storage, backend_container)
                    write_backend_outputs_from_env(backend_rg, backend_storage, backend_container)
                    continue
        else:
            backend_config = backend_config_for(module_dir)
            if os.environ.get("GITHUB_ACTIONS") == "true" and backend_config is None:
                raise RuntimeError("BACKEND_RESOURCE_GROUP_NAME and BACKEND_STORAGE_ACCOUNT_NAME must be set in CI.")
            if backend_config:
                print(
                    "Using remote backend: "
                    f"rg={backend_config['resource_group_name']} "
                    f"sa={backend_config['storage_account_name']} "
                    f"container={backend_config['container_name']} "
                    f"key={backend_config['key']}"
                )
        if module_dir.name == "01_resource_group":
            write_resource_group_tfvars()
        if module_dir.name == "02_networking":
            write_networking_tfvars()
        if module_dir.name == "03_storage_account":
            write_storage_account_tfvars()
        if module_dir.name == "04_key_vault":
            write_key_vault_tfvars()
        if module_dir.name == "05_log_analytics_app_insights":
            write_log_analytics_tfvars()
        if module_dir.name == "06_container_registry":
            write_acr_tfvars()
        if module_dir.name == "07_data_factory":
            write_data_factory_tfvars()
        if module_dir.name == "08_adf_linked_services":
            write_adf_linked_services_tfvars()
        if module_dir.name == "09_adf_pipeline_http":
            write_adf_pipeline_http_tfvars()
        if module_dir.name == "10_adf_dataflow_bronze_silver":
            write_adf_dataflow_tfvars()
        if module_dir.name == "11_adf_pipeline_silver_dataflow":
            write_adf_pipeline_silver_tfvars()
        if module_dir.name == "12_adf_dataflow_silver_gold":
            write_adf_dataflow_gold_tfvars()
        if module_dir.name == "13_adf_pipeline_gold_dataflow":
            write_adf_pipeline_gold_tfvars()
        if module_dir.name == "14_adf_pipeline_master":
            write_adf_pipeline_master_tfvars()
        if module_dir.name == "15_machine_learning_workspace":
            write_aml_workspace_tfvars()
        if module_dir.name == "16_aml_storage_account":
            write_aml_storage_tfvars()
        if module_dir.name == "17_aml_compute":
            write_aml_compute_tfvars()
        if module_dir.name == "18_acr_rbac":
            write_acr_rbac_tfvars()
            acr_outputs = TERRAFORM_DIR / "06_container_registry" / "outputs.json"
            compute_outputs = TERRAFORM_DIR / "17_aml_compute" / "outputs.json"
            acr_id = read_outputs_value(acr_outputs, "acr_id")
            compute_principal_id = read_outputs_value(compute_outputs, "compute_principal_id")
            if not acr_id or not compute_principal_id:
                raise RuntimeError("Missing outputs for ACR or AML compute. Deploy those first.")
            ensure_role_assignment_import(
                module_dir,
                "azurerm_role_assignment.acr_pull",
                compute_principal_id,
                acr_id,
                backend_config,
            )
        if module_dir.name == "19_storage_rbac":
            write_storage_rbac_tfvars()
            storage_outputs = TERRAFORM_DIR / "03_storage_account" / "outputs.json"
            compute_outputs = TERRAFORM_DIR / "17_aml_compute" / "outputs.json"
            storage_account_id = read_outputs_value(storage_outputs, "storage_account_id")
            compute_principal_id = read_outputs_value(compute_outputs, "compute_principal_id")
            if not storage_account_id or not compute_principal_id:
                raise RuntimeError("Missing outputs for storage or AML compute. Deploy those first.")
            ensure_role_assignment_import(
                module_dir,
                "azurerm_role_assignment.storage_blob_contributor",
                compute_principal_id,
                storage_account_id,
                backend_config,
            )
        terraform_apply(module_dir, backend_config)
        write_outputs(module_dir)

    if args.aml_job_config_only or TERRAFORM_DIR.joinpath("06_container_registry") in modules:
        update_aml_train_job_yaml()

    if args.acr_build_train_image:
        acr_outputs = TERRAFORM_DIR / "06_container_registry" / "outputs.json"
        acr_name = read_outputs_value(acr_outputs, "acr_name")
        if not acr_name:
            raise RuntimeError("acr_name not found. Deploy ACR first.")
        image_tag = env_or_default("AML_TRAIN_IMAGE_TAG", DEFAULTS["AML_TRAIN_IMAGE_TAG"])
        dockerfile = ROOT / "docker" / "train" / "Dockerfile"
        az_cmd = get_az_cmd()
        run([
            az_cmd, "acr", "build",
            "--registry", acr_name,
            "--image", f"mlops-cancer-train:{image_tag}",
            "-f", str(dockerfile),
            ".",
        ], cwd=ROOT)

    if args.docker_build_train_image:
        acr_outputs = TERRAFORM_DIR / "06_container_registry" / "outputs.json"
        login_server = read_outputs_value(acr_outputs, "acr_login_server")
        acr_name = read_outputs_value(acr_outputs, "acr_name")
        if not login_server or not acr_name:
            raise RuntimeError("ACR outputs not found. Deploy ACR first.")
        image_tag = env_or_default("AML_TRAIN_IMAGE_TAG", DEFAULTS["AML_TRAIN_IMAGE_TAG"])
        dockerfile = ROOT / "docker" / "train" / "Dockerfile"
        image = f"{login_server}/mlops-cancer-train:{image_tag}"
        run(["docker", "build", "-t", image, "-f", str(dockerfile), "."], cwd=ROOT)
        az_cmd = get_az_cmd()
        run([az_cmd, "acr", "login", "--name", acr_name], cwd=ROOT)
        run(["docker", "push", image], cwd=ROOT)

    if args.docker_build_infer_image:
        acr_outputs = TERRAFORM_DIR / "06_container_registry" / "outputs.json"
        login_server = read_outputs_value(acr_outputs, "acr_login_server")
        acr_name = read_outputs_value(acr_outputs, "acr_name")
        if not login_server or not acr_name:
            raise RuntimeError("ACR outputs not found. Deploy ACR first.")
        image_tag = env_or_default("AML_TRAIN_IMAGE_TAG", DEFAULTS["AML_TRAIN_IMAGE_TAG"])
        dockerfile = ROOT / "docker" / "inference" / "Dockerfile"
        image = f"{login_server}/mlops-cancer-infer:{image_tag}"
        run(["docker", "build", "-t", image, "-f", str(dockerfile), "."], cwd=ROOT)
        az_cmd = get_az_cmd()
        run([az_cmd, "acr", "login", "--name", acr_name], cwd=ROOT)
        run(["docker", "push", image], cwd=ROOT)

    if modules:
        sync_aml_workspace_keys()

    adf_module_names = {
        "07_data_factory",
        "08_adf_linked_services",
        "09_adf_pipeline_http",
        "10_adf_dataflow_bronze_silver",
        "11_adf_pipeline_silver_dataflow",
        "12_adf_dataflow_silver_gold",
        "13_adf_pipeline_gold_dataflow",
        "14_adf_pipeline_master",
    }
    if modules and not args.skip_adf_run:
        if any(module_dir.name in adf_module_names for module_dir in modules):
            run_adf_master_pipeline()


if __name__ == "__main__":
    main()
