output "data_factory_id" {
  value = azurerm_data_factory.main.id
}

output "data_factory_name" {
  value = azurerm_data_factory.main.name
}

output "data_factory_location" {
  value = azurerm_data_factory.main.location
}

output "data_factory_principal_id" {
  value = azurerm_data_factory.main.identity[0].principal_id
}
