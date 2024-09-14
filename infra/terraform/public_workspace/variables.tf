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
variable "location" {
  type    = string
}

variable "github_org" {
  type    = string
}

variable "github_repo" {
  type     = string
}

variable "tfstate_storage_acct" {
  type    = string
}

variable "tfstate_rg_name" {
  type    = string
}

variable "rg_name" {
  type    = string
  default = "mlopsv2-rg"
}

variable "storage_acct" {
  type    = string
  default = "mlopsv2st"
}

variable "keyvault_name" {
  type    = string
  default = "mlopsv2-kv"
}

variable "appinsights_name" {
  type    = string
  default = "mlopsv2-appins"
}

variable "container_registry_name" {
  type    = string
  default = "mlopsv2acr"
}

variable "workspace_name" {
  type    = string
  default = "mlopsv2-ws"
}
