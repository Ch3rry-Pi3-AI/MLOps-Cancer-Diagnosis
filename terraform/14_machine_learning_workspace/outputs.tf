output "aml_workspace_id" {
  value = azurerm_machine_learning_workspace.main.id
}

output "aml_workspace_name" {
  value = azurerm_machine_learning_workspace.main.name
}

output "aml_workspace_location" {
  value = azurerm_machine_learning_workspace.main.location
}

output "aml_workspace_principal_id" {
  value = azurerm_machine_learning_workspace.main.identity[0].principal_id
}
