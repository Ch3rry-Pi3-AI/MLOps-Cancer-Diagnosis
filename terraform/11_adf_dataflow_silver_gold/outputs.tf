output "dataflow_name" {
  value = azapi_resource.dataflow.name
}

output "silver_source_dataset_name" {
  value = azurerm_data_factory_dataset_parquet.silver_source.name
}
