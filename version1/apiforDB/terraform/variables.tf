# Define the Resource Group Name
variable "resource_group_name" {
  description = "The name of the resource group in which to create the resources."
  type        = string
  default     = "Hackathon_Devops2"
}

# Define the Azure Location
variable "location" {
  description = "The Azure location where resources will be created."
  type        = string
  default     = "East US"
}

# Define the Databricks Workspace Name
variable "databricks_workspace_name" {
  description = "The name of the Databricks workspace."
  type        = string
  default     = "MyDatabricksWorkspace"
}

# Define the Databricks SKU
variable "databricks_sku" {
  description = "The pricing tier for the Azure Databricks workspace."
  type        = string
  default     = "standard"
}

# Define the Databricks Clusters Configuration
variable "databricks_clusters" {
  description = "A map of Databricks clusters to create, including their configurations."
  type = map(object({
    cluster_name  = string
    spark_version = string
    node_type     = string
    min_workers   = number
    max_workers   = number
  }))
  default = {
    cluster1 = {
      cluster_name  = "MyCluster"
      spark_version = "15.4 LTS (Scala 2.12, Spark 3.5.0)"
      node_type     = "Standard_D4ds_v5"
      min_workers   = 2
      max_workers   = 8
    }
  }
}

# Define the configuration for secure cluster connectivity
variable "enable_secure_cluster_connectivity" {
  description = "Whether to deploy Azure Databricks workspace with Secure Cluster Connectivity (No Public IP)."
  type        = bool
  default     = false
}

# Define the configuration for deploying in a VNet
variable "enable_vnet_deployment" {
  description = "Whether to deploy Azure Databricks workspace in your own Virtual Network (VNet)."
  type        = bool
  default     = false
}

# Define the configuration for customer-managed key encryption
variable "enable_customer_managed_key" {
  description = "Whether to enable customer-managed key encryption."
  type        = bool
  default     = false
}

variable "key_vault_id" {
  description = "The ID of the Azure Key Vault used for customer-managed key encryption."
  type        = string
  default     = ""
}

variable "key_id" {
  description = "The ID of the encryption key used for customer-managed key encryption."
  type        = string
  default     = ""
}

# Define the configuration for compliance and security features
variable "enable_compliance_security_profile" {
  description = "Whether to enable the compliance security profile."
  type        = bool
  default     = false
}

variable "enable_enhanced_security_monitoring" {
  description = "Whether to enable enhanced security monitoring."
  type        = bool
  default     = false
}

variable "enable_automatic_cluster_update" {
  description = "Whether to enable automatic cluster updates."
  type        = bool
  default     = false
}

# Define the VNet ID for deployment if using VNet
variable "vnet_id" {
  description = "The ID of the virtual network to use for deployment."
  type        = string
  default     = ""
}
