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
- `TERRAFORM_EXE` (optional path override if Terraform is blocked by AppLocker)

## Deploy
```powershell
python scripts\deploy.py
```

## Destroy
```powershell
python scripts\destroy.py
```
