terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.2.0"  
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

data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}

resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  sku                 = var.acr_sku
}
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  kubernetes_version  = var.kubernetes_version
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  dns_prefix          = var.dns_prefix
  node_resource_group = var.node_resource_group
  # local_account_disabled = !var.enable_local_accounts
  private_cluster_enabled   = false
  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  dynamic "default_node_pool" {
    for_each = var.node_pools
    content {
      name                = default_node_pool.value.name
      os_sku              = default_node_pool.value.os_sku
      vm_size             = default_node_pool.value.vm_size
      type                = "VirtualMachineScaleSets"
      node_count = 1
      node_labels = {
        role = "general"
      }
    }
  }
  
  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin     = var.network_plugin
    network_policy     = var.network_policy
    load_balancer_sku  = "standard"
    service_cidr       = var.service_cidr
    dns_service_ip     = var.dns_service_ip
  }

  auto_scaler_profile {
    balance_similar_node_groups      = true
    expander                         = "random"
    max_graceful_termination_sec     = 600
    max_node_provisioning_time       = "15m"
    max_unready_nodes                = 3
    max_unready_percentage           = 45
    new_pod_scale_up_delay           = "10s"
    scale_down_delay_after_add       = "10m"
    scale_down_delay_after_delete    = "10s"
    scale_down_delay_after_failure   = "3m"
    scan_interval                    = "10s"
    scale_down_unneeded              = "10m"
    scale_down_unready               = "20m"
    scale_down_utilization_threshold = "0.5"
  }
}

resource "azurerm_role_assignment" "acr_pull" {
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name = "AcrPull"
  scope                = azurerm_container_registry.acr.id
   skip_service_principal_aad_check = true
}


