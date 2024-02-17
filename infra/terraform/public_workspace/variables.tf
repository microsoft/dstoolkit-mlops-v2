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
    validation {
        condition = (length(var.rg_name) <= 90 && length(var.rg_name) > 2 && can(regex("[-\\w\\._\\(\\)]+", var.rg_name)) )
        error_message = "Resource group name may only contain alphanumeric characters, dash, underscores, parentheses and periods."
    }
    default = "mlops-test-v2"
}
variable "basename" {
  type    = string
  default = "mlops"
}

variable "project_code" {
  type    = string
  default = "v2"
}

variable "version_num" {
  type    = string
  default = "100"
}

variable "location" {
  type    = string
  default = "eastus"
}
