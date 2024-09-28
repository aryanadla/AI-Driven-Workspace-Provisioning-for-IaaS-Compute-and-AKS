output "vm_public_ip" {
  value = azurerm_public_ip.appip.ip_address
}

output "admin_username" {
  value = var.admin_username
}

output "linux_pem_key" {
  value     = local_file.linuxpemkey.content
  sensitive = true
}

output "vm_id" {
  value = azurerm_linux_virtual_machine.linuxvm.id
}

output "vm_name" {
  value = var.vm
}

output "resource_group" {
  value = var.rgname
}
# output "ssh_public_key" {
#   value       = tls_private_key.linuxkey.public_key_openssh
# }
