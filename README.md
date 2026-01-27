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
- `scripts/`: Deploy/destroy helpers (auto-writes terraform.tfvars)
- `guides/setup.md`: Detailed setup guide

## Deploy/Destroy Options
Deploy:
```powershell
python scripts\deploy.py
python scripts\deploy.py --rg-only
```

Destroy:
```powershell
python scripts\destroy.py
python scripts\destroy.py --rg-only
```

## Outputs
After each apply, module outputs are written to `terraform/01_resource_group/outputs.json`.
