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
- `scripts/`: Helper scripts to deploy/destroy Terraform resources
- `guides/setup.md`: This guide

## Configure Terraform
The deploy script writes `terraform/01_resource_group/terraform.tfvars` automatically.
If you want different defaults, edit `DEFAULTS` in `scripts/deploy.py` or set env vars in `.env`.

Supported environment variables:
- `RESOURCE_GROUP_NAME`
- `RESOURCE_GROUP_NAME_PREFIX`
- `LOCATION`
- `TERRAFORM_EXE` (optional path override if Terraform is blocked by AppLocker)

## Deploy
```powershell
python scripts\deploy.py
```

## Destroy
```powershell
python scripts\destroy.py
```
