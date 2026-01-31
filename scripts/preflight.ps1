$ErrorActionPreference = "Stop"

$rg = (Get-Content .\terraform\01_resource_group\outputs.json | ConvertFrom-Json).resource_group_name.value
$rgId = (Get-Content .\terraform\01_resource_group\outputs.json | ConvertFrom-Json).resource_group_id.value
$ws = (Get-Content .\terraform\15_machine_learning_workspace\outputs.json | ConvertFrom-Json).aml_workspace_name.value
$acr = (Get-Content .\terraform\06_container_registry\outputs.json | ConvertFrom-Json).acr_name.value
$sub = $rgId.Split("/subscriptions/")[1].Split("/")[0]
$compute = "cpu-cluster"

Write-Host "Resource group: $rg"
Write-Host "Workspace: $ws"
Write-Host "ACR: $acr"
Write-Host "Compute: $compute"

$wsUrl = "https://management.azure.com/subscriptions/$sub/resourceGroups/$rg/providers/Microsoft.MachineLearningServices/workspaces/$ws?api-version=2024-04-01"
$computeUrl = "https://management.azure.com/subscriptions/$sub/resourceGroups/$rg/providers/Microsoft.MachineLearningServices/workspaces/$ws/computes/$compute?api-version=2023-04-01"

Write-Host "`nWorkspace identity:"
az rest --method get --url $wsUrl --query identity

Write-Host "`nCompute identity:"
az rest --method get --url $computeUrl --query identity

Write-Host "`nACR info:"
az acr show -n $acr --query "{name:name, id:id, adminUserEnabled:adminUserEnabled, loginServer:loginServer}"
