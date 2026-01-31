output "dataflow_name" {
  value = azapi_resource.dataflow.name
}

output "bronze_source_dataset_name" {
  value = azurerm_data_factory_dataset_delimited_text.bronze_source.name
}
