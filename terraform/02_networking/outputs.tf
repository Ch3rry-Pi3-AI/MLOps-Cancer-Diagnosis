output "vnet_id" {
  value = azurerm_virtual_network.main.id
}

output "vnet_name" {
  value = azurerm_virtual_network.main.name
}

output "subnet_ids" {
  value = { for name, subnet in azurerm_subnet.main : name => subnet.id }
}

output "subnet_names" {
  value = sort(keys(azurerm_subnet.main))
}
