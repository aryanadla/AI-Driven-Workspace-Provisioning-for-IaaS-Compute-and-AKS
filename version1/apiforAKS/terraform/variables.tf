variable "resource_group_name" {
  type        = string
  description = "The name of the resource group"
}

variable "acr_name" {
  type        = string
  description = "The name of the Azure Container Registry"
}

variable "acr_sku" {
  type        = string
  description = "The SKU of the Azure Container Registry"
}

variable "cluster_name" {
  type        = string
  description = "The name of the AKS cluster"
}

variable "kubernetes_version" {
  type        = string
  description = "The version of Kubernetes to use for the AKS cluster"
}

variable "dns_prefix" {
  type        = string
  description = "The DNS prefix to use with the AKS cluster"
}

variable "node_resource_group" {
  type        = string
  description = "The name of the resource group for AKS cluster nodes"
}

# variable "enable_local_accounts" {
#   type        = bool
#   description = "Whether to enable local accounts on the AKS cluster"
# }

variable "node_pools" {
  type = list(object({
    name               = string
    os_sku             = string
    node_count         = number
    vm_size            = string
  }))
  description = "A list of node pools to create in the AKS cluster"
}

variable "network_plugin" {
  type        = string
  description = "The network plugin to use for the AKS cluster"
}

variable "network_policy" {
  type        = string
  description = "The network policy to use for the AKS cluster"
}

variable "service_cidr" {
  type        = string
  description = "The CIDR block for Kubernetes services"
}

variable "dns_service_ip" {
  type        = string
  description = "The IP address for the Kubernetes DNS service"
}