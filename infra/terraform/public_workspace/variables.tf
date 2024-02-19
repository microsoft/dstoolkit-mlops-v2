# variable "subscription_id" {
#   type    = string
#   default = ""
# }
# variable "tenant_id" {
#   type    = string
#   default = ""
# }
# variable "client_id" {
#   type    = string
#   default = ""
# }


##############################
## Resource Group Variables
##############################
variable "rg_name" {
  type    = string
  default = "rg-terraform"
}
variable "tfstate_rg_name" {
  type    = string
  default = "rg-tfstate-terraform"
}

variable "storage_acct" {
  type    = string
  default = "stterraform"
}

variable "tfstate_storage_acct" {
  type    = string
  default = "sttfstateterraform"
}

variable "keyvault_name" {
  type    = string
  default = "kvterraform"
}

variable "appinsights_name" {
  type    = string
  default = "appiterraform"
}

variable "container_registry_name" {
  type    = string
  default = "crterraform"
}

variable "workspace_name" {
  type    = string
  default = "amlterraform"
}


variable "location" {
  type    = string
  default = "eastus"
}
