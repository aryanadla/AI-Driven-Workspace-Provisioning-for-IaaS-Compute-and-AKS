terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.1.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "e38e4eed-8fbd-4713-b27d-0f419989008a"
  client_id       = "16087f09-1d27-4fe2-8509-7a757712b93d"
  client_secret   = "KRB8Q~q2FYK6nEN1-3KDF~dRIxsOfYwP7e.sNboM"
  tenant_id       = "9b415834-803a-4da0-afdc-fe6b1d52d649"
   resource_provider_registrations = "none"
}

provider "databricks" {
  azure_workspace_resource_id = azurerm_databricks_workspace.workspace.id
  azure_client_id             = "16087f09-1d27-4fe2-8509-7a757712b93d"
  azure_client_secret         = "KRB8Q~q2FYK6nEN1-3KDF~dRIxsOfYwP7e.sNboM"
  azure_tenant_id             = "9b415834-803a-4da0-afdc-fe6b1d52d649"
}

# Define the Resource Group as a data source
data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

# Define the Azure Databricks Workspace
resource "azurerm_databricks_workspace" "workspace" {
  name                = var.databricks_workspace_name
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  sku                 = var.databricks_sku
}

# Define Azure Databricks Clusters
resource "databricks_cluster" "cluster" {
  for_each       = var.databricks_clusters
  cluster_name   = each.value.cluster_name
  spark_version  = each.value.spark_version
  node_type_id   = each.value.node_type

  autoscale {
    min_workers = each.value.min_workers
    max_workers = each.value.max_workers
  }

  # Optional configurations - uncomment if needed
  # secure_cluster_connectivity = var.enable_secure_cluster_connectivity
  # vnet_id = var.enable_vnet_deployment ? var.vnet_id : null
  # workspace_id = azurerm_databricks_workspace.workspace.id

  # Optional infrastructure encryption settings - uncomment if needed
  # infrastructure_encryption {
  #   enabled = var.enable_customer_managed_key
  # }
}

