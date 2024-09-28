provider "random" {}

# Resource Group
data "azurerm_resource_group" "appgrp" {
  name = var.rgname
}

# Generate Random Name for Virtual Network
resource "random_id" "vnet_name" {
  byte_length = 4
}

# Virtual Network
resource "azurerm_virtual_network" "appnetwork" {
  name                = "vnet-${random_id.vnet_name.hex}"
  location            = data.azurerm_resource_group.appgrp.location
  resource_group_name = data.azurerm_resource_group.appgrp.name
  address_space       = ["10.0.0.0/16"]

  depends_on = [data.azurerm_resource_group.appgrp]
}

# Generate Random Name for Subnet A
resource "random_id" "subnetA_name" {
  byte_length = 4
}

# Subnet A
resource "azurerm_subnet" "subnetA" {
  name                 = "subnetA-${random_id.subnetA_name.hex}"
  resource_group_name  = data.azurerm_resource_group.appgrp.name
  virtual_network_name = azurerm_virtual_network.appnetwork.name
  address_prefixes     = ["10.0.1.0/24"]

  depends_on = [azurerm_virtual_network.appnetwork]
}

# Generate Random Name for Subnet B
resource "random_id" "subnetB_name" {
  byte_length = 4
}

# Subnet B
resource "azurerm_subnet" "subnetB" {
  name                 = "subnetB-${random_id.subnetB_name.hex}"
  resource_group_name  = data.azurerm_resource_group.appgrp.name
  virtual_network_name = azurerm_virtual_network.appnetwork.name
  address_prefixes     = ["10.0.2.0/24"]

  depends_on = [azurerm_virtual_network.appnetwork]
}

# Generate Random Name for Public IP
resource "random_id" "public_ip_name" {
  byte_length = 4
}

# Public IP
resource "azurerm_public_ip" "appip" {
  name                = "pip-${random_id.public_ip_name.hex}"
  resource_group_name = data.azurerm_resource_group.appgrp.name
  location            = data.azurerm_resource_group.appgrp.location
  allocation_method   = "Static"

  depends_on = [data.azurerm_resource_group.appgrp]
}

# Generate Random Name for Network Interface
resource "random_id" "network_interface_name" {
  byte_length = 4
}

# Network Interface
resource "azurerm_network_interface" "appinterface" {
  name                = "nic-${random_id.network_interface_name.hex}"
  location            = data.azurerm_resource_group.appgrp.location
  resource_group_name = data.azurerm_resource_group.appgrp.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnetA.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.appip.id
  }

  depends_on = [azurerm_subnet.subnetA, azurerm_public_ip.appip]
}

# Generate Random Name for Network Security Group
resource "random_id" "nsg_name" {
  byte_length = 4
}

# Network Security Group
resource "azurerm_network_security_group" "appnsg" {
  name                = "nsg-${random_id.nsg_name.hex}"
  location            = data.azurerm_resource_group.appgrp.location
  resource_group_name = data.azurerm_resource_group.appgrp.name

  security_rule {
    name                       = "AllowSSH"
    priority                   = 300
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  depends_on = [data.azurerm_resource_group.appgrp]
}

# Subnet NSG Association
resource "azurerm_subnet_network_security_group_association" "appnsglink" {
  subnet_id                 = azurerm_subnet.subnetA.id
  network_security_group_id = azurerm_network_security_group.appnsg.id
}

# TLS Private Key
resource "tls_private_key" "linuxkey" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Save Private Key to Local File
resource "local_file" "linuxpemkey" {
  filename = "linuxkey.pem"
  content  = tls_private_key.linuxkey.private_key_pem

  depends_on = [tls_private_key.linuxkey]
}

# Linux Virtual Machine
resource "azurerm_linux_virtual_machine" "linuxvm" {
  name                = var.vm
  resource_group_name = data.azurerm_resource_group.appgrp.name
  location            = data.azurerm_resource_group.appgrp.location
  size                = var.vmsize
  admin_username      = var.admin_username
  network_interface_ids = [
    azurerm_network_interface.appinterface.id
  ]

  admin_ssh_key {
    username   = var.admin_username
    public_key = tls_private_key.linuxkey.public_key_openssh
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts"
    version   = "latest"
  }

  depends_on = [
    azurerm_network_interface.appinterface,
    data.azurerm_resource_group.appgrp,
    tls_private_key.linuxkey
  ]
}
