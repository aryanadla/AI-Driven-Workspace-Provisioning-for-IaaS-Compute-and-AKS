variable "rgname"{
  type=string
}
variable "vmsize"{
  type=string
}


# Variable for the admin username of the Linux VM
variable "admin_username" {
  description = "Admin username for the Linux virtual machine."
  type    = string
  default = "linuxusr"  # Default admin username
}

# Variable for the name of the virtual machine
variable "vm" {
  description = "Name of the Linux virtual machine."
  type = string
  default = "linuxvm"  # Default name for the VM
}
