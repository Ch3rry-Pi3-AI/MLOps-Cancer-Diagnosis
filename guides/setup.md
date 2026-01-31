# Project Setup Guide

This project provisions Azure resources using Terraform and includes helper scripts.

## Prerequisites
- Azure CLI (az) installed and authenticated
- Terraform installed (>= 1.5)
- Python 3.10+ (for running the helper scripts)
- uv (optional, for local Python dependency management)

## Azure CLI
Check your Azure CLI and login status:

```powershell
az --version
az login
az account show
```

If you need to switch subscriptions:

```powershell
az account list --output table
az account set --subscription "<subscription-id-or-name>"
az account show
```

## GitHub Actions (Secrets)
Create a service principal and add it as a GitHub Actions secret.

1) Generate JSON credentials:
```powershell
az ad sp create-for-rbac --name "gh-mlops-cancer" --role contributor --scopes /subscriptions/<subscription-id> --sdk-auth
```

2) GitHub -> **Settings -> Secrets and variables -> Actions -> New repository secret**:
   - Name: `AZURE_CREDENTIALS`
   - Value: paste the **entire JSON** output.

3) Grant the service principal RBAC assignment rights (one-time):
```powershell
az role assignment create --assignee <clientId> --role "User Access Administrator" --scope /subscriptions/<subscription-id>
```
Note: this command does **not** change `AZURE_CREDENTIALS`. You do not need to update the GitHub secret after granting this role.

## Terraform Setup
Check if Terraform is installed and on PATH:

```powershell
terraform version
```

Install or update Terraform on Windows:

```powershell
winget install HashiCorp.Terraform
```

```powershell
choco install terraform -y
```

After installing, re-open PowerShell and re-run terraform version.

## Project Structure
- `terraform/01_resource_group`: Azure resource group
- `terraform/02_networking`: VNet + subnets (foundation for private endpoints)
- `terraform/03_storage_account`: ADLS Gen2 storage account + containers
- `terraform/04_key_vault`: Azure Key Vault
- `terraform/05_log_analytics_app_insights`: Log Analytics + Application Insights
- `terraform/06_container_registry`: Azure Container Registry (ACR)
- `terraform/07_data_factory`: Azure Data Factory (system-assigned identity)
- `terraform/08_adf_linked_services`: ADF linked services (HTTP + ADLS Gen2)
- `terraform/09_adf_pipeline_http`: ADF pipeline to land raw dataset into ADLS bronze
- `terraform/10_adf_dataflow_bronze_silver`: ADF mapping data flow for bronze -> silver cleanup
- `terraform/11_adf_pipeline_silver_dataflow`: ADF pipeline to execute bronze -> silver data flow
- `terraform/12_adf_dataflow_silver_gold`: ADF mapping data flow for silver -> gold feature encoding
- `terraform/13_adf_pipeline_gold_dataflow`: ADF pipeline to execute silver -> gold data flow
- `terraform/14_adf_pipeline_master`: ADF master pipeline (ingest -> silver -> gold)
- `terraform/15_machine_learning_workspace`: Azure ML workspace (v2)
- `terraform/16_aml_storage_account`: Non-HNS storage account for AML workspace
- `terraform/17_aml_compute`: AML compute cluster
- `terraform/18_acr_rbac`: AcrPull for AML compute identity
- `terraform/19_storage_rbac`: Storage Blob Data Contributor for AML compute identity
- `scripts/`: Helper scripts to deploy/destroy Terraform resources
- `guides/setup.md`: This guide

## Configure Terraform
The deploy script writes `terraform/01_resource_group/terraform.tfvars` automatically.
If you want different defaults, edit `DEFAULTS` in `scripts/deploy.py` or set env vars in `.env`.

Supported environment variables:
- `RESOURCE_GROUP_NAME`
- `RESOURCE_GROUP_NAME_PREFIX`
- `LOCATION`
- `VNET_NAME`
- `VNET_NAME_PREFIX`
- `ADDRESS_SPACE` (comma-separated)
- `SUBNET_PREFIXES` (JSON map)
- `STORAGE_ACCOUNT_NAME`
- `STORAGE_ACCOUNT_NAME_PREFIX`
- `ACCOUNT_REPLICATION_TYPE`
- `ACCOUNT_TIER`
- `PUBLIC_NETWORK_ACCESS_ENABLED`
- `IS_HNS_ENABLED`
- `CONTAINER_NAMES` (comma-separated)
- `STORAGE_BLOB_CONTRIBUTOR_OBJECT_ID`
- `KEY_VAULT_NAME`
- `KEY_VAULT_NAME_PREFIX`
- `KEY_VAULT_SKU_NAME`
- `KEY_VAULT_ENABLE_RBAC`
- `KEY_VAULT_PUBLIC_NETWORK_ACCESS_ENABLED`
- `KEY_VAULT_SOFT_DELETE_RETENTION_DAYS`
- `KEY_VAULT_PURGE_PROTECTION_ENABLED`
- `KEY_VAULT_ADMIN_OBJECT_ID`
- `LOG_ANALYTICS_NAME`
- `LOG_ANALYTICS_NAME_PREFIX`
- `LOG_ANALYTICS_SKU`
- `LOG_ANALYTICS_RETENTION_IN_DAYS`
- `APP_INSIGHTS_NAME`
- `APP_INSIGHTS_NAME_PREFIX`
- `APP_INSIGHTS_APPLICATION_TYPE`
- `ACR_NAME`
- `ACR_NAME_PREFIX`
- `ACR_SKU`
- `ACR_ADMIN_ENABLED`
- `ACR_PUBLIC_NETWORK_ACCESS_ENABLED`
- `DATA_FACTORY_NAME`
- `DATA_FACTORY_NAME_PREFIX`
- `HTTP_LINKED_SERVICE_NAME`
- `HTTP_LINKED_SERVICE_NAME_PREFIX`
- `HTTP_BASE_URL`
- `HTTP_AUTHENTICATION_TYPE`
- `HTTP_ENABLE_CERTIFICATE_VALIDATION`
- `INTEGRATION_RUNTIME_NAME`
- `ADLS_LINKED_SERVICE_NAME`
- `ADLS_LINKED_SERVICE_NAME_PREFIX`
- `LINKED_SERVICE_DESCRIPTION`
- `ADF_PIPELINE_NAME`
- `ADF_PIPELINE_NAME_PREFIX`
- `HTTP_DATASET_NAME`
- `HTTP_DATASET_NAME_PREFIX`
- `SINK_DATASET_NAME`
- `SINK_DATASET_NAME_PREFIX`
- `HTTP_RELATIVE_URL`
- `SINK_FILE_SYSTEM`
- `SINK_FOLDER`
- `SINK_FILE`
- `ADF_DATAFLOW_NAME`
- `ADF_DATAFLOW_NAME_PREFIX`
- `BRONZE_SOURCE_DATASET_NAME`
- `BRONZE_SOURCE_DATASET_NAME_PREFIX`
- `BRONZE_SOURCE_CONTAINER`
- `BRONZE_SOURCE_FOLDER`
- `BRONZE_SOURCE_FILE`
- `SILVER_SINK_CONTAINER`
- `SILVER_SINK_FOLDER`
- `SILVER_SINK_FORMAT`
- `ADF_SILVER_PIPELINE_NAME`
- `ADF_SILVER_PIPELINE_NAME_PREFIX`
- `ADF_DATAFLOW_COMPUTE_TYPE`
- `ADF_DATAFLOW_CORE_COUNT`
- `ADF_DATAFLOW_TRACE_LEVEL`
- `ADF_GOLD_DATAFLOW_NAME`
- `ADF_GOLD_DATAFLOW_NAME_PREFIX`
- `SILVER_SOURCE_DATASET_NAME`
- `SILVER_SOURCE_DATASET_NAME_PREFIX`
- `SILVER_SOURCE_CONTAINER`
- `SILVER_SOURCE_FOLDER`
- `GOLD_SINK_CONTAINER`
- `GOLD_SINK_FOLDER`
- `GOLD_SINK_FORMAT`
- `ADF_GOLD_PIPELINE_NAME`
- `ADF_GOLD_PIPELINE_NAME_PREFIX`
- `ADF_MASTER_PIPELINE_NAME`
- `ADF_MASTER_PIPELINE_NAME_PREFIX`
- `AML_WORKSPACE_NAME`
- `AML_WORKSPACE_NAME_PREFIX`
- `AML_PUBLIC_NETWORK_ACCESS_ENABLED`
- `AML_STORAGE_ACCOUNT_NAME`
- `AML_STORAGE_ACCOUNT_NAME_PREFIX`
- `AML_STORAGE_ACCOUNT_REPLICATION_TYPE`
- `AML_STORAGE_ACCOUNT_TIER`
- `AML_STORAGE_PUBLIC_NETWORK_ACCESS_ENABLED`
- `AML_COMPUTE_NAME`
- `AML_TRAIN_IMAGE_TAG`
- `AML_COMPUTE_VM_SIZE`
- `AML_COMPUTE_VM_PRIORITY`
- `AML_COMPUTE_MIN_INSTANCES`
- `AML_COMPUTE_MAX_INSTANCES`
- `AML_COMPUTE_IDLE_TIME` (ISO 8601 duration, e.g. PT2M)
- `TERRAFORM_EXE` (optional path override if Terraform is blocked by AppLocker)

## Azure ML (training image + job)
Build and push the training image:
```powershell
az acr login --name <acr-name>
docker build -t <acr-login-server>/mlops-cancer-train:0.1.0 -f docker/train/Dockerfile .
docker push <acr-login-server>/mlops-cancer-train:0.1.0
```

Build in ACR (no local Docker required):
```powershell
python scripts\deploy.py --acr-build-train-image
```

Build/push using local Docker (recommended when ACR Tasks are blocked):
```powershell
python scripts\deploy.py --docker-build-train-image
python scripts\deploy.py --docker-build-infer-image
```

Register AML environment and render the pipeline YAML:
```powershell
uv run .\scripts\register_aml_assets.py
```

Register the pipeline component and submit a run:
```powershell
uv run .\scripts\register_aml_assets.py --register-pipeline-component --pipeline-component-version 1
uv run .\scripts\run_pipeline_component.py --register-data-asset --component-version 1
```

Deploy endpoint and smoke test:
```powershell
uv run .\scripts\deploy_endpoint.py
uv run .\scripts\smoke_test_endpoint.py --endpoint-name <endpoint-name>
```

Submit the legacy single-job run:
```powershell
az ml job create --file pipelines/aml/jobs/train.yml --resource-group <rg> --workspace-name <aml-workspace>
```

## Deploy
```powershell
python scripts\deploy.py
```

## Destroy
```powershell
python scripts\destroy.py
```
