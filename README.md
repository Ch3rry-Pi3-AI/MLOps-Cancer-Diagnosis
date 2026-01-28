# Azure MLOps Cancer Diagnosis (IaC)

Terraform-first Azure MLOps infrastructure with a modular folder layout. We will add resources one at a time; the first module provisions the resource group.

## Dataset
This project uses the UCI Breast Cancer dataset stored locally under `data/`.

Source: `https://archive.ics.uci.edu/dataset/14/breast+cancer`

Attribution (required):
Zwitter, M. & Soklic, M. (1988). Breast Cancer [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C51P4M.

## Quick Start
1) Install prerequisites:
   - Azure CLI (az)
   - Terraform (>= 1.5)
   - Python 3.10+

2) Authenticate to Azure:
```powershell
az login
az account show
```

3) Deploy infrastructure:
```powershell
python scripts\deploy.py
```

## Resource Naming
Resource names use a clear prefix plus a random animal suffix for uniqueness, for example:
`rg-mlops-cancer-bright-otter`

Override by setting explicit name variables or adjusting the prefixes in `.env` or the scripts.

## Project Structure
- `terraform/01_resource_group`: Azure resource group
- `terraform/02_networking`: VNet + subnets (foundation for private endpoints)
- `terraform/03_storage_account`: ADLS Gen2 storage account + containers
- `terraform/04_key_vault`: Azure Key Vault
- `terraform/05_log_analytics_app_insights`: Log Analytics + Application Insights
- `terraform/06_container_registry`: Azure Container Registry (ACR)
- `scripts/`: Deploy/destroy helpers (auto-writes terraform.tfvars)
- `guides/setup.md`: Detailed setup guide

## Deploy/Destroy Options
Deploy:
```powershell
python scripts\deploy.py
python scripts\deploy.py --rg-only
python scripts\deploy.py --networking-only
python scripts\deploy.py --storage-only
python scripts\deploy.py --keyvault-only
python scripts\deploy.py --observability-only
python scripts\deploy.py --acr-only
```

Destroy:
```powershell
python scripts\destroy.py
python scripts\destroy.py --rg-only
python scripts\destroy.py --networking-only
python scripts\destroy.py --storage-only
python scripts\destroy.py --keyvault-only
python scripts\destroy.py --observability-only
python scripts\destroy.py --acr-only
```

## Outputs
After each apply, module outputs are written to the module folder, for example:
- `terraform/01_resource_group/outputs.json`
- `terraform/02_networking/outputs.json`
- `terraform/03_storage_account/outputs.json`
- `terraform/04_key_vault/outputs.json`
- `terraform/05_log_analytics_app_insights/outputs.json`
- `terraform/06_container_registry/outputs.json`
