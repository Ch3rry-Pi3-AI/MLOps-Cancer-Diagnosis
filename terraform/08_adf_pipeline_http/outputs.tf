output "pipeline_name" {
  value = azapi_resource.pipeline.name
}

output "http_dataset_name" {
  value = azapi_resource.http_dataset.name
}

output "sink_dataset_name" {
  value = azapi_resource.adls_sink_dataset.name
}
