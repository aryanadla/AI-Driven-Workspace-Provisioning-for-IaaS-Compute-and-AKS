
# Output Databricks Workspace Information
output "databricks_workspace_id" {
  description = "The ID of the Databricks workspace."
  value       = azurerm_databricks_workspace.workspace.id
}

output "databricks_workspace_endpoint" {
  description = "The endpoint of the Databricks workspace."
  value       = azurerm_databricks_workspace.workspace.workspace_url
}