output "compute_name" {
  value = azapi_resource.main.name
}

output "compute_id" {
  value = azapi_resource.main.id
}

output "compute_principal_id" {
  value = azapi_resource.main.identity[0].principal_id
}
